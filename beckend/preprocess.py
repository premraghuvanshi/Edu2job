import sqlite3
import os
import pandas as pd
import pickle
import numpy as np
import streamlit as st
import sys

# Path setup
db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'storage.db')

# 1. CRITICAL: Tokenizer function for CountVectorizer
def career_tokenizer(text):
    if pd.isna(text): 
        return []
    return [s.strip().lower() for s in str(text).split(',')]

# Fix for Pickle AttributeError
import __main__
__main__.career_tokenizer = career_tokenizer

def fetch_user_education(user_id):
    """Fetches academic profile. Handles 'certificates' vs 'certifications' naming."""
    conn = sqlite3.connect(db_path)
    query = "SELECT * FROM EDUCATION WHERE user_id=? ORDER BY education_id DESC LIMIT 1"
    
    try:
        df = pd.read_sql_query(query, conn, params=(user_id,))
        conn.close()
        
        if not df.empty:
            # Normalize column names to lowercase
            df.columns = [c.lower() for c in df.columns]
            data = df.iloc[0].to_dict()
            
            # Map 'certificates' (DB) to the key used by prediction logic
            # We check 'certificates' first as per your DB update, fallback to 'certifications'
            certs_val = data.get('certificates') or data.get('certifications') or ""
            
            return {
                'degree': str(data.get('degree', '')).strip().upper(),
                'specialization': str(data.get('specialization', '')).strip().upper(),
                'skills': str(data.get('skills', '')).strip().lower(),
                'certificates': str(certs_val).strip().lower(),
                'cgpa': float(data.get('cgpa', 0))
            }
        return None
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

# Load the High-Accuracy Model Assets
try:
    with open('beckend/job_model_v5.pkl', 'rb') as f:
        assets = pickle.load(f)
        model = assets['model']
        edu_map = assets['edu_map']
        spec_le = assets['spec_le']
        skill_vec = assets['skill_vec']
        cert_vec = assets['cert_vec']
        scaler = assets['scaler']
        target_le = assets['target_le']
except FileNotFoundError:
    model = None
    st.error("Model file 'job_model_v5.pkl' not found.")
except Exception as e:
    model = None
    st.error(f"Error loading model: {e}")

def predict():
    user_id = st.session_state.get('user_id')
    if not user_id:
        st.error("User session not found. Please log in.")
        return

    try:
        user_profile = fetch_user_education(user_id)

        if user_profile and model:
            # 1. Map Education to Rank
            edu_rank = edu_map.get(user_profile['degree'], 0)
            
            # 2. Transform Specialization
            try:
                spec_encoded = spec_le.transform([user_profile['specialization']])[0]
            except:
                spec_encoded = 0 

            # 3. Vectorize Skills and Certificates (using the 'certificates' key from user_profile)
            skills_features = skill_vec.transform([user_profile['skills']]).toarray()
            certs_features = cert_vec.transform([user_profile['certificates']]).toarray()

            # 4. Scale Numeric Features (CGPA, Edu_Rank)
            numeric_features = scaler.transform([[user_profile['cgpa'], edu_rank]])

            # 5. Combine Features: [Numeric, Spec_ID, Skills, Certs]
            X_spec = np.array([[spec_encoded]])
            X_combined = np.hstack((numeric_features, X_spec, skills_features, certs_features))

            # 6. Make Prediction
            prediction_id = model.predict(X_combined)[0]
            job_role = target_le.inverse_transform([prediction_id])[0]

            # 7. Confidence Score
            probs = model.predict_proba(X_combined)[0]
            confidence = float(max(probs))

            # 8. Save to History
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO PREDICTIONHISTORY (user_id, predicted_roles, confidence_scores)
                    VALUES (?, ?, ?)          
                """, (user_id, job_role, round(confidence, 4)))
                conn.commit()
                conn.close()
            except Exception as e:
                st.error(f"History Logging Error: {e}")

            # 9. Result UI
            st.success(f"### Recommended Job: {job_role}")
            st.info(f"AI Confidence Score: **{confidence*100:.2f}%**")
            st.progress(confidence)
            
        else:
            st.warning("No academic profile found. Please update your profile details.")

    except Exception as e:
        st.error(f"Prediction logic error: {e}")

def get_history(user_id):
    try:
        conn = sqlite3.connect(db_path)
        query = """
            SELECT predicted_roles, confidence_scores, timestamp 
            FROM PREDICTIONHISTORY 
            WHERE user_id = ? 
            ORDER BY timestamp DESC LIMIT 5
        """
        df = pd.read_sql_query(query, conn, params=(user_id,))
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error loading history: {e}")
        return pd.DataFrame()
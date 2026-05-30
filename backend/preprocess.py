import sqlite3
import pandas as pd
import pickle
import numpy as np
import streamlit as st
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from backend.utils import career_tokenizer

# ==========================================
# 1. CONFIGURATION & CONSTANTS
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'data' / 'storage.db'
MODEL_PATH = BASE_DIR / 'backend' / 'job_model_v5.pkl'


# ==========================================
# 2. DATA ACCESS LAYER (Database Operations)
# ==========================================
def fetch_user_education(user_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves and standardizes the user's academic profile from the database."""
    query = "SELECT * FROM EDUCATION WHERE user_id=? ORDER BY education_id DESC LIMIT 1"
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            df = pd.read_sql_query(query, conn, params=(user_id,))
            
        if df.empty:
            return None

        df.columns = [c.lower() for c in df.columns]
        data = df.iloc[0].to_dict()
        
        certs_val = data.get('certificates') or data.get('certifications') or ""
        
        return {
            'degree': str(data.get('degree', '')).strip(),
            'specialization': str(data.get('specialization', '')).strip(),
            'skills': str(data.get('skills', '')).strip().lower(),
            'certificates': str(certs_val).strip().lower(),
            'cgpa': float(data.get('cgpa', 0.0))
        }
    except Exception as e:
        print(f"Database Read Error (Education): {e}")
        return None

def log_prediction_history(user_id: int, job_role: str, confidence: float) -> bool:
    """Logs the prediction result to the database."""
    query = """
        INSERT INTO PREDICTIONHISTORY (user_id, predicted_roles, confidence_scores)
        VALUES (?, ?, ?)
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (user_id, job_role, round(confidence, 4)))
            conn.commit()
        return True
    except Exception as e:
        print(f"Database Write Error (History): {e}")
        return False

def get_history(user_id: int) -> pd.DataFrame:
    """Retrieves the last 5 predictions for a user."""
    query = """
        SELECT predicted_roles, confidence_scores, timestamp 
        FROM PREDICTIONHISTORY 
        WHERE user_id = ? 
        ORDER BY timestamp DESC LIMIT 5
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            return pd.read_sql_query(query, conn, params=(user_id,))
    except Exception as e:
        print(f"Database Read Error (History): {e}")
        return pd.DataFrame()


# ==========================================
# 3. MACHINE LEARNING LAYER (Business Logic)
# ==========================================
class CareerPredictor:
    """Encapsulates model loading and inference to prevent global scope pollution."""
    
    def __init__(self, model_path: Path):
        self.model_path = model_path
        self.assets = self._load_assets()

    def _load_assets(self) -> Optional[Dict[str, Any]]:
        """Loads the serialized model and preprocessors lazily."""
        try:
            with open(self.model_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Model Load Error: {e}")
            return None

    def execute_prediction(self, profile: Dict[str, Any]) -> Tuple[Optional[str], float, Optional[pd.DataFrame]]:
        """Transforms user data and executes the XGBoost prediction pipeline."""
        if not self.assets:
            raise ValueError("Machine learning model assets are not loaded.")

        # Extract assets
        model = self.assets['model']
        edu_map = self.assets['edu_map']
        spec_le = self.assets['spec_le']
        skill_vec = self.assets['skill_vec']
        cert_vec = self.assets['cert_vec']
        scaler = self.assets['scaler']
        target_le = self.assets['target_le']

        # Transform Features
        edu_rank = edu_map.get(profile['degree'], 0)
        
        try:
            spec_encoded = spec_le.transform([profile['specialization']])[0]
        except ValueError:
            spec_encoded = 0 

        skills_features = skill_vec.transform([profile['skills']]).toarray()
        certs_features = cert_vec.transform([profile['certificates']]).toarray()
        numeric_features = scaler.transform([[profile['cgpa'], edu_rank]])

        # Construct Input Matrix
        X_spec = np.array([[spec_encoded]])
        X_combined = np.hstack((numeric_features, X_spec, skills_features, certs_features))

        # Predict
        prediction_id = model.predict(X_combined)[0]
        job_role = target_le.inverse_transform([prediction_id])[0]
        
        # Calculate Probabilities
        probs = model.predict_proba(X_combined)[0]
        confidence = float(max(probs))
        
        match_data = pd.DataFrame({
            'Job Role': target_le.classes_,
            'Match Percentage': probs * 100
        }).sort_values(by='Match Percentage', ascending=False).head(10)

        return job_role, confidence, match_data


# ==========================================
# 4. PRESENTATION LAYER (Streamlit UI)
# ==========================================
def predict():
    """Streamlit wrapper that coordinates the database, ML layer, and UI state."""
    user_id = st.session_state.get('user_id')
    if not user_id:
        st.error("User session not found. Please log in.")
        return

    user_profile = fetch_user_education(user_id)
    if not user_profile:
        st.warning("No academic profile found. Please update your profile details.")
        return

    try:
        predictor = CareerPredictor(MODEL_PATH)
        job_role, confidence, match_data = predictor.execute_prediction(user_profile)
        
        # Save exact matches to session state for the dashboard UI to render
        st.session_state['ai_match_graph_data'] = match_data
        
        # Log to DB
        log_prediction_history(user_id, job_role, confidence)

        # Render Results
        st.success(f"### Recommended Job: {job_role}")
        st.info(f"AI Confidence Score: **{confidence*100:.2f}%**")
        st.progress(confidence)

    except ValueError as ve:
        st.error(f"System Error: {ve} Please contact administration.")
    except Exception as e:
        st.error(f"Prediction execution failed: {e}")
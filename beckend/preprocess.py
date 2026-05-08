import sqlite3
import os
import pandas as pd
import pickle
import streamlit as st

db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'storage.db')

def fetch_user_education(user_id):
    conn=sqlite3.connect(db_path)
    query="""
     SELECT degree, specialization, CGPA, year_of_comp
     FROM EDUCATION
     WHERE user_id=?
     ORDER BY education_id DESC LIMIT 1
     """
    try:
        df=pd.read_sql_query(query , conn, params=(user_id,))
        conn.close()
        
        if not df.empty:
            data = df.iloc[0].to_dict()
            data['degree'] = str(data['degree']).strip().upper()
            data['specialization'] = str(data['specialization']).strip().upper()
            return data
        return None
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None


try:
    with open('beckend/job_model_v5.pkl','rb') as f:
      assets = pickle.load(f)
      model=assets['model']
      encoders=assets['encoders']
except FileNotFoundError:
    model = None
    st.error("Model file not found! Check your folder structure.")

def predict():
    user_id = st.session_state.get('user_id')
    try:
        user_profile = fetch_user_education(user_id)

        if user_profile and model:
            
            d_enc = encoders["Degree"].transform([user_profile['degree']])[0]
            s_enc = encoders["Specialization"].transform([user_profile['specialization']])[0]

            
            feature_names = ['Degree', 'Specialization', 'CGPA', 'YearOfCompletion']
            input_df = pd.DataFrame([[
                d_enc, 
                s_enc, 
                user_profile['CGPA'], 
                user_profile['year_of_comp']
            ]], columns=feature_names)

            
            prediction = model.predict(input_df)[0]
            job_role = encoders['JobRole'].inverse_transform([prediction])[0]

            probs = model.predict_proba(input_df)[0]
            confidence = float(max(probs))

           
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO PREDICTIONHISTORY (user_id, predicted_roles, confidence_scores)
                    VALUES (?,?,?)         
                """, (user_id, job_role, round(confidence, 4)))
                conn.commit()
                conn.close()
            except Exception as e:
                st.error(f"Database Error: {e}")

            # 5. UI Result
            st.success(f"### Recommended Job: {job_role}")
            st.info(f"Confidence Score: **{confidence*100:.2f}%**")
            
        else:
            st.warning("Ensure your profile is updated.")

    except ValueError:
        
        st.error("**Profile Value Error:** Your Degree or Specialization is not recognized by our AI model.")
        st.info("Please update your profile using the dropdown menus to ensure compatibility.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")


def get_history(user_id):
    try:
      conn=sqlite3.connect('data/storage.db')
      query="""
         SELECT predicted_roles , confidence_scores, timestamp
         FROM PREDICTIONHISTORY
         WHERE user_id = ?
         ORDER BY timestamp DESC LIMIT 5
      """
      df=pd.read_sql_query(query,conn,params=(user_id,))
      conn.close()
      return df
    except Exception as e:
        st.error(f"Database Error :{e}")
        return pd.DataFrame()
import streamlit as st
import pandas as pd
import os
import sqlite3
import matplotlib.pyplot as plt
from beckend.model_training import train_career_model

def inject_ultra_premium_theme():
    st.markdown("""
    <style>
        /* 1. ANIMATED MESH GRADIENT BACKGROUND */
        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .stApp {
            background: linear-gradient(-45deg, #020617, #0f172a, #064e3b, #020617);
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
            color: #f8fafc;
        }

        /* 2. PREMIUM GLASS CONTAINER WITH FLOAT EFFECT */
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
            100% { transform: translateY(0px); }
        }

        [data-testid="stVerticalBlock"] > div:has(div.stTabs) {
            background: rgba(255, 255, 255, 0.02);
            backdrop-filter: blur(15px);
            border-radius: 24px;
            padding: 40px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
            animation: float 6s ease-in-out infinite;
        }

        /* 3. SIDEBAR: NEUMORPHIC DARK */
        [data-testid="stSidebar"] {
            background-color: rgba(2, 6, 23, 0.9) !important;
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(16, 185, 129, 0.1);
        }

        /* 4. SIDEBAR METRICS */
        [data-testid="stMetric"] {
            background: rgba(16, 185, 129, 0.05);
            border-left: 4px solid #10b981;
            padding: 20px !important;
            border-radius: 12px;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        [data-testid="stMetric"]:hover {
            background: rgba(16, 185, 129, 0.15);
            transform: translateX(10px) scale(1.02);
            box-shadow: 0 0 20px rgba(16, 185, 129, 0.2);
        }

        /* 5. INPUT FIELDS */
        input {
            background-color: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: #ecfdf5 !important;
            border-radius: 10px !important;
        }

        /* 6. BUTTONS */
        div.stButton > button {
            width: 100%;
            background: #020617 !important;
            color: #f8fafc !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            padding: 14px;
            border-radius: 12px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            transition: all 0.4s ease;
        }

        div.stButton > button:hover {
            border-color: #10b981 !important;
            color: #10b981 !important;
            box-shadow: 0 0 15px rgba(16, 185, 129, 0.4);
            transform: translateY(-2px);
        }

        [data-testid="stSidebarNav"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

inject_ultra_premium_theme()

# FIX 1: Use cache_resource to prevent UnserializableReturnValueError
@st.cache_resource
def get_db_connection():
    conn = sqlite3.connect('data/storage.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def admin_panel():
    if st.session_state.get('role') != 'admin':
        st.error("Access Denied")
        if st.button("Return to login"):
            st.switch_page("app.py")
        st.stop()
    
    st.set_page_config(page_title="Edu2Job Admin", layout="wide")
    st.title("Administrative Control Center")
    st.write(f"Welcome back, **{st.session_state.get('user_name','Admin')}**")
    st.markdown("---")

    # Metrics Sidebar
    with st.sidebar:
        st.header("System Stats")
        conn = get_db_connection()
        total_u = conn.execute("SELECT COUNT(*) FROM USER").fetchone()[0]
        total_p = conn.execute("SELECT COUNT(*) FROM PREDICTIONHISTORY").fetchone()[0]
        st.metric("Total Students", total_u)
        st.metric("Predictions Made", total_p)

        if st.button("Logout", use_container_width=True):
            st.session_state.clear()
            st.switch_page("app.py")

    tab1, tab2, tab3 = st.tabs(["User Management", "Career Trends", "Model Operations"])

    with tab1:
        st.subheader("User Administration")
        conn = get_db_connection()
        user_df = pd.read_sql_query("SELECT user_id, name, email, role FROM USER", conn)

        for _, row in user_df.iterrows():
            with st.expander(f"ID:{row['user_id']} | {row['name']} ({row['role'].upper()})"):
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"**Email:** {row['email']}")
                
                if row['role'] == 'user':
                    if c2.button("Promote", key=f"p_{row['user_id']}", use_container_width=True):
                        conn.execute("UPDATE USER SET role='admin' WHERE user_id=?", (row['user_id'],))
                        conn.commit()
                        st.rerun()
                if c3.button("Delete", key=f"d_{row['user_id']}", type="primary", use_container_width=True):
                    conn.execute("DELETE FROM USER WHERE user_id=?", (row['user_id'],))
                    conn.execute("DELETE FROM EDUCATION WHERE user_id=?", (row['user_id'],))
                    conn.commit()
                    st.rerun()

    with tab2:
        st.subheader("System Insights")
        conn = get_db_connection()
        query = """
            SELECT E.degree, P.predicted_roles
            FROM EDUCATION E
            JOIN PREDICTIONHISTORY P ON E.user_id = P.user_id
        """
        trend_df = pd.read_sql_query(query, conn)

        if not trend_df.empty:
            col_left, col_right = st.columns(2)
            with col_left:
                st.write("**Top Job Role Predictions**")
                st.bar_chart(trend_df['predicted_roles'].value_counts())
            with col_right:
                st.write("**Prediction by Degree Type**")
                st.bar_chart(trend_df["degree"].value_counts())
        else:
            st.info("No prediction data available yet.")

    with tab3:
        st.subheader("Machine Learning Operations")
        
        st.write("### Step 1: Update Training Dataset")
        uploaded_file = st.file_uploader("Upload new CSV dataset", type=["csv"])
        
        if uploaded_file is not None:
            if st.button("Confirm Upload & Overwrite"):
                try:
                    df_new = pd.read_csv(uploaded_file)
                    os.makedirs('data', exist_ok=True)
                    # Save to the specific path used for training
                    df_new.to_csv('data/job_dataset.csv', index=False)
                    st.success("Dataset updated! Path: `data/job_dataset.csv`")
                except Exception as e:
                    st.error(f"Error saving dataset: {e}")

        st.markdown("---")
        
        st.write("### Step 2: Model Management")
        model_path = 'beckend/job_model_v5.pkl'
        if os.path.exists(model_path):
            st.success(f'Active Model: `{model_path}` is currently serving.')
        else:
            st.warning("No model found. Please train the system.")

        if st.button("Trigger Full System Retrain"):
            with st.spinner("Retraining Random Forest... Please wait"):
                try:
                    # FIX 2: Pass the specific path to the trainer
                    # FIX 3: Add None check to prevent "NoneType * int" error
                    accuracy = train_career_model(csv_path='data/job_dataset.csv')
                    
                    if accuracy is not None:
                        st.success(f"Model Retrained! New Testing Accuracy: **{accuracy*100:.2f}%**")
                    else:
                        st.error("Training failed: The training function returned no result. Check if the dataset is valid.")
                except Exception as e:
                    st.error(f"Critical Training Failure: {e}")

if __name__ == "__main__":
    admin_panel()
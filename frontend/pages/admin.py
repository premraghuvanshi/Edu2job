import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path

# Correct backend import
from backend.model_training import train_career_model

# ==========================================
# 1. CONFIGURATION & PATHS
# ==========================================
# Resolves to the root project directory (Edu2job/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / 'data' / 'storage.db'
CSV_PATH = BASE_DIR / 'data' / 'job_dataset.csv'
MODEL_PATH = BASE_DIR / 'backend' / 'job_model_v5.pkl'

REQUIRED_COLUMNS = {
    'Education Level', 'Specialization', 'Skills', 
    'Certifications', 'CGPA', 'Recommended Career'
}

# ==========================================
# 2. UI STYLING
# ==========================================
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

        /* 2. PREMIUM GLASS CONTAINER */
        [data-testid="stVerticalBlock"] > div:has(div.stTabs) {
            background: rgba(255, 255, 255, 0.02);
            backdrop-filter: blur(15px);
            border-radius: 24px;
            padding: 40px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
        }

        /* 3. SIDEBAR & METRICS */
        [data-testid="stSidebar"] {
            background-color: rgba(2, 6, 23, 0.9) !important;
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(16, 185, 129, 0.1);
        }
        [data-testid="stMetric"] {
            background: rgba(16, 185, 129, 0.05);
            border-left: 4px solid #10b981;
            padding: 20px !important;
            border-radius: 12px;
            transition: all 0.3s ease;
        }
        [data-testid="stMetric"]:hover {
            transform: translateX(5px);
            box-shadow: 0 0 15px rgba(16, 185, 129, 0.2);
        }

        /* 4. BUTTONS & INPUTS */
        div.stButton > button {
            background: #020617 !important;
            color: #f8fafc !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            padding: 12px;
            border-radius: 12px;
            font-weight: bold;
            text-transform: uppercase;
            transition: all 0.3s ease;
        }
        div.stButton > button:hover {
            border-color: #10b981 !important;
            color: #10b981 !important;
            transform: translateY(-2px);
        }
        div.stButton > button[kind="primary"] {
            border: 1px solid rgba(16, 185, 129, 0.3) !important;
        }
        
        [data-testid="stSidebarNav"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. CORE ADMIN APPLICATION
# ==========================================
def admin_panel():
    # Strict Authorization Check
    if st.session_state.get('role') != 'admin':
        st.error("Access Denied. Administrator privileges required.")
        if st.button("Return to Login"):
            st.switch_page("app.py")
        st.stop()
    
    st.set_page_config(page_title="Edu2Job Admin", layout="wide")
    inject_ultra_premium_theme()
    
    st.title("Administrative Control Center")
    st.write(f"Welcome back, **{st.session_state.get('user_name', 'Admin')}**")
    st.markdown("---")

    # --- SIDEBAR METRICS ---
    with st.sidebar:
        st.header("System Stats")
        try:
            with sqlite3.connect(str(DB_PATH), timeout=10) as conn:
                total_u = conn.execute("SELECT COUNT(*) FROM USER").fetchone()[0]
                total_p = conn.execute("SELECT COUNT(*) FROM PREDICTIONHISTORY").fetchone()[0]
            st.metric("Total Students", total_u)
            st.metric("Predictions Made", total_p)
        except Exception as e:
            st.error(f"Database connection error: {e}")

        if st.button("Logout", width="stretch"):
            st.session_state.clear()
            st.switch_page("app.py")

    tab1, tab2, tab3 = st.tabs(["User Management", "Career Trends", "Model Operations"])

    # --- TAB 1: USER MANAGEMENT ---
    with tab1:
        st.subheader("User Administration")
        try:
            with sqlite3.connect(str(DB_PATH), timeout=10) as conn:
                user_df = pd.read_sql_query("SELECT user_id, name, email, role FROM USER", conn)

            for _, row in user_df.iterrows():
                with st.expander(f"ID:{row['user_id']} | {row['name']} ({row['role'].upper()})"):
                    c1, c2, c3 = st.columns([3, 1, 1])
                    c1.write(f"**Email:** {row['email']}")
                    
                    if row['role'] == 'user':
                        if c2.button("Promote", key=f"p_{row['user_id']}", width="stretch"):
                            with sqlite3.connect(str(DB_PATH), timeout=10) as write_conn:
                                write_conn.execute("UPDATE USER SET role='admin' WHERE user_id=?", (row['user_id'],))
                                write_conn.commit()
                            st.rerun()
                            
                    if c3.button("Delete", key=f"d_{row['user_id']}", type="primary", width="stretch"):
                        with sqlite3.connect(str(DB_PATH), timeout=10) as write_conn:
                            write_conn.execute("DELETE FROM USER WHERE user_id=?", (row['user_id'],))
                            write_conn.execute("DELETE FROM EDUCATION WHERE user_id=?", (row['user_id'],))
                            write_conn.commit()
                        st.rerun()
        except Exception as e:
            st.error(f"Error loading users: {e}")

    # --- TAB 2: SYSTEM INSIGHTS ---
    with tab2:
        st.subheader("System Insights")
        try:
            with sqlite3.connect(str(DB_PATH), timeout=10) as conn:
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
        except Exception as e:
            st.error(f"Error loading trends: {e}")

    # --- TAB 3: MACHINE LEARNING OPERATIONS ---
    with tab3:
        st.subheader("Machine Learning Operations")
        
        st.write("### Step 1: Update Training Dataset")
        uploaded_file = st.file_uploader("Upload new CSV dataset", type=["csv"])
        
        if uploaded_file is not None:
            if st.button("Confirm Upload & Overwrite"):
                try:
                    df_new = pd.read_csv(uploaded_file)
                    
                    if REQUIRED_COLUMNS.issubset(set(df_new.columns)):
                        CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
                        df_new.to_csv(CSV_PATH, index=False)
                        st.success(f"Dataset securely updated! Path: `{CSV_PATH}`")
                    else:
                        missing = REQUIRED_COLUMNS - set(df_new.columns)
                        st.error(f"Upload Rejected: CSV is missing required columns: {missing}")
                except Exception as e:
                    st.error(f"Error saving dataset: {e}")

        st.markdown("---")
        
        st.write("### Step 2: Model Management")
        if MODEL_PATH.exists():
            st.success(f'Active Model: `{MODEL_PATH.name}` is currently serving.')
        else:
            st.warning("No model found. Please train the system.")

        if st.button("Trigger Full System Retrain"):
            with st.spinner("Retraining XGBoost Pipeline... Please wait"):
                try:
                    accuracy = train_career_model(csv_path=str(CSV_PATH))
                    
                    if accuracy is not None:
                        st.success(f"Model Retrained Successfully! New Testing Accuracy: **{accuracy*100:.2f}%**")
                    else:
                        st.error("Training failed: The training pipeline crashed. Check the terminal logs.")
                except Exception as e:
                    st.error(f"Critical Training Failure: {e}")

if __name__ == "__main__":
    admin_panel()
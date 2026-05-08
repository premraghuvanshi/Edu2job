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

        /* 4. SIDEBAR METRICS: SLIDE & GLOW HOVER */
        [data-testid="stMetric"] {
            background: rgba(16, 185, 129, 0.05);
            border-left: 4px solid #10b981;
            padding: 20px !important;
            border-radius: 12px;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            cursor: pointer;
        }
        [data-testid="stMetric"]:hover {
            background: rgba(16, 185, 129, 0.15);
            transform: translateX(10px) scale(1.02);
            box-shadow: 0 0 20px rgba(16, 185, 129, 0.2);
        }

        /* 5. INPUT FIELDS: CYBERPUNK FOCUS */
        input {
            background-color: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: #ecfdf5 !important;
            border-radius: 10px !important;
            transition: all 0.3s ease;
        }
        input:focus {
            border-color: #10b981 !important;
            box-shadow: 0 0 15px rgba(16, 185, 129, 0.3) !important;
            background-color: rgba(16, 185, 129, 0.05) !important;
        }

        /* 6. BUTTONS: EMERALD GRADIENT */
        div.stButton > button {
            width: 100%;
            background: #020617 !important; /* Deep dark background */
            color: #f8fafc !important; /* Light text */
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            padding: 14px;
            border-radius: 12px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }

        div.stButton > button:hover {
            background: #020617 !important;
            border-color: #10b981 !important; /* Lite Emerald glow border */
            color: #10b981 !important; /* Text also shifts slightly to match */
            box-shadow: 0 0 15px rgba(16, 185, 129, 0.4); /* Lite glow effect */
            transform: translateY(-2px);
        }

        /* Specifically for Primary buttons if used */
        div.stButton > button[kind="primary"] {
            background: #020617 !important;
            border: 1px solid rgba(16, 185, 129, 0.3) !important;
        }

        /* 7. TABS STYLING */
        .stTabs [data-baseweb="tab-list"] { gap: 20px; }
        .stTabs [data-baseweb="tab"] {
            color: #94a3b8;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            color: #10b981 !important;
            border-bottom-color: #10b981 !important;
        }

        /* Hide Default Sidebar Nav */
        [data-testid="stSidebarNav"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

inject_ultra_premium_theme()

def get_db_connection():
    conn=sqlite3.connect('data/storage.db')
    conn.row_factory=sqlite3.Row
    return conn
def admin_panel():
    if st.session_state.get('role')!='admin':
        st.error("Access Denied")
        if st.button("Return to login"):
            st.switch_page("app.py")
        st.stop()
    st.set_page_config(page_title="Edu2Job Admin", layout="wide")
    st.title("Administrative Control Center")
    st.write(f"Welcome back, **{st.session_state.get('user_name','Admin')}**")
    st.markdown("---")

    with st.sidebar:
        st.header("System Stats")
        conn = get_db_connection()
        total_u= conn.execute("SELECT COUNT (*) FROM USER").fetchone()[0]
        total_p =conn.execute("SELECT COUNT(*) FROM PREDICTIONHISTORY").fetchone()[0]
        conn.close()
        st.metric("Total Students", total_u)
        st.metric("Prediction Made", total_p)

        if st.button("Logout",use_container_width=True):
            st.session_state.clear()
            st.switch_page("app.py")

    tab1, tab2, tab3 = st.tabs(["User Management", "Career Trends","Model Operations"])

    with tab1:
        st.subheader("User Administration")
        conn=get_db_connection()
        user_df = pd.read_sql_query("SELECT user_id, name, email, role FROM USER",conn)

        for _, row in user_df.iterrows():
            with st.expander(f"ID:{row['user_id']} | {row['name']} ({row['role'].upper()})"):
                c1,c2,c3=st.columns([3,1,1])
                c1.write(f"**Email:** {row['email']}")
                
                if row['role']=='user':
                    if c2.button("Promote", key=f"p_{row['user_id']}", use_container_width=True):
                        conn.execute("UPDATE USER SET role= 'admin' WHERE user_id=?", (row['user_id'],))
                        conn.commit()
                        st.rerun()
                if c3.button("Delete", key=f"d_{row['user_id']}", type="primary", use_container_width=True):
                    conn.execute("DELETE FROM USER WHERE user_id = ?", (row['user_id'],))
                    conn.execute("DELETE FROM EDUCATION WHERE user_id=?",(row['user_id'],))
                    conn.commit()
                    st.rerun()
        conn.close()
    with tab2:
        st.subheader("System Insights")
        conn=get_db_connection()
        query="""
             SELECT E.degree, P.predicted_roles
             FROM EDUCATION E
             JOIN PREDICTIONHISTORY P ON E.user_id = P.user_id
            """
        trend_df = pd.read_sql_query(query, conn)
        conn.close()

        if not trend_df.empty:
            col_left, col_right= st.columns(2)
            with col_left:
                st.write("**Top Job Role Predictions**")
                st.bar_chart(trend_df['predicted_roles'].value_counts())
            with col_right:
                st.write("**Prediction by Degree Type**")
                st.bar_chart(trend_df["degree"].value_counts())
        else:
            st.info("NO prediction data available to analyze trends yet.")
    with tab3:
        st.subheader("Machine Learning Operations")
        
        # Section 1: Data Update
        st.write("###  Step 1: Update Training Dataset")
        uploaded_file = st.file_uploader("Upload new CSV dataset to replace 'job_dataset.csv'", type=["csv"])
        
        if uploaded_file is not None:
            if st.button(" Confirm Upload & Overwrite"):
                try:
                    # Save the new file to the data directory
                    df_new = pd.read_csv(uploaded_file)
                    os.makedirs('data', exist_ok=True)
                    df_new.to_csv('data/job_dataset.csv', index=False)
                    st.success("Dataset updated successfully! You can now proceed to retrain.")
                except Exception as e:
                    st.error(f"Error saving dataset: {e}")

        st.markdown("---")
        
        # Section 2: Model Retraining
        st.write("###  Step 2: Model Management")
        if os.path.exists('beckend/job_model_v5.pkl'):
            st.success('Active Model: `job_model_v5.pkl` is currently serving.')
        else:
            st.warning("No model found. Please train the system.")

        if st.button(" Trigger Full System Retrain"):
            with st.spinner("Retraining Random Forest... Calculating Entropy & Info Gain"):
                try:
                    accuracy = train_career_model()
                    st.success(f"Model Retrained! New Testing Accuracy: **{accuracy*100:.2f}%**")
                except Exception as e:
                    st.error(f"Training Failed: {e}")

                    

if __name__ == "__main__":
    admin_panel()
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)
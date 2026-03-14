import streamlit as st
import pandas as pd
import os
import sqlite3
import matplotlib.pyplot as plt
from beckend.model_training import train_career_model

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
        st.subheader("Machine Learning Operations (MLOps)")
        st.write("Current Model: `beckend/job_model_v5.pkl`")

        if os.path.exists('beckend/job_model_v5.pkl'):
            st.success('Model Binary is active and serving')

        else:
            st.error("Model Binary not found")

        st.markdown("---")
        st.write("Click below to trigger a full system retrain using `data/job_dataset.csv`.")
        if st.button("Retrain System Model"):
            with st.spinner("Calculating Entropy and INformation Gain.."):
                try:
                    accuracy=train_career_model()
                    st.success(f"Model Updated! New Accuracy: **{accuracy*100:.2f}%**")
                except Exception as e :
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
import streamlit as st
import pandas as pd
from beckend.preprocess import  predict , get_history
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


if 'token' not in st.session_state:
    st.error("Please login first!")
    if st.button("Return to Login"):
        st.switch_page('app.py')
    st.stop()
    
st.title("User Dashboard")
st.markdown("---")
st.sidebar.title(f"Hi,{st.session_state.get('user_name','Student')}")
st.sidebar.markdown("---")

if st.sidebar.button("Dashboard Home", use_container_width=True):
    st.rerun()
if st.sidebar.button("View profile",use_container_width=True):
    st.switch_page("pages/profile.py")

st.sidebar.markdown("---")
if st.sidebar.button("Logout", use_container_width=True, type="secondary"):
    st.session_state.clear()
    st.switch_page("app.py")




if "prediction" in st.session_state:
        st.info(f"**Last Prediction:** {st.session_state['prediction']}")

if st.button("Predict My Job Role", type="primary"):
    predict()
st.markdown("---")
with st.expander("Industry Demand Analysis"):
  st.write("This chart shows the distribution of career paths available in our current dataset.")

  try:
    # Use relative path from root
    df_data = pd.read_csv('data/job_dataset.csv')
    
    # Calculate the frequency of each job role
    role_counts = df_data['JobRole'].value_counts()
    
    # Streamlit's native bar chart
    st.bar_chart(role_counts)
    
    # Optional: Display as a table for clarity
    with st.expander("See Raw Distribution Data"):
        st.write(role_counts)

  except FileNotFoundError:
    st.warning("Dataset not found.")
with st.expander("View Prediction History",expanded=False):
    history_df=get_history(st.session_state['user_id'])

    if not history_df.empty:
        history_df.columns=['Recommended Role','Confidence', 'Timestamp']

        st.dataframe(
            history_df.style.format({"Confidence": "{:.2%}"}),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No history found.")







    
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

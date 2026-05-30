import streamlit as st
import pandas as pd

# Fixed import to match the actual refactored backend filename
from beckend.preprocess import predict, get_history

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
            background: #020617 !important;
            color: #f8fafc !important;
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
            border-color: #10b981 !important;
            color: #10b981 !important;
            box-shadow: 0 0 15px rgba(16, 185, 129, 0.4);
            transform: translateY(-2px);
        }

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

        /* 8. HIDE SIDEBAR NAV */
        [data-testid="stSidebarNav"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 1. INITIALIZATION & AUTHENTICATION
# ==========================================
inject_ultra_premium_theme()

if 'user_id' not in st.session_state:
    st.error("Authentication required. Please log in.")
    if st.button("Return to Login"):
        st.switch_page('app.py')
    st.stop()

# ==========================================
# 2. SIDEBAR NAVIGATION
# ==========================================
st.sidebar.title(f"Hi, {st.session_state.get('user_name', 'Student')}")
st.sidebar.markdown("---")

if st.sidebar.button("Dashboard Home", width="stretch"):
    st.rerun()

if st.sidebar.button("View Profile", width="stretch"):
    st.switch_page("pages/profile.py")

st.sidebar.markdown("---")

if st.sidebar.button("Logout", width="stretch", type="secondary"):
    st.session_state.clear()
    st.switch_page("app.py")

# ==========================================
# 3. MAIN DASHBOARD AREA
# ==========================================
st.title("User Dashboard")
st.markdown("---")

if st.button("Predict My Job Role", type="primary"):
    with st.spinner("Analyzing profile and computing exact probability distribution..."):
        predict()
        
st.markdown("---")

# ==========================================
# 4. ANALYTICS & RESULTS PANELS
# ==========================================
with st.expander("Personalized AI Career Match", expanded=True):
    if "ai_match_graph_data" in st.session_state:
        st.write("This chart indicates the mathematical alignment of your profile against available career paths.")
        st.bar_chart(
            data=st.session_state["ai_match_graph_data"],
            x="Job Role",
            y="Match Percentage",
            color="#10b981",
            width="stretch"
        )
    else:
        st.info("Click the 'Predict My Job Role' button to generate your personalized distribution.")

with st.expander("View Prediction History", expanded=False):
    history_df = get_history(st.session_state['user_id'])

    if not history_df.empty:
        history_df.columns = ['Recommended Role', 'Confidence', 'Timestamp']
        st.dataframe(
            history_df.style.format({"Confidence": "{:.2%}"}),
            width="stretch",
            hide_index=True
        )
    else:
        st.info("No prediction history found on this account.")
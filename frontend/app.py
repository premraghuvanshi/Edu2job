import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st


from beckend.auth import (
    register_user, 
    login_user, 
    generate_token, 
    get_google_auth_url,    
    verify_google_token,    
    get_or_create_google_user 
)
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

@st.dialog("Reset Your Password")
def reset_password_dialog():
    st.write("Enter your registered email and a new password.")
    res_email = st.text_input("Registered Email")
    res_new_pass = st.text_input("New Password", type="password")
    res_confirm_pass = st.text_input("Confirm New Password", type="password")
    
    if st.button("Reset Password", type="primary"):
        if res_new_pass != res_confirm_pass:
            st.error("Passwords do not match!")
        elif not res_email or not res_new_pass:
            st.warning("Please fill all fields.")
        else:
            from beckend.auth import reset_password
            result = reset_password(res_email, res_new_pass)
            if result["status"] == "success":
                st.success(result["message"])
                st.info("You can now close this window and sign in.")
            else:
                st.error(result["message"])

with st.sidebar:
    st.title(" Edu2job")
    st.caption("AI-Powered Career Intelligence")
    
    
    st.markdown("---")
    
  
    st.subheader("Live Insights")
    st.metric(label="Model Accuracy", value="98.4%", delta="1.2%")
    st.metric(label="Total Users", value="50+", delta="Active")
    
    st.markdown("---")
    st.divider()
    st.caption("© 2026 Edu2job Project Team")


query_params = st.query_params

if "code" in query_params and 'token' not in st.session_state:
    auth_code = query_params["code"]
    
    
    user_info = verify_google_token(auth_code)
    
   
    user_id, role = get_or_create_google_user(user_info['email'], user_info['name'])
    
   
    st.session_state['token'] = generate_token(user_id, role)
    st.session_state['user_id'] = user_id
    st.session_state['user_name'] = user_info['name']
    st.session_state['role'] = role
    
   
    st.query_params.clear()
    if role == 'admin':
        st.switch_page("pages/admin.py")
    else:
        st.switch_page("pages/dashboard.py")

st.title("Edu2job: Job Role Prediction System")



tab1, tab2 = st.tabs([" Sign In", " Create Account"])

with tab1:
    st.subheader("Login to Your Dashboard")
    col1, _ = st.columns([2, 1])
    with col1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Sign In", type="primary", use_container_width=True)

        if login_btn:
            result = login_user(email, password)
            if result["status"] == "success":
                st.session_state['token'] = generate_token(result["id"], result["role"])
                st.session_state['user_id'] = result["id"]
                st.session_state["user_name"] = result["name"]
                st.session_state["role"] = result["role"]

                if result["role"] == "admin":
                    st.switch_page("pages/admin.py")
                else:
                    st.switch_page("pages/dashboard.py")
            else:
                st.error("Invalid Email or Password")
        if st.button("Forgot Password?", type="secondary"):
           reset_password_dialog()

    
        google_url = get_google_auth_url()
        st.link_button("Login with Google", google_url, use_container_width=True)

with tab2:
    st.subheader("Register New Account")
    with st.form("reg_form"):
        new_user = st.text_input("Full Name")
        new_email = st.text_input("Email Address")
        new_password = st.text_input("Create Password", type='password')
        reg_btn = st.form_submit_button("Register", use_container_width=True)

    if reg_btn:
        if new_user and new_email and new_password:
            if register_user(new_user, new_email, new_password):
                st.success("Account Created Successfully! Please switch to the Sign In tab.")
            else:
                st.error("Registration failed. Email might already be in use.")
        else:
            st.warning("Please fill in all fields.")


st.markdown("---")
with st.expander("ℹ About the System"):
    st.write("""
    Edu2job is a machine learning integrated platform. 
    - **Step 1:** Users register and provide academic details.
    - **Step 2:** The Decision Tree Classifier analyzes data.
    - **Step 3:** The system predicts the most suitable Job Role with confidence scores.
    """)

st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

    

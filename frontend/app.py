import os
import sys
import streamlit as st

# Ensure backend module path is accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from beckend.auth import (
    register_user, 
    login_user, 
    generate_token, 
    get_google_auth_url,    
    verify_google_token,    
    get_or_create_google_user 
)

# ==========================================
# 1. UI STYLING & THEMING
# ==========================================
def inject_ultra_premium_theme():
    """Injects custom CSS for the dark emerald animated theme."""
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

        /* 3. SIDEBAR STYLING */
        [data-testid="stSidebar"] {
            background-color: rgba(2, 6, 23, 0.9) !important;
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(16, 185, 129, 0.1);
        }

        /* 4. METRICS & INPUTS */
        [data-testid="stMetric"] {
            background: rgba(16, 185, 129, 0.05);
            border-left: 4px solid #10b981;
            padding: 20px !important;
            border-radius: 12px;
            transition: all 0.4s ease;
        }
        [data-testid="stMetric"]:hover {
            transform: translateX(5px);
        }
        input {
            background-color: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: #ecfdf5 !important;
            border-radius: 10px !important;
        }
        input:focus {
            border-color: #10b981 !important;
            box-shadow: 0 0 10px rgba(16, 185, 129, 0.3) !important;
        }

        /* 5. BUTTONS */
        div.stButton > button {
            width: 100%;
            background: #020617 !important;
            color: #f8fafc !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            padding: 14px;
            border-radius: 12px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            transition: all 0.3s ease;
        }
        div.stButton > button:hover {
            border-color: #10b981 !important;
            color: #10b981 !important;
            box-shadow: 0 0 15px rgba(16, 185, 129, 0.3);
            transform: translateY(-2px);
        }

        /* Hide Default Nav */
        [data-testid="stSidebarNav"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

inject_ultra_premium_theme()

# ==========================================
# 2. DIALOGS & MODALS
# ==========================================
@st.dialog("Reset Your Password")
def reset_password_dialog():
    """Secure password reset dialog requiring the old password."""
    st.write("Please verify your identity to change your password.")
    res_email = st.text_input("Registered Email")
    res_old_pass = st.text_input("Current Password", type="password")
    res_new_pass = st.text_input("New Password", type="password")
    res_confirm_pass = st.text_input("Confirm New Password", type="password")
    
    if st.button("Update Password", type="primary"):
        if not res_email or not res_old_pass or not res_new_pass:
            st.warning("Please fill out all fields.")
        elif res_new_pass != res_confirm_pass:
            st.error("New passwords do not match!")
        else:
            from beckend.auth import reset_password
            result = reset_password(res_email, res_old_pass, res_new_pass)
            if result.get("status") == "success":
                st.success(result["message"])
                st.info("You can now close this window and sign in.")
            else:
                st.error(result.get("message", "Reset failed."))

# ==========================================
# 3. SIDEBAR LAYOUT
# ==========================================
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

# ==========================================
# 4. GOOGLE OAUTH CALLBACK HANDLING
# ==========================================
query_params = st.query_params
if "code" in query_params and 'token' not in st.session_state:
    try:
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
    except Exception as e:
        st.error("Google Authentication Failed. Please check server configuration.")
        print(f"OAuth Error: {e}")

# ==========================================
# 5. MAIN APPLICATION UI
# ==========================================
st.title("Edu2job: Job Role Prediction System")

tab1, tab2 = st.tabs([" Sign In", " Create Account"])

# --- TAB 1: LOGIN ---
with tab1:
    st.subheader("Login to Your Dashboard")
    col1, _ = st.columns([2, 1])
    with col1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Sign In", type="primary", width="stretch")

        if login_btn:
            result = login_user(email, password)
            if result.get("status") == "success":
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

        # Safely render Google Login button
        try:
            google_url = get_google_auth_url()
            st.link_button("Login with Google", google_url, width="stretch")
        except ValueError as ve:
            st.warning("Google Login is currently disabled (Missing Configuration).")

# --- TAB 2: REGISTER ---
with tab2:
    st.subheader("Register New Account")
    with st.form("reg_form"):
        new_user = st.text_input("Full Name")
        new_email = st.text_input("Email Address")
        new_password = st.text_input("Create Password", type='password')
        reg_btn = st.form_submit_button("Register", width="stretch")

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
    - **Step 2:** The **XGBoost** machine learning model analyzes the skills and profile data.
    - **Step 3:** The system predicts the most suitable Job Role based on industry distributions, providing exact confidence scores.
    """)
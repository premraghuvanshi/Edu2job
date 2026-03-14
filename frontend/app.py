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

# --- NATIVE STREAMLIT SIDEBAR ---
with st.sidebar:
    st.title(" Edu2job")
    st.caption("AI-Powered Career Intelligence")
    
    
    st.markdown("---")
    
    # 2. Key Metrics Section
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

# menu=["Register","Login"]
# choice=st.sidebar.selectbox("Menu",menu)

# if choice == "Register":
#     st.subheader("Create New Account")
#     new_user=st.text_input("Username")
#     new_email=st.text_input("Email")
#     new_password=st.text_input("Password", type='password')

#     if st.button("Register"):
#         if register_user(new_user,new_email,new_password):
#             st.success("Account Created")
#         else:
#             st.error("Email already exists.")


# elif choice == "Login":
#     st.subheader("Login to Your Dashboard")
#     email=st.text_input("Email")
#     password=st.text_input("Password", type="password")


#     if st.button("Login"):
#         result=login_user(email,password)
#         if result["status"]=="success":
#             token=generate_token(result["id"],result["role"])
#             st.session_state['token']=token
#             st.session_state['user_id']=result["id"]
#             st.session_state["user_name"]=result["name"]
#             st.session_state["role"]=result["role"]

#             if result["role"]=="admin":
#                 st.switch_page("pages/admin.py")
#             else:
#                 st.switch_page("pages/dashboard.py")
            
#         else:
#             st.error("Invalid Email or Password")
#     st.write("---") # Visual separator
    
#     # Google Login Button
#     google_url = get_google_auth_url()
#     st.link_button("Login with Google", google_url, type="primary", use_container_width=True)

tab1, tab2 = st.tabs([" Sign In", " Create Account"])

with tab1:
    st.subheader("Login to Your Dashboard")
    # Using columns to center the login form
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

    

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st

from beckend.auth import register_user, login_user, generate_token

st.title("Edu2job: Job Role Prediction System")

menu=["Register","Login"]
choice=st.sidebar.selectbox("Menu",menu)

if choice == "Register":
    st.subheader("Create New Account")
    new_user=st.text_input("Username")
    new_email=st.text_input("Email")
    new_password=st.text_input("Password", type='password')

    if st.button("Register"):
        if register_user(new_user,new_email,new_password):
            st.success("Account Created")
        else:
            st.error("Email already exists.")


elif choice == "Login":
    st.subheader("Login to Your Dashboard")
    email=st.text_input("Email")
    password=st.text_input("Password", type="password")


    if st.button("Login"):
        result=login_user(email,password)
        if result["status"]=="success":
            token=generate_token(result["id"],result["role"])
            st.session_state['token']=token
            st.session_state['user_id']=result["id"]
            st.session_state["user_name"]=result["name"]
            st.session_state["role"]=result["role"]

            if result["role"]=="admin":
                st.switch_page("pages/admin.py")
            else:
                st.switch_page("pages/dashboard.py")
            
        else:
            st.error("Invalid Email or Password")


st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

    

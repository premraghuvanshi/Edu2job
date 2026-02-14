import streamlit as st

if 'token' not in st.session_state:
    st.error("Please login first!")
    st.stop()

st.sidebar.title(f"Hi, {st.session_state['user_name']}")
menu=st.sidebar.radio("Navigation", ["Dashboard Home", "View Profile", "Logout"])

if menu == "Dashboard Home":
    st.title("User Dashboard")
    st.write("Welcome to the Edu2job Prediction System.")
elif menu ==  "View Profile":
    st.switch_page("pages/profile.py")
elif menu == "Logout":
    st.session_state.clear()
    st.success("Logged out successfully")
    st.switch_page("app.py")
    
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

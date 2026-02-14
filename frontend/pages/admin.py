import streamlit as st

if 'token' not in st.session_state:
    st.error("Please login first!")
    st.stop()
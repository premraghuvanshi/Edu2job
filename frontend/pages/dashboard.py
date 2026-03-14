import streamlit as st
import pickle
import pandas as pd
from beckend.preprocess import  predict , get_history


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
st.subheader("Industry Demand Analysis")
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

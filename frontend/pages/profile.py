import streamlit as st
from beckend.auth import get_user_profile, save_education
import pandas as pd

@st.cache_data
def get_dropdown_options():
    try:
        df = pd.read_csv('data/job_dataset.csv')
        degrees_list = sorted(df['Degree'].unique().tolist())
        specs_list = sorted(df['Specialization'].unique().tolist())
        return degrees_list, specs_list
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        return ["B.Tech", "MCA"], ["Data Science", "AIML"]

degrees_options, specs_options = get_dropdown_options()

if 'token' not in st.session_state:
    st.error("Access Denied")
    if st.button("Return to Login"):
        st.switch_page('app.py')
    st.stop()

user_id = st.session_state['user_id']
user_data= get_user_profile(user_id)

st.title("My Professional Profile")

if user_data:
    name, email, deg, spec, cgpa, certs, year = user_data

   
    tab1, tab2 = st.tabs([" View Profile", " Edit Details"])

    with tab1:
        
        with st.container(border=True):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.write("### Basic Info")
                st.write(f"**Name:** {name}")
                st.write(f"**Email:** {email}")
            with col2:
                
                m_col1, m_col2 = st.columns(2)
                m_col1.metric("CGPA", f"{cgpa}/10")
                m_col2.metric("Batch", int(year) if year else "N/A")

        st.subheader(" Education Details")
        if deg:
            with st.container(border=True):
                c1, c2 = st.columns(2)
                c1.write(f"**Degree:** {deg}")
                c2.write(f"**Specialization:** {spec}")
                
                st.divider()
                st.write(f"Certificates: {certs if certs else 'No professional certifications listed.'}")
        else:
            st.info("Your education profile is incomplete. Please switch to the 'Edit Details' tab.")

    with tab2:
        st.subheader("Update Academic Information")
        with st.form("update_profile_form", border=True):
            f_col1, f_col2 = st.columns(2)
            
            default_deg_idx = degrees_options.index(deg) if deg in degrees_options else 0
            new_deg = f_col1.selectbox("Current Degree", degrees_options, index=default_deg_idx)
            
            default_spec_idx = specs_options.index(spec) if spec in specs_options else 0
            new_spec = f_col2.selectbox("Specialization", specs_options, index=default_spec_idx)

            new_cgpa = f_col1.number_input("Current CGPA", min_value=0.0, max_value=10.0, step=0.01, value=float(cgpa) if cgpa else 0.0)
            new_year = f_col2.number_input("Year of Completion", min_value=2020, max_value=2031, step=1, value=int(year) if year else 2024)

            new_certs = st.text_area("Certifications (Comma separated)", value=certs if certs else "", help="List your NPTEL, Coursera, or Industry certs")

           
            _, btn_col, _ = st.columns([1, 1, 1])
            if btn_col.form_submit_button(" Save Profile Updates", use_container_width=True):
                if new_spec and new_cgpa > 0:
                    success = save_education(user_id, new_deg, new_spec, new_cgpa, new_year, new_certs)
                    if success:
                        st.success("Success! Your profile has been updated.")
                        st.rerun()
                    else:
                        st.error("Database error: Could not save changes.")
                else:
                    st.warning("Please enter a valid Specialization and CGPA.")

if st.sidebar.button("Back to Dashboard", use_container_width=True):
    st.switch_page("pages/dashboard.py")
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

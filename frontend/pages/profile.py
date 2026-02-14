import streamlit as st
from beckend.auth import get_user_profile, save_education

if 'token' not in st.session_state:
    st.error("Access Denied")
    st.stop()

user_id = st.session_state['user_id']
user_data= get_user_profile(user_id)

st.title("User Profile")

if user_data:
    name, email, deg, spec, cgpa, certs = user_data

    st.subheader("Personal Information")
    st.write(f"**Name:**{name}")
    st .write(f"**Email:**{email}")

    st.markdown("---")

    st.subheader("Education Background")
    if deg :
        st.write(f"**Degree:**{deg}")
        st.write(f"**Specialization:**{spec}")
        st.write(f"**CGPA:**{cgpa}")
        st.write(f"**Certificates:**{certs if certs else "None listed"}")
    else:
        st.info("NO education details found.")

    st.markdown("---")

    with st.expander("Update Education Details"):
        with st.form("update_profile_form"):
            new_deg=st.selectbox("Degree",["B.Tech", "BCA", "M.Tech", "MCA" ],
                                 index=["B.Tech", "BCA", "M.Tech", "MCA" ].index(deg) if deg else 0)
            
            new_spec=st.text_input("Specialization", value=spec if spec else "")

            new_cgpa=st.number_input("CGPA",min_value=0.0,max_value=10.0, step=0.01, value=float(cgpa) if cgpa else 0.0)

            new_certs=st.text_input("Certificates(Optional)", value=certs if certs else "")

            if st.form_submit_button("Save Changes"):
                if new_spec and new_cgpa>0:
                    success=save_education(user_id, new_deg, new_spec, new_cgpa, new_certs)
                    if success:
                        st.success("Profile updated")
                        st.rerun()
                    else:
                        st.error("Failed to update profile.")
                else:
                    st.warning("Please fill in the required fields")
if st.button("Back to Dashboard"):
    st.switch_page("pages/dashboard.py")


st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

import streamlit as st
from beckend.auth import get_user_profile, save_education
import pandas as pd
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
    name, email, deg, spec, cgpa, skills, year ,linkedin, certs = user_data

   
    tab1, tab2 = st.tabs([" View Profile", " Edit Details"])

    with tab1:
        
        with st.container(border=True):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.write("### Basic Info")
                st.write(f"**Name:** {name}")
                st.write(f"**Email:** {email}")
                if linkedin:
                    st.link_button("LinkedIn Profile", linkedin)
            with col2:
                
                m_col1, m_col2 = st.columns(2)
                m_col1.metric("CGPA", f"{cgpa}/10")
                m_col2.metric("Batch", int(year) if year else "N/A")

        st.subheader(" Education Details")
        st.subheader("Academic & Skills")
        with st.container(border=True):
            st.write(f"**Degree:** {deg} in {spec}")
            st.divider()
            st.write(f"**Skills:** {skills if skills else 'No skills listed yet.'}")
            st.write(f"**Certificates:** {certs if certs else 'No certificates listed.'}")

    with tab2:
        st.subheader("Update Professional Details")
        
        # --- Resume Section ---
        with st.expander("📄 Auto-update from Resume", expanded=False):
            uploaded_file = st.file_uploader("Upload PDF Resume to extract skills", type="pdf")
            if uploaded_file:
                # Mock extraction logic for your portfolio
                st.info("Simulating Skill Extraction...")
                extracted_skills = "Python, SQL, Machine Learning, Streamlit" # You can integrate PyPDF2 here
                st.success(f"Extracted: {extracted_skills}")

        with st.form("update_profile_form", border=True):
            f_col1, f_col2 = st.columns(2)
            
            # Dropdowns
            default_deg_idx = degrees_options.index(deg) if deg in degrees_options else 0
            new_deg = f_col1.selectbox("Current Degree", degrees_options, index=default_deg_idx)
            
            default_spec_idx = specs_options.index(spec) if spec in specs_options else 0
            new_spec = f_col2.selectbox("Specialization", specs_options, index=default_spec_idx)

            # Socials & GPA
            new_linkedin = st.text_input("LinkedIn Profile URL", value=linkedin if linkedin else "")
            new_cgpa = f_col1.number_input("Current CGPA", min_value=0.0, max_value=10.0, step=0.01, value=float(cgpa) if cgpa else 0.0)
            new_year = f_col2.number_input("Year of Completion", min_value=2020, max_value=2031, step=1, value=int(year) if year else 2024)

            # Skills and Certs
            new_skills = st.text_area("Skills (Comma separated)", value=skills if skills else "", help="e.g. Python, Java, SQL")
            new_certs = st.text_area("Certifications", value=certs if certs else "")

            if st.form_submit_button(" Save All Updates", use_container_width=True):
                success = save_education(user_id, new_deg, new_spec, new_cgpa, new_year, new_skills, new_linkedin, new_certs)
                if success:
                    st.success("Profile Updated!")
                    st.rerun()
                else:
                
                    st.warning("Please enter a valid details")

if st.sidebar.button("Back to Dashboard", use_container_width=True):
    st.switch_page("pages/dashboard.py")
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

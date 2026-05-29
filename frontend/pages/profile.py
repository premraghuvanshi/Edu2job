import streamlit as st
from beckend.auth import get_user_profile, save_education
import pandas as pd
from beckend.parser import extract_raw_text, parse_resume_via_gemini  # <-- NEW IMPORT

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
        # Load your sanitized dataset
        df = pd.read_csv('data/job_dataset.csv')
        
        degrees_list = sorted(df['Education Level'].dropna().unique().tolist())
        specs_list = sorted(df['Specialization'].dropna().unique().tolist())
        
        # Flattening Skills: Split by comma, strip whitespace, and get unique values
        all_skills = df['Skills'].dropna().str.split(',').explode().str.strip().unique()
        skill_list = sorted([s for s in all_skills if s]) # Remove empty strings
        
        # Flattening Certificates
        all_certs = df['Certifications'].dropna().str.split(',').explode().str.strip().unique()
        certs_list = sorted([c for c in all_certs if c])
        
        return degrees_list, specs_list, skill_list, certs_list
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        return ["B.Tech", "MCA"], ["AIML"], ["Python"], ["AWS"]

degrees_options, specs_options , skill_options, certificates_options = get_dropdown_options()

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
        
        # --- STATE INITIALIZATION FOR AI FORM UPDATES ---
        if "form_data" not in st.session_state:
            st.session_state["form_data"] = {
                "degree": deg, 
                "spec": spec, 
                "cgpa": float(cgpa) if cgpa else 0.0,
                "skills": [s.strip() for s in skills.split(',')] if skills else [],
                "certs": [c.strip() for c in certs.split(',')] if certs else []
            }

        # --- Resume Section ---
        with st.expander("📄 Auto-update from Resume", expanded=False):
            uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])
            
            if uploaded_file and st.button("Extract Data with AI"):
                with st.spinner("Analyzing and normalizing with Gemini..."):
                    raw_text = extract_raw_text(uploaded_file)
                    if raw_text:
                        # Pass dataset unique lists to the semantic AI parser
                        ai_data = parse_resume_via_gemini(
                            raw_text=raw_text,
                            allowed_degrees=degrees_options,
                            allowed_specs=specs_options,
                            allowed_skills=skill_options,
                            allowed_certs=certificates_options
                        )
                        
                        if ai_data:
                            # 1. Update numeric fields
                            st.session_state["form_data"]["cgpa"] = ai_data.get("cgpa", 0.0)
                            
                            # 2. Update categorical dropdowns safely
                            extracted_deg = ai_data.get("degree", "")
                            if extracted_deg in degrees_options:
                                st.session_state["form_data"]["degree"] = extracted_deg
                                
                            extracted_spec = ai_data.get("spec", "")
                            if extracted_spec in specs_options:
                                st.session_state["form_data"]["spec"] = extracted_spec
                            
                            # 3. Filter valid arrays and combine with existing profile data
                            valid_skills = [s for s in ai_data.get("skills", []) if s in skill_options]
                            valid_certs = [c for c in ai_data.get("certifications", []) if c in certificates_options]
                            
                            st.session_state["form_data"]["skills"] = list(set(st.session_state["form_data"]["skills"] + valid_skills))
                            st.session_state["form_data"]["certs"] = list(set(st.session_state["form_data"]["certs"] + valid_certs))
                            
                            st.success("Extraction Complete! Abbreviations mapped successfully. Form updated below.")
                        else:
                            st.error("AI failed to interpret data.")
                    else:
                        st.error("Could not read PDF text.")

        with st.form("update_profile_form", border=True):
            f_col1, f_col2 = st.columns(2)
            
            # Dropdowns reading strictly from session state
            current_deg = st.session_state["form_data"]["degree"]
            default_deg_idx = degrees_options.index(current_deg) if current_deg in degrees_options else 0
            new_deg = f_col1.selectbox("Current Degree", degrees_options, index=default_deg_idx)
            
            current_spec = st.session_state["form_data"]["spec"]
            default_spec_idx = specs_options.index(current_spec) if current_spec in specs_options else 0
            new_spec = f_col2.selectbox("Specialization", specs_options, index=default_spec_idx)

            # Socials & GPA
            new_linkedin = st.text_input("LinkedIn Profile URL", value=linkedin if linkedin else "")
            new_cgpa = f_col1.number_input("Current CGPA", min_value=0.0, max_value=10.0, step=0.01, value=st.session_state["form_data"]["cgpa"])
            new_year = f_col2.number_input("Year of Completion", min_value=2020, max_value=2031, step=1, value=int(year) if year else 2024)

            # Use multiselect for Skills and Certs (Defaulting to AI/DB State)
            selected_skills = st.multiselect(
                "Select Skills", 
                options=skill_options, 
                default=[s for s in st.session_state["form_data"]["skills"] if s in skill_options]
            )

            selected_certs = st.multiselect(
               "Select Certifications", 
               options=certificates_options, 
               default=[c for c in st.session_state["form_data"]["certs"] if c in certificates_options]
            )

            if st.form_submit_button(" Save All Updates", use_container_width=True):
                # Join the list back into a comma-separated string for the database
                final_skills_str = ", ".join(selected_skills)
                final_certs_str = ", ".join(selected_certs)
        
                success = save_education(
                   user_id, new_deg, new_spec, new_cgpa, new_year, 
                   final_skills_str, new_linkedin, final_certs_str
                )
                if success:
                   # Clear temporary form state upon successful DB write
                   del st.session_state["form_data"]
                   st.success("Profile Updated!")
                   st.rerun()
                else:
                   st.warning("Please enter valid details")

if st.sidebar.button("Back to Dashboard", use_container_width=True):
    st.switch_page("pages/dashboard.py")

st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)
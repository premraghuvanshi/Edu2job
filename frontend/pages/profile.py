import streamlit as st
import pandas as pd
from pathlib import Path

# Correct backend imports
from backend.auth import get_user_profile, save_education
from backend.parser import extract_raw_text, parse_resume_via_gemini

# ==========================================
# 1. CONFIGURATION & PATHS
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CSV_PATH = BASE_DIR / 'data' / 'job_dataset.csv'

# ==========================================
# 2. UI STYLING
# ==========================================
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

        /* 2. PREMIUM GLASS CONTAINER */
        [data-testid="stVerticalBlock"] > div:has(div.stTabs) {
            background: rgba(255, 255, 255, 0.02);
            backdrop-filter: blur(15px);
            border-radius: 24px;
            padding: 40px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
        }

        /* 3. SIDEBAR & METRICS */
        [data-testid="stSidebar"] {
            background-color: rgba(2, 6, 23, 0.9) !important;
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(16, 185, 129, 0.1);
        }
        [data-testid="stMetric"] {
            background: rgba(16, 185, 129, 0.05);
            border-left: 4px solid #10b981;
            padding: 20px !important;
            border-radius: 12px;
            transition: all 0.3s ease;
        }
        [data-testid="stMetric"]:hover {
            transform: translateX(5px);
            box-shadow: 0 0 15px rgba(16, 185, 129, 0.2);
        }

        /* 4. INPUTS */
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

        /* 5. BUTTONS */
        div.stButton > button {
            width: 100%;
            background: #020617 !important;
            color: #f8fafc !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            padding: 12px;
            border-radius: 12px;
            font-weight: bold;
            text-transform: uppercase;
            transition: all 0.3s ease;
        }
        div.stButton > button:hover {
            border-color: #10b981 !important;
            color: #10b981 !important;
            transform: translateY(-2px);
        }
        div.stButton > button[kind="primary"] {
            border: 1px solid rgba(16, 185, 129, 0.3) !important;
        }

        /* 6. TABS & HIDING NATIVE NAV */
        .stTabs [data-baseweb="tab-list"] { gap: 20px; }
        .stTabs [data-baseweb="tab"] { color: #94a3b8; font-weight: 600; }
        .stTabs [aria-selected="true"] { color: #10b981 !important; border-bottom-color: #10b981 !important; }
        [data-testid="stSidebarNav"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DATA PROCESSING
# ==========================================
@st.cache_data(show_spinner=False)
def get_dropdown_options(file_path: Path):
    try:
        if not file_path.exists():
            st.error("Dataset missing. Using fallback options.")
            return ["B.Tech", "MCA"], ["AIML", "Computer Science"], ["Python", "Java"], ["AWS", "Azure"]
            
        df = pd.read_csv(file_path)
        
        degrees_list = sorted(df['Education Level'].dropna().unique().tolist())
        specs_list = sorted(df['Specialization'].dropna().unique().tolist())
        
        all_skills = df['Skills'].dropna().str.split(',').explode().str.strip().unique()
        skill_list = sorted([s for s in all_skills if s]) 
        
        all_certs = df['Certifications'].dropna().str.split(',').explode().str.strip().unique()
        certs_list = sorted([c for c in all_certs if c])
        
        return degrees_list, specs_list, skill_list, certs_list
    except Exception as e:
        st.error(f"Error loading dropdown data: {e}")
        return ["B.Tech", "MCA"], ["AIML"], ["Python"], ["AWS"]

# ==========================================
# 4. MAIN APPLICATION LOGIC
# ==========================================
inject_ultra_premium_theme()

if 'user_id' not in st.session_state:
    st.error("Authentication required. Please log in.")
    if st.button("Return to Login"):
        st.switch_page('app.py')
    st.stop()

degrees_options, specs_options, skill_options, certificates_options = get_dropdown_options(CSV_PATH)

user_id = st.session_state['user_id']
user_data = get_user_profile(user_id)

st.title("My Professional Profile")

if user_data:
    # Safely unpack with defaults to prevent crashes for newly registered users with empty profiles
    name = user_data[0] or "Student"
    email = user_data[1] or ""
    deg = user_data[2] or ""
    spec = user_data[3] or ""
    cgpa = float(user_data[4]) if user_data[4] else 0.0
    skills = user_data[5] or ""
    year = int(user_data[6]) if user_data[6] else 2024
    linkedin = user_data[7] or ""
    certs = user_data[8] or ""

    tab1, tab2 = st.tabs(["👁️ View Profile", "✏️ Edit Details"])

    # --- TAB 1: VIEW PROFILE ---
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
                m_col1.metric("CGPA", f"{cgpa:.2f}/10")
                m_col2.metric("Batch", int(year))

        st.subheader("📚 Education & Skills")
        with st.container(border=True):
            st.write(f"**Degree:** {deg if deg else 'Not provided'} in {spec if spec else 'Not provided'}")
            st.divider()
            st.write(f"**Skills:** {skills if skills else 'No skills listed yet.'}")
            st.write(f"**Certificates:** {certs if certs else 'No certificates listed.'}")

    # --- TAB 2: EDIT PROFILE ---
    with tab2:
        st.subheader("Update Professional Details")
        
        # Safe State Initialization
        if "form_data" not in st.session_state:
            st.session_state["form_data"] = {
                "degree": deg if deg in degrees_options else (degrees_options[0] if degrees_options else ""), 
                "spec": spec if spec in specs_options else (specs_options[0] if specs_options else ""), 
                "cgpa": cgpa,
                "skills": [s.strip() for s in skills.split(',')] if skills else [],
                "certs": [c.strip() for c in certs.split(',')] if certs else []
            }

        # --- Resume Auto-Parser ---
        with st.expander("📄 Auto-update from Resume", expanded=False):
            uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])
            
            if uploaded_file and st.button("Extract Data with AI"):
                with st.spinner("Analyzing and normalizing with Gemini..."):
                    raw_text = extract_raw_text(uploaded_file)
                    if raw_text:
                        ai_data = parse_resume_via_gemini(
                            raw_text=raw_text,
                            allowed_degrees=degrees_options,
                            allowed_specs=specs_options,
                            allowed_skills=skill_options,
                            allowed_certs=certificates_options
                        )
                        
                        if ai_data:
                            # Safely map Gemini outputs back to form state
                            st.session_state["form_data"]["cgpa"] = float(ai_data.get("cgpa", 0.0))
                            
                            extracted_deg = ai_data.get("degree", "")
                            if extracted_deg in degrees_options:
                                st.session_state["form_data"]["degree"] = extracted_deg
                                
                            extracted_spec = ai_data.get("spec", "")
                            if extracted_spec in specs_options:
                                st.session_state["form_data"]["spec"] = extracted_spec
                            
                            valid_skills = [s for s in ai_data.get("skills", []) if s in skill_options]
                            valid_certs = [c for c in ai_data.get("certifications", []) if c in certificates_options]
                            
                            st.session_state["form_data"]["skills"] = list(set(st.session_state["form_data"]["skills"] + valid_skills))
                            st.session_state["form_data"]["certs"] = list(set(st.session_state["form_data"]["certs"] + valid_certs))
                            
                            st.success("Extraction Complete! Form populated below.")
                        else:
                            st.error("AI failed to interpret data.")
                    else:
                        st.error("Could not read document text.")

        # --- Manual Form Override ---
        with st.form("update_profile_form", border=True):
            f_col1, f_col2 = st.columns(2)
            
            current_deg = st.session_state["form_data"].get("degree")
            default_deg_idx = degrees_options.index(current_deg) if current_deg in degrees_options else 0
            new_deg = f_col1.selectbox("Current Degree", degrees_options, index=default_deg_idx)
            
            current_spec = st.session_state["form_data"].get("spec")
            default_spec_idx = specs_options.index(current_spec) if current_spec in specs_options else 0
            new_spec = f_col2.selectbox("Specialization", specs_options, index=default_spec_idx)

            new_linkedin = st.text_input("LinkedIn Profile URL", value=linkedin if linkedin else "")
            new_cgpa = f_col1.number_input("Current CGPA", min_value=0.0, max_value=10.0, step=0.01, value=float(st.session_state["form_data"].get("cgpa", 0.0)))
            new_year = f_col2.number_input("Year of Completion", min_value=2020, max_value=2031, step=1, value=int(year))

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

            if st.form_submit_button("💾 Save All Updates", width="stretch"):
                final_skills_str = ", ".join(selected_skills)
                final_certs_str = ", ".join(selected_certs)
        
                success = save_education(
                   user_id, new_deg, new_spec, new_cgpa, new_year, 
                   final_skills_str, new_linkedin, final_certs_str
                )
                if success:
                   if "form_data" in st.session_state:
                       del st.session_state["form_data"]
                   st.success("Profile Updated Successfully!")
                   st.rerun()
                else:
                   st.warning("Database write failed. Please check inputs.")

# ==========================================
# 5. NAVIGATION
# ==========================================
if st.sidebar.button("Back to Dashboard", width="stretch"):
    st.switch_page("pages/dashboard.py")
import pdfplumber
import json
import docx
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def extract_raw_text(uploaded_file):
    """Extracts raw text from PDF or DOCX files."""
    try:
        text = ""
        file_name = uploaded_file.name.lower()
        
        # Route 1: PDF Extraction
        if file_name.endswith('.pdf'):
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    text += (page.extract_text() or "") + "\n"
                    
        # Route 2: DOCX Extraction
        elif file_name.endswith('.docx'):
            doc = docx.Document(uploaded_file)
            for para in doc.paragraphs:
                text += para.text + "\n"
                
        else:
            print("Unsupported file format.")
            return None
            
        return text.strip()
        
    except Exception as e:
        print(f"File extraction failed: {e}")
        return None
    
def parse_resume_via_gemini(raw_text, allowed_degrees, allowed_specs, allowed_skills, allowed_certs):
    """Uses Gemini 2.5 Flash to semantically map resume text to exact CSV vocabularies."""
    client=genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    system_instruction=f"""
    You are a semantic data classifier and extraction engine. 
    
    CRITICAL CLASSIFICATION RULES:
    1. Hierarchical Mapping (Specialization/Branch): If the resume lists a sub-branch (e.g., 'AIML', 'Artificial Intelligence', 'Data Science', 'IT'), you MUST classify it under the closest parent category found in ALLOWED SPECIALIZATIONS (e.g., map it to 'Computer Science').
    2. Skill Normalization: If a skill contains descriptive fluff (e.g., 'Python Programming', 'Advanced Java', 'Building Machine Learning Models'), strip the fluff and map it exactly to the core skill in ALLOWED SKILLS (e.g., 'Python', 'Java', 'Machine Learning').
    3. Degree Normalization: Map variations (B.Tech, B.E., BSc) to the closest allowed tier in ALLOWED DEGREES (e.g., 'Bachelor\\'s').
    4. Exact Output ONLY: Every string you output MUST be an exact, character-for-character match to a string in the ALLOWED lists. If a concept absolutely cannot map to the provided lists, ignore it.
    
    ALLOWED DEGREES: {allowed_degrees}
    ALLOWED SPECIALIZATIONS: {allowed_specs}
    ALLOWED SKILLS: {allowed_skills}
    ALLOWED CERTIFICATIONS: {allowed_certs}
    
    Schema:
    {{
        "cgpa": float (Convert percentages to 10.0 scale. Default 0.0),
        "degree": string (Exact match from ALLOWED DEGREES),
        "spec": string (Exact match from ALLOWED SPECIALIZATIONS),
        "skills": list of strings (Exact matches from ALLOWED SKILLS),
        "certifications": list of strings (Exact matches from ALLOWED CERTIFICATIONS)
    }}
    """

    try :
        response=client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Extract and classify from this resume: \n\n{raw_text}",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                temperature=0.0

            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"API Error: {e}")
        return None
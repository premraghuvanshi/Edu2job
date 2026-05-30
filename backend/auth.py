import sqlite3
import bcrypt
import jwt
import os
import json
import urllib.parse
import requests as http_requests
from datetime import datetime, timedelta, timezone
from google.oauth2 import id_token
from google.auth.transport import requests
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# 1. CONFIGURATION & CONSTANTS
# ==========================================
db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'storage.db')

REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8501")
SUPER_KEY = os.getenv("SUPER_KEY")

SCOPES = [
    "openid", 
    "https://www.googleapis.com/auth/userinfo.email", 
    "https://www.googleapis.com/auth/userinfo.profile"
]

# ==========================================
# 2. CORE AUTHENTICATION
# ==========================================
def register_user(name, email, password):
    email = email.strip().lower()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        cursor.execute('''
            INSERT INTO USER(name , email , password_hash, role)
            VALUES(?,?,?,?)
        ''', (name, email, hashed_pw, 'user'))
        conn.commit()
        return True 
    except sqlite3.IntegrityError:
        print("Email already exists.")
        return False
    finally:
        conn.close()
    
def login_user(email, ent_password):
    email = email.strip().lower()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT password_hash, role, user_id , name FROM USER WHERE email=?', (email,))
    result = cursor.fetchone()
    conn.close()

    if result:
        stored_hash = result[0]
        user_role = result[1]
        user_id = result[2]
        user_name = result[3]
        
        if isinstance(stored_hash, str):
            if stored_hash.startswith("b'") and stored_hash.endswith("'"):
                stored_hash = stored_hash[2:-1]
            stored_bytes = stored_hash.encode('utf-8')
        else:
            stored_bytes = stored_hash

        if bcrypt.checkpw(ent_password.encode('utf-8'), stored_bytes):
            return {'status': "success", 'role': user_role, "id": user_id, "name": user_name}
        else:
            return {"status": "fail"}
    else:
        return {"status": "fail"}
    
def generate_token(user_id, role):
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.now(timezone.utc) + timedelta(hours=24)
    }
    token = jwt.encode(payload, SUPER_KEY, algorithm="HS256")
    return token

def reset_password(email, old_password, new_password):
    email = email.strip().lower()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT password_hash FROM USER WHERE email=?', (email,))
        result = cursor.fetchone()
        
        if not result:
            return {"status": "error", "message": "User not found"}
            
        stored_hash = result[0]
        stored_bytes = stored_hash.encode('utf-8') if isinstance(stored_hash, str) else stored_hash
        
        if not bcrypt.checkpw(old_password.encode('utf-8'), stored_bytes):
            return {"status": "error", "message": "Incorrect current password"}

        new_hashed_pw = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        cursor.execute('UPDATE USER SET password_hash=? WHERE email=?', (new_hashed_pw, email))
        conn.commit()
        return {"status": "success", "message": "Password updated successfully!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

# ==========================================
# 3. DATABASE PROFILE OPERATIONS
# ==========================================
def get_user_profile(user_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT u.name, u.email, e.degree, e.specialization, e.cgpa, 
                   e.skills, e.year_of_comp, e.linkedin, e.certificates
            FROM USER u
            LEFT JOIN EDUCATION e ON u.user_id = e.user_id
            WHERE u.user_id=?
        ''', (user_id,))
        result = cursor.fetchone()
        return result
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()

def save_education(user_id, degree, specialization, cgpa, year, skills, linkedin, certificates):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM EDUCATION WHERE user_id=?", (user_id,))
        exists = cursor.fetchone()

        if exists:
            cursor.execute('''
                UPDATE EDUCATION
                SET degree=?, specialization=?, cgpa=?, year_of_comp=?, skills=?, linkedin=?, certificates=?
                WHERE user_id=?          
            ''', (degree, specialization, cgpa, year, skills, linkedin, certificates, user_id))
        else:
            cursor.execute("""
                INSERT INTO EDUCATION (user_id, degree, specialization, cgpa, skills, linkedin, certificates, year_of_comp)
                VALUES (?,?,?,?,?,?,?,?)          
            """, (user_id, degree, specialization, cgpa, skills, linkedin, certificates, year))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error saving education: {e}")
        return False
    finally:
        conn.close()

# ==========================================
# 4. GOOGLE OAUTH INTEGRATION (BULLETPROOF STATELESS FIX)
# ==========================================
def get_google_auth_url():
    secret_json = os.getenv("GOOGLE_CLIENT_SECRET_JSON")
    if not secret_json:
        raise ValueError("Missing GOOGLE_CLIENT_SECRET_JSON in environment variables.")
        
    secret_dict = json.loads(secret_json)
    client_config = secret_dict.get("web") or secret_dict.get("installed")
    
    if not client_config:
        raise ValueError("Invalid JSON format. Expected 'web' or 'installed' key.")
    
    params = {
        "client_id": client_config.get("client_id"),
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent"
    }
    
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    return url

def verify_google_token(code):
    secret_json = os.getenv("GOOGLE_CLIENT_SECRET_JSON")
    if not secret_json:
        raise ValueError("Missing GOOGLE_CLIENT_SECRET_JSON in environment variables.")
        
    secret_dict = json.loads(secret_json)
    client_config = secret_dict.get("web") or secret_dict.get("installed")
    
    token_url = client_config.get("token_uri", "https://oauth2.googleapis.com/token")
    data = {
        "code": code,
        "client_id": client_config.get("client_id"),
        "client_secret": client_config.get("client_secret"),
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    
    response = http_requests.post(token_url, data=data)
    response_data = response.json()
    
    if "error" in response_data:
        err_msg = response_data.get('error_description', response_data.get('error'))
        raise ValueError(f"OAuth Exchange Failed: {err_msg}")
        
    user_info = id_token.verify_oauth2_token(
        response_data["id_token"], 
        requests.Request(), 
        client_config["client_id"],
        clock_skew_in_seconds=10  
    )
    return user_info

def get_or_create_google_user(email, name):
    email = email.strip().lower()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_id, role FROM USER WHERE email=?", (email,))
    user = cursor.fetchone()
    
    if not user:
        cursor.execute(
            "INSERT INTO USER (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
            (name, email, 'GOOGLE_AUTH', 'user')
        )
        conn.commit()
        cursor.execute("SELECT user_id, role FROM USER WHERE email=?", (email,))
        user = cursor.fetchone()
    
    conn.close()
    return user[0], user[1]
import sqlite3
import bcrypt
import jwt
import os
from datetime import datetime, timedelta, timezone
from google.oauth2 import id_token
from google.auth.transport import requests
from google_auth_oauthlib.flow import Flow
from dotenv import load_dotenv

load_dotenv()
SUPER_KEY=os.getenv("SUPER_KEY")


def register_user(name , email , password):
    email = email.strip()
    conn=sqlite3.connect('data/storage.db')
    cursor=conn.cursor()
    try:
        hashed_pw=bcrypt.hashpw(password.encode("utf-8"),bcrypt.gensalt())

        cursor.execute('''
            INSERT INTO USER(name , email , password_hash, role)
            VALUES(?,?,?,?)
        ''', (name , email, hashed_pw, 'user'))
        conn.commit()
        print(f"User Register successfully")
        return True 
    except sqlite3.IntegrityError:
        print("Email already exists.")
        return False
    finally:
        conn.close()
    
def login_user(email, ent_password):
    email = email.strip()
    conn=sqlite3.connect("data/storage.db")
    cursor=conn.cursor()
    
    cursor.execute('SELECT password_hash, role, user_id , name FROM USER WHERE email=?',(email,))
    result=cursor.fetchone()
    conn.close()

    if result:
        stored_hash=result[0]
        user_role=result[1]
        user_id=result[2]
        user_name=result[3]
        

        if bcrypt.checkpw(ent_password.encode('utf-8'), stored_hash if isinstance(stored_hash, bytes) else stored_hash.encode('utf-8')):
            print("Login Successful!")
            return {'status': "success", 'role':user_role , "id": user_id,"name":user_name}
        else:
            print("Invalid Password")
            return {"status": "fail"}
    
    else:
        print("User not found")
        return{"status":"fail"}
    

def generate_token(user_id,role):
    payload={
        'user_id':user_id,
        'role':role,
        'exp': datetime.now(timezone.utc) + timedelta(hours=24)

    }
    token=jwt.encode(payload,SUPER_KEY,algorithm="HS256")
    return token

def get_user_profile(user_id):
    conn=sqlite3.connect("data/storage.db")
    cursor=conn.cursor()

    try:

        cursor.execute('''
        SELECT u.name, u.email, e.degree, e.specialization, e.cgpa, 
               e.skills, e.year_of_comp, e.linkedin, e.certificates
        FROM USER u
        LEFT JOIN EDUCATION e ON u.user_id = e.user_id
        WHERE u.user_id=?
    ''',(user_id,))

        result=cursor.fetchone()
        return result
    except sqlite3.Error as e:
        print(f"Database error:{e}")
        return None
    finally:
        conn.close()



def save_education(user_id, degree, specialization, cgpa, year, skills, linkedin, certificates):
    conn = sqlite3.connect("data/storage.db")
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


# This variable must match the filename you just saved
CLIENT_SECRETS_FILE = "client_secret.json"

# Define the data permissions we are requesting
SCOPES = [
    "openid", 
    "https://www.googleapis.com/auth/userinfo.email", 
    "https://www.googleapis.com/auth/userinfo.profile"
]

def get_google_auth_url():
    """Reads the JSON file and generates the Google Login URL."""
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri="http://localhost:8501" # Must match Google Console exactly
    )
    # prompt='consent' ensures the user sees the select account screen every time
    auth_url, _ = flow.authorization_url(prompt='consent')
    return auth_url


def verify_google_token(code):
    """Exchanges the authorization code for user profile data."""
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri="http://localhost:8501"
    )
    # Exchange the 'code' from the URL for actual credentials
    flow.fetch_token(code=code)
    credentials = flow.credentials
    # Add clock_skew_in_seconds to allow a 10-second difference
    user_info = id_token.verify_oauth2_token(
        credentials.id_token, 
        requests.Request(), 
        credentials.client_id,
        clock_skew_in_seconds=10  
    )
    
    # Verify the identity token provided by Google
   
    return user_info  # This dictionary contains 'email' and 'name'




def get_or_create_google_user(email, name):
   
    
    conn = sqlite3.connect('data/storage.db')
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
    return user[0], user[1]  # Returns (user_id, role)




def reset_password(email, new_password):
    email = email.strip()
    conn = sqlite3.connect("data/storage.db")
    cursor = conn.cursor()
    
    try:
        # 1. Check if user exists
        cursor.execute('SELECT 1 FROM USER WHERE email=?', (email,))
        if not cursor.fetchone():
            return {"status": "error", "message": "User not found"}

        # 2. Hash the new password
        hashed_pw = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())

        # 3. Update the database
        cursor.execute('UPDATE USER SET password_hash=? WHERE email=?', (hashed_pw, email))
        conn.commit()
        return {"status": "success", "message": "Password updated successfully!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()
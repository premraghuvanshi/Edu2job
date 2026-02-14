import sqlite3
import bcrypt

import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY="Prem@123-Project-Edu2job"


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
    token=jwt.encode(payload,SECRET_KEY,algorithm="HS256")
    return token

def get_user_profile(user_id):
    conn=sqlite3.connect("data/storage.db")
    cursor=conn.cursor()

    try:

        cursor.execute('''
            SELECT u.name, u.email, e.degree, e.specialization, e.cgpa, e.certificates , e.year_of_comp
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



def save_education(user_id, degree, specialization, cgpa, year, certificates="",):
    conn=sqlite3.connect("data/storage.db")
    cursor=conn.cursor()

    try:
        cursor.execute("SELECT 1 FROM EDUCATION WHERE user_id=?", (user_id,))
        exists=cursor.fetchone()

        if exists:
            cursor.execute('''
                UPDATE EDUCATION
                SET degree=?, specialization=?, cgpa=?, year_of_comp=? , certificates=?
                WHERE user_id=?          
            ''',(degree, specialization, cgpa, year ,certificates,  user_id))
        else:
            cursor.execute("""
                INSERT INTO EDUCATION (user_id, degree, specialization, cgpa, certificates ,year_of_comp )
                VALUES (?,?,?,?,?,?)          
            """, (user_id, degree, specialization, cgpa, certificates, year))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error saving education:{e}")
        return False
    finally:
        conn.close()

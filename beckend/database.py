import sqlite3


def create_db():
    conn=sqlite3.connect('data/storage.db')
    cursor=conn.cursor()


    cursor.execute('''
        CREATE TABLE IF NOT EXISTS USER (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,     
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user'
                                   
        )
    ''')


    cursor.execute('''
        CREATE TABLE IF NOT EXISTS EDUCATION(
            education_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            degree TEXT NOT NULL,
            specialization TEXT NOT NULL,
            CGPA REAL NOT NULL,
            certificates TEXT,
            FOREIGN KEY (user_id) REFERENCES USER (user_id)
        )
    ''')
    

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS PREDICTIONHISTORY (
            prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            predicted_roles TEXT NOT NULL,
            confidence_scores REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES USER (user_id) 
        )
    ''')
    conn.commit()
    conn.close()
    print("Database created successfully")
if __name__ == "__main__":
    create_db()
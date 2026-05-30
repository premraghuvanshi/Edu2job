# import sqlite3


# def create_db():
#     conn=sqlite3.connect('data/storage.db')
#     cursor=conn.cursor()


#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS USER (
#             user_id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL,
#             email TEXT UNIQUE NOT NULL,     
#             password_hash TEXT NOT NULL,
#             role TEXT DEFAULT 'user'
                                   
#         )
#     ''')


#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS EDUCATION(
#             education_id INTEGER PRIMARY KEY AUTOINCREMENT,
#             user_id INTEGER NOT NULL,
#             degree TEXT NOT NULL,
#             specialization TEXT NOT NULL,
#             CGPA REAL NOT NULL,
#             certificates TEXT,
#             year_of_comp REAL NOT NULL,
#             FOREIGN KEY (user_id) REFERENCES USER (user_id)
#         )
#     ''')
    

#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS PREDICTIONHISTORY (
#             prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
#             user_id INTEGER NOT NULL,
#             predicted_roles TEXT NOT NULL,
#             confidence_scores REAL NOT NULL,
#             timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
#             FOREIGN KEY (user_id) REFERENCES USER (user_id) 
#         )
#     ''')
#     conn.commit()
#     conn.close()
#     print("Database created successfully")
# if __name__ == "__main__":
#     create_db()

# import pandas as pd
# import numpy as np
# import random

# # 1. 15 Degrees & 30 Specializations (Tech & Non-Tech)
# degrees = ["B.Tech", "M.Tech", "B.E.", "M.E.", "BCA", "MCA", "B.Sc", "M.Sc", "B.Voc", "Diploma", "BBA", "MBA", "B.Com", "M.Com", "B.A."]
# tech_specs = ["Artificial Intelligence", "Machine Learning", "Data Science", "Cyber Security", "Cloud Computing", "Full Stack Dev", "Mobile App Dev", "DevOps", "Software Testing", "Blockchain", "Data Analytics", "Network Security", "Embedded Systems", "IoT Systems", "Big Data"]
# non_tech_specs = ["Digital Marketing", "Human Resources", "Finance", "Sales", "Operations", "Business Analytics", "Supply Chain", "Project Management", "UI/UX Design", "Content Strategy", "Product Management", "Corporate Law", "Accounting", "Public Relations", "Customer Success"]
# all_specs = tech_specs + non_tech_specs

# data = []

# # 2. GENERATION LOGIC WITH CGPA TIERING
# for _ in range(5000):
#     deg = random.choice(degrees)
#     spec = random.choice(all_specs)
#     cgpa = round(random.uniform(5.0, 10.0), 2)
#     year = random.randint(2024, 2027)
    
#     spec_idx = all_specs.index(spec)
#     is_tech = spec_idx < 15

#     # Determine CGPA Class
#     if cgpa < 6:
#         tier = "Support"
#     elif 6 <= cgpa < 7:
#         tier = "Junior"
#     elif 7 <= cgpa < 8.5:
#         tier = "Core"
#     else: # cgpa >= 8.5
#         tier = "Elite"

#     # 3. MAPPING TO 50 ROLES
#     # Logic: Spec defines the domain, Tier defines the seniority
#     if is_tech:
#         if tier == "Support": role = f"Tech Support {spec[:5]}"
#         elif tier == "Junior": role = f"Junior {spec} Engineer"
#         elif tier == "Core": role = f"{spec} Specialist"
#         else: role = f"Senior {spec} Architect"
#     else:
#         if tier == "Support": role = f"Operations Asst ({spec[:5]})"
#         elif tier == "Junior": role = f"Junior {spec} Associate"
#         elif tier == "Core": role = f"{spec} Manager"
#         else: role = f"Strategic {spec} Lead"

#     data.append([deg, spec, cgpa, year, role])

# # 4. SAVE AND VERIFY
# df = pd.DataFrame(data, columns=['Degree', 'Specialization', 'CGPA', 'YearOfCompletion', 'JobRole'])

# # Ensure we hit exactly 50 unique roles (Truncate/Cap if necessary)
# unique_roles = df['JobRole'].unique()
# if len(unique_roles) > 50:
#     # Map excess roles to the top 50 to maintain consistency
#     role_map = {role: unique_roles[i % 50] for i, role in enumerate(unique_roles)}
#     df['JobRole'] = df['JobRole'].map(role_map)

# df.to_csv('data/job_dataset.csv', index=False)
# print(f"✅ Created tiered dataset with {df['JobRole'].nunique()} unique roles.")



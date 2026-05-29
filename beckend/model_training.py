import pandas as pd
import numpy as np
import pickle
import os
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score

# 1. Helper function for text processing (Must be top-level for pickle)
def career_tokenizer(text):
    if pd.isna(text) or str(text).strip() == "": 
        return []
    # Splits by comma and cleans up whitespace
    return [s.strip().lower() for s in str(text).split(',')]

def train_career_model(csv_path='data/job_dataset.csv'):
    """
    Trains the career prediction model using XGBoost.
    Returns: float (accuracy) on success, None on failure.
    """
    # Ensure backend directory exists
    if not os.path.exists('beckend'):
        os.makedirs('beckend')

    # 2. Robust Path Handling
    # If the provided path doesn't exist, try to check the root directory as a fallback
    if not os.path.exists(csv_path):
        fallback_path = os.path.basename(csv_path)
        if os.path.exists(fallback_path):
            csv_path = fallback_path
        else:
            print(f"Error: Dataset file not found at {csv_path} or {fallback_path}")
            return None 
    
    try:
        df = pd.read_csv(csv_path)
        
        if df.empty:
            print("Error: The provided dataset is empty.")
            return None

        print(f"Training on {len(df)} rows using CountVectorizers...")

        # 3. Process Education Level (Ordinal Mapping)
        # Normalize column names to handle variations in CSV headers
        df.columns = [c.title() if c.lower() != 'cgpa' else 'CGPA' for c in df.columns]
        
        edu_map = {
            'Matric': 1, 
            'High School': 2, 
            'Intermediate': 2, 
            "Bachelor's": 3, 
            "Master's": 4, 
            'PhD': 5
        }
        
        # Ensure 'Education Level' column exists
        if 'Education Level' not in df.columns:
            edu_cols = [c for c in df.columns if 'edu' in c.lower()]
            if edu_cols:
                df.rename(columns={edu_cols[0]: 'Education Level'}, inplace=True)
            else:
                print("Error: 'Education Level' column missing from dataset.")
                return None

        df['Edu_Rank'] = df['Education Level'].map(edu_map).fillna(0)

        # 4. Process Specialization (Label Encoding)
        spec_le = LabelEncoder()
        df['Spec_ID'] = spec_le.fit_transform(df['Specialization'].astype(str))

        # 5. Process Skills & Certifications (Count Vectorization - Binary)
        skill_vec = CountVectorizer(tokenizer=career_tokenizer, token_pattern=None, binary=True)
        cert_vec = CountVectorizer(tokenizer=career_tokenizer, token_pattern=None, binary=True)

        X_skills = skill_vec.fit_transform(df['Skills'].astype(str)).toarray()
        X_certs = cert_vec.fit_transform(df['Certifications'].astype(str)).toarray()

        # 6. Process Numeric Features (CGPA and Edu_Rank)
        scaler = StandardScaler()
        # Convert CGPA to numeric to prevent scaling errors
        df['CGPA'] = pd.to_numeric(df['CGPA'], errors='coerce').fillna(0)
        X_num = scaler.fit_transform(df[['CGPA', 'Edu_Rank']])

        # 7. Process Target
        target_le = LabelEncoder()
        y = target_le.fit_transform(df['Recommended Career'].astype(str))

        # 8. Combine All Features
        # Order: [Numeric, Specialization, Skills, Certifications]
        X_spec = df[['Spec_ID']].values
        X_combined = np.hstack((X_num, X_spec, X_skills, X_certs))

        # 9. Split and Train
        X_train, X_test, y_train, y_test = train_test_split(
            X_combined, y, test_size=0.30, random_state=42, stratify=y
        )

        model = XGBClassifier(
            n_estimators=500,
            learning_rate=0.05,
            max_depth=6,
            gamma=0.1,
            objective='multi:softprob',
            random_state=42,
            n_jobs=-1
        )
        
        print("Fitting model...")
        model.fit(X_train, y_train)

        # 10. Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Final Test Accuracy: {accuracy * 100:.2f}%")

        # 11. Save all objects for prediction
        with open('beckend/job_model_v5.pkl', 'wb') as f:
            pickle.dump({
                'model': model,
                'edu_map': edu_map,
                'spec_le': spec_le,
                'skill_vec': skill_vec,
                'cert_vec': cert_vec,
                'scaler': scaler,
                'target_le': target_le
            }, f)
        
        print("Success: High-accuracy model saved at beckend/job_model_v5.pkl")
        
        # CRITICAL: Return the accuracy value to the Admin Panel (frontend)
        return float(accuracy)

    except Exception as e:
        print(f"Internal Training Error: {e}")
        return None

if __name__ == "__main__":
    train_career_model()
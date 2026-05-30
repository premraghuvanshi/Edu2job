import pandas as pd
import numpy as np
import pickle
import logging
from pathlib import Path
from typing import Optional
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score

# CRITICAL FIX: Import tokenizer from an isolated utils file to ensure stable unpickling
from backend.utils import career_tokenizer

# ==========================================
# 1. CONFIGURATION & LOGGING
# ==========================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Dynamically resolve absolute paths to prevent cloud deployment crashes
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CSV_PATH = BASE_DIR / 'data' / 'job_dataset.csv'
MODEL_SAVE_DIR = BASE_DIR / 'backend'
MODEL_SAVE_PATH = MODEL_SAVE_DIR / 'job_model_v5.pkl'

# ==========================================
# 2. TRAINING PIPELINE
# ==========================================
def train_career_model(csv_path: Optional[str] = None) -> Optional[float]:
    """
    Trains the XGBoost career prediction model and serializes the pipeline assets.
    
    Args:
        csv_path (str, optional): Custom path to training data. Defaults to data/job_dataset.csv.
        
    Returns:
        Optional[float]: The test accuracy score on success, or None on failure.
    """
    dataset_path = Path(csv_path) if csv_path else DEFAULT_CSV_PATH
    
    # 1. Validate Environment & Data
    if not dataset_path.exists():
        logger.error(f"Dataset file not found at: {dataset_path}")
        return None 
    
    MODEL_SAVE_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        df = pd.read_csv(dataset_path)
        if df.empty:
            logger.error("The provided dataset is empty.")
            return None

        logger.info(f"Initiating training pipeline on {len(df)} records...")

        # 2. Normalize Schema
        df.columns = [c.title() if c.lower() != 'cgpa' else 'CGPA' for c in df.columns]
        
        if 'Education Level' not in df.columns:
            edu_cols = [c for c in df.columns if 'edu' in c.lower()]
            if edu_cols:
                df.rename(columns={edu_cols[0]: 'Education Level'}, inplace=True)
            else:
                logger.error("'Education Level' column missing from dataset schema.")
                return None

        # 3. Process Education (Ordinal Encoding)
        edu_map = {
            'Matric': 1, 
            'High School': 2, 
            'Intermediate': 2, 
            "Bachelor's": 3, 
            "Master's": 4, 
            'PhD': 5
        }
        df['Edu_Rank'] = df['Education Level'].map(edu_map).fillna(0)

        # 4. Process Specialization (Label Encoding)
        spec_le = LabelEncoder()
        df['Spec_ID'] = spec_le.fit_transform(df['Specialization'].astype(str))

        # 5. Process Text Features (Count Vectorization)
        skill_vec = CountVectorizer(tokenizer=career_tokenizer, token_pattern=None, binary=True)
        cert_vec = CountVectorizer(tokenizer=career_tokenizer, token_pattern=None, binary=True)

        X_skills = skill_vec.fit_transform(df['Skills'].astype(str)).toarray()
        X_certs = cert_vec.fit_transform(df['Certifications'].astype(str)).toarray()

        # 6. Process Numeric Features
        scaler = StandardScaler()
        df['CGPA'] = pd.to_numeric(df['CGPA'], errors='coerce').fillna(0)
        X_num = scaler.fit_transform(df[['CGPA', 'Edu_Rank']])

        # 7. Process Target Labels
        target_le = LabelEncoder()
        y = target_le.fit_transform(df['Recommended Career'].astype(str))

        # 8. Matrix Assembly
        X_spec = df[['Spec_ID']].values
        X_combined = np.hstack((X_num, X_spec, X_skills, X_certs))

        # 9. Train/Test Split
        X_train, X_test, y_train, y_test = train_test_split(
            X_combined, y, test_size=0.30, random_state=42, stratify=y
        )

        # 10. Model Initialization & Training
        model = XGBClassifier(
            n_estimators=500,
            learning_rate=0.05,
            max_depth=6,
            gamma=0.1,
            objective='multi:softprob',
            random_state=42,
            n_jobs=-1
        )
        
        logger.info("Fitting XGBoost Classifier...")
        model.fit(X_train, y_train)

        # 11. Evaluation
        y_pred = model.predict(X_test)
        accuracy = float(accuracy_score(y_test, y_pred))
        logger.info(f"Model Training Complete. Test Accuracy: {accuracy * 100:.2f}%")

        # 12. Serialization
        pipeline_assets = {
            'model': model,
            'edu_map': edu_map,
            'spec_le': spec_le,
            'skill_vec': skill_vec,
            'cert_vec': cert_vec,
            'scaler': scaler,
            'target_le': target_le
        }
        
        with open(MODEL_SAVE_PATH, 'wb') as f:
            pickle.dump(pipeline_assets, f)
            
        logger.info(f"Pipeline assets successfully serialized to {MODEL_SAVE_PATH}")
        return accuracy

    except Exception as e:
        logger.error(f"Critical Failure in Training Pipeline: {str(e)}", exc_info=True)
        return None

if __name__ == "__main__":
    train_career_model()
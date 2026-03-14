import pandas as pd
import os
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

def train_career_model(csv_path='data/job_dataset.csv'):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(csv_path)
    encoders={}
    categorical_column=['Degree','Specialization','JobRole']

    for col in categorical_column:
        df[col] = df[col].astype(str).str.strip().str.upper()
        le=LabelEncoder()
        df[col]=le.fit_transform(df[col])
        encoders[col]=le

    X =df[['Degree','Specialization','CGPA','YearOfCompletion']]
    y =df['JobRole']

    x_train, x_test, y_train, y_test =train_test_split(X,y, test_size=0.25, random_state=42,stratify=y)

    model=RandomForestClassifier(n_estimators=100 ,criterion='entropy', max_depth=None, min_samples_split=2 , random_state=42)
    model.fit(x_train, y_train)

    y_pred = model.predict(x_test)
    accuracy=accuracy_score(y_test, y_pred)

    print("-"*30)
    print(f"REPORT: Model Training Complete")
    print(f"Final Accuracy:{accuracy*100:.2f}%")
    print("-"*30)

    model_output_path=os.path.join(base_dir, 'job_model_v5.pkl')
    with open(model_output_path, 'wb') as f:
        pickle.dump({
            'model': model,
            'encoders':encoders
        },f)
    print(f"Success: Model binary saved at {model_output_path}")
    return accuracy
if __name__ =='__main__':
   train_career_model()
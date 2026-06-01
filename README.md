# Edu2Job: Job Role Prediction System

## Overview
An end-to-end machine learning pipeline and user interface designed to predict optimal career trajectories based on educational background, technical skills, and academic performance. The system utilizes an XGBoost classification model, Google OAuth 2.0 for secure authentication, and a lightweight SQLite database for session and prediction history persistence.

## Problem Statement & Solution

**The Problem:** Students and graduates often lack clear, data-driven guidance on which career paths align with their specific academic profiles, leading to misaligned job searches and wasted potential. 

**The Solution:** Edu2Job evaluates a user's education level, specialization, technical skills, certifications, and CGPA. It processes these metrics through a trained XGBoost classification model to output an optimized, highly probable career trajectory, bridging the gap between academic qualifications and industry demands.

## Architecture & Technical Stack

* **Frontend:** Streamlit, Pandas
* **Backend Pipeline:** Python 3.10+
* **Machine Learning:** XGBoost (job_model_v5), Scikit-Learn
* **Database Engine:** SQLite3
* **Authentication:** Google OAuth 2.0 (via Google API Client)
* **Version Control:** Git / GitHub

## Repository Structure

```text
Edu2Job/
├── .env.example             # Template for required environment variables
├── .gitignore               # Exclusions for credentials, DB, and environments
├── README.md                # System documentation
├── requirements.txt         # Pinned Python dependency versions
├── beckend/                 
│   ├── model_training.py    # Training pipeline scripts
│   └── job_model_v5.pkl     # Serialized XGBoost model
├── frontend/                
│   ├── pages/               # Multi-page Streamlit components (Admin, User)
│   └── app.py             # Primary Streamlit application entry point
└── data/                    
    ├── job_dataset.csv      # Base training data
    └── storage.db.example   # Database directory persistence
```

## Local Development Setup

Execute the following commands to provision the application on a local development machine.

### 1. Clone the Repository
```bash
git clone [https://github.com/premraghuvanshi/Edu2Job.git](https://github.com/premraghuvanshi/Edu2Job.git)
cd Edu2Job
```

### 2. Configure the Virtual Environment
Create and activate an isolated Python environment to prevent global dependency conflicts.
```bash
# Windows
python -m venv env
.\env\Scripts\activate

# Linux/macOS
python3 -m venv env
source env/bin/activate
```

### 3. Install Dependencies
Install the strictly pinned libraries required for the system architecture.
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
The application requires specific credentials to handle OAuth and administrative authorization.
1. Create a file named `.env` in the root directory.
2. Copy the structure from `.env.example`.
3. Input your active credentials:

```env
SUPER_KEY=your_secure_admin_key_here
GOOGLE_REDIRECT_URI=http://localhost:8501
GOOGLE_CLIENT_SECRET_JSON={"web":{"client_id":"...","client_secret":"..."}}
```
*Security Note: Never commit the `.env` file or raw `.json` credential files to version control.*

### 5. Initialize the Database
The application utilizes SQLite for file-based storage. The application logic automatically generates `storage.db` and the required table schemas within the `/data` directory upon initial execution. 

### 6. Execute the Application
Launch the Streamlit development server.
```bash
streamlit run app.py
```
The user interface will be accessible at `http://localhost:8501`.

## Production Deployment Specifications

Deployment to production environments requires a VPS (Virtual Private Server) or dedicated server instance. Serverless compute platforms (e.g., Streamlit Community Cloud, Heroku, Vercel) utilize ephemeral filesystems that will critically fail by erasing the SQLite database and administrative model updates upon container termination.

**Deployment Checklist:**
1. **Infrastructure:** Provision a persistent Linux VPS (Ubuntu 22.04 LTS or 24.04 LTS).
2. **Network Configuration:** Update `GOOGLE_REDIRECT_URI` in the production `.env` file to reflect the live server IP or FQDN (Fully Qualified Domain Name).
3. **OAuth Authorization:** Add the production URI to the Authorized Redirect URIs list within the Google Cloud Console.
4. **Process Management:** Execute the application inside a terminal multiplexer (e.g., `tmux` or `screen`) or configure it as a `systemd` service to ensure continuous uptime and automatic restart upon server reboot.

## Author
Prem Raghuvanshi

import pandas as pd

def career_tokenizer(text):
    """
    Standardized tokenizer for career skills and certifications.
    Must be in this isolated file to prevent Pickle __main__ namespace crashes.
    """
    if pd.isna(text) or str(text).strip() == "": 
        return []
    return [s.strip().lower() for s in str(text).split(',')]
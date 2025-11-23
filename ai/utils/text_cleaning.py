# text_cleaning.py
"""
Helper functions to clean and normalize text for analysis.
"""

import re

def clean_text(text: str) -> str:
    """
    Normalize text for NLP:
    - Lowercase
    - Remove special characters
    - Strip extra spaces
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

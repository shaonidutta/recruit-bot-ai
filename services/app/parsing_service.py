# services/app/parsing_service.py

import re
import spacy
from typing import Dict, List, Any

# Load a pre-trained NLP model. This is a one-time cost.
# Ensure you have downloaded it first.
nlp = spacy.load("en_core_web_sm")


def parse_job_description(raw_text: str) -> Dict[str, Any]:
    """
    Extracts structured data from a raw job description using NLP and keyword matching.
    """
    parsed_data = {"skills": [], "experience_years": None, "mentioned_tools": []}

    # --- 1. Simple Keyword Matching ---
    # Example: Look for common skills
    potential_skills = [
        "Python",
        "JavaScript",
        "React",
        "Node.js",
        "FastAPI",
        "SQL",
        "AWS",
    ]
    found_skills = {
        skill
        for skill in potential_skills
        if re.search(r"\b" + re.escape(skill) + r"\b", raw_text, re.IGNORECASE)
    }
    parsed_data["skills"] = list(found_skills)

    # Example: Use regex to find years of experience
    # This looks for patterns like "5+ years", "3-5 years", "2 years of experience"
    experience_match = re.search(r"(\d+)\+?-?(\d+)?\s+years?", raw_text, re.IGNORECASE)
    if experience_match:
        parsed_data["experience_years"] = int(experience_match.group(1))

    # --- 2. Advanced NLP Extraction with spaCy ---
    doc = nlp(raw_text)

    # Example: Use Named Entity Recognition (NER) to find company/product names
    # ORG = Organization, PRODUCT = Product
    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT"]:
            parsed_data["mentioned_tools"].append(ent.text)

    # Remove duplicates
    parsed_data["mentioned_tools"] = list(set(parsed_data["mentioned_tools"]))

    return parsed_data

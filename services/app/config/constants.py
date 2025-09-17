"""
Application Constants
Converted from backend/src/config/constants.js
"""

# Job Sources Configuration
JOB_SOURCES = {
    "LINKEDIN": "linkedin",
    "INDEED": "indeed",
    "GOOGLE": "google"
}

# Agent Configuration
AGENT_CONFIG = {
    "linkedin": {
        "name": "linkedin",
        "function": "fetch_linkedin_jobs"
    },
    "indeed": {
        "name": "indeed",
        "function": "fetch_indeed_jobs"
    },
    "google": {
        "name": "google",
        "function": "fetch_google_jobs"
    }
}

# Database Collections
COLLECTIONS = {
    "users": "users",
    "jobs": "jobs",
    "candidates": "candidates",
    "campaigns": "campaigns",
    "matches": "matches",
    # NEW: Enrichment collections
    "companies": "companies",
    "contacts": "contacts"
}

# Default Values
DEFAULT_KEYWORDS = "Software Engineer"
DEFAULT_CRON_SCHEDULE = "0 2 * * *"  # 2:00 AM daily
DEFAULT_TIMEZONE = "UTC"

# Matching Configuration
MATCHING_THRESHOLD = 0.4  # Minimum similarity score for candidate matches

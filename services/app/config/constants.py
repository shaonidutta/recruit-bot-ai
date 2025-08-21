"""
Application Constants
Converted from backend/src/config/constants.js
"""

# Job Sources Configuration
JOB_SOURCES = {
    "INDEED": "agents/indeed",
    "LINKEDIN": "agents/linkedin",
}

# Agent Configuration
AGENT_CONFIG = {
    "linkedin": {
        "name": "linkedin",
        "endpoint": "agents/linkedin"
    },
    "indeed": {
        "name": "indeed", 
        "endpoint": "agents/indeed"
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

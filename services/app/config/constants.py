"""
Application Constants
Converted from backend/src/config/constants.js

NOTE: For matching threshold, import from workflow_config.py (single source of truth)
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

# NOTE: MATCHING_THRESHOLD moved to workflow_config.py (single source of truth)
# Import from: from app.config.workflow_config import WorkflowConfig
# Usage: WorkflowConfig.MATCHING_THRESHOLD

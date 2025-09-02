"""
Environment configuration for the cashout tracker application.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Google Sheets configuration
GOOGLE_SERVICE_ACCOUNT_EMAIL = os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL')
GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')

def validate_config():
    """Validate that all required environment variables are set."""
    if not GOOGLE_SERVICE_ACCOUNT_EMAIL:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_EMAIL environment variable is required")
    if not GOOGLE_SHEET_ID:
        raise ValueError("GOOGLE_SHEET_ID environment variable is required")
    
    # Check if credentials file exists
    if not os.path.exists(GOOGLE_CREDENTIALS_FILE):
        raise FileNotFoundError(f"Credentials file not found: {GOOGLE_CREDENTIALS_FILE}")
    
    return True

if __name__ == "__main__":
    try:
        validate_config()
        print("✅ Configuration validation passed!")
        print(f"Service Account: {GOOGLE_SERVICE_ACCOUNT_EMAIL}")
        print(f"Credentials File: {GOOGLE_CREDENTIALS_FILE}")
        print(f"Sheet ID: {GOOGLE_SHEET_ID}")
    except Exception as e:
        print(f"❌ Configuration error: {e}")

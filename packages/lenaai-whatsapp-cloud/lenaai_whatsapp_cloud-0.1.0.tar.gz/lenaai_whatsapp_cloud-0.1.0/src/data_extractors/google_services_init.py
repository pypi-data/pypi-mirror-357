import os
import json
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth import default
from googleapiclient.discovery import build

# Import configuration from config.py
from src.utils.config import CLIENT_SECRET_FILE, SHEET_SCOPE, TOKEN_FILE, LOCAL_ENV, DRIVE_SCOPES

# Define proper Google API scopes
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
]

# Logger setup
logger = logging.getLogger(__name__)

def get_credentials(scopes):
    """
    Get valid credentials for Google APIs.
    
    Args:
        scopes: List of API scopes required
        
    Returns:
        Credentials object for Google API
    """
    creds = None
    
    try:
        if LOCAL_ENV:
            # Local auth flow with credential file
            if os.path.exists(TOKEN_FILE):
                try:
                    creds = Credentials.from_authorized_user_file(TOKEN_FILE, scopes)
                except Exception as e:
                    logger.warning(f"Error loading token file: {e}")
                    if os.path.exists(TOKEN_FILE):
                        os.remove(TOKEN_FILE)
            
            # If credentials don't exist or are invalid, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        CLIENT_SECRET_FILE, scopes)
                    creds = flow.run_local_server(port=0)
                    
                    # Save the credentials for future use
                    with open(TOKEN_FILE, 'w') as token:
                        token.write(creds.to_json())
        else:
            # Production auth using Workload Identity Federation
            creds, _ = default(scopes=scopes)
            logger.info(f"✅ Authentication successful via Workload Identity Federation!")
        
        return creds
    
    except Exception as e:
        logger.error(f"❌ Failed to get credentials: {e}")
        raise RuntimeError(f"Failed to get Google API credentials: {e}")

def get_drive_service():
    """Build and return a Google Drive service object."""
    try:
        creds = get_credentials(GOOGLE_SCOPES)
        service = build("drive", "v3", credentials=creds)
        logger.info("✅ Drive service initialized successfully")
        return service
    except Exception as e:
        logger.error(f"❌ Failed to setup Google Drive service: {e}")
        raise RuntimeError(f"Failed to setup Google Drive service: {e}")

def get_sheets_service():
    """Build and return a Google Sheets service object."""
    try:
        creds = get_credentials(GOOGLE_SCOPES)  # Use GOOGLE_SCOPES instead of SHEET_SCOPE
        service = build("sheets", "v4", credentials=creds)
        logger.info("✅ Sheets service initialized successfully")
        return service
    except Exception as e:
        logger.error(f"❌ Failed to setup Google Sheets service: {e}")
        raise RuntimeError(f"Failed to setup Google Sheets service: {e}")

# Initialize service instances
try:
    driveService = get_drive_service()
    sheetsService = get_sheets_service()
except Exception as e:
    logger.error(f"❌ Failed to initialize Google services: {e}")
    # Allow imports to work even if services fail initially
    driveService = None
    sheetsService = None
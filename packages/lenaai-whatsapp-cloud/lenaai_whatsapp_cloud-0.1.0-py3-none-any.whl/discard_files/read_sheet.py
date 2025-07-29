import os
import json
import logging
import re
from typing import List, Dict, Any
import asyncio
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.auth import default
from src.utils.config import CLIENT_SECRET_FILE, SHEET_SCOPE, TOKEN_FILE
SCOPES = SHEET_SCOPE

class GoogleSheetReader:
    """
    A class to handle reading data from Google Sheets.
    """
    
    def __init__(self):
        """
        Initialize the Google Sheet Reader.
        Set up logging and prepare service.
        """
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize service as None
        self.service = None
    
    def get_credentials(self) -> Credentials:
        """
        Get valid credentials for Google Sheets API.
        
        Returns:
            Credentials object for Google API
        """
        creds = None
        
        # Check if token file exists
        if os.path.exists(TOKEN_FILE):
            try:
                creds = Credentials.from_authorized_user_info(
                    json.load(open(TOKEN_FILE)), SCOPES)
            except Exception as e:
                self.logger.warning(f"Error loading token file: {e}")
                if os.path.exists(TOKEN_FILE):
                    os.remove(TOKEN_FILE)
        
        # If credentials don't exist or are invalid, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        CLIENT_SECRET_FILE, SCOPES)
                    creds = flow.run_console()
                    
                    # Save the credentials for future use
                    with open(TOKEN_FILE, 'w') as token:
                        token.write(creds.to_json())
                        
                except Exception as e:
                    self.logger.error(f"Error during authentication: {e}")
                    raise
        if not creds:
            self.logger.info("Loading credentials from environment")
            creds, _ = default(scopes=SCOPES)

        return creds

    def get_sheets_service(self):
        """
        Build and return a Google Sheets service object.
        
        Returns:
            Google Sheets service object
        """
        try:
            if not self.service:
                creds = self.get_credentials()
                self.service = build('sheets', 'v4', credentials=creds)
                self.logger.info("Google Sheets service created successfully")
            return self.service
        except Exception as e:
            self.logger.error(f"Failed to create Google Sheets service: {e}")
            raise

    def extract_spreadsheet_id(self, spreadsheet_url: str) -> str:
        """
        Extract spreadsheet ID from a Google Sheets URL.
        
        Args:
            spreadsheet_url: The URL of the Google Spreadsheet
            
        Returns:
            The spreadsheet ID
            
        Raises:
            ValueError: If URL is invalid
        """
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", spreadsheet_url)
        if not match:
            raise ValueError("Invalid Google Spreadsheet URL")
        return match.group(1)

    async def read_spreadsheet_data(self, spreadsheet_url: str, sheet_range: str = "Sheet1") -> List[List[Any]]:
        """
        Read data from a Google Spreadsheet using its URL.
        
        Args:
            spreadsheet_url: The URL of the Google Spreadsheet
            sheet_range: The sheet name or range to read
            
        Returns:
            List of rows containing the spreadsheet data
        """
        try:
            # Extract the spreadsheet ID from the URL
            spreadsheet_id = self.extract_spreadsheet_id(spreadsheet_url)
            
            # Get the sheets service
            service = self.get_sheets_service()
            
            # Call the Sheets API
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id, range=sheet_range).execute()
            
            # Get the values from the result
            values = result.get('values', [])
            
            if not values:
                self.logger.warning("No data found in spreadsheet")
                return []
            
            self.logger.info(f"Successfully read {len(values)} rows from spreadsheet")
            return values
        
        except Exception as e:
            self.logger.error(f"Error reading spreadsheet: {e}")
            raise

# Create a singleton instance for easy importing
sheet_reader = GoogleSheetReader()

# For backward compatibility
async def read_spreadsheet_data(spreadsheet_url: str, sheet_range: str = "Sheet1") -> List[List[Any]]:
    """
    Legacy function to read spreadsheet data using the GoogleSheetReader class.
    """
    return await sheet_reader.read_spreadsheet_data(spreadsheet_url, sheet_range)
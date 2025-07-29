import os
import re
import logging
import pandas as pd
from io import BytesIO
from typing import List, Dict, Any, Union, Optional
import asyncio
from datetime import datetime

# Import the Google services from the correct path
from src.data_extractors.google_services_init import driveService, sheetsService

# Configure logger
logger = logging.getLogger(__name__)

def determine_source_type(url: str) -> str:
    """
    Determine the source type based on the URL pattern.
    """
    # First check if it's a local file path for Excel
    if os.path.exists(url) and url.endswith(('.xlsx', '.xls', '.xlsm')):
        return "excel_file"
    
    # Check if it's an Excel file in Google Drive
    if re.search(r"\.xls[x]?", url) or "/edit?usp=sharing&ouid=" in url:
        return "excel_drive"
    
    # Otherwise, assume it's a Google Sheet
    return "google_sheet"

class SpreadsheetReader:
    """
    A unified class for reading data from different spreadsheet sources:
    - Google Sheets
    - Google Drive Excel files
    - Local Excel files
    """
    
    @staticmethod
    def extract_spreadsheet_id(url: str) -> str:
        """
        Extract spreadsheet ID from a Google Sheets URL.
        
        Args:
            url: The URL of the Google Spreadsheet
            
        Returns:
            The spreadsheet ID
            
        Raises:
            ValueError: If URL is invalid
        """
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
        if not match:
            raise ValueError("Invalid Google Spreadsheet URL")
        return match.group(1)
    
    @staticmethod
    def extract_drive_file_id(url: str) -> str:
        """
        Extract file ID from a Google Drive URL.
        
        Args:
            url: The URL of the Google Drive file
            
        Returns:
            The file ID
            
        Raises:
            ValueError: If URL is invalid
        """
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
        if match:
            return match.group(1)
        
        match_alt = re.search(r"id=([a-zA-Z0-9-_]+)", url)
        if match_alt:
            return match_alt.group(1)
        
        raise ValueError("Invalid Google Drive URL")
    
    async def read_google_sheet(self, spreadsheet_url: str, sheet_range: str = "Sheet1") -> List[List[Any]]:
        """
        Read data from a Google Spreadsheet.
        
        Args:
            spreadsheet_url: URL of the Google Sheet
            sheet_range: Sheet name or range to read
            
        Returns:
            List of rows containing the spreadsheet data
        """
        try:
            spreadsheet_id = self.extract_spreadsheet_id(spreadsheet_url)
            logger.info(f"🔍 Reading Google Sheet with ID: {spreadsheet_id}")
            
            result = sheetsService.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id, range=sheet_range).execute()
            
            values = result.get('values', [])
            
            if not values:
                logger.warning("⚠ No data found in Google Sheet!")
                return []
            
            logger.info(f"✅ Successfully read {len(values)} rows from Google Sheet")
            return values
            
        except Exception as e:
            logger.error(f"❌ Failed to read Google Sheet ({spreadsheet_url}): {e}")
            raise
    
    async def read_drive_excel(self, file_url: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """
        Read data from an Excel file stored in Google Drive.
        
        Args:
            file_url: URL of the Excel file in Google Drive
            sheet_name: Name of the sheet to read (defaults to first sheet)
            
        Returns:
            Pandas DataFrame with the spreadsheet data
        """
        try:
            file_id = self.extract_drive_file_id(file_url)
            logger.info(f"🔍 Reading Excel from Google Drive with ID: {file_id}")
            
            request = driveService.files().get_media(fileId=file_id)
            file_content = BytesIO(request.execute())
            
            excel_file = pd.ExcelFile(file_content)
            available_sheets = excel_file.sheet_names
            logger.info(f"📑 Available sheets: {available_sheets}")
            
            if sheet_name and sheet_name in available_sheets:
                target_sheet = sheet_name
            else:
                target_sheet = available_sheets[0]  # Default to first sheet
            
            df = pd.read_excel(excel_file, sheet_name=target_sheet)
            logger.info(f"✅ Successfully read {len(df)} rows from Google Drive Excel")
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to read Excel from Google Drive ({file_url}): {e}")
            raise
    
    async def read_local_excel(self, file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """
        Read data from a local Excel file.
        
        Args:
            file_path: Path to the local Excel file
            sheet_name: Name of the sheet to read (defaults to first sheet)
            
        Returns:
            Pandas DataFrame with the spreadsheet data
        """
        try:
            logger.info(f"🔍 Reading local Excel file: {file_path}")
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Excel file not found: {file_path}")
            
            excel_file = pd.ExcelFile(file_path)
            available_sheets = excel_file.sheet_names
            logger.info(f"📑 Available sheets: {available_sheets}")
            
            if sheet_name and sheet_name in available_sheets:
                target_sheet = sheet_name
            else:
                target_sheet = available_sheets[0]  # Default to first sheet
            
            df = pd.read_excel(excel_file, sheet_name=target_sheet)
            logger.info(f"✅ Successfully read {len(df)} rows from local Excel file")
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to read local Excel file ({file_path}): {e}")
            raise
    
    async def read_any_source(self, source: str, sheet_name: str = "Sheet1") -> Union[List[List[Any]], pd.DataFrame]:
        """
        Unified method to read data from any spreadsheet source.
        Automatically detects the source type based on the URL/path.
        
        Args:
            source: URL or path to the spreadsheet
            sheet_name: Sheet name to read
            
        Returns:
            Either a list of rows (for Google Sheets) or a Pandas DataFrame (for Excel)
        """
        try:
            # Use the determine_source_type function to identify the source type
            source_type = determine_source_type(source)
            logger.info(f"🔍 Detected source type: {source_type} for {source}")
            
            if source_type == "google_sheet":
                # Google Sheet
                return await self.read_google_sheet(source, sheet_name)
                
            elif source_type == "excel_drive":
                # Google Drive Excel
                return await self.read_drive_excel(source, sheet_name)
                
            elif source_type == "excel_file":
                # Local Excel file
                return await self.read_local_excel(source, sheet_name)
                
            else:
                raise ValueError(f"Unsupported spreadsheet source type: {source_type}")
                
        except Exception as e:
            logger.error(f"❌ Failed to read from source ({source}): {e}")
            raise
    
    @staticmethod
    def dataframe_from_sheet_data(data: List[List[Any]]) -> pd.DataFrame:
        """
        Convert Google Sheets data format to Pandas DataFrame.
        
        Args:
            data: List of rows from Google Sheets API
            
        Returns:
            Pandas DataFrame
        """
        if not data:
            return pd.DataFrame()
        
        headers = data[0]
        rows = data[1:]
        
        # Handle missing values in rows
        processed_rows = []
        for row in rows:
            # Extend row if it's shorter than headers
            if len(row) < len(headers):
                row = row + [''] * (len(headers) - len(row))
            processed_rows.append(row)
        
        return pd.DataFrame(processed_rows, columns=headers)

# Create a singleton instance for easy importing
spreadsheet_reader = SpreadsheetReader()
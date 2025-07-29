import logging
from typing import Dict, Any, Tuple, Optional, List
from src.utils.config import MAX_MESSAGES
from src.message_handler.whatsapp_message_handler import WhatsAppMessageHandler
from discard_files.read_sheet import read_spreadsheet_data
from src.utils.status_enums import VideoSendStatus, MessageSendStatus

class SheetMessageProcessor:
    """
    Class to handle processing and sending of WhatsApp messages to contacts from spreadsheets.
    """
    
    def __init__(self, credentials: Dict[str, str]):
        """
        Initialize the sheet message processor.
        
        Args:
            credentials: Dictionary containing WhatsApp API credentials
        """
        self.credentials = credentials
        self.whatsapp_handler = WhatsAppMessageHandler(credentials)
        
    async def validate_phone_number(self, phone: str) -> bool:
        """
        Validates and formats a phone number.
        - If it starts with '+', removes it.
        - If it is 11 digits long, adds '2' to the beginning.
        - Ensures the final number starts with '2' and is 12 digits long.
        
        Args:
            phone: The phone number to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not phone:
            return False
            
        # Remove non-digit characters
        cleaned_phone = ''.join(filter(str.isdigit, phone))
        
        # If the number is 11 digits, add '2' at the beginning
        if len(cleaned_phone) == 11:
            cleaned_phone = '2' + cleaned_phone
        
        # Validate the final number
        return cleaned_phone.startswith('2') and len(cleaned_phone) == 12
    
    async def find_columns_indices(self, headers: List[str]) -> Tuple[int, Optional[int]]:
        """
        Find the indices of phone and name columns in the sheet headers.
        
        Args:
            headers: List of column headers
            
        Returns:
            Tuple[int, Optional[int]]: The indices of phone and name columns
        """
        phone_column_idx = None
        name_column_idx = None
        
        # Possible column names for phone and name/username
        possible_phone_names = ["phone", "phone number", "phonenumber", "mobile", "contact", "number", "phone_number"]
        possible_name_names = ["name", "username", "user name", "user", "contact name", "full name", "first name"]
        
        # Find phone column
        for i, header in enumerate(headers):
            header_lower = str(header).lower()
            if any(possible_name in header_lower for possible_name in possible_phone_names):
                phone_column_idx = i
                break
        
        # Find name column
        for i, header in enumerate(headers):
            header_lower = str(header).lower()
            if any(possible_name in header_lower for possible_name in possible_name_names):
                name_column_idx = i
                break
        
        # Fallback: use the first column for phone if we can't identify a phone column
        if phone_column_idx is None:
            phone_column_idx = 0
            logging.warning(f"Could not identify phone column, using first column: {headers[phone_column_idx]}")
        
        return phone_column_idx, name_column_idx
    
    async def process_and_send_video(self, spreadsheet_url: str, video_url: str, sheet_name: str = "Sheet1") -> Dict[str, Any]:
        """
        Process spreadsheet data and send video to valid phone numbers (Max 100).
        
        Args:
            spreadsheet_url: The ID of the Google Spreadsheet
            video_url: The URL of the video to send
            sheet_name: The name of the sheet to read from
            
        Returns:
            Dict[str, Any]: Results of the video sending operation
        """
        
        results = {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "invalid_numbers": 0,
            "details": []
        }
        
        try:
            # Read spreadsheet data
            
            records = await read_spreadsheet_data(spreadsheet_url, sheet_name)
            
            if not records or len(records) < 2:  # Need at least headers and one data row
                raise Exception("Not enough data in spreadsheet or empty spreadsheet")
                
            results["total"] = min(len(records) - 1, MAX_MESSAGES)  # Subtract 1 for header row
            
            # Assume first row contains headers
            headers = records[0]
            
            # Find phone and name column indices
            phone_column_idx, name_column_idx = await self.find_columns_indices(headers)
            
            # Process each record (skip the header row)
            count = 0
            for record in records[1:]:
                if count >= MAX_MESSAGES:
                    break
                    
                # Make sure the record has enough columns for the phone
                if len(record) <= phone_column_idx:
                    results["invalid_numbers"] += 1
                    results["details"].append({
                        "phone": "MISSING",
                        "status": "INVALID_RECORD",
                        "message": "Record doesn't have enough columns",
                        "username": ""
                    })
                    continue
                    
                phone = str(record[phone_column_idx])
                
                # Extract username if available
                username = ""
                if name_column_idx is not None and len(record) > name_column_idx:
                    username = str(record[name_column_idx])
                
                # Validate phone number
                is_valid = await self.validate_phone_number(phone)
                
                if not is_valid:
                    results["invalid_numbers"] += 1
                    results["details"].append({
                        "phone": phone,
                        "status": "INVALID_NUMBER",
                        "message": "Phone number does not start with 2 or is not 12 digits",
                        "username": username
                    })
                    continue
                    
                # Send video using the template
                status = await self.whatsapp_handler.send_arabic_real_estate_template(
                    to_number=phone,
                    video_url=video_url
                )
                
                if status == MessageSendStatus.SUCCESS:
                    results["successful"] += 1
                    results["details"].append({
                        "phone": phone,
                        "status": "SUCCESS",
                        "message": "Video sent successfully",
                        "username": username
                    })
                else:
                    results["failed"] += 1
                    results["details"].append({
                        "phone": phone,
                        "status": status.value,
                        "message": f"Failed to send video: {status.value}",
                        "username": username
                    })
                
                count += 1  # Increment message count
                
            return results
            
        except Exception as e:
            logging.error(f"Error processing and sending video: {str(e)}")
            raise Exception(f"Failed to process and send video: {str(e)}")
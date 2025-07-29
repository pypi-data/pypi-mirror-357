import logging
import json
import asyncio
import re
import pandas as pd
from typing import Dict, Any, Tuple, Optional, List, Union
from twilio.rest import Client

# Import our spreadsheet reader from the correct path
from src.data_extractors.spreadsheet_reader import spreadsheet_reader

# Configure logger
logger = logging.getLogger(__name__)

class TwilioSheetMessenger:
    """
    Class to handle processing and sending of Twilio WhatsApp messages
    from various spreadsheet sources.
    """
    
    def __init__(self, credentials: Dict[str, str]):
        """
        Initialize the Twilio processor with credentials.
        
        Args:
            credentials: Dictionary containing Twilio credentials
                - account_sid: Twilio account SID
                - auth_token: Twilio auth token
                - phone_number: Twilio WhatsApp number (format: whatsapp:+1234567890)
        """
        self.credentials = credentials
        self.client = Client(credentials['account_sid'], credentials['auth_token'])
        self.from_whatsapp_number = credentials['phone_number']
        self.template_sid = "HX05c18d8c1dad6a898817f54a825f9f15"  # Production template
    
    async def validate_phone_number(self, phone: str) -> Tuple[bool, str]:
        """
        Ensures number is properly formatted for Twilio WhatsApp.
        
        Args:
            phone: Input phone number
            
        Returns:
            Tuple of (is_valid, formatted_number)
        """
        if not phone:
            return False, ""
        
        cleaned_phone = str(phone).strip()
        
        # Remove non-numeric characters for validation
        digits_only = ''.join(filter(str.isdigit, cleaned_phone))
        
        # Format the number
        if not cleaned_phone.startswith('+'):
            # Handle different cases
            if len(digits_only) == 11:  # Full international number without +
                formatted_number = f"+{digits_only}"
            elif digits_only.startswith('2'):  # Cases like Egypt numbers
                formatted_number = f"+{digits_only}"
            else:
                # Add your country code logic here if needed
                formatted_number = f"+{digits_only}"
        else:
            formatted_number = cleaned_phone
        
        # Validate the number has enough digits
        is_valid = len(''.join(filter(str.isdigit, formatted_number))) >= 10
        return is_valid, formatted_number
    
    async def send_twilio_template(self, to_number: str, media_url: str) -> bool:
        """
        Send a template message via Twilio WhatsApp with media.
        
        Args:
            to_number: Recipient's phone number
            media_url: URL of the media to send
            
        Returns:
            True if message was sent successfully, False otherwise
        """
        try:
            # Ensure the number is properly formatted
            if not to_number.startswith('+'):
                to_number = f"+{to_number}"
            
            to_whatsapp = f"whatsapp:{to_number}"
            from_whatsapp = self.from_whatsapp_number
            
            # Create content variables for the media
            content_variables = json.dumps({"1": media_url})
            
            # Send the message
            message = self.client.messages.create(
                from_=from_whatsapp,
                to=to_whatsapp,
                content_sid=self.template_sid,
                content_variables=content_variables
            )
            
            logger.info(f"✅ Successfully sent template to {to_number} with SID: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error in Twilio template send to {to_number}: {str(e)}")
            return False
    
    async def process_and_send_media(self, source: str, media_url: str, sheet_name: str = "Sheet1") -> Dict[str, Any]:
        """
        Process data from any spreadsheet source and send media via Twilio template to all valid numbers.
        
        Args:
            source: URL or path to the spreadsheet (any supported type)
            media_url: URL of the media to send
            sheet_name: Name of the sheet to read
            
        Returns:
            Dictionary with results statistics
        """
        results = {
            "total": 0, 
            "successful": 0, 
            "failed": 0, 
            "invalid_numbers": 0, 
            "details": []
        }
        
        try:
            # Read the spreadsheet data (automatically detects the source type)
            data = await spreadsheet_reader.read_any_source(source, sheet_name)
            
            # Convert to DataFrame if it's not already
            if isinstance(data, list):
                df = spreadsheet_reader.dataframe_from_sheet_data(data)
            else:
                df = data
            
            # Validate we have data
            if df.empty:
                logger.warning(f"No data found in spreadsheet: {source}, sheet: {sheet_name}")
                return results
            
            # Get lowercase column names for case-insensitive matching
            columns = [col.lower() for col in df.columns]
            
            # Find phone and name columns
            phone_col = None
            name_col = None
            
            for i, col in enumerate(columns):
                if any(keyword in col for keyword in ['phone', 'mobile', 'number', 'tel']):
                    phone_col = df.columns[i]
                if any(keyword in col for keyword in ['name', 'username', 'user']):
                    name_col = df.columns[i]
            
            if not phone_col:
                logger.error(f"No phone number column found in spreadsheet headers: {df.columns.tolist()}")
                return results
            
            # Process each row
            for _, row in df.iterrows():
                phone = str(row[phone_col])
                name = str(row[name_col]) if name_col else "User"
                
                results["total"] += 1
                
                # Validate and format phone number
                is_valid, formatted_phone = await self.validate_phone_number(phone)
                
                if not is_valid:
                    results["invalid_numbers"] += 1
                    results["details"].append({
                        "phone": phone, 
                        "status": "INVALID_NUMBER", 
                        "username": name
                    })
                    continue
                
                # Send template
                status = await self.send_twilio_template(
                    to_number=formatted_phone, 
                    media_url=media_url
                )
                
                if status:
                    results["successful"] += 1
                    results["details"].append({
                        "phone": formatted_phone, 
                        "status": "SUCCESS", 
                        "username": name
                    })
                else:
                    results["failed"] += 1
                    results["details"].append({
                        "phone": formatted_phone, 
                        "status": "FAILED", 
                        "username": name
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing spreadsheet: {str(e)}")
            raise
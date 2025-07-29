import logging
import asyncio
import pandas as pd
from pyrogram import Client
from discard_files.read_sheet import read_spreadsheet_data
import os
import httpx
import time
import random
import re

class TelegramSheetProcessor:
    """
    Class to handle processing and sending of Telegram messages to contacts from spreadsheets.
    Uses Pyrogram client to send messages by phone number.
    """
    
    def __init__(self, credentials):
        """
        Initialize the Telegram sheet processor.
        
        Args:
            credentials: Dictionary containing Telegram API credentials
        """
        self.api_id = credentials.get("api_id")
        self.api_hash = credentials.get("api_hash")
        self.phone_number = credentials.get("phone_number") or credentials.get("phone")
        self.client = None
        self.is_bot = False
        self.client_id = credentials.get("client_id", "default")
        
        # Check if we're using a bot or user account
        self.bot_token = credentials.get("bot_token")
        
        # For logging
        logging.info(f"Initializing TelegramSheetProcessor with credentials: api_id={self.api_id}, "
                    f"has_api_hash={'Yes' if self.api_hash else 'No'}, "
                    f"has_phone={'Yes' if self.phone_number else 'No'}, "
                    f"has_bot_token={'Yes' if self.bot_token else 'No'}")
        
        # Make sure api_id is an integer
        if isinstance(self.api_id, str):
            try:
                self.api_id = int(self.api_id)
            except ValueError:
                raise ValueError(f"Invalid api_id: {self.api_id}. Must be an integer.")
        
        # Prioritize user account over bot if both are available
        if self.api_id and self.api_hash and self.phone_number:
            logging.info("Using Telegram user account authentication")
            self.client = Client(
                f"telegram_user_{self.client_id}",
                api_id=self.api_id,
                api_hash=self.api_hash,
                phone_number=self.phone_number,
                in_memory=False  # Save session to disk for faster reconnection
            )
        elif self.api_id and self.api_hash and self.bot_token:
            logging.info("Using Telegram bot authentication")
            self.is_bot = True
            self.client = Client(
                f"telegram_bot_{self.client_id}",
                api_id=self.api_id,
                api_hash=self.api_hash,
                bot_token=self.bot_token,
                in_memory=False  # Save session to disk for faster reconnection
            )
        else:
            logging.error("Invalid credentials provided")
            raise ValueError("Invalid credentials. Need either (api_id, api_hash, phone_number) or (api_id, api_hash, bot_token)")

    def format_phone_number(self, phone):
        """Format phone number to ensure it has a + prefix and is properly formatted."""
        if not phone:
            return None
            
        # Convert to string and strip spaces
        phone = str(phone).strip()
        if not phone:
            return None
            
        # Remove any non-digit characters (except +)
        digits_only = re.sub(r'[^\d+]', '', phone)
        
        # If no digits left, return None
        if not digits_only or digits_only == "+":
            return None
            
        # Add + prefix if not present
        if not digits_only.startswith("+"):
            return f"+{digits_only}"
            
        return digits_only

    def is_valid_identifier(self, identifier, id_type):
        """Check if the identifier is valid based on its type."""
        if not identifier:
            return False
            
        if id_type == "phone":
            # Phone should have + followed by at least 6 digits
            if not re.match(r'\+\d{6,}', identifier):
                return False
                
        elif id_type == "username":
            # Username should have @ followed by at least 5 characters
            if not re.match(r'@\w{5,}', identifier):
                return False
                
        return True

    async def download_media_from_google_drive(self, url):
        """Download media from Google Drive link to a temporary file."""
        try:
            # Create temp directory if it doesn't exist
            os.makedirs("temp", exist_ok=True)
            
            # Generate a unique filename
            filename = f"temp/media_{int(time.time())}_{random.randint(1000, 9999)}.jpg"
            
            # Extract file ID from Google Drive URL
            file_id = None
            if "drive.google.com/file/d/" in url:
                file_id = url.split("/file/d/")[1].split("/")[0].split("?")[0]
            elif "drive.google.com/open?id=" in url:
                file_id = url.split("id=")[1].split("&")[0]
            
            if not file_id:
                logging.error(f"Could not extract file ID from URL: {url}")
                return None
                
            # Use a direct URL with the export=view parameter
            direct_url = f"https://drive.google.com/uc?export=view&id={file_id}"
            
            # Download with follow_redirects=True to handle Google Drive redirects
            async with httpx.AsyncClient(follow_redirects=True) as client:
                logging.info(f"Downloading from URL: {direct_url}")
                response = await client.get(direct_url, timeout=60.0)
                
                # Check content type for HTML which might indicate a confirmation page
                content_type = response.headers.get('content-type', '')
                if 'text/html' in content_type.lower():
                    logging.warning(f"Received HTML response instead of file data. File might be too large or requires confirmation.")
                    # Try alternative method for large files
                    logging.info("Trying alternative download method...")
                    
                    # First get the download cookie
                    cookies_response = await client.get(
                        f"https://drive.google.com/uc?export=download&id={file_id}",
                        follow_redirects=False
                    )
                    
                    cookies = cookies_response.cookies
                    # If there's a download_warning cookie, we need to confirm the download
                    if any('download_warning' in k for k in cookies.keys()):
                        confirm_token = next(v for k, v in cookies.items() if 'download_warning' in k)
                        direct_url = f"https://drive.google.com/uc?export=download&id={file_id}&confirm={confirm_token}"
                    
                    # Try again with the updated URL and cookies
                    response = await client.get(direct_url, timeout=60.0, cookies=cookies, follow_redirects=True)
                
                # Save the file
                if response.status_code == 200:
                    with open(filename, "wb") as f:
                        f.write(response.content)
                    
                    logging.info(f"Successfully downloaded media to {filename}")
                    return filename
                else:
                    logging.error(f"Failed to download file: HTTP {response.status_code}")
                    return None
                    
        except Exception as e:
            logging.error(f"Error downloading media from Google Drive: {str(e)}")
            return None

    async def process_and_send_message(self, spreadsheet_url, message, video_url=None, sheet_name="Sheet1"):
        """
        Process spreadsheet data and send messages to Telegram users by phone number or username.
        """
        results = {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "details": []
        }

        # Download media file if URL is provided
        local_media_path = None
        if video_url:
            try:
                if "drive.google.com" in video_url:
                    local_media_path = await self.download_media_from_google_drive(video_url)
                else:
                    # For non-Google Drive URLs, use a simpler download method
                    os.makedirs("temp", exist_ok=True)
                    filename = f"temp/media_{int(time.time())}_{random.randint(1000, 9999)}.jpg"
                    
                    async with httpx.AsyncClient(follow_redirects=True) as client:
                        response = await client.get(video_url, timeout=30.0)
                        if response.status_code == 200:
                            with open(filename, "wb") as f:
                                f.write(response.content)
                            local_media_path = filename
                
                if not local_media_path:
                    logging.warning(f"Could not download media from {video_url}, will send text-only messages")
            except Exception as e:
                logging.error(f"Error processing video URL: {str(e)}")
                logging.warning("Will send text-only messages")

        try:
            # Read spreadsheet data
            records = await read_spreadsheet_data(spreadsheet_url, sheet_name)
            if not records or len(records) < 2:
                raise Exception("Spreadsheet is empty or lacks enough data")

            headers = records[0]
            
            # Determine which columns to use
            phone_column_idx = None
            username_column_idx = None
            chat_id_column_idx = None
            
            for idx, header in enumerate(headers):
                header_lower = str(header).lower()
                if header_lower == "phone":
                    phone_column_idx = idx
                elif header_lower == "username":
                    username_column_idx = idx
                elif header_lower in ["chat_id", "chatid", "chat id"]:
                    chat_id_column_idx = idx
            
            # Fall back to first column if no specific column is found
            if phone_column_idx is None and username_column_idx is None and chat_id_column_idx is None:
                phone_column_idx = 0
                
            media_column_idx = None
            try:
                media_column_idx = headers.index("media")
            except ValueError:
                pass
            
            logging.info(f"Found columns: phone={phone_column_idx}, username={username_column_idx}, "
                        f"chat_id={chat_id_column_idx}, media={media_column_idx}")

            # Print warning if using bot with phone numbers
            if self.is_bot and phone_column_idx is not None and chat_id_column_idx is None:
                logging.warning("Using bot account with phone numbers - this won't work! Bots can only send to chat_ids.")
            
            # Initialize client with context manager to auto-handle connect/disconnect
            async with self.client:
                logging.info(f"Telegram client started successfully")
                
                for row in records[1:]:
                    if not row:  # Skip empty rows
                        continue
                        
                    # Determine the identifier to use
                    identifier = None
                    id_type = None
                    
                    if chat_id_column_idx is not None and len(row) > chat_id_column_idx:
                        identifier = row[chat_id_column_idx]
                        id_type = "chat_id"
                    elif username_column_idx is not None and len(row) > username_column_idx:
                        identifier = row[username_column_idx]
                        if identifier and not str(identifier).startswith("@"):
                            identifier = f"@{identifier}"
                        id_type = "username"
                    elif phone_column_idx is not None and len(row) > phone_column_idx:
                        # Format phone number to ensure it has international format
                        identifier = self.format_phone_number(row[phone_column_idx])
                        id_type = "phone"
                    
                    # Validate the identifier
                    if not identifier or not self.is_valid_identifier(identifier, id_type):
                        results["failed"] += 1
                        original_value = row[phone_column_idx] if phone_column_idx is not None and len(row) > phone_column_idx else "Unknown"
                        results["details"].append({
                            "identifier": original_value, 
                            "status": "FAILED", 
                            "message": f"Invalid identifier: {original_value} (formatted to {identifier})"
                        })
                        continue
                    
                    # Get media if available
                    row_media = None
                    if media_column_idx is not None and len(row) > media_column_idx and row[media_column_idx]:
                        try:
                            if "drive.google.com" in str(row[media_column_idx]):
                                row_media = await self.download_media_from_google_drive(row[media_column_idx])
                            else:
                                # For non-Google Drive URLs
                                os.makedirs("temp", exist_ok=True)
                                filename = f"temp/media_{int(time.time())}_{random.randint(1000, 9999)}.jpg"
                                
                                async with httpx.AsyncClient(follow_redirects=True) as client:
                                    response = await client.get(row[media_column_idx], timeout=30.0)
                                    if response.status_code == 200:
                                        with open(filename, "wb") as f:
                                            f.write(response.content)
                                        row_media = filename
                        except Exception as e:
                            logging.error(f"Error processing row media: {str(e)}")
                    
                    # Use row-specific media if available, otherwise use the global one
                    media_to_use = row_media or local_media_path
                    
                    # Bot limitations check
                    if self.is_bot and id_type == "phone":
                        results["failed"] += 1
                        results["details"].append({
                            "identifier": identifier, 
                            "status": "FAILED", 
                            "message": "Bots can't initiate conversations by phone number. Use a user account or chat_ids instead."
                        })
                        continue
                    
                    try:
                        # For chat_id, we can send directly
                        if id_type == "chat_id":
                            chat_id = identifier
                        # For username or phone, we need to resolve to a user first
                        else:
                            try:
                                # Add a delay to avoid hitting rate limits
                                await asyncio.sleep(0.5)
                                
                                logging.info(f"Looking up user with identifier: {identifier} (type: {id_type})")
                                
                                # For phone numbers, try to import contact first
                                if id_type == "phone":
                                    try:
                                        # Try creating a temporary contact
                                        await self.client.import_contacts([{
                                            "phone": identifier,
                                            "first_name": "Contact",
                                            "last_name": identifier
                                        }])
                                        # Get user by phone
                                        user = await self.client.get_users(identifier)
                                    except Exception as e:
                                        logging.error(f"Error importing contact: {str(e)}")
                                        # Try direct lookup as fallback
                                        user = await self.client.get_users(identifier)
                                else:
                                    # For usernames, just do direct lookup
                                    user = await self.client.get_users(identifier)
                                
                                # Handle if result is a list
                                if isinstance(user, list):
                                    if not user:  # Empty list
                                        raise ValueError(f"No user found with identifier: {identifier}")
                                    user = user[0]  # Take the first match
                                    
                                chat_id = user.id
                                logging.info(f"Found user {user.first_name} (ID: {chat_id}) for identifier {identifier}")
                                
                            except Exception as e:
                                results["failed"] += 1
                                results["details"].append({
                                    "identifier": identifier, 
                                    "status": "FAILED", 
                                    "message": f"Failed to find user: {str(e)}"
                                })
                                continue
                        
                        # Add a delay to avoid hitting rate limits
                        await asyncio.sleep(1)
                        
                        # Send message
                        if media_to_use:
                            # Send photo with caption
                            await self.client.send_photo(
                                chat_id=chat_id, 
                                photo=media_to_use, 
                                caption=message
                            )
                        else:
                            # Send text-only message
                            await self.client.send_message(
                                chat_id=chat_id, 
                                text=message
                            )
                        
                        results["successful"] += 1
                        results["details"].append({
                            "identifier": identifier, 
                            "status": "SUCCESS", 
                            "message": "Message sent successfully"
                        })
                        
                    except Exception as e:
                        logging.error(f"Error sending message to {identifier}: {str(e)}")
                        results["failed"] += 1
                        results["details"].append({
                            "identifier": identifier, 
                            "status": "FAILED", 
                            "message": str(e)
                        })
                
            results["total"] = len([r for r in records[1:] if r])  # Count only non-empty rows

            # Clean up temporary files
            if local_media_path and os.path.exists(local_media_path):
                try:
                    os.remove(local_media_path)
                except:
                    pass

        except Exception as e:
            logging.error(f"Error processing messages: {str(e)}")
            raise Exception(f"Failed to process messages: {str(e)}")

        return results
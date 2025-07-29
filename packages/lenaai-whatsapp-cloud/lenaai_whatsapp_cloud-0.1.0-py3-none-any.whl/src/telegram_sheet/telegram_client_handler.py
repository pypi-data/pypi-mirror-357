import logging
from typing import Dict, Any, Optional, List
import os
import asyncio
from telethon import TelegramClient
from telethon.errors import PhoneNumberInvalidError, FloodWaitError, RPCError
from src.utils.config import LOCAL_ENV

class TelegramClientHandler:
    """
    Handler for Telegram client operations using the Telethon library.
    This allows sending messages to users by phone number.
    """
    
    def __init__(self, credentials: Dict[str, str]):
        """
        Initialize the Telegram client handler.
        
        Args:
            credentials: Dictionary containing Telegram API credentials
        """
        self.credentials = credentials
        self.client_id = credentials.get('client_id')
        self.api_id = credentials.get('api_id')
        self.api_hash = credentials.get('api_hash')
        self.phone = credentials.get('phone')
        self.client = None
        self._initialize_client()
        
    def _initialize_client(self):
        """
        Initialize the Telegram client with API credentials.
        """
        try:
            if not self.api_id or not self.api_hash or not self.phone:
                logging.error(f"❌ Missing Telegram API credentials for client_id: {self.client_id}")
                raise ValueError(f"Missing Telegram API credentials for client_id: {self.client_id}")
                
            # Create the Telegram client
            session_name = f"telegram_session_{self.client_id}"
            self.client = TelegramClient(session_name, self.api_id, self.api_hash)
            
            logging.info(f"✅ Telegram client initialized for client_id: {self.client_id}")
            
        except Exception as e:
            logging.error(f"❌ Error initializing Telegram client: {e}")
            raise
            
    async def start_client(self):
        """
        Start the Telegram client session.
        This should be called before sending any messages.
        """
        if not self.client:
            self._initialize_client()
            
        try:
            await self.client.start(phone=self.phone)
            logging.info(f"✅ Telegram client started for client_id: {self.client_id}")
        except Exception as e:
            logging.error(f"❌ Error starting Telegram client: {e}")
            raise
            
    async def stop_client(self):
        """
        Disconnect the Telegram client.
        """
        if self.client:
            await self.client.disconnect()
            logging.info(f"✅ Telegram client stopped for client_id: {self.client_id}")
            
    async def send_message_by_phone(self, phone_number: str, message: str) -> Dict[str, Any]:
        """
        Send a text message to a user identified by phone number.
        
        Args:
            phone_number: The recipient's phone number (international format with +)
            message: The message to send
            
        Returns:
            Dict with status information
        """
        result = {
            "status": "failed",
            "message": "Failed to send message"
        }
        
        try:
            # Make sure phone number has + prefix
            if not phone_number.startswith('+'):
                phone_number = '+' + phone_number
                
            # Start the client if not already started
            if not self.client.is_connected():
                await self.start_client()
                
            # Find the user by phone number
            user = await self.client.get_entity(phone_number)
            
            # Send the message
            await self.client.send_message(user, message)
            
            # Add a small delay to avoid flooding
            await asyncio.sleep(2)
            
            logging.info(f"✅ Message sent to {phone_number} via Telegram client")
            result = {
                "status": "success",
                "message": "Message sent successfully"
            }
            
        except PhoneNumberInvalidError:
            logging.error(f"❌ Invalid phone number: {phone_number}")
            result["message"] = f"Invalid phone number: {phone_number}"
            
        except FloodWaitError as e:
            # FloodWaitError means we need to wait X seconds before continuing
            logging.error(f"❌ Flood wait error: must wait {e.seconds} seconds")
            result["message"] = f"Rate limited: must wait {e.seconds} seconds"
            
        except RPCError as e:
            logging.error(f"❌ Telegram RPC error: {str(e)}")
            result["message"] = f"Telegram error: {str(e)}"
            
        except Exception as e:
            logging.error(f"❌ Error sending message via Telegram client: {e}")
            result["message"] = str(e)
            
        return result
            
    async def send_photo_by_phone(self, phone_number: str, photo_url: str, caption: str = "") -> Dict[str, Any]:
        """
        Send a photo to a user identified by phone number.
        
        Args:
            phone_number: The recipient's phone number (international format with +)
            photo_url: URL of the photo to send
            caption: Optional caption for the photo
            
        Returns:
            Dict with status information
        """
        result = {
            "status": "failed",
            "message": "Failed to send photo"
        }
        
        try:
            # Make sure phone number has + prefix
            if not phone_number.startswith('+'):
                phone_number = '+' + phone_number
                
            # Start the client if not already started
            if not self.client.is_connected():
                await self.start_client()
                
            # Find the user by phone number
            user = await self.client.get_entity(phone_number)
            
            # Send the photo
            await self.client.send_file(user, photo_url, caption=caption)
            
            # Add a small delay to avoid flooding
            await asyncio.sleep(2)
            
            logging.info(f"✅ Photo sent to {phone_number} via Telegram client")
            result = {
                "status": "success",
                "message": "Photo sent successfully"
            }
            
        except Exception as e:
            logging.error(f"❌ Error sending photo via Telegram client: {e}")
            result["message"] = str(e)
            
        return result
            
    async def send_video_by_phone(self, phone_number: str, video_url: str, caption: str = "") -> Dict[str, Any]:
        """
        Send a video to a user identified by phone number.
        
        Args:
            phone_number: The recipient's phone number (international format with +)
            video_url: URL of the video to send
            caption: Optional caption for the video
            
        Returns:
            Dict with status information
        """
        result = {
            "status": "failed",
            "message": "Failed to send video"
        }
        
        try:
            # Make sure phone number has + prefix
            if not phone_number.startswith('+'):
                phone_number = '+' + phone_number
                
            # Start the client if not already started
            if not self.client.is_connected():
                await self.start_client()
                
            # Find the user by phone number
            user = await self.client.get_entity(phone_number)
            
            # Send the video
            await self.client.send_file(user, video_url, caption=caption)
            
            # Add a small delay to avoid flooding
            await asyncio.sleep(2)
            
            logging.info(f"✅ Video sent to {phone_number} via Telegram client")
            result = {
                "status": "success",
                "message": "Video sent successfully"
            }
            
        except Exception as e:
            logging.error(f"❌ Error sending video via Telegram client: {e}")
            result["message"] = str(e)
            
        return result
    
    async def send_bulk_messages_by_phone(self, phone_numbers: List[str], message: str, 
                                         video_url: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Send messages in bulk to a list of phone numbers.
        This is specifically designed for first-time messaging.
        
        Args:
            phone_numbers: List of recipient phone numbers
            message: The message to send
            video_url: Optional URL of a video to send
            
        Returns:
            List of dictionaries with results for each recipient
        """
        results = []
        
        try:
            # Start the client if not already started
            if not self.client.is_connected():
                await self.start_client()
                
            for phone in phone_numbers:
                try:
                    # Make sure phone number has + prefix
                    if not phone.startswith('+'):
                        phone = '+' + phone
                        
                    # Find the user by phone number
                    user = await self.client.get_entity(phone)
                    
                    # Send video if provided
                    if video_url:
                        await self.client.send_file(user, video_url, caption=message)
                    else:
                        # Otherwise just send the text message
                        await self.client.send_message(user, message)
                    
                    logging.info(f"✅ Message sent to {phone} via Telegram client")
                    results.append({
                        "phone": phone,
                        "status": "success",
                        "message": "Message sent successfully"
                    })
                    
                    # Important: wait between messages to avoid flooding
                    await asyncio.sleep(2)
                    
                except PhoneNumberInvalidError:
                    logging.error(f"❌ Invalid phone number: {phone}")
                    results.append({
                        "phone": phone,
                        "status": "failed",
                        "message": f"Invalid phone number: {phone}"
                    })
                    
                except FloodWaitError as e:
                    # FloodWaitError means we need to wait X seconds before continuing
                    logging.error(f"❌ Flood wait error: must wait {e.seconds} seconds")
                    results.append({
                        "phone": phone,
                        "status": "failed",
                        "message": f"Rate limited: must wait {e.seconds} seconds"
                    })
                    
                    # Wait the required time before continuing
                    await asyncio.sleep(e.seconds)
                    
                except Exception as e:
                    logging.error(f"❌ Error sending message to {phone}: {e}")
                    results.append({
                        "phone": phone,
                        "status": "failed",
                        "message": str(e)
                    })
                    
            await self.client.disconnect()
            return results
            
        except Exception as e:
            logging.error(f"❌ Error in bulk messaging: {e}")
            
            # Make sure to disconnect the client
            try:
                await self.client.disconnect()
            except:
                pass
                
            return results
import logging
from datetime import datetime
from typing import Dict, List, Any
import asyncio
import aiohttp
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from src.message_handler.base_message_handler import BaseMessageHandler
from src.utils.status_enums import MessageSendStatus, VideoSendStatus
from src.utils.config import LENAAI_UPDATE_DB_ENDPOINT

class TwilioMessageHandler(BaseMessageHandler):
    """
    A class to handle all Twilio WhatsApp messaging operations.
    """
    
    def __init__(self, credentials: Dict[str, str]):
        """
        Initialize the Twilio WhatsApp message handler.
        
        Args:
            credentials: Dictionary containing 'account_sid', 'auth_token', and 'phone_number'
        """
        super().__init__(credentials)
        self.credentials = credentials
        self.account_sid = credentials['account_sid']
        self.auth_token = credentials['auth_token']
        self.from_number = credentials['phone_number'] 
        
        
        self.client = Client(self.account_sid, self.auth_token)
        self.platform = "twilio_whatsapp"
        
        # Log initialization
        logging.info(f"✅ Initialized Twilio WhatsApp handler with account {self.account_sid[:6]}**** and sandbox number {self.from_number}")
        
    async def update_firestore_history(self, session, to_number: str, message: str):
        """
        Updates Firestore history with the bot's response.
        """
        # Clean phone number for storage by removing whatsapp: prefix if present
        clean_number = to_number
        if clean_number.startswith('whatsapp:'):
            clean_number = clean_number[9:]  # Remove 'whatsapp:' prefix
            
        bot_response_data = {
            "phone_number": clean_number,
            "client_id": self.credentials['client_id'],
            "bot_response": message,
            "platform": self.platform,
            "timestamp": datetime.utcnow().isoformat()
        }

        async with session.post(LENAAI_UPDATE_DB_ENDPOINT, json=bot_response_data) as history_response:
            if history_response.status == 200:
                logging.info("✅ Bot response saved in Firestore history")
            else:
                logging.error(f"❌ Failed to update Firestore history: {history_response.status} - {await history_response.text()}")

    async def send_text(self, to_number: str, message: str):
        """
        Sends a text message through Twilio WhatsApp asynchronously.
        
        Args:
            to_number: The recipient's phone number (should include 'whatsapp:' prefix)
            message: The text message to send
            
        Returns:
            Status of the send operation
        """
        if not message.strip():
            logging.error("❌ Empty message provided")
            return MessageSendStatus.FAILED_TO_SEND

        # Add 'whatsapp:' prefix if not present
        if not to_number.startswith('whatsapp:'):
            to_whatsapp = f"whatsapp:{to_number}"
        else:
            to_whatsapp = to_number
            
        # Always use the sandbox number as the from address
        from_whatsapp = self.from_number

        try:
            # Log the exact values being used
            logging.info(f"🚀 Sending Twilio message FROM: {from_whatsapp} TO: {to_whatsapp}")
            
            # Create a sync function to be executed in a thread pool
            def send_message_sync():
                try:
                    message_obj = self.client.messages.create(
                        body=message,
                        from_=from_whatsapp,
                        to=to_whatsapp
                    )
                    logging.info(f"✅ Text message sent successfully with SID: {message_obj.sid}")
                    return MessageSendStatus.SUCCESS
                except TwilioRestException as e:
                    logging.error(f"❌ Twilio error: {e}")
                    return MessageSendStatus.FAILED_TO_SEND
                except Exception as e:
                    logging.error(f"❌ Error sending text message: {str(e)}")
                    return MessageSendStatus.FAILED_TO_SEND

            # Run the sync function in a thread pool
            loop = asyncio.get_running_loop()
            status = await loop.run_in_executor(None, send_message_sync)
            
            # Update Firestore if successful
            # if status == MessageSendStatus.SUCCESS:
            #     async with aiohttp.ClientSession() as session:
            #         await self.update_firestore_history(session, to_number, message)
                    
            return status
                
        except Exception as e:
            logging.error(f"❌ Error sending text message: {str(e)}")
            return MessageSendStatus.FAILED_TO_SEND
    
    async def send_image(self, to_number: str, image_url: str):
        """
        Sends a single image through Twilio WhatsApp asynchronously.
        
        Args:
            to_number: The recipient's phone number
            image_url: The URL of the image to send
            
        Returns:
            Status of the send operation
        """
        # Add 'whatsapp:' prefix if not present
        if not to_number.startswith('whatsapp:'):
            to_whatsapp = f"whatsapp:{to_number}"
        else:
            to_whatsapp = to_number
            
        # Always use the sandbox number as the from address
        from_whatsapp = self.from_number

        try:
            logging.info(f"🚀 Attempting to send image: {image_url} to {to_whatsapp}")
            
            # Create a sync function to be executed in a thread pool
            def send_image_sync():
                try:
                    message = self.client.messages.create(
                        media_url=[image_url],
                        from_=from_whatsapp,
                        to=to_whatsapp
                    )
                    logging.info(f"✅ Image sent successfully: {image_url} with SID: {message.sid}")
                    return {
                        "url": image_url,
                        "status": "success",
                        "message": "Image sent successfully",
                        "sid": message.sid
                    }
                except TwilioRestException as e:
                    logging.error(f"❌ Twilio error sending image {image_url}: {e}")
                    return {
                        "url": image_url,
                        "status": "failed",
                        "message": str(e)
                    }
                except Exception as e:
                    logging.error(f"❌ Error sending image: {str(e)}")
                    return {
                        "url": image_url,
                        "status": "failed",
                        "message": str(e)
                    }

            # Run the sync function in a thread pool
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, send_image_sync)
                    
        except Exception as e:
            logging.error(f"❌ Error sending image: {str(e)}")
            return {
                "url": image_url,
                "status": "failed",
                "message": str(e)
            }

    async def send_images(self, to_number: str, image_urls: List[str]):
        """
        Sends multiple images through Twilio WhatsApp asynchronously.
        
        Args:
            to_number: The recipient's phone number
            image_urls: List of image URLs to send
            
        Returns:
            List of results for each image
        """
        results = []
        
        # Twilio can send only one media attachment per message
        for image_url in image_urls:
            result = await self.send_image(to_number, image_url)
            results.append(result)
            # Add a small delay between messages to avoid rate limiting
            await asyncio.sleep(1)
        
        return results

    async def send_video(self, to_number: str, video_url: str):
        """
        Sends a video through Twilio WhatsApp asynchronously.
        
        Args:
            to_number: The recipient's phone number
            video_url: The URL of the video to send
            
        Returns:
            Status of the send operation
        """
        # Add 'whatsapp:' prefix if not present
        if not to_number.startswith('whatsapp:'):
            to_whatsapp = f"whatsapp:{to_number}"
        else:
            to_whatsapp = to_number
            
        # Always use the sandbox number as the from address
        from_whatsapp = self.from_number

        try:
            logging.info(f"🚀 Attempting to send video: {video_url} to {to_whatsapp}")
            
            # Create a sync function to be executed in a thread pool
            def send_video_sync():
                try:
                    message = self.client.messages.create(
                        media_url=[video_url],
                        from_=from_whatsapp,
                        to=to_whatsapp
                    )
                    logging.info(f"✅ Video sent successfully with SID: {message.sid}")
                    return VideoSendStatus.SUCCESS
                except TwilioRestException as e:
                    logging.error(f"❌ Twilio error sending video: {e}")
                    return VideoSendStatus.FAILED_TO_SEND
                except Exception as e:
                    logging.error(f"❌ Error sending video: {str(e)}")
                    return VideoSendStatus.FAILED_TO_SEND

            # Run the sync function in a thread pool
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, send_video_sync)
                
        except Exception as e:
            logging.error(f"❌ Error sending video: {str(e)}")
            return VideoSendStatus.FAILED_TO_SEND

    async def send_message(self, to_number: str, message: str = None, albums: Dict = None, video_url: str = None):
        """
        Main function to send WhatsApp messages with optional media asynchronously.
        
        Args:
            to_number: The recipient's phone number
            message: Optional text message
            albums: Optional dictionary of image albums to send
            video_url: Optional video URL to send
            
        Returns:
            Dictionary with status information
        """
        status = {
            "text": None,
            "images": [],
            "video": None
        }
        
        # Send text if provided
        if message:
            text_status = await self.send_text(to_number, message)
            status["text"] = text_status.value
            # Add a small delay after sending text before sending media
            await asyncio.sleep(1)
        
        # Send images if provided
        if albums:
            for description, images in albums.items():
                # First send the description text for this album
                if description:
                    desc_status = await self.send_text(to_number, description)
                    # Give Twilio API time to process the message
                    await asyncio.sleep(1)
                    
                # Then send the images for this album
                if images:
                    image_results = await self.send_images(to_number, images)
                    status["images"].extend(image_results)
                    # Add delay between albums
                    await asyncio.sleep(1)
        
        # Send video if provided
        if video_url:
            video_status = await self.send_video(to_number, video_url)
            status["video"] = video_status.value
        
        return status
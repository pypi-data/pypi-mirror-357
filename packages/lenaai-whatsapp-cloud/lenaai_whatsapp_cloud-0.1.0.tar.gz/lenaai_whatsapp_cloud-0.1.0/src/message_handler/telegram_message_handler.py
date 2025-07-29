from datetime import datetime
import json
import logging
from typing import Dict, List, Any
import aiohttp

from src.message_handler.base_message_handler import BaseMessageHandler
from src.utils.config import LENAAI_UPDATE_DB_ENDPOINT
from src.utils.status_enums import MessageSendStatus, VideoSendStatus


class TelegramMessageHandler(BaseMessageHandler):
    """
    Handler for Telegram messaging operations.
    """
    
    def __init__(self, credentials: Dict[str, str]):
        """
        Initialize the Telegram message handler.
        
        Args:
            credentials: Dictionary containing 'bot_token' and 'client_id'
        """
        super().__init__(credentials)
        self.platform = "telegram"
        self.base_url = f"https://api.telegram.org/bot{credentials['bot_token']}"

    async def update_firestore_history(self, session, chat_id: str, message: str):
        """
        Updates Firestore history with the bot's response.
        """
        bot_response_data = {
            "phone_number": chat_id,  # todo For Telegram we use chat_id
            "client_id": self.credentials['client_id'],
            "bot_response": message,
            "timestamp": datetime.utcnow().isoformat(),
            "platform": self.platform
        }

        async with session.post(LENAAI_UPDATE_DB_ENDPOINT, json=bot_response_data) as history_response:
            if history_response.status == 200:
                logging.info("✅ Bot response saved in Firestore history")
            else:
                logging.error(f"❌ Failed to update Firestore history: {history_response.status} - {await history_response.text()}")

    
    async def send_text(self, chat_id: str, message: str):
        """
        Sends a text message through Telegram.
        """
        if not message.strip():
            logging.error("❌ Empty message provided")
            return MessageSendStatus.FAILED_TO_SEND

        try:
            params = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"  # Can use HTML formatting
            }
            
            logging.info(f"Sending text message to Telegram: {params}")
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/sendMessage", params=params) as response:
                    if response.status == 200:
                        logging.info("✅ Telegram text message sent successfully")
                        # Update Firestore history
                        # await self.update_firestore_history(session, chat_id, message)
                        return MessageSendStatus.SUCCESS
                    else:
                        response_text = await response.text()
                        logging.error(f"❌ Failed to send Telegram text. Response: {response.status} - {response_text}")
                        return MessageSendStatus.FAILED_TO_SEND
                
        except Exception as e:
            logging.error(f"❌ Error sending Telegram text: {str(e)}")
            return MessageSendStatus.FAILED_TO_SEND
        
    async def send_image(self, chat_id: str, image_url: str):
        """
        Sends a single image through Telegram.
        
        Args:
            chat_id: The Telegram chat ID
            image_url: The URL of the image to send
            
        Returns:
            Status of the send operation
        """
        try:
            logging.info(f"🚀 Attempting to send Telegram image: {image_url} to {chat_id}")
            
            params = {
                "chat_id": chat_id,
                "photo": image_url,
                # The problem is here - boolean values need to be converted to strings
                "disable_notification": "true"  # Change from True to "true"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/sendPhoto", params=params) as response:
                    response_text = await response.text()
                    
                    if response.status == 200:
                        logging.info(f"✅ Telegram image sent successfully: {image_url}")
                        return {
                            "url": image_url,
                            "status": "success",
                            "message": "Image sent successfully"
                        }
                    else:
                        logging.error(f"❌ Failed to send Telegram image {image_url}. Response: {response.status} - {response_text}")
                        return {
                            "url": image_url,
                            "status": "failed",
                            "message": response_text
                        }
                    
        except Exception as e:
            logging.error(f"❌ Error sending Telegram image: {str(e)}")
            return {
                "url": image_url,
                "status": "failed",
                "message": str(e)
            }

    async def send_images(self, chat_id: str, image_urls: List[str]):
        """
        Sends multiple images through Telegram.
        
        Args:
            chat_id: The Telegram chat ID
            image_urls: List of image URLs to send
            
        Returns:
            List of result dictionaries with status for each image
        """
        results = []
        
        try:
            async with aiohttp.ClientSession() as session:
                for img_url in image_urls:
                    logging.info(f"🚀 Attempting to send Telegram image: {img_url} to {chat_id}")
                    
                    params = {
                        "chat_id": chat_id,
                        "photo": img_url,
                        "disable_notification": "true"  # Changed from boolean True to string "true"
                    }
                    
                    async with session.get(f"{self.base_url}/sendPhoto", params=params) as response:
                        response_text = await response.text()
                        
                        if response.status == 200:
                            logging.info(f"✅ Telegram image sent successfully: {img_url}")
                            
                            results.append({
                                "url": img_url,
                                "status": "success",
                                "message": "Image sent successfully"
                            })
                        else:
                            logging.error(f"❌ Failed to send Telegram image {img_url}. Response: {response.status} - {response_text}")
                            
                            results.append({
                                "url": img_url,
                                "status": "failed",
                                "message": response_text
                            })
                    
        except Exception as e:
            logging.error(f"❌ Error sending Telegram images: {str(e)}")
            
            results.append({
                "url": "unknown",
                "status": "failed",
                "message": str(e)
            })
        
        return results

    async def send_video(self, chat_id: str, video_url: str) -> VideoSendStatus:
        """
        Sends a video through Telegram.
        """
        try:
            params = {
                "chat_id": chat_id,
                "video": video_url
            }
            
            logging.info(f"Sending video to Telegram: {video_url}")
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/sendVideo", params=params) as response:
                    if response.status == 200:
                        logging.info("✅ Telegram video sent successfully")
                        return VideoSendStatus.SUCCESS
                    else:
                        response_text = await response.text()
                        logging.error(f"❌ Failed to send Telegram video. Response: {response.status} - {response_text}")
                        return VideoSendStatus.FAILED_TO_SEND
                
        except Exception as e:
            logging.error(f"❌ Error sending Telegram video: {str(e)}")
            return VideoSendStatus.FAILED_TO_SEND

    async def send_message(self, chat_id: str, message: str = None, albums: Dict = None, video_url: str = None):
        """
        Main function to send Telegram messages with optional media.
        """
        status = {
            "text": None,
            "images": [],
            "video": None
        }
        
        # Send text if provided
        if message:
            text_status = await self.send_text(chat_id, message)
            status["text"] = text_status.value
        
        # Send images if provided
        if albums:
            for unit, images in albums.items():
                # For Telegram, we can send a group of images as an album
                # But first, let's send a text message with the album name
                if unit:
                    await self.send_text(chat_id, f"📷 {unit}")
                
                # Then send the images
                image_results = await self.send_images(chat_id, images)
                status["images"].extend(image_results)
        
        # Send video if provided
        if video_url:
            video_status = await self.send_video(chat_id, video_url)
            status["video"] = video_status.value
        
        return status
        
    async def send_media_group(self, chat_id: str, media_urls: List[str], media_type: str = "photo"):
        """
        Sends a group of media (photos or videos) as an album.
        Telegram allows up to 10 items in a media group.
        
        Args:
            chat_id: The Telegram chat ID
            media_urls: List of media URLs
            media_type: Either "photo" or "video"
            
        Returns:
            Result of the operation
        """
        if not media_urls:
            return []
            
        # Telegram allows max 10 items in a media group
        media_urls = media_urls[:10]
        
        # Create media items
        media = []
        for url in media_urls:
            media.append({
                "type": media_type,
                "media": url
            })
            
        params = {
            "chat_id": chat_id,
            "media": json.dumps(media)
        }
        
        try:
            logging.info(f"Sending media group to Telegram: {media}")
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/sendMediaGroup", json=params) as response:
                    if response.status == 200:
                        logging.info("✅ Telegram media group sent successfully")
                        return {"status": "success", "message": "Media group sent successfully"}
                    else:
                        response_text = await response.text()
                        logging.error(f"❌ Failed to send Telegram media group. Response: {response.status} - {response_text}")
                        return {"status": "failed", "message": response_text}
        except Exception as e:
            logging.error(f"❌ Error sending Telegram media group: {str(e)}")
            return {"status": "failed", "message": str(e)}
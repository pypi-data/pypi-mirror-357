from datetime import datetime
import logging
from typing import Dict, List, Any
import aiohttp
import os
from pathlib import Path

from src.message_handler.base_message_handler import BaseMessageHandler
from src.utils.config import FACEBOOK_GRAPH_API_VERSION, LENAAI_UPDATE_DB_ENDPOINT
from src.utils.status_enums import MessageSendStatus, VideoSendStatus


class MessengerMessageHandler(BaseMessageHandler):
    """
    Handler for Facebook Messenger messaging operations.
    """
    
    def __init__(self, credentials: Dict[str, str]):
        """
        Initialize the Messenger message handler.
        
        Args:
            credentials: Dictionary containing 'page_id' and 'access_token'
        """
        super().__init__(credentials)
        self.platform = "messenger"
        self.base_url = f"https://graph.facebook.com/{FACEBOOK_GRAPH_API_VERSION}/me/messages"
        self.headers = {
            "Authorization": f"Bearer {credentials['access_token']}",
            "Content-Type": "application/json"
        }

    async def update_firestore_history(self, session, recipient_id: str, message: str):
        """
        Updates Firestore history with the bot's response.
        """
        bot_response_data = {
            "phone_number": recipient_id,  # todo For Messenger we use user_id instead of phone_number
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

    
    async def send_text(self, recipient_id: str, message: str):
        """
        Sends a text message through Facebook Messenger.
        """
        if not message.strip():
            logging.error("❌ Empty message provided")
            return MessageSendStatus.FAILED_TO_SEND

        try:
            payload = {
                "recipient": {"id": recipient_id},
                "message": {"text": message},
                "messaging_type": "RESPONSE"
            }
            
            logging.info(f"Sending text message to Messenger: {payload}")
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url, 
                    json=payload, 
                    headers=self.headers,
                    params={"access_token": self.credentials['access_token']}
                ) as response:
                    if response.status == 200:
                        logging.info("✅ Messenger text message sent successfully")
                        # Update Firestore history
                        # await self.update_firestore_history(session, recipient_id, message)
                        return MessageSendStatus.SUCCESS
                    else:
                        response_text = await response.text()
                        logging.error(f"❌ Failed to send Messenger text. Response: {response.status} - {response_text}")
                        return MessageSendStatus.FAILED_TO_SEND
                
        except Exception as e:
            logging.error(f"❌ Error sending Messenger text: {str(e)}")
            return MessageSendStatus.FAILED_TO_SEND
        
    async def send_image(self, recipient_id: str, image_url: str):
        """
        Sends a single image through Facebook Messenger.
        
        Args:
            recipient_id: The recipient's ID
            image_url: The URL of the image to send
            
        Returns:
            Status of the send operation
        """
        try:
            logging.info(f"🚀 Attempting to send Messenger image: {image_url} to {recipient_id}")
            
            payload = {
                "recipient": {"id": recipient_id},
                "message": {
                    "attachment": {
                        "type": "image",
                        "payload": {
                            "url": image_url,
                            "is_reusable": True
                        }
                    }
                },
                "messaging_type": "RESPONSE"
            }

            logging.info(f"📤 Messenger API Payload: {payload}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url, 
                    json=payload, 
                    headers=self.headers,
                    params={"access_token": self.credentials['access_token']}
                ) as response:
                    response_text = await response.text()
                    
                    if response.status == 200:
                        logging.info(f"✅ Messenger image sent successfully: {image_url}")
                        return {
                            "url": image_url,
                            "status": "success",
                            "message": "Image sent successfully"
                        }
                    else:
                        logging.error(f"❌ Failed to send Messenger image {image_url}. Response: {response.status} - {response_text}")
                        return {
                            "url": image_url,
                            "status": "failed",
                            "message": response_text
                        }
                    
        except Exception as e:
            logging.error(f"❌ Error sending Messenger image: {str(e)}")
            return {
                "url": image_url,
                "status": "failed",
                "message": str(e)
            }

    async def upload_attachment(self, attachment_type: str, file_path: Path) -> str:
        """
        Uploads an attachment directly to Facebook's attachment upload API.
        
        Args:
            attachment_type: Type of attachment ('image', 'video', etc.)
            file_path: Path to the file to upload
            
        Returns:
            Attachment ID if successful, None otherwise
        """
        try:
            upload_url = f"https://graph.facebook.com/{FACEBOOK_GRAPH_API_VERSION}/me/message_attachments"
            
            # Determine mime type based on file extension
            file_extension = os.path.splitext(file_path)[1].lower()
            if file_extension in ['.jpg', '.jpeg']:
                mime_type = 'image/jpeg'
            elif file_extension == '.png':
                mime_type = 'image/png'
            elif file_extension == '.gif':
                mime_type = 'image/gif'
            elif file_extension in ['.mp4', '.mov']:
                mime_type = 'video/mp4'
            else:
                mime_type = 'application/octet-stream'
            
            logging.info(f"Uploading {attachment_type} attachment from {file_path} with mime type {mime_type}")
            
            # Read the file data
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Create form data for the upload
            form = aiohttp.FormData()
            form.add_field('message', '{"attachment":{"type":"' + attachment_type + '","payload":{"is_reusable":true}}}')
            form.add_field('filedata', file_data, 
                          filename=os.path.basename(file_path),
                          content_type=mime_type)
            
            # Upload to Facebook
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    upload_url,
                    data=form,
                    params={"access_token": self.credentials['access_token']}
                ) as response:
                    if response.status != 200:
                        response_text = await response.text()
                        logging.error(f"Failed to upload attachment: {response.status} - {response_text}")
                        return None
                    
                    response_json = await response.json()
                    attachment_id = response_json.get("attachment_id")
                    
                    if not attachment_id:
                        logging.error("No attachment ID received from Messenger")
                        return None
                    
                    logging.info(f"✅ Successfully uploaded attachment: {attachment_id}")
                    return attachment_id
                    
        except Exception as e:
            logging.error(f"Error uploading attachment: {str(e)}")
            return None

    async def send_attachment_by_id(self, recipient_id: str, attachment_id: str, attachment_type: str):
        """
        Sends a message with an attachment that was previously uploaded.
        
        Args:
            recipient_id: The recipient's ID
            attachment_id: The attachment ID from a previous upload
            attachment_type: Type of attachment ('image', 'video', etc.)
            
        Returns:
            Status of the send operation
        """
        try:
            payload = {
                "recipient": {"id": recipient_id},
                "message": {
                    "attachment": {
                        "type": attachment_type,
                        "payload": {
                            "attachment_id": attachment_id
                        }
                    }
                },
                "messaging_type": "RESPONSE"
            }
            
            logging.info(f"Sending attachment by ID to Messenger: {attachment_id}")
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url, 
                    json=payload, 
                    headers=self.headers,
                    params={"access_token": self.credentials['access_token']}
                ) as response:
                    if response.status == 200:
                        logging.info("✅ Messenger attachment sent successfully")
                        return {
                            "attachment_id": attachment_id,
                            "status": "success",
                            "message": "Attachment sent successfully"
                        }
                    else:
                        response_text = await response.text()
                        logging.error(f"❌ Failed to send Messenger attachment. Response: {response.status} - {response_text}")
                        return {
                            "attachment_id": attachment_id,
                            "status": "failed",
                            "message": response_text
                        }
                
        except Exception as e:
            logging.error(f"❌ Error sending Messenger attachment: {str(e)}")
            return {
                "attachment_id": attachment_id,
                "status": "failed",
                "message": str(e)
            }

    async def upload_and_send_image(self, recipient_id: str, image_path: Path):
        """
        Uploads an image file to Facebook and then sends it.
        
        Args:
            recipient_id: The recipient's ID
            image_path: Path to the image file
            
        Returns:
            Status dictionary
        """
        try:
            logging.info(f"Uploading and sending image from {image_path} to {recipient_id}")
            
            # 1. Upload the image to get an attachment ID
            attachment_id = await self.upload_attachment("image", image_path)
            
            if not attachment_id:
                return {
                    "url": str(image_path),
                    "status": "failed",
                    "message": "Failed to upload image to Facebook"
                }
            
            # 2. Send the image using the attachment ID
            result = await self.send_attachment_by_id(recipient_id, attachment_id, "image")
            
            # 3. Format the response to match the expected format
            return {
                "url": str(image_path),
                "status": result.get("status", "failed"),
                "message": result.get("message", "Unknown error")
            }
            
        except Exception as e:
            logging.error(f"❌ Error in upload and send image: {str(e)}")
            return {
                "url": str(image_path),
                "status": "failed",
                "message": str(e)
            }

    async def send_images(self, recipient_id: str, image_urls: List[str]):
        """
        Sends images through Facebook Messenger.
        """
        results = []
        
        try:
            async with aiohttp.ClientSession() as session:
                for img_url in image_urls:
                    logging.info(f"🚀 Attempting to send Messenger image: {img_url} to {recipient_id}")
                    
                    payload = {
                        "recipient": {"id": recipient_id},
                        "message": {
                            "attachment": {
                                "type": "image",
                                "payload": {
                                    "url": img_url,
                                    "is_reusable": True
                                }
                            }
                        },
                        "messaging_type": "RESPONSE"
                    }

                    logging.info(f"📤 Messenger API Payload: {payload}")
                    
                    async with session.post(
                        self.base_url, 
                        json=payload, 
                        headers=self.headers,
                        params={"access_token": self.credentials['access_token']}
                    ) as response:
                        response_text = await response.text()
                        
                        if response.status == 200:
                            logging.info(f"✅ Messenger image sent successfully: {img_url}")
                            
                            results.append({
                                "url": img_url,
                                "status": "success",
                                "message": "Image sent successfully"
                            })
                        else:
                            logging.error(f"❌ Failed to send Messenger image {img_url}. Response: {response.status} - {response_text}")
                            
                            results.append({
                                "url": img_url,
                                "status": "failed",
                                "message": response_text
                            })
                    
        except Exception as e:
            logging.error(f"❌ Error sending Messenger images: {str(e)}")
            
            results.append({
                "url": "unknown",
                "status": "failed",
                "message": str(e)
            })
        
        return results

    async def send_video(self, recipient_id: str, video_url: str) -> VideoSendStatus:
        """
        Sends a video through Facebook Messenger.
        """
        try:
            # Prepare and send the video
            payload = {
                "recipient": {"id": recipient_id},
                "message": {
                    "attachment": {
                        "type": "video",
                        "payload": {
                            "url": video_url,
                            "is_reusable": True
                        }
                    }
                },
                "messaging_type": "RESPONSE"
            }
            
            logging.info(f"Sending video to Messenger: {video_url}")
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url, 
                    json=payload, 
                    headers=self.headers,
                    params={"access_token": self.credentials['access_token']}
                ) as response:
                    if response.status == 200:
                        logging.info("✅ Messenger video sent successfully")
                        return VideoSendStatus.SUCCESS
                    else:
                        response_text = await response.text()
                        logging.error(f"❌ Failed to send Messenger video. Response: {response.status} - {response_text}")
                        return VideoSendStatus.FAILED_TO_SEND
                
        except Exception as e:
            logging.error(f"❌ Error sending Messenger video: {str(e)}")
            return VideoSendStatus.FAILED_TO_SEND

    async def send_message(self, recipient_id: str, message: str = None, albums: Dict = None, video_url: str = None):
        """
        Main function to send Messenger messages with optional media.
        """
        status = {
            "text": None,
            "images": [],
            "video": None
        }
        
        # Send text if provided
        if message:
            text_status = await self.send_text(recipient_id, message)
            status["text"] = text_status.value
        
        # Send images if provided
        if albums:
            for unit, images in albums.items():
                # For Messenger, let's send a text message with the album name first
                if unit:
                    await self.send_text(recipient_id, f"📷 {unit}")
                
                image_results = await self.send_images(recipient_id, images)
                status["images"].extend(image_results)
        
        # Send video if provided
        if video_url:
            video_status = await self.send_video(recipient_id, video_url)
            status["video"] = video_status.value
        
        return status
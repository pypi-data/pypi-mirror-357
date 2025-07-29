import logging
import ast
import json
import asyncio
import os
import time
from typing import Dict, Any, List, Optional
import aiofiles
import httpx

from src.webhook_handler.base_webhook_handler import BaseWebhookHandler
from src.utils.config import LENAAI_CHAT_ENDPOINT, LENAAI_LANGGRAPH_ENDPOINT, LENAAI_VOICE_PROCESS_ENDPOINT

class MessengerWebhookHandler(BaseWebhookHandler):
    """
    A class to handle Facebook Messenger webhook operations.
    """
    
    def __init__(self, credentials: Dict[str, str]):
        """
        Initialize the Messenger webhook handler.
        """
        super().__init__(credentials, "messenger")
    
    def extract_image_urls(self, images_data) -> List[str]:
        """
        Extract image URLs from either a JSON string or a list of image objects.
        """
        if not images_data:
            return []
        
        try:
            # If images_data is already a list, use it directly
            if isinstance(images_data, list):
                images_list = images_data
            # If it's a string, parse it as before
            elif isinstance(images_data, str):
                images_data = images_data.strip()
                if images_data.startswith("{") and images_data.endswith("}"):
                    images_data = "[" + images_data + "]"  # Convert single dict to list
                
                try:
                    images_list = json.loads(images_data)
                except json.JSONDecodeError:
                    images_list = ast.literal_eval(images_data)
            else:
                logging.error(f"Unexpected type for images_data: {type(images_data)}")
                return []
            
            # Ensure it's a list
            if not isinstance(images_list, list):
                images_list = [images_list]

            # Extract URLs
            valid_urls = [
                image['url'] for image in images_list
                if isinstance(image, dict) and 'url' in image
            ]

            return valid_urls
        except (ValueError, SyntaxError, json.JSONDecodeError) as e:
            logging.error(f"❌ Error parsing images data: {str(e)}")
            return []

    async def process_chat_api_response(self, sender_id: str, response_data: Dict):
        """
        Process the response from the chat API and send appropriate messages.
        """
        try:
            message = response_data.get("message", "Sorry, I couldn't process your message.")

            # Check if auto-reply is off
            if message == "Auto-reply is off":
                logging.info("Auto-reply is off. No response will be sent.")
                return
            
            # First send the main message
            await self.message_handler.send_text(sender_id, message)
            
            # Extract properties and their images
            properties = response_data.get("properties", []) or []
            
            # Process properties and send images for each property separately with descriptions
            for prop in properties:
                property_id = prop.get("property_id", "unknown")
                metadata = prop.get("metadata", {})
                description = prop.get("description", "")
                
                # Create a short description for the property
                short_desc = f"Property {property_id} - {metadata.get('compound', '')}"
                
                # Extract image URLs using a safer approach
                images_data = self.extract_image_urls(metadata.get("images", ""))
                
                if images_data:
                    # Send property description
                    await self.message_handler.send_text(sender_id, description)
                    # if description:
                    #     await self.message_handler.send_text(sender_id, description)
                    
                    await asyncio.sleep(2)
                    # Send images for this property
                    for image_url in images_data:
                        try:
                            # Use the send_images method with a single image
                            await self.message_handler.send_images(sender_id, [image_url])
                            # Small delay to prevent rate limiting
                            await asyncio.sleep(0.5)
                        except Exception as img_error:
                            logging.error(f"❌ Error sending image {image_url}: {str(img_error)}")
        except Exception as e:
            logging.error(f"❌ Error processing chat API response: {str(e)}", exc_info=True)
            await self.message_handler.send_text(
                sender_id, 
                "Sorry, I encountered an error processing the response."
            )
    
    async def process_text_message(self, sender_id: str, user_message: str):
        """
        Process Messenger text messages and send response with property images if available.
        """
        logging.info(f"Received Messenger message from {sender_id}: {user_message}")

        try:
            async with httpx.AsyncClient(timeout=50.0) as client:
                # Request with client_id and platform
                chat_response = await client.post(
                    LENAAI_LANGGRAPH_ENDPOINT, 
                    json={
                        "query": user_message, 
                        "phone_number": sender_id,
                        "client_id": self.credentials['client_id'],
                        "platform": "messenger"
                    }
                )
                if chat_response.status_code == 200:
                    response_data = chat_response.json()
                    logging.info(f"✅ Chat response {response_data}")
                    
                    await self.process_chat_api_response(sender_id, response_data)
                else:
                    logging.error(f"❌ Failed to get chat response: {chat_response.text}")
                    await self.message_handler.send_text(
                        sender_id, 
                        "I'm having trouble processing your message right now."
                    )
        except Exception as e:
            logging.error(f"❌ Error in chat processing: {str(e)}")
            await self.message_handler.send_text(
                sender_id, 
                "Sorry, can you please try again later?"
            )

    async def get_media_url(self, media_id_or_url: str) -> Optional[str]:
        """
        Retrieve the URL for a Messenger media item using its ID,
        or return the URL directly if it's already a URL.
        
        Args:
            media_id_or_url: Either a media ID or a direct URL
            
        Returns:
            Media URL or None if failed
        """
        # If it's already a URL, just return it
        if media_id_or_url.startswith("http"):
            logging.info(f"Media is already a URL: {media_id_or_url}")
            return media_id_or_url
            
        # Otherwise, treat it as an attachment ID and get the URL
        url = f"https://graph.facebook.com/v19.0/{media_id_or_url}"
        headers = {
            "Authorization": f"Bearer {self.credentials['access_token']}"
        }
        
        try:
            logging.info(f"Getting media URL for ID: {media_id_or_url}")
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                logging.info(f"Media URL response: Status {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    media_url = data.get("url")
                    logging.info(f"Retrieved media URL: {media_url}")
                    return media_url
                else:
                    logging.error(f"Failed to get media URL: {response.text}")
                    return None
        except Exception as e:
            logging.error(f"Error getting media URL: {str(e)}")
            return None
    
    async def download_media(self, media_url: str, save_path: str) -> Optional[str]:
        """
        Download media from the given URL and save it to a file.
        
        Args:
            media_url: URL of the media to download
            save_path: Path where to save the file (without extension)
            
        Returns:
            Full path to the downloaded file, or None if download failed
        """
        try:
            # Log detailed debug info
            logging.info(f"Downloading media from URL: {media_url}")
            
            # Try a HEAD request first to get info about the file
            async with httpx.AsyncClient() as client:
                try:
                    head_response = await client.head(media_url)
                    logging.info(f"HEAD response status: {head_response.status_code}")
                    logging.info(f"HEAD response headers: {dict(head_response.headers)}")
                except Exception as e:
                    logging.warning(f"HEAD request failed: {str(e)}")
            
            # Attempt to download the file
            async with httpx.AsyncClient() as client:
                response = await client.get(media_url)
                
                # Log detailed response info
                logging.info(f"GET response status: {response.status_code}")
                logging.info(f"Content-Type: {response.headers.get('Content-Type')}")
                logging.info(f"Content length: {len(response.content)} bytes")
                
                if response.status_code == 200:
                    content_type = response.headers.get("Content-Type", "")
                    logging.info(f"Detected content type: {content_type}")
                    
                    # Determine file extension based on content type
                    if "ogg" in content_type or "audio/ogg" in content_type:
                        ext = ".ogg"
                    elif "mp3" in content_type or "audio/mpeg" in content_type:
                        ext = ".mp3"
                    elif "mp4" in content_type or "video/mp4" in content_type:
                        ext = ".mp4"  # Facebook often sends audio as MP4
                    elif "wav" in content_type or "audio/wav" in content_type:
                        ext = ".wav"
                    else:
                        # Default to mp3 if content type is not recognized
                        ext = ".mp3"
                        logging.warning(f"Unrecognized content type: {content_type}, defaulting to {ext}")

                    save_path_with_ext = save_path + ext
                    logging.info(f"Saving to: {save_path_with_ext}")
                    
                    # Save the file
                    async with aiofiles.open(save_path_with_ext, "wb") as f:
                        await f.write(response.content)

                    # Verify file was saved correctly
                    if os.path.exists(save_path_with_ext):
                        file_size = os.path.getsize(save_path_with_ext)
                        logging.info(f"✅ Media downloaded successfully: {save_path_with_ext}, size: {file_size} bytes")
                        return save_path_with_ext
                    else:
                        logging.error(f"❌ File was not saved correctly: {save_path_with_ext}")
                        return None
                else:
                    logging.error(f"❌ Failed to download media: Status {response.status_code}")
                    if response.status_code >= 400:
                        logging.error(f"Error response: {response.text[:1000]}")
                    return None
        except Exception as e:
            logging.error(f"❌ Error downloading media: {str(e)}", exc_info=True)
            return None
    
    async def process_voice_message(self, sender_id: str, media_id_or_url: str):
        """
        Process Messenger voice messages and send response.
        
        Args:
            sender_id: The sender's ID
            media_id_or_url: Either a media ID or a direct URL to the audio
        """
        try:
            # Send acknowledgment to user
            await self.message_handler.send_text(
                sender_id,
                "جارى معالجة رسالتك الصوتيه 🧏 وسوف ارد عليك حالا ⌛️⏳"
            )
            
            # Get the audio URL if needed (or use directly if already a URL)
            audio_url = media_id_or_url
            if not media_id_or_url.startswith("http"):
                # It's an ID, not a URL, so get the URL
                audio_url = await self.get_media_url(media_id_or_url)
            
            if not audio_url:
                logging.error(f"❌ Could not retrieve audio URL for: {media_id_or_url}")
                await self.message_handler.send_text(
                    sender_id, 
                    "Sorry, I couldn't process your voice message."
                )
                return
                
            logging.info(f"Processing voice message from {sender_id}, URL: {audio_url}")
            
            # Send to voice process endpoint
            async with httpx.AsyncClient(timeout=60.0) as client:
                logging.info(f"Sending to voice process endpoint: {audio_url}")
                
                # Prepare the request
                voice_request = {
                    "media_url": audio_url,
                    "phone_number": sender_id,
                    "client_id": self.credentials['client_id'],
                    "platform": "messenger",
                    "access_token": self.credentials['access_token']
                }
                
                # Call the voice processing endpoint
                try:
                    # Make the actual API call
                    voice_process_response = await client.post(
                        LENAAI_VOICE_PROCESS_ENDPOINT,  # Change to your actual endpoint
                        json=voice_request,
                        timeout=60.0
                    )
                    
                    # Handle the response
                    if voice_process_response.status_code == 200:
                        response_data = voice_process_response.json()
                        logging.info(f"✅ Voice message processed for {sender_id}")
                        
                        # Extract the message and properties
                        message = response_data.get("message", "")
                        properties = response_data.get("properties", None)
                        
                        # Create a response object with the necessary fields
                        chat_response = {
                            "message": message,
                            "properties": properties
                        }
                        
                        # Process the response
                        await self.process_chat_api_response(sender_id, chat_response)
                    else:
                        logging.error(f"❌ Voice process failed: {voice_process_response.status_code} {voice_process_response.text[:100]}")
                        await self.message_handler.send_text(
                            sender_id, 
                            "Sorry, I couldn't process your voice message."
                        )
                except Exception as req_error:
                    logging.error(f"❌ Error calling voice process endpoint: {str(req_error)}", exc_info=True)
                    await self.message_handler.send_text(
                        sender_id, 
                        "Sorry, I encountered an error processing your voice message."
                    )
            
        except Exception as e:
            logging.error(f"❌ Error processing voice message: {e}", exc_info=True)
            try:
                await self.message_handler.send_text(
                    sender_id, 
                    "Sorry, there was an error processing your voice message."
                )
            except Exception as send_error:
                logging.error(f"❌ Failed to send error message: {send_error}")

    async def process_attachment(self, sender_id: str, attachment: Dict[str, Any]):
        """
        Process Messenger attachment messages (images, videos, etc.)
        """
        attachment_type = attachment.get("type", "").lower()
        payload = attachment.get("payload", {})
        
        logging.info(f"Processing {attachment_type} attachment: {json.dumps(payload, indent=2)}")
        
        if attachment_type == "audio":
            # Get the URL directly from the payload
            url = payload.get("url")
            if url:
                logging.info(f"Audio URL from payload: {url}")
                await self.process_voice_message(sender_id, url)
            else:
                # Try to get attachment ID
                attachment_id = payload.get("attachment_id")
                if attachment_id:
                    logging.info(f"Audio attachment ID: {attachment_id}")
                    await self.process_voice_message(sender_id, attachment_id)
                else:
                    logging.error(f"❌ No URL or attachment ID found in payload: {payload}")
                    await self.message_handler.send_text(
                        sender_id, 
                        "I received your audio, but couldn't process it. Please try again."
                    )
        elif attachment_type == "image":
            await self.message_handler.send_text(sender_id, "I received your image, but I can only process text and voice messages at the moment.")
        elif attachment_type == "video":
            await self.message_handler.send_text(sender_id, "I received your video, but I can only process text and voice messages at the moment.")
        else:
            await self.message_handler.send_text(sender_id, "I received your attachment, but I can only process text and voice messages at the moment.")
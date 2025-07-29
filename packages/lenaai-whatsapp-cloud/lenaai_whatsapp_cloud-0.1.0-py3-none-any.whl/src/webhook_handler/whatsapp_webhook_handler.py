import logging
import ast
import json
import asyncio
import os
import time
from typing import Optional, Dict, List
import aiofiles
import httpx

from src.webhook_handler.base_webhook_handler import BaseWebhookHandler
from src.utils.config import FACEBOOK_GRAPH_API_VERSION, LENAAI_CHAT_ENDPOINT, LENAAI_VOICE_PROCESS_ENDPOINT, LENAAI_LANGGRAPH_ENDPOINT

class WhatsAppWebhookHandler(BaseWebhookHandler):
    """
    A class to handle WhatsApp webhook operations.
    """
    
    def __init__(self, credentials: dict):
        """
        Initialize the WhatsApp webhook handler.
        """
        super().__init__(credentials, "whatsapp")
    
    async def get_media_url(self, media_id: str) -> Optional[str]:
        """
        Retrieve the URL for a WhatsApp media item using its ID.
        """
        url = f"https://graph.facebook.com/{FACEBOOK_GRAPH_API_VERSION}/{media_id}"
        headers = {
            "Authorization": f"Bearer {self.credentials['access_token']}"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("url")
                else:
                    logging.error(f"Failed to get media URL: {response.text}")
                    return None
        except Exception as e:
            logging.error(f"Error getting media URL: {str(e)}")
            return None

    async def download_media(self, media_url: str, save_path: str) -> Optional[str]:
        """
        Download media from the given URL and save it to a file.
        """
        headers = {
            "Authorization": f"Bearer {self.credentials['access_token']}"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(media_url, headers=headers)
                if response.status_code == 200:
                    content_type = response.headers.get("Content-Type", "")
                    ext = ".ogg" if "ogg" in content_type else ".mp3" if "mp3" in content_type else ".wav"

                    save_path_with_ext = save_path + ext
                    async with aiofiles.open(save_path_with_ext, "wb") as f:
                        await f.write(await response.aread())

                    logging.info(f"✅ Media downloaded successfully: {save_path_with_ext}")
                    return save_path_with_ext
                else:
                    logging.error(f"❌ Failed to download media: {response.text}")
                    return None
        except Exception as e:
            logging.error(f"❌ Error downloading media: {e}")
            return None

    def extract_image_urls(self, images_str) -> List[str]:
        """
        Extract image URLs from the complex image string format.
        Handles both string representations and direct list/dict objects.
        """
        if not images_str:
            return []
        
        try:
            # Handle the case when images_str is already a list of dictionaries
            if isinstance(images_str, list):
                return [image['url'] for image in images_str if isinstance(image, dict) and 'url' in image]
                
            # Handle the case when images_str is a single dictionary
            if isinstance(images_str, dict) and 'url' in images_str:
                return [images_str['url']]
                
            # Handle the case when images_str is a string representation
            if isinstance(images_str, str):
                images_str = images_str.strip()
                # Try to parse JSON first
                try:
                    parsed_data = json.loads(images_str)
                except json.JSONDecodeError:
                    # Fall back to ast.literal_eval if JSON parsing fails
                    try:
                        parsed_data = ast.literal_eval(images_str)
                    except (ValueError, SyntaxError):
                        logging.error(f"❌ Failed to parse image string: {images_str}")
                        return []
                        
                # Handle the parsed data based on its type
                if isinstance(parsed_data, list):
                    return [image['url'] for image in parsed_data if isinstance(image, dict) and 'url' in image]
                elif isinstance(parsed_data, dict) and 'url' in parsed_data:
                    return [parsed_data['url']]
                    
            return []
        except Exception as e:
            logging.error(f"❌ Error extracting image URLs: {str(e)}")
            return []

    async def process_chat_api_response(self, from_number: str, response_data: Dict):
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
            await self.message_handler.send_text(from_number, message)
            
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
                images_data = self.extract_image_urls(metadata.get("images", []))
                
                if images_data:
                    # Send property description
                    # await self.message_handler.send_text(from_number, short_desc)
                    if description:
                        await self.message_handler.send_text(from_number, description)

                    await asyncio.sleep(2)

                    # Send images for this property
                    for image_url in images_data:
                        try:
                            # Use the send_images method with a single image
                            await self.message_handler.send_images(from_number, [image_url])
                            # Small delay to prevent rate limiting
                            await asyncio.sleep(0.5)
                        except Exception as img_error:
                            logging.error(f"❌ Error sending image {image_url}: {str(img_error)}")
        except Exception as e:
            logging.error(f"❌ Error processing chat API response: {str(e)}", exc_info=True)
            await self.message_handler.send_text(
                from_number, 
                "Sorry, I encountered an error processing the response."
            )

    async def process_text_message(self, from_number: str, user_message: str):
        """
        Process WhatsApp text messages and send response with property images if available.
        """
        logging.info(f"Received WhatsApp message from {from_number}: {user_message}")

        try:
            async with httpx.AsyncClient(timeout=50.0) as client:
                # Request with client_id and platform
                chat_response = await client.post(
                    LENAAI_LANGGRAPH_ENDPOINT, 
                    json={
                        "query": user_message, 
                        "phone_number": from_number, # todo change user_id
                        "client_id": self.credentials['client_id'],
                        "platform": "whatsapp"
                    }
                )
                if chat_response.status_code == 200:
                    response_data = chat_response.json()
                    logging.info(f"✅ Chat response {response_data}")
                    
                    await self.process_chat_api_response(from_number, response_data)
                else:
                    logging.error(f"❌ Failed to get chat response: {chat_response.text}")
                    await self.message_handler.send_text(
                        from_number, 
                        "I'm having trouble processing your message right now."
                    )
        except Exception as e:
            logging.error(f"❌ Error in chat processing: {str(e)}")
            await self.message_handler.send_text(
                from_number, 
                "Sorry, can you please try again later?"
            )

    async def process_voice_message(self, from_number: str, media_id: str):
        """
        Process WhatsApp voice messages and send response with property images if available.
        """
        try:
            # Send acknowledgment to user
            await self.message_handler.send_text(
                from_number, 
                "جارى معالجة رسالتك الصوتيه 🧏 وسوف ارد عليك حالا ⌛️⏳"
            )
            
            # Step 1: Get the media URL
            audio_url = await self.get_media_url(media_id)
            if not audio_url:
                logging.error(f"❌ Could not retrieve audio URL for media_id: {media_id}")
                await self.message_handler.send_text(
                    from_number, 
                    "Sorry, I couldn't process your voice message."
                )
                return
                    
            logging.info(f"Processing voice message from {from_number}, URL: {audio_url}")
            
            # Create temp directory if it doesn't exist
            os.makedirs("temp_media", exist_ok=True)
            
            # Generate a unique filename
            timestamp = int(time.time())
            temp_file_path = f"temp_media/whatsapp_audio_{timestamp}"
            
            # Step 2: Try downloading the file to verify access
            try:
                # Test a HEAD request first
                async with httpx.AsyncClient() as client:
                    headers = {"Authorization": f"Bearer {self.credentials['access_token']}"}
                    head_response = await client.head(audio_url, headers=headers)
                    logging.info(f"HEAD response status: {head_response.status_code}")
                    logging.info(f"HEAD response headers: {dict(head_response.headers)}")
            except Exception as e:
                logging.warning(f"HEAD request failed: {str(e)}")
            
            # Step 3: Process using the voice processing endpoint
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Log the API call
                logging.info(f"Sending request to voice process endpoint with URL: {audio_url}")
                logging.info(f"Request data: phone_number={from_number}, client_id={self.credentials['client_id']}, platform=whatsapp")
                
                # Make the API call
                chat_voice_response = await client.post(
                    LENAAI_VOICE_PROCESS_ENDPOINT,
                    json={
                        "media_url": audio_url, 
                        "phone_number": from_number,
                        "client_id": self.credentials['client_id'],
                        "platform": "whatsapp",
                        "access_token": self.credentials['access_token']
                    }
                )
                
                # Log the response
                logging.info(f"Voice process response status: {chat_voice_response.status_code}")
                
                if chat_voice_response.status_code == 200:
                    response_data = chat_voice_response.json()
                    logging.info(f"✅ Voice message processed for {from_number}")
                    
                    await self.process_chat_api_response(from_number, response_data)
                else:
                    logging.error(f"❌ Failed to process voice message: {chat_voice_response.text[:500]}")
                    await self.message_handler.send_text(
                        from_number, 
                        "Sorry, I couldn't process your voice message."
                    )
        except Exception as e:
            logging.error(f"❌ Error processing voice message: {e}", exc_info=True)
            try:
                await self.message_handler.send_text(
                    from_number, 
                    "Sorry, there was an error processing your voice message."
                )
            except Exception as send_error:
                logging.error(f"❌ Failed to send error message: {send_error}")
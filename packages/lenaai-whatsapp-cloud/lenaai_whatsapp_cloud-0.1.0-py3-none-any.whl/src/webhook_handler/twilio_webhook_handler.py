import logging
import os
import time
import httpx
import aiofiles
import asyncio
from typing import Dict, Optional, List

from src.webhook_handler.base_webhook_handler import BaseWebhookHandler
from src.utils.config import LENAAI_CHAT_ENDPOINT, LENAAI_LANGGRAPH_ENDPOINT, LENAAI_VOICE_PROCESS_ENDPOINT

class TwilioWebhookHandler(BaseWebhookHandler):
    """
    A class to handle Twilio WhatsApp webhook operations.
    """
    
    def __init__(self, credentials: dict):
        """
        Initialize the Twilio webhook handler.
        """
        super().__init__(credentials, "twilio_whatsapp")
    
    async def download_media(self, media_url: str, save_path: str) -> Optional[str]:
        """
        Download media from the given URL and save it to a file.
        """
        # Basic auth with account_sid and auth_token
        auth = (self.credentials['account_sid'], self.credentials['auth_token'])

        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                logging.info(f"Downloading media from URL: {media_url}")
                response = await client.get(media_url, auth=auth)
                
                if response.status_code == 200:
                    # Get file extension from Content-Type or URL
                    content_type = response.headers.get("Content-Type", "")
                    logging.info(f"Downloaded content type: {content_type}")
                    
                    # Determine extension based on content type
                    if "audio/ogg" in content_type:
                        ext = ".ogg"
                    elif "audio/mpeg" in content_type or "audio/mp3" in content_type:
                        ext = ".mp3"
                    elif "audio/wav" in content_type:
                        ext = ".wav"
                    else:
                        # Default to ogg if content type is unknown
                        ext = ".ogg"
                        logging.info(f"Using default extension .ogg for content type: {content_type}")

                    save_path_with_ext = save_path + ext
                    async with aiofiles.open(save_path_with_ext, "wb") as f:
                        await f.write(response.content)

                    file_size = os.path.getsize(save_path_with_ext)
                    logging.info(f"✅ Media downloaded successfully: {save_path_with_ext}, size: {file_size} bytes")
                    return save_path_with_ext
                else:
                    logging.error(f"❌ Failed to download media: Status code {response.status_code}")
                    logging.error(f"Response: {response.text[:500]}")
                    return None
        except Exception as e:
            logging.error(f"❌ Error downloading media: {str(e)}")
            return None

    async def extract_image_urls(self, images_data):
        """
        Extract image URLs from the properties data.
        
        Args:
            images_data: List of image objects with URL information
            
        Returns:
            List of image URLs
        """
        if not images_data:
            logging.warning("No image data provided to extract_image_urls")
            return []
        
        urls = []
        try:
            for img in images_data:
                if isinstance(img, dict) and 'url' in img:
                    url = img.get('url')
                    if url and isinstance(url, str):
                        urls.append(url)
            
            num_urls = len(urls)
            if num_urls > 0:
                logging.info(f"✅ Extracted {num_urls} image URLs")
                # Log only first 2 URLs to avoid cluttering logs
                if num_urls > 0:
                    logging.info(f"First URL: {urls[0]}")
                if num_urls > 1:
                    logging.info(f"Second URL: {urls[1]}")
            else:
                logging.warning("⚠️ No valid image URLs found in the data")
                
            return urls
        except Exception as e:
            logging.error(f"❌ Error extracting image URLs: {str(e)}")
            return []

    async def process_chat_api_response(self, from_number: str, response_data: Dict):
        """
        Process the response from the chat API and send appropriate messages.
        Uses send_images to batch send all images for each property.
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
            
            # Process properties one at a time, sending all images for each property together
            for prop in properties:
                property_id = prop.get("property_id", "unknown")
                metadata = prop.get("metadata", {})
                description = prop.get("description", "")
                
                # Create a short description for the property
                short_desc = f"Property {property_id} - {metadata.get('compound', '')}"
                logging.info(f"Processing images for property: {short_desc}")
                
                # Extract image URLs
                images = metadata.get("images", [])
                logging.info(f"Found {len(images)} image objects for property {property_id}")
                
                # Extract image URLs first to check if there are any to send
                images_data = await self.extract_image_urls(images)
                
                if images_data:
                    # Send the property description
                    await self.message_handler.send_text(from_number, description)
                    
                    # Wait to ensure the description is sent before starting to send images
                    await asyncio.sleep(2)
                    
                    # Use send_images to send all images for this property in a batch
                    logging.info(f"Sending {len(images_data)} images for property {property_id} using send_images")
                    results = await self.message_handler.send_images(from_number, images_data)
                    
                    # Log results
                    success_count = sum(1 for r in results if r.get("status") == "success")
                    logging.info(f"✅ Successfully sent {success_count}/{len(images_data)} images for property {property_id}")
                    
                    # Add a delay between properties
                    await asyncio.sleep(3)
                else:
                    logging.warning(f"⚠️ No images to send for property {property_id}")
        except Exception as e:
            logging.error(f"❌ Error processing chat API response: {str(e)}")
            await self.message_handler.send_text(
                from_number, 
                "Sorry, I encountered an error processing the response."
            )

    async def process_text_message(self, from_number: str, user_message: str):
        """
        Process Twilio WhatsApp text messages and send response with property images if available.
        """
        logging.info(f"Received Twilio WhatsApp message from {from_number}: {user_message}")

        # Remove 'whatsapp:' prefix if present
        cleaned_number = from_number
        if cleaned_number.startswith('whatsapp:'):
            cleaned_number = cleaned_number[9:]  # Remove 'whatsapp:' prefix

        try:
            async with httpx.AsyncClient(timeout=50.0) as client:
                # Request with client_id and platform
                chat_response = await client.post(
                    LENAAI_LANGGRAPH_ENDPOINT, 
                    json={
                        "query": user_message, 
                        "phone_number": cleaned_number,
                        "client_id": self.credentials['client_id'],
                        "platform": "twilio_whatsapp"
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

    async def process_voice_message(self, from_number: str, media_url: str):
        """
        Process Twilio WhatsApp voice messages and send response with property images if available.
        """
        try:
            # Send acknowledgment to user
            await self.message_handler.send_text(
                from_number, 
                "جارى معالجة رسالتك الصوتيه 🧏 وسوف ارد عليك حالا ⌛️⏳"
            )
            
            logging.info(f"Processing voice message from {from_number}, URL: {media_url}")
            
            # Create temp directory if it doesn't exist
            os.makedirs("temp_media", exist_ok=True)
            
            # Generate a unique filename
            timestamp = int(time.time())
            temp_file_path = f"temp_media/twilio_audio_{timestamp}"
            
            # Step 1: Download the audio file
            downloaded_file = await self.download_media(media_url, temp_file_path)
            if not downloaded_file:
                logging.error(f"❌ Failed to download voice message from: {media_url}")
                await self.message_handler.send_text(
                    from_number, 
                    "Sorry, I couldn't download your voice message."
                )
                return
            
            # Remove 'whatsapp:' prefix if present
            cleaned_number = from_number
            if cleaned_number.startswith('whatsapp:'):
                cleaned_number = cleaned_number[9:]  # Remove 'whatsapp:' prefix
            
            # Step 2: Process using the voice processing endpoint with file upload
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    logging.info(f"Sending voice file to processing endpoint: {downloaded_file}")
                    
                    # Use the multipart/form-data endpoint for file uploads
                    files = {'file': open(downloaded_file, 'rb')}
                    form_data = {
                        'phone_number': cleaned_number,
                        'client_id': self.credentials['client_id'],
                        'platform': 'twilio_whatsapp'
                    }
                    
                    # Send to the dedicated file upload endpoint
                    voice_process_response = await client.post(
                        LENAAI_VOICE_PROCESS_ENDPOINT,
                        data=form_data,
                        files=files
                    )
                    
                    # Close the file
                    files['file'].close()
                    
                    # Process the response
                    logging.info(f"Voice process response status: {voice_process_response.status_code}")
                    
                    if voice_process_response.status_code == 200:
                        response_data = voice_process_response.json()
                        logging.info(f"✅ Voice message processed for {from_number}")
                        
                        await self.process_chat_api_response(from_number, response_data)
                    else:
                        logging.error(f"❌ Failed to process voice message: {voice_process_response.text[:500]}")
                        await self.message_handler.send_text(
                            from_number, 
                            "Sorry, I couldn't process your voice message."
                        )
                    
            except Exception as process_error:
                logging.error(f"❌ Error in voice processing: {str(process_error)}")
                await self.message_handler.send_text(
                    from_number,
                    "Sorry, I encountered an error processing your voice message."
                )
            finally:
                # Clean up the temporary file
                try:
                    if downloaded_file and os.path.exists(downloaded_file):
                        os.remove(downloaded_file)
                        logging.info(f"Temporary file removed: {downloaded_file}")
                except Exception as e:
                    logging.error(f"Failed to remove temporary file: {e}")
                    
        except Exception as e:
            logging.error(f"❌ Error processing voice message: {e}")
            try:
                await self.message_handler.send_text(
                    from_number, 
                    "Sorry, there was an error processing your voice message."
                )
            except Exception as send_error:
                logging.error(f"❌ Failed to send error message: {send_error}")
import logging
import ast
import json
import asyncio
import os
import time
from typing import Dict, List
import httpx

from src.webhook_handler.base_webhook_handler import BaseWebhookHandler
from src.utils.config import LENAAI_CHAT_ENDPOINT, LENAAI_LANGGRAPH_ENDPOINT, LENAAI_VOICE_PROCESS_ENDPOINT

class TelegramWebhookHandler(BaseWebhookHandler):
    """
    A class to handle Telegram webhook operations.
    """
    
    def __init__(self, credentials: dict):
        """
        Initialize the Telegram webhook handler.
        """
        super().__init__(credentials, "telegram")
    
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

    async def process_chat_api_response(self, chat_id: str, response_data: Dict):
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
            await self.message_handler.send_text(chat_id, message)
            
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
                    await self.message_handler.send_text(chat_id, description)
                    # if description:
                    #     await self.message_handler.send_text(chat_id, description)
                    
                    # Send images for this property
                    await asyncio.sleep(2)
                    for image_url in images_data:
                        try:
                            # Use the send_images method with a single image
                            await self.message_handler.send_images(chat_id, [image_url])
                            # Small delay to prevent rate limiting
                            await asyncio.sleep(0.5)
                        except Exception as img_error:
                            logging.error(f"❌ Error sending image {image_url}: {str(img_error)}")
        except Exception as e:
            logging.error(f"❌ Error processing chat API response: {str(e)}", exc_info=True)
            await self.message_handler.send_text(
                chat_id, 
                "Sorry, I encountered an error processing the response."
            )
    
    async def process_text_message(self, chat_id: str, user_message: str):
        """
        Process Telegram text messages and send response with property images if available.
        """
        logging.info(f"Received Telegram message from {chat_id}: {user_message}")

        try:
            async with httpx.AsyncClient(timeout=50.0) as client:
                # Request with client_id and platform
                chat_response = await client.post(
                    LENAAI_LANGGRAPH_ENDPOINT, 
                    json={
                        "query": user_message, 
                        "phone_number": chat_id, # todo change user_id
                        "client_id": self.credentials['client_id'],
                        "platform": "telegram"
                    }
                )
                if chat_response.status_code == 200:
                    response_data = chat_response.json()
                    logging.info(f"✅ Chat response {response_data}")
                    
                    await self.process_chat_api_response(chat_id, response_data)
                else:
                    logging.error(f"❌ Failed to get chat response: {chat_response.text}")
                    await self.message_handler.send_text(
                        chat_id, 
                        "I'm having trouble processing your message right now."
                    )
        except Exception as e:
            logging.error(f"❌ Error in chat processing: {str(e)}")
            await self.message_handler.send_text(
                chat_id, 
                "Sorry, can you please try again later?"
            )

    async def process_voice_message(self, chat_id: str, file_id: str):
        """
        Process Telegram voice messages.
        Download the voice message, transcribe it, and send a response.
        """
        try:
            # Send acknowledgment to user
            await self.message_handler.send_text(
                chat_id,
                "جارى معالجة رسالتك الصوتيه 🧏 وسوف ارد عليك حالا ⌛️⏳"
            )
            
            # Get the file path from Telegram
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.telegram.org/bot{self.credentials['bot_token']}/getFile",
                    params={"file_id": file_id}
                )
                
                if response.status_code != 200:
                    logging.error(f"❌ Failed to get file path: {response.text}")
                    await self.message_handler.send_text(
                        chat_id, 
                        "Sorry, I couldn't process your voice message."
                    )
                    return
                
                file_path = response.json().get("result", {}).get("file_path")
                
                if not file_path:
                    logging.error("❌ File path not found in response")
                    await self.message_handler.send_text(
                        chat_id, 
                        "Sorry, I couldn't process your voice message."
                    )
                    return
                
                # Get the file URL
                file_url = f"https://api.telegram.org/file/bot{self.credentials['bot_token']}/{file_path}"
                
                logging.info(f"Processing voice message from {chat_id}, URL: {file_url}")
                
                # Make POST request to voice process endpoint
                async with httpx.AsyncClient(timeout=60.0) as voice_client:
                    logging.info(f"Sending to voice process endpoint: {file_url}")
                    
                    # Prepare request data
                    voice_request = {
                        "media_url": file_url,
                        "phone_number": chat_id,
                        "client_id": self.credentials['client_id'],
                        "platform": "telegram",
                        "bot_token": self.credentials['bot_token']
                    }
                    
                    try:
                        # Make the actual API call
                        voice_process_response = await voice_client.post(
                            LENAAI_VOICE_PROCESS_ENDPOINT,  # Change to your actual endpoint
                            json=voice_request,
                            timeout=60.0
                        )
                        
                        # Handle the response
                        if voice_process_response.status_code == 200:
                            response_data = voice_process_response.json()
                            logging.info(f"✅ Voice message processed for {chat_id}")
                            
                            # Extract the message and properties
                            message = response_data.get("message", "")
                            properties = response_data.get("properties", None)
                            
                            # Create a response object with the necessary fields
                            chat_response = {
                                "message": message,
                                "properties": properties
                            }
                            
                            # Process the response
                            await self.process_chat_api_response(chat_id, chat_response)
                        else:
                            logging.error(f"❌ Voice process failed: {voice_process_response.status_code} {voice_process_response.text[:100]}")
                            await self.message_handler.send_text(
                                chat_id, 
                                "Sorry, I couldn't process your voice message."
                            )
                    except Exception as req_error:
                        logging.error(f"❌ Error calling voice process endpoint: {str(req_error)}", exc_info=True)
                        await self.message_handler.send_text(
                            chat_id, 
                            "Sorry, I encountered an error processing your voice message."
                        )
        except Exception as e:
            logging.error(f"❌ Error processing voice message: {e}", exc_info=True)
            await self.message_handler.send_text(
                chat_id, 
                "Sorry, there was an error processing your voice message."
            )
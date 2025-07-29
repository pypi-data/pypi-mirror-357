import ast
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
import aiofiles
import httpx

from message_handler.whatsapp_message_handler import WhatsAppMessageHandler
from utils.config import FACEBOOK_GRAPH_API_VERSION, LENAAI_CHAT_ENDPOINT, LENAAI_WHATSAPP_ENDPOINT


class WebhookHandler:
    """
    A class to handle all webhook operations for WhatsApp messages.
    """
    
    def __init__(self, credentials: Dict[str, str]):
        """
        Initialize the webhook handler.
        
        Args:
            credentials: Dictionary containing 'phone_number_id', 'access_token', and 'client_id'
        """
        self.credentials = credentials
        self.message_handler = WhatsAppMessageHandler(credentials)
    
    async def get_media_url(self, media_id: str) -> Optional[str]:
        """
        Retrieve the URL for a media item using its ID.
        
        Args:
            media_id: The WhatsApp media ID
            
        Returns:
            The media URL or None if retrieval failed
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
        
        Args:
            media_url: The URL to download from
            save_path: Base path to save the file (without extension)
            
        Returns:
            The full save path with extension or None if download failed
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

    async def get_and_download_media(self, media_id: str) -> Optional[str]:
        """
        Get media URL and download it.
        
        Args:
            media_id: The WhatsApp media ID
            
        Returns:
            The path to the downloaded file or None if operation failed
        """
        media_url = await self.get_media_url(media_id)
        if media_url:
            return await self.download_media(media_url, "voice")
        else:
            logging.error("Media URL could not be retrieved.")
            return None

    def extract_image_urls(self, images_data: Any) -> List[str]:
        """
        Extract image URLs from various formats (list, dict, or string).
        
        Args:
            images_data: Data containing image information
            
        Returns:
            List of valid image URLs
        """
        if not images_data:
            return []
        
        try:
            images_list = []
            
            # Handle case when images_data is already a list
            if isinstance(images_data, list):
                images_list = images_data
            # Handle case when images_data is a string that needs parsing
            elif isinstance(images_data, str):
                images_data = images_data.strip()
                if images_data.startswith("{") and images_data.endswith("}"):
                    images_data = "[" + images_data + "]"  # Convert single dict to list
                
                # Try parsing as JSON
                try:
                    images_list = json.loads(images_data)
                except json.JSONDecodeError:
                    try:
                        images_list = ast.literal_eval(images_data)
                    except:
                        logging.error(f"❌ Unable to parse image data string: {images_data}")
                        return []
            # Handle case when images_data is a single dict
            elif isinstance(images_data, dict):
                images_list = [images_data]
            else:
                logging.error(f"❌ Unsupported image data type: {type(images_data)}")
                return []
            
            # Ensure we have a list
            if not isinstance(images_list, list):
                images_list = [images_list]

            # Extract URLs
            valid_urls = []
            for image in images_list:
                if isinstance(image, dict) and 'url' in image:
                    valid_urls.append(image['url'])
                    
            return valid_urls
            
        except Exception as e:
            logging.error(f"❌ Error extracting image URLs: {str(e)}")
            return []
    
    def format_property_details(self, metadata: Dict, property_id: str) -> str:
        """
        Format property details into a readable description.
        
        Args:
            metadata: Dictionary containing property metadata
            property_id: ID of the property
            
        Returns:
            Formatted property description string
        """
        # Basic property info
        compound = metadata.get('compound', 'Unknown location')
        building_type = metadata.get('buildingType', 'Property')
        rooms = metadata.get('roomsCount', 0)
        bathrooms = metadata.get('bathroomCount', 0)
        
        # Price information
        total_price = metadata.get('totalPrice', 0)
        down_payment = metadata.get('downPayment', 0)
        
        # Format price with commas for thousands
        def format_price(price):
            if not price:
                return "N/A"
            try:
                return f"{int(price):,}"
            except (ValueError, TypeError):
                return str(price)
        
        # Build the description
        details = []
        details.append(f"*Property {property_id}*")
        details.append(f"*Location:* {compound}")
        
        if building_type:
            details.append(f"*Type:* {building_type}")
        
        # Add rooms and bathrooms
        features = []
        if rooms:
            room_text = f"{rooms} room{'s' if rooms != 1 else ''}"
            features.append(room_text)
        if bathrooms:
            bath_text = f"{bathrooms} bathroom{'s' if bathrooms != 1 else ''}"
            features.append(bath_text)
        
        if features:
            details.append(f"*Features:* {', '.join(features)}")
        
        # Add prices
        if total_price:
            details.append(f"*Price:* {format_price(total_price)} EGP")
        if down_payment:
            details.append(f"*Down Payment:* {format_price(down_payment)} EGP")
        
        # Additional details that might be useful
        if metadata.get('developer'):
            details.append(f"*Developer:* {metadata.get('developer')}")
        if metadata.get('deliveryDate'):
            details.append(f"*Delivery:* {metadata.get('deliveryDate')}")
        if metadata.get('finishing'):
            details.append(f"*Finishing:* {metadata.get('finishing')}")
        
        return "\n".join(details)

    async def process_text_message(self, from_number: str, user_message: str):
        """
        Process text messages and send response with property images if available.
        
        Args:
            from_number: The sender's WhatsApp number
            user_message: The message text sent by the user
        """
        logging.info(f"Received WhatsApp message from {from_number}: {user_message}")

        try:
            async with httpx.AsyncClient(timeout=50.0) as client:
                # Updated request with client_id
                chat_response = await client.post(
                    LENAAI_CHAT_ENDPOINT, 
                    json={
                        "query": user_message, 
                        "phone_number": from_number,
                        "client_id": self.credentials['client_id'],
                    }
                )
                
                if chat_response.status_code == 200:
                    try:
                        response_data = chat_response.json()
                        logging.info(f"✅ Chat response received")
                        
                        message = response_data.get("message", "Sorry, I couldn't process your message.")

                        # Check if auto-reply is off
                        if message == "Auto-reply is off":
                            logging.info("Auto-reply is off. No response will be sent.")
                            return
                        
                        # Extract properties and their images
                        properties = response_data.get("properties", [])
                        if properties is None:
                            properties = []
                        
                        albums = {}
                        
                        # Process properties and create image albums
                        for prop in properties:
                            if not isinstance(prop, dict):
                                logging.error(f"❌ Property is not a dictionary: {prop}")
                                continue
                                
                            property_id = prop.get("property_id", "unknown")
                            metadata = prop.get("metadata", {})
                            if not isinstance(metadata, dict):
                                logging.error(f"❌ Metadata is not a dictionary: {metadata}")
                                continue
                            
                            # Create a detailed property description
                            detailed_desc = self.format_property_details(metadata, property_id)
                            
                            # Extract image URLs using a safer approach
                            images_data = metadata.get("images", [])
                            images_urls = self.extract_image_urls(images_data)
                            
                            if images_urls:
                                albums[detailed_desc] = images_urls
                        
                        # Send message with images
                        await self.message_handler.send_message(from_number, message, albums)
                        
                    except (json.JSONDecodeError, TypeError) as json_err:
                        logging.error(f"❌ JSON parsing error: {str(json_err)}")
                        response_text = await chat_response.text()
                        logging.error(f"Response content: {response_text[:500]}...")  # Log first 500 chars
                        await self.message_handler.send_text(
                            from_number, 
                            "I'm having trouble processing your message right now."
                        )
                else:
                    logging.error(f"❌ Failed to get chat response: Status {chat_response.status_code}")
                    response_text = await chat_response.text()
                    logging.error(f"Error response: {response_text[:500]}...")  # Log first 500 chars
                    await self.message_handler.send_text(
                        from_number, 
                        "I'm having trouble processing your message right now."
                    )
        except Exception as e:
            logging.error(f"❌ Error in chat processing: {str(e)}", exc_info=True)
            await self.message_handler.send_text(
                from_number, 
                "Sorry, can you please try again later?"
            )

    async def process_voice_message(self, from_number: str, media_id: str):
        """
        Process voice messages and send response with property images if available.
        
        Args:
            from_number: The sender's WhatsApp number
            media_id: The WhatsApp media ID for the voice message
        """
        try:
            audio_url = await self.get_media_url(media_id)
            if not audio_url:
                logging.error(f"❌ Could not retrieve audio URL for media_id: {media_id}")
                await self.message_handler.send_text(
                    from_number, 
                    "Sorry, I couldn't process your voice message."
                )
                return
                
            logging.info(f"Processing voice message from {from_number}, URL: {audio_url}")
            
            async with httpx.AsyncClient(timeout=50.0) as client:
                chat_voice_response = await client.post(
                    LENAAI_WHATSAPP_ENDPOINT,
                    json={
                        "media_url": audio_url, 
                        "phone_number": from_number,
                        "client_id": self.credentials['client_id'],
                        "whatsapp_access_token": self.credentials['access_token']
                    }
                )
                
                if chat_voice_response.status_code == 200:
                    try:
                        response_data = chat_voice_response.json()
                        logging.info(f"✅ Voice message processed for {from_number}")
                        
                        # Extract message text
                        message = response_data.get("message", "I've processed your voice message.")

                        # Check if auto-reply is off
                        if message == "Auto-reply is off":
                            logging.info("Auto-reply is off. No response will be sent.")
                            return
                        
                        # Extract properties and their images
                        properties = response_data.get("properties", [])
                        if properties is None:
                            properties = []
                            
                        albums = {}
                        
                        # Process properties and create image albums
                        for prop in properties:
                            if not isinstance(prop, dict):
                                logging.error(f"❌ Property is not a dictionary: {prop}")
                                continue
                                
                            property_id = prop.get("property_id", "unknown")
                            metadata = prop.get("metadata", {})
                            if not isinstance(metadata, dict):
                                logging.error(f"❌ Metadata is not a dictionary: {metadata}")
                                continue
                            
                            # Create a detailed property description
                            detailed_desc = self.format_property_details(metadata, property_id)
                            
                            # Extract image URLs using a safer approach
                            images_data = metadata.get("images", [])
                            images_urls = self.extract_image_urls(images_data)
                            
                            if images_urls:
                                albums[detailed_desc] = images_urls
                        
                        # Send message with images
                        await self.message_handler.send_message(from_number, message, albums)
                        
                    except (json.JSONDecodeError, TypeError) as json_err:
                        logging.error(f"❌ JSON parsing error: {str(json_err)}")
                        response_text = await chat_voice_response.text()
                        logging.error(f"Response content: {response_text[:500]}...")  # Log first 500 chars
                        await self.message_handler.send_text(
                            from_number, 
                            "I'm having trouble processing your voice message right now."
                        )
                else:
                    logging.error(f"❌ Failed to process voice message: Status {chat_voice_response.status_code}")
                    response_text = await chat_voice_response.text()
                    logging.error(f"Error response: {response_text[:500]}...")
                    await self.message_handler.send_text(
                        from_number, 
                        "Sorry, I couldn't process your voice message."
                    )
        except Exception as e:
            logging.error(f"❌ Error processing voice message: {str(e)}", exc_info=True)
            try:
                await self.message_handler.send_text(
                    from_number, 
                    "Sorry, there was an error processing your voice message."
                )
            except Exception as send_error:
                logging.error(f"❌ Failed to send error message: {send_error}")
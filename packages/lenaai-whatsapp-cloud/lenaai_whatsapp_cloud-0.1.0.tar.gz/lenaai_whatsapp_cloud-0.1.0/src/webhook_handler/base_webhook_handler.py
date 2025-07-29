import ast
import json
import logging
from typing import Dict, List, Any

from src.webhook_handler.webhook_handler_factory import create_message_handler

class BaseWebhookHandler:
    """
    Base class for platform-specific webhook handlers
    """
    
    def __init__(self, credentials: Dict[str, str], platform: str):
        """
        Initialize the webhook handler.
        
        Args:
            credentials: Dictionary containing platform-specific credentials
            platform: The platform identifier ("whatsapp", "messenger", "telegram")
        """
        self.credentials = credentials
        self.platform = platform
        self.message_handler = create_message_handler(platform, credentials)
    
    async def extract_image_urls(self, images_str) -> List[str]:
        """
        Extract image URLs from the complex image string format.
        
        Args:
            images_str: String containing image data
            
        Returns:
            List of valid image URLs
        """
        if not images_str:
            return []
        
        try:
            # Ensure images_str is correctly formatted before parsing
            if isinstance(images_str, str):
                images_str = images_str.strip()
                if images_str.startswith("{") and images_str.endswith("}"):
                    images_str = "[" + images_str + "]"  # Convert single dict to list
            
            # Try parsing as JSON
            try:
                images_list = json.loads(images_str)
            except json.JSONDecodeError:
                images_list = ast.literal_eval(images_str)
            
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
            logging.error(f"❌ Error parsing images string: {str(e)}")
            return []

    async def process_chat_api_response(self, user_id: str, response_data: Dict[str, Any]):
        """
        Process the response from the Lena AI chat API and send appropriate messages.
        
        Args:
            user_id: The recipient ID (depends on platform)
            response_data: Response data from the Lena AI chat API
        """
        # Extract message text
        message = response_data.get("message", "I couldn't process your message.")

        # Check if auto-reply is off
        if message == "Auto-reply is off":
            logging.info("Auto-reply is off. No response will be sent.")
            return
        
        # Extract properties and their images
        properties = response_data.get("properties", []) or []
        
        albums = {}
        
        # Process properties and create image albums
        for prop in properties:
            property_id = prop.get("property_id", "unknown")
            metadata = prop.get("metadata", {})
            
            # Create a short description for the property
            short_desc = f"Property {property_id} - {metadata.get('compound', '')}"
            
            # Extract image URLs using a safer approach
            images_data = await self.extract_image_urls(metadata.get("images", ""))
            
            if images_data:
                albums[short_desc] = images_data  
        
        # Send message with images
        await self.message_handler.send_message(user_id, message, albums)
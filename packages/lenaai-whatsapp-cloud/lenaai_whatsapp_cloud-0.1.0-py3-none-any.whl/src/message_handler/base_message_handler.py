from abc import ABC, abstractmethod
from datetime import datetime
import logging
from typing import Dict, List, Optional, Any

class BaseMessageHandler(ABC):
    """
    Abstract base class for all message handlers (WhatsApp, Messenger, Telegram).
    """
    
    def __init__(self, credentials: Dict[str, str]):
        """
        Initialize the message handler.
        
        Args:
            credentials: Dictionary containing platform-specific credentials
        """
        self.credentials = credentials
        self.platform = None  # Will be set by child classes
        
    @abstractmethod
    async def send_text(self, to_id: str, message: str) -> Any:
        """
        Sends a text message through the platform.
        
        Args:
            to_id: The recipient identifier (could be phone number, chat id, etc.)
            message: The text message to send
            
        Returns:
            Platform-specific status indicator
        """
        pass
    
    @abstractmethod
    async def send_image(self, to_id: str, image_url: str) -> Dict[str, Any]:
        """
        Sends a single image through the platform.
        
        Args:
            to_id: The recipient identifier
            image_url: URL of the image to send
            
        Returns:
            Dictionary with status information for the image
        """
        pass
    
    @abstractmethod
    async def send_images(self, to_id: str, image_urls: List[str]) -> List[Dict[str, Any]]:
        """
        Sends images through the platform.
        
        Args:
            to_id: The recipient identifier
            image_urls: List of image URLs to send
            
        Returns:
            List of result dictionaries with status for each image
        """
        pass
    
    @abstractmethod
    async def send_video(self, to_id: str, video_url: str) -> Any:
        """
        Sends a video through the platform.
        
        Args:
            to_id: The recipient identifier
            video_url: The URL of the video to send
            
        Returns:
            Platform-specific status indicator
        """
        pass
    
    @abstractmethod
    async def send_message(self, to_id: str, message: str = None, albums: Dict = None, video_url: str = None) -> Dict[str, Any]:
        """
        Main function to send messages with optional media.
        
        Args:
            to_id: The recipient identifier
            message: Optional text message
            albums: Optional dictionary of image albums to send
            video_url: Optional video URL to send
            
        Returns:
            Dictionary with status information
        """
        pass
import logging
from typing import Dict, Optional, Any

from src.message_handler.whatsapp_message_handler import WhatsAppMessageHandler
from src.message_handler.messenger_message_handler import MessengerMessageHandler
from src.message_handler.telegram_message_handler import TelegramMessageHandler
from src.message_handler.twilio_message_handler import TwilioMessageHandler


def create_message_handler(platform: str, credentials: Dict[str, Any]):
    """
    Factory function to create the appropriate message handler based on platform.
    
    Args:
        platform: The messaging platform ("whatsapp", "messenger", "telegram", "twilio_whatsapp")
        credentials: Dictionary containing platform-specific credentials
        
    Returns:
        An instance of a platform-specific message handler
    """
    platform = platform.lower()
    
    if platform == "whatsapp":
        return WhatsAppMessageHandler(credentials)
    elif platform == "messenger":
        return MessengerMessageHandler(credentials)
    elif platform == "telegram":
        return TelegramMessageHandler(credentials)
    elif platform == "twilio_whatsapp":
        return TwilioMessageHandler(credentials)
    else:
        logging.error(f"❌ Unsupported platform: {platform}")
        raise ValueError(f"Unsupported platform: {platform}")
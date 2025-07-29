from typing import List, Optional, Literal
from pydantic import BaseModel, Field

# ============ WhatsApp Models ============
class VideoMessage(BaseModel):
    to_number: str
    video_url: str
    client_id: str  

class ImageMessage(BaseModel):
    to_number: str
    image_urls: List[str]
    client_id: str  

class TextMessage(BaseModel):
    to_number: str
    message: str
    client_id: str  

class VideoSendRequest(BaseModel):
    spreadsheet_url: str
    video_url: str
    sheet_name: Optional[str] = "Sheet1"
    client_id: str

# ============ Telegram Models ============
class TelegramTextMessage(BaseModel):
    to_number: str
    message: str
    client_id: str  

class TelegramImageMessage(BaseModel):
    to_number: str
    image_urls: List[str]
    client_id: str  

class TelegramVideoMessage(BaseModel):
    to_number: str
    video_url: str
    client_id: str  

class TelegramSendRequest(BaseModel):
    spreadsheet_url: str
    message: str
    video_url: Optional[str] = None
    sheet_name: Optional[str] = "Sheet1"
    client_id: str


class TwilioMediaSendRequest(BaseModel):
    spreadsheet_url: str
    media_url: str
    sheet_name: Optional[str] = "Sheet1"
    client_id: str
    
# ============ Legacy Multi-Platform Models ============
# Kept for backward compatibility if needed
class MultiPlatformTextMessage(BaseModel):
    to_number: str
    message: str
    client_id: str
    platform: Literal["whatsapp", "messenger", "telegram", "twilio_whatsapp"]

class MultiPlatformImageMessage(BaseModel):
    to_number: str
    image_urls: List[str]
    client_id: str
    platform: Literal["whatsapp", "messenger", "telegram", "twilio_whatsapp"]

class MultiPlatformVideoMessage(BaseModel):
    to_number: str
    video_url: str
    client_id: str
    platform: Literal["whatsapp", "messenger", "telegram", "twilio_whatsapp"]

class MultiPlatformVideoSendRequest(BaseModel):
    spreadsheet_url: str
    video_url: Optional[str] = None
    message: Optional[str] = None
    sheet_name: Optional[str] = "Sheet1"
    client_id: str
    platform: Literal["whatsapp", "messenger", "telegram", "twilio_whatsapp"] = "whatsapp"
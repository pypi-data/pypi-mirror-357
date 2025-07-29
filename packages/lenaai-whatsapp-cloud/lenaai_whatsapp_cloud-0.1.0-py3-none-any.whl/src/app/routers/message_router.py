import aiohttp
import re
import logging
import os
import uuid
import aiofiles
from pathlib import Path
from fastapi import APIRouter, HTTPException

from src.utils.config import (
    get_credentials, 
    get_messenger_credentials,
    get_telegram_credentials,
    get_twilio_credentials
)
from src.utils.convert_to_downloadable_link import extract_drive_direct_link
from src.utils.model import (
    MultiPlatformTextMessage, 
    MultiPlatformImageMessage, 
    MultiPlatformVideoMessage
)
from src.utils.status_enums import MessageSendStatus, ImageSendStatus, VideoSendStatus
from src.message_handler.whatsapp_message_handler import WhatsAppMessageHandler
from src.message_handler.messenger_message_handler import MessengerMessageHandler
from src.message_handler.telegram_message_handler import TelegramMessageHandler
from src.message_handler.twilio_message_handler import TwilioMessageHandler

# Initialize router (prefix will be added in main.py)
message_router = APIRouter()

# Create a directory for temporary image storage
TEMP_IMAGE_DIR = Path("./temp_images")
TEMP_IMAGE_DIR.mkdir(exist_ok=True)

# Dependencies to get various message handlers
async def get_whatsapp_handler(client_id: str):
    """
    Dependency that creates and returns a WhatsAppMessageHandler instance.
    """
    credentials = await get_credentials(client_id)
    return WhatsAppMessageHandler(credentials)

async def get_messenger_handler(client_id: str):
    """
    Dependency that creates and returns a MessengerMessageHandler instance.
    """
    credentials = await get_messenger_credentials(client_id)
    return MessengerMessageHandler(credentials)

async def get_telegram_handler(client_id: str):
    """
    Dependency that creates and returns a TelegramMessageHandler instance.
    """
    credentials = await get_telegram_credentials(client_id)
    return TelegramMessageHandler(credentials)

async def get_twilio_handler(client_id: str):
    """
    Dependency that creates and returns a TwilioMessageHandler instance.
    """
    credentials = await get_twilio_credentials(client_id)
    return TwilioMessageHandler(credentials)

async def get_platform_handler(platform: str, client_id: str):
    """
    Get the appropriate message handler based on platform.
    """
    platform = platform.lower()
    
    if platform == "whatsapp":
        return await get_whatsapp_handler(client_id)
    elif platform == "messenger":
        return await get_messenger_handler(client_id)
    elif platform == "telegram":
        return await get_telegram_handler(client_id)
    elif platform == "twilio_whatsapp":
        return await get_twilio_handler(client_id)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")

# Helper function to extract file ID from Google Drive URL
def extract_file_id_from_gdrive_url(url: str) -> str:
    """
    Extract the file ID from a Google Drive URL.
    
    Args:
        url: The Google Drive URL
        
    Returns:
        The file ID or None if it couldn't be extracted
    """
    if "/file/d/" in url:
        return url.split("/file/d/")[1].split("/")[0]
    elif "/d/" in url:
        return url.split("/d/")[1].split("/")[0]
    elif "id=" in url:
        match = re.search(r"id=([a-zA-Z0-9_-]+)", url)
        if match:
            return match.group(1)
    
    return None

# Helper function to download an image from a URL
async def download_image(url: str) -> Path:
    """
    Downloads an image from a URL and saves it to a temporary file.
    
    Args:
        url: The URL of the image
        
    Returns:
        Path to the downloaded image
    """
    try:
        # Create a unique filename
        temp_file = TEMP_IMAGE_DIR / f"{uuid.uuid4()}.jpg"
        
        # Download the image
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    logging.error(f"Failed to download image: {response.status}")
                    return None
                
                # Save the image to the temporary file
                async with aiofiles.open(temp_file, 'wb') as f:
                    await f.write(await response.read())
        
        return temp_file
        
    except Exception as e:
        logging.error(f"Error downloading image: {str(e)}")
        return None

# Helper function to download from Google Drive
async def download_gdrive_image(file_id: str) -> Path:
    """
    Downloads an image from Google Drive and saves it to a temporary file.
    
    Args:
        file_id: The Google Drive file ID
        
    Returns:
        Path to the downloaded image
    """
    # Create a direct download link
    direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    
    # Download the image using the common download function
    return await download_image(direct_url)


@message_router.post("/message/template-text", 
    summary="Send Template Text Message",
    description="Send a template text message via any supported platform (WhatsApp, Messenger, Telegram, Twilio)",
    response_description="Message sending status and details")
async def send_template_text_message_multi_platform(message_data: MultiPlatformTextMessage):
    """
    Send a text message via the specified platform.
    
    Supports all major messaging platforms:
    - WhatsApp Business API
    - Facebook Messenger
    - Telegram
    - Twilio WhatsApp
    
    The message will be sent to the specified recipient and logged in the system.
    """
    try:
        # Get the appropriate handler
        message_handler = await get_platform_handler(message_data.platform, message_data.client_id)
        
        logging.info(f"Sending template text message to {message_data}")

        # The ID field can be phone number, user ID, or chat ID depending on platform
        status = await message_handler.send_real_estate_intro_template(
            message_data.to_number
        )
        
        if status == MessageSendStatus.SUCCESS:
            async with aiohttp.ClientSession() as session:
                await message_handler.update_firestore_history(
                    session, message_data.to_number, message_data.message
                )
            return {
                "status": "success",
                "message": "Message sent successfully",
                "platform": message_data.platform,
                "recipient": message_data.to_number
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to send message"
            )
            
    except Exception as e:
        logging.error(f"❌ Error in multi-platform text message endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# General multi-platform text message endpoint
@message_router.post("/message/free-text", 
    summary="Send Text Message",
    description="Send a text message via any supported platform (WhatsApp, Messenger, Telegram, Twilio)",
    response_description="Message sending status and details")
async def send_text_message_multi_platform(message_data: MultiPlatformTextMessage):
    """
    Send a text message via the specified platform.
    
    Supports all major messaging platforms:
    - WhatsApp Business API
    - Facebook Messenger
    - Telegram
    - Twilio WhatsApp
    
    The message will be sent to the specified recipient and logged in the system.
    """
    try:
        # Get the appropriate handler
        message_handler = await get_platform_handler(message_data.platform, message_data.client_id)
        
        logging.info(f"Sending text message to {message_data}")

        # The ID field can be phone number, user ID, or chat ID depending on platform
        status = await message_handler.send_free_text(
            message_data.to_number,
            message_data.message
        )
        
        if status == MessageSendStatus.SUCCESS:
            async with aiohttp.ClientSession() as session:
                await message_handler.update_firestore_history(
                    session, message_data.to_number, message_data.message
                )
            return {
                "status": "success",
                "message": "Message sent successfully",
                "platform": message_data.platform,
                "recipient": message_data.to_number
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to send message"
            )
            
    except Exception as e:
        logging.error(f"❌ Error in multi-platform text message endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# General multi-platform image message endpoint
@message_router.post("/message/images",
    summary="Send Images",
    description="Send one or more images via any supported platform",
    response_description="Image sending status and results")
async def send_images_multi_platform(image_data: MultiPlatformImageMessage):
    """
    Send images via the specified platform.
    
    Supports sending multiple images in a single request.
    Images can be provided as URLs or Google Drive links.
    """
    try:
        # Log the incoming request data
        logging.info(f"Received image request: Platform={image_data.platform}, Client ID={image_data.client_id}, To={image_data.to_number}")
        logging.info(f"Original Image URLs: {image_data.image_urls}")
        
        # Get the appropriate handler
        logging.info(f"Getting message handler for platform: {image_data.platform}")
        message_handler = await get_platform_handler(image_data.platform, image_data.client_id)
        logging.info(f"Handler type: {type(message_handler).__name__}")
        
        results = []
        
        # For Messenger, handle Google Drive URLs with special download-then-upload approach
        if image_data.platform.lower() == "messenger":
            temp_files = []  # Keep track of temp files to clean up later
            
            # Process each image URL
            for url in image_data.image_urls:
                try:
                    if "drive.google.com" in url:
                        # For Google Drive URLs, download and upload
                        logging.info(f"Processing Google Drive URL: {url}")
                        
                        # 1. Extract file ID
                        file_id = extract_file_id_from_gdrive_url(url)
                        if not file_id:
                            logging.error(f"Could not extract file ID from Google Drive URL: {url}")
                            results.append({
                                "url": url,
                                "status": "failed",
                                "message": "Failed to extract file ID from Google Drive URL"
                            })
                            continue
                        
                        # 2. Download the image
                        logging.info(f"Downloading image from Google Drive, file ID: {file_id}")
                        temp_file = await download_gdrive_image(file_id)
                        if not temp_file:
                            logging.error(f"Failed to download image from Google Drive: {url}")
                            results.append({
                                "url": url,
                                "status": "failed",
                                "message": "Failed to download image from Google Drive"
                            })
                            continue
                        
                        temp_files.append(temp_file)
                        
                        # 3. Upload to Facebook Messenger
                        logging.info(f"Uploading image to Facebook Messenger: {temp_file}")
                        result = await message_handler.upload_and_send_image(
                            image_data.to_number, 
                            temp_file
                        )
                        results.append(result)
                    else:
                        # For non-Google Drive URLs, use the normal approach
                        result = await message_handler.send_image(image_data.to_number, url)
                        results.append(result)
                except Exception as e:
                    logging.error(f"Error processing image {url}: {str(e)}")
                    results.append({
                        "url": url,
                        "status": "failed",
                        "message": str(e)
                    })
            
            # Clean up temp files
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                        logging.info(f"Removed temporary file: {temp_file}")
                except Exception as e:
                    logging.error(f"Error removing temporary file: {str(e)}")
        else:
            # For other platforms, use the existing approach
            converted_urls = []
            for url in image_data.image_urls:
                converted_url = await extract_drive_direct_link(url)
                converted_urls.append(converted_url)
            
            logging.info(f"Converted Image URLs: {converted_urls}")
            
            # Send the images with converted URLs
            logging.info(f"Sending {len(converted_urls)} images to {image_data.to_number}")
            results = await message_handler.send_images(
                image_data.to_number,
                image_urls=converted_urls
            )
        
        # Log the results
        logging.info(f"Image sending results: {results}")
        
        any_success = any(r.get("status") == "success" for r in results)
        all_success = all(r.get("status") == "success" for r in results)
        
        if all_success:
            return {
                "status": "success",
                "message": "All images sent successfully",
                "platform": image_data.platform,
                "details": results
            }
        elif any_success:
            return {
                "status": "partial_success",
                "message": "Some images sent successfully",
                "platform": image_data.platform,
                "details": results
            }
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Failed to send all images",
                    "platform": image_data.platform,
                    "details": results
                }
            )
            
    except Exception as e:
        logging.error(f"❌ Error in multi-platform image endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    
# General multi-platform video message endpoint
@message_router.post("/multi-platform/video")
async def send_video_multi_platform(video_data: MultiPlatformVideoMessage):
    """
    Send a video via the specified platform.
    """
    try:
        # Extract direct link for videos (if from Google Drive)
        video_url = await extract_drive_direct_link(video_data.video_url)
        
        # Get the appropriate handler
        message_handler = await get_platform_handler(video_data.platform, video_data.client_id)
        
        # Send the video
        status = await message_handler.send_video(
            video_data.to_number,
            video_url=video_url
        )
        
        if status == VideoSendStatus.SUCCESS:
            return {
                "status": "success",
                "message": "Video sent successfully",
                "platform": video_data.platform
            }
        elif status == VideoSendStatus.FAILED_TO_CONVERT:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to convert video to {video_data.platform} format"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to send video via {video_data.platform}"
            )
            
    except Exception as e:
        logging.error(f"❌ Error in multi-platform video endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
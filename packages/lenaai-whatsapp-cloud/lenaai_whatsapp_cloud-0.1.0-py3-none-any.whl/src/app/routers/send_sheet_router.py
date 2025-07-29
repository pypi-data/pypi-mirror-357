import logging
from fastapi import APIRouter, HTTPException, File, UploadFile, Form
import os
import httpx
from src.utils.config import (
    LENAAI_LEADING_MESSAGE_ENDPOINT, 
    get_credentials, 
    get_telegram_client_credentials,
    get_twilio_credentials
)
from src.utils.convert_to_downloadable_link import extract_drive_direct_link
from src.utils.model import TwilioMediaSendRequest, VideoSendRequest
from src.whatsapp_sheet.send_sheet_handlers import SheetMessageProcessor
from src.telegram_sheet.telegram_sheet_handlers import TelegramSheetProcessor
from src.twilio_sheet.twilio_sheet_message import TwilioSheetMessenger

# Initialize router (prefix will be added in main.py)
sheet_router = APIRouter()

# WhatsApp endpoint - using your existing implementation
@sheet_router.post("/bulk/whatsapp/video",
    summary="Send WhatsApp Video to Spreadsheet",
    description="Send a video to all valid WhatsApp phone numbers in a Google Spreadsheet",
    response_description="Bulk sending results and statistics")
async def send_whatsapp_video_to_spreadsheet(request: VideoSendRequest):
    """
    Endpoint to send a video to all valid WhatsApp phone numbers in a spreadsheet.
    Updates user interactions and returns detailed results of the operation.
    
    This endpoint reads phone numbers from a Google Spreadsheet and sends a video
    to each valid number via WhatsApp Business API. It tracks success/failure rates
    and updates user interaction status for successful sends.
    """
    try:
        credentials = await get_credentials(request.client_id)
        
        # Create the sheet message processor
        sheet_processor = SheetMessageProcessor(credentials)
        
        # Process the spreadsheet and send videos
        videoURL = await extract_drive_direct_link(request.video_url)
        results = await sheet_processor.process_and_send_video(
            spreadsheet_url=request.spreadsheet_url, 
            video_url=videoURL, 
            sheet_name=request.sheet_name
        )
        
        # Extract failed numbers for the response
        failed_numbers = []
        invalid_numbers = []
        
        for detail in results["details"]:
            if detail["status"] == "INVALID_NUMBER":
                invalid_numbers.append(detail["phone"])
            elif detail["status"] != "SUCCESS":
                failed_numbers.append(detail["phone"])
            
            # Update user interaction for each successful send
            if detail["status"] == "SUCCESS":
                try:
                    # Call the user-interact endpoint
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            LENAAI_LEADING_MESSAGE_ENDPOINT,
                            json={
                                "phone_number": detail["phone"], #todo
                                "client_id": request.client_id,
                                "toggle_ai_auto_reply": True,
                                "username": detail["username"],
                                "platform": "whatsapp"
                            }
                        )
                        
                        if response.status_code != 200 or not response.json().get("status"):
                            logging.warning(f"Failed to update user interaction for {detail['phone']}: {response.text}")
                            
                except Exception as e:
                    logging.error(f"Error updating user interaction for {detail['phone']}: {str(e)}")
                
        # Construct a detailed response
        return {
            "status": "completed",
            "message": "Processing completed.",
            "platform": "whatsapp",
            "spreadsheet_url": request.spreadsheet_url,
            "summary": {
                "total_processed": results["total"],
                "successful": results["successful"],
                "failed": results["failed"],
                "invalid_numbers": results["invalid_numbers"]
            },
            "failed_numbers": failed_numbers,
            "invalid_numbers": invalid_numbers,
            "details": results["details"]  # Include full details for reference
        }
        
    except Exception as e:
        logging.error(f"Error in send_whatsapp_video_to_spreadsheet endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Simplified Telegram endpoint
@sheet_router.post("/bulk/telegram/message",
    summary="Send Telegram Message to Spreadsheet",
    description="Send a message (and optionally a video) to Telegram users in a Google Spreadsheet",
    response_description="Bulk sending results and statistics")
async def send_telegram_message_to_spreadsheet(
    spreadsheet_url: str,
    message: str,
    video_url: str = None,
    sheet_name: str = "Sheet1",
    client_id: str = None
):
    """
    Endpoint to send a message (and optionally a video) to Telegram users in a spreadsheet.
    
    This endpoint reads Telegram user IDs from a Google Spreadsheet and sends a message
    (and optionally a video) to each user via Telegram. It supports both text messages
    and media attachments.
    """
    try:
        if not client_id:
            raise HTTPException(status_code=400, detail="client_id is required")

        # Get credentials from your existing system
        credentials = await get_telegram_client_credentials(client_id)
        
        # Initialize the processor
        try:
            sheet_processor = TelegramSheetProcessor(credentials)
        except Exception as e:
            logging.error(f"Error initializing TelegramSheetProcessor: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error initializing Telegram client: {str(e)}")

        # Process and send messages
        try:
            results = await sheet_processor.process_and_send_message(
                spreadsheet_url=spreadsheet_url, 
                message=message,
                video_url=video_url, 
                sheet_name=sheet_name
            )
        except Exception as e:
            logging.error(f"Error in process_and_send_message: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error sending messages: {str(e)}")

        return {
            "status": "completed",
            "message": "Processing completed.",
            "platform": "telegram",
            "spreadsheet_url": spreadsheet_url,
            "summary": {
                "total_processed": results["total"],
                "successful": results["successful"],
                "failed": results["failed"]
            },
            "details": results["details"]
        }

    except Exception as e:
        logging.error(f"Error in send_telegram_message_to_spreadsheet: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    

@sheet_router.post("/bulk/twilio/media",
    summary="Send Twilio Media to Spreadsheet",
    description="Send media to all valid phone numbers in a spreadsheet via Twilio WhatsApp",
    response_description="Bulk sending results and statistics")
async def send_twilio_media_to_spreadsheet(request: TwilioMediaSendRequest):
    """
    Endpoint to send media to all valid phone numbers in a spreadsheet via Twilio WhatsApp.
    Accepts a Google Sheet URL or Google Drive Excel URL.
    
    This endpoint reads phone numbers from a Google Spreadsheet and sends media
    (images, videos, documents) to each valid number via Twilio WhatsApp API.
    It tracks success/failure rates and updates user interaction status.
    """
    try:
        # Validate client_id
        if not request.client_id:
            raise HTTPException(status_code=400, detail="client_id is required")
            
        # Get credentials for the client
        credentials = await get_twilio_credentials(request.client_id)
        logging.info(f"Retrieved Twilio credentials for client_id: {request.client_id}")
        
        # Create the Twilio sheet processor
        sheet_processor = TwilioSheetMessenger(credentials)
        
        # Process the media URL if it's a Google Drive link
        try:
            media_url = await extract_drive_direct_link(request.media_url)
            logging.info(f"Converted media URL: {media_url}")
        except Exception as e:
            logging.warning(f"Could not convert media URL, using original: {e}")
            media_url = request.media_url
        
        # Process the spreadsheet and send media
        results = await sheet_processor.process_and_send_media(
            source=request.spreadsheet_url, 
            media_url=media_url, 
            sheet_name=request.sheet_name
        )
        
        # Extract failed numbers for the response
        failed_numbers = []
        invalid_numbers = []
        
        for detail in results["details"]:
            if detail["status"] == "INVALID_NUMBER":
                invalid_numbers.append(detail["phone"])
            elif detail["status"] != "SUCCESS":
                failed_numbers.append(detail["phone"])
            
            # Update user interaction for each successful send
            if detail["status"] == "SUCCESS":
                try:
                    # Call the user-interact endpoint
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            LENAAI_LEADING_MESSAGE_ENDPOINT,
                            json={
                                "phone_number": detail["phone"], #todo
                                "client_id": request.client_id,
                                "toggle_ai_auto_reply": True,
                                "username": detail["username"],
                                "platform": "twilio_whatsapp"
                            }
                        )
                        
                        if response.status_code != 200 or not response.json().get("status"):
                            logging.warning(f"Failed to update user interaction for {detail['phone']}: {response.text}")
                            
                except Exception as e:
                    logging.error(f"Error updating user interaction for {detail['phone']}: {str(e)}")
                
        return {
            "status": "completed",
            "message": "Processing completed.",
            "platform": "twilio_whatsapp",
            "spreadsheet_url": request.spreadsheet_url,
            "summary": {
                "total_processed": results["total"],
                "successful": results["successful"],
                "failed": results["failed"],
                "invalid_numbers": results["invalid_numbers"]
            },
            "failed_numbers": failed_numbers,
            "invalid_numbers": invalid_numbers,
            "details": results["details"]
        }
        
    except Exception as e:
        logging.error(f"Error in send_twilio_media_to_spreadsheet endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@sheet_router.post("/bulk/twilio/file",
    summary="Send Twilio Media Using Excel File",
    description="Upload an Excel file and send media to phone numbers in the file via Twilio",
    response_description="Bulk sending results and statistics")
async def send_twilio_media_using_excel_file(
    client_id: str = Form(...),
    media_url: str = Form(...),
    sheet_name: str = Form("Sheet1"),
    excel_file: UploadFile = File(...)
):
    """
    Endpoint to send media using an uploaded Excel file via Twilio WhatsApp.
    
    This endpoint accepts an Excel file upload containing phone numbers and sends
    media to each valid number via Twilio WhatsApp API. It's useful when you don't
    want to use Google Sheets.
    """
    try:
        # Validate client_id
        if not client_id:
            raise HTTPException(status_code=400, detail="client_id is required")
            
        # Get credentials for the client
        credentials = await get_twilio_credentials(client_id)
        logging.info(f"Retrieved Twilio credentials for client_id: {client_id}")
        
        # Create the Twilio sheet processor
        sheet_processor = TwilioSheetMessenger(credentials)
        
        # Process the media URL if it's a Google Drive link
        try:
            processed_media_url = await extract_drive_direct_link(media_url)
            logging.info(f"Converted media URL: {processed_media_url}")
        except Exception as e:
            logging.warning(f"Could not convert media URL, using original: {e}")
            processed_media_url = media_url
        
        # Process the Excel file and send media
        results = await sheet_processor.process_and_send_media_from_file(
            excel_file=excel_file,
            media_url=processed_media_url, 
            sheet_name=sheet_name
        )
        
        return {
            "status": "completed",
            "message": "Processing completed.",
            "platform": "twilio_whatsapp",
            "filename": excel_file.filename,
            "summary": {
                "total_processed": results["total"],
                "successful": results["successful"],
                "failed": results["failed"],
                "invalid_numbers": results["invalid_numbers"]
            },
            "details": results["details"]
        }
        
    except Exception as e:
        logging.error(f"Error in send_twilio_media_using_excel_file endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
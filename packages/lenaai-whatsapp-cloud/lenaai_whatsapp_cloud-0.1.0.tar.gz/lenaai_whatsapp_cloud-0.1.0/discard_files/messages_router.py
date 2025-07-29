from fastapi import FastAPI, Request
import logging
from utils.config import get_credentials, get_credentials_by_business_id
from utils.model import ImageMessage, TextMessage, VideoMessage
from discard_files.whatsapp_messages import whatsapp
from fastapi import APIRouter

msgs_router = APIRouter()

# Endpoint to receive messages
@msgs_router.post("/webhook")
async def receive_message(request: Request):
    try:
        data = await request.json()
        logging.info(f"Incoming WhatsApp data: {data}")

        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        messages = changes.get("value", {}).get("messages", [])

        if not messages:
            logging.warning("⚠️ No messages found in the webhook payload.")
            return {"status": "no_message"}
        # Extract the recipient phone number (our WABA number)
        recipient_number_id = changes.get("value", {}).get("metadata", {}).get("phone_number_id")        
        if not recipient_number_id:
            logging.error("❌ No recipient phone number found in webhook data.")
            return {"status": "error", "message": "Missing recipient number"}
        
        # Determine the client_id based on the recipient phone number
        credentials = await get_credentials_by_business_id(recipient_number_id)
        if not credentials:
            logging.error(f"❌ receive_message No matching client found for recipient {recipient_number_id}")
            return {"status": "error", "message": "Invalid recipient number"}

        message_data = messages[0]
        from_number = message_data.get("from")
        user_message = message_data.get("text", {}).get("body", "").strip()

        logging.info(f"📩 Received message from {from_number}: {user_message}")

        if from_number and user_message:
            reply, albums = whatsapp.forward_to_lena_ai(from_number, user_message, credentials)
            whatsapp.send_whatsapp_message(from_number, reply,credentials , albums)

        return {"status": "message_processed"}

    except Exception as e:
        logging.error(f"❌ Error processing message: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}
    



@msgs_router.post("/send-message")
async def send_text_message_endpoint(message_data: TextMessage):
    try:
        credentials = await get_credentials(message_data.client_id)
        success = whatsapp.send_whatsapp_message(
            to_number=message_data.to_number,
            message=message_data.message,
            credentials = credentials
        )
        
        if success:
            return {
                "status": "success",
                "message": "Message sent successfully"
            }
        else:
            return {
                "status": "error",
                "message": "Failed to send message"
            }
    except Exception as e:
        logging.error(f"❌ Error sending message: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e)
        }


@msgs_router.post("/send-images")
async def send_images_endpoint(image_data: ImageMessage):
    try:
        credentials = await get_credentials(image_data.client_id)
        success = whatsapp.send_whatsapp_message(
            to_number=image_data.to_number,
            message="",
            credentials = credentials,
            albums=image_data.image_urls
        )

        if success:
            return {
                "status": "success",
                "message": "Message and images sent successfully"
            }
        else:
            return {
                "status": "error",
                "message": "Failed to send message or images"
            }
    except Exception as e:
        logging.error(f"❌ Error sending images: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e)
        }


@msgs_router.post("/send-video")
async def send_video_endpoint(video_data: VideoMessage):
    try:
        credentials = await get_credentials(video_data.client_id)
        success = whatsapp.send_whatsapp_message(
            to_number=video_data.to_number,
            message="",
            credentials = credentials,
            video_url=video_data.video_url
        )
        
        if success:
            return {
                "status": "success",
                "message": "Message and video sent successfully"
            }
        else:
            return {
                "status": "error",
                "message": "Failed to send message or video"
            }
    except Exception as e:
        logging.error(f"❌ Error sending video message: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e)
        }
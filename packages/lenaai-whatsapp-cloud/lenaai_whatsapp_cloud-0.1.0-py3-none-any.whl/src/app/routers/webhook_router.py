import json
import os
from fastapi import APIRouter, Form, Request, BackgroundTasks, Depends, HTTPException, Response, Query
import logging
import httpx

from src.utils.config import (
    get_credentials_by_business_id, 
    get_telegram_credentials_by_token,
    get_credentials_by_page_id,
    get_twilio_credentials_by_account_sid,
)
from src.webhook_handler.whatsapp_webhook_handler import WhatsAppWebhookHandler
from src.webhook_handler.messenger_webhook_handler import MessengerWebhookHandler
from src.webhook_handler.telegram_webhook_handler import TelegramWebhookHandler
from src.webhook_handler.twilio_webhook_handler import TwilioWebhookHandler


# Initialize router (prefix will be added in main.py)
webhook_router = APIRouter()

# Dependency to get WhatsApp WebhookHandler
async def get_whatsapp_handler(business_id: str):
    """
    Dependency that creates and returns a WhatsAppWebhookHandler instance
    based on business ID credentials.
    """
    if not business_id:
        return None
    
    credentials = await get_credentials_by_business_id(business_id)
    if credentials:
        return WhatsAppWebhookHandler(credentials)
    return None

# Dependency to get Messenger WebhookHandler
async def get_messenger_handler(page_id: str):
    """
    Dependency that creates and returns a MessengerWebhookHandler instance
    based on page ID credentials.
    """
    if not page_id:
        return None
    
    credentials = await get_credentials_by_page_id(page_id)
    if credentials:
        return MessengerWebhookHandler(credentials)
    return None

# Dependency to get Telegram WebhookHandler
async def get_telegram_handler(bot_token: str):
    """
    Dependency that creates and returns a TelegramWebhookHandler instance
    based on bot token credentials.
    """
    if not bot_token:
        return None
    
    credentials = await get_telegram_credentials_by_token(bot_token)
    if credentials:
        return TelegramWebhookHandler(credentials)
    return None

@webhook_router.post("/webhook-whatsapp")
async def whatsapp_webhook_handler(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Handle incoming WhatsApp messages (text & voice) and determine client_id from recipient number.
    Uses the WhatsAppWebhookHandler class to process messages in the background.
    
    This endpoint receives webhook notifications from WhatsApp Business API when users send messages.
    It processes the messages and sends AI-powered responses back to the users.
    """
    try:
        # Log request details for debugging
        logging.info(f"🔍 WhatsApp webhook request received")
        logging.info(f"🔍 Request method: {request.method}")
        logging.info(f"🔍 Request URL: {request.url}")
        logging.info(f"🔍 Request headers: {dict(request.headers)}")
        
        # Get the raw body first to check if it's empty
        body = await request.body()
        logging.info(f"🔍 Request body length: {len(body) if body else 0}")
        logging.info(f"🔍 Request body: {body[:500] if body else 'None'}")  # Log first 500 chars
        
        if not body:
            logging.warning("⚠️ Received empty webhook request body")
            return {"status": "no_data", "message": "Empty request body received"}
        
        # Try to parse JSON
        try:
            data = json.loads(body)
        except json.JSONDecodeError as e:
            logging.error(f"❌ Failed to parse webhook JSON: {e}")
            logging.error(f"Raw body: {body}")
            return {"status": "invalid_json", "message": f"JSON parsing failed: {str(e)}"}
        
        logging.info(f"✅ Successfully parsed WhatsApp data: {json.dumps(data, indent=2)}")

        # Extract main WhatsApp payload details
        entry = data.get("entry", [])
        if not entry:
            logging.warning("⚠️ No entry found in webhook data")
            return {"status": "no_entry", "message": "No entry found in webhook data"}
            
        entry = entry[0]
        changes = entry.get("changes", [])
        if not changes:
            logging.warning("⚠️ No changes found in webhook data")
            return {"status": "no_changes", "message": "No changes found in webhook data"}
            
        changes = changes[0]
        messages = changes.get("value", {}).get("messages", [])

        # Extract the WhatsApp Business Account ID
        whatsapp_business_account_id = entry.get("id")
        
        if not whatsapp_business_account_id:
            logging.error("❌ No WhatsApp Business Account ID found in webhook data.")
            return {"status": "error", "message": "Missing business account ID"}

        # Get the handler with the business credentials
        webhook_handler = await get_whatsapp_handler(whatsapp_business_account_id)
        
        if not webhook_handler:
            logging.error(f"❌ [webhook_handler_endpoint] No matching client found for business account ID {whatsapp_business_account_id}")
            return {"status": "error", "message": "Invalid business account ID"}

        if not messages:
            logging.warning("⚠️ No messages found in the webhook payload.")
            return {"status": "no_message", "message": "No messages found in webhook payload"}

        message_data = messages[0]
        from_number = message_data.get("from")

        if "text" in message_data:
            user_message = message_data["text"]["body"].strip()
            logging.info(f"📩 Received text from {from_number}: {user_message}")
            
            # Process the text message in the background
            background_tasks.add_task(
                webhook_handler.process_text_message,
                from_number, 
                user_message
            )
            
        elif "audio" in message_data:
            media_id = message_data["audio"]["id"]
            logging.info(f"🎤 Received voice message from {from_number}, Media ID: {media_id}")
            
            # Process the voice message in the background
            background_tasks.add_task(
                webhook_handler.process_voice_message,
                from_number, 
                media_id
            )

        else:
            logging.info(f"📩 Received unsupported message type from {from_number}")
            return {"status": "unsupported", "message": "Unsupported message type"}

        return {"status": "message_processed", "message": "Message processed successfully"}

    except Exception as e:
        logging.error(f"❌ Error processing WhatsApp message: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@webhook_router.post("/webhook/messenger",
    summary="Messenger Webhook",
    description="Handle incoming Facebook Messenger messages and process them with AI responses",
    response_description="Message processing status")
async def messenger_webhook_handler(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Handle incoming Facebook Messenger messages.
    
    This endpoint receives webhook notifications from Facebook Messenger when users send messages.
    It processes text messages, audio attachments, and other media types.
    """
    try:
        data = await request.json()
        logging.info(f"Incoming Messenger data: {json.dumps(data, indent=2)}")
        
        # Check if this is a page webhook
        if "object" not in data or data["object"] != "page":
            logging.error("❌ Received non-page webhook event")
            return {"status": "error", "message": "Webhook event object is not 'page'"}
            
        # Process each entry (usually just one)
        for entry in data.get("entry", []):
            page_id = entry.get("id")
            
            if not page_id:
                logging.error("❌ No page ID found in webhook data.")
                continue
                
            # Get the handler for this page
            webhook_handler = await get_messenger_handler(page_id)
            
            if not webhook_handler:
                logging.error(f"❌ No matching client found for page ID {page_id}")
                continue
                
            # Process each messaging event
            for messaging in entry.get("messaging", []):
                sender_id = messaging.get("sender", {}).get("id")
                
                if not sender_id:
                    logging.error("❌ No sender ID found in messaging data.")
                    continue
                    
                # Check for text message
                if "message" in messaging and "text" in messaging["message"]:
                    text = messaging["message"]["text"]
                    logging.info(f"📩 Received Messenger text from {sender_id}: {text}")
                    
                    # Process the text message in the background
                    background_tasks.add_task(
                        webhook_handler.process_text_message,
                        sender_id, 
                        text
                    )
                
                # Check for attachments
                elif "message" in messaging and "attachments" in messaging["message"]:
                    attachments = messaging["message"]["attachments"]
                    logging.info(f"📎 Received Messenger attachment from {sender_id}: {json.dumps(attachments, indent=2)}")
                    
                    for attachment in attachments:
                        attachment_type = attachment.get("type", "").lower()
                        
                        # Handle audio attachments specially
                        if attachment_type == "audio":
                            logging.info(f"🎤 Received audio attachment from {sender_id}")
                            
                            # Extract audio details
                            payload = attachment.get("payload", {})
                            url = payload.get("url")
                            
                            if url:
                                logging.info(f"🔗 Audio URL: {url}")
                                # Process audio directly with URL
                                background_tasks.add_task(
                                    webhook_handler.process_voice_message,
                                    sender_id,
                                    url
                                )
                            else:
                                # Try to get attachment ID
                                attachment_id = payload.get("attachment_id")
                                if attachment_id:
                                    logging.info(f"🔢 Audio attachment ID: {attachment_id}")
                                    background_tasks.add_task(
                                        webhook_handler.process_voice_message,
                                        sender_id,
                                        attachment_id
                                    )
                                else:
                                    logging.error(f"❌ No URL or attachment ID found for audio: {payload}")
                                    background_tasks.add_task(
                                        webhook_handler.message_handler.send_text,
                                        sender_id,
                                        "I received your audio, but couldn't process it. Please try again."
                                    )
                        else:
                            # Process other attachment types
                            background_tasks.add_task(
                                webhook_handler.process_attachment,
                                sender_id, 
                                attachment
                            )
                else:
                    logging.info(f"📩 Received unsupported Messenger event from {sender_id}: {json.dumps(messaging, indent=2)}")
        
        return {"status": "messages_processed"}
        
    except Exception as e:
        logging.error(f"❌ Error processing Messenger message: {str(e)}", exc_info=True)
        return {"status": "error", "message": str(e)}

@webhook_router.post("/webhook/telegram/{bot_token}",
    summary="Telegram Webhook",
    description="Handle incoming Telegram messages and process them with AI responses",
    response_description="Message processing status")
async def telegram_webhook_handler(
    bot_token: str, 
    request: Request, 
    background_tasks: BackgroundTasks
):
    """
    Handle incoming Telegram messages.
    The bot token is used to identify which client's bot is receiving the message.
    
    This endpoint receives webhook notifications from Telegram when users send messages to your bot.
    It processes the messages and sends AI-powered responses back to the users.
    """
    try:
        # Verify the token matches a registered bot
        webhook_handler = await get_telegram_handler(bot_token)
        
        if not webhook_handler:
            logging.error(f"❌ No matching client found for bot token: {bot_token[:10]}...")
            return {"status": "error", "message": "Invalid bot token"}
            
        # Process the update
        data = await request.json()
        logging.info(f"Incoming Telegram update: {data}")
        
        if "message" not in data:
            logging.info("No message in Telegram update")
            return {"status": "no_message"}
            
        message = data["message"]
        chat_id = str(message.get("chat", {}).get("id"))
        
        if not chat_id:
            logging.error("❌ No chat ID found in Telegram message")
            return {"status": "error", "message": "Missing chat ID"}
            
        # Check for text message
        if "text" in message:
            text = message["text"]
            logging.info(f"📩 Received Telegram text from {chat_id}: {text}")
            
            # Process the text message in the background
            background_tasks.add_task(
                webhook_handler.process_text_message,
                chat_id, 
                text
            )
            
        # Check for voice message
        elif "voice" in message:
            file_id = message["voice"]["file_id"]
            logging.info(f"🎤 Received Telegram voice from {chat_id}, File ID: {file_id}")
            
            # Process the voice message in the background
            background_tasks.add_task(
                webhook_handler.process_voice_message,
                chat_id, 
                file_id
            )
            
        else:
            logging.info(f"📩 Received unsupported Telegram message from {chat_id}")
            # Let the user know we only support text and voice for now
            background_tasks.add_task(
                webhook_handler.message_handler.send_text,
                chat_id,
                "I can only process text and voice messages at the moment."
            )
            
        return {"status": "message_processed"}
        
    except Exception as e:
        logging.error(f"❌ Error processing Telegram message: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}
    

# Add this dependency function to webhook_router.py
async def get_twilio_handler(account_sid: str):
    """
    Dependency that creates and returns a TwilioWebhookHandler instance
    based on account SID credentials.
    """
    if not account_sid:
        return None
    
    credentials = await get_twilio_credentials_by_account_sid(account_sid)
    if credentials:
        return TwilioWebhookHandler(credentials)
    return None

# Add this webhook endpoint to webhook_router.py
@webhook_router.post("/webhook-twilio")
async def twilio_webhook_handler(
    request: Request,
    background_tasks: BackgroundTasks,
    AccountSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    Body: str = Form(None),
    NumMedia: int = Form(0),
    MediaContentType0: str = Form(None),
    MediaUrl0: str = Form(None),
    MessageSid: str = Form(...),
):
    """
    Handle incoming Twilio WhatsApp messages (text & voice).
    Uses the TwilioWebhookHandler class to process messages in the background.
    """
    try:
        logging.info(f"Incoming Twilio data: AccountSid={AccountSid}, From={From}, To={To}, NumMedia={NumMedia}")
        
        # Get the handler with the Twilio credentials
        webhook_handler = await get_twilio_handler(AccountSid)
        
        if not webhook_handler:
            logging.error(f"❌ No matching client found for Twilio account SID: {AccountSid}")
            return Response(content="Invalid Account SID", status_code=403)

        # Check if this is a voice message
        is_voice = NumMedia > 0 and MediaContentType0 and "audio" in MediaContentType0.lower()
        
        if Body and not is_voice:
            # Process text message
            user_message = Body.strip()
            logging.info(f"📩 Received text from {From}: {user_message}")
            
            # Process the text message in the background
            background_tasks.add_task(
                webhook_handler.process_text_message,
                From,  # Keep the 'whatsapp:' prefix
                user_message
            )
            
        elif is_voice and MediaUrl0:
            # Process voice message
            logging.info(f"🎤 Received voice message from {From}, Media URL: {MediaUrl0}")
            
            # Process the voice message in the background
            background_tasks.add_task(
                webhook_handler.process_voice_message,
                From,  # Keep the 'whatsapp:' prefix
                MediaUrl0  # Pass the media URL directly
            )
            
        elif NumMedia > 0 and MediaUrl0:
            # Handle other types of media (images, documents, etc.)
            logging.info(f"📎 Received media from {From}, Media URL: {MediaUrl0}")
            
            # For now, respond with a simple acknowledgment
            background_tasks.add_task(
                webhook_handler.message_handler.send_text,
                From,
                "I received your media attachment, but I currently only process text and voice messages."
            )
            
        else:
            logging.info(f"📩 Received unsupported message type from {From}")
            # Let the user know what we support
            background_tasks.add_task(
                webhook_handler.message_handler.send_text,
                From,
                "I can only process text and voice messages at the moment."
            )
            
        # Return a TwiML response
        twiml_response = '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'
        return Response(content=twiml_response, media_type="application/xml")
        
    except Exception as e:
        logging.error(f"❌ Error processing Twilio message: {e}", exc_info=True)
        # Return a TwiML response even on error
        twiml_response = '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'
        return Response(content=twiml_response, media_type="application/xml")
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
import logging
import os
import httpx
import json
from src.utils.config import (
    verify_messenger_token,
    verify_telegram_token,
    verify_twilio_token,
    verify_whatsapp_token,
    get_credentials_by_business_id
)
from src.app.routers.message_router import message_router
from src.app.routers.webhook_router import webhook_router
from src.app.routers.send_sheet_router import sheet_router
from fastapi.middleware.cors import CORSMiddleware
from src.webhook_handler.whatsapp_webhook_handler import WhatsAppWebhookHandler


# Initialize FastAPI app
app = FastAPI(
    title="WhatsApp Cloud API",
    description="Multi-platform messaging API for WhatsApp, Messenger, Telegram, and Twilio",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Include routers with proper prefixes and tags
app.include_router(
    message_router,
    prefix="/api/v1",
    tags=["Messaging"],
    responses={404: {"description": "Not found"}}
)

app.include_router(
    webhook_router,
    prefix="/api/v1",
    tags=["Webhooks"],
    responses={404: {"description": "Not found"}}
)

app.include_router(
    sheet_router,
    prefix="/api/v1",
    tags=["Bulk Messaging"],
    responses={404: {"description": "Not found"}}
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for testing, restrict this in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)


@app.get("/", tags=["Health"])
def read_root():
    """
    Health check endpoint to verify the API is running.
    """
    return {
        "message": "WhatsApp Cloud API is running",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs"
    }

@app.get("/health", tags=["Health"])
def health_check():
    """
    Detailed health check endpoint.
    """
    return {
        "status": "healthy",
        "service": "WhatsApp Cloud API",
        "version": "1.0.0",
        "timestamp": "2024-01-01T00:00:00Z"
    }

# Webhook verification endpoints (moved to main for better organization)
@app.get("/webhook-whatsapp", tags=["Webhook Verification"])
async def verify_webhook_whatsapp(request: Request):
    """
    WhatsApp webhook verification endpoint.
    
    Used by WhatsApp to verify your webhook URL during setup.
    Requires hub.challenge and hub.verify_token query parameters.
    """
    challenge = request.query_params.get("hub.challenge")
    token = request.query_params.get("hub.verify_token")

    logging.info(f"🔍 WhatsApp webhook verification request received")
    logging.info(f"🔍 Challenge: {challenge}")
    logging.info(f"🔍 Token: {token[:10] if token else 'None'}...")

    # Check if token is provided
    if not token:
        logging.error("❌ No verify_token provided in webhook verification request")
        return {"error": "Missing verify_token parameter"}

    # Verify the token
    if await verify_whatsapp_token(token):
        if challenge:
            logging.info(f"✅ Webhook verification successful, returning challenge: {challenge}")
            return int(challenge)
        else:
            logging.warning("⚠️ Token verified but no challenge provided")
            return {"status": "verified", "message": "Token verified but no challenge provided"}
    else:
        logging.error("❌ Webhook verification failed - invalid token")
        return {"error": "Verification failed - invalid token"}

@app.get("/webhook-messenger", tags=["Webhook Verification"])
async def verify_webhook_messenger(request: Request):
    """
    Facebook Messenger webhook verification endpoint.
    
    Used by Messenger to verify your webhook URL during setup.
    Requires hub.challenge and hub.verify_token query parameters.
    """
    challenge = request.query_params.get("hub.challenge")
    token = request.query_params.get("hub.verify_token")

    logging.info(f"Messenger webhook verification request received: token={token}, challenge={challenge}")

    if await verify_messenger_token(token):
        return int(challenge) if challenge else "Missing challenge"
    
    return {"error": "Verification failed"}

@app.get("/telegram-webhook/{bot_token}", tags=["Webhook Verification"])
async def telegram_webhook_handler(token: str, request: Request):
    """
    Telegram webhook verification and setup endpoint.
    
    - Takes the bot token from the URL path
    - Verifies it against configured TELEGRAM_BOT_TOKEN values
    - Sets up the webhook with Telegram API
    """
    logging.info(f"Telegram webhook request received for token: {token[:8]}...")
    
    # Verify this is a valid bot token
    if not await verify_telegram_token(token):
        logging.error(f"Invalid Telegram bot token received: {token[:8]}...")
        raise HTTPException(status_code=403, detail="Invalid bot token")
    
    # Get the base URL for the webhook callback
    host = request.headers.get("host", "api.lenaai.net")
    scheme = request.headers.get("x-forwarded-proto", "https")
    base_url = f"{scheme}://{host}"
    
    # Construct the full webhook URL
    webhook_url = f"{base_url}/telegram-webhook/{token}"
    
    # Call Telegram API to set the webhook
    telegram_api_url = f"https://api.telegram.org/bot{token}/setWebhook"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(telegram_api_url, params={"url": webhook_url})
            result = response.json()
            
            if response.status_code == 200 and result.get("ok"):
                return {
                    "status": "success", 
                    "message": f"Webhook successfully set to {webhook_url}",
                    "telegram_response": result
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to set webhook",
                    "telegram_response": result
                }
    
    except Exception as e:
        logging.error(f"Error setting Telegram webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error setting webhook: {str(e)}")

@app.get("/webhook-twilio", tags=["Webhook Verification"])
async def verify_webhook_twilio(request: Request):
    """
    Twilio webhook verification endpoint.
    
    Twilio usually just needs a 200 OK response for validation.
    No special verification required.
    """
    logging.info("Twilio webhook verification request received")
    
    # Just return OK for Twilio webhook verification
    return {"status": "success", "message": "Twilio webhook URL is valid"}

@app.post("/verify-twilio", tags=["Authentication"])
async def verify_twilio_auth(request: Request):
    """
    Verify a Twilio auth token against stored credentials.
    
    Used to validate Twilio authentication tokens.
    """
    try:
        data = await request.json()
        token = data.get("auth_token")
        
        if not token:
            return {"valid": False, "message": "No auth token provided"}
        
        is_valid = await verify_twilio_token(token)
        
        if is_valid:
            return {"valid": True, "message": "Auth token is valid"}
        else:
            return {"valid": False, "message": "Auth token does not match any client"}
            
    except Exception as e:
        logging.error(f"Error verifying Twilio token: {str(e)}")
        return {"valid": False, "error": str(e)}


import uvicorn


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8008)
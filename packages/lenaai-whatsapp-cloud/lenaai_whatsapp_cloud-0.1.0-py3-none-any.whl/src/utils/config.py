import json
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import HTTPException
from google.cloud import secretmanager
from typing import Dict, Optional

# Load environment variables from .env file
load_dotenv(override=True)

def access_secret(secret_id: str) -> Optional[str]:
    """Retrieve a secret from Google Secret Manager."""
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{GOOGLE_CLOUD_PROJECT_ID}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"Error accessing secret {secret_id}: {str(e)}")
        return None

LOCAL_ENV = os.getenv("LOCAL_ENV", "False").lower() == "true"
GOOGLE_CLOUD_PROJECT_ID = "chat-history-449709"
# Load VERIFY_TOKEN
if LOCAL_ENV:
    CLIENT_SECRET_FILE = os.getenv("CLIENT_SECRET_FILE")
else:
    CLIENT_SECRET_FILE = access_secret("CLIENT_SECRET_FILE")

if not CLIENT_SECRET_FILE:
    raise ValueError("Missing CLIENT_SECRET_FILE environment variable.")

# Lena Ai endpoints
LENAAI_CHAT_ENDPOINT="https://api.lenaai.net/chat"
LENAAI_LANGGRAPH_ENDPOINT="https://api.lenaai.net/chat/langgraph"
LENAAI_VOICE_PROCESS_ENDPOINT="https://api.lenaai.net/voice_process"
LENAAI_UPDATE_DB_ENDPOINT="https://api.lenaai.net/add_bot_response"
LENAAI_LEADING_MESSAGE_ENDPOINT="https://api.lenaai.net/leading_message"
# google drive 
TOKEN_FILE = "token.json"
SHEET_SCOPE = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
MAX_MESSAGES = 100 
FACEBOOK_GRAPH_API_VERSION = "v18.0"

async def get_credentials(client_id: str) -> Dict[str, str]:
    """Retrieve WhatsApp credentials asynchronously based on the client ID."""
    if not client_id:
        raise ValueError("Client ID is required.")

    if LOCAL_ENV:
        access_token = os.getenv(f"WHATSAPP_ACCESS_TOKEN_{client_id}")
        phone_number_id = os.getenv(f"WHATSAPP_PHONE_NUMBER_ID_{client_id}")
    else:
        access_token = access_secret(f"WHATSAPP_ACCESS_TOKEN_{client_id}")
        phone_number_id = access_secret(f"WHATSAPP_PHONE_NUMBER_ID_{client_id}")

    if not access_token or not phone_number_id:
        raise ValueError(f"Missing credentials for client ID: {client_id}")

    return {
        "access_token": access_token,
        "phone_number_id": phone_number_id,
        "client_id": client_id
    }

async def get_messenger_credentials(client_id: str) -> Dict[str, str]:
    """Retrieve Messenger credentials asynchronously based on the client ID."""
    if not client_id:
        raise ValueError("Client ID is required.")

    if LOCAL_ENV:
        access_token = os.getenv(f"MESSENGER_ACCESS_TOKEN_{client_id}")
        page_id = os.getenv(f"MESSENGER_PAGE_ID_{client_id}")
    else:
        access_token = access_secret(f"MESSENGER_ACCESS_TOKEN_{client_id}")
        page_id = access_secret(f"MESSENGER_PAGE_ID_{client_id}")

    if not access_token or not page_id:
        raise ValueError(f"Missing Messenger credentials for client ID: {client_id}")

    return {
        "access_token": access_token,
        "page_id": page_id,
        "client_id": client_id
    }

async def get_telegram_api_credentials(client_id: str) -> Dict[str, str]:
    """Retrieve Telegram API credentials for Telethon client, based on the client ID."""
    if not client_id:
        raise ValueError("Client ID is required.")
        
    if LOCAL_ENV:
        api_id = os.getenv(f"TELEGRAM_API_ID_{client_id}")
        api_hash = os.getenv(f"TELEGRAM_API_HASH_{client_id}")
        phone = os.getenv(f"TELEGRAM_PHONE_{client_id}")
    else:
        api_id = access_secret(f"TELEGRAM_API_ID_{client_id}")
        api_hash = access_secret(f"TELEGRAM_API_HASH_{client_id}")
        phone = access_secret(f"TELEGRAM_PHONE_{client_id}")
        
    if not api_id or not api_hash or not phone:
        raise ValueError(f"Missing Telegram API credentials for client_id: {client_id}")
        
    return {
        "api_id": api_id,
        "api_hash": api_hash,
        "phone": phone,
        "client_id": client_id
    }

async def get_telegram_client_credentials(client_id: str) -> Dict[str, str]:
    """
    Retrieve all Telegram credentials needed for the client operation.
    This combines both API credentials for Telethon and bot token.
    """
    if not client_id:
        raise ValueError("Client ID is required.")
        
    # Get Telegram bot credentials (token)
    bot_credentials = await get_telegram_credentials(client_id)
    
    # Get Telegram API credentials (for Telethon client)
    api_credentials = await get_telegram_api_credentials(client_id)
    
    # Combine all credentials
    combined_credentials = {**bot_credentials, **api_credentials}
    
    return combined_credentials

async def get_credentials_by_business_id(whatsapp_business_account_id: str) -> Optional[Dict[str, str]]:
    """Retrieve client credentials dynamically using the WhatsApp Business Account ID."""
    
    LOCAL_ENV = os.getenv("LOCAL_ENV", "False").lower() == "true"

    if LOCAL_ENV:
        client_ids_str = os.getenv("CLIENT_IDS", "")
    else:
        client_ids_str = access_secret("CLIENT_IDS")  # Fetch from Google Secret Manager

    if not client_ids_str:
        return None

    # Properly split the client IDs using `,`
    client_ids = [c.strip() for c in client_ids_str.split(",") if c.strip()]

    for client_id in client_ids:
        print(f"🔍 Checking credentials for client_id: {client_id}")

        if LOCAL_ENV:
            stored_business_id = os.getenv(f"WHATSAPP_BUSINESS_ACCOUNT_{client_id}")
        else:
            stored_business_id = access_secret(f"WHATSAPP_BUSINESS_ACCOUNT_{client_id}")

        if str(stored_business_id) == str(whatsapp_business_account_id):
            print(f"✅ Match found! client_id: {client_id}")
            return await get_credentials(client_id)

    return None

async def get_credentials_by_page_id(page_id: str) -> Optional[Dict[str, str]]:
    """Retrieve client credentials dynamically using the Facebook Page ID."""
    
    LOCAL_ENV = os.getenv("LOCAL_ENV", "False").lower() == "true"

    if LOCAL_ENV:
        client_ids_str = os.getenv("CLIENT_IDS", "")
    else:
        client_ids_str = access_secret("CLIENT_IDS")  # Fetch from Google Secret Manager

    if not client_ids_str:
        return None

    # Properly split the client IDs using `,`
    client_ids = [c.strip() for c in client_ids_str.split(",") if c.strip()]

    for client_id in client_ids:
        print(f"🔍 Checking Messenger credentials for client_id: {client_id}")

        if LOCAL_ENV:
            stored_page_id = os.getenv(f"MESSENGER_PAGE_ID_{client_id}")
        else:
            stored_page_id = access_secret(f"MESSENGER_PAGE_ID_{client_id}")

        if str(stored_page_id) == str(page_id):
            print(f"✅ Match found! client_id: {client_id}")
            return await get_messenger_credentials(client_id)

    return None

async def get_telegram_credentials(client_id: str) -> Dict[str, str]:
    """Retrieve Telegram bot credentials asynchronously based on the client ID."""
    if not client_id:
        raise ValueError("Client ID is required.")

    LOCAL_ENV = os.getenv("LOCAL_ENV", "False").lower() == "true"
    
    if LOCAL_ENV:
        bot_token = os.getenv(f"TELEGRAM_BOT_TOKEN_{client_id}")
    else:
        bot_token = access_secret(f"TELEGRAM_BOT_TOKEN_{client_id}")
    
    if not bot_token:
        raise ValueError(f"Missing Telegram bot token for client ID: {client_id}")
    
    return {
        "bot_token": bot_token,
        "client_id": client_id
    }

async def get_telegram_credentials_by_token(bot_token: str) -> Optional[Dict[str, str]]:
    """Retrieve Telegram bot credentials dynamically using the bot token."""
    LOCAL_ENV = os.getenv("LOCAL_ENV", "False").lower() == "true"

    if LOCAL_ENV:
        client_ids_str = os.getenv("CLIENT_IDS", "")
    else:
        client_ids_str = access_secret("CLIENT_IDS")  # Fetch from Google Secret Manager
    
    if not client_ids_str:
        return None
    
    # Properly split the client IDs using `,`
    client_ids = [c.strip() for c in client_ids_str.split(",") if c.strip()]
    
    for client_id in client_ids:
        print(f"🔍 Checking credentials for client_id: {client_id}")
        
        if LOCAL_ENV:
            stored_bot_token = os.getenv(f"TELEGRAM_BOT_TOKEN_{client_id}")
        else:
            stored_bot_token = access_secret(f"TELEGRAM_BOT_TOKEN_{client_id}")
        
        if stored_bot_token == bot_token:
            print(f"✅ Match found! client_id: {client_id}")
            return await get_telegram_credentials(client_id)
    
    return None

async def store_session_string(client_id, session_string):
    """
    Store the session string for a client to avoid interactive authentication.
    
    Args:
        client_id: The identifier for the client
        session_string: The session string to store
    """
    try:
        # Ensure credentials directory exists
        Path("./credentials").mkdir(exist_ok=True)
        
        credentials_path = Path(f"./credentials/{client_id}.json")
        
        # If file doesn't exist, create it with session string
        if not credentials_path.exists():
            credentials = {
                "session_string": session_string
            }
        else:
            # Otherwise, update existing file
            with open(credentials_path, "r") as f:
                credentials = json.load(f)
            
            # Update with session string
            credentials["session_string"] = session_string
        
        with open(credentials_path, "w") as f:
            json.dump(credentials, f, indent=4)
            
        return True
        
    except Exception as e:
        logging.error(f"Error storing session string: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error storing session string: {str(e)}")
    

async def get_telegram_user_credentials(client_id: str) -> Dict[str, str]:
    """
    Retrieve Telegram user account credentials for Pyrogram client.
    This function prioritizes user account credentials over bot tokens.
    """
    if not client_id:
        raise ValueError("Client ID is required.")
    
    LOCAL_ENV = os.getenv("LOCAL_ENV", "False").lower() == "true"
    
    # Getting API credentials
    if LOCAL_ENV:
        api_id = os.getenv(f"TELEGRAM_API_ID_{client_id}")
        api_hash = os.getenv(f"TELEGRAM_API_HASH_{client_id}")
        phone = os.getenv(f"TELEGRAM_PHONE_{client_id}")
    else:
        api_id = access_secret(f"TELEGRAM_API_ID_{client_id}")
        api_hash = access_secret(f"TELEGRAM_API_HASH_{client_id}")
        phone = access_secret(f"TELEGRAM_PHONE_{client_id}")
    
    # Convert API ID to integer if it's a string
    if api_id and isinstance(api_id, str):
        try:
            api_id = int(api_id)
        except ValueError:
            logging.error(f"Invalid API ID format for client ID {client_id}")
    
    # Return user credentials
    return {
        "api_id": api_id,
        "api_hash": api_hash,
        "phone_number": phone,  # Note: Using phone_number key for Pyrogram client
        "client_id": client_id
    }

# Update this function in your config.py

async def get_telegram_client_credentials(client_id: str) -> Dict[str, str]:
    """
    Retrieve all Telegram credentials needed for the client operation.
    This combines both API credentials and bot token, prioritizing user account.
    """
    if not client_id:
        raise ValueError("Client ID is required.")
    
    # Get Telegram bot credentials (token)
    try:
        bot_credentials = await get_telegram_credentials(client_id)
    except Exception as e:
        logging.warning(f"Error getting bot credentials: {str(e)}")
        bot_credentials = {"client_id": client_id}
    
    # Get Telegram API credentials (for user account)
    try:
        user_credentials = await get_telegram_user_credentials(client_id)
    except Exception as e:
        logging.warning(f"Error getting user credentials: {str(e)}")
        user_credentials = {"client_id": client_id}
    
    # Combine all credentials, prioritizing user account credentials
    combined_credentials = {**bot_credentials, **user_credentials}
    
    # Log the credential types we have (for debugging)
    has_bot = "bot_token" in combined_credentials and combined_credentials["bot_token"]
    has_user = all(k in combined_credentials and combined_credentials[k] for k in ["api_id", "api_hash", "phone_number"])
    
    logging.info(f"Telegram credentials for {client_id}: has_bot_token={has_bot}, has_user_account={has_user}")
    
    return combined_credentials

async def get_all_client_ids():
    """Get all client IDs from environment variables or secret manager."""
    if LOCAL_ENV:
        client_ids_str = os.getenv("CLIENT_IDS", "")
    else:
        client_ids_str = access_secret("CLIENT_IDS")
    
    if not client_ids_str:
        return []
    
    # Split and clean client IDs
    return [c.strip() for c in client_ids_str.split(",") if c.strip()]

async def verify_whatsapp_token(token):
    """
    Verify the token against all VERIFY_TOKEN_{CLIENT_ID} tokens
    """
    # Handle None or empty token
    if not token:
        logging.error(f"❌ WhatsApp token verification failed. Token is None or empty.")
        return False
    
    # Get all client IDs
    client_ids = await get_all_client_ids()
    
    logging.info(f"🔍 Verifying WhatsApp token against {len(client_ids)} clients")
    
    # Check client-specific tokens
    for client_id in client_ids:
        if LOCAL_ENV:
            client_token = os.getenv(f"VERIFY_TOKEN_{client_id}")
        else:
            client_token = access_secret(f"VERIFY_TOKEN_{client_id}")
        
        logging.info(f"🔍 Checking client {client_id}: token={client_token[:10] if client_token else 'None'}...")
        
        if token == client_token:
            logging.info(f"✅ Matched WhatsApp verification token for client: {client_id}")
            return True
    
    logging.error(f"❌ WhatsApp token verification failed. No matching token found for token: {token[:10] if token else 'None'}...")
    return False

async def verify_messenger_token(token):
    """
    Verify the token against all MESSENGER_ACCESS_TOKEN_{CLIENT_ID} tokens
    """
    # Get all client IDs
    client_ids = await get_all_client_ids()
    
    # Check client-specific tokens
    for client_id in client_ids:
        if LOCAL_ENV:
            client_token = os.getenv(f"MESSENGER_ACCESS_TOKEN_{client_id}")
        else:
            client_token = access_secret(f"MESSENGER_ACCESS_TOKEN_{client_id}")
        
        if token == client_token:
            logging.info(f"Matched Messenger access token for client: {client_id}")
            return True
    
    logging.error(f"❌ Messenger token verification failed. No matching token found.")
    return False

async def verify_telegram_token(token):
    """
    Verify the token against all TELEGRAM_BOT_TOKEN_{CLIENT_ID} tokens
    """
    # Get all client IDs
    client_ids = await get_all_client_ids()
    
    # Check client-specific tokens
    for client_id in client_ids:
        if LOCAL_ENV:
            client_token = os.getenv(f"TELEGRAM_BOT_TOKEN_{client_id}")
        else:
            client_token = access_secret(f"TELEGRAM_BOT_TOKEN_{client_id}")
        
        if token == client_token:
            logging.info(f"Matched Telegram bot token for client: {client_id}")
            return True
    
    logging.error(f"❌ Telegram token verification failed. No matching token found.")
    return False

async def get_twilio_credentials(client_id: str) -> Dict[str, str]:
    """Retrieve Twilio credentials asynchronously based on the client ID."""
    if not client_id:
        raise ValueError("Client ID is required.")

    if LOCAL_ENV:
        account_sid = os.getenv(f"TWILIO_ACCOUNT_SID_{client_id}")
        auth_token = os.getenv(f"TWILIO_AUTH_TOKEN_{client_id}")
        phone_number = os.getenv(f"TWILIO_FROM_NUMBER_{client_id}")
    else:
        account_sid = access_secret(f"TWILIO_ACCOUNT_SID_{client_id}")
        auth_token = access_secret(f"TWILIO_AUTH_TOKEN_{client_id}")
        phone_number = access_secret(f"TWILIO_FROM_NUMBER_{client_id}")

    if not account_sid or not auth_token or not phone_number:
        raise ValueError(f"Missing Twilio credentials for client ID: {client_id}")

    return {
        "account_sid": account_sid,
        "auth_token": auth_token,
        "phone_number": phone_number,
        "client_id": client_id
    }

async def get_twilio_credentials_by_account_sid(account_sid: str) -> Optional[Dict[str, str]]:
    """Retrieve client credentials dynamically using the Twilio Account SID."""
    
    if LOCAL_ENV:
        client_ids_str = os.getenv("CLIENT_IDS", "")
    else:
        client_ids_str = access_secret("CLIENT_IDS")

    if not client_ids_str:
        return None

    client_ids = [c.strip() for c in client_ids_str.split(",") if c.strip()]

    for client_id in client_ids:
        print(f"🔍 Checking Twilio credentials for client_id: {client_id}")

        if LOCAL_ENV:
            stored_account_sid = os.getenv(f"TWILIO_ACCOUNT_SID_{client_id}")
        else:
            stored_account_sid = access_secret(f"TWILIO_ACCOUNT_SID_{client_id}")

        if str(stored_account_sid) == str(account_sid):
            print(f"✅ Match found! client_id: {client_id}")
            return await get_twilio_credentials(client_id)

    return None

async def verify_twilio_token(token):
    """
    Verify the token against all TWILIO_AUTH_TOKEN_{CLIENT_ID} tokens
    """
    # Get all client IDs
    client_ids = await get_all_client_ids()
    
    # Check client-specific tokens
    for client_id in client_ids:
        if LOCAL_ENV:
            client_token = os.getenv(f"TWILIO_AUTH_TOKEN_{client_id}")
        else:
            client_token = access_secret(f"TWILIO_AUTH_TOKEN_{client_id}")
        
        if token == client_token:
            logging.info(f"Matched Twilio auth token for client: {client_id}")
            return True
    
    logging.error(f"❌ Twilio token verification failed. No matching token found.")
    return False


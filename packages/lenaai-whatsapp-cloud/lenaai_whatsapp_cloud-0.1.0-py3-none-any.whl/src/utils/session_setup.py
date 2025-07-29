import asyncio
import json
import argparse
from pathlib import Path
from pyrogram import Client

async def setup_telegram_session(client_id):
    """
    Interactive script to set up a Telegram session and save the session string.
    This should be run once per client to generate the session string.
    """
    # Load credentials
    credentials_path = Path(f"./credentials/{client_id}.json")
    
    if not credentials_path.exists():
        print(f"Error: Client ID {client_id} not found")
        return False
    
    with open(credentials_path, "r") as f:
        credentials = json.load(f)
    
    # Ensure API ID is an integer
    if isinstance(credentials.get("api_id"), str):
        credentials["api_id"] = int(credentials["api_id"])
    
    # Get required credentials
    api_id = credentials.get("api_id")
    api_hash = credentials.get("api_hash")
    phone_number = credentials.get("phone_number")
    
    if not all([api_id, api_hash, phone_number]):
        print("Error: Missing required credentials (api_id, api_hash, or phone_number)")
        return False
    
    print(f"Setting up Telegram session for client ID: {client_id}")
    print("You will need to complete the authentication process interactively.")
    print("This includes entering the verification code sent to your Telegram account.")
    
    # Create client instance
    client = Client(
        f"temp_session_{client_id}",
        api_id=api_id,
        api_hash=api_hash,
        phone_number=phone_number
    )
    
    try:
        # Start client and generate session string
        await client.start()
        session_string = await client.export_session_string()
        await client.stop()
        
        # Update credentials with session string
        credentials["session_string"] = session_string
        
        with open(credentials_path, "w") as f:
            json.dump(credentials, f, indent=4)
        
        print("Session string generated and saved successfully!")
        print(f"Updated credentials file: {credentials_path}")
        return True
        
    except Exception as e:
        print(f"Error setting up session: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set up Telegram session for a client")
    parser.add_argument("client_id", help="Client ID to set up session for")
    args = parser.parse_args()
    
    asyncio.run(setup_telegram_session(args.client_id))
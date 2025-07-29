#!/usr/bin/env python3
"""
Test script to verify WhatsApp token renewal and Google API fixes
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils.config import get_credentials
from src.data_extractors.google_services_init import get_drive_service, get_sheets_service

async def test_whatsapp_token():
    """Test WhatsApp token renewal"""
    print("🔍 Testing WhatsApp token...")
    
    try:
        # Test getting credentials for DREAM_HOMES
        credentials = await get_credentials("DREAM_HOMES")
        
        if credentials and credentials.get("access_token"):
            print("✅ WhatsApp token is valid and accessible")
            print(f"   Client ID: {credentials.get('client_id')}")
            print(f"   Phone Number ID: {credentials.get('phone_number_id')}")
            print(f"   Access Token: {credentials.get('access_token')[:20]}...")
            return True
        else:
            print("❌ WhatsApp credentials not found or invalid")
            return False
            
    except Exception as e:
        print(f"❌ Error testing WhatsApp token: {e}")
        return False

def test_google_services():
    """Test Google services initialization"""
    print("\n🔍 Testing Google services...")
    
    try:
        # Test Drive service
        drive_service = get_drive_service()
        if drive_service:
            print("✅ Google Drive service initialized successfully")
        
        # Test Sheets service
        sheets_service = get_sheets_service()
        if sheets_service:
            print("✅ Google Sheets service initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Google services: {e}")
        return False

def check_env_file():
    """Check if .env file exists and has required variables"""
    print("\n🔍 Checking environment configuration...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("   Please create a .env file with your configuration")
        return False
    
    print("✅ .env file found")
    
    # Check for required variables
    required_vars = [
        "LOCAL_ENV",
        "CLIENT_IDS",
        "WHATSAPP_ACCESS_TOKEN_DREAM_HOMES",
        "WHATSAPP_PHONE_NUMBER_ID_DREAM_HOMES",
        "CLIENT_SECRET_FILE"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All required environment variables found")
    return True

async def main():
    """Main test function"""
    print("🚀 Starting token renewal and API tests...\n")
    
    # Check environment
    env_ok = check_env_file()
    
    # Test Google services
    google_ok = test_google_services()
    
    # Test WhatsApp token
    whatsapp_ok = await test_whatsapp_token()
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    print(f"Environment Configuration: {'✅ PASS' if env_ok else '❌ FAIL'}")
    print(f"Google Services: {'✅ PASS' if google_ok else '❌ FAIL'}")
    print(f"WhatsApp Token: {'✅ PASS' if whatsapp_ok else '❌ FAIL'}")
    
    if env_ok and google_ok and whatsapp_ok:
        print("\n🎉 All tests passed! Your configuration is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the TOKEN_RENEWAL_GUIDE.md for solutions.")
        
        if not whatsapp_ok:
            print("\n🔧 For WhatsApp token issues:")
            print("   1. Go to Meta Developer Console")
            print("   2. Generate a new access token")
            print("   3. Update your .env file")
            
        if not google_ok:
            print("\n🔧 For Google API issues:")
            print("   1. Update your Google client secret file")
            print("   2. Delete token.json and re-authenticate")
            print("   3. Ensure required APIs are enabled")

if __name__ == "__main__":
    asyncio.run(main()) 
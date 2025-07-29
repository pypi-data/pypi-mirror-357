#!/usr/bin/env python3
"""
Simple test script to verify WhatsApp webhook is working.
"""

import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8008"

def test_empty_request():
    """Test handling of empty requests."""
    print("📭 Testing empty request handling...")
    
    url = f"{BASE_URL}/webhook-whatsapp"
    
    try:
        response = requests.post(url, data="")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Empty request handled properly!")
            return True
        else:
            print("❌ Empty request not handled properly!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing empty request: {e}")
        return False

def test_webhook_verification():
    """Test the webhook verification endpoint."""
    print("\n🔐 Testing WhatsApp webhook verification...")
    
    url = f"{BASE_URL}/webhook-whatsapp"
    params = {
        "hub.mode": "subscribe",
        "hub.challenge": "1234567890",
        "hub.verify_token": "test"  # This should match your verify token
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook verification successful!")
            return True
        else:
            print("❌ Webhook verification failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing webhook verification: {e}")
        return False

def main():
    """Run tests."""
    print("🚀 Starting WhatsApp webhook tests...\n")
    
    # Test empty request handling
    empty_success = test_empty_request()
    
    # Test webhook verification
    verification_success = test_webhook_verification()
    
    print("\n" + "="*50)
    print("📊 Test Results:")
    print(f"Empty Request Handling: {'✅ PASS' if empty_success else '❌ FAIL'}")
    print(f"Webhook Verification: {'✅ PASS' if verification_success else '❌ FAIL'}")
    print("="*50)
    
    if empty_success and verification_success:
        print("\n🎉 Webhook is working correctly!")
        print("Next steps:")
        print("1. Configure your webhook URL in Facebook Developer Console")
        print("2. Test with real WhatsApp messages")
    else:
        print("\n⚠️ Some tests failed. Check your configuration.")

if __name__ == "__main__":
    main() 
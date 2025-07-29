#!/usr/bin/env python3
"""
Test script to send WhatsApp messages
"""

import requests
import json

def test_whatsapp_message():
    base_url = "http://127.0.0.1:8008"
    
    print("🧪 Testing WhatsApp message sending...")
    print(f"📍 Base URL: {base_url}")
    print("-" * 50)
    
    # Test sending WhatsApp message
    print("📱 Testing WhatsApp message endpoint...")
    
    # Replace this with your actual WhatsApp phone number (with country code)
    # Example: "+1234567890" (your actual phone number)
    your_phone_number = "201157745463"  # Change this to your actual WhatsApp number
    
    payload = {
        "platform": "whatsapp",
        "client_id": "DREAM_HOMES",
        "to_number": your_phone_number,
        "message": "Hello! This is a test message from your WhatsApp Cloud API. 🚀"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/message/text",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Message sent successfully!")
            print(f"   📞 Sent to: {your_phone_number}")
        else:
            print("   ❌ Failed to send message")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_whatsapp_message() 
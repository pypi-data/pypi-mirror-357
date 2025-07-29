#!/usr/bin/env python3
"""
Test script to send WhatsApp template messages
"""

import requests
import json

def test_whatsapp_template():
    base_url = "http://127.0.0.1:8008"
    
    print("🧪 Testing WhatsApp template message...")
    print(f"📍 Base URL: {base_url}")
    print("-" * 50)
    
    # Replace with your actual WhatsApp phone number
    your_phone_number = "+201157745463"  # Change this to your actual WhatsApp number
    
    # Test with a simple text template
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
            print("   ✅ Template message sent successfully!")
            print(f"   📞 Sent to: {your_phone_number}")
        else:
            print("   ❌ Failed to send template message")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_whatsapp_template() 
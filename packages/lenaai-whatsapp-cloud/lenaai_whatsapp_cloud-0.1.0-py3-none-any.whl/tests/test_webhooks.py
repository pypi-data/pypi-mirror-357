#!/usr/bin/env python3
"""
Webhook Endpoint Testing Script
This script demonstrates why webhook endpoints appear to "do nothing"
"""

import requests
import json

def test_webhook_endpoints():
    base_url = "http://127.0.0.1:8008"
    
    print("🧪 Testing Webhook Endpoints")
    print("=" * 60)
    
    # Test 1: GET /webhook-twilio (should always work)
    print("\n1️⃣ Testing GET /webhook-twilio (should work):")
    try:
        response = requests.get(f"{base_url}/webhook-twilio")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: GET /webhook-whatsapp (will fail without proper tokens)
    print("\n2️⃣ Testing GET /webhook-whatsapp (will fail):")
    try:
        response = requests.get(f"{base_url}/webhook-whatsapp?hub.challenge=123456&hub.verify_token=test")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: GET /webhook-messenger (will fail without proper tokens)
    print("\n3️⃣ Testing GET /webhook-messenger (will fail):")
    try:
        response = requests.get(f"{base_url}/webhook-messenger?hub.challenge=123456&hub.verify_token=test")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: POST /webhook-twilio (will work with form data)
    print("\n4️⃣ Testing POST /webhook-twilio (should work):")
    try:
        form_data = {
            "AccountSid": "test_account",
            "From": "+1234567890",
            "To": "+0987654321",
            "Body": "Hello from test",
            "MessageSid": "test_message_123",
            "NumMedia": "0"
        }
        response = requests.post(f"{base_url}/webhook-twilio", data=form_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: POST /webhook-whatsapp (will fail without proper payload)
    print("\n5️⃣ Testing POST /webhook-whatsapp (will fail):")
    try:
        payload = {
            "entry": [{
                "id": "test_business_id",
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": "+1234567890",
                            "text": {"body": "Hello"}
                        }]
                    }
                }]
            }]
        }
        response = requests.post(f"{base_url}/webhook-whatsapp", json=payload)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 6: POST /webhook-messenger (will fail without proper payload)
    print("\n6️⃣ Testing POST /webhook-messenger (will fail):")
    try:
        payload = {
            "object": "page",
            "entry": [{
                "id": "test_page_id",
                "messaging": [{
                    "sender": {"id": "test_user_id"},
                    "message": {"text": "Hello"}
                }]
            }]
        }
        response = requests.post(f"{base_url}/webhook-messenger", json=payload)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("📋 Summary:")
    print("✅ GET /webhook-twilio - Always works (no verification needed)")
    print("❌ GET /webhook-whatsapp - Fails (needs proper verify_token)")
    print("❌ GET /webhook-messenger - Fails (needs proper verify_token)")
    print("✅ POST /webhook-twilio - Works (processes form data)")
    print("❌ POST /webhook-whatsapp - Fails (needs proper business_id)")
    print("❌ POST /webhook-messenger - Fails (needs proper page_id)")
    print("\n💡 These endpoints are designed for real platform webhooks, not manual testing!")

if __name__ == "__main__":
    test_webhook_endpoints() 
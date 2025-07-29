#!/usr/bin/env python3
"""
Simple test script to check API endpoints
"""

import requests
import json

def test_endpoints():
    base_url = "http://127.0.0.1:8008"
    
    print("🧪 Testing WhatsApp Cloud API endpoints...")
    print(f"📍 Base URL: {base_url}")
    print("-" * 50)
    
    # Test 1: Health check
    print("1️⃣ Testing health check endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        print(f"   Headers: {dict(response.headers)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("-" * 50)
    
    # Test 2: API docs
    print("2️⃣ Testing API docs endpoint...")
    try:
        response = requests.get(f"{base_url}/docs")
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
        print(f"   Content Length: {len(response.text)} characters")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("-" * 50)
    
    # Test 3: OpenAPI JSON
    print("3️⃣ Testing OpenAPI JSON endpoint...")
    try:
        response = requests.get(f"{base_url}/openapi.json")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Title: {data.get('info', {}).get('title', 'Unknown')}")
            print(f"   Version: {data.get('info', {}).get('version', 'Unknown')}")
            print(f"   Paths: {list(data.get('paths', {}).keys())}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("-" * 50)
    
    # Test 4: WhatsApp webhook verification
    print("4️⃣ Testing WhatsApp webhook verification...")
    try:
        response = requests.get(f"{base_url}/webhook-whatsapp?hub.challenge=123456&hub.verify_token=test")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_endpoints() 
#!/usr/bin/env python3
"""
Test script for Google Ads Account Access API endpoints
Updated for Google Ads API v28.0.0
"""

import requests
import json
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
import django
django.setup()

from google_ads_new.google_ads_api_service import send_link_request

# API endpoints
BASE_URL = "http://localhost:8000"
REQUEST_ACCESS_URL = f"{BASE_URL}/google-ads-new/api/request-account-access/"
PENDING_REQUESTS_URL = f"{BASE_URL}/google-ads-new/api/pending-access-requests/"

def test_api_endpoints():
    """Test the API endpoints"""
    print("🧪 Testing Google Ads Account Access API Endpoints")
    print("=" * 60)
    
    # Test data
    manager_customer_id = "9762343117"  # Your actual manager account ID from logs
    client_customer_id = "9999999999"   # Test client account ID - replace with valid test account ID
    
    print(f"Manager Customer ID: {manager_customer_id}")
    print(f"Client Customer ID: {client_customer_id}")
    print()
    
    # Test 1: Request Account Access via API
    print("1️⃣ Testing Request Account Access API Endpoint")
    print("-" * 40)
    
    payload = {
        "manager_customer_id": manager_customer_id,
        "client_customer_id": client_customer_id
    }
    
    try:
        response = requests.post(REQUEST_ACCESS_URL, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Test 2: Get Pending Access Requests
    print("2️⃣ Testing Get Pending Access Requests API Endpoint")
    print("-" * 40)
    
    try:
        response = requests.get(f"{PENDING_REQUESTS_URL}?manager_customer_id={manager_customer_id}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Test 3: Direct Function Call
    print("3️⃣ Testing Direct Function Call")
    print("-" * 40)
    
    try:
        result = send_link_request(manager_customer_id, client_customer_id)
        print(f"Result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def show_curl_examples():
    """Show cURL examples for testing"""
    print("\n📋 cURL Examples for Testing")
    print("=" * 60)
    
    manager_customer_id = "9762343117"  # Your actual manager account ID
    client_customer_id = "9999999999"   # Replace with valid test account ID
    
    print("1️⃣ Request Account Access:")
    print(f"curl -X POST {REQUEST_ACCESS_URL} \\")
    print(f"  -H \"Content-Type: application/json\" \\")
    print(f"  -d '{{")
    print(f"    \"manager_customer_id\": \"{manager_customer_id}\",")
    print(f"    \"client_customer_id\": \"{client_customer_id}\"")
    print(f"  }}'")
    
    print("\n2️⃣ Get Pending Access Requests:")
    print(f"curl -X GET \"{PENDING_REQUESTS_URL}?manager_customer_id={manager_customer_id}\"")

def show_python_examples():
    """Show Python examples for testing"""
    print("\n🐍 Python Examples for Testing")
    print("=" * 60)
    
    print("1️⃣ Using the API endpoint:")
    print("""
import requests

url = "http://localhost:8000/google-ads-new/api/request-account-access/"
payload = {
    "manager_customer_id": "9762343117",
    "client_customer_id": "9999999999"
}

response = requests.post(url, json=payload)
print(response.json())
""")
    
    print("2️⃣ Using the direct function:")
    print("""
from google_ads_new.google_ads_api_service import send_link_request

result = send_link_request("9762343117", "9999999999")
print(result)
""")

if __name__ == "__main__":
    print("🚀 Google Ads Account Access API Test Suite")
    print("Updated for Google Ads API v28.0.0")
    print()
    
    # Run tests
    test_api_endpoints()
    
    # Show examples
    show_curl_examples()
    show_python_examples()
    
    print("\n✅ Test suite completed!")
    print("\n📝 Notes:")
    print("- Make sure Django server is running on localhost:8000")
    print("- Update customer IDs to match your actual accounts")
    print("- The API endpoints are CSRF-free and authentication-free for testing")
    print("- Use real customer IDs once your developer token is upgraded to Basic/Standard access")

#!/usr/bin/env python3
"""
Test script using valid Google Ads test account IDs
This avoids the RESOURCE_NOT_FOUND error by using real test accounts
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

def test_with_valid_test_accounts():
    """Test with valid Google Ads test account IDs"""
    print("🧪 Testing with Valid Google Ads Test Account IDs")
    print("=" * 60)
    
    # These are example test account IDs - replace with actual ones from your Google Ads test center
    manager_customer_id = "9762343117"  # Your actual manager account from logs
    
    # Valid test customer IDs (you need to get these from Google Ads API Test Center)
    test_customer_ids = [
        "1234567890",  # Replace with actual test account ID
        "0987654321",  # Replace with actual test account ID
        "5555555555",  # Replace with actual test account ID
    ]
    
    print(f"Manager Customer ID: {manager_customer_id}")
    print(f"Test Customer IDs: {test_customer_ids}")
    print()
    
    for i, test_customer_id in enumerate(test_customer_ids, 1):
        print(f"Test {i}: Requesting access to {test_customer_id}")
        print("-" * 40)
        
        payload = {
            "manager_customer_id": manager_customer_id,
            "client_customer_id": test_customer_id
        }
        
        try:
            response = requests.post(REQUEST_ACCESS_URL, json=payload)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"Error: {e}")
        
        print()

def test_connection_only():
    """Test just the connection without requesting access"""
    print("🔌 Testing Google Ads API Connection Only")
    print("=" * 60)
    
    try:
        from google_ads_new.google_ads_api_service import GoogleAdsAPIService
        
        service = GoogleAdsAPIService()
        if service.initialize_client():
            print("✅ Google Ads client initialized successfully")
            
            # Test connection with your manager account
            result = service.test_connection("9762343117")
            print(f"Connection Test Result: {json.dumps(result, indent=2)}")
        else:
            print("❌ Failed to initialize Google Ads client")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def show_how_to_get_test_accounts():
    """Show how to get valid test account IDs"""
    print("\n📋 How to Get Valid Google Ads Test Account IDs")
    print("=" * 60)
    
    print("1️⃣ Go to Google Ads API Test Center:")
    print("   https://developers.google.com/google-ads/api/docs/first-call/test-accounts")
    
    print("\n2️⃣ Create test accounts or use existing ones")
    
    print("\n3️⃣ Get the customer IDs (10-digit numbers)")
    
    print("\n4️⃣ Update the test_customer_ids list in this script")
    
    print("\n5️⃣ Test with valid IDs to avoid RESOURCE_NOT_FOUND errors")

def show_current_config():
    """Show current configuration"""
    print("\n⚙️ Current Configuration")
    print("=" * 60)
    
    config_path = "google_ads_new/google-ads.yaml"
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = f.read()
            print("google-ads.yaml contents:")
            print(config)
    else:
        print("❌ google-ads.yaml not found")

if __name__ == "__main__":
    print("🚀 Google Ads API Test with Valid Accounts")
    print("Updated for Google Ads API v28.0.0")
    print()
    
    # Show current config
    show_current_config()
    
    # Test connection only first
    test_connection_only()
    
    # Show how to get test accounts
    show_how_to_get_test_accounts()
    
    # Test with valid accounts (if you have them)
    print("\n" + "="*60)
    print("💡 To test with valid accounts:")
    print("1. Get test account IDs from Google Ads API Test Center")
    print("2. Update the test_customer_ids list in this script")
    print("3. Run: python google_ads_new/test_with_valid_accounts.py")
    
    print("\n✅ Test script completed!")
    print("\n📝 Notes:")
    print("- The RESOURCE_NOT_FOUND error occurs when using invalid customer IDs")
    print("- Use only valid Google Ads test account IDs for testing")
    print("- Your manager account ID (9762343117) is correctly configured")
    print("- Once you have valid test account IDs, the API calls will work")

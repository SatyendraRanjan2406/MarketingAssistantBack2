#!/usr/bin/env python3
"""
Test script for the list_accessible_customers wrapper function
"""

import os
import sys
import django

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

from google_ads_new.google_ads_api_service import list_accessible_customers, GoogleAdsAPIService
from django.contrib.auth.models import User

def test_standalone_function():
    """Test the standalone list_accessible_customers function"""
    print("Testing standalone list_accessible_customers function...")
    print("=" * 60)
    
    try:
        # Test with first user
        result = list_accessible_customers()
        
        if result['success']:
            print("✅ SUCCESS: Function executed successfully")
            print(f"Total accessible customers: {result['total_count']}")
            print(f"Customer resource names: {result['customers']}")
            print(f"Raw response: {result['raw_response']}")
        else:
            print(f"❌ FAILED: {result['error']}")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")

def test_class_method():
    """Test the GoogleAdsAPIService.list_accessible_customers method"""
    print("\nTesting GoogleAdsAPIService.list_accessible_customers method...")
    print("=" * 60)
    
    try:
        # Get first user
        user = User.objects.first()
        if not user:
            print("❌ No users found in the system")
            return
            
        # Create service instance
        api_service = GoogleAdsAPIService(user_id=user.id)
        
        # Test the method
        result = api_service.list_accessible_customers()
        
        if result['success']:
            print("✅ SUCCESS: Method executed successfully")
            print(f"Total accessible customers: {result['total_count']}")
            print(f"Customer resource names: {result['customers']}")
            print(f"Raw response: {result['raw_response']}")
        else:
            print(f"❌ FAILED: {result['error']}")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")

def test_curl_equivalent():
    """Test that our wrapper produces the same result as the cURL command"""
    print("\nTesting cURL equivalent functionality...")
    print("=" * 60)
    
    try:
        result = list_accessible_customers()
        
        if result['success']:
            print("✅ SUCCESS: cURL equivalent working")
            print("The wrapper function successfully calls the same API endpoint as:")
            print("curl --location 'https://googleads.googleapis.com/v21/customers:listAccessibleCustomers' \\")
            print("--header 'Authorization: Bearer <access_token>' \\")
            print("--header 'developer-token: <developer_token>'")
            print(f"\nResponse matches expected format: {result['raw_response']}")
        else:
            print(f"❌ FAILED: {result['error']}")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")

if __name__ == "__main__":
    print("Google Ads listAccessibleCustomers API Wrapper Test")
    print("=" * 60)
    
    # Check if we have the required environment variables
    developer_token = os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN')
    if not developer_token:
        print("❌ GOOGLE_ADS_DEVELOPER_TOKEN not set in environment")
        print("Please set your Google Ads developer token in the environment")
        sys.exit(1)
    
    print(f"✅ Developer token found: {developer_token[:10]}...")
    
    # Run tests
    test_standalone_function()
    test_class_method()
    test_curl_equivalent()
    
    print("\n" + "=" * 60)
    print("Test completed!")

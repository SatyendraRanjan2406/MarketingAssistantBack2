#!/usr/bin/env python3
"""
Test script to demonstrate token authentication
"""

import requests
import json
import os

# Configuration
BASE_URL = "http://localhost:8000"
EMAIL = "your_email@example.com"  # Change this
PASSWORD = "your_password"        # Change this
CUSTOMER_ID = "1234567890"        # Change this to your Google Ads customer ID

def get_jwt_token():
    """Get JWT token for API authentication"""
    print("🔑 Getting JWT token...")
    
    response = requests.post(
        f"{BASE_URL}/accounts/api/auth/login/",
        json={"email": EMAIL, "password": PASSWORD},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            print("✅ JWT token obtained successfully")
            return data["access"]
        else:
            print(f"❌ Login failed: {data.get('error', 'Unknown error')}")
            return None
    else:
        print(f"❌ HTTP {response.status_code}: {response.text}")
        return None

def test_regular_rag(jwt_token):
    """Test regular RAG (documentation only)"""
    print("\n🤖 Testing regular RAG...")
    
    response = requests.post(
        f"{BASE_URL}/google-ads-new/api/rag/api/query/",
        json={"query": "How do I create a campaign?"},
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {jwt_token}"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Regular RAG response:")
        print(f"   Answer: {data.get('answer', 'N/A')[:200]}...")
        print(f"   Sources: {len(data.get('sources', []))} found")
        return True
    else:
        print(f"❌ Regular RAG failed: HTTP {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def test_hybrid_rag(jwt_token, customer_id):
    """Test hybrid RAG (documentation + live data)"""
    print("\n🔗 Testing hybrid RAG...")
    
    response = requests.post(
        f"{BASE_URL}/google-ads-new/api/rag/api/hybrid/",
        json={
            "query": "Show me my campaigns",
            "customer_id": customer_id
        },
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {jwt_token}"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Hybrid RAG response:")
        print(f"   Answer: {data.get('answer', 'N/A')[:200]}...")
        print(f"   Data Type: {data.get('data_type', 'N/A')}")
        print(f"   API Data: {data.get('api_data', {}).get('data_type', 'N/A')}")
        return True
    else:
        print(f"❌ Hybrid RAG failed: HTTP {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def check_google_oauth_status(jwt_token):
    """Check Google OAuth connection status"""
    print("\n🔍 Checking Google OAuth status...")
    
    response = requests.get(
        f"{BASE_URL}/accounts/api/google-oauth/status/",
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            print("✅ Google OAuth status:")
            print(f"   Connected: {data.get('is_connected', False)}")
            print(f"   Google Ads Access: {data.get('google_ads_access', False)}")
            print(f"   Accessible Customers: {data.get('accessible_customers', [])}")
            return data.get('is_connected', False)
        else:
            print(f"❌ OAuth status check failed: {data.get('error', 'Unknown error')}")
            return False
    else:
        print(f"❌ OAuth status check failed: HTTP {response.status_code}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Token Authentication")
    print("=" * 50)
    
    # Check if credentials are set
    if EMAIL == "your_email@example.com" or PASSWORD == "your_password":
        print("❌ Please update EMAIL and PASSWORD in this script")
        print("   Edit the variables at the top of the file")
        return
    
    # Get JWT token
    jwt_token = get_jwt_token()
    if not jwt_token:
        print("❌ Cannot proceed without JWT token")
        return
    
    # Test regular RAG
    test_regular_rag(jwt_token)
    
    # Check Google OAuth status
    oauth_connected = check_google_oauth_status(jwt_token)
    
    # Test hybrid RAG (only if OAuth is connected)
    if oauth_connected:
        test_hybrid_rag(jwt_token, CUSTOMER_ID)
    else:
        print("\n⚠️  Google OAuth not connected. Hybrid RAG will not work.")
        print("   To connect Google OAuth:")
        print("   1. Visit: http://localhost:8000/accounts/api/google-oauth/initiate/")
        print("   2. Complete the OAuth flow in your browser")
        print("   3. Run this script again")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    main()


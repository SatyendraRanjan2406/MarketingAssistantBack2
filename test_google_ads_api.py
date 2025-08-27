#!/usr/bin/env python
"""
Test script to directly call Google Ads API and debug the issue
"""
import os
import sys
import django
import requests
import json

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

from django.contrib.auth.models import User
from google_ads_new.models import GoogleAdsAccount

def test_google_ads_api():
    """Test Google Ads API directly"""
    
    # Get user and accounts
    user = User.objects.get(id=2)  # Your user ID
    user_auth = user.google_auth_set.first()
    
    if not user_auth:
        print("❌ No Google OAuth found for user")
        return
    
    print(f"✅ Found Google OAuth for user: {user_auth.google_email}")
    print(f"📧 Google Email: {user_auth.google_email}")
    print(f"🔑 Access Token: {user_auth.access_token[:50]}...")
    print(f"⏰ Token Expiry: {user_auth.token_expiry}")
    print(f"🔧 Scopes: {user_auth.scopes}")
    
    # Check if token is expired
    from django.utils import timezone
    if user_auth.token_expiry <= timezone.now():
        print("❌ Access token is EXPIRED!")
        return
    else:
        print("✅ Access token is still valid")
    
    # Get developer token
    developer_token = os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN')
    if not developer_token:
        print("❌ No GOOGLE_ADS_DEVELOPER_TOKEN found in environment")
        return
    else:
        print(f"✅ Developer token found: {developer_token[:10]}...")
    
    # Get Google Ads accounts
    accounts = GoogleAdsAccount.objects.filter(user=user, is_active=True)
    print(f"📊 Found {accounts.count()} Google Ads accounts")
    
    for account in accounts:
        print(f"  - Account: {account.account_name} ({account.customer_id})")
        print(f"    Manager: {account.is_manager}")
        print(f"    Test: {account.is_test_account}")
        
        # Test API call for this account
        test_account_api(account, user_auth.access_token, developer_token)

def test_account_api(account, access_token, developer_token):
    """Test API call for specific account"""
    print(f"\n🔬 Testing API for account: {account.customer_id}")
    
    # Simple GAQL query
    gaql = """
    SELECT 
        campaign.id, 
        campaign.name, 
        campaign.status
    FROM campaign 
    LIMIT 5
    """
    
    url = f"https://googleads.googleapis.com/v21/customers/{account.customer_id}/googleAds:search"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "developer-token": developer_token,
        "Content-Type": "application/json"
    }
    
    print(f"🌐 API URL: {url}")
    print(f"📋 GAQL Query: {gaql.strip()}")
    
    try:
        response = requests.post(url, headers=headers, json={"query": gaql})
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Success!")
            print(f"📋 Response: {json.dumps(data, indent=2)}")
            
            if "results" in data and data["results"]:
                print(f"🎉 Found {len(data['results'])} campaigns!")
                for i, result in enumerate(data["results"]):
                    campaign = result.get("campaign", {})
                    print(f"  {i+1}. {campaign.get('name')} ({campaign.get('id')}) - {campaign.get('status')}")
            else:
                print("⚠️  API returned success but no campaign results")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"📄 Error Response: {response.text}")
            
    except Exception as e:
        print(f"💥 Exception: {str(e)}")

if __name__ == "__main__":
    test_google_ads_api()


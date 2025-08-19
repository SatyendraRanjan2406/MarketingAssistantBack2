#!/usr/bin/env python3
"""
Check Google Ads API Status
This script verifies if Google Ads API is properly enabled and accessible.
"""

import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import GoogleAuthError

def check_google_ads_api():
    """Check Google Ads API status"""
    
    print("🔍 Checking Google Ads API Status")
    print("=" * 50)
    
    # Check environment variables
    print("\n📋 Environment Variables Check:")
    required_vars = [
        'GOOGLE_ADS_CLIENT_ID',
        'GOOGLE_ADS_CLIENT_SECRET', 
        'GOOGLE_ADS_REFRESH_TOKEN',
        'GOOGLE_ADS_DEVELOPER_TOKEN',
        'GOOGLE_ADS_CUSTOMER_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value and value != 'your_refresh_token':
            print(f"✅ {var}: {value[:20]}...")
        else:
            print(f"❌ {var}: Not set or placeholder")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing or incomplete variables: {', '.join(missing_vars)}")
        print("Please complete your .env file configuration.")
        return False
    
    print("\n✅ All required environment variables are set!")
    
    # Check if we can create credentials
    print("\n🔐 Testing Credentials Creation:")
    try:
        creds = Credentials(
            token=None,
            refresh_token=os.getenv('GOOGLE_ADS_REFRESH_TOKEN'),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv('GOOGLE_ADS_CLIENT_ID'),
            client_secret=os.getenv('GOOGLE_ADS_CLIENT_SECRET'),
            scopes=[
                'https://www.googleapis.com/auth/adwords',
                'https://www.googleapis.com/auth/userinfo.email'
            ]
        )
        
        print("✅ Credentials object created successfully")
        
        # Try to refresh the token
        print("\n🔄 Testing Token Refresh:")
        creds.refresh(Request())
        print("✅ Token refresh successful!")
        print(f"🔑 Access Token: {creds.token[:20]}...")
        
        return True
        
    except GoogleAuthError as e:
        print(f"❌ Google Auth Error: {e}")
        print("\n🔧 This usually means:")
        print("1. Google Ads API is not enabled")
        print("2. OAuth consent screen is not configured")
        print("3. Credentials are invalid")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    success = check_google_ads_api()
    
    if success:
        print("\n🎉 Google Ads API is properly configured!")
        print("You can now use the chat feature with real Google Ads data.")
    else:
        print("\n🔧 Please fix the issues above before proceeding.")
        print("1. Enable Google Ads API in Google Cloud Console")
        print("2. Complete OAuth consent screen setup")
        print("3. Generate a valid refresh token")

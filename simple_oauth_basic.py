#!/usr/bin/env python3
"""
Basic Google OAuth Script - No Offline Access
This script tests basic OAuth without requesting offline access.
"""

import os
import json
import webbrowser
import urllib.parse
from google_auth_oauthlib.flow import InstalledAppFlow

# OAuth 2.0 scopes
SCOPES = [
    'https://www.googleapis.com/auth/adwords',
    'openid',
    'https://www.googleapis.com/auth/userinfo.email'
]

def main():
    print("🔑 Basic Google OAuth - Test Basic Access")
    print("=" * 50)
    
    # Check credentials file
    creds_file = 'google_ads_credentials.json'
    if not os.path.exists(creds_file):
        print(f"❌ {creds_file} not found!")
        return
    
    try:
        # Load client config
        with open(creds_file, 'r') as f:
            client_config = json.load(f)
        
        print("✅ Credentials loaded")
        
        # Create flow with basic parameters (no offline access)
        flow = InstalledAppFlow.from_client_config(
            client_config,
            SCOPES,
            redirect_uri='http://localhost:8000/'
        )
        
        # Get authorization URL with basic parameters
        auth_url, _ = flow.authorization_url()
        
        print(f"\n🌐 Basic Authorization URL Generated!")
        print(f"📱 Opening browser...")
        
        # Open browser
        webbrowser.open(auth_url)
        
        print(f"\n📝 INSTRUCTIONS:")
        print(f"1. Complete the authorization in your browser")
        print(f"2. You'll be redirected to localhost:8000")
        print(f"3. Copy the 'code' parameter from the URL")
        print(f"4. Paste it here")
        
        # Get authorization code from user
        print(f"\n📝 Paste the authorization code here:")
        auth_code = input("Authorization code: ").strip()
        
        if not auth_code:
            print("❌ No authorization code provided")
            return
        
        # Decode URL-encoded authorization code
        try:
            auth_code = urllib.parse.unquote(auth_code)
            print(f"🔍 Decoded authorization code: {auth_code[:20]}...")
        except Exception as e:
            print(f"⚠️  Could not decode authorization code: {e}")
        
        print(f"\n🔄 Exchanging code for tokens...")
        
        # Exchange code for tokens
        try:
            flow.fetch_token(code=auth_code)
        except Exception as e:
            print(f"❌ Error exchanging code for tokens: {e}")
            return
        
        # Get credentials
        credentials = flow.credentials
        
        print(f"\n✅ Token Exchange Complete!")
        print(f"🔑 Refresh Token: {credentials.refresh_token}")
        print(f"📧 Access Token: {credentials.token[:20]}..." if credentials.token else "None")
        
        if credentials.refresh_token:
            print("✅ Success! Got a refresh token")
        else:
            print("⚠️  No refresh token (this is normal for basic OAuth)")
            print("💡 To get a refresh token, we need to fix the OAuth configuration")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"💡 This suggests a configuration issue in Google Cloud Console")

if __name__ == "__main__":
    main()

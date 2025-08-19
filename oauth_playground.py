#!/usr/bin/env python3
"""
Google OAuth Playground Style Script
This script tries to get a refresh token using a different OAuth approach.
"""

import os
import json
import webbrowser
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

# OAuth 2.0 scopes
SCOPES = [
    'https://www.googleapis.com/auth/adwords',
    'https://www.googleapis.com/auth/userinfo.email'
]

def main():
    print("🔑 Google OAuth Playground Style")
    print("=" * 40)
    
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
        
        # Create flow with specific parameters
        flow = Flow.from_client_config(
            client_config,
            SCOPES,
            redirect_uri='http://localhost:8080/'
        )
        
        # Set OAuth parameters
        flow.oauth2session.access_type = 'offline'
        flow.oauth2session.prompt = 'consent'
        
        print("\n🌐 Starting OAuth flow...")
        print("⚠️  IMPORTANT: Check 'Keep me signed in' if prompted!")
        print("⚠️  If you see 'This app isn't verified', click 'Advanced' then 'Go to [App Name]'")
        
        # Get authorization URL
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            prompt='consent'
        )
        
        print(f"\n🔗 Authorization URL:")
        print(auth_url)
        print(f"\n📱 Opening browser...")
        
        # Open browser
        webbrowser.open(auth_url)
        
        # Get authorization code from user
        print(f"\n📝 After authorization, you'll be redirected to localhost:8080")
        print(f"📝 Copy the 'code' parameter from the URL and paste it here:")
        
        auth_code = input("Enter authorization code: ").strip()
        
        if not auth_code:
            print("❌ No authorization code provided")
            return
        
        # Exchange code for tokens
        flow.fetch_token(code=auth_code)
        
        # Get credentials
        credentials = flow.credentials
        
        print(f"\n✅ Success!")
        print(f"🔑 Refresh Token: {credentials.refresh_token}")
        print(f"📧 Email: {getattr(credentials, 'id_token', 'N/A')}")
        
        if credentials.refresh_token:
            # Save to .env
            update_env(credentials.refresh_token)
            print("✅ Updated .env file")
        else:
            print("❌ No refresh token received!")
            print("💡 This usually means Google didn't provide one")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def update_env(refresh_token):
    """Update .env file with refresh token"""
    env_file = '.env'
    
    if not os.path.exists(env_file):
        with open(env_file, 'w') as f:
            f.write(f'GOOGLE_ADS_REFRESH_TOKEN={refresh_token}\n')
        return
    
    # Read and update existing .env
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Find and update GOOGLE_ADS_REFRESH_TOKEN
    updated = False
    for i, line in enumerate(lines):
        if line.startswith('GOOGLE_ADS_REFRESH_TOKEN='):
            lines[i] = f'GOOGLE_ADS_REFRESH_TOKEN={refresh_token}\n'
            updated = True
            break
    
    if not updated:
        lines.append(f'GOOGLE_ADS_REFRESH_TOKEN={refresh_token}\n')
    
    with open(env_file, 'w') as f:
        f.writelines(lines)

if __name__ == "__main__":
    main()

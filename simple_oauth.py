#!/usr/bin/env python3
"""
Simple Google Ads OAuth Script
This script focuses on getting a refresh token using a different approach.
"""

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

# OAuth 2.0 scopes
SCOPES = [
    'https://www.googleapis.com/auth/adwords',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid'  # Google automatically adds this
]

def main():
    print("🔑 Simple Google Ads OAuth")
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
        
        # Create flow with explicit offline access
        flow = InstalledAppFlow.from_client_config(
            client_config,
            SCOPES,
            redirect_uri='http://localhost:8000/'
        )
        
        # Force offline access
        flow.oauth2session.access_type = 'offline'
        flow.oauth2session.prompt = 'consent'
        
        print("\n🌐 Starting OAuth flow...")
        print("⚠️  IMPORTANT: Check 'Keep me signed in' if prompted!")
        print("⚠️  If you see 'This app isn't verified', click 'Advanced' then 'Go to [App Name]'")
        
        # Run the flow
        credentials = flow.run_local_server(port=8000)
        
        print(f"\n✅ Success!")
        print(f"🔑 Refresh Token: {credentials.refresh_token}")
        print(f"📧 Email: {getattr(credentials, 'id_token', 'N/A')}")
        
        if credentials.refresh_token:
            # Save to .env
            update_env(credentials.refresh_token)
            print("✅ Updated .env file")
        else:
            print("❌ No refresh token received!")
            print("💡 Try revoking access in Google Cloud Console and run again")
            
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

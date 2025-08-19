#!/usr/bin/env python3
"""
Get Google Ads Refresh Token
This script specifically requests offline access to get a refresh token.
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
    print("🔑 Get Google Ads Refresh Token (Offline Access)")
    print("=" * 55)
    
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
        
        # Create flow with offline access
        flow = InstalledAppFlow.from_client_config(
            client_config,
            SCOPES,
            redirect_uri='http://localhost:8000/'
        )
        
        # Force offline access
        flow.oauth2session.access_type = 'offline'
        flow.oauth2session.prompt = 'consent'
        
        # Get authorization URL with offline access
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            prompt='consent'
        )
        
        print(f"\n🌐 Authorization URL Generated (Offline Access)!")
        print(f"📱 Opening browser...")
        print(f"⚠️  IMPORTANT: Check 'Keep me signed in' if prompted!")
        
        # Open browser
        webbrowser.open(auth_url)
        
        print(f"\n📝 INSTRUCTIONS:")
        print(f"1. Complete the authorization in your browser")
        print(f"2. Make sure to check 'Keep me signed in' if prompted")
        print(f"3. You'll be redirected to localhost:8000")
        print(f"4. Copy the 'code' parameter from the URL")
        print(f"5. Paste it here")
        
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
        
        print(f"\n🔄 Exchanging code for tokens (offline access)...")
        
        # Exchange code for tokens
        flow.fetch_token(code=auth_code)
        
        # Get credentials
        credentials = flow.credentials
        
        print(f"\n✅ Token Exchange Complete!")
        print(f"🔑 Refresh Token: {credentials.refresh_token}")
        print(f"📧 Access Token: {credentials.token[:20]}..." if credentials.token else "None")
        
        if credentials.refresh_token:
            print("🎉 SUCCESS! Got a refresh token!")
            
            # Save to .env file
            update_env(credentials.refresh_token)
            print("✅ Updated .env file with refresh token")
            
            # Save full credentials
            save_credentials(credentials)
            print("✅ Saved full credentials to google_ads_token.json")
            
        else:
            print("❌ Still no refresh token received!")
            print("💡 This suggests the OAuth consent screen needs offline access configuration")
            
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

def save_credentials(credentials):
    """Save full credentials to file"""
    creds_data = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    
    with open('google_ads_token.json', 'w') as f:
        json.dump(creds_data, f, indent=2)

if __name__ == "__main__":
    main()

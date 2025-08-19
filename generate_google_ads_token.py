#!/usr/bin/env python3
"""
Google Ads OAuth Token Generator
This script helps generate a refresh token for Google Ads API access.
"""

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# OAuth 2.0 scopes
SCOPES = [
    'https://www.googleapis.com/auth/adwords',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid'  # Google automatically adds this scope
]

def revoke_existing_tokens():
    """Revoke existing tokens to force new authorization"""
    token_file = 'google_ads_token.json'
    if os.path.exists(token_file):
        try:
            with open(token_file, 'r') as f:
                creds_data = json.load(f)
            
            if creds_data.get('token'):
                print("🔄 Revoking existing tokens...")
                try:
                    creds = Credentials(
                        token=creds_data['token'],
                        refresh_token=creds_data.get('refresh_token'),
                        token_uri=creds_data['token_uri'],
                        client_id=creds_data['client_id'],
                        client_secret=creds_data['client_secret'],
                        scopes=creds_data['scopes']
                    )
                    
                    # Revoke the token
                    creds.revoke(Request())
                    print("✅ Existing tokens revoked successfully")
                except Exception as e:
                    print(f"⚠️  Could not revoke tokens: {e}")
                    
                # Remove the token file
                os.remove(token_file)
                print("🗑️  Removed old token file")
        except Exception as e:
            print(f"⚠️  Error handling existing tokens: {e}")

def generate_refresh_token():
    """Generate a refresh token for Google Ads API access"""
    
    print("🔑 Google Ads OAuth Token Generator")
    print("=" * 50)
    
    # Revoke existing tokens to force new authorization
    revoke_existing_tokens()
    
    # Check if credentials file exists
    credentials_file = 'google_ads_credentials.json'
    if not os.path.exists(credentials_file):
        print(f"❌ Credentials file '{credentials_file}' not found!")
        print("\n🔧 Please download your OAuth 2.0 credentials from Google Cloud Console:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Select your project")
        print("3. Go to APIs & Services > Credentials")
        print("4. Click 'Create Credentials' > 'OAuth 2.0 Client IDs'")
        print("5. Choose 'Desktop application'")
        print("6. Download the JSON file and rename it to 'google_ads_credentials.json'")
        print("7. Place it in the same directory as this script")
        return
    
    try:
        # Load client configuration
        with open(credentials_file, 'r') as f:
            client_config = json.load(f)
        
        print("✅ Credentials file loaded successfully")
        
        # Use a fixed port for easier setup
        port = 8080
        redirect_uri = f'http://localhost:{port}/'
        
        # Create OAuth flow
        flow = InstalledAppFlow.from_client_config(
            client_config,
            SCOPES,
            redirect_uri=redirect_uri
        )
        
        # Force refresh token generation with multiple approaches
        flow.oauth2session.access_type = 'offline'
        flow.oauth2session.prompt = 'consent'
        
        # Try to force approval prompt for older versions
        if hasattr(flow.oauth2session, 'approval_prompt'):
            flow.oauth2session.approval_prompt = 'force'
        
        print(f"\n🌐 Starting OAuth flow on port {port}...")
        print("This will open your browser for authentication.")
        print(f"After authentication, you'll be redirected to {redirect_uri}")
        print("⚠️  IMPORTANT: Make sure to check 'Keep me signed in' if prompted!")
        print("⚠️  IMPORTANT: If you see 'This app isn't verified', click 'Advanced' then 'Go to [App Name]'")
        print(f"📝 Make sure you've added {redirect_uri} to your Google Cloud Console OAuth redirect URIs")
        
        # Run the OAuth flow
        credentials = flow.run_local_server(port=port)
        
        print("\n✅ Authentication successful!")
        print(f"🔑 Refresh Token: {credentials.refresh_token}")
        
        # Try to get email from different possible locations
        email = "N/A"
        if hasattr(credentials, 'id_token'):
            try:
                import jwt
                decoded = jwt.decode(credentials.id_token, options={"verify_signature": False})
                email = decoded.get('email', 'N/A')
            except:
                pass
        
        print(f"📧 Email: {email}")
        print(f"🔐 Scopes: {', '.join(credentials.scopes)}")
        
        # Save credentials to file for future use
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
        
        print(f"\n💾 Credentials saved to 'google_ads_token.json'")
        
        # Update .env file
        update_env_file(credentials.refresh_token)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure you have valid OAuth credentials")
        print("2. Check that Google Ads API is enabled")
        print("3. Verify your redirect URI is configured in Google Cloud Console")
        print("4. Make sure you're using the correct credentials file")

def update_env_file(refresh_token):
    """Update the .env file with the new refresh token"""
    
    env_file = '.env'
    if not os.path.exists(env_file):
        print(f"⚠️  .env file not found. Please create it manually with:")
        print(f"GOOGLE_ADS_REFRESH_TOKEN={refresh_token}")
        return
    
    try:
        # Read current .env file
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Check if GOOGLE_ADS_REFRESH_TOKEN already exists
        if 'GOOGLE_ADS_REFRESH_TOKEN=' in content:
            # Update existing token
            lines = content.split('\n')
            updated_lines = []
            for line in lines:
                if line.startswith('GOOGLE_ADS_REFRESH_TOKEN='):
                    updated_lines.append(f'GOOGLE_ADS_REFRESH_TOKEN={refresh_token}')
                else:
                    updated_lines.append(line)
            
            # Write updated content
            with open(env_file, 'w') as f:
                f.write('\n'.join(updated_lines))
            
            print(f"✅ Updated .env file with new refresh token")
        else:
            # Add new token
            with open(env_file, 'a') as f:
                f.write(f'\nGOOGLE_ADS_REFRESH_TOKEN={refresh_token}\n')
            
            print(f"✅ Added refresh token to .env file")
            
    except Exception as e:
        print(f"⚠️  Could not update .env file: {e}")
        print(f"Please manually add: GOOGLE_ADS_REFRESH_TOKEN={refresh_token}")

if __name__ == "__main__":
    generate_refresh_token()

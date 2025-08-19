#!/usr/bin/env python3
"""
Setup script for environment variables
Run this script to help configure your .env file
"""

import os
import getpass

def setup_environment():
    """Interactive setup for environment variables"""
    print("🔧 Setting up environment variables for Marketing Assistant")
    print("=" * 60)
    
    # Check if .env file exists
    env_file = '.env'
    if os.path.exists(env_file):
        print(f"✅ Found existing {env_file} file")
        overwrite = input("Do you want to overwrite it? (y/N): ").lower()
        if overwrite != 'y':
            print("Setup cancelled. Your existing .env file remains unchanged.")
            return
    else:
        print(f"📝 Creating new {env_file} file")
    
    # OpenAI API Key
    print("\n🔑 OpenAI API Key Setup")
    print("-" * 30)
    print("You need an OpenAI API key to use the AI chat features.")
    print("Get one from: https://platform.openai.com/api-keys")
    print()
    
    openai_key = getpass.getpass("Enter your OpenAI API key (or press Enter to skip): ")
    
    # Google Ads API (optional)
    print("\n📊 Google Ads API Setup (Optional)")
    print("-" * 35)
    print("Skip this section if you don't need Google Ads integration yet.")
    print()
    
    google_ads_client_id = input("Google Ads Client ID (optional): ").strip()
    google_ads_client_secret = getpass.getpass("Google Ads Client Secret (optional): ").strip()
    google_ads_developer_token = input("Google Ads Developer Token (optional): ").strip()
    google_ads_refresh_token = input("Google Ads Refresh Token (optional): ").strip()
    
    # Write to .env file
    env_content = f"""# OpenAI API Configuration
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY={openai_key if openai_key else 'your_openai_api_key_here'}

# Google Ads API Configuration (optional)
GOOGLE_ADS_CLIENT_ID={google_ads_client_id if google_ads_client_id else 'your_google_ads_client_id'}
GOOGLE_ADS_CLIENT_SECRET={google_ads_client_secret if google_ads_client_secret else 'your_google_ads_client_secret'}
GOOGLE_ADS_DEVELOPER_TOKEN={google_ads_developer_token if google_ads_developer_token else 'your_developer_token'}
GOOGLE_ADS_REFRESH_TOKEN={google_ads_refresh_token if google_ads_refresh_token else 'your_refresh_token'}

# Django Configuration
DEBUG=True
SECRET_KEY=your_django_secret_key_here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DATABASE_URL=sqlite:///db.sqlite3
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print(f"\n✅ Successfully created/updated {env_file}")
        
        if openai_key:
            print("🔑 OpenAI API key configured successfully!")
            print("💡 You can now use the AI chat features.")
        else:
            print("⚠️  No OpenAI API key provided.")
            print("💡 AI chat features will be disabled until you add a valid API key.")
        
        if any([google_ads_client_id, google_ads_client_secret, google_ads_developer_token, google_ads_refresh_token]):
            print("📊 Google Ads API configuration started.")
            print("💡 Complete the configuration to enable Google Ads features.")
        else:
            print("📊 Google Ads API configuration skipped.")
        
        print(f"\n📁 Your {env_file} file is ready!")
        print("🚀 Restart your Django server to load the new environment variables.")
        
    except Exception as e:
        print(f"❌ Error creating {env_file}: {e}")
        print("Please create the file manually using the template in env_template.txt")

if __name__ == "__main__":
    setup_environment()

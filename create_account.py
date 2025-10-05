#!/usr/bin/env python3
"""
Create Google Ads Account
This script helps you create your first Google Ads account in the Django database.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

from google_ads_app.models import GoogleAdsAccount
from django.contrib.auth.models import User

def create_google_ads_account():
    """Create a Google Ads account for the user"""
    
    print("🔑 Create Google Ads Account")
    print("=" * 40)
    
    # Get the first user (or create one if none exists)
    try:
        user = User.objects.first()
        if not user:
            print("❌ No users found in database")
            print("💡 Please create a user first or run migrations")
            return
        
        print(f"✅ Found user: {user.username} (ID: {user.id})")
        
        # Check if account already exists
        existing_accounts = GoogleAdsAccount.objects.filter(user=user)
        if existing_accounts.exists():
            print(f"📋 Found {existing_accounts.count()} existing account(s):")
            for acc in existing_accounts:
                print(f"   - {acc.customer_id} ({acc.account_name})")
            return
        
        # Get account details from environment
        customer_id = os.getenv('GOOGLE_ADS_CUSTOMER_ID')
        # login_customer_id = os.getenv('GOOGLE_ADS_LOGIN_CUSTOMER_ID')
        
        if not customer_id:
            print("❌ GOOGLE_ADS_CUSTOMER_ID not found in environment")
            return
        
        print(f"🔍 Customer ID from .env: {customer_id}")
        # print(f"🔍 Login Customer ID from .env: {login_customer_id}")
        
        # Create the account
        account = GoogleAdsAccount.objects.create(
            user=user,
            customer_id=customer_id,
            account_name=f"Google Ads Account {customer_id}",
            is_active=True,
            currency_code="USD",  # Default currency
            time_zone="America/New_York"  # Default timezone
        )
        
        print(f"✅ Successfully created Google Ads account:")
        print(f"   - Customer ID: {account.customer_id}")
        print(f"   - Account Name: {account.account_name}")
        print(f"   - User: {account.user.username}")
        print(f"   - Active: {account.is_active}")
        
        print(f"\n🎉 Your Google Ads account is now set up!")
        print(f"💡 You can now use the chat feature to analyze your data")
        
    except Exception as e:
        print(f"❌ Error creating account: {e}")

if __name__ == "__main__":
    create_google_ads_account()

#!/usr/bin/env python3
"""
Add Multiple Google Ads Accounts
This script helps you add multiple Google Ads accounts manually.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

from google_ads_new.models import GoogleAdsAccount
from django.contrib.auth.models import User

def add_google_ads_account():
    """Add a Google Ads account manually"""
    
    print("🔑 Add Google Ads Account Manually")
    print("=" * 40)
    
    # Get available users
    users = User.objects.all()
    if not users.exists():
        print("❌ No users found in database")
        return
    
    print("👥 Available users:")
    for i, user in enumerate(users):
        print(f"   {i+1}. {user.username} (ID: {user.id})")
    
    # Select user
    try:
        user_choice = int(input("\nSelect user (enter number): ")) - 1
        if user_choice < 0 or user_choice >= len(users):
            print("❌ Invalid user selection")
            return
        selected_user = users[user_choice]
        print(f"✅ Selected user: {selected_user.username}")
    except ValueError:
        print("❌ Please enter a valid number")
        return
    
    # Get account details
    print("\n📝 Enter account details:")
    
    customer_id = input("Customer ID (e.g., 6077394633): ").strip()
    if not customer_id:
        print("❌ Customer ID is required")
        return
    
    account_name = input("Account Name (e.g., 'My Business Account'): ").strip()
    if not account_name:
        account_name = f"Google Ads Account {customer_id}"
    
    currency_code = input("Currency Code (e.g., USD, EUR, GBP) [default: USD]: ").strip().upper()
    if not currency_code:
        currency_code = "USD"
    
    time_zone = input("Time Zone (e.g., America/New_York, Europe/London) [default: America/New_York]: ").strip()
    if not time_zone:
        time_zone = "America/New_York"
    
    # Check if account already exists
    existing = GoogleAdsAccount.objects.filter(customer_id=customer_id)
    if existing.exists():
        print(f"⚠️  Account with Customer ID {customer_id} already exists:")
        for acc in existing:
            print(f"   - {acc.account_name} (User: {acc.user.username})")
        
        overwrite = input("Do you want to update this account? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("❌ Account creation cancelled")
            return
        
        # Update existing account
        account = existing.first()
        account.account_name = account_name
        account.currency_code = currency_code
        account.time_zone = time_zone
        account.is_active = True
        account.save()
        print(f"✅ Updated existing account: {account.account_name}")
    else:
        # Create new account
        account = GoogleAdsAccount.objects.create(
            user=selected_user,
            customer_id=customer_id,
            account_name=account_name,
            is_active=True,
            currency_code=currency_code,
            time_zone=time_zone
        )
        print(f"✅ Created new account: {account.account_name}")
    
    print(f"\n📋 Account Details:")
    print(f"   - Customer ID: {account.customer_id}")
    print(f"   - Account Name: {account.account_name}")
    print(f"   - User: {account.user.username}")
    print(f"   - Currency: {account.currency_code}")
    print(f"   - Time Zone: {account.time_zone}")
    print(f"   - Active: {account.is_active}")

def list_accounts():
    """List all existing Google Ads accounts"""
    
    print("📋 Existing Google Ads Accounts")
    print("=" * 40)
    
    accounts = GoogleAdsAccount.objects.all().order_by('user__username', 'account_name')
    
    if not accounts.exists():
        print("❌ No Google Ads accounts found")
        return
    
    current_user = None
    for account in accounts:
        if current_user != account.user.username:
            current_user = account.user.username
            print(f"\n👤 User: {current_user}")
        
        print(f"   📊 {account.account_name}")
        print(f"      Customer ID: {account.customer_id}")
        print(f"      Currency: {account.currency_code}")
        print(f"      Time Zone: {account.time_zone}")
        print(f"      Active: {account.is_active}")
        print(f"      Created: {account.created_at.strftime('%Y-%m-%d %H:%M')}")

def main():
    """Main menu"""
    
    while True:
        print("\n🔑 Google Ads Account Management")
        print("=" * 40)
        print("1. Add new account")
        print("2. List existing accounts")
        print("3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == "1":
            add_google_ads_account()
        elif choice == "2":
            list_accounts()
        elif choice == "3":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()

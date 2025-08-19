#!/usr/bin/env python3
"""
Test script for Comprehensive Google Ads Sync
Demonstrates syncing all Google Ads data into the database
"""

import requests
import json
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
import django
django.setup()

from google_ads_new.comprehensive_sync_service import ComprehensiveGoogleAdsSyncService

# API endpoints
BASE_URL = "http://localhost:8000"
COMPREHENSIVE_SYNC_URL = f"{BASE_URL}/google-ads-new/api/comprehensive-sync/"

def test_comprehensive_sync_api():
    """Test the comprehensive sync API endpoint"""
    print("🧪 Testing Comprehensive Google Ads Sync API")
    print("=" * 60)
    
    # Test data
    manager_customer_id = "9762343117"  # Your actual manager account ID
    
    print(f"Manager Customer ID: {manager_customer_id}")
    print()
    
    # Test 1: Comprehensive sync (last 7 days)
    print("1️⃣ Testing Comprehensive Sync (Last 7 Days)")
    print("-" * 40)
    
    payload = {
        "manager_customer_id": manager_customer_id,
        "days_back": 7,
        "incremental": False
    }
    
    try:
        response = requests.post(COMPREHENSIVE_SYNC_URL, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Test 2: Incremental daily sync (last 1 day)
    print("2️⃣ Testing Incremental Daily Sync (Last 1 Day)")
    print("-" * 40)
    
    payload = {
        "manager_customer_id": manager_customer_id,
        "incremental": True
    }
    
    try:
        response = requests.post(COMPREHENSIVE_SYNC_URL, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Test 3: Custom date range sync
    print("3️⃣ Testing Custom Date Range Sync (Last 30 Days)")
    print("-" * 40)
    
    payload = {
        "manager_customer_id": manager_customer_id,
        "days_back": 30,
        "incremental": False
    }
    
    try:
        response = requests.post(COMPREHENSIVE_SYNC_URL, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_direct_sync_service():
    """Test the sync service directly"""
    print("\n🔌 Testing Direct Sync Service")
    print("=" * 60)
    
    try:
        sync_service = ComprehensiveGoogleAdsSyncService()
        
        if sync_service.initialize_client():
            print("✅ Google Ads client initialized successfully")
            
            # Test getting client accounts
            manager_customer_id = "9762343117"
            print(f"\n📊 Getting client accounts for manager: {manager_customer_id}")
            
            client_accounts = sync_service.get_all_client_accounts(manager_customer_id)
            print(f"Found {len(client_accounts)} client accounts:")
            
            for account in client_accounts:
                print(f"  - {account['customer_id']}: {account['descriptive_name']}")
                
                # Test getting campaigns for this account
                campaigns = sync_service.get_campaigns(account['customer_id'])
                print(f"    Campaigns: {len(campaigns)}")
                
                # Test getting ad groups for this account
                ad_groups = sync_service.get_ad_groups(account['customer_id'])
                print(f"    Ad Groups: {len(ad_groups)}")
                
                # Test getting keywords for this account
                keywords = sync_service.get_keywords(account['customer_id'])
                print(f"    Keywords: {len(keywords)}")
                
                # Test getting performance data for this account
                performance = sync_service.get_performance_data(
                    account['customer_id'], 
                    "2025-08-11",  # 7 days ago
                    "2025-08-18"   # today
                )
                print(f"    Performance Records: {len(performance)}")
                
                break  # Only test first account for demo
        else:
            print("❌ Failed to initialize Google Ads client")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def show_curl_examples():
    """Show cURL examples for testing"""
    print("\n📋 cURL Examples for Comprehensive Sync")
    print("=" * 60)
    
    manager_customer_id = "9762343117"
    
    print("1️⃣ Comprehensive Sync (Last 7 Days):")
    print(f"curl -X POST {COMPREHENSIVE_SYNC_URL} \\")
    print(f"  -H \"Content-Type: application/json\" \\")
    print(f"  -d '{{")
    print(f"    \"manager_customer_id\": \"{manager_customer_id}\",")
    print(f"    \"days_back\": 7,")
    print(f"    \"incremental\": false")
    print(f"  }}'")
    
    print("\n2️⃣ Incremental Daily Sync (Last 1 Day):")
    print(f"curl -X POST {COMPREHENSIVE_SYNC_URL} \\")
    print(f"  -H \"Content-Type: application/json\" \\")
    print(f"  -d '{{")
    print(f"    \"manager_customer_id\": \"{manager_customer_id}\",")
    print(f"    \"incremental\": true")
    print(f"  }}'")
    
    print("\n3️⃣ Custom Date Range (Last 30 Days):")
    print(f"curl -X POST {COMPREHENSIVE_SYNC_URL} \\")
    print(f"  -H \"Content-Type: application/json\" \\")
    print(f"  -d '{{")
    print(f"    \"manager_customer_id\": \"{manager_customer_id}\",")
    print(f"    \"days_back\": 30,")
    print(f"    \"incremental\": false")
    print(f"  }}'")

def show_management_command_examples():
    """Show Django management command examples"""
    print("\n🐍 Django Management Command Examples")
    print("=" * 60)
    
    print("1️⃣ Comprehensive Sync (Last 7 Days):")
    print("python manage.py comprehensive_sync")
    
    print("\n2️⃣ Custom Date Range (Last 30 Days):")
    print("python manage.py comprehensive_sync --days-back 30")
    
    print("\n3️⃣ Incremental Daily Sync:")
    print("python manage.py comprehensive_sync --incremental")
    
    print("\n4️⃣ Custom Manager ID:")
    print("python manage.py comprehensive_sync --manager-id 9762343117")

if __name__ == "__main__":
    print("🚀 Comprehensive Google Ads Sync Test Suite")
    print("Updated for Google Ads API v28.0.0")
    print()
    
    # Test API endpoints
    test_comprehensive_sync_api()
    
    # Test direct service
    test_direct_sync_service()
    
    # Show examples
    show_curl_examples()
    show_management_command_examples()
    
    print("\n✅ Test suite completed!")
    print("\n📝 Notes:")
    print("- Make sure Django server is running on localhost:8000")
    print("- The comprehensive sync will pull ALL data from ALL client accounts")
    print("- Use incremental sync for daily updates")
    print("- Performance data is filtered by date range for efficiency")
    print("- All data is stored in your PostgreSQL database")
    print("- Check Django admin to view synced data")

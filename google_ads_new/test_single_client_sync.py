#!/usr/bin/env python3
"""
Test script for the Single Client Account Sync API

This script demonstrates how to use the new API endpoint to sync individual client accounts.
"""

import requests
import json
from datetime import datetime


def test_single_client_sync_api():
    """Test the single client sync API endpoint"""
    
    base_url = "http://localhost:8000/google-ads-new"
    
    print("🚀 Testing Single Client Account Sync API")
    print("=" * 50)
    
    # Test 1: Sync all data types for a client account
    print("\n📊 Test 1: Sync all data types for client account 4180736466")
    print("-" * 60)
    
    payload = {
        "client_customer_id": "4180736466",
        "days_back": 7,
        "sync_types": ["campaigns", "ad_groups", "keywords", "performance"]
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/sync-single-client/",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Message: {result.get('message')}")
            print("Summary:")
            summary = result.get('summary', {})
            print(f"  - Account: {summary.get('account_name')} ({summary.get('client_customer_id')})")
            print(f"  - Date Range: {summary.get('start_date')} to {summary.get('end_date')}")
            print(f"  - Campaigns Synced: {summary.get('campaigns_synced')}")
            print(f"  - Ad Groups Synced: {summary.get('ad_groups_synced')}")
            print(f"  - Keywords Synced: {summary.get('keywords_synced')}")
            print(f"  - Performance Records: {summary.get('performance_records_synced')}")
            if summary.get('errors'):
                print(f"  - Errors: {summary.get('errors')}")
        else:
            print("❌ Failed!")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Sync only campaigns and ad groups
    print("\n📊 Test 2: Sync only campaigns and ad groups for client account 3048406696")
    print("-" * 70)
    
    payload = {
        "client_customer_id": "3048406696",
        "days_back": 3,
        "sync_types": ["campaigns", "ad_groups"]
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/sync-single-client/",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Message: {result.get('message')}")
            print("Summary:")
            summary = result.get('summary', {})
            print(f"  - Account: {summary.get('account_name')} ({summary.get('client_customer_id')})")
            print(f"  - Sync Types: {summary.get('sync_types')}")
            print(f"  - Campaigns Synced: {summary.get('campaigns_synced')}")
            print(f"  - Ad Groups Synced: {summary.get('ad_groups_synced')}")
        else:
            print("❌ Failed!")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Sync only performance data
    print("\n📊 Test 3: Sync only performance data for client account 4477009303")
    print("-" * 65)
    
    payload = {
        "client_customer_id": "4477009303",
        "days_back": 1,
        "sync_types": ["performance"]
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/sync-single-client/",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Message: {result.get('message')}")
            print("Summary:")
            summary = result.get('summary', {})
            print(f"  - Account: {summary.get('account_name')} ({summary.get('client_customer_id')})")
            print(f"  - Sync Types: {summary.get('sync_types')}")
            print(f"  - Performance Records: {summary.get('performance_records_synced')}")
        else:
            print("❌ Failed!")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Invalid client ID
    print("\n📊 Test 4: Test with invalid client ID")
    print("-" * 40)
    
    payload = {
        "client_customer_id": "9999999999",
        "days_back": 7,
        "sync_types": ["campaigns"]
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/sync-single-client/",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 400:
            result = response.json()
            print("✅ Expected failure!")
            print(f"Error: {result.get('error')}")
        else:
            print("❌ Unexpected response!")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def show_curl_examples():
    """Show cURL examples for the API"""
    
    print("\n🔧 cURL Examples")
    print("=" * 30)
    
    print("\n1. Sync all data types for a client account:")
    print("""curl -X POST http://localhost:8000/google-ads-new/api/sync-single-client/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "client_customer_id": "4180736466",
    "days_back": 7,
    "sync_types": ["campaigns", "ad_groups", "keywords", "performance"]
  }'""")
    
    print("\n2. Sync only campaigns and ad groups:")
    print("""curl -X POST http://localhost:8000/google-ads-new/api/sync-single-client/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "client_customer_id": "3048406696",
    "days_back": 3,
    "sync_types": ["campaigns", "ad_groups"]
  }'""")
    
    print("\n3. Sync only performance data:")
    print("""curl -X POST http://localhost:8000/google-ads-new/api/sync-single-client/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "client_customer_id": "4477009303",
    "days_back": 1,
    "sync_types": ["performance"]
  }'""")
    
    print("\n4. Sync with default settings (all types, 7 days):")
    print("""curl -X POST http://localhost:8000/google-ads-new/api/sync-single-client/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "client_customer_id": "4180736466"
  }'""")


def show_python_examples():
    """Show Python examples for the API"""
    
    print("\n🐍 Python Examples")
    print("=" * 20)
    
    print("\n1. Basic usage:")
    print("""import requests

# Sync all data types
response = requests.post(
    "http://localhost:8000/google-ads-new/api/sync-single-client/",
    json={
        "client_customer_id": "4180736466",
        "days_back": 7,
        "sync_types": ["campaigns", "ad_groups", "keywords", "performance"]
    }
)

if response.status_code == 200:
    result = response.json()
    print(f"Sync completed: {result['summary']}")
else:
    print(f"Sync failed: {response.text}")""")
    
    print("\n2. Using the sync service directly:")
    print("""from google_ads_new.comprehensive_sync_service import ComprehensiveGoogleAdsSyncService

service = ComprehensiveGoogleAdsSyncService()
result = service.sync_single_client_account(
    client_customer_id="4180736466",
    days_back=7,
    sync_types=["campaigns", "ad_groups"]
)

if result['success']:
    print(f"Sync completed: {result['summary']}")
else:
    print(f"Sync failed: {result['error']}")""")


if __name__ == "__main__":
    print("🎯 Single Client Account Sync API Test Suite")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test the API
        test_single_client_sync_api()
        
        # Show examples
        show_curl_examples()
        show_python_examples()
        
        print("\n✅ Test suite completed!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")

"""
Test script for the Single Client Account Sync API

This script demonstrates how to use the new API endpoint to sync individual client accounts.
"""

import requests
import json
from datetime import datetime


def test_single_client_sync_api():
    """Test the single client sync API endpoint"""
    
    base_url = "http://localhost:8000/google-ads-new"
    
    print("🚀 Testing Single Client Account Sync API")
    print("=" * 50)
    
    # Test 1: Sync all data types for a client account
    print("\n📊 Test 1: Sync all data types for client account 4180736466")
    print("-" * 60)
    
    payload = {
        "client_customer_id": "4180736466",
        "days_back": 7,
        "sync_types": ["campaigns", "ad_groups", "keywords", "performance"]
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/sync-single-client/",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Message: {result.get('message')}")
            print("Summary:")
            summary = result.get('summary', {})
            print(f"  - Account: {summary.get('account_name')} ({summary.get('client_customer_id')})")
            print(f"  - Date Range: {summary.get('start_date')} to {summary.get('end_date')}")
            print(f"  - Campaigns Synced: {summary.get('campaigns_synced')}")
            print(f"  - Ad Groups Synced: {summary.get('ad_groups_synced')}")
            print(f"  - Keywords Synced: {summary.get('keywords_synced')}")
            print(f"  - Performance Records: {summary.get('performance_records_synced')}")
            if summary.get('errors'):
                print(f"  - Errors: {summary.get('errors')}")
        else:
            print("❌ Failed!")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Sync only campaigns and ad groups
    print("\n📊 Test 2: Sync only campaigns and ad groups for client account 3048406696")
    print("-" * 70)
    
    payload = {
        "client_customer_id": "3048406696",
        "days_back": 3,
        "sync_types": ["campaigns", "ad_groups"]
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/sync-single-client/",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Message: {result.get('message')}")
            print("Summary:")
            summary = result.get('summary', {})
            print(f"  - Account: {summary.get('account_name')} ({summary.get('client_customer_id')})")
            print(f"  - Sync Types: {summary.get('sync_types')}")
            print(f"  - Campaigns Synced: {summary.get('campaigns_synced')}")
            print(f"  - Ad Groups Synced: {summary.get('ad_groups_synced')}")
        else:
            print("❌ Failed!")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Sync only performance data
    print("\n📊 Test 3: Sync only performance data for client account 4477009303")
    print("-" * 65)
    
    payload = {
        "client_customer_id": "4477009303",
        "days_back": 1,
        "sync_types": ["performance"]
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/sync-single-client/",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Message: {result.get('message')}")
            print("Summary:")
            summary = result.get('summary', {})
            print(f"  - Account: {summary.get('account_name')} ({summary.get('client_customer_id')})")
            print(f"  - Sync Types: {summary.get('sync_types')}")
            print(f"  - Performance Records: {summary.get('performance_records_synced')}")
        else:
            print("❌ Failed!")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Invalid client ID
    print("\n📊 Test 4: Test with invalid client ID")
    print("-" * 40)
    
    payload = {
        "client_customer_id": "9999999999",
        "days_back": 7,
        "sync_types": ["campaigns"]
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/sync-single-client/",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 400:
            result = response.json()
            print("✅ Expected failure!")
            print(f"Error: {result.get('error')}")
        else:
            print("❌ Unexpected response!")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def show_curl_examples():
    """Show cURL examples for the API"""
    
    print("\n🔧 cURL Examples")
    print("=" * 30)
    
    print("\n1. Sync all data types for a client account:")
    print("""curl -X POST http://localhost:8000/google-ads-new/api/sync-single-client/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "client_customer_id": "4180736466",
    "days_back": 7,
    "sync_types": ["campaigns", "ad_groups", "keywords", "performance"]
  }'""")
    
    print("\n2. Sync only campaigns and ad groups:")
    print("""curl -X POST http://localhost:8000/google-ads-new/api/sync-single-client/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "client_customer_id": "3048406696",
    "days_back": 3,
    "sync_types": ["campaigns", "ad_groups"]
  }'""")
    
    print("\n3. Sync only performance data:")
    print("""curl -X POST http://localhost:8000/google-ads-new/api/sync-single-client/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "client_customer_id": "4477009303",
    "days_back": 1,
    "sync_types": ["performance"]
  }'""")
    
    print("\n4. Sync with default settings (all types, 7 days):")
    print("""curl -X POST http://localhost:8000/google-ads-new/api/sync-single-client/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "client_customer_id": "4180736466"
  }'""")


def show_python_examples():
    """Show Python examples for the API"""
    
    print("\n🐍 Python Examples")
    print("=" * 20)
    
    print("\n1. Basic usage:")
    print("""import requests

# Sync all data types
response = requests.post(
    "http://localhost:8000/google-ads-new/api/sync-single-client/",
    json={
        "client_customer_id": "4180736466",
        "days_back": 7,
        "sync_types": ["campaigns", "ad_groups", "keywords", "performance"]
    }
)

if response.status_code == 200:
    result = response.json()
    print(f"Sync completed: {result['summary']}")
else:
    print(f"Sync failed: {response.text}")""")
    
    print("\n2. Using the sync service directly:")
    print("""from google_ads_new.comprehensive_sync_service import ComprehensiveGoogleAdsSyncService

service = ComprehensiveGoogleAdsSyncService()
result = service.sync_single_client_account(
    client_customer_id="4180736466",
    days_back=7,
    sync_types=["campaigns", "ad_groups"]
)

if result['success']:
    print(f"Sync completed: {result['summary']}")
else:
    print(f"Sync failed: {result['error']}")""")


if __name__ == "__main__":
    print("🎯 Single Client Account Sync API Test Suite")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test the API
        test_single_client_sync_api()
        
        # Show examples
        show_curl_examples()
        show_python_examples()
        
        print("\n✅ Test suite completed!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")


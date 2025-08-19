#!/usr/bin/env python3
"""
Simple test script to verify Google Ads API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_dashboard():
    """Test the dashboard endpoint"""
    print("Testing dashboard endpoint...")
    
    try:
        # First, try to access the dashboard (should redirect to login)
        response = requests.get(f"{BASE_URL}/google-ads/dashboard/", allow_redirects=False)
        print(f"Dashboard response status: {response.status_code}")
        
        if response.status_code == 302:
            print("✓ Dashboard redirects to login (expected)")
        else:
            print(f"✗ Unexpected dashboard response: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Dashboard test failed: {e}")

def test_api_endpoints():
    """Test API endpoints"""
    print("\nTesting API endpoints...")
    
    # Test dashboard API
    try:
        response = requests.get(f"{BASE_URL}/google-ads/api/dashboard/")
        print(f"Dashboard API status: {response.status_code}")
        
        if response.status_code == 401:
            print("✓ Dashboard API requires authentication (expected)")
        else:
            print(f"✗ Unexpected dashboard API response: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Dashboard API test failed: {e}")
    
    # Test accounts API
    try:
        response = requests.get(f"{BASE_URL}/google-ads/api/accounts/")
        print(f"Accounts API status: {response.status_code}")
        
        if response.status_code == 401:
            print("✓ Accounts API requires authentication (expected)")
        else:
            print(f"✗ Unexpected accounts API response: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Accounts API test failed: {e}")

def test_admin():
    """Test admin interface"""
    print("\nTesting admin interface...")
    
    try:
        response = requests.get(f"{BASE_URL}/admin/")
        print(f"Admin response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Admin interface accessible")
        else:
            print(f"✗ Admin interface not accessible: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Admin test failed: {e}")

def test_urls():
    """Test URL patterns"""
    print("\nTesting URL patterns...")
    
    urls_to_test = [
        "/google-ads/dashboard/",
        "/google-ads/api/accounts/",
        "/google-ads/api/campaigns/",
        "/google-ads/api/ad-groups/",
        "/google-ads/api/keywords/",
        "/google-ads/api/performance/",
        "/google-ads/api/reports/",
        "/google-ads/api/alerts/",
        "/google-ads/api/dashboard/",
        "/google-ads/api/sync-account/",
        "/google-ads/api/create-campaign/",
        "/google-ads/api/create-keyword/",
        "/google-ads/api/export-performance/",
    ]
    
    for url in urls_to_test:
        try:
            response = requests.get(f"{BASE_URL}{url}", allow_redirects=False)
            print(f"{url}: {response.status_code}")
        except Exception as e:
            print(f"{url}: Error - {e}")

if __name__ == "__main__":
    print("Google Ads Marketing Assistant - API Test")
    print("=" * 50)
    
    test_dashboard()
    test_api_endpoints()
    test_admin()
    test_urls()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("\nTo access the application:")
    print(f"1. Admin interface: {BASE_URL}/admin/")
    print(f"2. Dashboard: {BASE_URL}/google-ads/dashboard/")
    print(f"3. API endpoints: {BASE_URL}/google-ads/api/")
    print("\nNote: You'll need to log in with the superuser account (admin/admin)")

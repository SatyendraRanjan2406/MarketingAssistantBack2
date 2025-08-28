#!/usr/bin/env python3
"""
Test Script for Live Monitoring API
Demonstrates how to use the live monitoring endpoints
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# Setup Django
sys.path.append('/Users/satyendra/marketing_assistant_back')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

from django.contrib.auth.models import User
from google_ads_new.models import GoogleAdsAccount, GoogleAdsPerformance, GoogleAdsCampaign
from google_ads_new.live_monitoring_service import LiveMonitoringService

def test_live_monitoring_service():
    """Test the LiveMonitoringService directly"""
    print("🧪 Testing LiveMonitoringService Directly")
    print("=" * 50)
    
    try:
        # Get the testuser and their account
        user = User.objects.get(username='testuser')
        if not user:
            print("❌ testuser not found in database")
            return False
        
        account = GoogleAdsAccount.objects.filter(user=user).first()
        if not account:
            print("❌ No Google Ads accounts found for testuser")
            return False
        
        print(f"✅ Testing with user: {user.username} (ID: {user.id})")
        print(f"✅ Testing with account: {account.account_name} (ID: {account.id})")
        
        # Test the monitoring service
        monitoring_service = LiveMonitoringService(account.id)
        monitoring_data = monitoring_service.get_live_monitoring_data()
        
        print(f"\n📊 Live Monitoring Data Retrieved:")
        print(f"   Status: {monitoring_data.get('status')}")
        print(f"   Timestamp: {monitoring_data.get('timestamp')}")
        print(f"   Last Updated: {monitoring_data.get('last_updated')}")
        
        # Show monitoring sections
        monitoring = monitoring_data.get('monitoring', {})
        print(f"\n🔍 Monitoring Sections:")
        print(f"   Performance Insights: {len(monitoring.get('performance', []))} items")
        print(f"   Alerts: {len(monitoring.get('alerts', []))} items")
        print(f"   Optimization: {len(monitoring.get('optimization', []))} items")
        print(f"   Trends: {len(monitoring.get('trends', []))} items")
        
        # Show quick stats
        quick_stats = monitoring_data.get('quick_stats', {})
        print(f"\n📈 Quick Stats:")
        print(f"   Active Campaigns: {quick_stats.get('active_campaigns')}")
        print(f"   Total Spend (24h): {quick_stats.get('total_spend_24h')}")
        print(f"   Avg ROAS: {quick_stats.get('avg_roas')}")
        print(f"   Conversions: {quick_stats.get('conversions')}")
        
        # Show campaign overview
        campaign_overview = monitoring_data.get('campaign_overview', {})
        print(f"\n🎯 Campaign Overview:")
        print(f"   Total Campaigns: {campaign_overview.get('total_campaigns')}")
        print(f"   Active Campaigns: {campaign_overview.get('active_campaigns')}")
        print(f"   Paused Campaigns: {campaign_overview.get('paused_campaigns')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing LiveMonitoringService: {e}")
        return False

def test_api_endpoints():
    """Test the API endpoints"""
    print("\n🌐 Testing Live Monitoring API Endpoints")
    print("=" * 50)
    
    # Get the test account ID
    try:
        user = User.objects.get(username='testuser')
        account = GoogleAdsAccount.objects.filter(user=user).first()
        if not account:
            print("❌ No test account found")
            return
        
        account_id = account.id
        print(f"✅ Testing with account ID: {account_id}")
        
    except Exception as e:
        print(f"❌ Error getting test account: {e}")
        return
    
    # Base URL for the API
    base_url = "http://localhost:8000"
    
    # Test endpoints - using the correct URL prefix
    endpoints = [
        f"/google-ads-new/api/live-monitoring/",
        f"/google-ads-new/api/live-monitoring/account/{account_id}/",
        f"/google-ads-new/api/live-monitoring/account/{account_id}/quick-stats/",
        f"/google-ads-new/api/live-monitoring/account/{account_id}/insights/",
        f"/google-ads-new/api/live-monitoring/account/{account_id}/performance/",
    ]
    
    for endpoint in endpoints:
        print(f"\n🔗 Testing: {endpoint}")
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"   ✅ Success: {response.status_code}")
                data = response.json()
                print(f"   📊 Status: {data.get('status')}")
                print(f"   💬 Message: {data.get('message')}")
            elif response.status_code == 401:
                print(f"   🔒 Unauthorized: {response.status_code} (Authentication required)")
            elif response.status_code == 404:
                print(f"   ❌ Not Found: {response.status_code}")
            else:
                print(f"   ⚠️  Other Status: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection Error: Django server not running")
        except Exception as e:
            print(f"   ❌ Error: {e}")

def create_sample_data():
    """Create sample data for testing"""
    print("\n📝 Creating Sample Data for Testing")
    print("=" * 50)
    
    try:
        # Get or create user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            print(f"✅ Created user: {user.username}")
        else:
            print(f"✅ Using existing user: {user.username}")
        
        # Get or create Google Ads account
        account, created = GoogleAdsAccount.objects.get_or_create(
            customer_id='1234567890',
            defaults={
                'user': user,
                'account_name': 'Test Google Ads Account',
                'currency_code': 'USD',
                'time_zone': 'America/New_York',
                'is_active': True
            }
        )
        
        if created:
            print(f"✅ Created account: {account.account_name}")
        else:
            print(f"✅ Using existing account: {account.account_name}")
        
        # Get or create campaign
        campaign, created = GoogleAdsCampaign.objects.get_or_create(
            campaign_id='123456789',
            defaults={
                'account': account,
                'campaign_name': 'Test Campaign',
                'campaign_status': 'ENABLED',
                'campaign_type': 'SEARCH',
                'start_date': datetime.now().date(),
                'budget_amount': 100.00,
                'budget_type': 'DAILY'
            }
        )
        
        if created:
            print(f"✅ Created campaign: {campaign.campaign_name}")
        else:
            print(f"✅ Using existing campaign: {campaign.campaign_name}")
        
        # Create sample performance data
        performance, created = GoogleAdsPerformance.objects.get_or_create(
            account=account,
            campaign=campaign,
            date=datetime.now().date(),
            defaults={
                'impressions': 1000,
                'clicks': 50,
                'cost_micros': 50000000,  # $50.00
                'conversions': 5,
                'conversion_value': 250.00
            }
        )
        
        if created:
            print(f"✅ Created performance data for {performance.date}")
        else:
            print(f"✅ Using existing performance data for {performance.date}")
        
        return account.id
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return None

def main():
    """Main test function"""
    print("🚀 Live Monitoring API Test Suite")
    print("=" * 60)
    
    # Create sample data
    account_id = create_sample_data()
    if not account_id:
        print("❌ Failed to create sample data")
        return
    
    # Test the service directly
    if test_live_monitoring_service():
        print("\n✅ LiveMonitoringService test passed!")
    else:
        print("\n❌ LiveMonitoringService test failed!")
    
    # Test API endpoints
    test_api_endpoints()
    
    print("\n🎉 Test suite completed!")
    print("\n💡 To test the API with a running Django server:")
    print("   1. Start Django: python manage.py runserver")
    print("   2. Run this script again to test API endpoints")
    print("   3. Or test manually with curl/Postman")

if __name__ == "__main__":
    main()

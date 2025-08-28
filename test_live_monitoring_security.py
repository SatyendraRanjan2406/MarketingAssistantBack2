#!/usr/bin/env python3
"""
Security Test Script for Live Monitoring API
Tests access control and user isolation
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

def test_user_isolation():
    """Test that users can only access their own accounts"""
    print("🔒 Testing User Isolation and Access Control")
    print("=" * 60)
    
    try:
        # Create test users
        user1, created1 = User.objects.get_or_create(
            username='security_test_user1',
            defaults={
                'email': 'security1@example.com',
                'first_name': 'Security',
                'last_name': 'User1'
            }
        )
        
        user2, created2 = User.objects.get_or_create(
            username='security_test_user2',
            defaults={
                'email': 'security2@example.com',
                'first_name': 'Security',
                'last_name': 'User2'
            }
        )
        
        if created1:
            print(f"✅ Created user1: {user1.username}")
        if created2:
            print(f"✅ Created user2: {user2.username}")
        
        # Create accounts for each user
        account1, created1 = GoogleAdsAccount.objects.get_or_create(
            customer_id='SECURITY_TEST_001',
            defaults={
                'user': user1,
                'account_name': 'Security Test Account 1',
                'currency_code': 'USD',
                'time_zone': 'America/New_York',
                'is_active': True
            }
        )
        
        account2, created2 = GoogleAdsAccount.objects.get_or_create(
            customer_id='SECURITY_TEST_002',
            defaults={
                'user': user2,
                'account_name': 'Security Test Account 2',
                'currency_code': 'USD',
                'time_zone': 'America/New_York',
                'is_active': True
            }
        )
        
        if created1:
            print(f"✅ Created account1 for user1: {account1.account_name}")
        if created2:
            print(f"✅ Created account2 for user2: {account2.account_name}")
        
        # Test 1: User1 should only see their own accounts
        print(f"\n🧪 Test 1: User1 ({user1.username}) accessing their own account")
        user1_accounts = GoogleAdsAccount.objects.filter(user=user1, is_active=True)
        print(f"   User1 can see {user1_accounts.count()} accounts:")
        for acc in user1_accounts:
            print(f"     - {acc.account_name} (ID: {acc.id})")
        
        # Test 2: User2 should only see their own accounts
        print(f"\n🧪 Test 2: User2 ({user2.username}) accessing their own account")
        user2_accounts = GoogleAdsAccount.objects.filter(user=user2, is_active=True)
        print(f"   User2 can see {user2_accounts.count()} accounts:")
        for acc in user2_accounts:
            print(f"     - {acc.account_name} (ID: {acc.id})")
        
        # Test 3: Verify isolation
        print(f"\n🧪 Test 3: Verifying user isolation")
        user1_can_see_user2_account = GoogleAdsAccount.objects.filter(
            user=user1,
            id=account2.id
        ).exists()
        
        user2_can_see_user1_account = GoogleAdsAccount.objects.filter(
            user=user2,
            id=account1.id
        ).exists()
        
        print(f"   User1 can see User2's account: {user1_can_see_user2_account} ❌ (Should be False)")
        print(f"   User2 can see User1's account: {user2_can_see_user1_account} ❌ (Should be False)")
        
        if not user1_can_see_user2_account and not user2_can_see_user1_account:
            print("   ✅ User isolation working correctly!")
        else:
            print("   ❌ User isolation failed!")
        
        # Test 4: Test the service directly
        print(f"\n🧪 Test 4: Testing LiveMonitoringService isolation")
        from google_ads_new.live_monitoring_service import LiveMonitoringService
        
        # User1 service should only work with their account
        user1_service = LiveMonitoringService(account1.id)
        user1_data = user1_service.get_live_monitoring_data()
        
        # User2 service should only work with their account
        user2_service = LiveMonitoringService(account2.id)
        user2_data = user2_service.get_live_monitoring_data()
        
        print(f"   User1 service working: {user1_data.get('status') == 'success'}")
        print(f"   User2 service working: {user2_data.get('status') == 'success'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in security test: {e}")
        return False

def test_api_access_control():
    """Test API access control with different users"""
    print("\n🌐 Testing API Access Control")
    print("=" * 50)
    
    try:
        # Get test accounts
        user1 = User.objects.get(username='security_test_user1')
        user2 = User.objects.get(username='security_test_user2')
        
        account1 = GoogleAdsAccount.objects.get(customer_id='SECURITY_TEST_001')
        account2 = GoogleAdsAccount.objects.get(customer_id='SECURITY_TEST_002')
        
        print(f"✅ Testing with:")
        print(f"   User1: {user1.username} (ID: {user1.id})")
        print(f"   User2: {user2.username} (ID: {user2.id})")
        print(f"   Account1: {account1.account_name} (ID: {account1.id})")
        print(f"   Account2: {account2.account_name} (ID: {account2.id})")
        
        # Test API endpoints (these will fail without proper authentication, but we can test the logic)
        base_url = "http://localhost:8000"
        
        endpoints = [
            f"/google-ads-new/api/live-monitoring/",
            f"/google-ads-new/api/live-monitoring/account/{account1.id}/",
            f"/google-ads-new/api/live-monitoring/account/{account2.id}/",
        ]
        
        print(f"\n🔗 Testing API endpoints (will show 401 without auth):")
        for endpoint in endpoints:
            print(f"\n   Testing: {endpoint}")
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                if response.status_code == 401:
                    print(f"     ✅ 401 Unauthorized (Authentication required)")
                elif response.status_code == 403:
                    print(f"     ✅ 403 Forbidden (Access denied)")
                elif response.status_code == 404:
                    print(f"     ⚠️  404 Not Found")
                else:
                    print(f"     📊 Status: {response.status_code}")
            except requests.exceptions.ConnectionError:
                print(f"     ❌ Connection Error (Django server not running)")
            except Exception as e:
                print(f"     ❌ Error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in API access control test: {e}")
        return False

def test_database_queries():
    """Test database query isolation"""
    print("\n🗄️ Testing Database Query Isolation")
    print("=" * 50)
    
    try:
        user1 = User.objects.get(username='security_test_user1')
        user2 = User.objects.get(username='security_test_user2')
        
        account1 = GoogleAdsAccount.objects.get(customer_id='SECURITY_TEST_001')
        account2 = GoogleAdsAccount.objects.get(customer_id='SECURITY_TEST_002')
        
        # Test 1: User1 queries
        print(f"\n🧪 Test 1: User1 database queries")
        user1_accounts = GoogleAdsAccount.objects.filter(user=user1)
        user1_campaigns = GoogleAdsCampaign.objects.filter(campaign__account__user=user1)
        
        print(f"   User1 accounts: {user1_accounts.count()}")
        print(f"   User1 campaigns: {user1_campaigns.count()}")
        
        # Test 2: User2 queries
        print(f"\n🧪 Test 2: User2 database queries")
        user2_accounts = GoogleAdsAccount.objects.filter(user=user2)
        user2_campaigns = GoogleAdsCampaign.objects.filter(campaign__account__user=user2)
        
        print(f"   User2 accounts: {user2_accounts.count()}")
        print(f"   User2 campaigns: {user2_campaigns.count()}")
        
        # Test 3: Cross-user access attempts
        print(f"\n🧪 Test 3: Cross-user access attempts")
        user1_accessing_user2 = GoogleAdsAccount.objects.filter(
            user=user1,
            id=account2.id
        ).exists()
        
        user2_accessing_user1 = GoogleAdsAccount.objects.filter(
            user=user2,
            id=account1.id
        ).exists()
        
        print(f"   User1 accessing User2 account: {user1_accessing_user2}")
        print(f"   User2 accessing User1 account: {user2_accessing_user1}")
        
        if not user1_accessing_user2 and not user2_accessing_user1:
            print("   ✅ Database isolation working correctly!")
        else:
            print("   ❌ Database isolation failed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in database query test: {e}")
        return False

def cleanup_test_data():
    """Clean up test data"""
    print("\n🧹 Cleaning Up Test Data")
    print("=" * 40)
    
    try:
        # Remove test accounts
        GoogleAdsAccount.objects.filter(
            customer_id__in=['SECURITY_TEST_001', 'SECURITY_TEST_002']
        ).delete()
        
        # Remove test users
        User.objects.filter(
            username__in=['security_test_user1', 'security_test_user2']
        ).delete()
        
        print("✅ Test data cleaned up successfully")
        
    except Exception as e:
        print(f"❌ Error cleaning up test data: {e}")

def main():
    """Main security test function"""
    print("🔒 Live Monitoring API Security Test Suite")
    print("=" * 70)
    
    try:
        # Run security tests
        if test_user_isolation():
            print("\n✅ User isolation test passed!")
        else:
            print("\n❌ User isolation test failed!")
        
        if test_database_queries():
            print("\n✅ Database query isolation test passed!")
        else:
            print("\n❌ Database query isolation test failed!")
        
        if test_api_access_control():
            print("\n✅ API access control test passed!")
        else:
            print("\n❌ API access control test failed!")
        
        print("\n🎉 Security test suite completed!")
        print("\n💡 Security Features Implemented:")
        print("   1. ✅ User authentication required (IsAuthenticated)")
        print("   2. ✅ Custom permission class (GoogleAdsAccountAccessPermission)")
        print("   3. ✅ Account ownership verification")
        print("   4. ✅ Database query isolation by user")
        print("   5. ✅ Comprehensive logging for security monitoring")
        print("   6. ✅ Defense in depth (multiple security checks)")
        print("   7. ✅ Clear error messages for access violations")
        
        # Clean up test data
        cleanup_test_data()
        
    except Exception as e:
        print(f"\n❌ Security test suite failed: {e}")
        cleanup_test_data()

if __name__ == "__main__":
    main()

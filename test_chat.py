#!/usr/bin/env python3
"""
Test script for Google Ads Chat Service
Run this to test the chat functionality without the full Django server
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

# Now import Django models and services
from google_ads_app.chat_service import GoogleAdsChatService
from google_ads_app.models import GoogleAdsAccount, GoogleAdsCampaign, GoogleAdsPerformance

def test_chat_service():
    """Test the chat service functionality"""
    print("🧪 Testing Google Ads Chat Service...")
    
    # Check if we have any data
    try:
        accounts_count = GoogleAdsAccount.objects.count()
        campaigns_count = GoogleAdsCampaign.objects.count()
        performance_count = GoogleAdsPerformance.objects.count()
        
        print(f"📊 Found {accounts_count} accounts, {campaigns_count} campaigns, {performance_count} performance records")
        
        if accounts_count == 0:
            print("⚠️  No Google Ads accounts found. Please sync some data first.")
            return False
            
    except Exception as e:
        print(f"❌ Error checking data: {e}")
        return False
    
    # Test chat service initialization
    try:
        # Use a dummy API key for testing
        chat_service = GoogleAdsChatService(
            user_id=1,  # Assuming user ID 1 exists
            openai_api_key="test_key"
        )
        print("✅ Chat service initialized successfully")
        
        # Test getting user context
        context = chat_service.get_user_data_context()
        if "error" in context:
            print(f"⚠️  Context error: {context['error']}")
        else:
            print(f"✅ User context retrieved: {context.get('accounts_count', 0)} accounts")
            print(f"   Total spend: ${context.get('total_spend', 0):.2f}")
            print(f"   CTR: {context.get('ctr', 0):.2%}")
        
        # Test quick insights
        insights = chat_service.get_quick_insights()
        if "error" in insights:
            print(f"⚠️  Insights error: {insights['error']}")
        else:
            print(f"✅ Quick insights generated: {len(insights.get('insights', []))} insights")
            print(f"   Actions: {len(insights.get('actions', []))} recommendations")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing chat service: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_models():
    """Test the data models"""
    print("\n🔍 Testing Data Models...")
    
    try:
        # Test GoogleAdsAccount
        accounts = GoogleAdsAccount.objects.all()[:5]
        print(f"✅ GoogleAdsAccount: {len(accounts)} accounts found")
        
        # Test GoogleAdsCampaign
        campaigns = GoogleAdsCampaign.objects.all()[:5]
        print(f"✅ GoogleAdsCampaign: {len(campaigns)} campaigns found")
        
        # Test GoogleAdsPerformance
        performance = GoogleAdsPerformance.objects.all()[:5]
        print(f"✅ GoogleAdsPerformance: {len(performance)} records found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing models: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Google Ads Chat Service Tests\n")
    
    # Test 1: Data Models
    models_ok = test_data_models()
    
    # Test 2: Chat Service
    chat_ok = test_chat_service()
    
    # Summary
    print("\n" + "="*50)
    print("📋 TEST SUMMARY")
    print("="*50)
    
    if models_ok:
        print("✅ Data Models: PASSED")
    else:
        print("❌ Data Models: FAILED")
    
    if chat_ok:
        print("✅ Chat Service: PASSED")
    else:
        print("❌ Chat Service: FAILED")
    
    if models_ok and chat_ok:
        print("\n🎉 All tests passed! The chat service is ready to use.")
        print("\n📝 Next steps:")
        print("1. Set your OPENAI_API_KEY in .env file")
        print("2. Run: python manage.py runserver")
        print("3. Visit: http://localhost:8000/google-ads/chat/")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure you have Google Ads data synced")
        print("2. Check database migrations: python manage.py migrate")
        print("3. Verify your Google Ads API credentials")

if __name__ == "__main__":
    main()

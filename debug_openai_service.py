#!/usr/bin/env python3
"""
Debug OpenAI Service Script
Tests the OpenAI service to identify issues with dynamic analysis generation
"""

import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

def debug_openai_service():
    """Debug the OpenAI service to identify issues"""
    
    print("🔍 Debugging OpenAI Service...")
    print("=" * 50)
    
    # Check environment variables
    print("\n1. Environment Variables Check:")
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"   ✅ OPENAI_API_KEY found: {api_key[:10]}...")
        print(f"   📏 Key length: {len(api_key)} characters")
    else:
        print("   ❌ OPENAI_API_KEY not found!")
        print("   💡 Set it in your .env file: OPENAI_API_KEY=sk-your-key-here")
        return
    
    # Test OpenAI service initialization
    print("\n2. OpenAI Service Initialization:")
    try:
        from google_ads_new.openai_service import GoogleAdsOpenAIService
        openai_service = GoogleAdsOpenAIService()
        print("   ✅ OpenAI service initialized successfully")
    except Exception as e:
        print(f"   ❌ OpenAI service initialization failed: {e}")
        return
    
    # Test basic OpenAI connection
    print("\n3. OpenAI API Connection Test:")
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use accessible model
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        print("   ✅ OpenAI API connection successful")
        print(f"   📝 Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"   ❌ OpenAI API connection failed: {e}")
        return
    
    # Test analysis response generation
    print("\n4. Analysis Response Generation Test:")
    try:
        # Test data
        test_data = {
            "account_name": "Test Account",
            "campaigns_count": 3,
            "campaigns": [
                {"campaign_name": "Test Campaign 1", "status": "ENABLED", "budget": 100},
                {"campaign_name": "Test Campaign 2", "status": "PAUSED", "budget": 150},
                {"campaign_name": "Test Campaign 3", "status": "ENABLED", "budget": 200}
            ],
            "analysis_type": "campaign_optimization"
        }
        
        # Generate response
        response = openai_service.generate_analysis_response(
            "OPTIMIZE_CAMPAIGN",
            test_data,
            "Testing campaign optimization analysis"
        )
        
        print("   ✅ Analysis response generated successfully")
        print(f"   📊 Response type: {type(response)}")
        
        if "blocks" in response:
            print(f"   🎨 UI blocks generated: {len(response['blocks'])}")
            for i, block in enumerate(response['blocks']):
                print(f"      Block {i+1}: {block.get('type', 'unknown')}")
        else:
            print(f"   ⚠️  Response structure: {list(response.keys())}")
            
    except Exception as e:
        print(f"   ❌ Analysis response generation failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test with real user data
    print("\n5. Real User Data Test:")
    try:
        from django.contrib.auth.models import User
        from google_ads_new.models import GoogleAdsAccount
        
        # Get a test user
        user = User.objects.first()
        if not user:
            print("   ⚠️  No users found in database")
            return
        
        print(f"   👤 Using user: {user.username}")
        
        # Check if user has Google Ads accounts
        accounts = GoogleAdsAccount.objects.filter(user=user, is_active=True)
        if accounts.exists():
            account = accounts.first()
            print(f"   📊 Found account: {account.account_name}")
            
            # Get real campaign data
            from google_ads_new.models import GoogleAdsCampaign
            campaigns = GoogleAdsCampaign.objects.filter(account=account)
            print(f"   🎯 Campaigns found: {campaigns.count()}")
            
            if campaigns.exists():
                # Prepare real data
                real_data = {
                    "account_name": account.account_name,
                    "campaigns_count": campaigns.count(),
                    "campaigns": list(campaigns.values('campaign_name', 'campaign_status', 'budget_amount', 'campaign_type')),
                    "analysis_type": "campaign_optimization"
                }
                
                print("   🔍 Testing with real campaign data...")
                response = openai_service.generate_analysis_response(
                    "OPTIMIZE_CAMPAIGN",
                    real_data,
                    f"Optimizing campaigns for account {account.account_name}"
                )
                
                if "blocks" in response:
                    print(f"   ✅ Real data analysis successful: {len(response['blocks'])} blocks")
                else:
                    print(f"   ⚠️  Real data analysis response: {list(response.keys())}")
            else:
                print("   ⚠️  No campaigns found for this account")
        else:
            print("   ⚠️  No Google Ads accounts found for this user")
            
    except Exception as e:
        print(f"   ❌ Real user data test failed: {e}")
        import traceback
        traceback.print_exc()

def test_analysis_service():
    """Test the analysis service integration"""
    
    print("\n🔧 Testing Analysis Service Integration:")
    print("=" * 50)
    
    try:
        from django.contrib.auth.models import User
        from google_ads_new.analysis_service import GoogleAdsAnalysisService
        
        # Get a test user
        user = User.objects.first()
        if not user:
            print("   ⚠️  No users found in database")
            return
        
        print(f"   👤 Using user: {user.username}")
        
        # Initialize analysis service
        analysis_service = GoogleAdsAnalysisService(user)
        print("   ✅ Analysis service initialized")
        
        # Test optimize_campaign method
        print("\n   🎯 Testing optimize_campaign method:")
        try:
            result = analysis_service.optimize_campaign()
            print(f"   📊 Result type: {type(result)}")
            
            if "error" in result:
                print(f"   ❌ Error: {result['error']}")
            elif "blocks" in result:
                print(f"   ✅ Success: {len(result['blocks'])} UI blocks generated")
            else:
                print(f"   ⚠️  Unexpected result structure: {list(result.keys())}")
                
        except Exception as e:
            print(f"   ❌ optimize_campaign failed: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"   ❌ Analysis service test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main debug function"""
    
    print("🚀 Starting OpenAI Service Debug...")
    
    # Debug OpenAI service
    debug_openai_service()
    
    # Test analysis service
    test_analysis_service()
    
    print("\n🎯 Debug Summary:")
    print("   - Check OPENAI_API_KEY in .env file")
    print("   - Verify OpenAI API key is valid and has credits")
    print("   - Check Django database connection")
    print("   - Review error logs for specific issues")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Demo script for OpenAI Fallback Integration
Tests the fallback mechanism when intent actions don't match predefined actions
"""

import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

def demo_fallback_integration():
    """Demo the fallback mechanism for unmatched actions"""
    
    print("🔄 OpenAI Fallback Integration Demo")
    print("=" * 50)
    
    try:
        from google_ads_new.chat_service import GoogleAdsChatService
        from google_ads_new.openai_service import GoogleAdsOpenAIService
        from django.contrib.auth.models import User
        
        # Get a test user
        try:
            user = User.objects.first()
            if not user:
                print("❌ No users found. Please create a user first.")
                return
        except Exception as e:
            print(f"❌ Error getting user: {e}")
            return
        
        print(f"✅ Using user: {user.username}")
        
        # Initialize chat service
        chat_service = GoogleAdsChatService(user)
        
        # Test unmatched actions
        unmatched_actions = [
            "ANALYZE_CUSTOM_METRICS",
            "OPTIMIZE_BIDDING_STRATEGY", 
            "ANALYZE_CROSS_CHANNEL_PERFORMANCE",
            "GENERATE_CREATIVE_BRIEF",
            "ANALYZE_CUSTOMER_JOURNEY"
        ]
        
        print("\n🧪 Testing Fallback for Unmatched Actions...")
        print("   These actions are not in our predefined list of 43 actions.")
        print("   They should automatically fallback to OpenAI for intelligent responses.")
        
        for action in unmatched_actions:
            print(f"\n🔍 Testing Action: {action}")
            
            try:
                # Create a mock intent
                mock_intent = type('MockIntent', (), {
                    'action': action,
                    'confidence': 0.85,
                    'parameters': {},
                    'requires_auth': True
                })()
                
                # Test the fallback mechanism
                message = f"Please {action.lower().replace('_', ' ')} for my Google Ads account"
                
                # Process the message (this should trigger fallback)
                results = chat_service.process_message(message, mock_intent)
                
                if "openai_fallback_response" in results:
                    print(f"   ✅ Fallback triggered successfully!")
                    print(f"   📝 Fallback message: {results.get('fallback_message', 'N/A')}")
                    
                    # Check OpenAI response structure
                    openai_response = results["openai_fallback_response"]
                    if "blocks" in openai_response:
                        print(f"   🎨 Generated {len(openai_response['blocks'])} UI blocks")
                        
                        # Show block types
                        block_types = [block.get('type', 'unknown') for block in openai_response['blocks']]
                        print(f"   📊 Block types: {', '.join(block_types)}")
                        
                        # Show sample content
                        for i, block in enumerate(openai_response['blocks'][:2]):  # Show first 2 blocks
                            block_type = block.get('type', 'unknown')
                            if block_type == 'text':
                                content = block.get('content', '')[:80] + '...' if len(block.get('content', '')) > 80 else block.get('content', '')
                                print(f"      Block {i+1} ({block_type}): {content}")
                            elif block_type == 'chart':
                                title = block.get('title', 'No title')
                                chart_type = block.get('chart_type', 'unknown')
                                print(f"      Block {i+1} ({block_type}): {title} ({chart_type})")
                            elif block_type == 'table':
                                title = block.get('title', 'No title')
                                headers = block.get('headers', [])
                                print(f"      Block {i+1} ({block_type}): {title} - {len(headers)} columns")
                            elif block_type == 'list':
                                title = block.get('title', 'No title')
                                items_count = len(block.get('items', []))
                                print(f"      Block {i+1} ({block_type}): {title} - {items_count} items")
                            elif block_type == 'actions':
                                title = block.get('title', 'No title')
                                items_count = len(block.get('items', []))
                                print(f"      Block {i+1} ({block_type}): {title} - {items_count} actions")
                    else:
                        print(f"   ⚠️  OpenAI response doesn't have expected 'blocks' structure")
                        print(f"   📄 Response keys: {list(openai_response.keys())}")
                
                else:
                    print(f"   ❌ Fallback not triggered")
                    print(f"   📄 Results keys: {list(results.keys())}")
                    
            except Exception as e:
                print(f"   ❌ Error testing fallback: {e}")
        
        print("\n🎯 Fallback Integration Features:")
        print("   ✅ Automatic redirection to OpenAI for unmatched actions")
        print("   ✅ Context-aware prompts with user's Google Ads data")
        print("   ✅ Structured UI block responses (charts, tables, lists, actions)")
        print("   ✅ Seamless integration with existing chat flow")
        print("   ✅ Fallback message indication for users")
        
        print("\n🔧 How It Works:")
        print("   1. User sends message with unmatched intent action")
        print("   2. System detects action is not in predefined list")
        print("   3. Automatically redirects to OpenAI service")
        print("   4. OpenAI generates intelligent response with UI blocks")
        print("   5. Frontend renders response with fallback indicator")
        
        print("\n📱 Frontend Integration:")
        print("   ✅ AnalysisBlock handles 'openai_fallback' type")
        print("   ✅ renderOpenAIBlock renders all block types")
        print("   ✅ Blue border indicator shows fallback responses")
        print("   ✅ Seamless user experience")
        
        print("\n🚀 Ready to use! The system now handles any action type:")
        print("   - Predefined actions (43 total) → Use analysis service")
        print("   - Unmatched actions → Automatically fallback to OpenAI")
        print("   - All responses include rich UI components")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all required packages are installed:")
        print("   pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("💡 Check the Django setup and database connection")

def test_openai_fallback_directly():
    """Test OpenAI fallback service directly"""
    
    print("\n" + "=" * 50)
    print("🧪 Direct OpenAI Fallback Service Test")
    print("=" * 50)
    
    try:
        from google_ads_new.openai_service import GoogleAdsOpenAIService
        from google_ads_new.data_service import GoogleAdsDataService
        from django.contrib.auth.models import User
        
        # Get a test user
        user = User.objects.first()
        if not user:
            print("❌ No users found for direct test")
            return
        
        # Initialize services
        openai_service = GoogleAdsOpenAIService()
        data_service = GoogleAdsDataService(user)
        
        # Get sample data
        account_data = data_service.get_campaign_data()
        
        # Test custom action
        custom_action = "ANALYZE_CUSTOM_METRICS"
        user_context = "User wants to analyze custom metrics not covered by standard actions"
        
        print(f"🔍 Testing OpenAI fallback for: {custom_action}")
        
        response = openai_service.generate_analysis_response(
            custom_action,
            account_data,
            user_context
        )
        
        if "blocks" in response:
            print(f"✅ OpenAI fallback response generated successfully!")
            print(f"📊 Response contains {len(response['blocks'])} UI blocks")
            print(f"🎯 Action: {response.get('action', 'N/A')}")
            print(f"📝 Data source: {response.get('data_source', 'N/A')}")
            
            # Show block types
            block_types = [block.get('type', 'unknown') for block in response['blocks']]
            print(f"🎨 Block types: {', '.join(block_types)}")
            
        else:
            print(f"⚠️  OpenAI response doesn't have expected structure")
            print(f"📄 Response keys: {list(response.keys())}")
            
    except Exception as e:
        print(f"❌ Direct test error: {e}")

if __name__ == "__main__":
    demo_fallback_integration()
    test_openai_fallback_directly()


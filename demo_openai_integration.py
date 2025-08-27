#!/usr/bin/env python3
"""
Demo script for OpenAI integration with Google Ads analysis
This script demonstrates how OpenAI generates dynamic responses for all analysis actions
"""

import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

def demo_openai_integration():
    """Demo the OpenAI integration with Google Ads analysis"""
    
    print("🚀 OpenAI Integration Demo for Google Ads Analysis")
    print("=" * 60)
    
    try:
        from google_ads_new.openai_service import GoogleAdsOpenAIService
        from google_ads_new.data_service import GoogleAdsDataService
        from django.contrib.auth.models import User
        
        # Get a test user (you'll need to create one or use an existing one)
        try:
            user = User.objects.first()
            if not user:
                print("❌ No users found. Please create a user first.")
                return
        except Exception as e:
            print(f"❌ Error getting user: {e}")
            return
        
        print(f"✅ Using user: {user.username}")
        
        # Initialize services
        try:
            openai_service = GoogleAdsOpenAIService()
            print("✅ OpenAI service initialized successfully")
        except ValueError as e:
            print(f"❌ OpenAI service initialization failed: {e}")
            print("💡 Please set your OPENAI_API_KEY in the .env file")
            print("   Example: OPENAI_API_KEY=your_actual_key_here")
            return
        
        data_service = GoogleAdsDataService(user)
        print("✅ Data service initialized successfully")
        
        # Demo data fetching
        print("\n📊 Fetching Real Campaign Data...")
        campaign_data = data_service.get_campaign_data()
        
        if "error" in campaign_data:
            print(f"❌ Error fetching campaign data: {campaign_data['error']}")
            print("💡 This might be because no Google Ads accounts are connected yet.")
            print("   The system will still work with mock data for demonstration.")
            
            # Use mock data for demo
            campaign_data = {
                "account_name": "Demo Account",
                "campaigns_count": 3,
                "ad_groups_count": 8,
                "campaigns": [
                    {"campaign_name": "Brand Awareness", "campaign_status": "ENABLED", "budget_amount": 1000},
                    {"campaign_name": "Product Sales", "campaign_status": "ENABLED", "budget_amount": 2000},
                    {"campaign_name": "Lead Generation", "campaign_status": "PAUSED", "budget_amount": 500}
                ],
                "ad_groups": [
                    {"ad_group_name": "Primary Keywords", "campaign__campaign_name": "Brand Awareness"},
                    {"ad_group_name": "Secondary Keywords", "campaign__campaign_name": "Brand Awareness"},
                    {"ad_group_name": "Product Specific", "campaign__campaign_name": "Product Sales"}
                ]
            }
        
        print(f"✅ Campaign data: {campaign_data['campaigns_count']} campaigns, {campaign_data['ad_groups_count']} ad groups")
        
        # Demo OpenAI analysis
        print("\n🤖 Generating OpenAI Analysis...")
        print("   This will call the OpenAI API to generate dynamic responses.")
        print("   Make sure you have set your OPENAI_API_KEY in the environment.")
        
        # Test different analysis types
        analysis_actions = [
            "CHECK_CAMPAIGN_CONSISTENCY",
            "CHECK_SITELINKS", 
            "ANALYZE_AUDIENCE",
            "OPTIMIZE_CAMPAIGN"
        ]
        
        for action in analysis_actions:
            print(f"\n🔍 Testing: {action}")
            try:
                response = openai_service.generate_analysis_response(
                    action, 
                    campaign_data,
                    f"Demo analysis for {action}"
                )
                
                if "blocks" in response:
                    print(f"   ✅ Generated {len(response['blocks'])} UI blocks")
                    print(f"   📝 Response type: {response.get('data_source', 'unknown')}")
                    
                    # Show block types
                    block_types = [block.get('type', 'unknown') for block in response['blocks']]
                    print(f"   🎨 Block types: {', '.join(block_types)}")
                    
                    # Show sample content
                    for i, block in enumerate(response['blocks'][:2]):  # Show first 2 blocks
                        block_type = block.get('type', 'unknown')
                        if block_type == 'text':
                            content = block.get('content', '')[:100] + '...' if len(block.get('content', '')) > 100 else block.get('content', '')
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
                    print(f"   ❌ Unexpected response format: {list(response.keys())}")
                    
            except Exception as e:
                            print(f"   ❌ Error generating analysis: {e}")
            print("   💡 This might be due to missing OpenAI API key or API limits.")
            print("   💡 Check that OPENAI_API_KEY is set in your .env file")
        
        print("\n🎯 OpenAI Integration Features:")
        print("   ✅ Dynamic response generation based on real data")
        print("   ✅ Multiple UI block types (charts, tables, lists, actions)")
        print("   ✅ Context-aware analysis for each action type")
        print("   ✅ Real-time data integration")
        print("   ✅ Fallback responses when OpenAI is unavailable")
        
        print("\n🔧 Setup Instructions:")
        print("   1. Get OpenAI API key from https://platform.openai.com/api-keys")
        print("   2. Create .env file: cp env_template.txt .env")
        print("   3. Edit .env with your API key: OPENAI_API_KEY=your_actual_key")
        print("   4. Install requirements: pip install -r requirements.txt")
        
        print("\n📱 Frontend Integration:")
        print("   ✅ AnalysisBlock component handles all response types")
        print("   ✅ Automatic rendering of charts, tables, lists, and actions")
        print("   ✅ Responsive design for all device types")
        print("   ✅ Error handling and fallback displays")
        
        print("\n🚀 Ready to use! The system now generates dynamic, AI-powered")
        print("   responses for all Google Ads analysis actions.")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all required packages are installed:")
        print("   pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("💡 Check the Django setup and database connection")

if __name__ == "__main__":
    demo_openai_integration()

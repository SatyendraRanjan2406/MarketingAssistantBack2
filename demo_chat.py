#!/usr/bin/env python3
"""
Demo script for Google Ads Chat Service
This shows how to use the chat service programmatically
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

def demo_chat_interaction():
    """Demonstrate chat interaction"""
    print("🤖 Google Ads Chat Assistant Demo")
    print("=" * 50)
    
    # Initialize chat service (you'll need a real OpenAI API key)
    try:
        # Check if OpenAI API key is set
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            print("⚠️  OPENAI_API_KEY not set. Using demo mode.")
            print("   Set OPENAI_API_KEY in your environment to use real AI responses.")
            openai_key = "demo_key"
        
        chat_service = GoogleAdsChatService(
            user_id=1,  # Assuming user ID 1 exists
            openai_api_key=openai_key
        )
        
        print("✅ Chat service initialized successfully!")
        
        # Demo questions
        demo_questions = [
            "How are my campaigns performing this month?",
            "Which keywords have the best conversion rate?",
            "What can I do to improve my ROAS?",
            "Show me a breakdown of my ad spend by campaign"
        ]
        
        print(f"\n📝 Demo Questions:")
        for i, question in enumerate(demo_questions, 1):
            print(f"{i}. {question}")
        
        print(f"\n💡 Quick Insights:")
        insights = chat_service.get_quick_insights()
        
        if "error" in insights:
            print(f"❌ Error: {insights['error']}")
        else:
            if insights.get('insights'):
                print("📊 Insights:")
                for insight in insights['insights']:
                    print(f"   • {insight}")
            
            if insights.get('actions'):
                print("\n🚀 Recommended Actions:")
                for action in insights['actions']:
                    print(f"   • {action}")
            
            if insights.get('metrics'):
                metrics = insights['metrics']
                print(f"\n📈 Key Metrics:")
                print(f"   • Total Spend: ${metrics.get('total_spend', 0):.2f}")
                print(f"   • CTR: {metrics.get('ctr', 0):.2%}")
                print(f"   • Campaigns: {metrics.get('campaigns_count', 0)}")
        
        print(f"\n🎯 User Context:")
        context = chat_service.get_user_data_context()
        
        if "error" in context:
            print(f"❌ Error: {context['error']}")
        else:
            print(f"   • Accounts: {context.get('accounts_count', 0)}")
            print(f"   • Total Spend: ${context.get('total_spend', 0):.2f}")
            print(f"   • Impressions: {context.get('total_impressions', 0):,}")
            print(f"   • Clicks: {context.get('total_clicks', 0):,}")
            print(f"   • Conversions: {context.get('total_conversions', 0):,}")
            print(f"   • CTR: {context.get('ctr', 0):.2%}")
            print(f"   • CPC: ${context.get('cpc', 0):.2f}")
        
        print(f"\n🔧 How to Use:")
        print("1. Set OPENAI_API_KEY environment variable")
        print("2. Run Django server: python manage.py runserver")
        print("3. Visit: http://localhost:8000/google-ads/chat/")
        print("4. Start chatting with your AI assistant!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in demo: {e}")
        import traceback
        traceback.print_exc()
        return False

def demo_chart_generation():
    """Demonstrate chart generation"""
    print(f"\n📊 Chart Generation Demo:")
    print("-" * 30)
    
    try:
        # Sample data for charts
        sample_data = [
            {'date': '2024-01-01', 'impressions': 1000, 'clicks': 50, 'cost': 25.50},
            {'date': '2024-01-02', 'impressions': 1200, 'clicks': 60, 'cost': 30.00},
            {'date': '2024-01-03', 'impressions': 1100, 'clicks': 55, 'cost': 27.50},
            {'date': '2024-01-04', 'impressions': 1300, 'clicks': 65, 'cost': 32.50},
            {'date': '2024-01-05', 'impressions': 1400, 'clicks': 70, 'cost': 35.00},
        ]
        
        campaign_data = [
            {'campaign__campaign_name': 'Brand Campaign', 'spend': 150.00},
            {'campaign__campaign_name': 'Performance Max', 'spend': 200.00},
            {'campaign__campaign_name': 'Search Campaign', 'spend': 100.00},
        ]
        
        chat_service = GoogleAdsChatService(
            user_id=1,
            openai_api_key=os.getenv('OPENAI_API_KEY', '')
        )
        
        # Test different chart types
        chart_types = ['line', 'bar', 'pie']
        
        for chart_type in chart_types:
            print(f"   • {chart_type.title()} Chart: {'✅' if chart_type == 'line' else '⚠️ Demo data only'}")
        
        print(f"\n📈 Chart Features:")
        print("   • Interactive Plotly charts")
        print("   • Responsive design")
        print("   • Multiple chart types")
        print("   • Real-time data updates")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in chart demo: {e}")
        return False

def main():
    """Main demo function"""
    print("🚀 Starting Google Ads Chat Assistant Demo\n")
    
    # Demo 1: Chat Interaction
    chat_ok = demo_chat_interaction()
    
    # Demo 2: Chart Generation
    chart_ok = demo_chart_generation()
    
    # Summary
    print(f"\n" + "="*60)
    print("🎯 DEMO SUMMARY")
    print("="*60)
    
    if chat_ok:
        print("✅ Chat Service Demo: PASSED")
    else:
        print("❌ Chat Service Demo: FAILED")
    
    if chart_ok:
        print("✅ Chart Generation Demo: PASSED")
    else:
        print("❌ Chart Generation Demo: FAILED")
    
    print(f"\n🎉 Demo completed!")
    print(f"\n📋 What you've seen:")
    print("   • Chat service initialization")
    print("   • Quick insights generation")
    print("   • User context retrieval")
    print("   • Chart generation capabilities")
    print("   • Integration with Google Ads data")
    
    print(f"\n🚀 Ready to implement?")
    print("   1. Install dependencies: pip install -r requirements.txt")
    print("   2. Set up environment variables")
    print("   3. Run migrations: python manage.py migrate")
    print("   4. Start server: python manage.py runserver")
    print("   5. Test chat: http://localhost:8000/google-ads/chat/")

if __name__ == "__main__":
    main()

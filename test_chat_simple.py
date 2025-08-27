#!/usr/bin/env python3
"""
Simple test script for Google Ads Chat Service
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

# Now import the chat service
from google_ads_app.chat_service import GoogleAdsChatService

def test_chat_service():
    """Test the chat service functionality"""
    print("🧪 Testing Google Ads Chat Service...")
    
    try:
        # Test without API key
        print("1. Testing without OpenAI API key...")
        chat_service = GoogleAdsChatService(user_id=1)
        
        # Test quick insights
        insights = chat_service.get_quick_insights()
        print(f"   ✅ Quick insights: {insights}")
        
        # Test chat without API key
        response = chat_service.chat("Hello")
        print(f"   ✅ Chat response: {response}")
        
        # Test with environment API key
        print("\n2. Testing with environment API key...")
        chat_service_with_key = GoogleAdsChatService(user_id=1, openai_api_key=os.getenv('OPENAI_API_KEY', ''))
        
        # This should fail gracefully
        try:
            response = chat_service_with_key.chat("Hello")
            print(f"   ✅ Chat response: {response}")
        except Exception as e:
            print(f"   ⚠️  Expected error with dummy key: {e}")
        
        print("\n🎉 Chat service test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing chat service: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_chat_service()

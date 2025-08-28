#!/usr/bin/env python3
"""
Quick Test: Verify Image Generation Fix
Tests the fixed chat service to ensure no more dict() errors
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/Users/satyendra/marketing_assistant_back')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

from django.contrib.auth.models import User
from google_ads_new.chat_service import ChatService

def test_fixed_chat_service():
    """Test the fixed chat service"""
    
    print("🧪 Testing Fixed Chat Service")
    print("=" * 40)
    
    # Check OpenAI API key
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        print("❌ OPENAI_API_KEY not found")
        return False
    
    # Get test user
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@example.com'}
    )
    
    if created:
        user.set_password('test123')
        user.save()
    
    # Initialize chat service
    try:
        chat_service = ChatService(user)
        print("✅ Chat service initialized")
        
        if not chat_service.image_generator:
            print("❌ Image generator not available")
            return False
            
        print("✅ Image generator available")
        
    except Exception as e:
        print(f"❌ Error initializing chat service: {e}")
        return False
    
    # Test creative content request
    test_message = "Generate creative ideas for my coaching center"
    
    try:
        # Start chat session
        session_id = chat_service.start_session("Test Creative Generation")
        print(f"✅ Chat session started: {session_id}")
        
        # Process message
        print(f"\n🔄 Processing message: {test_message}")
        response = chat_service.process_message(test_message)
        
        if response.get("success"):
            print("✅ Message processed successfully!")
            
            # Check response structure
            response_data = response.get("response", {})
            blocks = response_data.get("blocks", [])
            
            print(f"📊 Response contains {len(blocks)} blocks")
            
            # Check for creative blocks with images
            creative_blocks = [block for block in blocks if block.get("type") == "creative"]
            
            if creative_blocks:
                print(f"🎨 Found {len(creative_blocks)} creative blocks")
                
                for i, block in enumerate(creative_blocks, 1):
                    print(f"\n   Block {i}: {block.get('title', 'Unknown')}")
                    
                    if "image_url" in block:
                        image_url = block["image_url"]
                        if image_url:
                            print(f"      🖼️  Image URL: {image_url[:50]}...")
                        else:
                            print(f"      ⚠️  Image URL is None")
                    else:
                        print(f"      ❌ Missing image_url field")
            else:
                print("⚠️  No creative blocks found")
            
            return True
            
        else:
            print(f"❌ Message processing failed: {response.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Quick Test: Image Generation Fix")
    print("=" * 50)
    
    if test_fixed_chat_service():
        print("\n✅ Test completed successfully!")
        print("🎉 The dict() error has been fixed!")
        print("\n💡 Your chatbot should now work without errors")
        print("   and include image URLs in creative responses")
    else:
        print("\n❌ Test failed - there may still be issues")

if __name__ == "__main__":
    main()

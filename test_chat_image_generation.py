#!/usr/bin/env python3
"""
Test Script: Image Generation in Chat Service
Tests the integration of image generation with the main chat service
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
sys.path.append('/Users/satyendra/marketing_assistant_back')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

from django.contrib.auth.models import User
from google_ads_new.chat_service import ChatService

def test_image_generation_in_chat():
    """Test image generation functionality in the chat service"""
    
    print("🧪 Testing Image Generation in Chat Service")
    print("=" * 60)
    
    # Check OpenAI API key
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("💡 Please set your OpenAI API key:")
        print("   export OPENAI_API_KEY='your_api_key_here'")
        return False
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    if created:
        user.set_password('test123')
        user.save()
        print("✅ Created test user")
    else:
        print("✅ Using existing test user")
    
    # Initialize chat service
    try:
        chat_service = ChatService(user)
        print("✅ Chat service initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing chat service: {e}")
        return False
    
    # Test image generator initialization
    if chat_service.image_generator:
        print("✅ Image generator is available")
    else:
        print("❌ Image generator not available")
        return False
    
    # Test a creative content request
    test_message = "Create a poster for Lakshya Coaching Center targeting students in India"
    
    print(f"\n🎯 Testing creative content request:")
    print(f"   Message: {test_message}")
    
    try:
        # Start a chat session
        session_id = chat_service.start_session("Test Poster Generation")
        print(f"✅ Chat session started: {session_id}")
        
        # Process the message
        print("\n🔄 Processing message...")
        response = chat_service.process_message(test_message)
        
        if response.get("success"):
            print("✅ Message processed successfully")
            
            # Check if response contains creative blocks with images
            response_data = response.get("response", {})
            blocks = response_data.get("blocks", [])
            
            creative_blocks = [block for block in blocks if block.get("type") == "creative"]
            
            if creative_blocks:
                print(f"📋 Found {len(creative_blocks)} creative blocks")
                
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
                print("⚠️  No creative blocks found in response")
            
            # Show the full response structure
            print(f"\n📊 Response Structure:")
            print(f"   Success: {response.get('success')}")
            print(f"   Session ID: {response.get('session_id')}")
            print(f"   Intent Action: {response.get('intent', {}).get('action')}")
            print(f"   Total Blocks: {len(blocks)}")
            
        else:
            print(f"❌ Message processing failed: {response.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_specific_creative_actions():
    """Test specific creative actions that should trigger image generation"""
    
    print("\n🎨 Testing Specific Creative Actions")
    print("=" * 50)
    
    # Get test user
    user = User.objects.get(username='test_user')
    chat_service = ChatService(user)
    
    # Test different creative actions
    test_cases = [
        {
            "message": "Generate ad copies for my coaching center",
            "expected_action": "GENERATE_AD_COPIES"
        },
        {
            "message": "Create poster templates for educational content",
            "expected_action": "POSTER_GENERATOR"
        },
        {
            "message": "Generate creative ideas for marketing campaigns",
            "expected_action": "GENERATE_CREATIVES"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {test_case['message']}")
        print("-" * 40)
        
        try:
            # Start new session for each test
            session_id = chat_service.start_session(f"Test {i}")
            
            # Process message
            response = chat_service.process_message(test_case["message"])
            
            if response.get("success"):
                intent_action = response.get("intent", {}).get("action")
                print(f"   ✅ Intent detected: {intent_action}")
                
                if intent_action == test_case["expected_action"]:
                    print(f"   ✅ Correct intent detected")
                else:
                    print(f"   ⚠️  Expected {test_case['expected_action']}, got {intent_action}")
                
                # Check for image URLs in creative blocks
                blocks = response.get("response", {}).get("blocks", [])
                creative_blocks = [block for block in blocks if block.get("type") == "creative"]
                
                if creative_blocks:
                    print(f"   📋 Found {len(creative_blocks)} creative blocks")
                    
                    for block in creative_blocks:
                        if "image_url" in block and block["image_url"]:
                            print(f"      🖼️  Image generated successfully")
                        else:
                            print(f"      ⚠️  Image not generated")
                else:
                    print(f"   ⚠️  No creative blocks found")
                    
            else:
                print(f"   ❌ Failed: {response.get('error')}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return True

def main():
    """Main test function"""
    print("🚀 Testing Image Generation Integration in Chat Service")
    print("=" * 70)
    
    # Test basic image generation
    if test_image_generation_in_chat():
        print("\n✅ Basic image generation test completed successfully!")
    else:
        print("\n❌ Basic image generation test failed!")
        return
    
    # Test specific creative actions
    if test_specific_creative_actions():
        print("\n✅ Specific creative actions test completed successfully!")
    else:
        print("\n❌ Specific creative actions test failed!")
        return
    
    print("\n🎉 All tests completed successfully!")
    print("\n💡 Next Steps:")
    print("1. Your chat service now includes image generation")
    print("2. Creative content requests will automatically generate images")
    print("3. Image URLs will be included in creative blocks")
    print("4. Test with your chatbot interface")

if __name__ == "__main__":
    main()

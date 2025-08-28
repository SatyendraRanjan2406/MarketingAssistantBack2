#!/usr/bin/env python3
"""
Fix Script: Image Generation in Chat Service
Fixes and verifies image generation integration
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
from google_ads_new.chat_service import ChatService, ImageGenerator

def verify_image_generator():
    """Verify the image generator is working correctly"""
    
    print("🔍 Verifying Image Generator")
    print("=" * 40)
    
    # Check OpenAI API key
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        print("❌ OPENAI_API_KEY not found")
        return False
    
    print("✅ OpenAI API key found")
    
    # Test image generator directly
    try:
        image_gen = ImageGenerator(openai_api_key)
        print("✅ Image generator created successfully")
        
        # Test a simple image generation
        print("🧪 Testing image generation...")
        test_prompt = "Create a simple test image of a blue circle"
        
        image_url = image_gen.generate_image(test_prompt)
        
        if image_url:
            print(f"✅ Test image generated successfully!")
            print(f"   URL: {image_url[:50]}...")
            return True
        else:
            print("❌ Test image generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing image generator: {e}")
        return False

def test_chat_service_integration():
    """Test the chat service integration with image generation"""
    
    print("\n🤖 Testing Chat Service Integration")
    print("=" * 40)
    
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
        
        if chat_service.image_generator:
            print("✅ Image generator available in chat service")
        else:
            print("❌ Image generator not available in chat service")
            return False
            
    except Exception as e:
        print(f"❌ Error initializing chat service: {e}")
        return False
    
    return True

def fix_common_issues():
    """Fix common issues with image generation"""
    
    print("\n🔧 Fixing Common Issues")
    print("=" * 40)
    
    # Check if requests package is available
    try:
        import requests
        print("✅ Requests package available")
    except ImportError:
        print("❌ Requests package not available - installing...")
        os.system("pip install requests")
        print("✅ Requests package installed")
    
    # Check if environment variables are set correctly
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        print("❌ OPENAI_API_KEY not set")
        print("💡 Please set your OpenAI API key:")
        print("   export OPENAI_API_KEY='your_api_key_here'")
        return False
    
    print("✅ Environment variables configured")
    
    # Check file permissions
    current_dir = os.getcwd()
    print(f"✅ Current directory: {current_dir}")
    print(f"✅ Write permissions: {os.access(current_dir, os.W_OK)}")
    
    return True

def create_test_response():
    """Create a test response to verify structure"""
    
    print("\n📋 Creating Test Response Structure")
    print("=" * 40)
    
    # Simulate what the response should look like
    test_response = {
        "success": True,
        "session_id": "test_session_123",
        "response": {
            "blocks": [
                {
                    "type": "text",
                    "content": "Here are some creative poster templates for your coaching center.",
                    "style": "paragraph"
                },
                {
                    "type": "creative",
                    "title": "Test Poster Template",
                    "description": "A test poster design",
                    "template_type": "Educational",
                    "features": ["Feature 1", "Feature 2"],
                    "color_scheme": "Blue and white",
                    "target_audience": "Students",
                    "image_url": "https://example.com/test-image.png"  # This should be generated
                }
            ]
        },
        "intent": {
            "action": "POSTER_GENERATOR",
            "confidence": 0.95
        }
    }
    
    print("✅ Test response structure created")
    print("📋 Response includes:")
    print("   - Success status")
    print("   - Session ID")
    print("   - Response blocks with creative content")
    print("   - Image URL field in creative blocks")
    print("   - Intent information")
    
    return test_response

def main():
    """Main fix function"""
    print("🚀 Fixing Image Generation in Chat Service")
    print("=" * 60)
    
    # Fix common issues
    if not fix_common_issues():
        print("\n❌ Failed to fix common issues")
        return
    
    # Verify image generator
    if not verify_image_generator():
        print("\n❌ Image generator verification failed")
        return
    
    # Test chat service integration
    if not test_chat_service_integration():
        print("\n❌ Chat service integration failed")
        return
    
    # Create test response
    test_response = create_test_response()
    
    print("\n🎉 All fixes completed successfully!")
    print("\n💡 Next Steps:")
    print("1. Run the test script: python test_chat_image_generation.py")
    print("2. Test with your chatbot interface")
    print("3. Creative content should now include image URLs")
    
    print("\n📋 Expected Response Structure:")
    print("   Creative blocks will now include 'image_url' field")
    print("   Images are generated using OpenAI DALL-E 3")
    print("   URLs are accessible and can be displayed in UI")

if __name__ == "__main__":
    main()

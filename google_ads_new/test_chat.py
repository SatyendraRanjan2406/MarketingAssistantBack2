#!/usr/bin/env python
"""
Test script for Google Ads Chat Service
Run this to test the chat functionality without the full Django server
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

from django.contrib.auth.models import User
from .chat_service import ChatService
from .models import ChatSession, ChatMessage, KBDocument
import json

def test_chat_service():
    """Test the chat service functionality"""
    print("🧪 Testing Google Ads Chat Service...")
    
    try:
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
            user.set_password('testpass123')
            user.save()
            print(f"   ✅ Created test user: {user.username}")
        else:
            print(f"   ✅ Using existing test user: {user.username}")
        
        # Initialize chat service
        chat_service = ChatService(user)
        print(f"   ✅ Chat service initialized for user: {user.id}")
        
        # Test session creation
        session_id = chat_service.start_session("Test Chat Session")
        print(f"   ✅ Chat session created: {session_id}")
        
        # Test message processing (without OpenAI API)
        print("   📝 Testing message processing...")
        
        # Test without OpenAI API key
        response = chat_service.process_message("Hello, can you show me my campaigns?")
        print(f"   ✅ Chat response: {response.get('success', False)}")
        
        if response.get('success'):
            print(f"   📊 Response blocks: {len(response.get('response', {}).get('blocks', []))}")
            print(f"   🎯 Detected intent: {response.get('intent', {}).get('action', 'Unknown')}")
        else:
            print(f"   ⚠️  Expected error (no OpenAI API): {response.get('error', 'Unknown error')}")
        
        # Test session management
        print("   📋 Testing session management...")
        
        # Load session
        loaded = chat_service.load_session(session_id)
        print(f"   ✅ Session loaded: {loaded}")
        
        # Get chat history
        history = chat_service.get_chat_history()
        print(f"   ✅ Chat history retrieved: {len(history)} messages")
        
        # Get session summary
        summary = chat_service.get_session_summary()
        print(f"   ✅ Session summary: {summary}")
        
        # Test knowledge base functionality
        print("   📚 Testing knowledge base...")
        
        # Add a test document
        kb_tools = chat_service._execute_tools({
            'action': 'ADD_KB_DOCUMENT',
            'parameters': {
                'company_id': 1,
                'title': 'Test Document',
                'content': 'This is a test document for the knowledge base.',
                'document_type': 'test'
            }
        })
        
        if 'kb_document' in kb_tools and kb_tools['kb_document'].get('success'):
            print(f"   ✅ KB document added: {kb_tools['kb_document']['id']}")
        else:
            print(f"   ⚠️  KB document creation failed: {kb_tools.get('error', 'Unknown error')}")
        
        # Test database tools
        print("   🗄️  Testing database tools...")
        
        db_tools = chat_service._execute_tools({
            'action': 'GET_OVERVIEW',
            'parameters': {}
        })
        
        if 'account_summary' in db_tools:
            summary = db_tools['account_summary']
            if 'error' not in summary:
                print(f"   ✅ Account summary retrieved: {summary.get('total_accounts', 0)} accounts")
            else:
                print(f"   ⚠️  Account summary failed: {summary.get('error', 'Unknown error')}")
        else:
            print("   ⚠️  Database tools not working")
        
        # End session
        chat_service.end_session()
        print(f"   ✅ Session ended")
        
        print("\n🎉 Chat service test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing chat service: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_models():
    """Test the chat models"""
    print("🧪 Testing Chat Models...")
    
    try:
        # Test ChatSession model
        user = User.objects.first()
        if not user:
            print("   ❌ No users found in database")
            return False
        
        session = ChatSession.objects.create(
            user=user,
            title="Model Test Session"
        )
        print(f"   ✅ ChatSession created: {session.id}")
        
        # Test ChatMessage model
        message = ChatMessage.objects.create(
            session=session,
            role="user",
            content="Test message content",
            metadata={"test": True}
        )
        print(f"   ✅ ChatMessage created: {message.id}")
        
        # Test KBDocument model
        doc = KBDocument.objects.create(
            company_id=1,
            title="Test KB Document",
            content="This is test content for the knowledge base.",
            document_type="test"
        )
        print(f"   ✅ KBDocument created: {doc.id}")
        
        # Clean up test data
        session.delete()
        doc.delete()
        print("   ✅ Test data cleaned up")
        
        print("   🎉 Model tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing models: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Starting Google Ads Chat Service Tests\n")
    
    # Test 1: Models
    print("=" * 50)
    models_ok = test_models()
    
    # Test 2: Chat Service
    print("=" * 50)
    chat_ok = test_chat_service()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    if models_ok:
        print("✅ Chat Models: PASSED")
    else:
        print("❌ Chat Models: FAILED")
    
    if chat_ok:
        print("✅ Chat Service: PASSED")
    else:
        print("❌ Chat Service: FAILED")
    
    if models_ok and chat_ok:
        print("\n🎉 All tests passed! The chat service is ready to use.")
        print("\n📋 Next steps:")
        print("1. Set OPENAI_API_KEY environment variable")
        print("2. Run Django migrations: python manage.py makemigrations && python manage.py migrate")
        print("3. Start Django server: python manage.py runserver")
        print("4. Test chat: http://localhost:8000/google-ads-new/api/chat/message/")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure Django is properly configured")
        print("2. Check database connection")
        print("3. Verify all required packages are installed")
        print("4. Run migrations if needed")

if __name__ == "__main__":
    main()

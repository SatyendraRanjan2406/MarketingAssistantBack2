#!/usr/bin/env python3
"""
Simple test to check if the basic ChatService works
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

from django.contrib.auth.models import User
from google_ads_new.chat_service import ChatService

def test_simple_chat():
    """Test the basic chat service"""
    try:
        # Get a user
        user = User.objects.get(id=25)
        print(f"✅ Using user: {user.username}")
        
        # Initialize chat service
        print("🔧 Initializing ChatService...")
        chat_service = ChatService(user)
        print("✅ ChatService initialized")
        
        # Test with a simple message
        message = "What is the weather like today?"
        
        print(f"📝 Processing message: '{message}'")
        result = chat_service.process_message(message)
        
        print("✅ Message processed successfully")
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_chat()

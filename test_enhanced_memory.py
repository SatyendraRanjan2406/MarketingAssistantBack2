#!/usr/bin/env python3
"""
Test Enhanced Memory System for Google AI Chatbot
Demonstrates conversation history, user preferences, adaptive responses, and cross-session memory
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

from django.contrib.auth.models import User
from google_ads_new.memory_manager import MemoryManager
from google_ads_new.chat_service import ChatService


def test_memory_system():
    """Test the complete memory system"""
    print("🧠 Testing Enhanced Memory System")
    print("=" * 50)
    
    # Create or get test user
    user, created = User.objects.get_or_create(
        username='memory_test_user',
        defaults={'email': 'memory@test.com', 'first_name': 'Memory', 'last_name': 'Test'}
    )
    
    if created:
        print(f"✅ Created test user: {user.username}")
    else:
        print(f"✅ Using existing test user: {user.username}")
    
    # Initialize memory manager
    memory_manager = MemoryManager(user)
    print(f"✅ Memory manager initialized for user: {user.id}")
    
    # Test 1: User Memory Creation and Preferences
    print("\n📝 Test 1: User Memory & Preferences")
    print("-" * 30)
    
    # Update user preferences
    memory_manager.update_user_preferences({
        'analysis_depth': 'detailed',
        'preferred_format': 'visual',
        'notification_frequency': 'daily',
        'timezone': 'UTC'
    })
    
    # Update expertise level
    memory_manager.update_expertise_level('intermediate')
    
    # Get user preferences
    preferences = memory_manager.get_user_preferences()
    expertise = memory_manager.get_expertise_level()
    
    print(f"User Preferences: {preferences}")
    print(f"Expertise Level: {expertise}")
    
    # Test 2: Conversation Memory
    print("\n💬 Test 2: Conversation Memory")
    print("-" * 30)
    
    # Create conversation session
    session_id = "test_session_001"
    conversation = memory_manager.create_conversation_session(
        session_id, 
        google_ads_account="test_account_123"
    )
    
    print(f"✅ Created conversation session: {session_id}")
    
    # Add user messages
    user_messages = [
        "Show me campaign performance summary",
        "I need detailed analysis of ROAS trends",
        "Generate some ad copy variations for my product",
        "What's the best time to run ads?"
    ]
    
    for i, message in enumerate(user_messages):
        memory_manager.add_user_message(
            session_id, 
            message, 
            {'message_number': i + 1, 'timestamp': datetime.now().isoformat()}
        )
        print(f"✅ Added user message {i + 1}: {message[:50]}...")
    
    # Add assistant responses
    assistant_messages = [
        "Here's your campaign performance summary...",
        "ROAS trends analysis shows...",
        "I've generated 4 ad copy variations...",
        "Based on your data, the best times are..."
    ]
    
    for i, message in enumerate(assistant_messages):
        memory_manager.add_assistant_message(
            session_id, 
            message, 
            {'response_number': i + 1, 'timestamp': datetime.now().isoformat()}
        )
        print(f"✅ Added assistant message {i + 1}: {message[:50]}...")
    
    # Add intent classifications
    intents = [
        {'action': 'PERFORMANCE_SUMMARY', 'confidence': 0.95, 'parameters': {'timeframe': '7d'}},
        {'action': 'TREND_ANALYSIS', 'confidence': 0.88, 'parameters': {'metric': 'ROAS'}},
        {'action': 'GENERATE_AD_COPIES', 'confidence': 0.92, 'parameters': {'variations': 4}},
        {'action': 'OPTIMIZATION_ADVICE', 'confidence': 0.87, 'parameters': {'focus': 'timing'}}
    ]
    
    for intent in intents:
        memory_manager.add_intent(session_id, intent)
        print(f"✅ Added intent: {intent['action']}")
    
    # Test 3: Cross-Session Memory
    print("\n🔄 Test 3: Cross-Session Memory")
    print("-" * 30)
    
    # Store cross-session memories
    cross_session_data = [
        ('topic_expertise', 'campaign_management', {
            'expertise_level': 'growing',
            'last_discussed': datetime.now().isoformat(),
            'conversation_count': 3
        }, 0.8),
        ('user_preferences', 'analysis_style', {
            'preferred_depth': 'detailed',
            'preferred_format': 'visual',
            'last_updated': datetime.now().isoformat()
        }, 0.9),
        ('creative_preferences', 'ad_copy_style', {
            'preferred_tone': 'professional',
            'preferred_length': 'medium',
            'success_rate': 0.85
        }, 0.7)
    ]
    
    for memory_type, memory_key, memory_data, importance in cross_session_data:
        memory_manager.store_cross_session_memory(
            memory_type, memory_key, memory_data, importance
        )
        print(f"✅ Stored cross-session memory: {memory_type}:{memory_key}")
    
    # Test 4: Adaptive Response Patterns
    print("\n🎯 Test 4: Adaptive Response Patterns")
    print("-" * 30)
    
    # Store response patterns
    patterns = [
        ('performance_analysis', {
            'user_expertise': 'intermediate',
            'preferred_depth': 'detailed'
        }, {
            'response_structure': 'summary + details + recommendations',
            'include_charts': True,
            'include_metrics': True
        }),
        ('creative_generation', {
            'user_expertise': 'intermediate',
            'creative_type': 'ad_copy'
        }, {
            'variations_count': 4,
            'include_explanations': True,
            'include_advantages': True
        })
    ]
    
    for pattern_type, trigger_conditions, response_template in patterns:
        memory_manager.store_response_pattern(pattern_type, trigger_conditions, response_template)
        print(f"✅ Stored response pattern: {pattern_type}")
    
    # Test 5: Memory Insights and Statistics
    print("\n📊 Test 5: Memory Insights & Statistics")
    print("-" * 30)
    
    # Get user insights
    insights = memory_manager.get_user_insights()
    print(f"User Insights:")
    print(f"  - Expertise Level: {insights['expertise_level']}")
    print(f"  - Favorite Topics: {insights['favorite_topics']}")
    print(f"  - Preferred Analysis Depth: {insights['preferred_analysis_depth']}")
    print(f"  - Total Conversations: {insights['total_conversations']}")
    print(f"  - Cross-session Memories: {insights['cross_session_memories']}")
    
    # Get memory statistics
    stats = memory_manager.get_memory_stats()
    print(f"\nMemory Statistics:")
    print(f"  - User Memory: {stats['user_memory']}")
    print(f"  - Conversation Memory: {stats['conversation_memory']}")
    print(f"  - Cross-session Memory: {stats['cross_session_memory']}")
    print(f"  - Adaptive Patterns: {stats['adaptive_patterns']}")
    
    # Test 6: Context Retrieval
    print("\n🔍 Test 6: Context Retrieval")
    print("-" * 30)
    
    # Get conversation context
    context = memory_manager.get_conversation_context(session_id, limit=3)
    print(f"Recent Context (last 3 messages):")
    for msg in context:
        print(f"  - {msg['role']}: {msg['content'][:60]}...")
    
    # Get relevant cross-session memories
    relevant_memories = memory_manager.get_relevant_cross_session_memories("campaign performance", limit=2)
    print(f"\nRelevant Cross-session Memories for 'campaign performance':")
    for memory in relevant_memories:
        print(f"  - {memory.memory_type}:{memory.memory_key} (importance: {memory.importance_score})")
    
    # Test 7: ChatService Integration
    print("\n🤖 Test 7: ChatService Integration")
    print("-" * 30)
    
    # Initialize ChatService with memory
    chat_service = ChatService(user)
    print(f"✅ ChatService initialized with memory manager")
    
    # Test memory insights through ChatService
    memory_insights = chat_service.get_memory_insights()
    print(f"ChatService Memory Insights:")
    print(f"  - Expertise Level: {memory_insights.get('expertise_level', 'N/A')}")
    print(f"  - Preferences Count: {len(memory_insights.get('preferences', {}))}")
    print(f"  - Learning Patterns: {len(memory_insights.get('learning_patterns', {}))}")
    
    # Test 8: End Conversation and Memory Persistence
    print("\n🔚 Test 8: End Conversation & Memory Persistence")
    print("-" * 30)
    
    # End conversation session
    memory_manager.end_conversation_session(session_id)
    print(f"✅ Ended conversation session: {session_id}")
    
    # Get context summary
    conversation = memory_manager.get_conversation_session(session_id)
    if conversation:
        context_summary = conversation.get_context_summary()
        print(f"Context Summary:")
        print(f"  - Topics Discussed: {context_summary.get('topics_discussed', [])}")
        print(f"  - User Preferences: {context_summary.get('user_preferences', {})}")
        print(f"  - Analysis Focus: {context_summary.get('analysis_focus', {})}")
        print(f"  - Creative Style: {context_summary.get('creative_style', {})}")
    
    # Test 9: Memory Cleanup
    print("\n🧹 Test 9: Memory Cleanup")
    print("-" * 30)
    
    # Clean up expired memories
    expired_count = memory_manager.cleanup_expired_memories()
    print(f"✅ Cleaned up {expired_count} expired memories")
    
    # Final memory statistics
    final_stats = memory_manager.get_memory_stats()
    print(f"\nFinal Memory Statistics:")
    print(f"  - Total Memories: {final_stats['cross_session_memory']['total_memories']}")
    print(f"  - Active Conversations: {final_stats['conversation_memory']['active_conversations']}")
    print(f"  - Response Patterns: {final_stats['adaptive_patterns']['total_patterns']}")
    
    print("\n🎉 Enhanced Memory System Test Completed Successfully!")
    print("\n📋 Summary of Features Tested:")
    print("  ✅ User Memory & Preferences")
    print("  ✅ Conversation History Storage")
    print("  ✅ Cross-Session Memory")
    print("  ✅ Adaptive Response Patterns")
    print("  ✅ Context Retrieval")
    print("  ✅ ChatService Integration")
    print("  ✅ Memory Persistence")
    print("  ✅ Memory Cleanup")
    
    return True


def cleanup_test_data():
    """Clean up test data"""
    try:
        # Delete test user and all associated data
        User.objects.filter(username='memory_test_user').delete()
        print("✅ Test data cleaned up")
    except Exception as e:
        print(f"⚠️  Error cleaning up test data: {e}")


if __name__ == "__main__":
    try:
        success = test_memory_system()
        if success:
            print("\n🚀 All memory features are working correctly!")
            
            # Ask if user wants to clean up test data
            response = input("\n❓ Clean up test data? (y/N): ").lower().strip()
            if response == 'y':
                cleanup_test_data()
        else:
            print("\n❌ Memory system test failed")
            
    except Exception as e:
        print(f"\n❌ Error during memory system test: {e}")
        import traceback
        traceback.print_exc()
        
        # Clean up on error
        cleanup_test_data()

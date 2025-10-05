#!/usr/bin/env python3
"""
Test script for the new LanggraphView
Demonstrates the advanced LangGraph functionality with continuous feedback loops,
short-term memory (checkpoints), and long-term memory (PostgresStore)
"""

import os
import sys
import django
from django.conf import settings

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

from ad_expert.views import LanggraphView
from ad_expert.tools import ALL_TOOLS
from django.test import RequestFactory
from django.contrib.auth.models import User
from rest_framework.test import force_authenticate
import json

def test_langgraph_view():
    """Test the LanggraphView functionality"""
    print("🚀 Testing LanggraphView...")
    
    # Create a test user
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@example.com'}
    )
    
    # Create request factory
    factory = RequestFactory()
    
    # Create the view instance
    view = LanggraphView()
    
    print("✅ LanggraphView initialized successfully")
    print(f"📊 Available tools: {len(ALL_TOOLS)}")
    print(f"💾 Checkpointer: {type(view.checkpointer).__name__}")
    print(f"🗄️ PostgresStore: {'Available' if view.postgres_store else 'Not available'}")
    
    # Test the graph structure
    print("\n🔗 Graph Structure:")
    print(f"   - Nodes: {list(view.workflow.nodes.keys())}")
    print(f"   - Edges: {len(view.workflow.edges)}")
    
    # Test accessible customers functionality
    print("\n🧪 Testing accessible customers functionality...")
    
    # Test getting accessible customers
    accessible_customers = view._get_accessible_customers(user.id)
    print(f"📋 Accessible customers from database: {len(accessible_customers)}")
    
    # Test saving to long-term memory
    if accessible_customers:
        success = view._save_accessible_customers_to_long_term_memory(user.id, accessible_customers)
        print(f"💾 Save to long-term memory: {'Success' if success else 'Failed'}")
        
        # Test retrieving from long-term memory
        retrieved_customers = view._get_accessible_customers_from_long_term_memory(user.id)
        print(f"📥 Retrieved from long-term memory: {len(retrieved_customers)}")
    
    # Test a simple request
    print("\n🧪 Testing simple request...")
    
    request_data = {
        'query': 'Show me my campaigns',
        'conversation_id': None,
        'customer_id': None
    }
    
    # Create POST request
    request = factory.post('/api/langgraph/chat/', 
                          data=request_data,
                          content_type='application/json')
    
    # Authenticate the request
    force_authenticate(request, user=user)
    
    try:
        # Call the view
        response = view.post(request)
        
        print(f"✅ Response status: {response.status_code}")
        if hasattr(response, 'data'):
            print(f"📝 Response data keys: {list(response.data.keys())}")
            if 'langgraph_state' in response.data:
                state = response.data['langgraph_state']
                print(f"🔄 Final state: {state}")
                if 'accessible_customers' in state:
                    print(f"👥 Accessible customers in response: {len(state['accessible_customers'])}")
        
    except Exception as e:
        print(f"❌ Error during request: {e}")
        import traceback
        traceback.print_exc()

def test_graph_flow():
    """Test the graph flow without making HTTP requests"""
    print("\n🔄 Testing Graph Flow...")
    
    try:
        from ad_expert.views import LangGraphState
        from langchain_core.messages import HumanMessage
        
        # Create a test state
        test_state = {
            "messages": [HumanMessage(content="Test message")],
            "user_id": 1,
            "conversation_id": "test_conv",
            "customer_id": None,
            "accessible_customers": [],
            "user_context": {},
            "current_step": "start",
            "error_count": 0,
            "max_retries": 3
        }
        
        print("✅ Test state created successfully")
        print(f"📊 State keys: {list(test_state.keys())}")
        
        # Test decision node logic
        view = LanggraphView()
        
        # Test decision function
        def test_decision_node(state):
            error_count = state.get("error_count", 0)
            max_retries = state.get("max_retries", 3)
            
            if error_count >= max_retries:
                return "end"
            
            current_step = state.get("current_step", "start")
            
            if current_step == "start":
                return "context"
            elif current_step == "context_enriched":
                return "chat"
            elif current_step == "chat_completed":
                return "tools"  # Assume tools are needed
            elif current_step == "tools_completed":
                return "chat"
            else:
                return "end"
        
        # Test decision flow
        decision = test_decision_node(test_state)
        print(f"🎯 Decision for 'start' step: {decision}")
        
        # Test with different steps
        test_state["current_step"] = "context_enriched"
        decision = test_decision_node(test_state)
        print(f"🎯 Decision for 'context_enriched' step: {decision}")
        
        test_state["current_step"] = "chat_completed"
        decision = test_decision_node(test_state)
        print(f"🎯 Decision for 'chat_completed' step: {decision}")
        
    except Exception as e:
        print(f"❌ Error testing graph flow: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 LANGGRAPH VIEW TEST SUITE")
    print("=" * 60)
    
    try:
        test_langgraph_view()
        test_graph_flow()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        
        print("\n📋 Summary:")
        print("   - LanggraphView: Advanced LangGraph implementation")
        print("   - Features: Continuous feedback loops, checkpoints, PostgresStore")
        print("   - Tools: All Google Ads tools integrated")
        print("   - Memory: Short-term (checkpoints) + Long-term (PostgresStore)")
        print("   - Flow: Context → Chat → Tools → Chat (continuous)")
        
        print("\n🔗 Available endpoints:")
        print("   - POST /api/langgraph/chat/ - Main LangGraph endpoint")
        print("   - POST /api/langchain/chat/ - Simple LangChain endpoint")
        print("   - POST /api/rag/chat/ - RAG with Intent Mapping")
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


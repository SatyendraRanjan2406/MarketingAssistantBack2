#!/usr/bin/env python3
"""
RAG System Demo Script for Google Ads Analysis
Showcases all RAG capabilities including smart context selection and hybrid responses
"""

import os
import django
import json
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

def demo_rag_system():
    """Demo the complete RAG system"""
    
    print("🤖 RAG System Demo for Google Ads Analysis")
    print("=" * 60)
    
    try:
        from google_ads_new.rag_service import GoogleAdsRAGService
        from django.contrib.auth.models import User
        
        # Get a test user
        try:
            user = User.objects.first()
            if not user:
                print("❌ No users found. Please create a user first.")
                return
        except Exception as e:
            print(f"❌ Error getting user: {e}")
            return
        
        print(f"✅ Using user: {user.username}")
        
        # Initialize RAG service
        print("\n🔧 Initializing RAG Service...")
        rag_service = GoogleAdsRAGService(user)
        print("✅ RAG service initialized successfully")
        
        # Show vector store stats
        stats = rag_service.get_vectorstore_stats()
        print(f"📊 Vector store: {stats.get('total_documents', 0)} documents")
        
        # Demo 1: Smart Context Selection
        print("\n🎯 Demo 1: Smart Context Selection")
        demo_smart_context_selection(rag_service)
        
        # Demo 2: Document Search and Retrieval
        print("\n🔍 Demo 2: Document Search and Retrieval")
        demo_document_search(rag_service)
        
        # Demo 3: RAG vs Direct OpenAI
        print("\n⚖️  Demo 3: RAG vs Direct OpenAI Comparison")
        demo_rag_vs_direct(rag_service)
        
        # Demo 4: Hybrid Response Generation
        print("\n🔄 Demo 4: Hybrid Response Generation")
        demo_hybrid_responses(rag_service)
        
        # Demo 5: Context Augmentation
        print("\n📚 Demo 5: Context Augmentation")
        demo_context_augmentation(rag_service)
        
        print("\n🎉 RAG System Demo Complete!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all required packages are installed:")
        print("   pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("💡 Check the Django setup and database connection")

def demo_smart_context_selection(rag_service):
    """Demo smart context selection"""
    
    print("   🧠 Testing intelligent context selection...")
    
    # Test queries with different characteristics
    test_cases = [
        {
            "query": "What are the best practices for Google Ads campaign structure?",
            "expected": "rag",
            "reason": "Knowledge-based query requiring best practices"
        },
        {
            "query": "How do I optimize my Quality Score?",
            "expected": "rag", 
            "reason": "Strategy question requiring expert knowledge"
        },
        {
            "query": "Show me my campaign performance data",
            "expected": "direct",
            "reason": "Data-focused query not requiring knowledge base"
        },
        {
            "query": "What bidding strategy should I use for e-commerce campaigns?",
            "expected": "rag",
            "reason": "Strategic question requiring industry knowledge"
        },
        {
            "query": "Create a new campaign",
            "expected": "direct",
            "reason": "Simple action request"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n      Test {i}: {test_case['query']}")
        print(f"         Expected: {test_case['expected']}")
        print(f"         Reason: {test_case['reason']}")
        
        try:
            # Test smart context selection
            context, use_rag = rag_service.smart_context_selection(
                test_case['query'], 
                {"has_campaigns": True, "campaign_count": 3}
            )
            
            actual = "rag" if use_rag else "direct"
            status = "✅" if actual == test_case['expected'] else "❌"
            
            print(f"         Result: {status} {actual.upper()}")
            
            if use_rag:
                print(f"         Context length: {len(context)} characters")
                print(f"         Context preview: {context[:100]}...")
            else:
                print(f"         Direct OpenAI selected")
                
        except Exception as e:
            print(f"         ❌ Error: {e}")

def demo_document_search(rag_service):
    """Demo document search and retrieval"""
    
    print("   📚 Testing document search capabilities...")
    
    # Test different search queries
    search_queries = [
        "campaign structure best practices",
        "Quality Score optimization",
        "bidding strategies",
        "ad copy optimization",
        "remarketing campaigns"
    ]
    
    for query in search_queries:
        print(f"\n      🔍 Searching for: '{query}'")
        
        try:
            # Search documents
            results = rag_service.search_documents(query, k=2)
            
            if results:
                print(f"         ✅ Found {len(results)} relevant documents")
                
                # Show document details
                for j, doc in enumerate(results, 1):
                    source = doc.metadata.get("source", "unknown")
                    content_preview = doc.page_content[:150] + "..." if len(doc.page_content) > 150 else doc.page_content
                    print(f"         Document {j} (Source: {source}):")
                    print(f"            {content_preview}")
            else:
                print(f"         ⚠️  No relevant documents found")
                
        except Exception as e:
            print(f"         ❌ Search error: {e}")

def demo_rag_vs_direct(rag_service):
    """Demo RAG vs Direct OpenAI comparison"""
    
    print("   ⚖️  Comparing RAG vs Direct OpenAI responses...")
    
    test_query = "What are the best practices for Google Ads optimization?"
    user_data = {"has_campaigns": True, "campaign_count": 5}
    
    try:
        print(f"\n      Query: '{test_query}'")
        
        # Get RAG response
        print(f"      🔍 Getting RAG response...")
        rag_response = rag_service.get_rag_response(test_query, "Sample context from knowledge base", user_data)
        
        # Get direct OpenAI response
        print(f"      🤖 Getting direct OpenAI response...")
        direct_response = rag_service.get_direct_openai_response(test_query, user_data)
        
        # Compare responses
        print(f"\n      📊 Response Comparison:")
        
        # RAG response details
        if "rag_metadata" in rag_response:
            rag_meta = rag_response["rag_metadata"]
            print(f"         RAG Response:")
            print(f"            Context used: {rag_meta.get('context_used', False)}")
            print(f"            Context length: {rag_meta.get('context_length', 0)}")
            print(f"            Generation method: {rag_meta.get('generation_method', 'unknown')}")
        
        # Direct response details
        if "rag_metadata" in direct_response:
            direct_meta = direct_response["rag_metadata"]
            print(f"         Direct OpenAI Response:")
            print(f"            Context used: {direct_meta.get('context_used', False)}")
            print(f"            Context length: {direct_meta.get('context_length', 0)}")
            print(f"            Generation method: {direct_meta.get('generation_method', 'unknown')}")
        
        # Show response structure
        if "blocks" in rag_response:
            rag_blocks = len(rag_response["blocks"])
            print(f"         RAG blocks: {rag_blocks}")
        
        if "blocks" in direct_response:
            direct_blocks = len(direct_response["blocks"])
            print(f"         Direct blocks: {direct_blocks}")
            
    except Exception as e:
        print(f"      ❌ Comparison error: {e}")

def demo_hybrid_responses(rag_service):
    """Demo hybrid response generation"""
    
    print("   🔄 Testing hybrid response generation...")
    
    # Test different query types
    hybrid_test_cases = [
        {
            "query": "What are the best practices for Google Ads campaign optimization?",
            "description": "Knowledge-based query (should use RAG)"
        },
        {
            "query": "Analyze my campaign performance data",
            "description": "Data-focused query (should use direct OpenAI)"
        },
        {
            "query": "How do I implement remarketing strategies?",
            "description": "Strategy question (should use RAG)"
        },
        {
            "query": "Create a new ad group",
            "description": "Simple action (should use direct OpenAI)"
        }
    ]
    
    for i, test_case in enumerate(hybrid_test_cases, 1):
        print(f"\n      Test {i}: {test_case['query']}")
        print(f"         Description: {test_case['description']}")
        
        try:
            # Get hybrid response
            hybrid_response = rag_service.get_hybrid_response(
                test_case['query'],
                {"has_campaigns": True, "campaign_count": 3}
            )
            
            if "response_type" in hybrid_response:
                response_type = hybrid_response["response_type"]
                print(f"         ✅ Response type: {response_type}")
                
                # Show hybrid metadata
                if "hybrid_metadata" in hybrid_response:
                    metadata = hybrid_response["hybrid_metadata"]
                    print(f"         📊 Context selection: {metadata.get('context_selection', 'unknown')}")
                    print(f"         📝 Selection reason: {metadata.get('selection_reason', 'unknown')}")
                
                # Show RAG metadata
                if "rag_metadata" in hybrid_response:
                    rag_meta = hybrid_response["rag_metadata"]
                    print(f"         🔍 Context used: {rag_meta.get('context_used', False)}")
                    print(f"         📏 Context length: {rag_meta.get('context_length', 0)}")
                
                # Show response structure
                if "blocks" in hybrid_response:
                    blocks = hybrid_response["blocks"]
                    print(f"         🎨 UI blocks generated: {len(blocks)}")
                    
                    # Show block types
                    block_types = [block.get('type', 'unknown') for block in blocks]
                    unique_types = list(set(block_types))
                    print(f"         📋 Block types: {', '.join(unique_types)}")
                    
            else:
                print(f"         ⚠️  Response missing type information")
                
        except Exception as e:
            print(f"         ❌ Hybrid response error: {e}")

def demo_context_augmentation(rag_service):
    """Demo context augmentation capabilities"""
    
    print("   📚 Testing context augmentation...")
    
    # Test context building
    test_query = "How do I optimize my Google Ads campaigns?"
    user_data = {"has_campaigns": True, "campaign_count": 5}
    
    try:
        print(f"\n      Query: '{test_query}'")
        
        # Get context and decision
        context, use_rag = rag_service.smart_context_selection(test_query, user_data)
        
        if use_rag:
            print(f"      ✅ RAG selected with context augmentation")
            print(f"      📏 Context length: {len(context)} characters")
            
            # Show context structure
            context_lines = context.split('\n')
            print(f"      📋 Context structure ({len(context_lines)} lines):")
            
            for i, line in enumerate(context_lines[:5]):  # Show first 5 lines
                if line.strip():
                    preview = line[:80] + "..." if len(line) > 80 else line
                    print(f"         Line {i+1}: {preview}")
            
            if len(context_lines) > 5:
                print(f"         ... and {len(context_lines) - 5} more lines")
            
            # Test context truncation
            print(f"\n      🔧 Testing context truncation...")
            truncated_context = rag_service._truncate_context(context, 2000)
            print(f"         Original length: {len(context)}")
            print(f"         Truncated length: {len(truncated_context)}")
            
        else:
            print(f"      ℹ️  Direct OpenAI selected (no context needed)")
            
    except Exception as e:
        print(f"      ❌ Context augmentation error: {e}")

def main():
    """Main demo function"""
    
    print("🚀 Starting RAG System Demo...")
    
    # Run demo
    demo_rag_system()
    
    print("\n🎯 RAG System Capabilities Demonstrated:")
    print("   ✅ Smart context selection (RAG vs Direct OpenAI)")
    print("   ✅ Document search and retrieval")
    print("   ✅ Context augmentation with knowledge base")
    print("   ✅ Hybrid response generation")
    print("   ✅ Intelligent context truncation")
    
    print("\n🔧 How to Use:")
    print("   1. Setup: python setup_rag_system.py")
    print("   2. Demo: python demo_rag_system.py")
    print("   3. Chat: Use the chat interface to test RAG responses")
    print("   4. Add Documents: Place knowledge base files in knowledge_base/")
    
    print("\n📚 Knowledge Base Management:")
    print("   - Add .md, .txt, .pdf files to knowledge_base/")
    print("   - Documents are automatically processed and embedded")
    print("   - Vector store persists between sessions")
    print("   - Use rag_service.clear_vectorstore() to reset")

if __name__ == "__main__":
    main()


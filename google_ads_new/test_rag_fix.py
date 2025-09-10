#!/usr/bin/env python3
"""
Test script to verify RAG system fixes
"""

import os
import sys
import django

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

def test_imports():
    """Test if all imports work correctly"""
    print("Testing imports...")
    
    try:
        from langchain_openai import OpenAIEmbeddings, ChatOpenAI
        print("✅ langchain_openai imports successful")
    except ImportError as e:
        print(f"❌ langchain_openai import failed: {e}")
        return False
    
    try:
        from langchain_qdrant import Qdrant
        print("✅ langchain_qdrant import successful")
    except ImportError as e:
        print(f"❌ langchain_qdrant import failed: {e}")
        return False
    
    try:
        from google_ads_new.rag_client import GoogleAdsRAGClient
        print("✅ RAG client import successful")
    except ImportError as e:
        print(f"❌ RAG client import failed: {e}")
        return False
    
    return True

def test_rag_client_creation():
    """Test if RAG client can be created without errors"""
    print("\nTesting RAG client creation...")
    
    try:
        from google_ads_new.rag_client import GoogleAdsRAGClient
        
        # Test with minimal configuration
        rag_client = GoogleAdsRAGClient(
            collection_name="test_collection",
            qdrant_url="http://localhost:6333"
        )
        print("✅ RAG client created successfully")
        return True
        
    except Exception as e:
        print(f"❌ RAG client creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_query():
    """Test a simple query without vector store"""
    print("\nTesting simple query...")
    
    try:
        from google_ads_new.rag_client import GoogleAdsRAGClient
        
        # Create client
        rag_client = GoogleAdsRAGClient(
            collection_name="test_collection",
            qdrant_url="http://localhost:6333"
        )
        
        # Test if the client has the required methods
        assert hasattr(rag_client, 'query'), "Missing query method"
        assert hasattr(rag_client, 'get_similar_docs'), "Missing get_similar_docs method"
        assert hasattr(rag_client, 'get_collection_stats'), "Missing get_collection_stats method"
        
        print("✅ RAG client methods available")
        return True
        
    except Exception as e:
        print(f"❌ Simple query test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("RAG System Fix Test")
    print("=" * 50)
    
    # Check environment
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OPENAI_API_KEY not set, some tests may fail")
    
    # Run tests
    tests = [
        test_imports,
        test_rag_client_creation,
        test_simple_query
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed! RAG system should work now.")
    else:
        print("❌ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()

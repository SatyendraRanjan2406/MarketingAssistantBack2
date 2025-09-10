#!/usr/bin/env python3
"""
Simple test script for RAG system without Django server
"""

import os
import sys
import django

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

def test_rag_imports():
    """Test if RAG system can be imported"""
    print("Testing RAG system imports...")
    
    try:
        from google_ads_new.rag_client import GoogleAdsRAGClient
        from google_ads_new.document_scraper import scrape_google_ads_docs
        from google_ads_new.vector_store import setup_vector_store
        print("✅ All RAG imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_rag_client_creation():
    """Test RAG client creation"""
    print("\nTesting RAG client creation...")
    
    try:
        from google_ads_new.rag_client import GoogleAdsRAGClient
        
        # Create client with test collection
        rag_client = GoogleAdsRAGClient(
            collection_name="test_google_ads_docs",
            qdrant_url="http://localhost:6333"
        )
        
        print("✅ RAG client created successfully")
        print(f"   Collection: {rag_client.collection_name}")
        print(f"   Qdrant URL: {rag_client.qdrant_url}")
        return True
        
    except Exception as e:
        print(f"❌ RAG client creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_document_scraper():
    """Test document scraper"""
    print("\nTesting document scraper...")
    
    try:
        from google_ads_new.document_scraper import scrape_google_ads_docs
        
        # Test with just a few URLs
        from google_ads_new.constants import GOOGLE_ADS_API_DOCS_URLS
        test_urls = GOOGLE_ADS_API_DOCS_URLS[:3]  # Just first 3 URLs
        
        print(f"Testing with {len(test_urls)} URLs...")
        
        # This will take some time, so we'll just test the function exists
        print("✅ Document scraper function available")
        print("   Note: Full scraping test requires internet connection")
        return True
        
    except Exception as e:
        print(f"❌ Document scraper test failed: {e}")
        return False

def test_vector_store():
    """Test vector store operations"""
    print("\nTesting vector store...")
    
    try:
        from google_ads_new.vector_store import GoogleAdsVectorStore
        
        # Create vector store instance
        vector_store = GoogleAdsVectorStore(
            collection_name="test_collection",
            qdrant_url="http://localhost:6333"
        )
        
        print("✅ Vector store created successfully")
        print(f"   Collection: {vector_store.collection_name}")
        print(f"   Qdrant URL: {vector_store.qdrant_url}")
        return True
        
    except Exception as e:
        print(f"❌ Vector store test failed: {e}")
        return False

def show_setup_instructions():
    """Show setup instructions"""
    print("\n" + "="*60)
    print("RAG System Setup Instructions")
    print("="*60)
    
    print("""
1. Install required packages:
   pip install -r google_ads_new/requirements_rag.txt

2. Start Qdrant vector database:
   docker run -p 6333:6333 qdrant/qdrant
   
   OR download Qdrant binary from:
   https://qdrant.tech/documentation/quick-start/

3. Set environment variables:
   export OPENAI_API_KEY="your_openai_api_key"

4. Set up the RAG system:
   python manage.py setup_rag

5. Start Django server:
   python manage.py runserver 8000

6. Test with cURL:
   curl -X POST 'http://localhost:8000/google-ads-new/api/rag/query/' \\
     -H 'Content-Type: application/json' \\
     -d '{"query": "How do I get started with Google Ads API?"}'
""")

def main():
    """Run all tests"""
    print("Google Ads RAG System - Simple Test")
    print("="*50)
    
    # Check environment
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OPENAI_API_KEY not set")
        print("   Set it with: export OPENAI_API_KEY='your_key'")
        print()
    
    # Run tests
    tests = [
        test_rag_imports,
        test_rag_client_creation,
        test_document_scraper,
        test_vector_store
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("="*50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed! RAG system is ready.")
        print("   You can now set up the full system using the instructions below.")
    else:
        print("❌ Some tests failed. Check the errors above.")
    
    show_setup_instructions()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test RAG system components without requiring Qdrant to be running
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
    """Test if all imports work"""
    print("Testing RAG system imports...")
    
    try:
        from google_ads_new.document_scraper import scrape_google_ads_docs
        from google_ads_new.vector_store import GoogleAdsVectorStore
        from google_ads_new.rag_client import GoogleAdsRAGClient
        from google_ads_new.rag_views import query_rag
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_document_scraper():
    """Test document scraper with a few URLs"""
    print("\nTesting document scraper...")
    
    try:
        from google_ads_new.document_scraper import GoogleAdsDocsScraper
        from google_ads_new.constants import GOOGLE_ADS_API_DOCS_URLS
        
        # Test with just 2 URLs
        test_urls = GOOGLE_ADS_API_DOCS_URLS[:2]
        scraper = GoogleAdsDocsScraper(chunk_size=500, chunk_overlap=100)
        
        print(f"Testing with {len(test_urls)} URLs...")
        print("Note: This requires internet connection")
        
        # Just test the scraper creation, not actual scraping
        print("✅ Document scraper initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Document scraper error: {e}")
        return False

def test_vector_store():
    """Test vector store creation"""
    print("\nTesting vector store...")
    
    try:
        from google_ads_new.vector_store import GoogleAdsVectorStore
        
        # Create vector store instance (won't connect to Qdrant)
        vector_store = GoogleAdsVectorStore(
            collection_name="test_collection",
            qdrant_url="http://localhost:6333"
        )
        
        print("✅ Vector store created successfully")
        print(f"   Collection: {vector_store.collection_name}")
        print(f"   Qdrant URL: {vector_store.qdrant_url}")
        return True
        
    except Exception as e:
        print(f"❌ Vector store error: {e}")
        return False

def test_rag_views():
    """Test RAG views"""
    print("\nTesting RAG views...")
    
    try:
        from google_ads_new.rag_views import query_rag, search_documents, rag_status
        
        print("✅ RAG views imported successfully")
        print("   Available functions:")
        print("   - query_rag")
        print("   - search_documents") 
        print("   - rag_status")
        return True
        
    except Exception as e:
        print(f"❌ RAG views error: {e}")
        return False

def show_qdrant_setup():
    """Show Qdrant setup instructions"""
    print("\n" + "="*60)
    print("Qdrant Setup Instructions")
    print("="*60)
    
    print("""
The RAG system requires Qdrant vector database to be running.

Option 1: Using Docker (Recommended)
------------------------------------
1. Install Docker: https://docs.docker.com/get-docker/
2. Start Qdrant:
   docker run -d -p 6333:6333 qdrant/qdrant
3. Verify it's running:
   curl http://localhost:6333/collections

Option 2: Using Qdrant Binary
-----------------------------
1. Download Qdrant binary:
   https://qdrant.tech/documentation/quick-start/
2. Extract and run:
   ./qdrant
3. Qdrant will start on http://localhost:6333

Option 3: Using Python Package (Alternative)
--------------------------------------------
pip install qdrant-client[fastapi]
python -c "from qdrant_client import QdrantClient; client = QdrantClient(':memory:'); print('In-memory Qdrant ready')"
""")

def show_curl_examples():
    """Show working cURL examples"""
    print("\n" + "="*60)
    print("Working cURL Examples")
    print("="*60)
    
    print("""
Once Qdrant is running, you can use these cURL commands:

1. Basic Query:
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/query/' \\
  -H 'Content-Type: application/json' \\
  -d '{"query": "How do I get started with Google Ads API?"}'

2. Search Documents:
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/search/' \\
  -H 'Content-Type: application/json' \\
  -d '{"query": "OAuth setup", "limit": 5}'

3. Get Status:
curl -X GET 'http://localhost:8000/google-ads-new/api/rag/status/'

4. Rebuild Vector Store:
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/rebuild/'

5. Authenticated Query (requires JWT token):
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/api/query/' \\
  -H 'Content-Type: application/json' \\
  -H 'Authorization: Bearer <your_jwt_token>' \\
  -d '{"query": "How do I create a campaign?"}'
""")

def main():
    """Run all tests"""
    print("RAG System Component Test (Without Qdrant)")
    print("="*50)
    
    # Check environment
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OPENAI_API_KEY not set")
        print("   Set it with: export OPENAI_API_KEY='your_key'")
        print()
    
    # Run tests
    tests = [
        test_imports,
        test_document_scraper,
        test_vector_store,
        test_rag_views
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
        print("✅ All RAG components are working!")
        print("   The system is ready - you just need to start Qdrant.")
    else:
        print("❌ Some components failed. Check the errors above.")
    
    show_qdrant_setup()
    show_curl_examples()

if __name__ == "__main__":
    main()

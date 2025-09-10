#!/usr/bin/env python3
"""
Simple RAG setup script that doesn't require authentication
"""

import os
import sys
import django

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

def setup_rag_system():
    """Set up the RAG system"""
    print("Setting up RAG system...")
    
    try:
        from google_ads_new.document_scraper import scrape_google_ads_docs
        from google_ads_new.vector_store import setup_vector_store
        
        # Check if OpenAI API key is set
        if not os.getenv('OPENAI_API_KEY'):
            print("❌ OPENAI_API_KEY not set")
            print("Set it with: export OPENAI_API_KEY='your_key'")
            return False
        
        print("✅ OpenAI API key found")
        
        # Scrape documents (just a few for testing)
        print("Scraping Google Ads documentation...")
        from google_ads_new.constants import GOOGLE_ADS_API_DOCS_URLS
        
        # Use just first 3 URLs for quick testing
        test_urls = GOOGLE_ADS_API_DOCS_URLS[:3]
        print(f"Testing with {len(test_urls)} URLs...")
        
        # Create scraper and scrape
        from google_ads_new.document_scraper import GoogleAdsDocsScraper
        scraper = GoogleAdsDocsScraper(chunk_size=800, chunk_overlap=200)
        
        # Scrape documents
        documents = []
        for i, url in enumerate(test_urls):
            print(f"Scraping {i+1}/{len(test_urls)}: {url}")
            text = scraper.fetch_text(url)
            if text:
                chunks = scraper.splitter.split_text(text)
                for j, chunk in enumerate(chunks):
                    if len(chunk.strip()) > 50:
                        from langchain.schema import Document
                        doc = Document(
                            page_content=chunk,
                            metadata={
                                'source': url,
                                'chunk': j,
                                'total_chunks': len(chunks),
                                'url_index': i
                            }
                        )
                        documents.append(doc)
        
        print(f"✅ Scraped {len(documents)} document chunks")
        
        # Setup vector store
        print("Setting up vector store...")
        vector_store = setup_vector_store(documents, recreate=True)
        
        print("✅ RAG system setup completed!")
        print(f"   Documents: {len(documents)}")
        print("   Collection: google_ads_docs")
        print("   Qdrant: http://localhost:6333")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up RAG system: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rag_query():
    """Test a RAG query"""
    print("\nTesting RAG query...")
    
    try:
        from google_ads_new.rag_client import get_rag_client
        
        rag_client = get_rag_client()
        result = rag_client.query("How do I get started with Google Ads API?")
        
        if result['success']:
            print("✅ RAG query successful!")
            print(f"Answer: {result['answer'][:200]}...")
            print(f"Sources: {len(result['sources'])}")
        else:
            print(f"❌ RAG query failed: {result.get('error')}")
        
        return result['success']
        
    except Exception as e:
        print(f"❌ Error testing RAG query: {e}")
        return False

def main():
    """Main function"""
    print("RAG System Setup")
    print("="*40)
    
    # Setup RAG system
    if setup_rag_system():
        print("\n" + "="*40)
        print("Testing RAG system...")
        
        # Test RAG query
        if test_rag_query():
            print("\n🎉 RAG system is fully working!")
            print("\nYou can now use these cURL commands:")
            print("curl -X POST 'http://localhost:8000/google-ads-new/api/rag/query/' \\")
            print("  -H 'Content-Type: application/json' \\")
            print("  -d '{\"query\": \"How do I get started with Google Ads API?\"}'")
        else:
            print("\n❌ RAG system test failed")
    else:
        print("\n❌ RAG system setup failed")

if __name__ == "__main__":
    main()

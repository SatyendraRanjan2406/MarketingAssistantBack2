#!/usr/bin/env python3
"""
Test script for the Google Ads RAG system
"""

import os
import sys
import django
import json
import requests

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

from google_ads_new.rag_client import get_rag_client, initialize_rag_client
from google_ads_new.document_scraper import scrape_google_ads_docs
from google_ads_new.vector_store import setup_vector_store

def test_rag_system():
    """Test the complete RAG system"""
    print("Testing Google Ads RAG System")
    print("=" * 60)
    
    try:
        # Test 1: Initialize RAG client
        print("1. Initializing RAG client...")
        rag_client = get_rag_client()
        print("✅ RAG client initialized successfully")
        
        # Test 2: Get collection stats
        print("\n2. Getting collection statistics...")
        stats = rag_client.get_collection_stats()
        print(f"Collection: {stats.get('collection_name', 'N/A')}")
        print(f"Total points: {stats.get('total_points', 'N/A')}")
        print(f"Indexed vectors: {stats.get('indexed_vectors', 'N/A')}")
        
        # Test 3: Test queries
        print("\n3. Testing RAG queries...")
        test_queries = [
            "How do I get started with Google Ads API?",
            "What is OAuth and how do I set it up?",
            "How do I create a campaign using the API?",
            "What are the common errors in Google Ads API?",
            "How do I manage account access?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\nQuery {i}: {query}")
            result = rag_client.query(query)
            
            if result['success']:
                print(f"✅ Answer: {result['answer'][:200]}...")
                print(f"Sources: {len(result['sources'])} documents")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
        
        # Test 4: Test document search
        print("\n4. Testing document search...")
        search_query = "OAuth setup"
        similar_docs = rag_client.get_similar_docs(search_query, limit=3)
        print(f"Found {len(similar_docs)} similar documents for '{search_query}'")
        
        for i, doc in enumerate(similar_docs, 1):
            print(f"  {i}. {doc['source']} (chunk {doc['chunk']})")
            print(f"     {doc['text'][:100]}...")
        
        print("\n✅ RAG system test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing RAG system: {e}")
        import traceback
        traceback.print_exc()

def test_api_endpoints():
    """Test the API endpoints"""
    print("\n" + "=" * 60)
    print("Testing API Endpoints")
    print("=" * 60)
    
    base_url = "http://localhost:8000/google-ads-new/api/rag"
    
    # Test queries
    test_queries = [
        "How do I authenticate with Google Ads API?",
        "What is a developer token?",
        "How do I create a campaign?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nTest {i}: Query API")
        print(f"Query: {query}")
        
        try:
            response = requests.post(
                f"{base_url}/query/",
                json={"query": query},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Answer: {data['answer'][:200]}...")
                    print(f"Sources: {len(data.get('sources', []))}")
                else:
                    print(f"❌ API Error: {data.get('error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Request Error: {e}")
    
    # Test status endpoint
    print(f"\nTesting status endpoint...")
    try:
        response = requests.get(f"{base_url}/status/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('status')}")
            print(f"Collection stats: {data.get('collection_stats')}")
        else:
            print(f"❌ Status check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Status check error: {e}")

def show_curl_examples():
    """Show cURL examples for testing"""
    print("\n" + "=" * 60)
    print("cURL Examples for Testing")
    print("=" * 60)
    
    print("""
# 1. Query the RAG system
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/query/' \\
  -H 'Content-Type: application/json' \\
  -d '{"query": "How do I get started with Google Ads API?"}'

# 2. Search for similar documents
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/search/' \\
  -H 'Content-Type: application/json' \\
  -d '{"query": "OAuth setup", "limit": 5}'

# 3. Get RAG system status
curl -X GET 'http://localhost:8000/google-ads-new/api/rag/status/'

# 4. Rebuild vector store (requires authentication)
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/rebuild/' \\
  -H 'Content-Type: application/json' \\
  -H 'Authorization: Bearer <your_jwt_token>'

# 5. REST API query (requires authentication)
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/api/query/' \\
  -H 'Content-Type: application/json' \\
  -H 'Authorization: Bearer <your_jwt_token>' \\
  -d '{"query": "How do I create a campaign?"}'
""")

if __name__ == "__main__":
    print("Google Ads RAG System Test")
    print("=" * 60)
    
    # Check environment variables
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not set in environment")
        print("Please set your OpenAI API key before running the test")
        sys.exit(1)
    
    # Run tests
    test_rag_system()
    test_api_endpoints()
    show_curl_examples()
    
    print("\n" + "=" * 60)
    print("Test completed!")

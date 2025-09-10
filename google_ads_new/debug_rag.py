#!/usr/bin/env python3
"""
Debug script to test RAG client and Qdrant integration
"""

import os
import sys
import django

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

from google_ads_new.rag_client import get_rag_client
from qdrant_client import QdrantClient

def debug_rag_client():
    print("🔍 Debugging RAG Client")
    print("=" * 50)
    
    try:
        # Test Qdrant connection
        print("1. Testing Qdrant connection...")
        qdrant_client = QdrantClient("localhost", port=6333)
        collections = qdrant_client.get_collections()
        print(f"   ✅ Connected to Qdrant. Collections: {[c.name for c in collections.collections]}")
        
        # Test collection info
        print("\n2. Testing collection info...")
        collection_info = qdrant_client.get_collection("google_ads_docs")
        print(f"   ✅ Collection 'google_ads_docs' has {collection_info.points_count} points")
        
        # Test direct Qdrant search
        print("\n3. Testing direct Qdrant search...")
        search_result = qdrant_client.search(
            collection_name="google_ads_docs",
            query_vector=[0.1] * 3072,  # Dummy vector
            limit=3,
            with_payload=True
        )
        print(f"   ✅ Direct search returned {len(search_result)} results")
        if search_result:
            print(f"   Sample result payload: {search_result[0].payload}")
        
        # Test RAG client
        print("\n4. Testing RAG client...")
        rag_client = get_rag_client()
        print(f"   ✅ RAG client initialized")
        
        # Test retriever
        print("\n5. Testing retriever...")
        docs = rag_client.retriever.invoke("OAuth authentication")
        print(f"   ✅ Retriever returned {len(docs)} documents")
        
        for i, doc in enumerate(docs):
            print(f"   Document {i+1}:")
            print(f"     Source: {doc.metadata.get('source', 'N/A')}")
            print(f"     Text: {doc.page_content[:100]}...")
            print(f"     Metadata: {doc.metadata}")
        
        # Test get_similar_docs
        print("\n6. Testing get_similar_docs...")
        similar_docs = rag_client.get_similar_docs("OAuth authentication", limit=3)
        print(f"   ✅ get_similar_docs returned {len(similar_docs)} documents")
        
        for i, doc in enumerate(similar_docs):
            print(f"   Similar doc {i+1}:")
            print(f"     Source: {doc.get('source', 'N/A')}")
            print(f"     Text: {doc.get('text', 'N/A')[:100]}...")
            print(f"     Metadata: {doc.get('metadata', {})}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_rag_client()

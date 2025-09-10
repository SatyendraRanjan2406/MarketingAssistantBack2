#!/usr/bin/env python3
"""
Start Qdrant in-memory for testing the RAG system
"""

import os
import sys
import django
import time
import threading
from qdrant_client import QdrantClient

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

def start_in_memory_qdrant():
    """Start Qdrant in-memory mode"""
    print("Starting Qdrant in-memory mode...")
    
    try:
        # Create in-memory Qdrant client
        client = QdrantClient(":memory:")
        
        # Create a test collection
        from qdrant_client.http import models as rest
        
        client.create_collection(
            collection_name="google_ads_docs",
            vectors_config=rest.VectorParams(
                size=3072,  # OpenAI embedding size
                distance=rest.Distance.COSINE
            )
        )
        
        print("✅ Qdrant in-memory mode started successfully!")
        print("   Collection 'google_ads_docs' created")
        print("   Vector size: 3072 (OpenAI embedding size)")
        print("   Distance metric: Cosine")
        
        return client
        
    except Exception as e:
        print(f"❌ Error starting Qdrant: {e}")
        return None

def test_rag_with_memory_qdrant():
    """Test RAG system with in-memory Qdrant"""
    print("\nTesting RAG system with in-memory Qdrant...")
    
    try:
        from google_ads_new.rag_client import GoogleAdsRAGClient
        
        # Create RAG client with in-memory Qdrant
        rag_client = GoogleAdsRAGClient(
            collection_name="google_ads_docs",
            qdrant_url=":memory:"
        )
        
        print("✅ RAG client created successfully with in-memory Qdrant")
        
        # Test collection info
        stats = rag_client.get_collection_stats()
        print(f"   Collection stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing RAG: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("Qdrant In-Memory Setup for RAG System")
    print("="*50)
    
    # Check environment
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OPENAI_API_KEY not set")
        print("   Set it with: export OPENAI_API_KEY='your_key'")
        print()
    
    # Start in-memory Qdrant
    client = start_in_memory_qdrant()
    if not client:
        return
    
    # Test RAG system
    if test_rag_with_memory_qdrant():
        print("\n✅ RAG system is ready with in-memory Qdrant!")
        print("\nYou can now test the API endpoints:")
        print("curl -X POST 'http://localhost:8000/google-ads-new/api/rag/query/' \\")
        print("  -H 'Content-Type: application/json' \\")
        print("  -d '{\"query\": \"How do I get started with Google Ads API?\"}'")
    else:
        print("\n❌ RAG system test failed")

if __name__ == "__main__":
    main()

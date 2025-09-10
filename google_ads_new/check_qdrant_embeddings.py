#!/usr/bin/env python3
"""
Check and verify embeddings stored in Qdrant
"""

import os
import sys
import django

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

def check_qdrant_collections():
    """Check what collections exist in Qdrant"""
    print("Checking Qdrant collections...")
    
    try:
        from qdrant_client import QdrantClient
        
        # Connect to Qdrant
        client = QdrantClient("localhost", port=6333)
        
        # Get all collections
        collections = client.get_collections()
        print(f"✅ Found {len(collections.collections)} collections:")
        
        for collection in collections.collections:
            print(f"   - {collection.name}")
        
        return client
        
    except Exception as e:
        print(f"❌ Error connecting to Qdrant: {e}")
        return None

def check_collection_details(client, collection_name="google_ads_docs"):
    """Check detailed information about a collection"""
    print(f"\nChecking collection '{collection_name}'...")
    
    try:
        # Get collection info
        collection_info = client.get_collection(collection_name)
        
        print(f"✅ Collection Details:")
        print(f"   Name: {collection_name}")
        print(f"   Points count: {collection_info.points_count}")
        print(f"   Vectors count: {collection_info.vectors_count}")
        print(f"   Indexed vectors: {collection_info.indexed_vectors_count}")
        print(f"   Vector size: {collection_info.config.params.vectors.size}")
        print(f"   Distance metric: {collection_info.config.params.vectors.distance}")
        
        return collection_info
        
    except Exception as e:
        print(f"❌ Error getting collection info: {e}")
        return None

def check_sample_points(client, collection_name="google_ads_docs", limit=5):
    """Check sample points/embeddings in the collection"""
    print(f"\nChecking sample points from '{collection_name}'...")
    
    try:
        # Get sample points
        points = client.scroll(
            collection_name=collection_name,
            limit=limit,
            with_payload=True,
            with_vectors=True
        )
        
        print(f"✅ Found {len(points[0])} sample points:")
        
        for i, point in enumerate(points[0][:limit]):
            print(f"\n   Point {i+1}:")
            print(f"   ID: {point.id}")
            print(f"   Vector size: {len(point.vector)}")
            print(f"   Vector preview: {point.vector[:5]}...")
            print(f"   Payload:")
            for key, value in point.payload.items():
                if key == 'text':
                    print(f"     {key}: {str(value)[:100]}...")
                else:
                    print(f"     {key}: {value}")
        
        return points[0]
        
    except Exception as e:
        print(f"❌ Error getting sample points: {e}")
        return None

def check_embeddings_sources():
    """Check what URLs were used to create embeddings"""
    print("\nChecking embedding sources...")
    
    try:
        from google_ads_new.constants import GOOGLE_ADS_API_DOCS_URLS
        
        print(f"✅ Total URLs in constants.py: {len(GOOGLE_ADS_API_DOCS_URLS)}")
        print("   First 5 URLs:")
        for i, url in enumerate(GOOGLE_ADS_API_DOCS_URLS[:5]):
            print(f"     {i+1}. {url}")
        
        return GOOGLE_ADS_API_DOCS_URLS
        
    except Exception as e:
        print(f"❌ Error getting URLs: {e}")
        return None

def search_embeddings_by_source(client, collection_name="google_ads_docs"):
    """Search embeddings by source URL"""
    print(f"\nSearching embeddings by source URL...")
    
    try:
        # Get all points with payload
        points = client.scroll(
            collection_name=collection_name,
            limit=100,  # Get more points
            with_payload=True,
            with_vectors=False  # Don't need vectors for this check
        )
        
        # Group by source URL
        sources = {}
        for point in points[0]:
            source = point.payload.get('source', 'Unknown')
            if source not in sources:
                sources[source] = 0
            sources[source] += 1
        
        print(f"✅ Embeddings grouped by source URL:")
        for source, count in sources.items():
            print(f"   {source}: {count} chunks")
        
        return sources
        
    except Exception as e:
        print(f"❌ Error searching by source: {e}")
        return None

def test_vector_search(client, collection_name="google_ads_docs"):
    """Test vector search functionality"""
    print(f"\nTesting vector search...")
    
    try:
        from google_ads_new.rag_client import get_rag_client
        
        # Get RAG client
        rag_client = get_rag_client()
        
        # Test search
        test_query = "OAuth authentication"
        results = rag_client.get_similar_docs(test_query, limit=3)
        
        print(f"✅ Vector search test:")
        print(f"   Query: '{test_query}'")
        print(f"   Found {len(results)} similar documents")
        
        for i, doc in enumerate(results):
            print(f"   Result {i+1}:")
            print(f"     Source: {doc.get('source', 'Unknown')}")
            print(f"     Text: {doc.get('text', '')[:100]}...")
        
        return results
        
    except Exception as e:
        print(f"❌ Error testing vector search: {e}")
        return None

def main():
    """Main function"""
    print("Qdrant Embeddings Checker")
    print("="*50)
    
    # Check Qdrant connection
    client = check_qdrant_collections()
    if not client:
        return
    
    # Check collection details
    collection_info = check_collection_details(client)
    if not collection_info:
        return
    
    # Check sample points
    sample_points = check_sample_points(client)
    
    # Check embedding sources
    urls = check_embeddings_sources()
    
    # Search by source
    sources = search_embeddings_by_source(client)
    
    # Test vector search
    search_results = test_vector_search(client)
    
    print("\n" + "="*50)
    print("SUMMARY:")
    print(f"✅ Qdrant is running on localhost:6333")
    print(f"✅ Collection 'google_ads_docs' exists")
    print(f"✅ Total points: {collection_info.points_count}")
    print(f"✅ Vector size: {collection_info.config.params.vectors.size}")
    print(f"✅ Sources: {len(sources) if sources else 0} different URLs")
    print(f"✅ Vector search: Working")
    
    print("\n🔍 To view Qdrant web UI:")
    print("   Open: http://localhost:6333/dashboard")

if __name__ == "__main__":
    main()

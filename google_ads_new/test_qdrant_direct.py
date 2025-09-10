#!/usr/bin/env python3
"""
Test script showing how to use qdrant-client directly (no langchain-qdrant needed)
"""

import os
import sys
import django

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

def test_qdrant_direct():
    """Test qdrant-client directly"""
    print("Testing qdrant-client directly...")
    
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.http import models as rest
        import uuid
        
        # Connect to Qdrant
        client = QdrantClient("localhost", port=6333)
        print("✅ Connected to Qdrant successfully")
        
        # Create a test collection
        collection_name = "test_google_ads_docs"
        
        try:
            # Delete if exists
            client.delete_collection(collection_name)
            print(f"✅ Deleted existing collection: {collection_name}")
        except:
            pass
        
        # Create collection
        client.create_collection(
            collection_name=collection_name,
            vectors_config=rest.VectorParams(
                size=3072,  # OpenAI embedding size
                distance=rest.Distance.COSINE
            )
        )
        print(f"✅ Created collection: {collection_name}")
        
        # Insert some test data
        test_points = [
            rest.PointStruct(
                id=str(uuid.uuid4()),
                vector=[0.1] * 3072,  # Dummy vector
                payload={
                    "text": "Google Ads API allows you to create and manage campaigns",
                    "source": "https://developers.google.com/google-ads/api/docs/get-started/introduction",
                    "section": "getting_started"
                }
            ),
            rest.PointStruct(
                id=str(uuid.uuid4()),
                vector=[0.2] * 3072,  # Dummy vector
                payload={
                    "text": "OAuth 2.0 is used for authentication with Google Ads API",
                    "source": "https://developers.google.com/google-ads/api/docs/oauth/overview",
                    "section": "oauth"
                }
            )
        ]
        
        client.upsert(
            collection_name=collection_name,
            points=test_points
        )
        print("✅ Inserted test data")
        
        # Search for similar documents
        query_vector = [0.15] * 3072  # Dummy query vector
        results = client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=2
        )
        
        print(f"✅ Found {len(results)} similar documents:")
        for i, result in enumerate(results):
            print(f"  {i+1}. Score: {result.score:.3f}")
            print(f"     Text: {result.payload['text']}")
            print(f"     Source: {result.payload['source']}")
        
        # Get collection info
        collection_info = client.get_collection(collection_name)
        print(f"✅ Collection info:")
        print(f"   Points: {collection_info.points_count}")
        print(f"   Vectors: {collection_info.vectors_count}")
        
        # Clean up
        client.delete_collection(collection_name)
        print(f"✅ Cleaned up collection: {collection_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_usage_examples():
    """Show usage examples"""
    print("\n" + "="*60)
    print("Usage Examples with qdrant-client")
    print("="*60)
    
    print("""
# 1. Basic Setup
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

client = QdrantClient("localhost", port=6333)

# 2. Create Collection
client.create_collection(
    collection_name="google_ads_docs",
    vectors_config=rest.VectorParams(
        size=3072,  # OpenAI embedding size
        distance=rest.Distance.COSINE
    )
)

# 3. Insert Documents
points = [
    rest.PointStruct(
        id="1",
        vector=your_embedding_vector,
        payload={
            "text": "Your document text",
            "source": "https://example.com",
            "section": "getting_started"
        }
    )
]
client.upsert(collection_name="google_ads_docs", points=points)

# 4. Search Similar Documents
results = client.search(
    collection_name="google_ads_docs",
    query_vector=your_query_embedding,
    limit=5
)

# 5. Get Collection Info
info = client.get_collection("google_ads_docs")
print(f"Total points: {info.points_count}")
""")

def main():
    """Run the test"""
    print("Qdrant Direct Usage Test")
    print("="*40)
    
    # Check if Qdrant is running
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient("localhost", port=6333)
        client.get_collections()
        print("✅ Qdrant is running")
    except Exception as e:
        print(f"❌ Qdrant is not running: {e}")
        print("Start Qdrant with: docker run -p 6333:6333 qdrant/qdrant")
        return
    
    # Run test
    if test_qdrant_direct():
        print("\n✅ All tests passed!")
        print("You can use qdrant-client directly without langchain-qdrant")
    else:
        print("\n❌ Tests failed")
    
    show_usage_examples()

if __name__ == "__main__":
    main()

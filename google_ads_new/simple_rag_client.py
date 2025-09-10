"""
Simple RAG Client using qdrant-client directly (no langchain-qdrant dependency)
"""

import os
import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
import uuid

logger = logging.getLogger(__name__)

class SimpleGoogleAdsRAGClient:
    """Simple RAG client using qdrant-client directly"""
    
    def __init__(self, 
                 collection_name: str = "google_ads_docs",
                 qdrant_url: str = "http://localhost:6333",
                 vector_size: int = 3072):
        
        self.collection_name = collection_name
        self.qdrant_url = qdrant_url
        self.vector_size = vector_size
        
        # Initialize Qdrant client
        self.qdrant = QdrantClient(url=qdrant_url, prefer_grpc=False)
    
    def create_collection(self, recreate: bool = False):
        """Create or recreate the collection"""
        try:
            if recreate:
                logger.info(f"Recreating collection: {self.collection_name}")
                self.qdrant.recreate_collection(
                    collection_name=self.collection_name,
                    vectors_config=rest.VectorParams(
                        size=self.vector_size,
                        distance=rest.Distance.COSINE
                    )
                )
            else:
                # Check if collection exists
                collections = self.qdrant.get_collections()
                collection_names = [col.name for col in collections.collections]
                
                if self.collection_name not in collection_names:
                    logger.info(f"Creating collection: {self.collection_name}")
                    self.qdrant.create_collection(
                        collection_name=self.collection_name,
                        vectors_config=rest.VectorParams(
                            size=self.vector_size,
                            distance=rest.Distance.COSINE
                        )
                    )
                else:
                    logger.info(f"Collection {self.collection_name} already exists")
                    
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise
    
    def upsert_documents(self, documents: List[Dict[str, Any]], embeddings: List[List[float]], batch_size: int = 100):
        """Upsert documents to the vector store"""
        try:
            logger.info(f"Upserting {len(documents)} documents to vector store")
            
            # Process in batches
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i:i + batch_size]
                batch_embeddings = embeddings[i:i + batch_size]
                points = []
                
                # Create points
                for doc, embedding in zip(batch_docs, batch_embeddings):
                    point_id = str(uuid.uuid4())
                    point = rest.PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload={
                            "source": doc.get("source", ""),
                            "text": doc.get("text", ""),
                            "chunk": doc.get("chunk", 0),
                            "total_chunks": doc.get("total_chunks", 0),
                            "url_index": doc.get("url_index", 0),
                            "title": doc.get("title", ""),
                            "section": doc.get("section", "general")
                        }
                    )
                    points.append(point)
                
                # Upsert batch
                self.qdrant.upsert(
                    collection_name=self.collection_name,
                    points=points
                )
                
                logger.info(f"Upserted batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
            
            logger.info("Successfully upserted all documents")
            
        except Exception as e:
            logger.error(f"Error upserting documents: {e}")
            raise
    
    def search_similar(self, query_embedding: List[float], limit: int = 5, score_threshold: float = 0.7):
        """Search for similar documents"""
        try:
            # Search
            results = self.qdrant.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
    
    def get_collection_info(self):
        """Get collection information"""
        try:
            collection_info = self.qdrant.get_collection(self.collection_name)
            return {
                'name': self.collection_name,
                'vectors_count': collection_info.vectors_count,
                'indexed_vectors_count': collection_info.indexed_vectors_count,
                'points_count': collection_info.points_count
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return None
    
    def delete_collection(self):
        """Delete the collection"""
        try:
            self.qdrant.delete_collection(self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")

def create_simple_rag_client(collection_name: str = "google_ads_docs") -> SimpleGoogleAdsRAGClient:
    """Create a simple RAG client"""
    return SimpleGoogleAdsRAGClient(collection_name=collection_name)

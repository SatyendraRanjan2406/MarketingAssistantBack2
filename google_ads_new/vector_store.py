"""
Vector Store Handler for Google Ads Documentation
Handles embeddings creation and vector database operations
"""

import os
import uuid
import logging
from typing import List, Dict, Any
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from qdrant_client.http.exceptions import UnexpectedResponse

logger = logging.getLogger(__name__)

class GoogleAdsVectorStore:
    """Vector store handler for Google Ads documentation"""
    
    def __init__(self, 
                 collection_name: str = "google_ads_docs",
                 qdrant_url: str = "http://localhost:6333",
                 embedding_model: str = "text-embedding-3-large"):
        
        self.collection_name = collection_name
        self.qdrant_url = qdrant_url
        
        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings(model=embedding_model)
        
        # Initialize Qdrant client
        self.qdrant = QdrantClient(url=qdrant_url, prefer_grpc=False)
        
        # Vector dimension for text-embedding-3-large
        self.vector_size = 3072
        
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
    
    def upsert_documents(self, documents: List[Document], batch_size: int = 100):
        """Upsert documents to the vector store"""
        try:
            logger.info(f"Upserting {len(documents)} documents to vector store")
            
            # Process in batches
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i:i + batch_size]
                points = []
                
                # Create embeddings for batch
                texts = [doc.page_content for doc in batch_docs]
                vectors = self.embeddings.embed_documents(texts)
                
                # Create points
                for doc, vector in zip(batch_docs, vectors):
                    point_id = str(uuid.uuid4())
                    point = rest.PointStruct(
                        id=point_id,
                        vector=vector,
                        payload={
                            "source": doc.metadata.get("source", ""),
                            "text": doc.page_content,
                            "chunk": doc.metadata.get("chunk", 0),
                            "total_chunks": doc.metadata.get("total_chunks", 0),
                            "url_index": doc.metadata.get("url_index", 0),
                            "title": doc.metadata.get("title", ""),
                            "section": doc.metadata.get("section", "general")
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
    
    def search_similar(self, query: str, limit: int = 5, score_threshold: float = 0.7):
        """Search for similar documents"""
        try:
            # Create query embedding
            query_vector = self.embeddings.embed_query(query)
            
            # Search
            results = self.qdrant.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
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
                'name': collection_info.config.params.vectors.size,
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

def setup_vector_store(documents: List[Document], recreate: bool = False) -> GoogleAdsVectorStore:
    """Setup vector store with documents"""
    vector_store = GoogleAdsVectorStore()
    vector_store.create_collection(recreate=recreate)
    vector_store.upsert_documents(documents)
    return vector_store

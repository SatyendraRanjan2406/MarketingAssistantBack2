"""
RAG Client for Google Ads Documentation
Provides question-answering capabilities using LangChain and Qdrant
"""

import os
import logging
from typing import List, Dict, Any, Optional
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
# from langchain_qdrant import QdrantVectorStore
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
# from qdrant_client import QdrantClient

logger = logging.getLogger(__name__)

class GoogleAdsRAGClient:
    """RAG client for Google Ads documentation queries"""
    
    def __init__(self, 
                 collection_name: str = "google_ads_docs",
                 qdrant_url: str = "http://localhost:6333",
                 embedding_model: str = "text-embedding-3-large",
                 llm_model: str = "gpt-4o",
                 temperature: float = 0.0):
        
        self.collection_name = collection_name
        self.qdrant_url = qdrant_url
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(model=embedding_model)
        
        # Initialize Qdrant client
        self.qdrant_client = None
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=llm_model,
            temperature=temperature
        )
        
        # Initialize vector store
        self.vectorstore =None 
        #  QdrantVectorStore(
        #     client=self.qdrant_client,
        #     collection_name=self.collection_name,
        #     embedding=self.embeddings
        # )
        
        # Initialize retriever
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": 4},
            search_type="similarity"
        )
        
        # Create custom prompt
        self.prompt_template = self._create_prompt_template()
        
        # Initialize QA chain
        self.qa_chain = self._create_qa_chain()
    
    def _create_prompt_template(self) -> PromptTemplate:
        """Create custom prompt template for Google Ads queries"""
        template = """You are a helpful assistant specialized in Google Ads API documentation. 
        Use the following pieces of context to answer the question about Google Ads API.
        If you don't know the answer based on the context, just say that you don't know, don't try to make up an answer.
        
        Context:
        {context}
        
        Question: {question}
        
        Answer: Provide a detailed, accurate answer based on the Google Ads API documentation. 
        Include relevant code examples, API endpoints, and best practices when applicable.
        If the question is about specific implementation details, provide step-by-step guidance.
        """
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def _create_qa_chain(self) -> RetrievalQA:
        """Create the QA chain"""
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",  # Use 'stuff' instead of 'map_rerank' for stability
            retriever=self.retriever,
            return_source_documents=True,
            chain_type_kwargs={
                "prompt": self.prompt_template
            }
        )
    
    def query(self, question: str) -> Dict[str, Any]:
        """Query the RAG system"""
        try:
            logger.info(f"Processing query: {question}")
            
            # Run the QA chain
            result = self.qa_chain({"query": question})
            
            # Extract relevant information
            answer = result.get("result", "")
            
            # Get sources directly from Qdrant for better metadata
            similar_docs = self.get_similar_docs(question, limit=4)
            sources = []
            for doc in similar_docs:
                source_info = {
                    "source": doc.get("source", ""),
                    "chunk": doc.get("chunk", 0),
                    "section": doc.get("section", "general"),
                    "text_preview": doc.get("text", "")[:200] + "..." if len(doc.get("text", "")) > 200 else doc.get("text", "")
                }
                sources.append(source_info)
            
            return {
                "answer": answer,
                "sources": sources,
                "query": question,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "answer": f"Sorry, I encountered an error while processing your query: {str(e)}",
                "sources": [],
                "query": question,
                "success": False,
                "error": str(e)
            }
    
    def get_similar_docs(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get similar documents without generating an answer"""
        try:
            # Get embedding for the query
            query_embedding = self.embeddings.embed_query(query)
            
            # Search directly in Qdrant
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                with_payload=True
            )
            
            # Convert Qdrant results to our format
            similar_docs = []
            for result in search_results:
                similar_docs.append({
                    "source": result.payload.get("source", ""),
                    "chunk": result.payload.get("chunk", 0),
                    "section": result.payload.get("section", "general"),
                    "text": result.payload.get("text", ""),
                    "metadata": {
                        "source": result.payload.get("source", ""),
                        "chunk": result.payload.get("chunk", 0),
                        "total_chunks": result.payload.get("total_chunks", 0),
                        "section": result.payload.get("section", "general"),
                        "title": result.payload.get("title", ""),
                        "url_index": result.payload.get("url_index", 0),
                        "_id": str(result.id),
                        "_collection_name": self.collection_name
                    }
                })
            
            return similar_docs
            
        except Exception as e:
            logger.error(f"Error getting similar documents: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            collection_info = self.qdrant_client.get_collection(self.collection_name)
            return {
                "collection_name": self.collection_name,
                "total_points": collection_info.points_count,
                "indexed_vectors": collection_info.indexed_vectors_count,
                "vectors_count": collection_info.vectors_count
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"error": str(e)}

# Global RAG client instance
_rag_client = None

def get_rag_client() -> GoogleAdsRAGClient:
    """Get or create the global RAG client instance"""
    global _rag_client
    if _rag_client is None:
        _rag_client = GoogleAdsRAGClient()
    return _rag_client

def initialize_rag_client(collection_name: str = "google_ads_docs") -> GoogleAdsRAGClient:
    """Initialize the RAG client with a specific collection"""
    global _rag_client
    _rag_client = GoogleAdsRAGClient(collection_name=collection_name)
    return _rag_client

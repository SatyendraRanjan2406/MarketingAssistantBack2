"""
RAG (Retrieval-Augmented Generation) Service for Google Ads Analysis
Provides intelligent context retrieval and augmentation for better AI responses
"""

import os
import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import hashlib
from datetime import datetime

# LangChain imports
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.document_loaders import (
    TextLoader, PyPDFLoader, Docx2txtLoader, 
    UnstructuredMarkdownLoader, CSVLoader
)
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

# Local imports
from .openai_service import GoogleAdsOpenAIService

logger = logging.getLogger(__name__)

class GoogleAdsRAGService:
    """RAG service for Google Ads analysis with intelligent context selection"""
    
    def __init__(self, user, vector_db_path: str = "vector_db"):
        self.user = user
        self.vector_db_path = Path(vector_db_path)
        self.vector_db_path.mkdir(exist_ok=True)
        
        # Initialize embeddings
        self.embeddings = self._initialize_embeddings()
        
        # Initialize vector store
        self.vectorstore = self._initialize_vectorstore()
        
        # Initialize OpenAI service for context selection
        self.openai_service = GoogleAdsOpenAIService()
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Document metadata
        self.document_sources = {
            "google_ads_official": "Official Google Ads documentation and help center",
            "best_practices": "Industry best practices and optimization guides",
            "case_studies": "Real-world success stories and examples",
            "performance_data": "Historical performance data and benchmarks",
            "creative_guidelines": "Ad creative and design guidelines",
            "technical_specs": "Technical specifications and requirements"
        }
        
        logger.info("RAG service initialized successfully")
    
    def _initialize_embeddings(self):
        """Initialize embeddings with fallback strategy"""
        try:
            # Try OpenAI embeddings first
            if os.getenv('OPENAI_API_KEY'):
                logger.info("Using OpenAI embeddings")
                return OpenAIEmbeddings()
            else:
                # Fallback to local embeddings
                logger.info("Using local HuggingFace embeddings")
                return HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2",
                    model_kwargs={'device': 'cpu'}
                )
        except Exception as e:
            logger.error(f"Error initializing embeddings: {e}")
            # Final fallback to basic embeddings
            logger.info("Using basic sentence transformers embeddings")
            return HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
    
    def _initialize_vectorstore(self):
        """Initialize or load existing vector store"""
        try:
            if (self.vector_db_path / "chroma.sqlite3").exists():
                logger.info("Loading existing vector store")
                return Chroma(
                    persist_directory=str(self.vector_db_path),
                    embedding_function=self.embeddings
                )
            else:
                logger.info("Creating new vector store")
                return Chroma(
                    persist_directory=str(self.vector_db_path),
                    embedding_function=self.embeddings
                )
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            raise
    
    def add_documents(self, documents: List[Document], source: str = "custom"):
        """Add documents to the vector store"""
        try:
            # Split documents into chunks
            chunks = self.text_splitter.split_documents(documents)
            
            # Add metadata to chunks
            for chunk in chunks:
                chunk.metadata.update({
                    "source": source,
                    "added_at": datetime.now().isoformat(),
                    "user_id": str(self.user.id)
                })
            
            # Add to vector store
            self.vectorstore.add_documents(chunks)
            self.vectorstore.persist()
            
            logger.info(f"Added {len(chunks)} chunks from {len(documents)} documents")
            return len(chunks)
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def add_text_file(self, file_path: str, source: str = "custom"):
        """Add a text file to the vector store"""
        try:
            loader = TextLoader(file_path)
            documents = loader.load()
            return self.add_documents(documents, source)
        except Exception as e:
            logger.error(f"Error adding text file {file_path}: {e}")
            raise
    
    def add_pdf_file(self, file_path: str, source: str = "custom"):
        """Add a PDF file to the vector store"""
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            return self.add_documents(documents, source)
        except Exception as e:
            logger.error(f"Error adding PDF file {file_path}: {e}")
            raise
    
    def add_markdown_file(self, file_path: str, source: str = "custom"):
        """Add a markdown file to the vector store"""
        try:
            loader = UnstructuredMarkdownLoader(file_path)
            documents = loader.load()
            return self.add_documents(documents, source)
        except Exception as e:
            logger.error(f"Error adding markdown file {file_path}: {e}")
            raise
    
    def add_csv_file(self, file_path: str, source: str = "custom"):
        """Add a CSV file to the vector store"""
        try:
            loader = CSVLoader(file_path)
            documents = loader.load()
            return self.add_documents(documents, source)
        except Exception as e:
            logger.error(f"Error adding CSV file {file_path}: {e}")
            raise
    
    def search_documents(self, query: str, k: int = 5, filters: Dict = None) -> List[Document]:
        """Search for relevant documents"""
        try:
            if filters:
                results = self.vectorstore.similarity_search(
                    query, 
                    k=k,
                    filter=filters
                )
            else:
                results = self.vectorstore.similarity_search(query, k=k)
            
            logger.info(f"Retrieved {len(results)} documents for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def smart_context_selection(self, query: str, user_data: Dict, max_context_length: int = 4000) -> Tuple[str, bool]:
        """
        Smart context selection - decides whether to use RAG or direct OpenAI
        Returns: (context_string, use_rag)
        """
        try:
            # Analyze query complexity and type
            query_analysis = self._analyze_query(query)
            
            # Check if RAG would be helpful
            rag_helpful = self._is_rag_helpful(query_analysis, user_data)
            
            if not rag_helpful:
                logger.info("RAG not helpful for this query, using direct OpenAI")
                return "", False
            
            # Retrieve relevant context
            relevant_docs = self.search_documents(query, k=3)
            
            if not relevant_docs:
                logger.info("No relevant documents found, using direct OpenAI")
                return "", False
            
            # Build context string
            context = self._build_context_string(relevant_docs, query, user_data)
            
            # Check context length
            if len(context) > max_context_length:
                # Truncate context intelligently
                context = self._truncate_context(context, max_context_length)
            
            logger.info(f"Using RAG with context length: {len(context)}")
            return context, True
            
        except Exception as e:
            logger.error(f"Error in smart context selection: {e}")
            return "", False
    
    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query to determine complexity and type"""
        analysis = {
            "length": len(query),
            "complexity": "simple",
            "type": "general",
            "requires_knowledge": False,
            "requires_data": False
        }
        
        # Analyze query length
        if len(query) > 100:
            analysis["complexity"] = "complex"
        elif len(query) > 50:
            analysis["complexity"] = "medium"
        
        # Analyze query type
        knowledge_keywords = [
            "best practice", "guideline", "recommendation", "how to",
            "strategy", "optimization", "industry standard", "case study"
        ]
        
        data_keywords = [
            "performance", "metrics", "data", "analysis", "report",
            "campaign", "budget", "conversion", "roas", "ctr"
        ]
        
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in knowledge_keywords):
            analysis["requires_knowledge"] = True
            analysis["type"] = "knowledge"
        
        if any(keyword in query_lower for keyword in data_keywords):
            analysis["requires_data"] = True
            analysis["type"] = "data"
        
        return analysis
    
    def _is_rag_helpful(self, query_analysis: Dict, user_data: Dict) -> bool:
        """Determine if RAG would be helpful for this query"""
        
        # RAG is helpful for knowledge-based queries
        if query_analysis["requires_knowledge"]:
            return True
        
        # RAG is helpful for complex queries
        if query_analysis["complexity"] == "complex":
            return True
        
        # RAG is helpful when user has limited data
        if query_analysis["requires_data"] and not user_data.get("has_campaigns", False):
            return True
        
        # RAG is helpful for strategic questions
        strategic_keywords = [
            "strategy", "planning", "approach", "methodology",
            "framework", "process", "workflow", "roadmap"
        ]
        
        if any(keyword in query_analysis.get("query", "").lower() for keyword in strategic_keywords):
            return True
        
        return False
    
    def _build_context_string(self, documents: List[Document], query: str, user_data: Dict) -> str:
        """Build context string from retrieved documents"""
        context_parts = []
        
        # Add document context
        for i, doc in enumerate(documents):
            source = doc.metadata.get("source", "unknown")
            context_parts.append(f"Document {i+1} (Source: {source}):\n{doc.page_content}\n")
        
        # Add user data context if relevant
        if user_data.get("has_campaigns"):
            context_parts.append(f"User has {user_data.get('campaign_count', 0)} active campaigns")
        
        # Add query context
        context_parts.append(f"User Query: {query}")
        
        return "\n".join(context_parts)
    
    def _truncate_context(self, context: str, max_length: int) -> str:
        """Intelligently truncate context while preserving important parts"""
        if len(context) <= max_length:
            return context
        
        # Split into parts
        parts = context.split("\n\n")
        
        # Keep the most recent/important parts
        truncated_parts = []
        current_length = 0
        
        for part in reversed(parts):
            if current_length + len(part) + 2 <= max_length:
                truncated_parts.insert(0, part)
                current_length += len(part) + 2
            else:
                break
        
        # Add truncation indicator
        truncated_context = "\n\n".join(truncated_parts)
        truncated_context += f"\n\n[Context truncated for length. Total available: {len(context)} chars]"
        
        return truncated_context
    
    def get_rag_response(self, query: str, context: str, user_data: Dict) -> Dict[str, Any]:
        """Generate RAG-enhanced response using OpenAI"""
        try:
            # Create augmented prompt
            augmented_prompt = self._create_augmented_prompt(query, context, user_data)
            
            # Generate response
            response = self.openai_service.generate_analysis_response(
                "RAG_ANALYSIS",
                {"query": query, "context": context, "user_data": user_data},
                augmented_prompt
            )
            
            # Add RAG metadata
            response["rag_metadata"] = {
                "context_used": True,
                "context_length": len(context),
                "context_sources": self._extract_context_sources(context),
                "generation_method": "rag"
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating RAG response: {e}")
            raise
    
    def _create_augmented_prompt(self, query: str, context: str, user_data: Dict) -> str:
        """Create augmented prompt with RAG context"""
        prompt = f"""
        You are a Google Ads expert analyst with access to authoritative documentation and best practices.
        
        CONTEXT FROM KNOWLEDGE BASE:
        {context}
        
        USER'S GOOGLE ADS DATA:
        {json.dumps(user_data, indent=2)}
        
        USER QUERY:
        {query}
        
        INSTRUCTIONS:
        1. Use the provided context to give authoritative, accurate answers
        2. Reference specific best practices and guidelines when applicable
        3. Combine knowledge base insights with user's actual data
        4. Provide actionable recommendations based on both sources
        5. Structure your response with multiple UI blocks (charts, tables, lists, actions, text)
        6. Always cite sources when making recommendations
        
        Generate a comprehensive, authoritative response that leverages both the knowledge base and user data.
        """
        
        return prompt
    
    def _extract_context_sources(self, context: str) -> List[str]:
        """Extract source information from context"""
        sources = []
        lines = context.split("\n")
        
        for line in lines:
            if "Source:" in line:
                source = line.split("Source:")[1].strip()
                if source and source not in sources:
                    sources.append(source)
        
        return sources
    
    def get_direct_openai_response(self, query: str, user_data: Dict) -> Dict[str, Any]:
        """Generate direct OpenAI response when RAG is not helpful"""
        try:
            response = self.openai_service.generate_analysis_response(
                "DIRECT_ANALYSIS",
                {"query": query, "user_data": user_data},
                f"User query: {query}\nUser data: {json.dumps(user_data, indent=2)}"
            )
            
            # Add direct response metadata
            response["rag_metadata"] = {
                "context_used": False,
                "context_length": 0,
                "context_sources": [],
                "generation_method": "direct"
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating direct OpenAI response: {e}")
            raise
    
    def get_hybrid_response(self, query: str, user_data: Dict) -> Dict[str, Any]:
        """Get hybrid response using smart context selection"""
        try:
            # Smart context selection
            context, use_rag = self.smart_context_selection(query, user_data)
            
            if use_rag:
                # Use RAG with context
                response = self.get_rag_response(query, context, user_data)
                response["response_type"] = "rag_enhanced"
            else:
                # Use direct OpenAI
                response = self.get_direct_openai_response(query, user_data)
                response["response_type"] = "direct_openai"
            
            # Add hybrid metadata
            response["hybrid_metadata"] = {
                "context_selection": "rag" if use_rag else "direct",
                "context_length": len(context) if use_rag else 0,
                "selection_reason": self._get_selection_reason(query, use_rag, user_data)
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating hybrid response: {e}")
            raise
    
    def _get_selection_reason(self, query: str, use_rag: bool, user_data: Dict) -> str:
        """Get reason for context selection decision"""
        if use_rag:
            return "RAG selected due to knowledge requirements or query complexity"
        else:
            return "Direct OpenAI selected due to simple query or data-focused request"
    
    def get_vectorstore_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        try:
            # Get collection info
            collection = self.vectorstore._collection
            
            stats = {
                "total_documents": collection.count(),
                "embedding_dimension": collection.embedding_function.dimension if hasattr(collection.embedding_function, 'dimension') else "unknown",
                "database_path": str(self.vector_db_path),
                "last_updated": datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting vector store stats: {e}")
            return {"error": str(e)}
    
    def clear_vectorstore(self):
        """Clear all documents from vector store"""
        try:
            # Delete the vector store directory
            import shutil
            if self.vector_db_path.exists():
                shutil.rmtree(self.vector_db_path)
                self.vector_db_path.mkdir(exist_ok=True)
            
            # Reinitialize vector store
            self.vectorstore = self._initialize_vectorstore()
            
            logger.info("Vector store cleared successfully")
            
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}")
            raise

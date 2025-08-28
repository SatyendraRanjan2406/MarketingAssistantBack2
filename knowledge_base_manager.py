#!/usr/bin/env python3
"""
Knowledge Base Manager with Automatic Vector Embedding and Image Generation
Monitors a folder for new knowledge base files, creates embeddings, generates images, and integrates with Google AI chatbot
"""

import os
import sys
import time
import hashlib
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import hashlib
import requests
import base64

# Add the project directory to Python path
sys.path.append('/Users/satyendra/marketing_assistant_back')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')

try:
    import django
    django.setup()
    from django.contrib.auth.models import User
    from google_ads_new.models import KBDocument
    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False
    print("⚠️  Django not available - running in standalone mode")

# LangChain imports
try:
    from langchain_openai import OpenAIEmbeddings
    from langchain_community.vectorstores import Chroma
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    from langchain_openai import ChatOpenAI
    from langchain.chains import ConversationalRetrievalChain
    from langchain.memory import ConversationBufferMemory
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("⚠️  LangChain not available - install with: pip install langchain langchain-openai")

class ImageGenerator:
    """Handles image generation using OpenAI DALL-E API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/images/generations"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_image(self, prompt: str, size: str = "1024x1024", quality: str = "standard", style: str = "vivid") -> Optional[str]:
        """Generate an image using DALL-E and return the URL"""
        try:
            payload = {
                "model": "dall-e-3",
                "prompt": prompt,
                "size": size,
                "quality": quality,
                "style": style,
                "n": 1
            }
            
            response = requests.post(self.base_url, headers=self.headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            if result.get("data") and len(result["data"]) > 0:
                image_url = result["data"][0]["url"]
                return image_url
            
            return None
            
        except Exception as e:
            logging.error(f"Error generating image: {e}")
            return None
    
    def generate_poster_image(self, title: str, description: str, template_type: str, color_scheme: str, target_audience: str) -> Optional[str]:
        """Generate a poster image based on creative specifications"""
        prompt = f"""Create a professional poster design for "{title}". 
        
        Description: {description}
        Template Type: {template_type}
        Color Scheme: {color_scheme}
        Target Audience: {target_audience}
        
        Style: Modern, professional, educational poster with clean typography, balanced layout, and visual hierarchy. 
        Include placeholder elements for text and imagery that would be added later.
        Make it suitable for printing and digital use."""
        
        return self.generate_image(prompt, size="1024x1024", quality="standard", style="vivid")
    
    def generate_creative_image(self, title: str, description: str, features: List[str], color_scheme: str) -> Optional[str]:
        """Generate a creative image based on specifications"""
        features_text = ", ".join(features[:3])  # Limit to first 3 features
        
        prompt = f"""Create a creative visual design for "{title}".
        
        Description: {description}
        Key Features: {features_text}
        Color Scheme: {color_scheme}
        
        Style: Creative, engaging, modern design that captures attention. 
        Include visual elements that represent the concept described.
        Make it suitable for marketing and promotional materials."""
        
        return self.generate_image(prompt, size="1024x1024", quality="standard", style="vivid")

class KnowledgeBaseManager:
    """Manages knowledge base files and vector embeddings with image generation"""
    
    def __init__(self, 
                 docs_folder: str = "knowledge_base_docs",
                 embeddings_folder: str = "knowledge_base_docs/embeddings",
                 processed_folder: str = "knowledge_base_docs/processed",
                 logs_folder: str = "knowledge_base_docs/logs"):
        
        self.docs_folder = Path(docs_folder)
        self.embeddings_folder = Path(embeddings_folder)
        self.processed_folder = Path(processed_folder)
        self.logs_folder = Path(logs_folder)
        
        # Create folders if they don't exist
        self.docs_folder.mkdir(exist_ok=True)
        self.embeddings_folder.mkdir(exist_ok=True)
        self.processed_folder.mkdir(exist_ok=True)
        self.logs_folder.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Initialize embeddings
        self.embeddings = None
        self.vectorstore = None
        self.initialize_embeddings()
        
        # Initialize image generator
        self.image_generator = None
        self.initialize_image_generator()
        
        # File tracking
        self.processed_files = self.load_processed_files()
        self.file_hashes = self.load_file_hashes()
        
        # Supported file types
        self.supported_extensions = {'.md', '.txt', '.pdf', '.docx', '.html'}
        
        # Initialize Django if available
        if DJANGO_AVAILABLE:
            self.django_user = self.get_or_create_django_user()
        
        self.logger.info("Knowledge Base Manager initialized successfully")
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_file = self.logs_folder / f"kb_manager_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def initialize_image_generator(self):
        """Initialize the image generator with OpenAI API key"""
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            try:
                self.image_generator = ImageGenerator(openai_api_key)
                self.logger.info("Image generator initialized successfully")
            except Exception as e:
                self.logger.error(f"Error initializing image generator: {e}")
                self.image_generator = None
        else:
            self.logger.warning("OPENAI_API_KEY not found - image generation disabled")
    
    def get_or_create_django_user(self) -> Optional[User]:
        """Get or create Django user for knowledge base operations"""
        if not DJANGO_AVAILABLE:
            return None
        
        try:
            user, created = User.objects.get_or_create(
                username='kb_manager',
                defaults={
                    'email': 'kb_manager@example.com',
                    'first_name': 'Knowledge Base',
                    'last_name': 'Manager'
                }
            )
            if created:
                user.set_password('kb_manager_123')
                user.save()
                self.logger.info("Created Django user: kb_manager")
            return user
        except Exception as e:
            self.logger.error(f"Error creating Django user: {e}")
            return None
    
    def initialize_embeddings(self):
        """Initialize OpenAI embeddings and vector store"""
        if not LANGCHAIN_AVAILABLE:
            self.logger.warning("LangChain not available - embeddings disabled")
            return
        
        try:
            # Initialize OpenAI embeddings
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if not openai_api_key:
                self.logger.error("OPENAI_API_KEY not found in environment variables")
                return
            
            self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
            
            # Initialize or load existing vector store
            self.vectorstore = Chroma(
                persist_directory=str(self.embeddings_folder),
                embedding_function=self.embeddings
            )
            
            self.logger.info("Embeddings and vector store initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing embeddings: {e}")
    
    def load_processed_files(self) -> set:
        """Load list of already processed files"""
        processed_file = self.processed_folder / "processed_files.json"
        if processed_file.exists():
            try:
                with open(processed_file, 'r') as f:
                    return set(json.load(f))
            except Exception as e:
                self.logger.error(f"Error loading processed files: {e}")
        return set()
    
    def save_processed_files(self):
        """Save list of processed files"""
        processed_file = self.processed_folder / "processed_files.json"
        try:
            with open(processed_file, 'w') as f:
                json.dump(list(self.processed_files), f)
        except Exception as e:
            self.logger.error(f"Error saving processed files: {e}")
    
    def load_file_hashes(self) -> Dict[str, str]:
        """Load file hashes to detect changes"""
        hash_file = self.processed_folder / "file_hashes.json"
        if hash_file.exists():
            try:
                with open(hash_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading file hashes: {e}")
        return {}
    
    def save_file_hashes(self):
        """Save file hashes"""
        hash_file = self.processed_folder / "file_hashes.json"
        try:
            with open(hash_file, 'w') as f:
                json.dump(self.file_hashes, f)
        except Exception as e:
            self.logger.error(f"Error saving file hashes: {e}")
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file content"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculating file hash: {e}")
            return ""
    
    def is_file_changed(self, file_path: Path) -> bool:
        """Check if file has changed since last processing"""
        current_hash = self.calculate_file_hash(file_path)
        file_key = str(file_path)
        
        if file_key not in self.file_hashes:
            return True
        
        return self.file_hashes[file_key] != current_hash
    
    def should_process_file(self, file_path: Path) -> bool:
        """Determine if file should be processed"""
        # Check if file extension is supported
        if file_path.suffix.lower() not in self.supported_extensions:
            return False
        
        # Check if file is already processed and unchanged
        if str(file_path) in self.processed_files and not self.is_file_changed(file_path):
            return False
        
        return True
    
    def read_file_content(self, file_path: Path) -> str:
        """Read content from different file types"""
        try:
            if file_path.suffix.lower() == '.md':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            elif file_path.suffix.lower() == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            elif file_path.suffix.lower() == '.html':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                self.logger.warning(f"Unsupported file type: {file_path.suffix}")
                return ""
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            return ""
    
    def extract_metadata(self, file_path: Path, content: str) -> Dict[str, Any]:
        """Extract metadata from file content and path"""
        metadata = {
            "source_file": str(file_path),
            "file_type": file_path.suffix.lower(),
            "file_size": len(content),
            "created_at": datetime.now().isoformat(),
            "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        }
        
        # Try to extract title from markdown
        if file_path.suffix.lower() == '.md':
            lines = content.split('\n')
            for line in lines:
                if line.startswith('# '):
                    metadata["title"] = line[2:].strip()
                    break
            if "title" not in metadata:
                metadata["title"] = file_path.stem
        
        # Try to extract tags from markdown
        if file_path.suffix.lower() == '.md':
            for line in lines:
                if line.startswith('**Tags**:'):
                    tags = line.replace('**Tags**:', '').strip()
                    metadata["tags"] = [tag.strip() for tag in tags.split(',')]
                    break
        
        return metadata
    
    def create_embeddings(self, content: str, metadata: Dict[str, Any]) -> bool:
        """Create vector embeddings for the content"""
        if not LANGCHAIN_AVAILABLE or not self.embeddings:
            self.logger.warning("Embeddings not available - skipping")
            return False
        
        try:
            # Split text into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
            
            chunks = text_splitter.split_text(content)
            
            # Create documents with metadata
            documents = []
            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        **metadata,
                        "chunk_id": i,
                        "total_chunks": len(chunks)
                    }
                )
                documents.append(doc)
            
            # Add to vector store
            self.vectorstore.add_documents(documents)
            
            # Persist the vector store
            self.vectorstore.persist()
            
            self.logger.info(f"Created embeddings for {len(chunks)} chunks")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating embeddings: {e}")
            return False
    
    def add_to_django_kb(self, file_path: Path, content: str, metadata: Dict[str, Any]) -> bool:
        """Add document to Django knowledge base"""
        if not DJANGO_AVAILABLE or not self.django_user:
            return False
        
        try:
            # Check if document already exists
            existing_doc = KBDocument.objects.filter(
                title=metadata.get("title", file_path.stem),
                company_id=1
            ).first()
            
            if existing_doc:
                # Update existing document
                existing_doc.content = content
                existing_doc.metadata = metadata
                existing_doc.save()
                self.logger.info(f"Updated Django KB document: {metadata.get('title', file_path.stem)}")
            else:
                # Create new document
                kb_doc = KBDocument.objects.create(
                    company_id=1,
                    title=metadata.get("title", file_path.stem),
                    content=content,
                    document_type="knowledge_base",
                    url="",
                    metadata=metadata
                )
                self.logger.info(f"Created Django KB document: {kb_doc.title}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding to Django KB: {e}")
            return False
    
    def process_file(self, file_path: Path) -> bool:
        """Process a single knowledge base file"""
        try:
            self.logger.info(f"Processing file: {file_path}")
            
            # Read file content
            content = self.read_file_content(file_path)
            if not content:
                self.logger.warning(f"Empty or unreadable file: {file_path}")
                return False
            
            # Extract metadata
            metadata = self.extract_metadata(file_path, content)
            
            # Create embeddings
            embeddings_success = self.create_embeddings(content, metadata)
            
            # Add to Django knowledge base
            django_success = self.add_to_django_kb(file_path, content, metadata)
            
            # Mark as processed
            self.processed_files.add(str(file_path))
            self.file_hashes[str(file_path)] = self.calculate_file_hash(file_path)
            
            # Save state
            self.save_processed_files()
            self.save_file_hashes()
            
            # Move to processed folder
            processed_path = self.processed_folder / file_path.name
            if file_path.exists():
                file_path.rename(processed_path)
            
            self.logger.info(f"Successfully processed: {file_path.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {e}")
            return False
    
    def process_all_files(self):
        """Process all files in the knowledge base folder"""
        self.logger.info("Processing all files in knowledge base folder")
        
        files_to_process = []
        for file_path in self.docs_folder.iterdir():
            if file_path.is_file() and self.should_process_file(file_path):
                files_to_process.append(file_path)
        
        if not files_to_process:
            self.logger.info("No new files to process")
            return
        
        self.logger.info(f"Found {len(files_to_process)} files to process")
        
        for file_path in files_to_process:
            self.process_file(file_path)
    
    def start_file_monitoring(self):
        """Start monitoring the knowledge base folder for new files"""
        if not LANGCHAIN_AVAILABLE:
            self.logger.warning("LangChain not available - file monitoring disabled")
            return
        
        class KnowledgeBaseHandler(FileSystemEventHandler):
            def __init__(self, manager):
                self.manager = manager
            
            def on_created(self, event):
                if not event.is_directory:
                    file_path = Path(event.src_path)
                    if self.manager.should_process_file(file_path):
                        self.manager.logger.info(f"New file detected: {file_path}")
                        # Wait a bit for file to be fully written
                        time.sleep(2)
                        self.manager.process_file(file_path)
            
            def on_modified(self, event):
                if not event.is_directory:
                    file_path = Path(event.src_path)
                    if self.manager.should_process_file(file_path):
                        self.manager.logger.info(f"File modified: {file_path}")
                        self.manager.process_file(file_path)
        
        event_handler = KnowledgeBaseHandler(self)
        observer = Observer()
        observer.schedule(event_handler, str(self.docs_folder), recursive=False)
        observer.start()
        
        self.logger.info(f"Started monitoring folder: {self.docs_folder}")
        return observer
    
    def search_knowledge_base(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search the knowledge base using vector similarity"""
        if not self.vectorstore:
            self.logger.warning("Vector store not available")
            return []
        
        try:
            results = self.vectorstore.similarity_search_with_score(query, k=top_k)
            
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": float(score)
                })
            
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Error searching knowledge base: {e}")
            return []
    
    def generate_creative_images(self, creative_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate images for creative blocks and add image URLs"""
        if not self.image_generator:
            self.logger.warning("Image generator not available")
            return creative_data
        
        try:
            # Generate image for creative blocks
            if "blocks" in creative_data:
                for block in creative_data["blocks"]:
                    if block.get("type") == "creative":
                        # Generate image for this creative block
                        image_url = self.image_generator.generate_poster_image(
                            title=block.get("title", ""),
                            description=block.get("description", ""),
                            template_type=block.get("template_type", ""),
                            color_scheme=block.get("color_scheme", ""),
                            target_audience=block.get("target_audience", "")
                        )
                        
                        if image_url:
                            block["image_url"] = image_url
                            self.logger.info(f"Generated image for creative block: {block.get('title')}")
                        else:
                            block["image_url"] = None
                            self.logger.warning(f"Failed to generate image for: {block.get('title')}")
            
            return creative_data
            
        except Exception as e:
            self.logger.error(f"Error generating creative images: {e}")
            return creative_data
    
    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        stats = {
            "total_files_processed": len(self.processed_files),
            "embeddings_available": self.embeddings is not None,
            "vector_store_available": self.vectorstore is not None,
            "image_generation_available": self.image_generator is not None,
            "django_integration": DJANGO_AVAILABLE,
            "langchain_available": LANGCHAIN_AVAILABLE
        }
        
        if self.vectorstore:
            try:
                # Get collection info
                collection = self.vectorstore._collection
                stats["total_embeddings"] = collection.count()
                stats["embedding_dimensions"] = collection.metadata.get("hnsw:space", "unknown")
            except Exception as e:
                stats["total_embeddings"] = "unknown"
                stats["embedding_dimensions"] = "unknown"
        
        return stats

def main():
    """Main function to run the knowledge base manager"""
    print("🚀 Starting Knowledge Base Manager with Image Generation...")
    
    # Initialize manager
    manager = KnowledgeBaseManager()
    
    # Process existing files
    manager.process_all_files()
    
    # Show stats
    stats = manager.get_knowledge_base_stats()
    print("\n📊 Knowledge Base Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Start file monitoring
    observer = manager.start_file_monitoring()
    
    try:
        print("\n👀 Monitoring knowledge base folder for new files...")
        print("   Press Ctrl+C to stop")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping Knowledge Base Manager...")
        if observer:
            observer.stop()
            observer.join()
        print("✅ Knowledge Base Manager stopped")

if __name__ == "__main__":
    main()

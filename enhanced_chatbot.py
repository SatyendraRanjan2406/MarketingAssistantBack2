#!/usr/bin/env python3
"""
Enhanced Google AI Chatbot with Knowledge Base Integration and Image Generation
Uses LangChain, ChatGPT, vector embeddings, and DALL-E for intelligent responses with images
"""

import os
import sys
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import requests

# Add the project directory to Python path
sys.path.append('/Users/satyendra/marketing_assistant_back')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')

try:
    import django
    django.setup()
    from django.contrib.auth.models import User
    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False
    print("⚠️  Django not available - running in standalone mode")

# LangChain imports
try:
    from langchain_openai import OpenAIEmbeddings, ChatOpenAI
    from langchain_community.vectorstores import Chroma
    from langchain.chains import ConversationalRetrievalChain
    from langchain.memory import ConversationBufferMemory
    from langchain.prompts import PromptTemplate
    from langchain.schema import Document
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
            print(f"❌ Error generating image: {e}")
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

class EnhancedGoogleAIChatbot:
    """Enhanced chatbot with knowledge base integration and image generation"""
    
    def __init__(self, 
                 embeddings_folder: str = "knowledge_base_docs/embeddings",
                 openai_model: str = "gpt-4o-mini"):
        
        self.embeddings_folder = Path(embeddings_folder)
        self.openai_model = openai_model
        
        # Initialize components
        self.embeddings = None
        self.vectorstore = None
        self.llm = None
        self.qa_chain = None
        self.memory = None
        self.image_generator = None
        
        # Initialize the system
        self.initialize_system()
        
        # Conversation history
        self.conversation_history = []
        
    def initialize_system(self):
        """Initialize all system components"""
        print("🔧 Initializing Enhanced Google AI Chatbot with Image Generation...")
        
        # Check OpenAI API key
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            print("❌ OPENAI_API_KEY not found in environment variables")
            return
        
        # Initialize embeddings
        if LANGCHAIN_AVAILABLE:
            try:
                print("📚 Initializing OpenAI embeddings...")
                self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
                print("✅ Embeddings initialized")
            except Exception as e:
                print(f"❌ Error initializing embeddings: {e}")
                return
        
        # Initialize vector store
        if self.embeddings and self.embeddings_folder.exists():
            try:
                print("🗄️  Loading vector store...")
                self.vectorstore = Chroma(
                    persist_directory=str(self.embeddings_folder),
                    embedding_function=self.embeddings
                )
                print("✅ Vector store loaded")
            except Exception as e:
                print(f"❌ Error loading vector store: {e}")
                return
        
        # Initialize language model
        try:
            print("🤖 Initializing ChatGPT...")
            self.llm = ChatOpenAI(
                model=self.openai_model,
                temperature=0.7,
                openai_api_key=openai_api_key
            )
            print("✅ ChatGPT initialized")
        except Exception as e:
            print(f"❌ Error initializing ChatGPT: {e}")
            return
        
        # Initialize image generator
        try:
            print("🎨 Initializing DALL-E image generator...")
            self.image_generator = ImageGenerator(openai_api_key)
            print("✅ Image generator initialized")
        except Exception as e:
            print(f"❌ Error initializing image generator: {e}")
            self.image_generator = None
        
        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Initialize QA chain
        if self.vectorstore and self.llm:
            try:
                print("🔗 Initializing QA chain...")
                self.qa_chain = ConversationalRetrievalChain.from_llm(
                    llm=self.llm,
                    retriever=self.vectorstore.as_retriever(
                        search_type="similarity",
                        search_kwargs={"k": 5}
                    ),
                    memory=self.memory,
                    return_source_documents=True,
                    verbose=False
                )
                print("✅ QA chain initialized")
            except Exception as e:
                print(f"❌ Error initializing QA chain: {e}")
                return
        
        print("🎉 Enhanced Google AI Chatbot with Image Generation initialized successfully!")
    
    def get_knowledge_base_context(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Get relevant context from knowledge base"""
        if not self.vectorstore:
            return []
        
        try:
            # Search for relevant documents
            results = self.vectorstore.similarity_search_with_score(query, k=top_k)
            
            context = []
            for doc, score in results:
                context.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": float(score)
                })
            
            return context
        except Exception as e:
            print(f"❌ Error searching knowledge base: {e}")
            return []
    
    def detect_creative_intent(self, query: str) -> bool:
        """Detect if the query is asking for creative content (posters, images, creatives)"""
        creative_keywords = [
            "poster", "image", "creative", "design", "visual", "banner", "flyer",
            "advertisement", "marketing material", "graphic", "artwork", "template",
            "create a poster", "generate image", "make a design", "visual content"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in creative_keywords)
    
    def generate_creative_response(self, query: str) -> Dict[str, Any]:
        """Generate a creative response with image generation"""
        if not self.image_generator:
            return {
                "response": "❌ Image generation not available. Please check your OpenAI API key.",
                "blocks": [],
                "context": []
            }
        
        try:
            # Create a creative response structure
            creative_response = {
                "blocks": [
                    {
                        "type": "text",
                        "content": f"Here are some creative designs based on your request: '{query}'. I'll generate visual templates for you.",
                        "style": "paragraph"
                    }
                ]
            }
            
            # Generate different creative templates
            templates = [
                {
                    "title": "Professional Business Template",
                    "description": "Clean, modern design suitable for business and professional use",
                    "template_type": "Business",
                    "features": ["Professional layout", "Clean typography", "Balanced composition"],
                    "color_scheme": "Professional blues and grays with accent colors",
                    "target_audience": "Business professionals and corporate clients"
                },
                {
                    "title": "Creative Marketing Template",
                    "description": "Eye-catching design for marketing campaigns and promotions",
                    "template_type": "Marketing",
                    "features": ["Bold colors", "Dynamic layout", "Attention-grabbing elements"],
                    "color_scheme": "Vibrant colors with high contrast",
                    "target_audience": "Marketing campaigns and promotional materials"
                },
                {
                    "title": "Educational Content Template",
                    "description": "Clear, informative design for educational materials",
                    "template_type": "Educational",
                    "features": ["Clear hierarchy", "Readable typography", "Organized layout"],
                    "color_scheme": "Educational colors with good readability",
                    "target_audience": "Students and educational institutions"
                }
            ]
            
            # Generate images for each template
            for template in templates:
                print(f"🎨 Generating image for: {template['title']}")
                
                image_url = self.image_generator.generate_poster_image(
                    title=template["title"],
                    description=template["description"],
                    template_type=template["template_type"],
                    color_scheme=template["color_scheme"],
                    target_audience=template["target_audience"]
                )
                
                # Create creative block with image
                creative_block = {
                    "type": "creative",
                    "title": template["title"],
                    "description": template["description"],
                    "template_type": template["template_type"],
                    "features": template["features"],
                    "color_scheme": template["color_scheme"],
                    "target_audience": template["target_audience"],
                    "image_url": image_url
                }
                
                creative_response["blocks"].append(creative_block)
                
                if image_url:
                    print(f"✅ Generated image: {image_url}")
                else:
                    print(f"⚠️  Failed to generate image for: {template['title']}")
            
            # Add workflow block
            workflow_block = {
                "type": "workflow",
                "title": "How to Use These Templates",
                "steps": [
                    {"step": "1", "action": "Choose the template that best fits your needs"},
                    {"step": "2", "action": "Download the image and use it as a base design"},
                    {"step": "3", "action": "Customize with your own text, logos, and branding"},
                    {"step": "4", "action": "Export in your preferred format for use"}
                ],
                "tools": ["Canva", "Adobe Creative Suite", "Figma", "Sketch"],
                "tips": [
                    "Use the generated images as inspiration and starting points",
                    "Customize colors and fonts to match your brand",
                    "Ensure text is readable and well-positioned"
                ]
            }
            
            creative_response["blocks"].append(workflow_block)
            
            return {
                "response": "I've generated several creative templates for you with images. Each template includes design specifications and a generated image that you can use as a starting point.",
                "blocks": creative_response["blocks"],
                "context": []
            }
            
        except Exception as e:
            print(f"❌ Error generating creative response: {e}")
            return {
                "response": f"❌ Error generating creative content: {str(e)}",
                "blocks": [],
                "context": []
            }
    
    def generate_response_with_context(self, query: str, context: List[Dict[str, Any]]) -> str:
        """Generate response using ChatGPT with knowledge base context"""
        if not self.llm:
            return "❌ Language model not available"
        
        try:
            # Prepare context for the prompt
            context_text = ""
            if context:
                context_text = "\n\nRelevant Information:\n"
                for i, item in enumerate(context, 1):
                    context_text += f"{i}. {item['content']}\n"
                    if 'metadata' in item and 'source_file' in item['metadata']:
                        context_text += f"   Source: {item['metadata']['source_file']}\n"
                context_text += "\n"
            
            # Create enhanced prompt
            prompt = f"""You are an expert Google Ads consultant and AI assistant. Use the following information to provide accurate, helpful responses.

{context_text}

User Question: {query}

Please provide a comprehensive, accurate answer based on the information above. If the information is not sufficient, say so and provide general best practices. Always be helpful and professional.

Answer:"""
            
            # Generate response
            response = self.llm.invoke(prompt)
            
            return response.content
            
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return f"❌ Error generating response: {str(e)}"
    
    def chat(self, user_input: str) -> Dict[str, Any]:
        """Main chat function with creative content support"""
        print(f"\n👤 User: {user_input}")
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # Check if this is a creative request
        if self.detect_creative_intent(user_input):
            print("🎨 Detected creative content request - generating images...")
            result = self.generate_creative_response(user_input)
        else:
            # Get knowledge base context
            context = self.get_knowledge_base_context(user_input)
            
            # Generate response
            if context:
                print(f"📚 Found {len(context)} relevant knowledge base entries")
                response = self.generate_response_with_context(user_input, context)
            else:
                print("📚 No relevant knowledge base entries found")
                response = self.generate_response_with_context(user_input, [])
            
            result = {
                "response": response,
                "blocks": [
                    {
                        "type": "text",
                        "content": response,
                        "style": "paragraph"
                    }
                ],
                "context": context
            }
        
        # Add response to conversation history
        self.conversation_history.append({"role": "assistant", "content": result["response"]})
        
        print(f"🤖 Assistant: {result['response']}")
        
        # Display image URLs if available
        if "blocks" in result:
            for block in result["blocks"]:
                if block.get("type") == "creative" and block.get("image_url"):
                    print(f"🖼️  Image generated: {block['image_url']}")
        
        return result
    
    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        stats = {
            "embeddings_available": self.embeddings is not None,
            "vector_store_available": self.vectorstore is not None,
            "llm_available": self.llm is not None,
            "qa_chain_available": self.qa_chain is not None,
            "image_generation_available": self.image_generator is not None,
            "conversation_history_length": len(self.conversation_history)
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
    
    def interactive_chat(self):
        """Start interactive chat session"""
        print("\n🎯 Starting Interactive Chat Session with Image Generation")
        print("=" * 60)
        print("💡 Ask me anything about Google Ads or request creative content!")
        print("🎨 For posters, images, or creatives, just ask and I'll generate them!")
        print("📚 I'll use the knowledge base to provide accurate answers")
        print("🛑 Type 'quit' or 'exit' to end the session")
        print("📊 Type 'stats' to see system statistics")
        print("=" * 60)
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye! Thanks for chatting!")
                    break
                
                if user_input.lower() == 'stats':
                    stats = self.get_knowledge_base_stats()
                    print("\n📊 System Statistics:")
                    for key, value in stats.items():
                        print(f"   {key}: {value}")
                    continue
                
                if not user_input:
                    continue
                
                # Process the query
                result = self.chat(user_input)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye! Thanks for chatting!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                continue

def main():
    """Main function to run the enhanced chatbot"""
    print("🚀 Starting Enhanced Google AI Chatbot with Image Generation...")
    
    # Check if knowledge base exists
    embeddings_folder = Path("knowledge_base_docs/embeddings")
    if not embeddings_folder.exists():
        print("❌ Knowledge base embeddings not found!")
        print("💡 Please run the knowledge base manager first:")
        print("   python knowledge_base_manager.py")
        return
    
    # Initialize chatbot
    chatbot = EnhancedGoogleAIChatbot()
    
    # Check if system is ready
    stats = chatbot.get_knowledge_base_stats()
    if not stats.get("vector_store_available", False):
        print("❌ Vector store not available!")
        print("💡 Please ensure the knowledge base manager has processed some files")
        return
    
    if not stats.get("llm_available", False):
        print("❌ Language model not available!")
        print("💡 Please check your OpenAI API key")
        return
    
    # Show system status
    print("\n📊 System Status:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Start interactive chat
    chatbot.interactive_chat()

if __name__ == "__main__":
    main()

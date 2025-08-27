#!/usr/bin/env python3
"""
RAG System Setup Script for Google Ads Analysis
Initializes the knowledge base and tests the RAG system
"""

import os
import django
import json
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

def setup_rag_system():
    """Setup the complete RAG system"""
    
    print("🚀 Setting up RAG System for Google Ads Analysis")
    print("=" * 60)
    
    try:
        from google_ads_new.rag_service import GoogleAdsRAGService
        from django.contrib.auth.models import User
        
        # Get a test user
        try:
            user = User.objects.first()
            if not user:
                print("❌ No users found. Please create a user first.")
                return
        except Exception as e:
            print(f"❌ Error getting user: {e}")
            return
        
        print(f"✅ Using user: {user.username}")
        
        # Initialize RAG service
        print("\n🔧 Initializing RAG Service...")
        rag_service = GoogleAdsRAGService(user)
        print("✅ RAG service initialized successfully")
        
        # Check vector store stats
        stats = rag_service.get_vectorstore_stats()
        print(f"📊 Vector store stats: {stats}")
        
        # Setup knowledge base
        print("\n📚 Setting up Knowledge Base...")
        setup_knowledge_base(rag_service)
        
        # Test RAG system
        print("\n🧪 Testing RAG System...")
        test_rag_system(rag_service)
        
        print("\n🎉 RAG System Setup Complete!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all required packages are installed:")
        print("   pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("💡 Check the Django setup and database connection")

def setup_knowledge_base(rag_service):
    """Setup the knowledge base with Google Ads documents"""
    
    print("   📖 Adding knowledge base documents...")
    
    # Knowledge base directory
    kb_dir = Path("knowledge_base")
    
    if not kb_dir.exists():
        print("   ⚠️  Knowledge base directory not found. Creating sample documents...")
        create_sample_documents()
    
    # Add documents to vector store
    documents_added = 0
    
    # Add markdown files
    for md_file in kb_dir.glob("*.md"):
        try:
            chunks_added = rag_service.add_markdown_file(str(md_file), md_file.stem)
            documents_added += chunks_added
            print(f"   ✅ Added {md_file.name}: {chunks_added} chunks")
        except Exception as e:
            print(f"   ❌ Error adding {md_file.name}: {e}")
    
    # Add text files
    for txt_file in kb_dir.glob("*.txt"):
        try:
            chunks_added = rag_service.add_text_file(str(txt_file), txt_file.stem)
            documents_added += chunks_added
            print(f"   ✅ Added {txt_file.name}: {chunks_added} chunks")
        except Exception as e:
            print(f"   ❌ Error adding {txt_file.name}: {e}")
    
    print(f"   📊 Total chunks added: {documents_added}")
    
    # Update stats
    stats = rag_service.get_vectorstore_stats()
    print(f"   📈 Vector store updated: {stats.get('total_documents', 0)} total documents")

def create_sample_documents():
    """Create sample knowledge base documents if they don't exist"""
    
    kb_dir = Path("knowledge_base")
    kb_dir.mkdir(exist_ok=True)
    
    # Create best practices document
    best_practices = """# Google Ads Best Practices

## Campaign Structure
- Single purpose per campaign
- Logical ad group structure
- Consistent naming conventions
- Budget allocation based on performance

## Keyword Strategy
- Focus on relevant, high-intent keywords
- Regular negative keyword management
- Balance broad and specific match types
- Monitor search terms report weekly

## Ad Copy Optimization
- Include primary keywords in headlines
- Use compelling calls-to-action
- Test different ad variations
- Refresh creative every 4-6 weeks

## Quality Score
- Ensure keyword-ad relevance
- Optimize landing page experience
- Monitor expected click-through rate
- Regular optimization and testing
"""
    
    with open(kb_dir / "google_ads_basics.txt", "w") as f:
        f.write(best_practices)
    
    # Create case study document
    case_study = """# Google Ads Success Case Study

## Company: E-commerce Fashion Retailer
**Challenge**: Low conversion rates and high cost per acquisition
**Solution**: Implemented comprehensive remarketing strategy
**Results**: 
- ROAS increased by 300%
- Cost per acquisition reduced by 45%
- Conversion rate improved by 2.8x

## Key Strategies Used
1. Dynamic remarketing with personalized recommendations
2. Audience segmentation based on behavior
3. A/B testing of ad copy and landing pages
4. Automated bidding strategies

## Implementation Timeline
- Week 1-2: Audience setup and segmentation
- Week 3-4: Creative development and testing
- Week 5-6: Campaign launch and optimization
- Week 7-8: Performance analysis and scaling
"""
    
    with open(kb_dir / "success_case_study.txt", "w") as f:
        f.write(case_study)
    
    print("   📝 Created sample knowledge base documents")

def test_rag_system(rag_service):
    """Test the RAG system with various queries"""
    
    print("   🔍 Testing RAG system functionality...")
    
    # Test queries
    test_queries = [
        "What are the best practices for Google Ads campaign structure?",
        "How can I improve my Quality Score?",
        "What bidding strategies work best for e-commerce?",
        "How do I prevent ad fatigue?",
        "What are the key metrics to monitor for Google Ads campaigns?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n   Test {i}: {query}")
        
        try:
            # Test smart context selection
            context, use_rag = rag_service.smart_context_selection(query, {"has_campaigns": True})
            
            if use_rag:
                print(f"      ✅ RAG selected (context length: {len(context)})")
                
                # Test document search
                relevant_docs = rag_service.search_documents(query, k=2)
                print(f"      📚 Found {len(relevant_docs)} relevant documents")
                
                # Show document sources
                sources = set()
                for doc in relevant_docs:
                    source = doc.metadata.get("source", "unknown")
                    sources.add(source)
                print(f"      📖 Sources: {', '.join(sources)}")
                
            else:
                print(f"      ℹ️  Direct OpenAI selected")
                
        except Exception as e:
            print(f"      ❌ Error testing query: {e}")
    
    # Test hybrid response
    print(f"\n   🧪 Testing hybrid response generation...")
    try:
        test_query = "What are the best practices for Google Ads optimization?"
        user_data = {"has_campaigns": True, "campaign_count": 5}
        
        hybrid_response = rag_service.get_hybrid_response(test_query, user_data)
        
        if "response_type" in hybrid_response:
            print(f"      ✅ Hybrid response generated: {hybrid_response['response_type']}")
            
            # Show metadata
            if "hybrid_metadata" in hybrid_response:
                metadata = hybrid_response["hybrid_metadata"]
                print(f"      📊 Context selection: {metadata.get('context_selection', 'unknown')}")
                print(f"      📝 Selection reason: {metadata.get('selection_reason', 'unknown')}")
            
            if "rag_metadata" in hybrid_response:
                rag_meta = hybrid_response["rag_metadata"]
                print(f"      🔍 Context used: {rag_meta.get('context_used', False)}")
                print(f"      📏 Context length: {rag_meta.get('context_length', 0)}")
                
        else:
            print(f"      ⚠️  Response missing metadata")
            
    except Exception as e:
        print(f"      ❌ Error testing hybrid response: {e}")

def test_document_operations(rag_service):
    """Test document operations"""
    
    print("\n📄 Testing Document Operations...")
    
    try:
        # Test adding a simple text document
        test_content = "This is a test document for RAG system testing."
        test_doc = f"test_document_{os.getpid()}.txt"
        
        with open(test_doc, "w") as f:
            f.write(test_content)
        
        # Add to vector store
        chunks_added = rag_service.add_text_file(test_doc, "test")
        print(f"   ✅ Test document added: {chunks_added} chunks")
        
        # Test search
        results = rag_service.search_documents("test document", k=1)
        if results:
            print(f"   ✅ Document search working: found {len(results)} results")
        else:
            print(f"   ⚠️  Document search returned no results")
        
        # Cleanup
        os.remove(test_doc)
        print(f"   🧹 Test document cleaned up")
        
    except Exception as e:
        print(f"   ❌ Error testing document operations: {e}")

def main():
    """Main setup function"""
    
    print("🤖 Setting up RAG system for Google Ads analysis...")
    
    # Setup RAG system
    setup_rag_system()
    
    print("\n📚 RAG System Features:")
    print("   ✅ Vector database (Chroma) with document storage")
    print("   ✅ Document processing pipeline (text, markdown, PDF)")
    print("   ✅ Semantic search and retrieval")
    print("   ✅ Context augmentation with knowledge base")
    print("   ✅ Smart context selection (RAG vs Direct OpenAI)")
    print("   ✅ Hybrid response generation")
    
    print("\n🔧 Next Steps:")
    print("   1. Test the system: python demo_rag_system.py")
    print("   2. Add more knowledge base documents")
    print("   3. Use the chat interface to test RAG responses")
    print("   4. Monitor and optimize context selection")

if __name__ == "__main__":
    main()


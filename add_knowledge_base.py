#!/usr/bin/env python3
"""
Script to add Google Search Ads Knowledge Base to the system
This script demonstrates how to add knowledge base documents to the system
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/Users/satyendra/marketing_assistant_back')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

from django.contrib.auth.models import User
from google_ads_new.models import KBDocument
from google_ads_new.langchain_tools import KnowledgeBaseTools

def add_google_ads_knowledge_base():
    """Add the Google Search Ads knowledge base to the system"""
    
    print("📚 Adding Google Search Ads Knowledge Base to the System")
    print("=" * 70)
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={'email': 'admin@example.com', 'first_name': 'Admin', 'last_name': 'User'}
    )
    
    if created:
        user.set_password('admin123')
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print("✅ Created admin user")
    else:
        print("✅ Using existing admin user")
    
    # Read the knowledge base document
    kb_file_path = "knowledge_base/google_search_ads_knowledge_base.md"
    
    try:
        with open(kb_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        print(f"✅ Read knowledge base file: {kb_file_path}")
    except FileNotFoundError:
        print(f"❌ Knowledge base file not found: {kb_file_path}")
        return
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return
    
    # Initialize knowledge base tools
    kb_tools = KnowledgeBaseTools(user, "kb_setup_session")
    
    # Check if document already exists
    existing_doc = KBDocument.objects.filter(
        title="Google Search Ads - Knowledge Base",
        company_id=1
    ).first()
    
    if existing_doc:
        print("📝 Updating existing knowledge base document...")
        existing_doc.content = content
        existing_doc.save()
        print("✅ Knowledge base document updated successfully")
        doc_id = existing_doc.id
    else:
        print("📝 Creating new knowledge base document...")
        
        # Create the knowledge base document
        try:
            kb_doc = KBDocument.objects.create(
                company_id=1,
                title="Google Search Ads - Knowledge Base",
                content=content,
                document_type="knowledge_base",
                url="",
                metadata={
                    "category": "Google Ads",
                    "subcategory": "Search Ads",
                    "tags": ["performance metrics", "optimization", "bidding", "keywords", "match types", "ad structure", "demographics", "analysis framework"],
                    "version": "1.0.0",
                    "last_updated": "2024-12-19",
                    "author": "Google Ads Development Team",
                    "difficulty_level": "Intermediate",
                    "estimated_read_time": "45 minutes"
                }
            )
            print("✅ Knowledge base document created successfully")
            doc_id = kb_doc.id
        except Exception as e:
            print(f"❌ Error creating document: {e}")
            return
    
    print(f"\n📋 Document Details:")
    print(f"   - ID: {doc_id}")
    print(f"   - Title: Google Search Ads - Knowledge Base")
    print(f"   - Company ID: 1")
    print(f"   - Document Type: knowledge_base")
    print(f"   - Content Length: {len(content)} characters")
    
    # Test knowledge base search
    print(f"\n🔍 Testing Knowledge Base Search...")
    
    # Test different search queries
    test_queries = [
        "CTR calculation formula",
        "keyword match types",
        "quality score factors",
        "bidding strategies",
        "ad extensions",
        "demographic targeting",
        "performance optimization",
        "auction insights"
    ]
    
    for query in test_queries:
        print(f"\n   Searching for: '{query}'")
        try:
            search_results = kb_tools.search_kb(query, company_id=1)
            
            if search_results and "results" in search_results:
                results = search_results["results"]
                if results:
                    top_result = results[0]
                    print(f"      ✅ Found: {top_result.get('title', 'N/A')}")
                    print(f"         Relevance: {top_result.get('relevance_score', 'N/A')}")
                    print(f"         Snippet: {top_result.get('snippet', 'N/A')[:100]}...")
                else:
                    print(f"      ⚠️  No results found")
            else:
                print(f"      ⚠️  Search returned no results")
                
        except Exception as e:
            print(f"      ❌ Search error: {e}")
    
    print(f"\n" + "=" * 70)
    print("🎉 Google Search Ads Knowledge Base Setup Complete!")
    print(f"\n💡 What's Been Added:")
    print(f"   • Comprehensive Google Search Ads knowledge base")
    print(f"   • 12 major sections covering all aspects of Google Ads")
    print(f"   • Performance metrics, optimization rules, and best practices")
    print(f"   • Automation decision rules and analysis frameworks")
    print(f"   • Ad structure, targeting, and compliance guidelines")
    
    print(f"\n🚀 Next Steps:")
    print(f"   1. Test the knowledge base with your chatbot")
    print(f"   2. Ask questions about Google Ads performance metrics")
    print(f"   3. Get optimization recommendations based on the knowledge base")
    print(f"   4. Use the analysis frameworks for campaign optimization")
    
    print(f"\n📖 Knowledge Base Sections:")
    print(f"   1. Core Performance Metrics")
    print(f"   2. Position and Visibility Metrics")
    print(f"   3. Keyword and Match Type Classifications")
    print(f"   4. Campaign Structure Metrics")
    print(f"   5. Mathematical Relationships")
    print(f"   6. Automation Decision Rules")
    print(f"   7. Data Validation Rules")
    print(f"   8. Reporting Aggregations")
    print(f"   9. Ads Structure and Components")
    print(f"   10. Audience Targeting and Demographics")
    print(f"   11. Google Ad Account Optimization Checks")
    print(f"   12. Analysis Framework")
    
    return doc_id

def test_knowledge_base_integration():
    """Test the knowledge base integration with the chatbot"""
    
    print(f"\n🧪 Testing Knowledge Base Integration...")
    print("-" * 50)
    
    # Get the knowledge base tools
    user = User.objects.get(username='admin')
    kb_tools = KnowledgeBaseTools(user, "test_session")
    
    # Test complex queries that should use the knowledge base
    complex_queries = [
        "How do I calculate CTR and what's a good benchmark?",
        "What are the different keyword match types and when should I use each?",
        "How can I optimize my Google Ads campaign for better performance?",
        "What factors affect Quality Score and how can I improve it?",
        "How should I structure my Responsive Search Ads for maximum effectiveness?",
        "What bidding strategies should I use for different campaign goals?",
        "How can I analyze auction insights to understand my competition?",
        "What demographic targeting strategies work best for educational services?"
    ]
    
    for i, query in enumerate(complex_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        print("   " + "-" * 50)
        
        try:
            # Search the knowledge base
            search_results = kb_tools.search_kb(query, company_id=1)
            
            if search_results and "results" in search_results:
                results = search_results["results"]
                if results:
                    print(f"   ✅ Knowledge base search successful")
                    print(f"   📊 Found {len(results)} relevant documents")
                    
                    # Show top result
                    top_result = results[0]
                    print(f"   🏆 Top Result:")
                    print(f"      Title: {top_result.get('title', 'N/A')}")
                    print(f"      Relevance: {top_result.get('relevance_score', 'N/A')}")
                    
                    # Show snippet
                    snippet = top_result.get('snippet', '')
                    if snippet:
                        print(f"      Snippet: {snippet[:150]}...")
                    
                    # Show metadata if available
                    metadata = top_result.get('metadata', {})
                    if metadata:
                        tags = metadata.get('tags', [])
                        if tags:
                            print(f"      Tags: {', '.join(tags[:3])}")
                else:
                    print(f"   ⚠️  No relevant documents found")
            else:
                print(f"   ⚠️  Search returned no results")
                
        except Exception as e:
            print(f"   ❌ Error during search: {e}")
    
    print(f"\n✅ Knowledge Base Integration Test Complete!")

if __name__ == "__main__":
    try:
        # Add the knowledge base
        doc_id = add_google_ads_knowledge_base()
        
        if doc_id:
            # Test the integration
            test_knowledge_base_integration()
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()

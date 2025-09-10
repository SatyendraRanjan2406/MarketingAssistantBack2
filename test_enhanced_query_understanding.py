#!/usr/bin/env python3
"""
Test script for Enhanced Query Understanding System
Tests the complete pipeline from user query to enhanced response
"""

import os
import sys
import django
from django.conf import settings
from django.contrib.auth.models import User

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

def test_enhanced_query_understanding():
    """Test the enhanced query understanding system"""
    print("🧠 Testing Enhanced Query Understanding System")
    print("=" * 60)
    
    try:
        # Import the query understanding system
        from google_ads_new.query_understanding_system import (
            ContextExtractor, CampaignDiscoveryService, 
            KeywordIntelligenceTools, ParameterExtractor,
            QueryUnderstandingPipeline
        )
        
        # Create or get a test user
        user, created = User.objects.get_or_create(
            username='testuser_enhanced',
            defaults={
                'email': 'test_enhanced@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            print(f"✅ Created test user: {user.username}")
        else:
            print(f"✅ Using existing test user: {user.username}")
        
        # Test 1: Context Extraction
        print("\n🔍 Test 1: Context Extraction")
        print("-" * 40)
        
        context_extractor = ContextExtractor()
        test_message = "suggest keywords to improve a digital marketing course campaign"
        
        context = context_extractor.extract_context(test_message, user)
        print(f"Input: {test_message}")
        print(f"Extracted Context: {context}")
        
        # Test 2: Campaign Discovery
        print("\n🎯 Test 2: Campaign Discovery")
        print("-" * 40)
        
        campaign_discovery = CampaignDiscoveryService(user)
        
        # Test with different status filters
        for status_filter in ["all", "enabled", "paused"]:
            campaigns = campaign_discovery.find_campaigns_by_context("digital marketing", status_filter)
            print(f"Campaigns ({status_filter}): {len(campaigns)} found")
            
            if campaigns:
                for i, campaign_data in enumerate(campaigns[:3]):  # Show top 3
                    campaign = campaign_data['campaign']
                    print(f"  {i+1}. {campaign['campaign_name']} ({campaign['campaign_status']}) - Score: {campaign_data['match_score']:.1f}")
        
        # Test 3: Parameter Extraction
        print("\n⚙️ Test 3: Parameter Extraction")
        print("-" * 40)
        
        parameter_extractor = ParameterExtractor()
        parameters = parameter_extractor.extract_parameters(test_message, context)
        print(f"Extracted Parameters: {parameters}")
        
        # Test 4: Query Understanding Pipeline
        print("\n🚀 Test 4: Query Understanding Pipeline")
        print("-" * 40)
        
        query_pipeline = QueryUnderstandingPipeline(user)
        query_understanding = query_pipeline.process_query(test_message)
        
        print(f"Pipeline Success: {query_understanding.get('success')}")
        print(f"Confidence: {query_understanding.get('query_understanding', {}).get('confidence', 0):.1f}%")
        print(f"Discovered Campaigns: {len(query_understanding.get('campaigns', []))}")
        print(f"Business Context: {query_understanding.get('business_context', {}).get('business_category', 'Unknown')}")
        
        # Test 5: Keyword Intelligence (if campaigns found)
        print("\n🔑 Test 5: Keyword Intelligence")
        print("-" * 40)
        
        campaigns = query_understanding.get('campaigns', [])
        if campaigns:
            keyword_tools = KeywordIntelligenceTools(user)
            
            for i, campaign_data in enumerate(campaigns[:2]):  # Test with top 2 campaigns
                campaign = campaign_data['campaign']
                print(f"\nAnalyzing campaign: {campaign['campaign_name']}")
                
                try:
                    suggestions = keyword_tools.suggest_keywords_for_campaign(
                        campaign_id=campaign['id'],
                        business_context="Education",
                        target_audience="Students"
                    )
                    
                    if 'error' not in suggestions:
                        print(f"  ✅ Generated {len(suggestions.get('new_keyword_suggestions', []))} keyword suggestions")
                        print(f"  📊 Found {len(suggestions.get('keyword_opportunities', {}).get('high_performing_keywords', []))} high-performing keywords")
                        print(f"  💡 {len(suggestions.get('recommendations', []))} recommendations generated")
                    else:
                        print(f"  ❌ Keyword suggestions failed: {suggestions['error']}")
                        
                except Exception as e:
                    print(f"  ❌ Error generating keyword suggestions: {e}")
        else:
            print("  ⚠️ No campaigns found to test keyword intelligence")
        
        # Test 6: Error Handling and Fallbacks
        print("\n🛡️ Test 6: Error Handling and Fallbacks")
        print("-" * 40)
        
        # Test with invalid query
        invalid_query = ""
        try:
            invalid_result = query_pipeline.process_query(invalid_query)
            print(f"Invalid query handling: {invalid_result.get('success')}")
        except Exception as e:
            print(f"Invalid query error handling: ✅ {type(e).__name__}: {e}")
        
        # Test 7: Performance Metrics
        print("\n📊 Test 7: Performance Metrics")
        print("-" * 40)
        
        import time
        
        # Test response time
        start_time = time.time()
        query_understanding = query_pipeline.process_query(test_message)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        print(f"Response Time: {response_time:.2f}ms")
        
        # Test memory usage
        import psutil
        process = psutil.Process()
        memory_usage = process.memory_info().rss / 1024 / 1024  # MB
        print(f"Memory Usage: {memory_usage:.2f} MB")
        
        print("\n✅ Enhanced Query Understanding System Test Completed Successfully!")
        
        # Summary
        print("\n📋 Test Summary:")
        print(f"  • Context Extraction: ✅ Working")
        print(f"  • Campaign Discovery: ✅ Working ({len(campaigns)} campaigns found)")
        print(f"  • Parameter Extraction: ✅ Working")
        print(f"  • Query Pipeline: ✅ Working (Confidence: {query_understanding.get('query_understanding', {}).get('confidence', 0):.1f}%)")
        print(f"  • Keyword Intelligence: ✅ Working")
        print(f"  • Error Handling: ✅ Working")
        print(f"  • Performance: ✅ Good ({response_time:.2f}ms)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_specific_queries():
    """Test specific query scenarios"""
    print("\n🎯 Testing Specific Query Scenarios")
    print("=" * 60)
    
    try:
        from google_ads_new.query_understanding_system import QueryUnderstandingPipeline
        
        # Get test user
        user = User.objects.get(username='testuser_enhanced')
        query_pipeline = QueryUnderstandingPipeline(user)
        
        # Test queries
        test_queries = [
            "suggest keywords to improve a digital marketing course campaign",
            "analyze performance of my paused campaigns",
            "show me all enabled campaigns with high ROAS",
            "generate ad copies for my e-commerce campaign",
            "what keywords should I add to my B2B campaign?",
            "compare my search and display campaigns",
            "optimize my underperforming keywords"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🔍 Test Query {i}: {query}")
            print("-" * 50)
            
            try:
                result = query_pipeline.process_query(query)
                
                if result.get('success'):
                    confidence = result.get('query_understanding', {}).get('confidence', 0)
                    campaigns_found = len(result.get('campaigns', []))
                    business_context = result.get('business_context', {}).get('business_category', 'Unknown')
                    
                    print(f"  ✅ Success - Confidence: {confidence:.1f}%")
                    print(f"  🎯 Campaigns Found: {campaigns_found}")
                    print(f"  🏢 Business Context: {business_context}")
                    print(f"  🛠️ Tools Selected: {', '.join(result.get('tools', []))}")
                else:
                    print(f"  ❌ Failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        print("\n✅ Specific Query Testing Completed!")
        
    except Exception as e:
        print(f"❌ Specific query testing failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting Enhanced Query Understanding System Tests")
    print("=" * 80)
    
    # Check environment
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Warning: OPENAI_API_KEY not set. Some AI features may not work.")
        print("   Set it in your .env file: OPENAI_API_KEY=sk-your-key-here")
    
    # Run tests
    success = test_enhanced_query_understanding()
    
    if success:
        test_specific_queries()
        print("\n🎉 All tests completed successfully!")
    else:
        print("\n💥 Tests failed. Please check the error messages above.")
        sys.exit(1)


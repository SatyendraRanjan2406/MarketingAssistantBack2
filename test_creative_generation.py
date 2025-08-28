#!/usr/bin/env python3
"""
Test script for Google Ads Creative Generation Tools
Demonstrates the new capabilities for generating ad copies, posters, and Meta ads creatives
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
from google_ads_new.google_ads_analysis_tools import GoogleAdsAnalysisTools

def test_creative_generation():
    """Test the creative generation tools"""
    
    # Get a test user (create one if it doesn't exist)
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'User'}
    )
    
    print("🧪 Testing Google Ads Creative Generation Tools")
    print("=" * 60)
    
    # Initialize the analysis tools
    analysis_tools = GoogleAdsAnalysisTools(user, "test_session")
    
    # Test 1: Generate Ad Copies
    print("\n📝 Test 1: Generate Ad Copies")
    print("-" * 40)
    
    context = "best poster generator create a poster for lakshya coaching center with a young student in poster, targeting for indian geography focusing on better CTA"
    
    # Test Google Ads ad copies
    print("\n🔍 Google Ads Ad Copies:")
    google_ads_result = analysis_tools.generate_ad_copies(context, "google_ads", 4)
    
    if "error" not in google_ads_result:
        print(f"✅ Generated {len(google_ads_result.get('ad_copies', []))} Google Ads ad copies")
        for i, ad_copy in enumerate(google_ads_result.get('ad_copies', [])[:2], 1):
            print(f"\n   Ad Copy {i}:")
            print(f"   - Headline 1: {ad_copy.get('headline1', 'N/A')}")
            print(f"   - Headline 2: {ad_copy.get('headline2', 'N/A')}")
            print(f"   - Headline 3: {ad_copy.get('headline3', 'N/A')}")
            print(f"   - Description: {ad_copy.get('description', 'N/A')}")
            print(f"   - CTA: {ad_copy.get('cta', 'N/A')}")
    else:
        print(f"❌ Error: {google_ads_result['error']}")
    
    # Test Meta Ads ad copies
    print("\n🔍 Meta Ads Ad Copies:")
    meta_ads_result = analysis_tools.generate_ad_copies(context, "meta_ads", 4)
    
    if "error" not in meta_ads_result:
        print(f"✅ Generated {len(meta_ads_result.get('ad_copies', []))} Meta Ads ad copies")
        for i, ad_copy in enumerate(meta_ads_result.get('ad_copies', [])[:2], 1):
            print(f"\n   Ad Copy {i}:")
            print(f"   - Headline: {ad_copy.get('headline', 'N/A')}")
            print(f"   - Primary Text: {ad_copy.get('primary_text', 'N/A')}")
            print(f"   - CTA: {ad_copy.get('cta', 'N/A')}")
    else:
        print(f"❌ Error: {meta_ads_result['error']}")
    
    # Test 2: Generate Poster Templates
    print("\n🎨 Test 2: Generate Poster Templates")
    print("-" * 40)
    
    poster_result = analysis_tools.generate_poster_templates(context, "students")
    
    if "error" not in poster_result:
        print(f"✅ Generated {len(poster_result.get('poster_templates', []))} poster templates")
        
        for i, template in enumerate(poster_result.get('poster_templates', [])[:2], 1):
            print(f"\n   Template {i}: {template.get('title', 'N/A')}")
            print(f"   - Type: {template.get('template_type', 'N/A')}")
            print(f"   - Description: {template.get('description', 'N/A')}")
            print(f"   - Color Scheme: {template.get('color_scheme', 'N/A')}")
            print(f"   - CTA Suggestions: {', '.join(template.get('cta_suggestions', [])[:2])}")
        
        # Show workflow
        workflow = poster_result.get('workflow', {})
        if workflow:
            print(f"\n   📋 Workflow: {workflow.get('title', 'N/A')}")
            for step in workflow.get('steps', [])[:3]:
                print(f"      Step {step.get('step', 'N/A')}: {step.get('action', 'N/A')}")
            
            print(f"\n   🛠️  Recommended Tools: {', '.join(workflow.get('tools', [])[:3])}")
    else:
        print(f"❌ Error: {poster_result['error']}")
    
    # Test 3: Generate Meta Ads Creatives
    print("\n📱 Test 3: Generate Meta Ads Creatives")
    print("-" * 40)
    
    meta_creatives_result = analysis_tools.generate_meta_ads_creatives(context, "all")
    
    if "error" not in meta_creatives_result:
        print(f"✅ Generated {len(meta_creatives_result.get('creative_ideas', []))} Meta ads creative ideas")
        
        for i, creative in enumerate(meta_creatives_result.get('creative_ideas', [])[:2], 1):
            print(f"\n   Creative {i}: {creative.get('title', 'N/A')}")
            print(f"   - Type: {creative.get('template_type', 'N/A')}")
            print(f"   - Description: {creative.get('description', 'N/A')}")
            print(f"   - Color Scheme: {creative.get('color_scheme', 'N/A')}")
            print(f"   - CTA Suggestions: {', '.join(creative.get('cta_suggestions', [])[:2])}")
        
        # Show workflow
        workflow = meta_creatives_result.get('workflow', {})
        if workflow:
            print(f"\n   📋 Workflow: {workflow.get('title', 'N/A')}")
            for step in workflow.get('steps', [])[:3]:
                print(f"      Step {step.get('step', 'N/A')}: {step.get('action', 'N/A')}")
            
            print(f"\n   🛠️  Recommended Tools: {', '.join(workflow.get('tools', [])[:3])}")
    else:
        print(f"❌ Error: {meta_creatives_result['error']}")
    
    # Test 4: Creative Suggestions
    print("\n🎯 Test 4: Creative Suggestions")
    print("-" * 40)
    
    if "creative_suggestions" in google_ads_result:
        suggestions = google_ads_result["creative_suggestions"]
        print("✅ Creative Suggestions Generated:")
        
        print(f"\n   🎨 Visual Elements:")
        for element in suggestions.get("visual_elements", [])[:2]:
            print(f"      - {element}")
        
        print(f"\n   🌈 Color Schemes:")
        for scheme in suggestions.get("color_schemes", [])[:2]:
            print(f"      - {scheme}")
        
        print(f"\n   📝 Typography:")
        for typography in suggestions.get("typography", [])[:2]:
            print(f"      - {typography}")
    
    print("\n" + "=" * 60)
    print("✅ Creative Generation Testing Complete!")
    print("\n💡 Key Features Demonstrated:")
    print("   • Multiple ad copy variations for Google Ads and Meta Ads")
    print("   • Poster template generation with design suggestions")
    print("   • Meta ads creative ideas and workflows")
    print("   • Creative suggestions for visuals, colors, and typography")
    print("   • Step-by-step implementation workflows")
    print("   • Tool recommendations for design and implementation")

if __name__ == "__main__":
    try:
        test_creative_generation()
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

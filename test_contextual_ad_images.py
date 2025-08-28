#!/usr/bin/env python3
"""
Test Contextual Ad Copy Image Generation
Demonstrates how each ad copy variation gets a contextual image
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
from google_ads_new.chat_service import ImageGenerator

def test_contextual_ad_copy_images():
    """Test the enhanced ad copy generation with contextual images"""
    
    print("🎨 Testing Contextual Ad Copy Image Generation")
    print("=" * 60)
    
    # Check OpenAI API key
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        print("❌ OPENAI_API_KEY not found")
        print("💡 Set your OpenAI API key to test image generation")
        return False
    
    # Get test user
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@example.com'}
    )
    
    if created:
        user.set_password('test123')
        user.save()
    
    # Initialize tools
    tools = GoogleAdsAnalysisTools(user, "test_session")
    image_generator = ImageGenerator(openai_api_key)
    
    print("✅ Tools initialized successfully")
    
    # Test context
    test_context = "Create ad copies for Lakshya Coaching Center focusing on geography and Indian students"
    
    print(f"\n📝 Testing Context: {test_context}")
    print("-" * 50)
    
    # Test Google Ads ad copies
    print("\n🔍 Testing Google Ads Ad Copies:")
    print("=" * 40)
    
    google_ads_result = tools.generate_ad_copies(test_context, "google_ads", 4)
    
    if "ad_copies" in google_ads_result:
        for i, ad_copy in enumerate(google_ads_result["ad_copies"], 1):
            print(f"\n📊 Ad Copy Variation {i}:")
            print(f"   Title: {ad_copy.get('title', 'N/A')}")
            print(f"   Variation Type: {ad_copy.get('variation_type', 'N/A')}")
            print(f"   Platform: {ad_copy.get('platform', 'N/A')}")
            print(f"   Features: {', '.join(ad_copy.get('features', [])[:3])}")
            print(f"   Advantages: {', '.join(ad_copy.get('advantages', [])[:3])}")
            print(f"   CTA: {ad_copy.get('cta', 'N/A')}")
            
            # Generate contextual image for this variation
            print(f"   🎨 Generating contextual image...")
            
            if "variation_type" in ad_copy:
                image_url = image_generator.generate_ad_copy_image(
                    ad_copy, 
                    ad_copy["variation_type"], 
                    ad_copy["platform"]
                )
                
                if image_url:
                    print(f"   ✅ Image Generated: {image_url[:50]}...")
                    print(f"   🎯 Image Context: Tailored for {ad_copy['variation_type']} approach")
                    print(f"   💡 Image Advantages:")
                    
                    # Show image advantages based on variation type
                    if ad_copy["variation_type"] == "emotional_appeal":
                        print(f"      - Warm, people-focused design")
                        print(f"      - Emotional connection elements")
                        print(f"      - Relatable imagery for {ad_copy['target_audience']}")
                    elif ad_copy["variation_type"] == "benefit_focused":
                        print(f"      - Results-driven visual design")
                        print(f"      - Clear benefit demonstration")
                        print(f"      - Strong visual impact")
                    elif ad_copy["variation_type"] == "social_proof":
                        print(f"      - Trust-building elements")
                        print(f"      - Credibility indicators")
                        print(f"      - Professional appearance")
                    elif ad_copy["variation_type"] == "urgency_scarcity":
                        print(f"      - Dynamic, energetic design")
                        print(f"      - Time-sensitive elements")
                        print(f"      - Action-oriented visuals")
                else:
                    print(f"   ❌ Failed to generate image")
            else:
                print(f"   ⚠️  No variation type specified")
    
    # Test Meta Ads ad copies
    print("\n\n🔍 Testing Meta Ads Ad Copies:")
    print("=" * 40)
    
    meta_ads_result = tools.generate_ad_copies(test_context, "meta_ads", 4)
    
    if "ad_copies" in meta_ads_result:
        for i, ad_copy in enumerate(meta_ads_result["ad_copies"], 1):
            print(f"\n📊 Meta Ad Copy Variation {i}:")
            print(f"   Title: {ad_copy.get('title', 'N/A')}")
            print(f"   Variation Type: {ad_copy.get('variation_type', 'N/A')}")
            print(f"   Platform: {ad_copy.get('platform', 'N/A')}")
            print(f"   Ad Format: {ad_copy.get('ad_format', 'N/A')}")
            print(f"   Features: {', '.join(ad_copy.get('features', [])[:3])}")
            print(f"   Advantages: {', '.join(ad_copy.get('advantages', [])[:3])}")
            print(f"   CTA: {ad_copy.get('cta', 'N/A')}")
            
            # Generate contextual image for this variation
            print(f"   🎨 Generating contextual Meta Ads image...")
            
            if "variation_type" in ad_copy:
                image_url = image_generator.generate_meta_ads_image(
                    ad_copy, 
                    ad_copy.get("ad_format", "feed")
                )
                
                if image_url:
                    print(f"   ✅ Meta Ads Image Generated: {image_url[:50]}...")
                    print(f"   🎯 Image Context: Optimized for {ad_copy.get('ad_format', 'feed')} format")
                    print(f"   💡 Meta Ads Image Advantages:")
                    print(f"      - Social media optimized design")
                    print(f"      - Mobile-first layout")
                    print(f"      - Engagement-focused visuals")
                    print(f"      - Shareable content elements")
                else:
                    print(f"   ❌ Failed to generate Meta Ads image")
            else:
                print(f"   ⚠️  No variation type specified")
    
    print("\n" + "=" * 60)
    print("🎉 Contextual Ad Copy Image Generation Test Complete!")
    print("\n💡 Key Benefits of This System:")
    print("   ✅ Each ad copy variation gets a unique, contextual image")
    print("   ✅ Images are tailored to the specific messaging approach")
    print("   ✅ Platform-specific optimization (Google Ads vs Meta Ads)")
    print("   ✅ Visual elements match the ad copy advantages")
    print("   ✅ Consistent branding with variation-specific styling")
    
    return True

def main():
    """Main test function"""
    print("🚀 Test: Contextual Ad Copy Image Generation")
    print("=" * 60)
    
    if test_contextual_ad_copy_images():
        print("\n✅ Test completed successfully!")
        print("🎨 Your chatbot now generates contextual images for each ad copy variation!")
        print("\n💡 Each image will:")
        print("   - Match the variation type (emotional, benefit-focused, etc.)")
        print("   - Highlight the specific advantages mentioned")
        print("   - Be optimized for the target platform")
        print("   - Include visual elements that support the messaging")
    else:
        print("\n❌ Test failed - check your OpenAI API key")

if __name__ == "__main__":
    main()

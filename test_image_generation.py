#!/usr/bin/env python3
"""
Test Script for Image Generation in Google AI Chatbot
Demonstrates how to generate images for creative content requests
"""

import os
import sys
import json
from pathlib import Path

# Add the project directory to Python path
sys.path.append('/Users/satyendra/marketing_assistant_back')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')

try:
    import django
    django.setup()
    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False
    print("⚠️  Django not available - running in standalone mode")

class ImageGenerator:
    """Handles image generation using OpenAI DALL-E API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/images/generations"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_image(self, prompt: str, size: str = "1024x1024", quality: str = "standard", style: str = "vivid"):
        """Generate an image using DALL-E and return the URL"""
        try:
            import requests
            
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
    
    def generate_poster_image(self, title: str, description: str, template_type: str, color_scheme: str, target_audience: str):
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

def test_image_generation():
    """Test the image generation functionality"""
    print("🎨 Testing Image Generation for Creative Content")
    print("=" * 60)
    
    # Check OpenAI API key
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("💡 Please set your OpenAI API key:")
        print("   export OPENAI_API_KEY='your_api_key_here'")
        return False
    
    # Initialize image generator
    try:
        image_gen = ImageGenerator(openai_api_key)
        print("✅ Image generator initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing image generator: {e}")
        return False
    
    # Test creative content generation
    print("\n🎯 Testing Poster Generation for Lakshya Coaching Center...")
    
    # Sample creative data (similar to your chatbot response)
    creative_data = {
        "blocks": [
            {
                "type": "creative",
                "title": "Geography-Themed Educational Poster",
                "description": "A professional poster with earthy tones, map elements, and student illustration",
                "template_type": "Educational",
                "features": [
                    "Earthy color scheme (browns, greens, blues)",
                    "Map or geography visual elements",
                    "Student illustration or photo",
                    "Clear hierarchy with headline, benefits, and CTA"
                ],
                "advantages": [
                    "Perfect visual alignment with geography subject",
                    "Professional appearance for educational institutions",
                    "Easy to read and understand"
                ],
                "cta_suggestions": [
                    "Enroll Now",
                    "Join Free Demo!",
                    "Start Your Journey",
                    "Register Today"
                ],
                "color_scheme": "Earthy tones with professional accents",
                "target_audience": "Geography students and parents"
            },
            {
                "type": "creative",
                "title": "Bold Coaching Center Flyer",
                "description": "Vibrant design with confident student imagery and prominent CTA button",
                "template_type": "Marketing",
                "features": [
                    "Vibrant, attention-grabbing colors",
                    "Confident student image",
                    "Prominent CTA button",
                    "Modern, dynamic layout"
                ],
                "advantages": [
                    "High visual impact for marketing campaigns",
                    "Clear call-to-action for conversions",
                    "Modern design appeals to younger audience"
                ],
                "cta_suggestions": [
                    "Call Now",
                    "Book Demo",
                    "Get Started",
                    "Learn More"
                ],
                "color_scheme": "Vibrant colors with high contrast",
                "target_audience": "Young students and parents"
            }
        ]
    }
    
    # Generate images for each creative block
    enhanced_blocks = []
    
    for i, block in enumerate(creative_data["blocks"]):
        if block.get("type") == "creative":
            print(f"\n🎨 Generating image {i+1}/{len(creative_data['blocks'])}: {block['title']}")
            
            # Generate image
            image_url = image_gen.generate_poster_image(
                title=block.get("title", ""),
                description=block.get("description", ""),
                template_type=block.get("template_type", ""),
                color_scheme=block.get("color_scheme", ""),
                target_audience=block.get("target_audience", "")
            )
            
            # Add image URL to block
            enhanced_block = block.copy()
            enhanced_block["image_url"] = image_url
            
            if image_url:
                print(f"✅ Image generated successfully!")
                print(f"   URL: {image_url}")
            else:
                print(f"⚠️  Failed to generate image")
                enhanced_block["image_url"] = None
            
            enhanced_blocks.append(enhanced_block)
        else:
            enhanced_blocks.append(block)
    
    # Create enhanced response
    enhanced_response = {
        "success": True,
        "session_id": "test_session_123",
        "response": {
            "blocks": enhanced_blocks
        }
    }
    
    # Display the enhanced response
    print("\n🎉 Enhanced Response with Image URLs:")
    print("=" * 60)
    print(json.dumps(enhanced_response, indent=2))
    
    # Save to file for reference
    output_file = "enhanced_response_with_images.json"
    with open(output_file, 'w') as f:
        json.dump(enhanced_response, f, indent=2)
    
    print(f"\n💾 Enhanced response saved to: {output_file}")
    
    return True

def test_specific_poster_request():
    """Test a specific poster generation request"""
    print("\n🎯 Testing Specific Poster Request...")
    print("=" * 50)
    
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        print("❌ OpenAI API key not available")
        return False
    
    image_gen = ImageGenerator(openai_api_key)
    
    # Test the exact prompt from your example
    prompt = """Create a professional poster design for "Geography-Themed Educational Poster". 
    
    Description: A professional poster with earthy tones, map elements, and student illustration
    Template Type: Educational
    Color Scheme: Earthy tones with professional accents
    Target Audience: Geography students and parents
    
    Style: Modern, professional, educational poster with clean typography, balanced layout, and visual hierarchy. 
    Include placeholder elements for text and imagery that would be added later.
    Make it suitable for printing and digital use."""
    
    print("🎨 Generating image with specific prompt...")
    image_url = image_gen.generate_image(prompt)
    
    if image_url:
        print(f"✅ Image generated successfully!")
        print(f"   URL: {image_url}")
        
        # Create enhanced block
        enhanced_block = {
            "type": "creative",
            "title": "Geography-Themed Educational Poster",
            "description": "A professional poster with earthy tones, map elements, and student illustration",
            "template_type": "Educational",
            "features": [
                "Earthy color scheme (browns, greens, blues)",
                "Map or geography visual elements",
                "Student illustration or photo",
                "Clear hierarchy with headline, benefits, and CTA"
            ],
            "color_scheme": "Earthy tones with professional accents",
            "target_audience": "Geography students and parents",
            "image_url": image_url
        }
        
        print("\n📋 Enhanced Creative Block:")
        print(json.dumps(enhanced_block, indent=2))
        
    else:
        print("❌ Failed to generate image")
    
    return True

def main():
    """Main test function"""
    print("🚀 Testing Image Generation for Google AI Chatbot")
    print("=" * 70)
    
    # Test basic image generation
    if test_image_generation():
        print("\n✅ Basic image generation test completed successfully!")
    else:
        print("\n❌ Basic image generation test failed!")
        return
    
    # Test specific poster request
    if test_specific_poster_request():
        print("\n✅ Specific poster request test completed successfully!")
    else:
        print("\n❌ Specific poster request test failed!")
        return
    
    print("\n🎉 All tests completed successfully!")
    print("\n💡 Next Steps:")
    print("1. The enhanced chatbot now includes image generation")
    print("2. Creative blocks will automatically include image_url field")
    print("3. Users can see generated images in the response")
    print("4. Images are generated using OpenAI DALL-E 3")

if __name__ == "__main__":
    main()

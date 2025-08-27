#!/usr/bin/env python3
"""
Setup script for OpenAI integration
Helps users configure their OpenAI API key and environment
"""

import os
import sys

def setup_openai():
    """Setup OpenAI configuration"""
    
    print("🚀 OpenAI Integration Setup")
    print("=" * 40)
    
    # Check if .env file exists
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"✅ .env file already exists")
        
        # Check if OPENAI_API_KEY is set
        with open(env_file, 'r') as f:
            content = f.read()
            if 'OPENAI_API_KEY=' in content:
                print("✅ OPENAI_API_KEY is configured in .env")
                
                # Check if it's not the default value
                if 'sk-your-actual-openai-api-key-here' in content:
                    print("⚠️  Warning: OPENAI_API_KEY still has default value")
                    print("   Please update it with your actual API key")
                else:
                    print("✅ OPENAI_API_KEY appears to be configured")
                    return True
            else:
                print("❌ OPENAI_API_KEY not found in .env")
    else:
        print(f"❌ .env file not found")
    
    print("\n🔧 Setup Instructions:")
    print("1. Get your OpenAI API key from: https://platform.openai.com/api-keys")
    print("2. Create .env file: cp env_template.txt .env")
    print("3. Edit .env and set your actual API key")
    print("4. The key should start with 'sk-'")
    
    # Offer to create .env from template
    template_file = "env_template.txt"
    if os.path.exists(template_file):
        print(f"\n📋 Template file found: {template_file}")
        response = input("Would you like me to create .env from template? (y/n): ").lower().strip()
        
        if response == 'y':
            try:
                import shutil
                shutil.copy(template_file, env_file)
                print(f"✅ Created {env_file} from template")
                print(f"📝 Please edit {env_file} and add your actual API key")
                return True
            except Exception as e:
                print(f"❌ Error creating .env: {e}")
                return False
        else:
            print("📝 Please create .env manually and add your API key")
            return False
    else:
        print(f"❌ Template file {template_file} not found")
        print("📝 Please create .env manually with:")
        print("   OPENAI_API_KEY=sk-your-actual-api-key-here")
        return False

def verify_setup():
    """Verify that OpenAI is properly configured"""
    
    print("\n🔍 Verifying OpenAI Configuration...")
    
    try:
        # Try to import and initialize OpenAI service
        from google_ads_new.openai_service import GoogleAdsOpenAIService
        
        try:
            openai_service = GoogleAdsOpenAIService()
            print("✅ OpenAI service initialized successfully")
            print("✅ Configuration is working correctly")
            return True
            
        except ValueError as e:
            print(f"❌ OpenAI service initialization failed: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all requirements are installed:")
        print("   pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main setup function"""
    
    print("🤖 Setting up OpenAI integration for Google Ads analysis...")
    
    # Setup OpenAI configuration
    if setup_openai():
        print("\n✅ Setup completed successfully!")
        
        # Verify the setup
        if verify_setup():
            print("\n🎉 OpenAI integration is ready to use!")
            print("\n📚 Next steps:")
            print("1. Test the integration: python demo_openai_integration.py")
            print("2. Use the chat interface to test analysis actions")
            print("3. All 43 analysis actions now use OpenAI for dynamic responses")
        else:
            print("\n⚠️  Setup completed but verification failed")
            print("   Please check your configuration and try again")
    else:
        print("\n❌ Setup failed")
        print("   Please follow the instructions above and try again")
        sys.exit(1)

if __name__ == "__main__":
    main()


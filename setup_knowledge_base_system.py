#!/usr/bin/env python3
"""
Setup Script for Knowledge Base System
Installs dependencies and configures the system
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"   stdout: {e.stdout}")
        if e.stderr:
            print(f"   stderr: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_pip():
    """Check if pip is available"""
    print("📦 Checking pip availability...")
    try:
        import pip
        print("✅ pip is available")
        return True
    except ImportError:
        print("❌ pip not found")
        return False

def install_requirements():
    """Install required packages"""
    print("📚 Installing required packages...")
    
    # Upgrade pip first
    if not run_command("python -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    requirements_file = "requirements_knowledge_base.txt"
    if Path(requirements_file).exists():
        if not run_command(f"pip install -r {requirements_file}", "Installing requirements"):
            return False
    else:
        print("⚠️  Requirements file not found, installing core packages manually...")
        
        # Install core packages manually
        core_packages = [
            "langchain",
            "langchain-openai", 
            "langchain-community",
            "chromadb",
            "watchdog",
            "openai",
            "python-dotenv"
        ]
        
        for package in core_packages:
            if not run_command(f"pip install {package}", f"Installing {package}"):
                print(f"⚠️  Failed to install {package}, continuing...")
    
    return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        "knowledge_base_docs",
        "knowledge_base_docs/processed",
        "knowledge_base_docs/embeddings", 
        "knowledge_base_docs/logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def check_environment_variables():
    """Check and guide user on environment variables"""
    print("🔑 Checking environment variables...")
    
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        
        print("\n💡 To set environment variables:")
        if platform.system() == "Windows":
            print("   set OPENAI_API_KEY=your_api_key_here")
        else:
            print("   export OPENAI_API_KEY=your_api_key_here")
        
        print("\n   Or create a .env file with:")
        print("   OPENAI_API_KEY=your_api_key_here")
        
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def test_imports():
    """Test if all required packages can be imported"""
    print("🧪 Testing package imports...")
    
    packages_to_test = [
        "langchain",
        "langchain_openai",
        "langchain_community", 
        "chromadb",
        "watchdog"
    ]
    
    failed_imports = []
    
    for package in packages_to_test:
        try:
            __import__(package)
            print(f"✅ {package} imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import {package}: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n⚠️  {len(failed_imports)} packages failed to import")
        return False
    
    print("✅ All packages imported successfully")
    return True

def create_sample_files():
    """Create sample knowledge base files"""
    print("📝 Creating sample files...")
    
    # Copy the Google Ads basics file if it exists
    source_file = "knowledge_base_docs/google_ads_basics.md"
    if Path(source_file).exists():
        print(f"✅ Sample file already exists: {source_file}")
    else:
        print("⚠️  Sample file not found, you can add your own knowledge base files to the knowledge_base_docs/ folder")
    
    return True

def show_next_steps():
    """Show next steps for the user"""
    print("\n🎉 Knowledge Base System Setup Complete!")
    print("=" * 50)
    
    print("\n📋 Next Steps:")
    print("1. Add your knowledge base files to the 'knowledge_base_docs/' folder")
    print("2. Run the knowledge base manager:")
    print("   python knowledge_base_manager.py")
    print("3. Start the enhanced chatbot:")
    print("   python enhanced_chatbot.py")
    
    print("\n📚 Supported File Types:")
    print("   - .md (Markdown)")
    print("   - .txt (Text)")
    print("   - .html (HTML)")
    print("   - .pdf (PDF)")
    print("   - .docx (Word)")
    
    print("\n🔧 System Features:")
    print("   - Automatic file monitoring")
    print("   - Vector embeddings with OpenAI")
    print("   - Chroma vector database")
    print("   - LangChain integration")
    print("   - ChatGPT-powered responses")
    print("   - Django integration (optional)")
    
    print("\n💡 Tips:")
    print("   - Files are automatically processed when added to the folder")
    print("   - Embeddings are created only once per file")
    print("   - The system detects file changes and reprocesses as needed")
    print("   - Use the 'stats' command in the chatbot to see system status")

def main():
    """Main setup function"""
    print("🚀 Setting up Knowledge Base System...")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        return False
    
    if not check_pip():
        return False
    
    # Create directories
    if not create_directories():
        return False
    
    # Install requirements
    if not install_requirements():
        print("⚠️  Some packages failed to install, but continuing...")
    
    # Test imports
    if not test_imports():
        print("⚠️  Some packages failed to import, but continuing...")
    
    # Check environment variables
    check_environment_variables()
    
    # Create sample files
    create_sample_files()
    
    # Show next steps
    show_next_steps()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Setup completed successfully!")
        else:
            print("\n❌ Setup encountered issues. Please check the errors above.")
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        import traceback
        traceback.print_exc()

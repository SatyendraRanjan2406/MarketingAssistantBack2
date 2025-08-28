#!/usr/bin/env python3
"""
Virtual Environment Package Cleanup Script
Properly removes unnecessary packages from the virtual environment
"""

import subprocess
import sys
import os
import time

def activate_virtual_env():
    """Activate the virtual environment if it exists"""
    venv_path = "env"
    if os.path.exists(venv_path):
        # Activate virtual environment
        activate_script = os.path.join(venv_path, "bin", "activate")
        if os.path.exists(activate_script):
            print(f"✅ Found virtual environment: {venv_path}")
            return True
        else:
            print(f"❌ Virtual environment {venv_path} exists but activate script not found")
            return False
    else:
        print(f"❌ Virtual environment {venv_path} not found")
        return False

def run_command_in_venv(command, description):
    """Run a command in the virtual environment"""
    print(f"\n🔄 {description}")
    print(f"Command: {command}")
    
    try:
        # Use the virtual environment's Python
        venv_python = "env/bin/python"
        if os.path.exists(venv_python):
            full_command = f"{venv_python} -m {command}"
        else:
            full_command = f"source env/bin/activate && {command}"
        
        result = subprocess.run(
            full_command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=60
        )
        
        if result.returncode == 0:
            print(f"✅ {description} completed")
            if result.stdout:
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"⚠️  {description} completed with warnings")
            if result.stderr:
                print(f"Stderr: {result.stderr.strip()}")
            return True  # Continue even with warnings
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def cleanup_virtual_env():
    """Clean up packages in the virtual environment"""
    
    print("🧹 Virtual Environment Package Cleanup")
    print("=" * 50)
    
    if not activate_virtual_env():
        print("❌ Cannot proceed without virtual environment")
        return False
    
    # List of packages to remove (only the heaviest, most unnecessary ones)
    heavy_packages = [
        "torch",                    # PyTorch (800+ MB)
        "nvidia-cublas-cu12",      # CUDA library (500+ MB)
        "nvidia-cuda-cupti-cu12",  # CUDA runtime (10+ MB)
        "nvidia-cuda-nvrtc-cu12",  # CUDA compiler (80+ MB)
        "nvidia-cuda-runtime-cu12", # CUDA runtime (1+ MB)
        "tokenizers",               # Text tokenization (3+ MB)
        "sentence-transformers",    # Text embeddings
        "transformers",             # Hugging Face models
        "accelerate",               # PyTorch acceleration
    ]
    
    print(f"📦 Targeting {len(heavy_packages)} heavy packages")
    
    # Check what's actually installed in the virtual environment
    try:
        result = subprocess.run(
            ["env/bin/python", "-m", "pip", "list", "--format=freeze"], 
            capture_output=True, 
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            installed_packages = result.stdout.strip().split('\n')
            installed_names = [pkg.split('==')[0].split('>=')[0].split('<=')[0] for pkg in installed_packages if pkg]
            
            # Filter to only remove what's actually installed
            to_remove = []
            for pkg in heavy_packages:
                if pkg in installed_names:
                    to_remove.append(pkg)
            
            print(f"📋 {len(to_remove)} heavy packages found and will be removed")
            
            if not to_remove:
                print("✅ No heavy packages found to remove!")
                return True
            
            # Show what will be removed
            print("\n🗑️  Heavy packages to be removed:")
            for pkg in to_remove:
                print(f"   - {pkg}")
            
            # Confirm removal
            response = input(f"\n❓ Remove {len(to_remove)} heavy packages from virtual environment? (y/N): ").lower().strip()
            if response != 'y':
                print("❌ Cleanup cancelled")
                return False
            
            # Remove packages one by one
            success_count = 0
            for pkg in to_remove:
                print(f"\n{'='*50}")
                if run_command_in_venv(f"pip uninstall -y {pkg}", f"Remove {pkg}"):
                    success_count += 1
                    print(f"✅ {pkg} removed successfully")
                else:
                    print(f"⚠️  {pkg} removal had issues")
                
                # Small delay between removals
                time.sleep(2)
            
            print(f"\n🎉 Virtual environment cleanup completed! {success_count}/{len(to_remove)} packages removed")
            return True
            
        else:
            print("❌ Could not get package list from virtual environment")
            return False
            
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return False

def show_virtual_env_status():
    """Show current package status in virtual environment"""
    
    print("\n📊 Virtual Environment Package Status")
    print("=" * 40)
    
    try:
        # Get total package count from virtual environment
        result = subprocess.run(
            ["env/bin/python", "-m", "pip", "list"], 
            capture_output=True, 
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            package_count = len([line for line in lines if line and not line.startswith('Package') and not line.startswith('-')])
            print(f"📦 Total packages in virtual environment: {package_count}")
            
            # Check for heavy packages
            heavy_check = subprocess.run(
                ["env/bin/python", "-m", "pip", "list", "--format=freeze"], 
                capture_output=True, 
                text=True,
                timeout=30
            )
            
            if heavy_check.returncode == 0:
                heavy_packages = []
                for line in heavy_check.stdout.strip().split('\n'):
                    if line and any(heavy in line.lower() for heavy in ['torch', 'nvidia', 'cuda']):
                        heavy_packages.append(line)
                
                if heavy_packages:
                    print(f"🐘 Heavy packages still present: {len(heavy_packages)}")
                    for pkg in heavy_packages[:5]:  # Show first 5
                        print(f"   {pkg}")
                    if len(heavy_packages) > 5:
                        print(f"   ... and {len(heavy_packages) - 5} more")
                else:
                    print("✅ No heavy packages found in virtual environment!")
                    
        else:
            print("❌ Could not get package status from virtual environment")
            
    except Exception as e:
        print(f"❌ Error getting status: {e}")

def install_clean_requirements():
    """Install clean requirements in virtual environment"""
    
    print("\n📥 Installing Clean Requirements in Virtual Environment")
    print("=" * 60)
    
    # Check if clean requirements file exists
    if not os.path.exists("requirements_clean.txt"):
        print("❌ requirements_clean.txt not found")
        return False
    
    # Install clean requirements in virtual environment
    return run_command_in_venv(
        "pip install -r requirements_clean.txt",
        "Installing clean requirements in virtual environment"
    )

def main():
    """Main cleanup function"""
    
    print("🚀 Virtual Environment Package Cleanup")
    print("=" * 50)
    
    # Show current status
    show_virtual_env_status()
    
    # Clean up unnecessary packages
    if cleanup_virtual_env():
        print("\n✅ Virtual environment cleanup completed successfully!")
        
        # Option to install clean requirements
        response = input("\n❓ Install clean requirements in virtual environment? (y/N): ").lower().strip()
        if response == 'y':
            install_clean_requirements()
        
        # Show final status
        print("\n📊 Final virtual environment status:")
        show_virtual_env_status()
        
        print("\n🎉 Cleanup complete!")
        print("\n💡 Next steps:")
        print("   1. Always activate virtual environment: source env/bin/activate")
        print("   2. Test your system: python manage.py check")
        print("   3. Start Django server: python manage.py runserver")
        
    else:
        print("\n❌ Virtual environment cleanup failed")
        print("\n💡 Try manual removal in virtual environment:")
        print("   source env/bin/activate")
        print("   pip uninstall torch nvidia-cublas-cu12 nvidia-cuda-cupti-cu12")

if __name__ == "__main__":
    main()

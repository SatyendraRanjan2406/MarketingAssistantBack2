#!/usr/bin/env python3
"""
Package Cleanup Script
Removes unnecessary packages that are not used in the codebase
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}")
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout:
                print(f"Output: {result.stdout.strip()}")
        else:
            print(f"❌ {description} failed")
            if result.stderr:
                print(f"Error: {result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False

def get_installed_packages():
    """Get list of installed packages"""
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "list", "--format=freeze"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return [line.strip() for line in result.stdout.split('\n') if line.strip()]
        return []
    except Exception as e:
        print(f"❌ Error getting installed packages: {e}")
        return []

def cleanup_unnecessary_packages():
    """Remove packages that are not needed"""
    
    print("🧹 Package Cleanup - Removing Unnecessary Dependencies")
    print("=" * 60)
    
    # List of packages to remove (not used in your codebase)
    packages_to_remove = [
        # Heavy PyTorch/CUDA packages (NOT needed - you use OpenAI API)
        "torch",
        "nvidia-cublas-cu12",
        "nvidia-cuda-cupti-cu12", 
        "nvidia-cuda-nvrtc-cu12",
        "nvidia-cuda-runtime-cu12",
        
        # Tokenizers (NOT needed - OpenAI handles this)
        "tokenizers",
        
        # SQL parsing (NOT used in your code)
        "sqlparse",
        
        # Retry logic (NOT used in your code)
        "tenacity",
        
        # Heavy ML packages (NOT needed)
        "sentence-transformers",
        "transformers",
        "accelerate",
        
        # Unused data science packages
        "matplotlib",
        "seaborn", 
        "plotly",
        
        # Unused text processing
        "tiktoken",
        "unstructured",
        
        # Unused file formats
        "pypdf",
        
        # Duplicate/conflicting packages
        "protobuf",  # May conflict with google-api-core
    ]
    
    print(f"\n📦 Found {len(packages_to_remove)} packages to remove")
    
    # Check what's actually installed
    installed_packages = get_installed_packages()
    installed_names = [pkg.split('==')[0].split('>=')[0].split('<=')[0] for pkg in installed_packages]
    
    # Filter to only remove what's actually installed
    to_remove = []
    for pkg in packages_to_remove:
        if pkg in installed_names:
            to_remove.append(pkg)
    
    print(f"📋 {len(to_remove)} packages are actually installed and will be removed")
    
    if not to_remove:
        print("✅ No unnecessary packages found to remove!")
        return True
    
    # Show what will be removed
    print("\n🗑️  Packages to be removed:")
    for pkg in to_remove:
        print(f"   - {pkg}")
    
    # Confirm removal
    response = input(f"\n❓ Remove {len(to_remove)} unnecessary packages? (y/N): ").lower().strip()
    if response != 'y':
        print("❌ Cleanup cancelled")
        return False
    
    # Remove packages
    success_count = 0
    for pkg in to_remove:
        if run_command(f"{sys.executable} -m pip uninstall -y {pkg}", f"Removing {pkg}"):
            success_count += 1
    
    print(f"\n🎉 Cleanup completed! {success_count}/{len(to_remove)} packages removed successfully")
    
    # Show remaining packages
    print("\n📊 Remaining packages:")
    remaining = get_installed_packages()
    for pkg in remaining[:20]:  # Show first 20
        print(f"   {pkg}")
    
    if len(remaining) > 20:
        print(f"   ... and {len(remaining) - 20} more packages")
    
    return True

def install_clean_requirements():
    """Install only the necessary packages"""
    
    print("\n📥 Installing Clean Requirements")
    print("=" * 40)
    
    # Check if clean requirements file exists
    if not os.path.exists("requirements_clean.txt"):
        print("❌ requirements_clean.txt not found")
        return False
    
    # Install clean requirements
    return run_command(
        f"{sys.executable} -m pip install -r requirements_clean.txt",
        "Installing clean requirements"
    )

def show_package_sizes():
    """Show sizes of installed packages"""
    
    print("\n📏 Package Size Analysis")
    print("=" * 30)
    
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "list", "--format=freeze"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            packages = result.stdout.strip().split('\n')
            
            # Get package info
            total_size = 0
            large_packages = []
            
            for pkg in packages:
                if pkg:
                    pkg_name = pkg.split('==')[0]
                    try:
                        # Try to get package size (this is approximate)
                        size_result = subprocess.run(
                            [sys.executable, "-m", "pip", "show", pkg_name], 
                            capture_output=True, text=True
                        )
                        if size_result.returncode == 0:
                            # Extract location to estimate size
                            for line in size_result.stdout.split('\n'):
                                if line.startswith('Location:'):
                                    location = line.split(':', 1)[1].strip()
                                    if os.path.exists(location):
                                        pkg_size = sum(
                                            os.path.getsize(os.path.join(dirpath, filename))
                                            for dirpath, dirnames, filenames in os.walk(location)
                                            for filename in filenames
                                        )
                                        total_size += pkg_size
                                        
                                        if pkg_size > 10 * 1024 * 1024:  # > 10MB
                                            large_packages.append((pkg_name, pkg_size))
                                    break
                    except:
                        pass
            
            print(f"📊 Total estimated package size: {total_size / (1024*1024):.1f} MB")
            
            if large_packages:
                print("\n🐘 Large packages (>10MB):")
                for pkg_name, size in sorted(large_packages, key=lambda x: x[1], reverse=True):
                    print(f"   {pkg_name}: {size / (1024*1024):.1f} MB")
            
    except Exception as e:
        print(f"❌ Error analyzing package sizes: {e}")

def main():
    """Main cleanup function"""
    
    print("🚀 Package Cleanup and Optimization")
    print("=" * 50)
    
    # Show current package sizes
    show_package_sizes()
    
    # Clean up unnecessary packages
    if cleanup_unnecessary_packages():
        print("\n✅ Package cleanup completed successfully!")
        
        # Option to install clean requirements
        response = input("\n❓ Install clean requirements? (y/N): ").lower().strip()
        if response == 'y':
            install_clean_requirements()
        
        # Show final package sizes
        print("\n📊 Final package analysis:")
        show_package_sizes()
        
        print("\n🎉 Cleanup complete! Your environment is now optimized.")
        print("\n💡 Benefits:")
        print("   ✅ Smaller virtual environment")
        print("   ✅ Faster startup times")
        print("   ✅ No unnecessary dependencies")
        print("   ✅ Cleaner package tree")
        print("   ✅ Better compatibility")
        
    else:
        print("\n❌ Package cleanup failed")

if __name__ == "__main__":
    main()

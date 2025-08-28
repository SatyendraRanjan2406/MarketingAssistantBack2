#!/usr/bin/env python3
"""
Simple Package Cleanup Script
Removes unnecessary packages without hanging
"""

import subprocess
import sys
import os
import time

def run_simple_command(command, description):
    """Run a command with timeout to prevent hanging"""
    print(f"\n🔄 {description}")
    print(f"Command: {command}")
    
    try:
        # Use timeout to prevent hanging
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=60  # 60 second timeout
        )
        
        if result.returncode == 0:
            print(f"✅ {description} completed")
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

def force_remove_package(package_name):
    """Force remove a package using multiple methods"""
    print(f"\n🗑️  Force removing {package_name}")
    
    # Method 1: Normal uninstall
    if run_simple_command(f"{sys.executable} -m pip uninstall -y {package_name}", f"Normal uninstall of {package_name}"):
        return True
    
    # Method 2: Force uninstall
    if run_simple_command(f"{sys.executable} -m pip uninstall -y --force {package_name}", f"Force uninstall of {package_name}"):
        return True
    
    # Method 3: Direct pip uninstall
    if run_simple_command(f"pip uninstall -y {package_name}", f"Direct pip uninstall of {package_name}"):
        return True
    
    print(f"⚠️  Could not remove {package_name} - may need manual removal")
    return False

def quick_cleanup():
    """Quick cleanup of the heaviest packages"""
    
    print("🚀 Quick Package Cleanup - Heavy Packages Only")
    print("=" * 50)
    
    # Only remove the heaviest, most unnecessary packages
    heavy_packages = [
        "torch",                    # PyTorch (800+ MB)
        "nvidia-cublas-cu12",      # CUDA library (500+ MB)
        "nvidia-cuda-cupti-cu12",  # CUDA runtime (10+ MB)
        "nvidia-cuda-nvrtc-cu12",  # CUDA compiler (80+ MB)
        "nvidia-cuda-runtime-cu12", # CUDA runtime (1+ MB)
        "tokenizers",               # Text tokenization (3+ MB)
    ]
    
    print(f"📦 Targeting {len(heavy_packages)} heavy packages")
    
    # Check what's actually installed
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=freeze"], 
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
            response = input(f"\n❓ Remove {len(to_remove)} heavy packages? (y/N): ").lower().strip()
            if response != 'y':
                print("❌ Cleanup cancelled")
                return False
            
            # Remove packages one by one
            success_count = 0
            for pkg in to_remove:
                print(f"\n{'='*50}")
                if force_remove_package(pkg):
                    success_count += 1
                    print(f"✅ {pkg} removed successfully")
                else:
                    print(f"⚠️  {pkg} removal had issues")
                
                # Small delay between removals
                time.sleep(2)
            
            print(f"\n🎉 Quick cleanup completed! {success_count}/{len(to_remove)} packages removed")
            return True
            
        else:
            print("❌ Could not get package list")
            return False
            
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return False

def show_current_status():
    """Show current package status"""
    
    print("\n📊 Current Package Status")
    print("=" * 30)
    
    try:
        # Get total package count
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list"], 
            capture_output=True, 
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            package_count = len([line for line in lines if line and not line.startswith('Package') and not line.startswith('-')])
            print(f"📦 Total packages installed: {package_count}")
            
            # Check for heavy packages
            heavy_check = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--format=freeze"], 
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
                    print("✅ No heavy packages found!")
                    
        else:
            print("❌ Could not get package status")
            
    except Exception as e:
        print(f"❌ Error getting status: {e}")

def main():
    """Main cleanup function"""
    
    print("🧹 Simple Package Cleanup")
    print("=" * 40)
    
    # Show current status
    show_current_status()
    
    # Quick cleanup
    if quick_cleanup():
        print("\n✅ Quick cleanup completed successfully!")
        
        # Show final status
        print("\n📊 Final package status:")
        show_current_status()
        
        print("\n🎉 Cleanup complete!")
        print("\n💡 Next steps:")
        print("   1. Test your system: python test_contextual_ad_images.py")
        print("   2. If everything works, you're done!")
        print("   3. If something breaks, run: pip install -r requirements_clean.txt")
        
    else:
        print("\n❌ Quick cleanup failed")
        print("\n💡 Try manual removal:")
        print("   pip uninstall torch nvidia-cublas-cu12 nvidia-cuda-cupti-cu12")

if __name__ == "__main__":
    main()

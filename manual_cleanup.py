#!/usr/bin/env python3
"""
Manual Package Cleanup Script
Step-by-step removal of heavy packages
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and show output"""
    print(f"\n🔄 {description}")
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=120)
        
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
        print(f"⏰ {description} timed out - continuing anyway")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def manual_cleanup():
    """Manual step-by-step cleanup"""
    
    print("🧹 Manual Package Cleanup - Step by Step")
    print("=" * 50)
    
    print("\n📋 This script will remove heavy packages one by one.")
    print("💡 If any step fails, you can continue manually.")
    
    # Step 1: Check current packages
    print("\n" + "="*50)
    print("STEP 1: Check current packages")
    print("="*50)
    
    run_command(f"{sys.executable} -m pip list --format=freeze | grep -E '(torch|nvidia|tokenizers)'", "Check for heavy packages")
    
    # Step 2: Remove torch
    print("\n" + "="*50)
    print("STEP 2: Remove PyTorch (torch)")
    print("="*50)
    
    response = input("❓ Remove PyTorch (torch)? This is the heaviest package (y/N): ").lower().strip()
    if response == 'y':
        run_command(f"{sys.executable} -m pip uninstall -y torch", "Remove PyTorch")
    else:
        print("⏭️  Skipping PyTorch removal")
    
    # Step 3: Remove CUDA libraries
    print("\n" + "="*50)
    print("STEP 3: Remove CUDA libraries")
    print("="*50)
    
    cuda_packages = [
        "nvidia-cublas-cu12",
        "nvidia-cuda-cupti-cu12", 
        "nvidia-cuda-nvrtc-cu12",
        "nvidia-cuda-runtime-cu12"
    ]
    
    for pkg in cuda_packages:
        response = input(f"❓ Remove {pkg}? (y/N): ").lower().strip()
        if response == 'y':
            run_command(f"{sys.executable} -m pip uninstall -y {pkg}", f"Remove {pkg}")
        else:
            print(f"⏭️  Skipping {pkg} removal")
    
    # Step 4: Remove other heavy packages
    print("\n" + "="*50)
    print("STEP 4: Remove other heavy packages")
    print("="*50)
    
    other_packages = [
        "tokenizers",
        "sentence-transformers",
        "transformers",
        "accelerate"
    ]
    
    for pkg in other_packages:
        response = input(f"❓ Remove {pkg}? (y/N): ").lower().strip()
        if response == 'y':
            run_command(f"{sys.executable} -m pip uninstall -y {pkg}", f"Remove {pkg}")
        else:
            print(f"⏭️  Skipping {pkg} removal")
    
    # Step 5: Remove unused utilities
    print("\n" + "="*50)
    print("STEP 5: Remove unused utilities")
    print("="*50)
    
    utility_packages = [
        "sqlparse",
        "tenacity",
        "matplotlib",
        "seaborn",
        "plotly"
    ]
    
    for pkg in utility_packages:
        response = input(f"❓ Remove {pkg}? (y/N): ").lower().strip()
        if response == 'y':
            run_command(f"{sys.executable} -m pip uninstall -y {pkg}", f"Remove {pkg}")
        else:
            print(f"⏭️  Skipping {pkg} removal")
    
    # Step 6: Final check
    print("\n" + "="*50)
    print("STEP 6: Final package check")
    print("="*50)
    
    run_command(f"{sys.executable} -m pip list --format=freeze | grep -E '(torch|nvidia|tokenizers)'", "Check remaining heavy packages")
    
    print("\n🎉 Manual cleanup completed!")
    print("\n💡 Next steps:")
    print("   1. Test your system: python test_contextual_ad_images.py")
    print("   2. If everything works, you're done!")
    print("   3. If something breaks, run: pip install -r requirements_clean.txt")

def quick_commands():
    """Show quick commands for manual execution"""
    
    print("\n" + "="*50)
    print("QUICK COMMANDS (if script fails)")
    print("="*50)
    
    print("\n🔧 Run these commands manually in your terminal:")
    print("\n# Remove PyTorch and CUDA:")
    print("pip uninstall -y torch")
    print("pip uninstall -y nvidia-cublas-cu12")
    print("pip uninstall -y nvidia-cuda-cupti-cu12")
    print("pip uninstall -y nvidia-cuda-nvrtc-cu12")
    print("pip uninstall -y nvidia-cuda-runtime-cu12")
    
    print("\n# Remove other heavy packages:")
    print("pip uninstall -y tokenizers")
    print("pip uninstall -y sentence-transformers")
    print("pip uninstall -y transformers")
    print("pip uninstall -y accelerate")
    
    print("\n# Remove unused utilities:")
    print("pip uninstall -y sqlparse")
    print("pip uninstall -y tenacity")
    print("pip uninstall -y matplotlib")
    print("pip uninstall -y seaborn")
    print("pip uninstall -y plotly")
    
    print("\n# Check what's left:")
    print("pip list --format=freeze | grep -E '(torch|nvidia|tokenizers)'")

def main():
    """Main function"""
    
    print("🚀 Manual Package Cleanup")
    print("=" * 40)
    
    print("\nChoose cleanup method:")
    print("1. Interactive step-by-step cleanup")
    print("2. Show quick commands for manual execution")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        manual_cleanup()
    elif choice == "2":
        quick_commands()
    elif choice == "3":
        print("👋 Exiting cleanup")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()

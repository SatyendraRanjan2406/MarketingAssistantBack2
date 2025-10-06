#!/bin/bash
# Quick EC2 Space Cleanup - Run this first for immediate space recovery

echo "🚀 Quick EC2 Space Cleanup"
echo "=========================="

# Check current space
echo "📊 Current disk usage:"
df -h

echo ""
echo "🧹 Quick cleanup starting..."

# 1. Remove git lock file (if exists)
echo "🔓 Removing git lock files..."
rm -f /home/ubuntu/MarketingAssistantBack2/.git/index.lock 2>/dev/null
rm -f /home/ubuntu/marketing_assistant_back/.git/index.lock 2>/dev/null

# 2. Clean package caches
echo "📦 Cleaning package caches..."
sudo apt clean
sudo apt autoremove -y

# 3. Clean logs
echo "📝 Cleaning logs..."
sudo journalctl --vacuum-time=1d
sudo find /var/log -name "*.log" -type f -mtime +3 -delete

# 4. Clean temp files
echo "🗑️ Cleaning temp files..."
sudo rm -rf /tmp/*
sudo rm -rf /var/tmp/*

# 5. Clean Docker (if exists)
echo "🐳 Cleaning Docker..."
if command -v docker &> /dev/null; then
    docker system prune -f
fi

# 6. Clean Python cache
echo "🐍 Cleaning Python cache..."
find /home -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find /home -name "*.pyc" -type f -delete 2>/dev/null

# 7. Clean project files
echo "📁 Cleaning project files..."
cd /home/ubuntu/MarketingAssistantBack2 2>/dev/null || cd /home/ubuntu/marketing_assistant_back 2>/dev/null

if [ -d "." ]; then
    # Remove generated files
    rm -rf generated_images/* 2>/dev/null
    rm -rf generated_visualizations/* 2>/dev/null
    rm -rf __pycache__/ 2>/dev/null
    rm -rf */__pycache__/ 2>/dev/null
    rm -rf .pytest_cache/ 2>/dev/null
    rm -f *.log 2>/dev/null
    rm -f *.db-journal 2>/dev/null
    
    echo "✅ Project cleanup completed"
fi

echo ""
echo "📊 Disk usage after quick cleanup:"
df -h

echo ""
echo "✅ Quick cleanup completed!"
echo "💡 Run the full cleanup script for more space recovery"

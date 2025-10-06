#!/bin/bash
# EC2 Disk Space Cleanup Script
# Run these commands on your EC2 server to free up space

echo "🧹 Starting EC2 Disk Space Cleanup..."
echo "=================================="

# 1. Check current disk usage
echo "📊 Current disk usage:"
df -h

echo ""
echo "🔍 Finding largest directories:"
du -sh /* 2>/dev/null | sort -hr | head -10

echo ""
echo "🧹 Starting cleanup process..."

# 2. Clean up package caches
echo "📦 Cleaning package caches..."
sudo apt clean
sudo apt autoremove -y
sudo apt autoclean

# 3. Clean up logs
echo "📝 Cleaning log files..."
sudo journalctl --vacuum-time=3d
sudo find /var/log -name "*.log" -type f -mtime +7 -delete
sudo find /var/log -name "*.log.*" -type f -mtime +7 -delete

# 4. Clean up temporary files
echo "🗑️ Cleaning temporary files..."
sudo rm -rf /tmp/*
sudo rm -rf /var/tmp/*
sudo rm -rf /tmp/.*

# 5. Clean up old kernels (be careful)
echo "🔧 Cleaning old kernels..."
sudo apt autoremove --purge

# 6. Clean up snap packages
echo "📦 Cleaning snap packages..."
sudo snap list --all | awk '/disabled/{print $1, $3}' | while read snapname revision; do 
    sudo snap remove "$snapname" --revision="$revision"
done

# 7. Clean up Docker (if using Docker)
echo "🐳 Cleaning Docker..."
if command -v docker &> /dev/null; then
    docker system prune -a -f
    docker volume prune -f
    docker image prune -a -f
fi

# 8. Clean up Python cache
echo "🐍 Cleaning Python cache..."
find /home -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find /home -name "*.pyc" -type f -delete 2>/dev/null
find /home -name "*.pyo" -type f -delete 2>/dev/null

# 9. Clean up pip cache
echo "📦 Cleaning pip cache..."
pip cache purge 2>/dev/null || true

# 10. Clean up npm cache (if using Node.js)
echo "📦 Cleaning npm cache..."
if command -v npm &> /dev/null; then
    npm cache clean --force
fi

# 11. Clean up old backups
echo "💾 Cleaning old backups..."
find /home -name "*.bak" -type f -mtime +30 -delete 2>/dev/null
find /home -name "*.backup" -type f -mtime +30 -delete 2>/dev/null

# 12. Clean up old downloads
echo "📥 Cleaning downloads..."
rm -rf /home/ubuntu/Downloads/* 2>/dev/null

# 13. Clean up your project specifically
echo "📁 Cleaning project files..."
cd /home/ubuntu/MarketingAssistantBack2 2>/dev/null || cd /home/ubuntu/marketing_assistant_back 2>/dev/null || echo "Project directory not found"

if [ -d "." ]; then
    # Remove generated images
    rm -rf generated_images/* 2>/dev/null
    rm -rf generated_visualizations/* 2>/dev/null
    
    # Remove Python cache
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
    find . -name "*.pyc" -type f -delete 2>/dev/null
    find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null
    find . -name ".coverage" -type f -delete 2>/dev/null
    find . -name "htmlcov" -type d -exec rm -rf {} + 2>/dev/null
    
    # Remove log files
    find . -name "*.log" -type f -mtime +7 -delete 2>/dev/null
    find . -name "*.log.*" -type f -mtime +7 -delete 2>/dev/null
    
    # Remove temporary files
    find . -name "*.tmp" -type f -delete 2>/dev/null
    find . -name "*.temp" -type f -delete 2>/dev/null
    
    # Remove old database files
    rm -f db.sqlite3.old 2>/dev/null
    rm -f *.db-journal 2>/dev/null
    
    echo "✅ Project cleanup completed"
fi

# 14. Clean up old snapshots (if using LVM)
echo "💾 Cleaning LVM snapshots..."
sudo lvremove /dev/ubuntu-vg/ubuntu-lv-snap-* 2>/dev/null || true

# 15. Clean up old journal logs
echo "📝 Cleaning journal logs..."
sudo journalctl --vacuum-size=100M

# 16. Clean up old apt cache
echo "📦 Cleaning apt cache..."
sudo apt-get clean
sudo apt-get autoclean

# 17. Clean up old kernels (more aggressive)
echo "🔧 Cleaning old kernels (aggressive)..."
sudo apt-get autoremove --purge -y

# 18. Clean up old log files in /var/log
echo "📝 Cleaning /var/log..."
sudo find /var/log -type f -name "*.log" -mtime +30 -delete
sudo find /var/log -type f -name "*.gz" -mtime +30 -delete

# 19. Clean up old core dumps
echo "💥 Cleaning core dumps..."
sudo find /var/crash -type f -mtime +7 -delete 2>/dev/null

# 20. Clean up old user data
echo "👤 Cleaning user data..."
sudo find /home -name ".cache" -type d -exec rm -rf {} + 2>/dev/null
sudo find /home -name ".thumbnails" -type d -exec rm -rf {} + 2>/dev/null

echo ""
echo "🎉 Cleanup completed!"
echo "=================================="

# Show final disk usage
echo "📊 Final disk usage:"
df -h

echo ""
echo "🔍 Largest directories after cleanup:"
du -sh /* 2>/dev/null | sort -hr | head -10

echo ""
echo "✅ EC2 cleanup completed successfully!"
echo "💡 Consider setting up automatic cleanup with cron jobs"

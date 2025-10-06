#!/bin/bash
# Setup Disk Space Monitoring for EC2
# This script sets up automatic cleanup and monitoring

echo "📊 Setting up EC2 Disk Space Monitoring"
echo "======================================"

# 1. Create a cleanup script
echo "📝 Creating automatic cleanup script..."
sudo tee /usr/local/bin/cleanup-disk.sh > /dev/null << 'EOF'
#!/bin/bash
# Automatic disk cleanup script

# Check disk usage
USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')

if [ $USAGE -gt 80 ]; then
    echo "$(date): Disk usage is ${USAGE}% - Running cleanup" >> /var/log/disk-cleanup.log
    
    # Quick cleanup
    apt clean
    apt autoremove -y
    journalctl --vacuum-time=3d
    find /var/log -name "*.log" -type f -mtime +7 -delete
    find /home -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
    find /home -name "*.pyc" -type f -delete 2>/dev/null
    
    # Clean project files
    cd /home/ubuntu/MarketingAssistantBack2 2>/dev/null || cd /home/ubuntu/marketing_assistant_back 2>/dev/null
    if [ -d "." ]; then
        rm -rf generated_images/* 2>/dev/null
        rm -rf generated_visualizations/* 2>/dev/null
        rm -rf __pycache__/ 2>/dev/null
        rm -rf */__pycache__/ 2>/dev/null
    fi
    
    echo "$(date): Cleanup completed" >> /var/log/disk-cleanup.log
fi
EOF

# Make it executable
sudo chmod +x /usr/local/bin/cleanup-disk.sh

# 2. Setup cron job for daily cleanup
echo "⏰ Setting up daily cleanup cron job..."
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/cleanup-disk.sh") | crontab -

# 3. Setup disk usage monitoring
echo "📊 Setting up disk usage monitoring..."
sudo tee /usr/local/bin/check-disk.sh > /dev/null << 'EOF'
#!/bin/bash
# Disk usage checker

USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
THRESHOLD=85

if [ $USAGE -gt $THRESHOLD ]; then
    echo "WARNING: Disk usage is ${USAGE}% (threshold: ${THRESHOLD}%)"
    echo "Consider running: /usr/local/bin/cleanup-disk.sh"
    
    # Send email notification if mail is configured
    if command -v mail &> /dev/null; then
        echo "Disk usage is ${USAGE}% on $(hostname)" | mail -s "Disk Space Warning" root
    fi
else
    echo "Disk usage is ${USAGE}% - OK"
fi
EOF

sudo chmod +x /usr/local/bin/check-disk.sh

# 4. Setup hourly disk check
echo "⏰ Setting up hourly disk check..."
(crontab -l 2>/dev/null; echo "0 * * * * /usr/local/bin/check-disk.sh") | crontab -

# 5. Create log rotation for cleanup logs
echo "📝 Setting up log rotation..."
sudo tee /etc/logrotate.d/disk-cleanup > /dev/null << 'EOF'
/var/log/disk-cleanup.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
EOF

# 6. Test the scripts
echo "🧪 Testing cleanup script..."
/usr/local/bin/cleanup-disk.sh

echo "🧪 Testing disk check script..."
/usr/local/bin/check-disk.sh

echo ""
echo "✅ Disk monitoring setup completed!"
echo "=================================="
echo "📊 Daily cleanup: 2:00 AM"
echo "📊 Hourly disk check: Every hour"
echo "📝 Logs: /var/log/disk-cleanup.log"
echo "🔧 Manual cleanup: /usr/local/bin/cleanup-disk.sh"
echo "📊 Manual check: /usr/local/bin/check-disk.sh"

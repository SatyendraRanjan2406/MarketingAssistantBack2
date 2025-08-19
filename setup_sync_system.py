#!/usr/bin/env python3
"""
Setup script for Google Ads Data Synchronization System
This script sets up the complete sync system with cron jobs and PostgreSQL
"""

import os
import sys
import subprocess
import getpass
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Not running in a virtual environment")
        print("   Consider activating your virtual environment first")
    
    print("✅ Dependencies check completed")
    return True

def setup_postgresql():
    """Set up PostgreSQL database"""
    print("\n🗄️  PostgreSQL Setup")
    print("=" * 40)
    
    # Check if PostgreSQL is running
    if not run_command("pg_isready", "Checking PostgreSQL connection"):
        print("❌ PostgreSQL is not running or not accessible")
        print("   Please start PostgreSQL and try again")
        return False
    
    # Get database configuration
    print("\n📝 Database Configuration:")
    db_name = input("Database name (default: marketing_assistant_db): ").strip() or "marketing_assistant_db"
    db_user = input("Database user (default: satyendra): ").strip() or "satyendra"
    db_password = getpass.getpass("Database password: ")
    db_host = input("Database host (default: localhost): ").strip() or "localhost"
    db_port = input("Database port (default: 5432): ").strip() or "5432"
    
    # Create database if it doesn't exist
    create_db_cmd = f"createdb -h {db_host} -p {db_port} -U {db_user} {db_name}"
    if not run_command(create_db_cmd, f"Creating database '{db_name}'"):
        print("⚠️  Database creation failed - it may already exist")
    
    # Update .env file with database settings
    env_content = f"""# Database Configuration
DB_NAME={db_name}
DB_USER={db_user}
DB_PASSWORD={db_password}
DB_HOST={db_host}
DB_PORT={db_port}

# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Google Ads API Configuration
GOOGLE_ADS_CLIENT_ID=your_google_ads_client_id
GOOGLE_ADS_CLIENT_SECRET=your_google_ads_client_secret
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=your_login_customer_id

# Redis Configuration (for Celery)
REDIS_URL=redis://localhost:6379/0

# Django Configuration
DEBUG=True
SECRET_KEY=your_django_secret_key_here
ALLOWED_HOSTS=localhost,127.0.0.1
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Database configuration saved to .env file")
    return True

def setup_redis():
    """Set up Redis for Celery"""
    print("\n🔴 Redis Setup")
    print("=" * 30)
    
    # Check if Redis is running
    if not run_command("redis-cli ping", "Checking Redis connection"):
        print("⚠️  Redis is not running")
        print("   Installing and starting Redis...")
        
        # Try to install Redis (macOS)
        if sys.platform == "darwin":
            if not run_command("brew install redis", "Installing Redis via Homebrew"):
                print("❌ Failed to install Redis via Homebrew")
                print("   Please install Redis manually and try again")
                return False
        
        # Start Redis
        if not run_command("brew services start redis", "Starting Redis service"):
            print("❌ Failed to start Redis service")
            return False
    
    print("✅ Redis is running")
    return True

def install_python_dependencies():
    """Install required Python packages"""
    print("\n🐍 Python Dependencies")
    print("=" * 30)
    
    requirements = [
        "psycopg2-binary",  # PostgreSQL adapter
        "celery",            # Async task queue
        "redis",             # Redis client
        "django-celery-beat", # Celery beat for scheduled tasks
    ]
    
    for package in requirements:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            print(f"❌ Failed to install {package}")
            return False
    
    print("✅ All Python dependencies installed")
    return True

def setup_django():
    """Set up Django with migrations"""
    print("\n🐘 Django Setup")
    print("=" * 25)
    
    # Run migrations
    if not run_command("python manage.py makemigrations", "Creating database migrations"):
        return False
    
    if not run_command("python manage.py migrate", "Applying database migrations"):
        return False
    
    # Create superuser if needed
    create_superuser = input("\nCreate a superuser? (y/N): ").lower()
    if create_superuser == 'y':
        if not run_command("python manage.py createsuperuser", "Creating superuser"):
            print("⚠️  Superuser creation failed - you can create one later")
    
    print("✅ Django setup completed")
    return True

def setup_celery():
    """Set up Celery configuration"""
    print("\n🌿 Celery Setup")
    print("=" * 25)
    
    # Create Celery beat schedule configuration
    celery_beat_config = """from celery import Celery
from celery.schedules import crontab

app = Celery('marketing_assistant_project')

# Configure Celery Beat schedule
app.conf.beat_schedule = {
    'daily-sync': {
        'task': 'google_ads_app.data_sync_service.sync_last_week_data_task',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2:00 AM
    },
    'weekly-sync': {
        'task': 'google_ads_app.data_sync_service.sync_historical_weeks_task',
        'schedule': crontab(hour=3, minute=0, day_of_week=0),  # Sunday at 3:00 AM
        'args': (None, 10),  # All accounts, 10 weeks
    },
}

app.conf.timezone = 'UTC'
"""
    
    with open('celery_beat_config.py', 'w') as f:
        f.write(celery_beat_config)
    
    print("✅ Celery configuration created")
    return True

def setup_cron():
    """Set up cron jobs"""
    print("\n⏰ Cron Jobs Setup")
    print("=" * 25)
    
    # Get project path
    project_path = Path.cwd().absolute()
    venv_path = Path(sys.executable).parent
    
    # Create cron configuration
    cron_content = f"""# Google Ads Marketing Assistant - Cron Jobs
# Generated by setup script

# Daily sync job - runs every day at 2:00 AM
0 2 * * * cd {project_path} && {venv_path}/python manage.py sync_daily_data >> /var/log/google_ads_daily_sync.log 2>&1

# Weekly sync job - runs every Sunday at 3:00 AM
0 3 * * 0 cd {project_path} && {venv_path}/python manage.py sync_historical_data --all-accounts --weeks 10 >> /var/log/google_ads_weekly_sync.log 2>&1

# Log rotation - runs monthly
0 5 1 * * find /var/log/google_ads_*.log -mtime +30 -delete
"""
    
    with open('crontab.txt', 'w') as f:
        f.write(cron_content)
    
    print("✅ Cron configuration created in crontab.txt")
    print("\n📋 To install cron jobs, run:")
    print(f"   crontab crontab.txt")
    print("\n📋 Or manually add to your crontab:")
    print(f"   crontab -e")
    
    return True

def create_startup_scripts():
    """Create startup scripts for the sync system"""
    print("\n🚀 Startup Scripts")
    print("=" * 25)
    
    # Create start script
    start_script = """#!/bin/bash
# Start Google Ads Marketing Assistant with sync system

echo "Starting Google Ads Marketing Assistant..."

# Start Redis (if not running)
if ! pgrep -x "redis-server" > /dev/null; then
    echo "Starting Redis..."
    brew services start redis
fi

# Start Celery worker
echo "Starting Celery worker..."
celery -A marketing_assistant_project worker --loglevel=info &

# Start Celery beat (scheduler)
echo "Starting Celery beat..."
celery -A marketing_assistant_project beat --loglevel=info &

# Start Django server
echo "Starting Django server..."
python manage.py runserver

echo "All services started!"
"""
    
    with open('start_sync_system.sh', 'w') as f:
        f.write(start_script)
    
    # Make executable
    os.chmod('start_sync_system.sh', 0o755)
    
    # Create stop script
    stop_script = """#!/bin/bash
# Stop Google Ads Marketing Assistant sync system

echo "Stopping Google Ads Marketing Assistant..."

# Stop Celery processes
pkill -f "celery.*worker"
pkill -f "celery.*beat"

# Stop Django server
pkill -f "manage.py runserver"

echo "All services stopped!"
"""
    
    with open('stop_sync_system.sh', 'w') as f:
        f.write(stop_script)
    
    os.chmod('stop_sync_system.sh', 0o755)
    
    print("✅ Startup scripts created:")
    print("   - start_sync_system.sh")
    print("   - stop_sync_system.sh")
    
    return True

def main():
    """Main setup function"""
    print("🚀 Google Ads Marketing Assistant - Sync System Setup")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup steps
    setup_steps = [
        ("PostgreSQL Database", setup_postgresql),
        ("Redis", setup_redis),
        ("Python Dependencies", install_python_dependencies),
        ("Django", setup_django),
        ("Celery", setup_celery),
        ("Cron Jobs", setup_cron),
        ("Startup Scripts", create_startup_scripts),
    ]
    
    for step_name, step_func in setup_steps:
        if not step_func():
            print(f"\n❌ Setup failed at: {step_name}")
            print("Please fix the issue and run the setup again")
            sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update your .env file with actual API keys")
    print("2. Install cron jobs: crontab crontab.txt")
    print("3. Start the system: ./start_sync_system.sh")
    print("4. Test the sync system with: python manage.py sync_daily_data --dry-run")
    
    print("\n📚 Documentation:")
    print("- Cron jobs: crontab.txt")
    print("- API endpoints: /google-ads/api/sync/")
    print("- Management commands: python manage.py help")

if __name__ == "__main__":
    main()

# 🚀 Google Ads Data Synchronization System

A comprehensive data synchronization system for Google Ads Marketing Assistant that automatically syncs campaign data, performance metrics, and historical data using cron jobs, Celery, and PostgreSQL.

## ✨ Features

- **🕐 Daily Sync**: Automatically syncs last week's data every day at 2:00 AM
- **📅 Weekly Sync**: Syncs historical data (curr-1 to curr-10 weeks) every Sunday at 3:00 AM
- **🔄 Async Processing**: Uses Celery for background task processing
- **📊 PostgreSQL Storage**: Robust database storage with proper indexing
- **🔍 Sync Logging**: Comprehensive logging of all sync operations
- **🎯 Force Sync API**: REST API to force sync N weeks of data
- **👤 User Login Sync**: Triggers sync when users log in (optional)
- **📈 Performance Monitoring**: Track sync performance and errors

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Cron Jobs     │    │   Celery Beat   │    │   Django App    │
│                 │    │   (Scheduler)   │    │                 │
│ • Daily Sync    │───▶│ • Daily Tasks   │───▶│ • Sync Service  │
│ • Weekly Sync   │    │ • Weekly Tasks  │    │ • API Endpoints │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Celery Worker │    │   PostgreSQL    │
                       │                 │    │                 │
                       │ • Task Queue    │    │ • Data Storage  │
                       │ • Background    │    │ • Sync Logs     │
                       │   Processing    │    │ • Performance   │
                       └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │     Redis       │
                       │                 │
                       │ • Task Broker   │
                       │ • Result Store  │
                       └─────────────────┘
```

## 🚀 Quick Start

### 1. Automated Setup (Recommended)

```bash
# Run the comprehensive setup script
python setup_sync_system.py
```

This script will:
- Set up PostgreSQL database
- Install Redis and Python dependencies
- Configure Celery and cron jobs
- Create startup scripts
- Set up Django migrations

### 2. Manual Setup

#### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Virtual environment

#### Installation Steps

```bash
# 1. Install Python dependencies
pip install psycopg2-binary celery redis django-celery-beat

# 2. Set up environment variables
cp .env.example .env
# Edit .env with your database and API credentials

# 3. Run Django migrations
python manage.py makemigrations
python manage.py migrate

# 4. Install cron jobs
crontab crontab.txt
```

## 📋 Cron Jobs

### Daily Sync (2:00 AM)
```bash
0 2 * * * cd /path/to/marketing_assistant && /path/to/venv/bin/python manage.py sync_daily_data >> /var/log/google_ads_daily_sync.log 2>&1
```

### Weekly Sync (Sunday 3:00 AM)
```bash
0 3 * * 0 cd /path/to/marketing_assistant && /path/to/venv/bin/python manage.py sync_historical_data --all-accounts --weeks 10 >> /var/log/google_ads_weekly_sync.log 2>&1
```

## 🔌 API Endpoints

### Data Synchronization

#### Force Sync N Weeks
```http
POST /google-ads/api/sync/force_sync/
Content-Type: application/json

{
    "account_id": 1,
    "weeks": 10
}
```

#### Sync Last Week Data
```http
POST /google-ads/api/sync/sync_last_week/
```

#### Get Sync Status
```http
GET /google-ads/api/sync/sync_status/
```

#### Sync Specific Account
```http
POST /google-ads/api/sync-account/{account_id}/
Content-Type: application/json

{
    "weeks": 10,
    "sync_type": "historical"
}
```

### Response Format
```json
{
    "success": true,
    "message": "Force sync initiated for 10 weeks",
    "sync_log_id": 123,
    "task_id": "abc-123-def",
    "account_name": "My Google Ads Account"
}
```

## 🛠️ Management Commands

### Daily Data Sync
```bash
# Sync all accounts
python manage.py sync_daily_data

# Sync specific account
python manage.py sync_daily_data --account-id 1

# Dry run (no actual syncing)
python manage.py sync_daily_data --dry-run
```

### Historical Data Sync
```bash
# Sync all accounts (10 weeks)
python manage.py sync_historical_data --all-accounts

# Sync specific account (5 weeks)
python manage.py sync_historical_data --account-id 1 --weeks 5

# Dry run
python manage.py sync_historical_data --all-accounts --dry-run
```

## 🌿 Celery Tasks

### Available Tasks
- `sync_last_week_data_task`: Sync last week's data
- `sync_historical_weeks_task`: Sync historical weeks data
- `force_sync_n_weeks_task`: Force sync N weeks
- `sync_new_account_data_task`: Sync new account data

### Starting Celery
```bash
# Start Celery worker
celery -A marketing_assistant_project worker --loglevel=info

# Start Celery beat (scheduler)
celery -A marketing_assistant_project beat --loglevel=info
```

## 📊 Database Models

### DataSyncLog
Tracks all synchronization operations:
- Sync type (daily, historical, force, new_account)
- Account reference
- Date ranges
- Results and status
- Timing information

### GoogleAdsAccount
Enhanced with sync-related fields:
- `last_sync_at`: Last successful sync timestamp
- `sync_status`: Current sync status (pending, in_progress, completed, failed)

## 🔄 Sync Process

### 1. Daily Sync Process
1. Calculate date range (last 7 days)
2. Get all active accounts
3. For each account:
   - Sync campaigns, ad groups, keywords
   - Sync performance data for the date range
   - Update account sync timestamp
4. Log sync operation

### 2. Historical Sync Process
1. Calculate week ranges (curr-1 to curr-N weeks)
2. For each week:
   - Sync data for that specific week
   - Handle errors gracefully
3. Log overall sync operation

### 3. Force Sync Process
1. Validate weeks parameter (1-52 weeks)
2. Create sync log entry
3. Trigger async historical sync
4. Return task ID for monitoring

## 📈 Monitoring & Logging

### Sync Logs
All sync operations are logged with:
- Timestamp and duration
- Success/failure status
- Detailed results
- Error messages (if any)

### Performance Metrics
- Sync duration per account
- Records synced per operation
- Error rates and types
- Account sync frequency

### Log Files
- `/var/log/google_ads_daily_sync.log`
- `/var/log/google_ads_weekly_sync.log`
- Django application logs

## 🚨 Error Handling

### Graceful Degradation
- Individual account failures don't stop other accounts
- Retry mechanisms for transient errors
- Comprehensive error logging
- Fallback responses for API endpoints

### Common Issues
1. **API Rate Limits**: Automatic retry with exponential backoff
2. **Network Errors**: Logged and retried
3. **Authentication Failures**: Account marked as failed, requires manual intervention
4. **Data Validation Errors**: Logged with details for debugging

## 🔧 Configuration

### Environment Variables
```bash
# Database
DB_NAME=marketing_assistant_db
DB_USER=satyendra
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Google Ads API
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_DEVELOPER_TOKEN=your_token
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
```

### Django Settings
```python
# Celery Configuration
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}
```

## 🧪 Testing

### Test Sync Operations
```bash
# Test daily sync (dry run)
python manage.py sync_daily_data --dry-run

# Test historical sync (dry run)
python manage.py sync_historical_data --all-accounts --dry-run

# Test specific account sync
python manage.py sync_historical_data --account-id 1 --weeks 5 --dry-run
```

### Test API Endpoints
```bash
# Test force sync
curl -X POST http://localhost:8000/google-ads/api/sync/force_sync/ \
  -H "Content-Type: application/json" \
  -d '{"account_id": 1, "weeks": 10}'

# Test sync status
curl http://localhost:8000/google-ads/api/sync/sync_status/
```

## 🚀 Production Deployment

### Systemd Services
Create systemd services for Celery and Django:

```ini
# /etc/systemd/system/google-ads-celery.service
[Unit]
Description=Google Ads Celery Worker
After=network.target

[Service]
Type=forking
User=your_user
WorkingDirectory=/path/to/marketing_assistant
ExecStart=/path/to/venv/bin/celery -A marketing_assistant_project worker --loglevel=info
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

### Log Rotation
```bash
# /etc/logrotate.d/google-ads
/var/log/google_ads_*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 your_user your_group
}
```

## 📚 Troubleshooting

### Common Issues

#### 1. Celery Worker Not Starting
```bash
# Check Redis connection
redis-cli ping

# Check Celery configuration
celery -A marketing_assistant_project inspect active
```

#### 2. Sync Jobs Failing
```bash
# Check sync logs
tail -f /var/log/google_ads_daily_sync.log

# Check Django logs
python manage.py shell
from google_ads_app.models import DataSyncLog
DataSyncLog.objects.filter(status='failed').order_by('-created_at')[:5]
```

#### 3. Database Connection Issues
```bash
# Test database connection
python manage.py dbshell

# Check environment variables
python manage.py shell
from django.conf import settings
print(settings.DATABASES)
```

### Debug Mode
Enable debug logging in Django settings:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'google_ads_app': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the logs and error messages
- Ensure all dependencies are properly installed

---

**Happy Syncing! 🚀📊**

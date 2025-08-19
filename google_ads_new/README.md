# 🚀 Google Ads New App

A fresh, clean implementation of Google Ads data management for the Marketing Assistant project.

## ✨ Features

### 📊 **Data Models**
- **GoogleAdsAccount**: Manage Google Ads accounts with sync status tracking
- **GoogleAdsCampaign**: Campaign information with status and budget details
- **GoogleAdsAdGroup**: Ad group management within campaigns
- **GoogleAdsKeyword**: Keyword tracking with match types and quality scores
- **GoogleAdsPerformance**: Performance metrics with automatic calculations
- **DataSyncLog**: Comprehensive sync operation logging

### 🔧 **Admin Interface**
- **Inline Editing**: Edit campaigns, ad groups, and keywords directly from account views
- **Performance Summary**: Real-time performance metrics display
- **Advanced Filtering**: Filter by status, type, date ranges, and more
- **Search Functionality**: Search across all fields for quick data access
- **Custom Admin Site**: Branded admin interface with custom headers

### 📈 **Automatic Calculations**
- **CTR**: Click-through rate (clicks/impressions)
- **CPC**: Cost per click
- **CPM**: Cost per thousand impressions
- **Conversion Rate**: Conversions per click
- **ROAS**: Return on ad spend

### 🔄 **Sync Service**
- **Daily Sync**: Sync last week's data
- **Historical Sync**: Sync data for specified number of weeks
- **Force Sync**: Manual sync for specific time periods
- **Comprehensive Logging**: Track all sync operations with detailed results

## 🚀 Quick Start

### 1. **Installation**
The app is already added to `INSTALLED_APPS` in your Django settings.

### 2. **Database Setup**
```bash
# Create and apply migrations
python manage.py makemigrations google_ads_new
python manage.py migrate
```

### 3. **Create Sample Data**
```bash
# Create sample data for testing
python manage.py create_new_sample_data --username admin --clean
```

### 4. **Access Admin**
- **URL**: `/admin/`
- **Username**: `admin_new`
- **Password**: `admin123`

## 📋 **Usage Examples**

### **Creating an Account**
```python
from google_ads_new.models import GoogleAdsAccount
from django.contrib.auth.models import User

user = User.objects.get(username='admin')
account = GoogleAdsAccount.objects.create(
    user=user,
    customer_id='123456789',
    account_name='My Google Ads Account',
    currency_code='USD',
    time_zone='America/New_York'
)
```

### **Running a Sync**
```python
from google_ads_new.sync_service import GoogleAdsSyncService

sync_service = GoogleAdsSyncService()
result = sync_service.sync_last_week_data()
print(f"Sync completed: {result['success']}")
```

### **Querying Performance Data**
```python
from google_ads_new.models import GoogleAdsPerformance
from django.db.models import Sum

# Get total impressions for an account
total_impressions = GoogleAdsPerformance.objects.filter(
    account__account_name='My Google Ads Account'
).aggregate(total=Sum('impressions'))['total']
```

## 🏗️ **Architecture**

### **Models Structure**
```
GoogleAdsAccount
├── GoogleAdsCampaign
│   ├── GoogleAdsAdGroup
│   │   └── GoogleAdsKeyword
│   └── GoogleAdsPerformance
└── GoogleAdsPerformance (account-level)
```

### **Sync Flow**
1. **Initialize**: Set up sync parameters and account selection
2. **Authenticate**: Verify account access and permissions
3. **Fetch Data**: Retrieve data from Google Ads API
4. **Process**: Transform and validate incoming data
5. **Store**: Save to database with calculated metrics
6. **Log**: Record sync operation details and results

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Google Ads API Configuration
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
```

### **Database Settings**
The app uses the same database configuration as your main project.

## 📊 **Performance Considerations**

- **Indexes**: Optimized database indexes on frequently queried fields
- **Select Related**: Efficient database queries with related object loading
- **Bulk Operations**: Support for bulk create/update operations
- **Async Processing**: Celery integration for background sync operations

## 🧪 **Testing**

### **Running Tests**
```bash
python manage.py test google_ads_new
```

### **Sample Data**
Use the management command to create realistic test data:
```bash
python manage.py create_new_sample_data --username testuser --clean
```

## 🔮 **Future Enhancements**

- **Real-time Sync**: Webhook-based real-time data updates
- **Advanced Analytics**: Custom reporting and visualization
- **Multi-account Management**: Bulk operations across multiple accounts
- **API Rate Limiting**: Intelligent API call management
- **Data Export**: CSV/Excel export functionality
- **Custom Dashboards**: User-configurable performance dashboards

## 📝 **Contributing**

1. Follow Django coding standards
2. Add comprehensive docstrings
3. Include unit tests for new features
4. Update this README for significant changes

## 📞 **Support**

For questions or issues:
- Check the Django admin interface for data validation
- Review sync logs for operation details
- Check database migrations for schema changes

---

**Built with ❤️ for the Marketing Assistant project**

# 🚀 Live Monitoring API for Google Ads

A comprehensive real-time monitoring and insights API for Google Ads accounts, providing live performance data, alerts, optimization recommendations, and trend analysis.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [API Endpoints](#api-endpoints)
- [Response Structure](#response-structure)
- [Installation & Setup](#installation--setup)
- [Usage Examples](#usage-examples)
- [Data Sources](#data-sources)
- [Configuration](#configuration)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## 🌟 Overview

The Live Monitoring API provides real-time insights into your Google Ads performance, similar to the dashboard you described:

- **Live Performance Monitoring**: Real-time metrics and insights
- **Smart Alerts**: Automatic detection of performance issues
- **Optimization Recommendations**: AI-powered suggestions for improvement
- **Trend Analysis**: Historical performance trends and comparisons
- **Multi-Account Support**: Monitor multiple Google Ads accounts simultaneously

## ✨ Features

### 🔍 **Real-Time Monitoring**
- Live performance data updated every few minutes
- 24-hour, 7-day, and 30-day performance comparisons
- Automatic calculation of derived metrics (CTR, CPC, CPM, ROAS)

### 🚨 **Smart Alerts**
- High CPM alerts with severity levels
- Budget utilization warnings
- Quality score monitoring
- Conversion rate drop detection

### 📊 **Performance Insights**
- ROAS trending analysis
- CTR improvement tracking
- Conversion rate monitoring
- Cost optimization opportunities

### 🎯 **Optimization Recommendations**
- Budget reallocation suggestions
- Keyword performance insights
- Ad group optimization opportunities
- Campaign performance analysis

### 📈 **Trend Analysis**
- Week-over-week performance comparisons
- Metric trend identification (up/down)
- Historical performance patterns
- Seasonal trend detection

## 🔒 **Security & Access Control**

### **User Isolation**
The Live Monitoring API implements strict user isolation to ensure users can only access their own Google Ads accounts:

- **Authentication Required**: All endpoints require valid JWT authentication
- **Account Ownership Verification**: Users can only access accounts they own
- **Database Query Isolation**: All database queries are filtered by user ID
- **Cross-User Access Prevention**: Attempts to access other users' accounts are blocked

### **Security Features**

#### 1. **Custom Permission Class**
```python
class GoogleAdsAccountAccessPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Verify user owns the Google Ads account
        return obj.user == request.user
```

#### 2. **Multiple Security Layers**
- **Layer 1**: Django REST Framework authentication
- **Layer 2**: Custom permission class
- **Layer 3**: Account ownership verification in views
- **Layer 4**: Database query filtering by user

#### 3. **Security Logging**
All access attempts are logged for security monitoring:
```python
logger.info(f"User {user.username} accessed live monitoring for account {account.account_name}")
logger.warning(f"Security violation: User {user.username} attempted to access account {account_id}")
```

#### 4. **Access Control Response Examples**

**Successful Access:**
```json
{
  "status": "success",
  "data": {
    "account": {
      "ownership_verified": true,
      "access_level": "owner"
    },
    "user_info": {
      "username": "user123",
      "user_id": 1,
      "access_verified": true
    }
  }
}
```

**Access Denied:**
```json
{
  "status": "error",
  "message": "Access denied: You can only access your own Google Ads accounts",
  "data": null
}
```

### **Testing Security**

Run the security test suite to verify access control:
```bash
python test_live_monitoring_security.py
```

This will test:
- User isolation
- Database query isolation
- API access control
- Cross-user access prevention

## 🔌 API Endpoints

### 1. **Main Live Monitoring** - `GET /api/live-monitoring/`
Returns monitoring data for all user accounts with aggregated insights.

**Response**: Comprehensive monitoring data across all accounts

### 2. **Account-Specific Monitoring** - `GET /api/live-monitoring/account/{account_id}/`
Returns detailed monitoring data for a specific Google Ads account.

**Parameters**:
- `account_id` (int): The ID of the Google Ads account

**Response**: Detailed monitoring data for the specified account

### 3. **Quick Stats** - `GET /api/live-monitoring/account/{account_id}/quick-stats/`
Returns quick statistics and campaign overview for an account.

**Response**: Active campaigns, spend, ROAS, conversions, and campaign overview

### 4. **Insights** - `GET /api/live-monitoring/account/{account_id}/insights/`
Returns specific types of insights for an account.

**Query Parameters**:
- `type` (string, optional): Type of insights to retrieve
  - `performance`: Performance insights only
  - `alerts`: Alerts and warnings only
  - `optimization`: Optimization recommendations only
  - `trends`: Trend analysis only
  - `all` (default): All insights

**Response**: Filtered insights based on the specified type

### 5. **Performance Metrics** - `GET /api/live-monitoring/account/{account_id}/performance/`
Returns detailed performance metrics and insights.

**Response**: Performance metrics, budget insights, and conversion insights

## 📊 Response Structure

### Main Response Format
```json
{
  "status": "success",
  "message": "Live monitoring data retrieved successfully",
  "data": {
    "timestamp": "2024-01-15T10:30:00Z",
    "last_updated": "2 minutes ago",
    "monitoring": {
      "performance": [...],
      "alerts": [...],
      "optimization": [...],
      "trends": [...]
    },
    "quick_stats": {...},
    "campaign_overview": {...},
    "performance_metrics": {...},
    "budget_insights": {...},
    "conversion_insights": {...}
  }
}
```

### Monitoring Sections

#### Performance Insights
```json
{
  "type": "PERFORMANCE",
  "time": "38m ago",
  "title": "ROAS Trending Up",
  "change": "+30%",
  "description": "Return on ad spend increased significantly"
}
```

#### Alerts
```json
{
  "type": "ALERT",
  "time": "1h ago",
  "title": "High CPM Alert",
  "change": "+45%",
  "description": "Cost per mille requires immediate attention",
  "severity": "high"
}
```

#### Optimization
```json
{
  "type": "OPTIMIZATION",
  "time": "2h ago",
  "title": "Budget Reallocation",
  "change": "12%",
  "description": "Opportunity to optimize budget distribution"
}
```

#### Quick Stats
```json
{
  "active_campaigns": 24,
  "total_spend_24h": "$12,450",
  "avg_roas": "3.8x",
  "conversions": "1,247",
  "impressions_24h": "45,230",
  "clicks_24h": "2,340",
  "ctr_24h": "5.17%"
}
```

## 🛠️ Installation & Setup

### 1. **Prerequisites**
- Django 4.2+ with Django REST Framework
- PostgreSQL database
- Google Ads API access
- Required Python packages (see requirements)

### 2. **Install Dependencies**
```bash
pip install -r requirements_clean.txt
```

### 3. **Database Setup**
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. **Environment Variables**
Ensure these are set in your `.env` file:
```bash
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
```

### 5. **URL Configuration**
The API endpoints are automatically included in your Django URLs when you import the live monitoring views.

## 📖 Usage Examples

### 1. **Get All Accounts Monitoring Data**
```python
import requests

# Get monitoring data for all accounts
response = requests.get(
    "http://localhost:8000/google_ads_new/api/live-monitoring/",
    headers={"Authorization": "Bearer YOUR_JWT_TOKEN"}
)

if response.status_code == 200:
    data = response.json()
    print(f"Monitoring {data['data']['total_accounts']} accounts")
    print(f"Total active campaigns: {data['data']['aggregated']['total_active_campaigns']}")
```

### 2. **Get Account-Specific Monitoring**
```python
# Get monitoring for account ID 1
response = requests.get(
    "http://localhost:8000/google_ads_new/api/live-monitoring/account/1/",
    headers={"Authorization": "Bearer YOUR_JWT_TOKEN"}
)

if response.status_code == 200:
    data = response.json()
    account_name = data['data']['account']['name']
    quick_stats = data['data']['monitoring']['quick_stats']
    print(f"Account: {account_name}")
    print(f"Active campaigns: {quick_stats['active_campaigns']}")
    print(f"24h spend: {quick_stats['total_spend_24h']}")
```

### 3. **Get Specific Insights**
```python
# Get only performance insights
response = requests.get(
    "http://localhost:8000/google_ads_new/api/live-monitoring/account/1/insights/?type=performance",
    headers={"Authorization": "Bearer YOUR_JWT_TOKEN"}
)

if response.status_code == 200:
    data = response.json()
    performance_insights = data['data']['insights']
    for insight in performance_insights:
        print(f"{insight['title']}: {insight['change']}")
```

### 4. **Get Quick Stats**
```python
# Get quick stats for account
response = requests.get(
    "http://localhost:8000/google_ads_new/api/live-monitoring/account/1/quick-stats/",
    headers={"Authorization": "Bearer YOUR_JWT_TOKEN"}
)

if response.status_code == 200:
    data = response.json()
    quick_stats = data['data']['quick_stats']
    campaign_overview = data['data']['campaign_overview']
    
    print(f"Quick Stats for {data['data']['account']['name']}:")
    print(f"  Active campaigns: {quick_stats['active_campaigns']}")
    print(f"  Total spend (24h): {quick_stats['total_spend_24h']}")
    print(f"  Average ROAS: {quick_stats['avg_roas']}")
    print(f"  Conversions: {quick_stats['conversions']}")
```

## 🗄️ Data Sources

The API aggregates data from multiple sources:

### **GoogleAdsPerformance Model**
- Impressions, clicks, cost, conversions
- Real-time performance metrics
- Historical trend data

### **GoogleAdsCampaign Model**
- Campaign status and configuration
- Budget information
- Campaign type and settings

### **GoogleAdsAccount Model**
- Account configuration
- Currency and timezone settings
- Sync status and last update

### **Calculated Metrics**
- CTR (Click-Through Rate)
- CPC (Cost Per Click)
- CPM (Cost Per Mille)
- ROAS (Return On Ad Spend)
- Conversion Rate

## ⚙️ Configuration

### **Alert Thresholds**
Configure alert sensitivity in the service:
```python
# In live_monitoring_service.py
class LiveMonitoringService:
    def __init__(self, account_id=None):
        # High CPM threshold
        self.high_cpm_threshold = 50  # $50 per 1000 impressions
        
        # Budget utilization threshold
        self.budget_utilization_threshold = 90  # 90%
        
        # Quality score threshold
        self.low_quality_score_threshold = 5  # Score below 5
```

### **Time Periods**
Customize monitoring time periods:
```python
# Default time periods
self.last_24h = self.now - timedelta(hours=24)
self.last_7d = self.now - timedelta(days=7)
self.last_30d = self.now - timedelta(days=30)
```

### **Performance Thresholds**
Set thresholds for significant changes:
```python
# Only show insights for significant changes
if abs(roas_change) >= 5:  # 5% change threshold
if abs(ctr_change) >= 3:   # 3% change threshold
```

## 🧪 Testing

### 1. **Run Test Script**
```bash
python test_live_monitoring_api.py
```

### 2. **Test with Django Server**
```bash
# Start Django server
python manage.py runserver

# In another terminal, test API endpoints
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/google_ads_new/api/live-monitoring/
```

### 3. **Test Specific Endpoints**
```bash
# Test account-specific monitoring
curl http://localhost:8000/google_ads_new/api/live-monitoring/account/1/

# Test quick stats
curl http://localhost:8000/google_ads_new/api/live-monitoring/account/1/quick-stats/

# Test insights with type filter
curl "http://localhost:8000/google_ads_new/api/live-monitoring/account/1/insights/?type=performance"
```

## 🔧 Troubleshooting

### **Common Issues**

#### 1. **No Data Returned**
- Check if Google Ads accounts exist in database
- Verify account is active (`is_active=True`)
- Check if performance data exists for the time period

#### 2. **Authentication Errors**
- Ensure JWT token is valid
- Check if user has access to the account
- Verify account ownership

#### 3. **Performance Issues**
- Check database indexes on performance tables
- Monitor query execution time
- Consider caching for frequently accessed data

#### 4. **Missing Metrics**
- Verify Google Ads API sync is working
- Check if performance data is being collected
- Ensure all required fields are populated

### **Debug Mode**
Enable debug logging:
```python
import logging
logging.getLogger('google_ads_new.live_monitoring_service').setLevel(logging.DEBUG)
```

### **Data Validation**
The service includes comprehensive error handling:
- Missing data gracefully handled
- Fallback values for missing metrics
- Detailed error logging for debugging

## 🚀 Performance Optimization

### **Database Optimization**
- Indexes on frequently queried fields
- Efficient aggregation queries
- Connection pooling for high traffic

### **Caching Strategy**
- Cache monitoring data for 5-10 minutes
- Redis caching for high-frequency requests
- In-memory caching for real-time data

### **Query Optimization**
- Use `select_related` for foreign key relationships
- Aggregate data at database level
- Limit data retrieval to necessary time periods

## 🔮 Future Enhancements

### **Planned Features**
- Real-time WebSocket updates
- Custom alert rules and thresholds
- Advanced trend analysis with ML
- Automated optimization recommendations
- Multi-currency support
- Export functionality (CSV, PDF)

### **Integration Possibilities**
- Slack/Teams notifications
- Email alert system
- Dashboard widgets
- Mobile app integration
- Third-party analytics tools

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review Django logs for errors
3. Test with the provided test script
4. Verify database connectivity and data

## 📄 License

This API is part of the Marketing Assistant Backend project.

---

**🎉 The Live Monitoring API provides real-time insights into your Google Ads performance, helping you make data-driven decisions and optimize your campaigns effectively!**

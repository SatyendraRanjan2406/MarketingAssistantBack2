# Comprehensive Google Ads Sync System

This system provides a complete solution for syncing all Google Ads data into your PostgreSQL database, including accounts, campaigns, ad groups, ads, keywords, and performance metrics.

## 🎯 **What It Syncs**

### **1. Account Hierarchy**
- **Manager Account (MCC)**: Your main account that manages multiple client accounts
- **Client Accounts**: All accounts under your manager account
- **Account Details**: Name, currency, timezone, sync status

### **2. Campaign Data**
- Campaign ID, name, status
- Campaign type (Search, Display, Video, etc.)
- Start/end dates
- Budget amount and type

### **3. Ad Group Data**
- Ad group ID, name, status
- Ad group type
- Associated campaign

### **4. Ad Data**
- Ad ID, status
- Responsive search ad headlines
- Associated ad group

### **5. Keyword Data**
- Keyword ID, text, match type
- Status, quality score
- Associated ad group

### **6. Performance Data**
- Impressions, clicks, conversions
- Cost (in micros)
- Conversion value
- Date-based filtering

## 🚀 **How to Use**

### **Option 1: Django Management Command**

```bash
# Comprehensive sync (last 7 days)
python manage.py comprehensive_sync

# Custom date range (last 30 days)
python manage.py comprehensive_sync --days-back 30

# Incremental daily sync (last 1 day)
python manage.py comprehensive_sync --incremental

# Custom manager ID
python manage.py comprehensive_sync --manager-id 9762343117
```

### **Option 2: API Endpoint**

```bash
# Comprehensive sync (last 7 days)
curl -X POST http://localhost:8000/google-ads-new/api/comprehensive-sync/ \
  -H "Content-Type: application/json" \
  -d '{
    "manager_customer_id": "9762343117",
    "days_back": 7,
    "incremental": false
  }'

# Incremental daily sync
curl -X POST http://localhost:8000/google-ads-new/api/comprehensive-sync/ \
  -H "Content-Type: application/json" \
  -d '{
    "manager_customer_id": "9762343117",
    "incremental": true
  }'
```

### **Option 3: Python Code**

```python
from google_ads_new.comprehensive_sync_service import ComprehensiveGoogleAdsSyncService

# Initialize service
sync_service = ComprehensiveGoogleAdsSyncService()

# Run comprehensive sync
result = sync_service.comprehensive_sync("9762343117", days_back=7)

# Run incremental sync
result = sync_service.incremental_daily_sync("9762343117")
```

## 📊 **Sync Process**

### **Step 1: Get All Client Accounts**
```sql
SELECT 
    customer_client.client_customer, 
    customer_client.descriptive_name, 
    customer_client.currency_code, 
    customer_client.time_zone 
FROM customer_client
```

### **Step 2: For Each Account, Pull:**
1. **Campaigns**
   ```sql
   SELECT campaign.id, campaign.name, campaign.status, 
          campaign.advertising_channel_type, campaign.start_date, 
          campaign.end_date, campaign.budget_amount_micros, 
          campaign.budget_type
   FROM campaign
   WHERE campaign.status != 'REMOVED'
   ```

2. **Ad Groups**
   ```sql
   SELECT ad_group.id, ad_group.name, ad_group.status, 
          ad_group.type, campaign.id
   FROM ad_group
   WHERE ad_group.status != 'REMOVED'
   ```

3. **Ads**
   ```sql
   SELECT ad_group_ad.ad.id, ad_group_ad.ad.responsive_search_ad.headlines, 
          ad_group_ad.status, ad_group.id
   FROM ad_group_ad
   WHERE ad_group_ad.status != 'REMOVED'
   ```

4. **Keywords**
   ```sql
   SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.text, 
          ad_group_criterion.keyword.match_type, ad_group_criterion.status, 
          ad_group_criterion.quality_info.quality_score, ad_group.id
   FROM ad_group_criterion
   WHERE ad_group_criterion.type = 'KEYWORD' 
     AND ad_group_criterion.status != 'REMOVED'
   ```

5. **Performance Data** (with date filtering)
   ```sql
   SELECT campaign.id, campaign.name, ad_group.id, ad_group.name,
          ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
          metrics.impressions, metrics.clicks, metrics.cost_micros,
          metrics.conversions, metrics.conversions_value, segments.date
   FROM keyword_view
   WHERE segments.date BETWEEN '2025-08-11' AND '2025-08-18'
   ```

### **Step 3: Store in Database**
- All data is stored using Django ORM
- Uses `update_or_create` for efficient upserts
- Maintains referential integrity
- Logs all sync operations

## 🔄 **Sync Types**

### **Comprehensive Sync**
- **Purpose**: Initial sync or periodic full refresh
- **Data**: All structural data + performance data for specified date range
- **Use Case**: Weekly syncs, data recovery, initial setup

### **Incremental Daily Sync**
- **Purpose**: Daily updates for ongoing operations
- **Data**: All structural data + performance data for last 1 day
- **Use Case**: Daily maintenance, real-time updates

## 📈 **Performance Features**

### **Date-Based Filtering**
- Performance data is filtered by date range
- Reduces API calls and data transfer
- Configurable via `days_back` parameter

### **Batch Processing**
- Uses Google Ads API `search_stream` for efficient data retrieval
- Processes data in batches to handle large accounts

### **Database Transactions**
- All database operations use atomic transactions
- Ensures data consistency
- Rollback on errors

## 🗄️ **Database Schema**

### **Tables Created**
1. **GoogleAdsAccount**: Account information
2. **GoogleAdsCampaign**: Campaign data
3. **GoogleAdsAdGroup**: Ad group data
4. **GoogleAdsKeyword**: Keyword data
5. **GoogleAdsPerformance**: Performance metrics
6. **DataSyncLog**: Sync operation logs

### **Relationships**
```
GoogleAdsAccount (1) → (Many) GoogleAdsCampaign
GoogleAdsCampaign (1) → (Many) GoogleAdsAdGroup
GoogleAdsAdGroup (1) → (Many) GoogleAdsKeyword
GoogleAdsKeyword (1) → (Many) GoogleAdsPerformance
GoogleAdsAccount (1) → (Many) GoogleAdsPerformance
```

## 🧪 **Testing**

### **Test Scripts**
```bash
# Test comprehensive sync
python google_ads_new/test_comprehensive_sync.py

# Test individual components
python google_ads_new/test_with_valid_accounts.py
```

### **API Testing**
```bash
# Test sync endpoint
curl -X POST http://localhost:8000/google-ads-new/api/comprehensive-sync/ \
  -H "Content-Type: application/json" \
  -d '{"manager_customer_id": "9762343117", "days_back": 7}'
```

## 📋 **Configuration**

### **Required Settings**
1. **Google Ads API credentials** in `google-ads.yaml`
2. **PostgreSQL database** configured in Django settings
3. **Manager account ID** with access to client accounts

### **Environment Variables**
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Google Ads (in google-ads.yaml)
developer_token: YOUR_TOKEN
login_customer_id: YOUR_MANAGER_ACCOUNT_ID
client_id: YOUR_CLIENT_ID
client_secret: YOUR_CLIENT_SECRET
refresh_token: YOUR_REFRESH_TOKEN
use_proto_plus: true
```

## 🚨 **Error Handling**

### **Common Errors**
1. **API Rate Limits**: Automatic retry with exponential backoff
2. **Invalid Customer IDs**: Detailed error messages with suggestions
3. **Permission Issues**: Clear guidance on account access
4. **Network Errors**: Graceful degradation and logging

### **Logging**
- All operations are logged to `DataSyncLog` table
- Detailed error messages for debugging
- Success/failure tracking for monitoring

## 🔒 **Security**

### **Authentication**
- Uses OAuth2 refresh tokens
- Secure credential storage
- API key management

### **Data Privacy**
- No sensitive data logging
- Secure database connections
- Audit trail for all operations

## 📚 **API Reference**

### **ComprehensiveGoogleAdsSyncService**

#### **Methods**
- `comprehensive_sync(manager_customer_id, days_back=7)`: Full sync
- `incremental_daily_sync(manager_customer_id)`: Daily sync
- `get_all_client_accounts(manager_customer_id)`: Get accounts
- `get_campaigns(customer_id)`: Get campaigns
- `get_ad_groups(customer_id, campaign_id=None)`: Get ad groups
- `get_ads(customer_id, ad_group_id=None)`: Get ads
- `get_keywords(customer_id, ad_group_id=None)`: Get keywords
- `get_performance_data(customer_id, start_date, end_date)`: Get metrics

#### **Database Methods**
- `sync_account_to_database(account_data)`: Sync account
- `sync_campaigns_to_database(account, campaigns_data)`: Sync campaigns
- `sync_ad_groups_to_database(account, ad_groups_data)`: Sync ad groups
- `sync_keywords_to_database(account, keywords_data)`: Sync keywords
- `sync_performance_to_database(account, performance_data)`: Sync metrics

## 🎉 **Getting Started**

1. **Install Dependencies**
   ```bash
   pip install google-ads==28.0.0
   ```

2. **Configure Google Ads API**
   ```bash
   # Update google-ads.yaml with your credentials
   ```

3. **Run Initial Sync**
   ```bash
   python manage.py comprehensive_sync --manager-id YOUR_MANAGER_ID
   ```

4. **Set Up Daily Sync**
   ```bash
   # Add to crontab or use Celery Beat
   python manage.py comprehensive_sync --incremental
   ```

5. **Monitor Results**
   - Check Django admin for synced data
   - Review sync logs for any issues
   - Monitor database growth and performance

## 📞 **Support**

For issues or questions:
1. Check the sync logs in Django admin
2. Review error messages in the console
3. Verify Google Ads API credentials
4. Ensure database connectivity

---

**Note**: This system requires a Google Ads developer token with Basic or Standard access (not just Test access) to work with real accounts.

# Single Client Account Sync API

This API endpoint allows you to sync individual Google Ads client accounts without having to sync the entire manager account.

## 🚀 API Endpoint

**URL:** `POST /google-ads-new/api/sync-single-client/`

**Authentication:** None required (CSRF exempt for testing)

## 📋 Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `client_customer_id` | string | ✅ | - | The Google Ads client account ID to sync |
| `days_back` | integer | ❌ | 7 | Number of days back to sync data for |
| `sync_types` | array | ❌ | `["campaigns", "ad_groups", "keywords", "performance"]` | Types of data to sync |

### Sync Types Available

- `campaigns` - Campaign information and settings
- `ad_groups` - Ad group details and configurations
- `keywords` - Keyword data and match types
- `performance` - Performance metrics and analytics

## 📊 Response Format

### Success Response (200)

```json
{
  "success": true,
  "message": "Client account sync completed successfully",
  "summary": {
    "client_customer_id": "4180736466",
    "account_name": "KSTAR BOOTCAMP",
    "start_date": "2025-08-12",
    "end_date": "2025-08-19",
    "sync_types": ["campaigns", "ad_groups", "keywords", "performance"],
    "campaigns_synced": 1,
    "ad_groups_synced": 1,
    "keywords_synced": 1,
    "performance_records_synced": 0,
    "errors": []
  }
}
```

### Error Response (400)

```json
{
  "success": false,
  "error": "Account 9999999999 not found or access denied"
}
```

## 🔧 Usage Examples

### 1. Sync All Data Types (Default)

```bash
curl -X POST http://localhost:8000/google-ads-new/api/sync-single-client/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_customer_id": "4180736466"
  }'
```

### 2. Sync Specific Data Types

```bash
curl -X POST http://localhost:8000/google-ads-new/api/sync-single-client/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_customer_id": "3048406696",
    "days_back": 3,
    "sync_types": ["campaigns", "ad_groups"]
  }'
```

### 3. Sync Only Performance Data

```bash
curl -X POST http://localhost:8000/google-ads-new/api/sync-single-client/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_customer_id": "4477009303",
    "days_back": 1,
    "sync_types": ["performance"]
  }'
```

### 4. Python Usage

```python
import requests

# Sync all data types
response = requests.post(
    "http://localhost:8000/google-ads-new/api/sync-single-client/",
    json={
        "client_customer_id": "4180736466",
        "days_back": 7,
        "sync_types": ["campaigns", "ad_groups", "keywords", "performance"]
    }
)

if response.status_code == 200:
    result = response.json()
    print(f"Sync completed: {result['summary']}")
else:
    print(f"Sync failed: {response.text}")
```

### 5. Direct Service Usage

```python
from google_ads_new.comprehensive_sync_service import ComprehensiveGoogleAdsSyncService

service = ComprehensiveGoogleAdsSyncService()
result = service.sync_single_client_account(
    client_customer_id="4180736466",
    days_back=7,
    sync_types=["campaigns", "ad_groups"]
)

if result['success']:
    print(f"Sync completed: {result['summary']}")
else:
    print(f"Sync failed: {result['error']}")
```

## 🎯 Use Cases

### 1. **Targeted Syncs**
- Sync only specific accounts that need updates
- Avoid syncing entire manager account when only one client needs data

### 2. **Selective Data Sync**
- Sync only campaigns and ad groups (no performance data)
- Sync only performance data for reporting
- Customize sync scope based on needs

### 3. **Incremental Updates**
- Sync last 1-3 days for daily updates
- Sync last 7-30 days for weekly/monthly reports

### 4. **Testing and Development**
- Test sync functionality with individual accounts
- Debug sync issues without affecting other accounts

## 🔍 Features

### **Account Validation**
- Verifies account exists and is accessible
- Returns descriptive error messages for access issues

### **Flexible Sync Types**
- Choose which data types to sync
- Mix and match based on requirements

### **Configurable Date Range**
- Customize how far back to sync data
- Optimize for different use cases

### **Error Handling**
- Continues sync even if some data types fail
- Provides detailed error reporting
- Logs all operations for debugging

### **Progress Tracking**
- Real-time sync progress updates
- Detailed summary of what was synced
- Error collection and reporting

## 📈 Performance Benefits

### **Faster Sync Times**
- Sync only what you need
- Avoid unnecessary data retrieval
- Reduced API calls to Google Ads

### **Resource Efficiency**
- Lower memory usage
- Reduced database load
- Faster response times

### **Scalability**
- Sync accounts in parallel
- Independent account processing
- Better resource utilization

## 🚨 Error Handling

### **Common Error Scenarios**

1. **Account Not Found**
   - Invalid customer ID
   - Account doesn't exist

2. **Access Denied**
   - Insufficient permissions
   - Account not linked to manager

3. **API Limits**
   - Rate limiting
   - Quota exceeded

4. **Data Issues**
   - Invalid data format
   - Missing required fields

### **Error Recovery**

- Partial sync completion
- Detailed error logging
- Graceful degradation
- Retry mechanisms

## 🔧 Testing

### **Test Script**

Run the included test script to verify functionality:

```bash
cd google_ads_new
python test_single_client_sync.py
```

### **Test Scenarios**

1. **Valid Account Sync**
   - Test with real account IDs
   - Verify data retrieval and storage

2. **Invalid Account**
   - Test with non-existent account
   - Verify error handling

3. **Partial Sync**
   - Test with limited sync types
   - Verify selective data retrieval

4. **Date Range Testing**
   - Test different day ranges
   - Verify date filtering

## 📚 Related APIs

- **Comprehensive Sync**: `/api/comprehensive-sync/` - Sync entire manager account
- **Account Access**: `/api/request-account-access/` - Request access to new accounts
- **Sync Status**: `/api/sync-status/` - Check sync status
- **Sync Logs**: `/api/sync-logs/` - View sync operation history

## 🎉 Summary

The Single Client Account Sync API provides a powerful, flexible way to sync individual Google Ads accounts with:

- **Selective data sync** - Choose what to sync
- **Configurable date ranges** - Customize time periods
- **Robust error handling** - Graceful failure management
- **Performance optimization** - Faster, more efficient syncs
- **Easy integration** - Simple REST API interface

This API is perfect for scenarios where you need to sync specific accounts or data types without the overhead of a full manager account sync.


This API endpoint allows you to sync individual Google Ads client accounts without having to sync the entire manager account.

## 🚀 API Endpoint

**URL:** `POST /google-ads-new/api/sync-single-client/`

**Authentication:** None required (CSRF exempt for testing)

## 📋 Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `client_customer_id` | string | ✅ | - | The Google Ads client account ID to sync |
| `days_back` | integer | ❌ | 7 | Number of days back to sync data for |
| `sync_types` | array | ❌ | `["campaigns", "ad_groups", "keywords", "performance"]` | Types of data to sync |

### Sync Types Available

- `campaigns` - Campaign information and settings
- `ad_groups` - Ad group details and configurations
- `keywords` - Keyword data and match types
- `performance` - Performance metrics and analytics

## 📊 Response Format

### Success Response (200)

```json
{
  "success": true,
  "message": "Client account sync completed successfully",
  "summary": {
    "client_customer_id": "4180736466",
    "account_name": "KSTAR BOOTCAMP",
    "start_date": "2025-08-12",
    "end_date": "2025-08-19",
    "sync_types": ["campaigns", "ad_groups", "keywords", "performance"],
    "campaigns_synced": 1,
    "ad_groups_synced": 1,
    "keywords_synced": 1,
    "performance_records_synced": 0,
    "errors": []
  }
}
```

### Error Response (400)

```json
{
  "success": false,
  "error": "Account 9999999999 not found or access denied"
}
```

## 🔧 Usage Examples

### 1. Sync All Data Types (Default)

```bash
curl -X POST http://localhost:8000/google-ads-new/api/sync-single-client/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_customer_id": "4180736466"
  }'
```

### 2. Sync Specific Data Types

```bash
curl -X POST http://localhost:8000/google-ads-new/api/sync-single-client/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_customer_id": "3048406696",
    "days_back": 3,
    "sync_types": ["campaigns", "ad_groups"]
  }'
```

### 3. Sync Only Performance Data

```bash
curl -X POST http://localhost:8000/google-ads-new/api/sync-single-client/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_customer_id": "4477009303",
    "days_back": 1,
    "sync_types": ["performance"]
  }'
```

### 4. Python Usage

```python
import requests

# Sync all data types
response = requests.post(
    "http://localhost:8000/google-ads-new/api/sync-single-client/",
    json={
        "client_customer_id": "4180736466",
        "days_back": 7,
        "sync_types": ["campaigns", "ad_groups", "keywords", "performance"]
    }
)

if response.status_code == 200:
    result = response.json()
    print(f"Sync completed: {result['summary']}")
else:
    print(f"Sync failed: {response.text}")
```

### 5. Direct Service Usage

```python
from google_ads_new.comprehensive_sync_service import ComprehensiveGoogleAdsSyncService

service = ComprehensiveGoogleAdsSyncService()
result = service.sync_single_client_account(
    client_customer_id="4180736466",
    days_back=7,
    sync_types=["campaigns", "ad_groups"]
)

if result['success']:
    print(f"Sync completed: {result['summary']}")
else:
    print(f"Sync failed: {result['error']}")
```

## 🎯 Use Cases

### 1. **Targeted Syncs**
- Sync only specific accounts that need updates
- Avoid syncing entire manager account when only one client needs data

### 2. **Selective Data Sync**
- Sync only campaigns and ad groups (no performance data)
- Sync only performance data for reporting
- Customize sync scope based on needs

### 3. **Incremental Updates**
- Sync last 1-3 days for daily updates
- Sync last 7-30 days for weekly/monthly reports

### 4. **Testing and Development**
- Test sync functionality with individual accounts
- Debug sync issues without affecting other accounts

## 🔍 Features

### **Account Validation**
- Verifies account exists and is accessible
- Returns descriptive error messages for access issues

### **Flexible Sync Types**
- Choose which data types to sync
- Mix and match based on requirements

### **Configurable Date Range**
- Customize how far back to sync data
- Optimize for different use cases

### **Error Handling**
- Continues sync even if some data types fail
- Provides detailed error reporting
- Logs all operations for debugging

### **Progress Tracking**
- Real-time sync progress updates
- Detailed summary of what was synced
- Error collection and reporting

## 📈 Performance Benefits

### **Faster Sync Times**
- Sync only what you need
- Avoid unnecessary data retrieval
- Reduced API calls to Google Ads

### **Resource Efficiency**
- Lower memory usage
- Reduced database load
- Faster response times

### **Scalability**
- Sync accounts in parallel
- Independent account processing
- Better resource utilization

## 🚨 Error Handling

### **Common Error Scenarios**

1. **Account Not Found**
   - Invalid customer ID
   - Account doesn't exist

2. **Access Denied**
   - Insufficient permissions
   - Account not linked to manager

3. **API Limits**
   - Rate limiting
   - Quota exceeded

4. **Data Issues**
   - Invalid data format
   - Missing required fields

### **Error Recovery**

- Partial sync completion
- Detailed error logging
- Graceful degradation
- Retry mechanisms

## 🔧 Testing

### **Test Script**

Run the included test script to verify functionality:

```bash
cd google_ads_new
python test_single_client_sync.py
```

### **Test Scenarios**

1. **Valid Account Sync**
   - Test with real account IDs
   - Verify data retrieval and storage

2. **Invalid Account**
   - Test with non-existent account
   - Verify error handling

3. **Partial Sync**
   - Test with limited sync types
   - Verify selective data retrieval

4. **Date Range Testing**
   - Test different day ranges
   - Verify date filtering

## 📚 Related APIs

- **Comprehensive Sync**: `/api/comprehensive-sync/` - Sync entire manager account
- **Account Access**: `/api/request-account-access/` - Request access to new accounts
- **Sync Status**: `/api/sync-status/` - Check sync status
- **Sync Logs**: `/api/sync-logs/` - View sync operation history

## 🎉 Summary

The Single Client Account Sync API provides a powerful, flexible way to sync individual Google Ads accounts with:

- **Selective data sync** - Choose what to sync
- **Configurable date ranges** - Customize time periods
- **Robust error handling** - Graceful failure management
- **Performance optimization** - Faster, more efficient syncs
- **Easy integration** - Simple REST API interface

This API is perfect for scenarios where you need to sync specific accounts or data types without the overhead of a full manager account sync.


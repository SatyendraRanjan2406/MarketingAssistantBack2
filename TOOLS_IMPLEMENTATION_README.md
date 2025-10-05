# Marketing Tools Implementation

## Overview

The `tools.py` file provides a unified API for managing campaigns across Google Ads and Meta Marketing platforms. It implements the `GET_CAMPAIGNS` function with full support for both providers.

## Features

### ✅ Implemented
- **GET_CAMPAIGNS** function with full TypeScript signature compliance
- **Google Ads API** integration with GAQL queries
- **Meta Marketing API** integration with Graph API
- **Unified response format** across both platforms
- **Comprehensive parameter support**:
  - `provider`: 'google' | 'meta'
  - `accountId`: Customer ID or Ad Account ID
  - `fields`: Custom field selection
  - `status`: Campaign status filtering
  - `dateRange`: Date range for metrics
  - `includeMetrics`: Boolean flag for metrics
  - `metrics`: Specific metrics to retrieve
  - `limit`: Result limit
  - `cursor`: Pagination cursor
  - `filters`: Custom filters

### 🔧 Technical Implementation

#### Google Ads Integration
- **GAQL Query Building**: Dynamic query construction with proper field mapping
- **OAuth Authentication**: Integrated with existing UserGoogleAuth system
- **Field Mapping**: Automatic mapping of common field names to GAQL fields
- **Metrics Support**: Full support for impressions, clicks, cost, conversions, etc.
- **Status Filtering**: Proper status filtering with IN clauses
- **Date Range**: Support for date-based metrics filtering

#### Meta Marketing Integration
- **Graph API**: Uses Facebook Graph API v18.0
- **Field Selection**: Dynamic field selection for campaigns
- **Insights Edge**: Automatic insights retrieval for metrics
- **Status Mapping**: Google Ads to Meta status mapping
- **Pagination**: Full cursor-based pagination support

#### Error Handling
- **Graceful Degradation**: Returns empty results with error messages
- **Comprehensive Logging**: Detailed error logging for debugging
- **Async Context**: Proper async/await handling for Django ORM

## Usage Examples

### Basic Campaign Retrieval
```python
from tools import MarketingTools

tools = MarketingTools()

# Get Google Ads campaigns
result = await tools.GET_CAMPAIGNS({
    "provider": "google",
    "accountId": "9631603999",
    "fields": ["campaign.id", "campaign.name", "campaign.status"],
    "status": ["ENABLED"],
    "limit": 10
})
```

### With Metrics
```python
# Get campaigns with performance metrics
result = await tools.GET_CAMPAIGNS({
    "provider": "google",
    "accountId": "9631603999",
    "fields": ["campaign.id", "campaign.name", "campaign.status"],
    "includeMetrics": True,
    "metrics": ["impressions", "clicks", "cost", "conversions"],
    "dateRange": {"from": "2025-01-01", "to": "2025-01-31"},
    "limit": 50
})
```

### Meta Marketing
```python
# Get Meta campaigns
result = await tools.GET_CAMPAIGNS({
    "provider": "meta",
    "accountId": "123456789",
    "fields": ["id", "name", "status", "start_time"],
    "status": ["ACTIVE"],
    "includeMetrics": True,
    "metrics": ["impressions", "clicks", "spend"],
    "limit": 25
})
```

## Response Format

### Success Response
```json
{
  "campaigns": [
    {
      "id": "123",
      "name": "Search - Brand",
      "status": "ENABLED",
      "startDate": "2025-07-01",
      "endDate": null,
      "impressions": 1000,
      "clicks": 50,
      "cost": 25.50,
      "conversions": 5
    }
  ],
  "nextCursor": null
}
```

### Error Response
```json
{
  "campaigns": [],
  "nextCursor": null,
  "error": "Error message describing what went wrong"
}
```

## Field Mapping

### Google Ads Fields
- `campaign.id` → Campaign ID
- `campaign.name` → Campaign Name
- `campaign.status` → Campaign Status
- `campaign.start_date` → Start Date
- `campaign.end_date` → End Date
- `campaign.advertising_channel_type` → Channel Type

### Meta Fields
- `id` → Campaign ID
- `name` → Campaign Name
- `status` → Campaign Status
- `start_time` → Start Time
- `stop_time` → Stop Time
- `created_time` → Created Time
- `updated_time` → Updated Time

## Metrics Support

### Google Ads Metrics
- `impressions` → metrics.impressions
- `clicks` → metrics.clicks
- `cost` → metrics.cost_micros (converted to dollars)
- `conversions` → metrics.conversions
- `ctr` → metrics.ctr
- `cpc` → metrics.average_cpc
- `cpm` → metrics.average_cpm
- `cpa` → metrics.average_cpa

### Meta Metrics
- `impressions` → insights.impressions
- `clicks` → insights.clicks
- `cost` → insights.spend
- `conversions` → insights.conversions
- `ctr` → insights.ctr
- `cpc` → insights.cpc
- `cpm` → insights.cpm
- `cpa` → insights.cpa

## Status Mapping

### Google Ads → Meta
- `ENABLED` → `ACTIVE`
- `PAUSED` → `PAUSED`
- `REMOVED` → `DELETED`

## Configuration Requirements

### Google Ads
- `GOOGLE_ADS_DEVELOPER_TOKEN`
- `GOOGLE_ADS_CLIENT_ID`
- `GOOGLE_ADS_CLIENT_SECRET`
- User refresh token in database

### Meta Marketing
- `META_ACCESS_TOKEN`

## Error Handling

The implementation includes comprehensive error handling:

1. **Authentication Errors**: Graceful handling of missing OAuth tokens
2. **API Errors**: Proper error propagation with detailed messages
3. **Query Errors**: GAQL syntax error handling
4. **Network Errors**: Request timeout and connection error handling
5. **Data Errors**: Malformed response handling

## Testing

The implementation includes a test function that can be run with:

```bash
python tools.py
```

This will test both Google Ads and Meta Marketing integrations (requires proper configuration).

## Future Enhancements

### Planned Features
- [ ] **GET_ADS** function implementation
- [ ] **GET_ADSETS** function implementation
- [ ] **CREATE_CAMPAIGN** function implementation
- [ ] **UPDATE_CAMPAIGN** function implementation
- [ ] **DELETE_CAMPAIGN** function implementation
- [ ] **Bulk operations** support
- [ ] **Rate limiting** and retry logic
- [ ] **Caching** for frequently accessed data
- [ ] **Webhook support** for real-time updates

### Technical Improvements
- [ ] **Connection pooling** for better performance
- [ ] **Async batching** for multiple requests
- [ ] **Response validation** with Pydantic models
- [ ] **Comprehensive logging** with structured logs
- [ ] **Metrics collection** for monitoring
- [ ] **Health checks** for API availability

## Dependencies

- `google-ads` - Google Ads API client
- `requests` - HTTP client for Meta API
- `asgiref` - Async support for Django
- `django` - Web framework
- `typing` - Type hints support

## License

This implementation is part of the Marketing Assistant Backend project.

# Google Ads Search Tool Implementation

## Overview

The `GOOGLE_ADS_SEARCH` tool provides direct access to the Google Ads REST API search endpoint, allowing you to execute GAQL (Google Ads Query Language) queries directly against the Google Ads API.

## Features

### ✅ Implemented
- **Direct REST API Access**: Uses Google Ads REST API v21
- **GAQL Query Support**: Execute any valid GAQL query
- **OAuth Authentication**: Bearer token authentication
- **Login Customer ID**: Support for manager account access
- **Result Formatting**: Automatic formatting of API responses
- **Error Handling**: Comprehensive error handling and logging
- **Pagination Support**: Next page token handling

## API Endpoint

```
POST https://googleads.googleapis.com/v21/customers/{customer_id}/googleAds:search
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `customer_id` | string | ✅ | Google Ads customer ID |
| `query` | string | ✅ | GAQL query string |
| `access_token` | string | ✅ | OAuth 2.0 access token |
| `login_customer_id` | string | ❌ | Login customer ID (uses env variable if not provided) |

## Environment Variables

Add these to your `.env` file:

```env
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=9762343117
```

## Usage Examples

### Basic Campaign Search
```python
from tools import MarketingTools

tools = MarketingTools()

# Search for campaigns with metrics
result = await tools.GOOGLE_ADS_SEARCH({
    "customer_id": "3048406696",
    "query": "SELECT campaign.id, campaign.name, campaign.status, metrics.impressions, metrics.clicks, metrics.ctr, metrics.conversions, metrics.cost_micros FROM campaign WHERE segments.date DURING LAST_30_DAYS ORDER BY metrics.impressions DESC",
    "access_token": "ya29.a0AQQ_BDTrAhNSuriWeucHovdKS17oUvrHOIYGm-8dYet6-eNTcdR9hn8yDv_YLncPEfuOcA8Fe0j2FaGdHRt2XYIUdsEVYrxwg2-0-6BwuH0E7FQhMQXPBRQ2gveX4wsgUmuejqLmlJ4eLYclWl1pW-m1BnmXv5sAAgDk3xq49H-uRgGQaw_bsYb3jqfa0Vt5HdrSwMIaCgYKAVQSARISFQHGX2MiY4AbxEZNXKASvwEJx6MUeg0206"
})
```

### Ad Group Search
```python
# Search for ad groups with performance data
result = await tools.GOOGLE_ADS_SEARCH({
    "customer_id": "3048406696",
    "query": "SELECT ad_group.id, ad_group.name, ad_group.status, metrics.impressions, metrics.clicks, metrics.cost_micros FROM ad_group WHERE segments.date DURING LAST_7_DAYS",
    "access_token": "your_access_token"
})
```

### Keyword Search
```python
# Search for keywords with performance data
result = await tools.GOOGLE_ADS_SEARCH({
    "customer_id": "3048406696",
    "query": "SELECT keyword_view.resource_name, keyword_view.keyword_text, keyword_view.match_type, metrics.impressions, metrics.clicks, metrics.ctr FROM keyword_view WHERE segments.date DURING LAST_14_DAYS",
    "access_token": "your_access_token"
})
```

## Response Format

### Success Response
```json
{
  "results": [
    {
      "campaign_id": "123456789",
      "campaign_name": "Search Campaign - Brand",
      "campaign_status": "ENABLED",
      "advertising_channel_type": "SEARCH",
      "start_date": "2024-01-01",
      "end_date": null,
      "impressions": 10000,
      "clicks": 500,
      "ctr": 0.05,
      "conversions": 25,
      "cost_micros": 5000000,
      "cost": 5.0,
      "average_cpc": 0.01,
      "average_cpm": 0.5,
      "conversion_rate": 0.05
    }
  ],
  "total_results": 1,
  "next_page_token": null,
  "success": true
}
```

### Error Response
```json
{
  "results": [],
  "total_results": 0,
  "next_page_token": null,
  "success": false,
  "error": "API request failed: 401 Unauthorized"
}
```

## Supported GAQL Queries

### Campaign Queries
```sql
-- Basic campaign info
SELECT campaign.id, campaign.name, campaign.status FROM campaign

-- Campaigns with metrics
SELECT campaign.id, campaign.name, metrics.impressions, metrics.clicks, metrics.cost_micros 
FROM campaign 
WHERE segments.date DURING LAST_30_DAYS

-- Campaigns by status
SELECT campaign.id, campaign.name, campaign.status 
FROM campaign 
WHERE campaign.status = 'ENABLED'
```

### Ad Group Queries
```sql
-- Ad groups with performance
SELECT ad_group.id, ad_group.name, ad_group.status, metrics.impressions, metrics.clicks 
FROM ad_group 
WHERE segments.date DURING LAST_7_DAYS

-- Ad groups by campaign
SELECT ad_group.id, ad_group.name, campaign.id 
FROM ad_group 
WHERE campaign.id = 123456789
```

### Keyword Queries
```sql
-- Keywords with performance
SELECT keyword_view.resource_name, keyword_view.keyword_text, keyword_view.match_type, metrics.impressions, metrics.clicks 
FROM keyword_view 
WHERE segments.date DURING LAST_14_DAYS

-- Keywords by match type
SELECT keyword_view.resource_name, keyword_view.keyword_text, keyword_view.match_type 
FROM keyword_view 
WHERE keyword_view.match_type = 'EXACT'
```

### Ad Queries
```sql
-- Ads with performance
SELECT ad_group_ad.ad.id, ad_group_ad.ad.name, ad_group_ad.status, metrics.impressions, metrics.clicks 
FROM ad_group_ad 
WHERE segments.date DURING LAST_7_DAYS
```

## Result Formatting

The tool automatically formats Google Ads API responses into a more consumable format:

### Campaign Data
- `campaign_id`: Campaign ID
- `campaign_name`: Campaign name
- `campaign_status`: Campaign status (ENABLED, PAUSED, etc.)
- `advertising_channel_type`: Channel type (SEARCH, DISPLAY, etc.)
- `start_date`: Campaign start date
- `end_date`: Campaign end date

### Metrics Data
- `impressions`: Number of impressions
- `clicks`: Number of clicks
- `ctr`: Click-through rate
- `conversions`: Number of conversions
- `cost_micros`: Cost in micros
- `cost`: Cost in dollars (converted from micros)
- `average_cpc`: Average cost per click
- `average_cpm`: Average cost per mille
- `conversion_rate`: Conversion rate (conversions/clicks)

### Segments Data
- `date`: Date of the data
- `device`: Device type (MOBILE, DESKTOP, etc.)
- `network`: Network type (SEARCH, DISPLAY, etc.)
- `ad_network_type`: Ad network type

### Ad Group Data
- `ad_group_id`: Ad group ID
- `ad_group_name`: Ad group name
- `ad_group_status`: Ad group status

### Keyword Data
- `keyword_id`: Keyword resource name
- `keyword_text`: Keyword text
- `keyword_match_type`: Match type (EXACT, PHRASE, BROAD)

## Error Handling

The tool includes comprehensive error handling:

1. **Parameter Validation**: Checks for required parameters
2. **API Errors**: Handles HTTP errors from Google Ads API
3. **Authentication Errors**: Handles OAuth token issues
4. **Network Errors**: Handles connection timeouts and network issues
5. **Data Errors**: Handles malformed responses

## Authentication

The tool requires:
1. **OAuth 2.0 Access Token**: Valid Bearer token
2. **Developer Token**: Set in environment variables
3. **Login Customer ID**: Set in environment variables

## Rate Limiting

Google Ads API has rate limits:
- **Queries per day**: Varies by account
- **Queries per minute**: 10,000 for most accounts
- **Concurrent requests**: 10 for most accounts

## Testing

Run the test function to verify the implementation:

```bash
python tools.py
```

This will test both the GET_CAMPAIGNS and GOOGLE_ADS_SEARCH tools.

## Integration with Existing System

The tool can be integrated with the existing LLM orchestrator:

```python
# In your LLM orchestrator
async def _execute_tools(self, tool_calls, user_id, customer_id=None, conversation_context=None):
    for tool_call in tool_calls:
        if tool_call['name'] == 'google_ads_search':
            # Get access token
            access_token = await sync_to_async(UserGoogleAuthService.get_or_refresh_valid_token)(user)
            
            # Execute search
            result = await self.tools.GOOGLE_ADS_SEARCH({
                'customer_id': customer_id,
                'query': tool_call['arguments']['query'],
                'access_token': access_token
            })
            
            results[tool_call['id']] = result
```

## Security Considerations

1. **Token Security**: Access tokens should be stored securely
2. **Environment Variables**: Keep sensitive data in environment variables
3. **HTTPS Only**: Always use HTTPS for API calls
4. **Token Refresh**: Implement token refresh logic for long-running applications

## Troubleshooting

### Common Issues

1. **401 Unauthorized**: Check access token validity
2. **403 Forbidden**: Check developer token and permissions
3. **400 Bad Request**: Check GAQL query syntax
4. **429 Too Many Requests**: Implement rate limiting

### Debug Mode

Enable debug logging to see detailed request/response information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- [ ] **Query Builder**: Helper functions for common queries
- [ ] **Caching**: Result caching for frequently accessed data
- [ ] **Batch Operations**: Support for multiple queries
- [ ] **Real-time Updates**: Webhook support for data changes
- [ ] **Query Validation**: GAQL syntax validation before execution

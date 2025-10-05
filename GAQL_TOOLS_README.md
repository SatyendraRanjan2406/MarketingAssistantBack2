# Google Ads GAQL Tools Implementation

## 📋 Overview

This document describes the comprehensive Google Ads tools implementation using GAQL (Google Ads Query Language) queries. All tools are built as LangChain tools and can be used directly in your applications.

## 🛠️ Available Tools

### 1. **Campaign Operations**

#### `get_campaigns`
- **Description**: Get all campaigns for a customer
- **Parameters**: 
  - `customer_id` (required): Google Ads customer ID
  - `access_token` (required): OAuth2 access token
  - `status_filter` (optional): Campaign status filter (ALL, ENABLED, PAUSED, REMOVED)
- **Returns**: Campaign data with metrics (impressions, clicks, CTR, conversions, cost, etc.)

#### `get_campaign_by_id`
- **Description**: Get specific campaign by ID
- **Parameters**:
  - `customer_id` (required): Google Ads customer ID
  - `access_token` (required): OAuth2 access token
  - `campaign_id` (required): Campaign ID to retrieve
- **Returns**: Detailed campaign information with performance metrics

### 2. **Ad Group Operations**

#### `get_ad_groups`
- **Description**: Get all ad groups for a customer or specific campaign
- **Parameters**:
  - `customer_id` (required): Google Ads customer ID
  - `access_token` (required): OAuth2 access token
  - `campaign_id` (optional): Campaign ID to filter ad groups
- **Returns**: Ad group data with metrics and bidding information

### 3. **Ad Operations**

#### `get_ads`
- **Description**: Get all ads for a customer or specific ad group
- **Parameters**:
  - `customer_id` (required): Google Ads customer ID
  - `access_token` (required): OAuth2 access token
  - `ad_group_id` (optional): Ad group ID to filter ads
- **Returns**: Ad data including headlines, descriptions, URLs, and performance metrics

### 4. **Keyword Operations**

#### `get_keywords`
- **Description**: Get all keywords for a customer or specific ad group
- **Parameters**:
  - `customer_id` (required): Google Ads customer ID
  - `access_token` (required): OAuth2 access token
  - `ad_group_id` (optional): Ad group ID to filter keywords
- **Returns**: Keyword data with quality scores, bid information, and performance metrics

### 5. **Performance Operations**

#### `get_performance_data`
- **Description**: Get performance data for campaigns, ad groups, or overall account
- **Parameters**:
  - `customer_id` (required): Google Ads customer ID
  - `access_token` (required): OAuth2 access token
  - `date_range` (optional): Date range (LAST_7_DAYS, LAST_30_DAYS, LAST_90_DAYS, etc.)
  - `campaign_id` (optional): Campaign ID to filter
  - `ad_group_id` (optional): Ad group ID to filter
- **Returns**: Comprehensive performance metrics with segmentation

### 6. **Budget Operations**

#### `get_budgets`
- **Description**: Get all budgets for a customer
- **Parameters**:
  - `customer_id` (required): Google Ads customer ID
  - `access_token` (required): OAuth2 access token
- **Returns**: Budget information with usage and recommendations

### 7. **Account Operations**

#### `get_account_overview`
- **Description**: Get account overview with key metrics and information
- **Parameters**:
  - `customer_id` (required): Google Ads customer ID
  - `access_token` (required): OAuth2 access token
- **Returns**: Customer information and aggregated performance metrics

### 8. **Search Term Operations**

#### `get_search_terms`
- **Description**: Get search terms that triggered ads
- **Parameters**:
  - `customer_id` (required): Google Ads customer ID
  - `access_token` (required): OAuth2 access token
  - `campaign_id` (optional): Campaign ID to filter
  - `ad_group_id` (optional): Ad group ID to filter
- **Returns**: Search term data with performance metrics

### 9. **Demographic Operations**

#### `get_demographic_data`
- **Description**: Get demographic performance data
- **Parameters**:
  - `customer_id` (required): Google Ads customer ID
  - `access_token` (required): OAuth2 access token
  - `campaign_id` (optional): Campaign ID to filter
- **Returns**: Demographic breakdown with performance metrics

### 10. **Geographic Operations**

#### `get_geographic_data`
- **Description**: Get geographic performance data
- **Parameters**:
  - `customer_id` (required): Google Ads customer ID
  - `access_token` (required): OAuth2 access token
  - `campaign_id` (optional): Campaign ID to filter
- **Returns**: Geographic breakdown with performance metrics

## 🔧 Implementation Details

### GAQL Query Examples

#### Campaign Query
```sql
SELECT 
    campaign.id, 
    campaign.name, 
    campaign.status, 
    campaign.advertising_channel_type,
    metrics.impressions, 
    metrics.clicks, 
    metrics.ctr, 
    metrics.conversions, 
    metrics.cost_micros
FROM campaign 
WHERE segments.date DURING LAST_30_DAYS
ORDER BY metrics.impressions DESC
```

#### Performance Query
```sql
SELECT 
    segments.date,
    segments.device,
    metrics.impressions,
    metrics.clicks,
    metrics.ctr,
    metrics.conversions,
    metrics.cost_micros
FROM campaign 
WHERE segments.date DURING LAST_30_DAYS
ORDER BY segments.date DESC
```

### API Integration

All tools use the Google Ads API v21 with the following configuration:
- **Base URL**: `https://googleads.googleapis.com/v21`
- **Authentication**: OAuth2 Bearer tokens
- **Developer Token**: From environment variable `GOOGLE_ADS_DEVELOPER_TOKEN`
- **Login Customer ID**: From environment variable `GOOGLE_ADS_LOGIN_CUSTOMER_ID`

### Error Handling

Each tool includes comprehensive error handling:
- API connection errors
- Invalid parameters
- Quota exceeded errors
- Authentication failures
- Malformed queries

## 📊 Usage Examples

### Basic Usage
```python
from ad_expert.tools import get_campaigns, get_performance_data

# Get all campaigns
campaigns = get_campaigns.invoke({
    "customer_id": "9631603999",
    "access_token": "your_access_token"
})

# Get performance data
performance = get_performance_data.invoke({
    "customer_id": "9631603999",
    "access_token": "your_access_token",
    "date_range": "LAST_7_DAYS"
})
```

### LangChain Integration
```python
from ad_expert.tools import ALL_TOOLS
from langchain.llms import OpenAI

# Bind tools to LLM
llm_with_tools = llm.bind_tools(ALL_TOOLS)

# Use in conversation
response = llm_with_tools.invoke([
    HumanMessage("Show me my campaign performance")
])
```

## 🔑 Environment Variables

Required environment variables:
```bash
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=9762343117
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
```

## 📈 Metrics Available

All tools return comprehensive metrics including:
- **Impressions**: Number of times ads were shown
- **Clicks**: Number of clicks on ads
- **CTR**: Click-through rate (clicks/impressions)
- **Conversions**: Number of conversions
- **Cost**: Total cost in micros
- **Average CPC**: Average cost per click
- **Conversion Rate**: Conversions/clicks
- **Cost Per Conversion**: Cost/conversions
- **Quality Scores**: For keywords and ads
- **Impression Share**: Share of available impressions

## 🚀 Integration with MCP

These tools are fully integrated with the MCP (Model Context Protocol) server and can be used in the RAGChat2View for comprehensive Google Ads data retrieval and analysis.

## 📝 Notes

- All monetary values are returned in micros (divide by 1,000,000 for actual currency)
- Date ranges use Google Ads API date format (LAST_30_DAYS, etc.)
- Customer IDs should be in format "9631603999" (without "customers/" prefix)
- All tools support filtering by campaign_id and ad_group_id where applicable
- Performance data can be segmented by device, network type, and date

## 🔄 Updates

This implementation supports Google Ads API v21 and includes all major operations for comprehensive Google Ads management and analysis.

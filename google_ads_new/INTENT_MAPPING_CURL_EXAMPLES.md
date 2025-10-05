# 🎯 Intent Mapping API - cURL Examples

Complete cURL examples for testing the Intent Mapping API endpoints.

## 🔑 Authentication

Most endpoints require JWT authentication. Get your token from the login API:

```bash
# Get JWT token
curl -X POST 'http://localhost:8000/accounts/api/auth/login/' \
  -H 'Content-Type: application/json' \
  -d '{"email": "your@email.com", "password": "your_password"}'
```

## 📋 API Endpoints

### 1. Map Query to Intents (Main Endpoint)

#### Basic Query Mapping
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "Show me all campaigns"
  }'
```

#### Query with User Context
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "Show me active campaigns from last 7 days with budget > $100",
    "user_context": {
      "customer_id": "1234567890",
      "campaigns": ["campaign1", "campaign2"],
      "account_type": "premium"
    }
  }'
```

#### Campaign by ID Query
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "Get campaign 12345 details from last 30 days"
  }'
```

#### Ad Group Query
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "Show me ad groups for campaign 67890 from last week"
  }'
```

#### Budget Query
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "Get budget information for campaigns with budget > $500"
  }'
```

#### Analysis Query
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "Compare performance of active campaigns from this month"
  }'
```

#### Creative Query
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "Generate ad copies for summer campaign"
  }'
```

#### Optimization Query
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "Optimize campaign 12345 performance"
  }'
```

### 2. Get Available Actions

#### All Actions
```bash
curl -X GET 'http://localhost:8000/google-ads-new/api/intent-mapping/actions/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'
```

#### Actions by Category
```bash
# Basic operations
curl -X GET 'http://localhost:8000/google-ads-new/api/intent-mapping/actions/basic_operations/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'

# Analysis actions
curl -X GET 'http://localhost:8000/google-ads-new/api/intent-mapping/actions/analysis/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'

# Creative actions
curl -X GET 'http://localhost:8000/google-ads-new/api/intent-mapping/actions/creative/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'

# Optimization actions
curl -X GET 'http://localhost:8000/google-ads-new/api/intent-mapping/actions/optimization/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'

# Technical actions
curl -X GET 'http://localhost:8000/google-ads-new/api/intent-mapping/actions/technical/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'

# Performance actions
curl -X GET 'http://localhost:8000/google-ads-new/api/intent-mapping/actions/performance/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'

# Keywords actions
curl -X GET 'http://localhost:8000/google-ads-new/api/intent-mapping/actions/keywords/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'

# Competitive actions
curl -X GET 'http://localhost:8000/google-ads-new/api/intent-mapping/actions/competitive/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'

# Knowledge base actions
curl -X GET 'http://localhost:8000/google-ads-new/api/intent-mapping/actions/knowledge_base/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'

# Analytics actions
curl -X GET 'http://localhost:8000/google-ads-new/api/intent-mapping/actions/analytics/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'

# Fallback actions
curl -X GET 'http://localhost:8000/google-ads-new/api/intent-mapping/actions/fallback/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'
```

#### Action Details
```bash
# Get specific action details
curl -X GET 'http://localhost:8000/google-ads-new/api/intent-mapping/actions/details/GET_CAMPAIGNS/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'

curl -X GET 'http://localhost:8000/google-ads-new/api/intent-mapping/actions/details/GET_CAMPAIGN_BY_ID/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'

curl -X GET 'http://localhost:8000/google-ads-new/api/intent-mapping/actions/details/ANALYZE_AUDIENCE/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'
```

### 3. Date Range Extraction

#### Extract Date Ranges
```bash
# Last 7 days
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/extract-date-range/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Show me data from last 7 days"}'

# This month
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/extract-date-range/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Get campaigns from this month"}'

# Yesterday
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/extract-date-range/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Show me performance from yesterday"}'

# Last 30 days
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/extract-date-range/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Get data from last 30 days"}'

# Today
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/extract-date-range/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Show me results from today"}'
```

### 4. Test Endpoint (No Authentication Required)

#### Test Basic Query
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/test/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Show me campaigns"}'
```

#### Test Complex Query
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/test/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Show me active campaigns from last 7 days with budget > $100"}'
```

#### Test Ad Group Query
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/test/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Get ad groups for campaign 12345"}'
```

#### Test Analysis Query
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/test/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Compare campaign performance and show trends"}'
```

#### Test Creative Query
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/test/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Generate ad copies for holiday campaign"}'
```

## 🧪 Test Script Examples

### Run the Test Script
```bash
python google_ads_new/test_intent_mapping.py
```

### Manual Testing with Variables
```bash
# Set your JWT token
export JWT_TOKEN="your_jwt_token_here"

# Test basic mapping
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/' \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"query": "Show me active campaigns from last 7 days"}'

# Test without auth
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/test/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Get campaign 12345 details"}'
```

## 📊 Expected Response Format

### Successful Response
```json
{
  "success": true,
  "actions": ["GET_CAMPAIGNS_WITH_FILTERS"],
  "date_range": {
    "start_date": "2024-01-08",
    "end_date": "2024-01-15",
    "period": "last_7_days"
  },
  "filters": [
    {
      "field": "status",
      "operator": "equals",
      "value": "ACTIVE",
      "description": "Campaigns with active status"
    },
    {
      "field": "budget",
      "operator": "greater_than",
      "value": 100,
      "description": "Campaigns with budget greater than $100"
    }
  ],
  "confidence": 0.95,
  "reasoning": "Query matches campaign filtering request with date range and budget filter",
  "parameters": {
    "limit": 50,
    "sort_by": "clicks",
    "order": "desc"
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": "Query is required"
}
```

## 🔍 Query Examples by Category

### Campaign Queries
```bash
# Get all campaigns
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/test/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Show me all campaigns"}'

# Get specific campaign
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/test/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Get campaign 12345 details"}'

# Filtered campaigns
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/test/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Show me active campaigns with budget > $500"}'
```

### Ad Queries
```bash
# Get all ads
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/test/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Show me all ads"}'

# Get ads for campaign
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/test/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Get ads for campaign 12345"}'

# Get specific ad
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/test/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Get ad 67890 details"}'
```

### Ad Group Queries
```bash
# Get all ad groups
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/test/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Show me all ad groups"}'

# Get ad groups for campaign
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/test/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Get ad groups for campaign 12345"}'

# Get specific ad group
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/test/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Get ad group 67890 details"}'
```

### Budget Queries
```bash
# Get all budgets
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/test/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Show me all budgets"}'

# Get budget for campaign
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/test/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Get budget for campaign 12345"}'

# Get specific budget
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/test/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Get budget 67890 details"}'
```

### Analysis Queries
```bash
# Performance summary
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/test/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Show me performance summary"}'

# Trend analysis
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/test/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Show me trend analysis for clicks"}'

# Compare campaigns
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/test/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Compare campaign performance"}'
```

### Creative Queries
```bash
# Generate ad copies
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/test/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Generate ad copies for summer campaign"}'

# Generate creatives
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/test/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Generate creative ideas for Facebook ads"}'

# Generate images
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/test/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Generate images for holiday promotion"}'
```

### Optimization Queries
```bash
# Optimize campaign
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/test/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Optimize campaign 12345"}'

# Optimize budget
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/test/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Optimize budget allocation"}'

# Optimize ad group
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/test/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Optimize ad group performance"}'
```

## 🚀 Quick Start

1. **Start the server:**
   ```bash
   python manage.py runserver 8000
   ```

2. **Test without authentication:**
   ```bash
   curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/test/' \
     -H 'Content-Type: application/json' \
     -d '{"query": "Show me campaigns"}'
   ```

3. **Get JWT token and test with authentication:**
   ```bash
   # Get token
   JWT_TOKEN=$(curl -s -X POST 'http://localhost:8000/accounts/api/auth/login/' \
     -H 'Content-Type: application/json' \
     -d '{"email": "your@email.com", "password": "your_password"}' | jq -r '.access')
   
   # Test with token
   curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/' \
     -H "Authorization: Bearer $JWT_TOKEN" \
     -H 'Content-Type: application/json' \
     -d '{"query": "Show me active campaigns from last 7 days"}'
   ```

## 📝 Notes

- Replace `YOUR_JWT_TOKEN` with your actual JWT token
- The test endpoint (`/test/`) doesn't require authentication
- All other endpoints require JWT authentication
- Responses include confidence scores and reasoning
- Date ranges are automatically extracted from natural language
- Filters are parsed from query conditions
- The system supports 70+ different intent actions


# 🎯 Intent Mapping API - Multiple Date Ranges & Filters (Array Format)

Updated cURL examples for the Intent Mapping API that now supports multiple date ranges and filters as arrays.

## 🔑 Get JWT Token First
```bash
curl -X POST 'http://localhost:8000/accounts/api/auth/login/' \
  -H 'Content-Type: application/json' \
  -d '{"email":"a@a.com","password":"a"}'
```

## 📋 Updated Response Format

The API now returns `date_ranges` and `filters` as arrays to handle multiple values:

```json
{
  "success": true,
  "actions": ["ACTION1", "ACTION2"],
  "date_ranges": [
    {
      "start_date": "2024-01-01",
      "end_date": "2024-01-31",
      "period": "this_month",
      "description": "This month data"
    },
    {
      "start_date": "2023-12-01",
      "end_date": "2023-12-31",
      "period": "last_month",
      "description": "Last month data"
    }
  ],
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
  "reasoning": "Query matches campaign analysis request with multiple date ranges and filters",
  "parameters": {
    "limit": 50,
    "sort_by": "clicks",
    "order": "desc"
  }
}
```

## 🧪 Test Examples

### 1. Multiple Date Ranges Query
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Show me active campaigns from last week and this week with budget > $100 and status paused"}'
```

**Expected Response:**
```json
{
  "success": true,
  "actions": ["GET_CAMPAIGNS_WITH_FILTERS"],
  "date_ranges": [
    {
      "start_date": null,
      "end_date": null,
      "period": "last_week",
      "description": "Data from last week"
    },
    {
      "start_date": null,
      "end_date": null,
      "period": "this_week",
      "description": "Data from this week"
    }
  ],
  "filters": [
    {
      "field": "budget",
      "operator": "greater_than",
      "value": 100,
      "description": "Campaigns with budget greater than $100"
    },
    {
      "field": "status",
      "operator": "equals",
      "value": "PAUSED",
      "description": "Campaigns with paused status"
    }
  ],
  "confidence": 0.95,
  "reasoning": "The query requests active campaigns with specific budget and status filters over two distinct time periods...",
  "parameters": {}
}
```

### 2. Quarter Comparison Query
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Compare campaigns from Q1 and Q2 with status active or paused and budget between $500 and $1000"}'
```

**Expected Response:**
```json
{
  "success": true,
  "actions": ["CAMPAIGN_SUMMARY_COMPARISON"],
  "date_ranges": [
    {
      "start_date": "2024-01-01",
      "end_date": "2024-03-31",
      "period": "Q1",
      "description": "First quarter of the year"
    },
    {
      "start_date": "2024-04-01",
      "end_date": "2024-06-30",
      "period": "Q2",
      "description": "Second quarter of the year"
    }
  ],
  "filters": [
    {
      "field": "status",
      "operator": "equals",
      "value": "ACTIVE",
      "description": "Campaigns with active status"
    },
    {
      "field": "status",
      "operator": "equals",
      "value": "PAUSED",
      "description": "Campaigns with paused status"
    },
    {
      "field": "budget",
      "operator": "between",
      "value": [500, 1000],
      "description": "Campaigns with budget between $500 and $1000"
    }
  ],
  "confidence": 0.95,
  "reasoning": "The query explicitly requests a comparison of campaigns across two quarters with specific status and budget filters...",
  "parameters": {}
}
```

### 3. Complex Multi-Filter Query
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Get campaigns with status active, budget > $500, name containing summer, and created between Jan 1 and Mar 31"}'
```

**Expected Response:**
```json
{
  "success": true,
  "actions": ["GET_CAMPAIGNS_WITH_FILTERS"],
  "date_ranges": [
    {
      "start_date": "2024-01-01",
      "end_date": "2024-03-31",
      "period": null,
      "description": "Created between Jan 1 and Mar 31"
    }
  ],
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
      "value": 500,
      "description": "Campaigns with budget greater than $500"
    },
    {
      "field": "name",
      "operator": "contains",
      "value": "summer",
      "description": "Campaigns containing summer in name"
    }
  ],
  "confidence": 0.95,
  "reasoning": "Query matches campaign filtering with multiple criteria and date range...",
  "parameters": {}
}
```

### 4. Ad Groups with Multiple Filters
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Show me ad groups for campaign 12345 and 67890 from last month and this month with status enabled or paused"}'
```

**Expected Response:**
```json
{
  "success": true,
  "actions": ["GET_ADSETS_BY_CAMPAIGN_ID"],
  "date_ranges": [
    {
      "start_date": "2024-08-01",
      "end_date": "2024-08-31",
      "period": "last_month",
      "description": "Last month data"
    },
    {
      "start_date": "2024-09-01",
      "end_date": "2024-09-10",
      "period": "this_month",
      "description": "This month data"
    }
  ],
  "filters": [
    {
      "field": "campaign_id",
      "operator": "in",
      "value": ["12345", "67890"],
      "description": "Ad groups for specific campaign IDs"
    },
    {
      "field": "status",
      "operator": "equals",
      "value": "ENABLED",
      "description": "Ad groups with enabled status"
    },
    {
      "field": "status",
      "operator": "equals",
      "value": "PAUSED",
      "description": "Ad groups with paused status"
    }
  ],
  "confidence": 0.95,
  "reasoning": "Query requests ad groups for multiple campaigns across two months with status filters...",
  "parameters": {}
}
```

## 📅 Date Range Extraction Examples

### Multiple Date Ranges
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/extract-date-range/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Show me data from last week and this month"}'
```

**Response:**
```json
{
  "success": true,
  "date_ranges": [
    {
      "start_date": "2025-09-01",
      "end_date": "2025-09-10",
      "period": "this_month",
      "description": "This month"
    }
  ]
}
```

### Single Date Range
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/extract-date-range/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Get campaigns from last 7 days"}'
```

**Response:**
```json
{
  "success": true,
  "date_ranges": [
    {
      "start_date": "2025-09-03",
      "end_date": "2025-09-10",
      "period": "last_7_days",
      "description": "Last 7 days"
    }
  ]
}
```

## 🔍 Filter Types Supported

### Status Filters
- `status = "ACTIVE"` - Active campaigns/ads
- `status = "PAUSED"` - Paused campaigns/ads
- `status = "ENABLED"` - Enabled ads
- `status in ["ACTIVE", "PAUSED"]` - Multiple status values

### Budget Filters
- `budget > 100` - Budget greater than $100
- `budget < 1000` - Budget less than $1000
- `budget between [500, 1000]` - Budget between $500 and $1000
- `budget >= 500` - Budget greater than or equal to $500

### Name Filters
- `name contains "summer"` - Name contains "summer"
- `name = "Holiday Campaign"` - Exact name match
- `name in ["Campaign A", "Campaign B"]` - Multiple name values

### Date Filters
- `created_date >= "2024-01-01"` - Created after date
- `modified_date <= "2024-01-31"` - Modified before date
- `created_date between ["2024-01-01", "2024-01-31"]` - Created between dates

### Campaign ID Filters
- `campaign_id = "12345"` - Specific campaign ID
- `campaign_id in ["12345", "67890"]` - Multiple campaign IDs

## 🎯 Key Features

✅ **Multiple Date Ranges** - Handle queries like "from Q1 and Q2"  
✅ **Multiple Filters** - Handle queries like "status active AND budget > $100"  
✅ **Array Format** - Both date_ranges and filters are now arrays  
✅ **Backward Compatibility** - Still works with single date ranges and filters  
✅ **Rich Descriptions** - Each date range and filter includes a description  
✅ **Complex Operators** - Supports "between", "in", "contains", etc.  
✅ **High Confidence** - Maintains high accuracy with complex queries  

## 🚀 Usage Examples

### Basic Query (Single Date Range, Single Filter)
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Show me active campaigns from last 7 days"}'
```

### Complex Query (Multiple Date Ranges, Multiple Filters)
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Compare campaigns from Q1 and Q2 with status active or paused and budget between $500 and $1000"}'
```

### Ad Group Query (Multiple Campaign IDs, Multiple Date Ranges)
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Get ad groups for campaigns 12345 and 67890 from last month and this month"}'
```

## 📝 Notes

- Replace `YOUR_JWT_TOKEN` with your actual JWT token
- The system now handles complex queries with multiple date ranges and filters
- All responses maintain backward compatibility with existing single-value queries
- Date ranges and filters are returned as arrays for maximum flexibility
- Each array item includes a description for better understanding
- The system supports complex operators like "between", "in", "contains"
- Confidence scores remain high even with complex multi-criteria queries

The Intent Mapping API now fully supports multiple date ranges and filters as arrays! 🎉


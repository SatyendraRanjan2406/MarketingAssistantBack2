# 🤖 RAG Chat API with Intent Mapping

A comprehensive RAG (Retrieval-Augmented Generation) chat system that integrates with Intent Mapping Service to provide intelligent responses with structured action execution.

## 📋 Overview

The RAG Chat API combines:
- **Intent Mapping**: Maps user queries to specific Google Ads actions using OpenAI
- **Tool Execution**: Executes 70+ intent actions with date ranges, filters, and ID support
- **LLM Orchestration**: Generates intelligent responses based on intent mapping results
- **Conversation Management**: Maintains chat history and context

## 🚀 Features

### ✅ Intent Mapping Integration
- Maps natural language queries to specific Google Ads actions
- Extracts date ranges, filters, and parameters automatically
- Supports complex queries with multiple criteria
- Returns confidence scores and reasoning

### ✅ Comprehensive Tool Support
- **70+ Intent Actions** across 12 categories
- **Date Range Support**: Last 7 days, this month, Q1/Q2, etc.
- **Filter Support**: Status, budget, name, custom filters
- **ID Support**: Campaign, ad, ad group, budget IDs
- **Parameter Support**: Sorting, limiting, grouping

### ✅ Categories of Actions
- **Basic Operations** (22): GET_CAMPAIGNS, CREATE_CAMPAIGN, GET_ADS, etc.
- **Analysis** (8): CAMPAIGN_SUMMARY_COMPARISON, TREND_ANALYSIS, etc.
- **Creative** (7): GENERATE_AD_COPIES, GENERATE_IMAGES, etc.
- **Optimization** (6): OPTIMIZE_CAMPAIGN, OPTIMIZE_BUDGETS, etc.
- **Audience** (3): ANALYZE_AUDIENCE, ANALYZE_DEMOGRAPHICS, etc.
- **Technical** (5): CHECK_CAMPAIGN_CONSISTENCY, CHECK_SITELINKS, etc.
- **Performance** (7): ANALYZE_DEVICE_PERFORMANCE, ANALYZE_LOCATION, etc.
- **Keywords** (4): ANALYZE_KEYWORD_TRENDS, SUGGEST_NEGATIVE_KEYWORDS, etc.
- **Competitive** (2): ANALYZE_COMPETITORS, ANALYZE_ADS_SHOWING_TIME
- **Knowledge Base** (3): SEARCH_KB, ADD_KB_DOCUMENT, SEARCH_DB
- **Analytics** (1): GET_ANALYTICS
- **Fallback** (2): QUERY_WITHOUT_SOLUTION, query_understanding_fallback

## 🛠️ API Endpoint

### RAG Chat Endpoint
```bash
POST /ad-expert/api/rag/chat/
```

**Authentication**: JWT Token required

**Request Body**:
```json
{
  "query": "Show me active campaigns from last 7 days with budget > $100",
  "conversation_id": "optional_conversation_id",
  "user_context": {
    "customer_id": "1234567890",
    "campaigns": ["campaign1", "campaign2"]
  }
}
```

**Response**:
```json
{
  "success": true,
  "intent_mapping": {
    "actions": ["GET_CAMPAIGNS_WITH_FILTERS"],
    "date_ranges": [
      {
        "start_date": "2024-01-08",
        "end_date": "2024-01-15",
        "period": "last_7_days",
        "description": "Data from last 7 days"
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
    "reasoning": "Query matches campaign filtering request with date range and budget filter",
    "parameters": {
      "limit": 50,
      "sort_by": "clicks",
      "order": "desc"
    }
  },
  "chat_response": "I found 5 active campaigns from the last 7 days with budgets over $100. Here are the key insights...",
  "conversation_id": 123,
  "timestamp": "2024-01-15T10:30:00Z",
  "query": "Show me active campaigns from last 7 days with budget > $100"
}
```

## 🧪 Usage Examples

### 1. Basic Campaign Query
```bash
curl -X POST 'http://localhost:8000/ad-expert/api/rag/chat/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Show me all campaigns"}'
```

### 2. Complex Query with Filters
```bash
curl -X POST 'http://localhost:8000/ad-expert/api/rag/chat/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "Compare campaigns from Q1 and Q2 with status active or paused and budget between $500 and $1000",
    "user_context": {
      "customer_id": "1234567890"
    }
  }'
```

### 3. Ad Group Query
```bash
curl -X POST 'http://localhost:8000/ad-expert/api/rag/chat/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "Get ad groups for campaign 12345 from last week",
    "conversation_id": 456
  }'
```

### 4. Creative Generation
```bash
curl -X POST 'http://localhost:8000/ad-expert/api/rag/chat/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "Generate ad copies for summer campaign with professional tone",
    "user_context": {
      "theme": "summer sale",
      "tone": "professional"
    }
  }'
```

### 5. Analysis Query
```bash
curl -X POST 'http://localhost:8000/ad-expert/api/rag/chat/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "Analyze device performance for my campaigns and show trends",
    "user_context": {
      "customer_id": "1234567890"
    }
  }'
```

## 🔧 Tool Parameters

### Date Ranges
```json
{
  "date_ranges": [
    {
      "start_date": "2024-01-01",
      "end_date": "2024-01-31",
      "period": "this_month",
      "description": "This month data"
    }
  ]
}
```

### Filters
```json
{
  "filters": [
    {
      "field": "status",
      "operator": "equals",
      "value": "ACTIVE",
      "description": "Campaigns with active status"
    },
    {
      "field": "budget",
      "operator": "between",
      "value": [500, 1000],
      "description": "Campaigns with budget between $500 and $1000"
    }
  ]
}
```

### ID Parameters
```json
{
  "campaign_id": "12345",
  "ad_group_id": "67890",
  "ad_id": "11111",
  "budget_id": "22222"
}
```

### List Parameters
```json
{
  "campaign_ids": ["12345", "67890"],
  "ad_group_ids": ["11111", "22222"],
  "ad_ids": ["33333", "44444"],
  "budget_ids": ["55555", "66666"]
}
```

## 📊 Response Types

### 1. Data Retrieval Response
```json
{
  "success": true,
  "action": "GET_CAMPAIGNS_WITH_FILTERS",
  "data": [
    {
      "id": "campaign_123",
      "name": "Summer Sale Campaign",
      "status": "ACTIVE",
      "clicks": 100,
      "impressions": 1000,
      "cost": 50.0,
      "ctr": 0.1,
      "cpc": 0.5
    }
  ],
  "parameters": {...},
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 2. Analysis Response
```json
{
  "success": true,
  "action": "ANALYZE_DEVICE_PERFORMANCE",
  "analysis": {
    "summary": "Device performance analysis completed",
    "metrics": {
      "total_clicks": 1000,
      "total_impressions": 10000,
      "total_cost": 500.0,
      "average_ctr": 0.1,
      "average_cpc": 0.5
    },
    "trends": {
      "clicks_trend": "increasing",
      "cost_trend": "stable",
      "performance_trend": "improving"
    }
  },
  "insights": [
    "Mobile performance is 20% better than desktop",
    "Tablet CTR is below average",
    "Consider increasing mobile bids"
  ],
  "parameters": {...},
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 3. Creative Generation Response
```json
{
  "success": true,
  "action": "GENERATE_AD_COPIES",
  "generated_content": [
    {
      "id": "generated_1",
      "title": "Summer Sale - 50% Off",
      "description": "Don't miss our biggest summer sale!",
      "headline": "Summer Sale - 50% Off Everything",
      "call_to_action": "Shop Now"
    }
  ],
  "parameters": {...},
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🎯 Intent Action Categories

### Basic Operations (22 actions)
- `GET_OVERVIEW` - Account overview
- `GET_CAMPAIGNS` - List campaigns
- `GET_CAMPAIGN_BY_ID` - Specific campaign
- `GET_CAMPAIGNS_WITH_FILTERS` - Filtered campaigns
- `CREATE_CAMPAIGN` - Create new campaign
- `GET_ADS` - List ads
- `GET_AD_BY_ID` - Specific ad
- `GET_ADS_WITH_FILTERS` - Filtered ads
- `GET_ADS_BY_CAMPAIGN_ID` - Campaign ads
- `GET_ADSETS` - List ad groups
- `GET_ADSET_BY_ID` - Specific ad group
- `GET_ADSETS_WITH_FILTERS` - Filtered ad groups
- `GET_ADSETS_BY_CAMPAIGN_ID` - Campaign ad groups
- `CREATE_AD` - Create new ad
- `PAUSE_CAMPAIGN` - Pause campaigns
- `RESUME_CAMPAIGN` - Resume campaigns
- `GET_PERFORMANCE` - Performance data
- `GET_KEYWORDS` - Keywords data
- `GET_BUDGETS` - Budget data
- `GET_BUDGET_BY_ID` - Specific budget
- `GET_BUDGETS_WITH_FILTERS` - Filtered budgets
- `GET_BUDGETS_BY_CAMPAIGN_ID` - Campaign budgets

### Analysis (8 actions)
- `CAMPAIGN_SUMMARY_COMPARISON` - Compare campaigns
- `PERFORMANCE_SUMMARY` - Performance summary
- `TREND_ANALYSIS` - Trend analysis
- `LISTING_ANALYSIS` - Listing analysis
- `PIE_CHART_DISPLAY` - Pie chart data
- `DUPLICATE_KEYWORDS_ANALYSIS` - Duplicate keywords
- `DIG_DEEPER_ANALYSIS` - Deep analysis
- `COMPARE_PERFORMANCE` - Performance comparison

### Creative (7 actions)
- `GENERATE_AD_COPIES` - Generate ad copy
- `GENERATE_CREATIVES` - Generate creatives
- `POSTER_GENERATOR` - Generate posters
- `META_ADS_CREATIVES` - Meta ad creatives
- `GENERATE_IMAGES` - Generate images
- `TEST_CREATIVE_ELEMENTS` - Test creatives
- `CHECK_CREATIVE_FATIGUE` - Check fatigue

### Optimization (6 actions)
- `OPTIMIZE_CAMPAIGN` - Optimize campaigns
- `OPTIMIZE_ADSET` - Optimize ad groups
- `OPTIMIZE_AD` - Optimize ads
- `OPTIMIZE_BUDGETS` - Optimize budgets
- `OPTIMIZE_TCPA` - Target CPA optimization
- `OPTIMIZE_BUDGET_ALLOCATION` - Budget allocation

### Audience (3 actions)
- `ANALYZE_AUDIENCE` - Audience analysis
- `ANALYZE_AUDIENCE_INSIGHTS` - Audience insights
- `ANALYZE_DEMOGRAPHICS` - Demographics

### Technical (5 actions)
- `CHECK_CAMPAIGN_CONSISTENCY` - Consistency check
- `CHECK_SITELINKS` - Sitelinks check
- `CHECK_LANDING_PAGE_URL` - URL compliance
- `CHECK_DUPLICATE_KEYWORDS` - Duplicate keywords
- `CHECK_TECHNICAL_COMPLIANCE` - Technical compliance

### Performance (7 actions)
- `ANALYZE_VIDEO_PERFORMANCE` - Video performance
- `ANALYZE_PLACEMENTS` - Placement analysis
- `ANALYZE_DEVICE_PERFORMANCE` - Device performance
- `ANALYZE_DEVICE_PERFORMANCE_DETAILED` - Detailed device
- `ANALYZE_TIME_PERFORMANCE` - Time performance
- `ANALYZE_LOCATION_PERFORMANCE` - Location performance
- `ANALYZE_LANDING_PAGE_MOBILE` - Mobile landing page

### Keywords (4 actions)
- `ANALYZE_KEYWORD_TRENDS` - Keyword trends
- `ANALYZE_AUCTION_INSIGHTS` - Auction insights
- `ANALYZE_SEARCH_TERMS` - Search terms
- `SUGGEST_NEGATIVE_KEYWORDS` - Negative keywords

### Competitive (2 actions)
- `ANALYZE_COMPETITORS` - Competitor analysis
- `ANALYZE_ADS_SHOWING_TIME` - Ad showing time

### Knowledge Base (3 actions)
- `SEARCH_KB` - Search knowledge base
- `ADD_KB_DOCUMENT` - Add documents
- `SEARCH_DB` - Search database

### Analytics (1 action)
- `GET_ANALYTICS` - Analytics data

### Fallback (2 actions)
- `QUERY_WITHOUT_SOLUTION` - No solution
- `query_understanding_fallback` - Understanding error

## 🔧 Setup and Configuration

### 1. Environment Variables
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

### 2. Dependencies
```bash
pip install openai langchain langchain-openai
```

### 3. Django Settings
```python
INSTALLED_APPS = [
    # ... other apps
    'ad_expert',
    'google_ads_new',
]
```

## 🚀 Advanced Features

### 1. Conversation Management
- Maintains chat history across requests
- Supports conversation_id for context
- Automatic conversation creation

### 2. Context Enhancement
- User context integration
- Intent mapping results in context
- Enhanced LLM responses

### 3. Error Handling
- Comprehensive error handling
- Graceful fallbacks
- Detailed error messages

### 4. Logging
- Detailed logging for debugging
- Performance monitoring
- Error tracking

## 📝 Notes

- All endpoints require JWT authentication
- Intent mapping uses OpenAI GPT-4o
- Tool execution is simulated (replace with actual Google Ads API calls)
- Supports 70+ different intent actions
- Handles complex queries with multiple criteria
- Maintains conversation context
- Provides structured responses with metadata

The RAG Chat API provides a powerful interface for intelligent Google Ads management through natural language queries! 🎉


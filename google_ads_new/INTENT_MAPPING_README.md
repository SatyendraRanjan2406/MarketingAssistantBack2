# 🎯 Intent Mapping System

A comprehensive system for mapping user queries to Google Ads intent actions using OpenAI, with automatic extraction of date ranges and filters.

## 📋 Overview

The Intent Mapping System analyzes natural language queries and maps them to specific Google Ads API actions, automatically extracting:
- **Intent Actions**: Which Google Ads operations to perform
- **Date Ranges**: Start/end dates and time periods
- **Filters**: Field-based filtering criteria
- **Parameters**: Additional query parameters

## 🚀 Features

### ✅ Intent Actions (70+ Actions)
- **Basic Operations**: Campaigns, Ads, Ad Groups, Budgets
- **Analysis**: Performance summaries, trend analysis, comparisons
- **Creative**: Ad copy generation, image creation, design ideas
- **Optimization**: Campaign optimization, budget allocation
- **Technical**: Compliance checks, audits, consistency validation
- **Performance**: Device, location, time-based analysis
- **Keywords**: Keyword trends, auction insights, search terms
- **Competitive**: Competitor analysis, ad showing time
- **Knowledge Base**: Document search and management

### 📅 Date Range Extraction
- **Relative Periods**: "last 7 days", "this month", "yesterday"
- **Specific Dates**: "from Jan 1 to Jan 31", "since 2024-01-01"
- **Smart Parsing**: Handles various date formats and expressions

### 🔍 Filter Extraction
- **Field-based**: Status, budget, name, type, etc.
- **Operators**: equals, contains, greater_than, less_than, in, not_in
- **Value Types**: Strings, numbers, booleans, arrays
- **Context-aware**: Understands campaign, ad, budget relationships

## 🛠️ API Endpoints

### Main Intent Mapping
```bash
POST /google-ads-new/api/intent-mapping/
```
**Body:**
```json
{
  "query": "Show me active campaigns from last 7 days with budget > $100",
  "user_context": {
    "customer_id": "1234567890",
    "campaigns": ["campaign1", "campaign2"]
  }
}
```

**Response:**
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

### Available Actions
```bash
GET /google-ads-new/api/intent-mapping/actions/
GET /google-ads-new/api/intent-mapping/actions/{category}/
GET /google-ads-new/api/intent-mapping/actions/details/{action_name}/
```

### Utility Endpoints
```bash
POST /google-ads-new/api/intent-mapping/extract-date-range/
POST /google-ads-new/api/intent-mapping/test/  # No auth required
```

## 📊 Intent Actions by Category

### Basic Operations (18 actions)
- `GET_OVERVIEW` - Account overview and summary
- `GET_CAMPAIGNS` - Retrieve campaign information
- `GET_CAMPAIGN_BY_ID` - Get specific campaign by ID
- `GET_CAMPAIGNS_WITH_FILTERS` - Get campaigns with filters
- `GET_ADS` - Get ads for campaigns
- `GET_AD_BY_ID` - Get specific ad by ID
- `GET_ADS_WITH_FILTERS` - Get ads with filters
- `GET_ADS_BY_CAMPAIGN_ID` - Get ads for specific campaign
- `GET_ADSETS` - Get ad groups (adsets)
- `GET_ADSET_BY_ID` - Get specific ad group by ID
- `GET_ADSETS_WITH_FILTERS` - Get ad groups with filters
- `GET_ADSETS_BY_CAMPAIGN_ID` - Get ad groups for campaign
- `GET_BUDGETS` - Get budget information
- `GET_BUDGET_BY_ID` - Get specific budget by ID
- `GET_BUDGETS_WITH_FILTERS` - Get budgets with filters
- `GET_BUDGETS_BY_CAMPAIGN_ID` - Get budgets for campaign
- `CREATE_CAMPAIGN` - Create new campaigns
- `CREATE_AD` - Create new ads

### Analysis (8 actions)
- `CAMPAIGN_SUMMARY_COMPARISON` - Compare campaigns and metrics
- `PERFORMANCE_SUMMARY` - Performance summary with insights
- `TREND_ANALYSIS` - Trend analysis with graphs
- `LISTING_ANALYSIS` - Listings with key insights
- `PIE_CHART_DISPLAY` - Pie chart data visualization
- `DUPLICATE_KEYWORDS_ANALYSIS` - Duplicate keyword analysis
- `DIG_DEEPER_ANALYSIS` - Hierarchical analysis requests
- `COMPARE_PERFORMANCE` - Performance comparison

### Creative (7 actions)
- `GENERATE_AD_COPIES` - Generate ad copy variations
- `GENERATE_CREATIVES` - Generate creative ideas
- `POSTER_GENERATOR` - Generate poster templates
- `META_ADS_CREATIVES` - Meta/Facebook ad creatives
- `GENERATE_IMAGES` - Generate images for ads
- `TEST_CREATIVE_ELEMENTS` - Test creative variations
- `CHECK_CREATIVE_FATIGUE` - Monitor creative fatigue

### Optimization (6 actions)
- `OPTIMIZE_CAMPAIGN` - Optimize campaign settings
- `OPTIMIZE_ADSET` - Optimize ad group performance
- `OPTIMIZE_AD` - Optimize individual ad performance
- `OPTIMIZE_BUDGETS` - Optimize budget allocation
- `OPTIMIZE_TCPA` - Target CPA optimization
- `OPTIMIZE_BUDGET_ALLOCATION` - Budget allocation optimization

### Technical (5 actions)
- `CHECK_CAMPAIGN_CONSISTENCY` - Campaign consistency checks
- `CHECK_SITELINKS` - Sitelinks and extensions check
- `CHECK_LANDING_PAGE_URL` - Landing page URL compliance
- `CHECK_DUPLICATE_KEYWORDS` - Duplicate keyword audit
- `CHECK_TECHNICAL_COMPLIANCE` - Technical compliance check

### Performance (7 actions)
- `ANALYZE_VIDEO_PERFORMANCE` - Video completion analysis
- `ANALYZE_PLACEMENTS` - Placement performance analysis
- `ANALYZE_DEVICE_PERFORMANCE` - Device performance analysis
- `ANALYZE_DEVICE_PERFORMANCE_DETAILED` - Detailed device analysis
- `ANALYZE_TIME_PERFORMANCE` - Time-based performance patterns
- `ANALYZE_LOCATION_PERFORMANCE` - Location-based performance
- `ANALYZE_LANDING_PAGE_MOBILE` - Mobile landing page analysis

### Keywords (4 actions)
- `ANALYZE_KEYWORD_TRENDS` - Keyword performance trends
- `ANALYZE_AUCTION_INSIGHTS` - Auction insights and competition
- `ANALYZE_SEARCH_TERMS` - Search terms performance
- `SUGGEST_NEGATIVE_KEYWORDS` - Negative keyword suggestions

### Competitive (2 actions)
- `ANALYZE_COMPETITORS` - Competitor performance analysis
- `ANALYZE_ADS_SHOWING_TIME` - Ad showing time analysis

### Knowledge Base (3 actions)
- `SEARCH_KB` - Search knowledge base
- `ADD_KB_DOCUMENT` - Add documents to knowledge base
- `SEARCH_DB` - Search local database

### Analytics (1 action)
- `GET_ANALYTICS` - Get analytics data and insights

### Fallback (2 actions)
- `QUERY_WITHOUT_SOLUTION` - Handle unsolvable queries
- `query_understanding_fallback` - Query understanding errors

## 🔧 Setup and Installation

### 1. Install Dependencies
```bash
pip install openai langchain langchain-openai
```

### 2. Environment Variables
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

### 3. Django Settings
Add to your Django settings:
```python
INSTALLED_APPS = [
    # ... other apps
    'google_ads_new',
]
```

### 4. Run Migrations
```bash
python manage.py migrate
```

## 🧪 Testing

### Run Test Script
```bash
python google_ads_new/test_intent_mapping.py
```

### Manual Testing with cURL

#### 1. Map Query to Intents
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "Show me active campaigns from last 7 days with budget > $100",
    "user_context": {
      "customer_id": "1234567890"
    }
  }'
```

#### 2. Get Available Actions
```bash
curl -X GET 'http://localhost:8000/google-ads-new/api/intent-mapping/actions/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'
```

#### 3. Test Without Authentication
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/test/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Show me campaigns"}'
```

## 📝 Usage Examples

### Example 1: Basic Campaign Query
```json
{
  "query": "Show me all campaigns",
  "user_context": {}
}
```
**Result:**
- Actions: `["GET_CAMPAIGNS"]`
- Confidence: 0.95
- No filters or date ranges

### Example 2: Filtered Campaign Query
```json
{
  "query": "Show me active campaigns with budget > $500",
  "user_context": {}
}
```
**Result:**
- Actions: `["GET_CAMPAIGNS_WITH_FILTERS"]`
- Filters: Status=ACTIVE, Budget>500
- Confidence: 0.92

### Example 3: Date Range Query
```json
{
  "query": "Get performance data from last 30 days",
  "user_context": {}
}
```
**Result:**
- Actions: `["GET_PERFORMANCE"]`
- Date Range: Last 30 days
- Confidence: 0.88

### Example 4: Complex Query
```json
{
  "query": "Show me active campaigns with budget > $1000 from last 7 days and compare their performance",
  "user_context": {
    "customer_id": "1234567890"
  }
}
```
**Result:**
- Actions: `["GET_CAMPAIGNS_WITH_FILTERS", "COMPARE_PERFORMANCE"]`
- Date Range: Last 7 days
- Filters: Status=ACTIVE, Budget>1000
- Confidence: 0.89

### Example 5: Ad Group Query
```json
{
  "query": "Get ad groups for campaign 12345 from last week",
  "user_context": {}
}
```
**Result:**
- Actions: `["GET_ADSETS_BY_CAMPAIGN_ID"]`
- Date Range: Last week
- Parameters: campaign_id=12345
- Confidence: 0.94

## 🔍 Filter Types

### Status Filters
- `status = "ACTIVE"` - Active campaigns/ads
- `status = "PAUSED"` - Paused campaigns/ads
- `status = "ENABLED"` - Enabled ads

### Budget Filters
- `budget > 100` - Budget greater than $100
- `budget < 1000` - Budget less than $1000
- `budget >= 500` - Budget greater than or equal to $500

### Name Filters
- `name contains "summer"` - Name contains "summer"
- `name = "Holiday Campaign"` - Exact name match

### Date Filters
- `created_date >= "2024-01-01"` - Created after date
- `modified_date <= "2024-01-31"` - Modified before date

## 🎯 Integration with Google Ads API

The intent mapping system is designed to work seamlessly with the Google Ads API:

1. **Query Analysis**: User query is analyzed for intent, filters, and date ranges
2. **Action Mapping**: Query is mapped to specific Google Ads API operations
3. **API Execution**: Mapped actions are executed with extracted parameters
4. **Response Processing**: Results are formatted and returned to user

## 🚀 Advanced Features

### Custom Context
The system can use user context to improve mapping accuracy:
```json
{
  "user_context": {
    "customer_id": "1234567890",
    "campaigns": ["campaign1", "campaign2"],
    "account_type": "premium",
    "user_preferences": {
      "default_date_range": "last_30_days",
      "preferred_metrics": ["clicks", "impressions"]
    }
  }
}
```

### Confidence Scoring
Each mapping includes a confidence score (0.0 to 1.0):
- **0.9-1.0**: Very high confidence, clear intent
- **0.7-0.9**: High confidence, good match
- **0.5-0.7**: Medium confidence, some ambiguity
- **0.3-0.5**: Low confidence, unclear intent
- **0.0-0.3**: Very low confidence, likely fallback

### Reasoning
Each mapping includes reasoning explaining the decision:
- Why specific actions were chosen
- How filters were extracted
- What date ranges were identified
- Any assumptions made

## 🔧 Customization

### Adding New Actions
1. Add action to `intent_actions` list in `IntentMappingService`
2. Include relevant keywords for matching
3. Update API documentation

### Custom Filters
1. Extend the `Filter` dataclass
2. Add filter extraction logic
3. Update the OpenAI prompt

### Custom Date Patterns
1. Add patterns to `extract_date_range_from_query`
2. Update the OpenAI prompt with new patterns
3. Test with various date expressions

## 📚 API Documentation

### Authentication
Most endpoints require JWT authentication:
```bash
Authorization: Bearer YOUR_JWT_TOKEN
```

### Error Handling
All endpoints return consistent error format:
```json
{
  "success": false,
  "error": "Error message"
}
```

### Rate Limiting
- OpenAI API calls are rate-limited
- Consider implementing caching for repeated queries
- Monitor API usage and costs

## 🎉 Conclusion

The Intent Mapping System provides a powerful way to convert natural language queries into structured Google Ads API operations. It automatically extracts date ranges, filters, and parameters, making it easy to build conversational interfaces for Google Ads management.

For more information, see the test script and API examples in this repository.


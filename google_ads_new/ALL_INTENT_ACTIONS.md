# 🎯 All Intent Actions Array

## **Complete List of Intent Actions**

```javascript
const INTENT_ACTIONS = [
  // === BASIC GOOGLE ADS OPERATIONS ===
  {
    "action": "GET_OVERVIEW",
    "description": "Get account overview and summary",
    "category": "basic_operations",
    "requires_auth": true
  },
  {
    "action": "GET_CAMPAIGNS",
    "description": "Retrieve campaign information",
    "category": "basic_operations",
    "requires_auth": true
  },
  {
    "action": "CREATE_CAMPAIGN",
    "description": "Create new campaigns with budgets",
    "category": "basic_operations",
    "requires_auth": true
  },
  {
    "action": "GET_ADS",
    "description": "Get ads for campaigns",
    "category": "basic_operations",
    "requires_auth": true
  },
  {
    "action": "CREATE_AD",
    "description": "Create new ads",
    "category": "basic_operations",
    "requires_auth": true
  },
  {
    "action": "PAUSE_CAMPAIGN",
    "description": "Pause active campaigns",
    "category": "basic_operations",
    "requires_auth": true
  },
  {
    "action": "RESUME_CAMPAIGN",
    "description": "Resume paused campaigns",
    "category": "basic_operations",
    "requires_auth": true
  },
  {
    "action": "GET_PERFORMANCE",
    "description": "Get performance data and metrics",
    "category": "basic_operations",
    "requires_auth": true
  },
  {
    "action": "GET_KEYWORDS",
    "description": "Get keywords for campaigns",
    "category": "basic_operations",
    "requires_auth": true
  },
  {
    "action": "GET_BUDGETS",
    "description": "Get budget information",
    "category": "basic_operations",
    "requires_auth": true
  },

  // === ANALYSIS ACTIONS ===
  {
    "action": "CAMPAIGN_SUMMARY_COMPARISON",
    "description": "Compare campaigns, ad groups, adsets, ads for key metrics and sorting",
    "category": "analysis",
    "requires_auth": true
  },
  {
    "action": "PERFORMANCE_SUMMARY",
    "description": "Show performance summary in tables with key insights and recommendations",
    "category": "analysis",
    "requires_auth": true
  },
  {
    "action": "TREND_ANALYSIS",
    "description": "Display trends using line graphs or bar graphs for metrics like clicks, CPC, CTR",
    "category": "analysis",
    "requires_auth": true
  },
  {
    "action": "LISTING_ANALYSIS",
    "description": "Show listings in tables with additional key insights based on data",
    "category": "analysis",
    "requires_auth": true
  },
  {
    "action": "PIE_CHART_DISPLAY",
    "description": "Display data in pie charts when requested",
    "category": "analysis",
    "requires_auth": true
  },
  {
    "action": "DUPLICATE_KEYWORDS_ANALYSIS",
    "description": "Analyze duplicate keywords across campaigns and provide consolidation recommendations",
    "category": "analysis",
    "requires_auth": true
  },
  {
    "action": "DIG_DEEPER_ANALYSIS",
    "description": "Handle follow-up analysis requests with hierarchical depth tracking",
    "category": "analysis",
    "requires_auth": true
  },
  {
    "action": "COMPARE_PERFORMANCE",
    "description": "Compare performance across different time periods or campaigns",
    "category": "analysis",
    "requires_auth": true
  },

  // === AUDIENCE & DEMOGRAPHICS ===
  {
    "action": "ANALYZE_AUDIENCE",
    "description": "Analyze audience size, overlap, and quality",
    "category": "audience",
    "requires_auth": true
  },
  {
    "action": "ANALYZE_AUDIENCE_INSIGHTS",
    "description": "Get detailed audience insights and demographics",
    "category": "audience",
    "requires_auth": true
  },
  {
    "action": "ANALYZE_DEMOGRAPHICS",
    "description": "Analyze demographic performance data",
    "category": "audience",
    "requires_auth": true
  },

  // === CREATIVE ACTIONS ===
  {
    "action": "GENERATE_AD_COPIES",
    "description": "Generate multiple ad copy variations for Google Ads",
    "category": "creative",
    "requires_auth": false
  },
  {
    "action": "GENERATE_CREATIVES",
    "description": "Generate creative ideas and designs for ads",
    "category": "creative",
    "requires_auth": false
  },
  {
    "action": "POSTER_GENERATOR",
    "description": "Generate poster templates and design suggestions",
    "category": "creative",
    "requires_auth": false
  },
  {
    "action": "META_ADS_CREATIVES",
    "description": "Generate creative ideas specifically for Meta/Facebook ads",
    "category": "creative",
    "requires_auth": false
  },
  {
    "action": "GENERATE_IMAGES",
    "description": "Generate images for ads and creatives",
    "category": "creative",
    "requires_auth": false
  },
  {
    "action": "TEST_CREATIVE_ELEMENTS",
    "description": "Test different creative elements and variations",
    "category": "creative",
    "requires_auth": true
  },
  {
    "action": "CHECK_CREATIVE_FATIGUE",
    "description": "Monitor creative fatigue and variety",
    "category": "creative",
    "requires_auth": true
  },

  // === OPTIMIZATION ACTIONS ===
  {
    "action": "OPTIMIZE_CAMPAIGN",
    "description": "Optimize campaign settings and performance",
    "category": "optimization",
    "requires_auth": true
  },
  {
    "action": "OPTIMIZE_ADSET",
    "description": "Optimize ad set performance",
    "category": "optimization",
    "requires_auth": true
  },
  {
    "action": "OPTIMIZE_AD",
    "description": "Optimize individual ad performance",
    "category": "optimization",
    "requires_auth": true
  },
  {
    "action": "OPTIMIZE_BUDGETS",
    "description": "Optimize budget allocation across campaigns",
    "category": "optimization",
    "requires_auth": true
  },
  {
    "action": "OPTIMIZE_TCPA",
    "description": "Target CPA optimization recommendations",
    "category": "optimization",
    "requires_auth": true
  },
  {
    "action": "OPTIMIZE_BUDGET_ALLOCATION",
    "description": "Campaign budget allocation optimization",
    "category": "optimization",
    "requires_auth": true
  },

  // === TECHNICAL ANALYSIS ===
  {
    "action": "CHECK_CAMPAIGN_CONSISTENCY",
    "description": "Check campaign consistency and best practices",
    "category": "technical",
    "requires_auth": true
  },
  {
    "action": "CHECK_SITELINKS",
    "description": "Check sitelinks and extensions",
    "category": "technical",
    "requires_auth": true
  },
  {
    "action": "CHECK_LANDING_PAGE_URL",
    "description": "Check landing page URL compliance",
    "category": "technical",
    "requires_auth": true
  },
  {
    "action": "CHECK_DUPLICATE_KEYWORDS",
    "description": "Check for duplicate keywords across campaigns",
    "category": "technical",
    "requires_auth": true
  },
  {
    "action": "CHECK_TECHNICAL_COMPLIANCE",
    "description": "Check technical compliance and policy adherence",
    "category": "technical",
    "requires_auth": true
  },

  // === PERFORMANCE ANALYSIS ===
  {
    "action": "ANALYZE_VIDEO_PERFORMANCE",
    "description": "Analyze video completion rates and format performance",
    "category": "performance",
    "requires_auth": true
  },
  {
    "action": "ANALYZE_PLACEMENTS",
    "description": "Analyze placement performance",
    "category": "performance",
    "requires_auth": true
  },
  {
    "action": "ANALYZE_DEVICE_PERFORMANCE",
    "description": "Analyze device performance data",
    "category": "performance",
    "requires_auth": true
  },
  {
    "action": "ANALYZE_DEVICE_PERFORMANCE_DETAILED",
    "description": "Detailed device performance analysis",
    "category": "performance",
    "requires_auth": true
  },
  {
    "action": "ANALYZE_TIME_PERFORMANCE",
    "description": "Analyze time-based performance patterns",
    "category": "performance",
    "requires_auth": true
  },
  {
    "action": "ANALYZE_LOCATION_PERFORMANCE",
    "description": "Analyze location-based performance",
    "category": "performance",
    "requires_auth": true
  },
  {
    "action": "ANALYZE_LANDING_PAGE_MOBILE",
    "description": "Analyze mobile landing page performance",
    "category": "performance",
    "requires_auth": true
  },

  // === KEYWORD ANALYSIS ===
  {
    "action": "ANALYZE_KEYWORD_TRENDS",
    "description": "Analyze keyword performance trends",
    "category": "keywords",
    "requires_auth": true
  },
  {
    "action": "ANALYZE_AUCTION_INSIGHTS",
    "description": "Analyze auction insights and competition",
    "category": "keywords",
    "requires_auth": true
  },
  {
    "action": "ANALYZE_SEARCH_TERMS",
    "description": "Analyze search terms performance",
    "category": "keywords",
    "requires_auth": true
  },
  {
    "action": "SUGGEST_NEGATIVE_KEYWORDS",
    "description": "Negative keyword exclusion suggestions",
    "category": "keywords",
    "requires_auth": true
  },

  // === COMPETITIVE ANALYSIS ===
  {
    "action": "ANALYZE_COMPETITORS",
    "description": "Analyze competitor performance and strategies",
    "category": "competitive",
    "requires_auth": true
  },
  {
    "action": "ANALYZE_ADS_SHOWING_TIME",
    "description": "Analyze when ads are showing and performance",
    "category": "competitive",
    "requires_auth": true
  },

  // === KNOWLEDGE BASE ===
  {
    "action": "SEARCH_KB",
    "description": "Search knowledge base for information",
    "category": "knowledge_base",
    "requires_auth": false
  },
  {
    "action": "ADD_KB_DOCUMENT",
    "description": "Add documents to knowledge base",
    "category": "knowledge_base",
    "requires_auth": true
  },
  {
    "action": "SEARCH_DB",
    "description": "Search local database",
    "category": "knowledge_base",
    "requires_auth": true
  },

  // === ANALYTICS ===
  {
    "action": "GET_ANALYTICS",
    "description": "Get analytics data and insights",
    "category": "analytics",
    "requires_auth": true
  },

  // === FALLBACK ACTIONS ===
  {
    "action": "QUERY_WITHOUT_SOLUTION",
    "description": "Handle queries that have no solution by prompting user in right direction",
    "category": "fallback",
    "requires_auth": false
  },
  {
    "action": "query_understanding_fallback",
    "description": "Fallback for query understanding errors",
    "category": "fallback",
    "requires_auth": false
  }
];
```

## **Actions by Category**

### **Basic Operations (10 actions)**
- GET_OVERVIEW, GET_CAMPAIGNS, CREATE_CAMPAIGN, GET_ADS, CREATE_AD
- PAUSE_CAMPAIGN, RESUME_CAMPAIGN, GET_PERFORMANCE, GET_KEYWORDS, GET_BUDGETS

### **Analysis (8 actions)**
- CAMPAIGN_SUMMARY_COMPARISON, PERFORMANCE_SUMMARY, TREND_ANALYSIS
- LISTING_ANALYSIS, PIE_CHART_DISPLAY, DUPLICATE_KEYWORDS_ANALYSIS
- DIG_DEEPER_ANALYSIS, COMPARE_PERFORMANCE

### **Audience & Demographics (3 actions)**
- ANALYZE_AUDIENCE, ANALYZE_AUDIENCE_INSIGHTS, ANALYZE_DEMOGRAPHICS

### **Creative (7 actions)**
- GENERATE_AD_COPIES, GENERATE_CREATIVES, POSTER_GENERATOR
- META_ADS_CREATIVES, GENERATE_IMAGES, TEST_CREATIVE_ELEMENTS
- CHECK_CREATIVE_FATIGUE

### **Optimization (6 actions)**
- OPTIMIZE_CAMPAIGN, OPTIMIZE_ADSET, OPTIMIZE_AD
- OPTIMIZE_BUDGETS, OPTIMIZE_TCPA, OPTIMIZE_BUDGET_ALLOCATION

### **Technical (5 actions)**
- CHECK_CAMPAIGN_CONSISTENCY, CHECK_SITELINKS, CHECK_LANDING_PAGE_URL
- CHECK_DUPLICATE_KEYWORDS, CHECK_TECHNICAL_COMPLIANCE

### **Performance (7 actions)**
- ANALYZE_VIDEO_PERFORMANCE, ANALYZE_PLACEMENTS, ANALYZE_DEVICE_PERFORMANCE
- ANALYZE_DEVICE_PERFORMANCE_DETAILED, ANALYZE_TIME_PERFORMANCE
- ANALYZE_LOCATION_PERFORMANCE, ANALYZE_LANDING_PAGE_MOBILE

### **Keywords (4 actions)**
- ANALYZE_KEYWORD_TRENDS, ANALYZE_AUCTION_INSIGHTS
- ANALYZE_SEARCH_TERMS, SUGGEST_NEGATIVE_KEYWORDS

### **Competitive (2 actions)**
- ANALYZE_COMPETITORS, ANALYZE_ADS_SHOWING_TIME

### **Knowledge Base (3 actions)**
- SEARCH_KB, ADD_KB_DOCUMENT, SEARCH_DB

### **Analytics (1 action)**
- GET_ANALYTICS

### **Fallback (2 actions)**
- QUERY_WITHOUT_SOLUTION, query_understanding_fallback

## **Total: 58 Intent Actions**

## **Usage in Code**

```javascript
// Filter actions by category
const creativeActions = INTENT_ACTIONS.filter(action => action.category === 'creative');

// Filter actions that require authentication
const authRequiredActions = INTENT_ACTIONS.filter(action => action.requires_auth);

// Get action by name
const getAction = (actionName) => INTENT_ACTIONS.find(action => action.action === actionName);

// Get all action names
const actionNames = INTENT_ACTIONS.map(action => action.action);
```

## **API Endpoints**

### **Chat Endpoints**
- `POST /api/chat/message/` - Send chat message
- `GET /api/chat/sessions/` - List chat sessions
- `POST /api/chat/sessions/create/` - Create new session
- `GET /api/chat/sessions/{id}/` - Get chat history
- `DELETE /api/chat/sessions/{id}/` - Delete session

### **RAG Endpoints**
- `POST /api/rag/query/` - RAG query (documentation only)
- `POST /api/rag/api/query/` - Authenticated RAG query
- `POST /api/rag/api/hybrid/` - Hybrid RAG (documentation + live data)
- `POST /api/rag/api/search/` - Search documents
- `GET /api/rag/api/status/` - RAG system status

### **Knowledge Base Endpoints**
- `POST /api/kb/add/` - Add document
- `GET /api/kb/search/?q=query` - Search documents
- `GET /api/kb/documents/` - List documents

### **Analytics Endpoints**
- `GET /api/insights/quick/` - Quick insights
- `GET /api/insights/context/` - User context
- `POST /api/tools/execute/` - Execute specific tool
- `GET /api/health/` - Service health check

### **Embedding Dashboard**
- `GET /embedding-dashboard/` - View embeddings dashboard
- `POST /api/rag/embedding-search/` - Search embeddings
- `GET /api/rag/embedding-stats/` - Get embedding statistics


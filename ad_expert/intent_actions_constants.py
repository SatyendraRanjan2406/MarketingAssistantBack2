"""
Intent Actions Constants for Ad Expert App
Complete list of all intent actions with their definitions
"""

# === BASIC GOOGLE ADS OPERATIONS ===
BASIC_OPERATIONS = [
    {
        "action": "GET_OVERVIEW",
        "description": "Get account overview and summary",
        "category": "basic_operations",
        "requires_auth": True,
        "keywords": ["overview", "summary", "account", "dashboard", "home"]
    },
    {
        "action": "GET_CAMPAIGNS",
        "description": "Retrieve campaign information",
        "category": "basic_operations",
        "requires_auth": True,
        "keywords": ["campaigns", "campaign", "list campaigns", "show campaigns"]
    },
    {
        "action": "GET_CAMPAIGN_BY_ID",
        "description": "Get specific campaign by ID with date ranges and filters",
        "category": "basic_operations",
        "requires_auth": True,
        "keywords": ["campaign id", "specific campaign", "campaign details", "get campaign", "campaign info"]
    },
    {
        "action": "GET_CAMPAIGNS_WITH_FILTERS",
        "description": "Get campaigns with specific filters and date ranges",
        "category": "basic_operations",
        "requires_auth": True,
        "keywords": ["filtered campaigns", "campaigns with", "campaigns by", "campaigns where"]
    },
    {
        "action": "CREATE_CAMPAIGN",
        "description": "Create new campaigns with budgets",
        "category": "basic_operations",
        "requires_auth": True,
        "keywords": ["create campaign", "new campaign", "add campaign", "setup campaign"]
    },
    {
        "action": "GET_ADS",
        "description": "Get ads for campaigns",
        "category": "basic_operations",
        "requires_auth": True,
        "keywords": ["ads", "advertisements", "show ads", "list ads"]
    },
    {
        "action": "GET_AD_BY_ID",
        "description": "Get specific ad by ID with date ranges and filters",
        "category": "basic_operations",
        "requires_auth": True,
        "keywords": ["ad id", "specific ad", "ad details", "get ad", "ad info"]
    },
    {
        "action": "GET_ADS_WITH_FILTERS",
        "description": "Get ads with specific filters and date ranges",
        "category": "basic_operations",
        "requires_auth": True,
        "keywords": ["filtered ads", "ads with", "ads by", "ads where", "ads for campaign"]
    },
    {
        "action": "GET_ADS_BY_CAMPAIGN_ID",
        "description": "Get all ads for a specific campaign ID",
        "category": "basic_operations",
        "requires_auth": True,
        "keywords": ["ads in campaign", "campaign ads", "ads for campaign id"]
    },
    {
        "action": "GET_ADSETS",
        "description": "Get ad groups (adsets) information",
        "category": "basic_operations",
        "requires_auth": True,
        "keywords": ["ad groups", "adsets", "ad sets", "adgroups", "list ad groups", "show ad groups"]
    },
    {
        "action": "GET_ADSET_BY_ID",
        "description": "Get specific ad group (adset) by ID with date ranges and filters",
        "category": "basic_operations",
        "requires_auth": True,
        "keywords": ["ad group id", "adset id", "specific ad group", "ad group details", "get ad group", "ad group info"]
    },
    {
        "action": "GET_ADSETS_WITH_FILTERS",
        "description": "Get ad groups (adsets) with specific filters and date ranges",
        "category": "basic_operations",
        "requires_auth": True,
        "keywords": ["filtered ad groups", "ad groups with", "ad groups by", "ad groups where", "adsets with"]
    },
    {
        "action": "GET_ADSETS_BY_CAMPAIGN_ID",
        "description": "Get all ad groups (adsets) for a specific campaign ID",
        "category": "basic_operations",
        "requires_auth": True,
        "keywords": ["ad groups in campaign", "campaign ad groups", "ad groups for campaign id", "adsets in campaign"]
    },
    {
        "action": "CREATE_AD",
        "description": "Create new ads",
        "category": "basic_operations",
        "requires_auth": True,
        "keywords": ["create ad", "new ad", "add ad", "make ad"]
    },
    {
        "action": "PAUSE_CAMPAIGN",
        "description": "Pause active campaigns",
        "category": "basic_operations",
        "requires_auth": True,
        "keywords": ["pause", "stop", "disable", "turn off"]
    },
    {
        "action": "RESUME_CAMPAIGN",
        "description": "Resume paused campaigns",
        "category": "basic_operations",
        "requires_auth": True,
        "keywords": ["resume", "start", "enable", "turn on", "activate"]
    },
    {
        "action": "GET_PERFORMANCE",
        "description": "Get performance data and metrics",
        "category": "basic_operations",
        "requires_auth": True,
        "keywords": ["performance", "metrics", "stats", "data", "results"]
    },
    {
        "action": "GET_KEYWORDS",
        "description": "Get keywords for campaigns",
        "category": "basic_operations",
        "requires_auth": True,
        "keywords": ["keywords", "keyword", "search terms", "queries"]
    },
    {
        "action": "GET_BUDGETS",
        "description": "Get budget information",
        "category": "basic_operations",
        "requires_auth": True,
        "keywords": ["budget", "budgets", "spending", "cost", "money"]
    },
    {
        "action": "GET_BUDGET_BY_ID",
        "description": "Get specific budget by ID with date ranges and filters",
        "category": "basic_operations",
        "requires_auth": True,
        "keywords": ["budget id", "specific budget", "budget details", "get budget", "budget info"]
    },
    {
        "action": "GET_BUDGETS_WITH_FILTERS",
        "description": "Get budgets with specific filters and date ranges",
        "category": "basic_operations",
        "requires_auth": True,
        "keywords": ["filtered budgets", "budgets with", "budgets by", "budgets where"]
    },
    {
        "action": "GET_BUDGETS_BY_CAMPAIGN_ID",
        "description": "Get all budgets for a specific campaign ID",
        "category": "basic_operations",
        "requires_auth": True,
        "keywords": ["budgets in campaign", "campaign budgets", "budgets for campaign id"]
    }
]

# === ANALYSIS ACTIONS ===
ANALYSIS_ACTIONS = [
    {
        "action": "CAMPAIGN_SUMMARY_COMPARISON",
        "description": "Compare campaigns, ad groups, adsets, ads for key metrics and sorting",
        "category": "analysis",
        "requires_auth": True,
        "keywords": ["compare", "comparison", "vs", "versus", "against", "sort", "rank"]
    },
    {
        "action": "PERFORMANCE_SUMMARY",
        "description": "Show performance summary in tables with key insights and recommendations",
        "category": "analysis",
        "requires_auth": True,
        "keywords": ["summary", "overview", "report", "insights", "recommendations"]
    },
    {
        "action": "TREND_ANALYSIS",
        "description": "Display trends using line graphs or bar graphs for metrics like clicks, CPC, CTR",
        "category": "analysis",
        "requires_auth": True,
        "keywords": ["trend", "trends", "graph", "chart", "line", "bar", "over time"]
    },
    {
        "action": "LISTING_ANALYSIS",
        "description": "Show listings in tables with additional key insights based on data",
        "category": "analysis",
        "requires_auth": True,
        "keywords": ["list", "listing", "table", "top", "best", "worst", "ranking"]
    },
    {
        "action": "PIE_CHART_DISPLAY",
        "description": "Display data in pie charts when requested",
        "category": "analysis",
        "requires_auth": True,
        "keywords": ["pie chart", "pie", "distribution", "breakdown", "split"]
    },
    {
        "action": "DUPLICATE_KEYWORDS_ANALYSIS",
        "description": "Analyze duplicate keywords across campaigns and provide consolidation recommendations",
        "category": "analysis",
        "requires_auth": True,
        "keywords": ["duplicate", "duplicates", "same keywords", "consolidate", "merge"]
    },
    {
        "action": "DIG_DEEPER_ANALYSIS",
        "description": "Handle follow-up analysis requests with hierarchical depth tracking",
        "category": "analysis",
        "requires_auth": True,
        "keywords": ["dig deeper", "more details", "expand", "drill down", "breakdown"]
    },
    {
        "action": "COMPARE_PERFORMANCE",
        "description": "Compare performance across different time periods or campaigns",
        "category": "analysis",
        "requires_auth": True,
        "keywords": ["compare performance", "performance comparison", "vs", "versus"]
    }
]

# === CREATIVE ACTIONS ===
CREATIVE_ACTIONS = [
    {
        "action": "GENERATE_AD_COPIES",
        "description": "Generate multiple ad copy variations for Google Ads",
        "category": "creative",
        "requires_auth": False,
        "keywords": ["ad copy", "copy", "text", "headlines", "descriptions", "generate copy"]
    },
    {
        "action": "GENERATE_CREATIVES",
        "description": "Generate creative ideas and designs for ads",
        "category": "creative",
        "requires_auth": False,
        "keywords": ["creative", "creatives", "design", "ideas", "concepts", "visual"]
    },
    {
        "action": "POSTER_GENERATOR",
        "description": "Generate poster templates and design suggestions",
        "category": "creative",
        "requires_auth": False,
        "keywords": ["poster", "flyer", "banner", "template", "design"]
    },
    {
        "action": "META_ADS_CREATIVES",
        "description": "Generate creative ideas specifically for Meta/Facebook ads",
        "category": "creative",
        "requires_auth": False,
        "keywords": ["facebook", "meta", "instagram", "social media", "facebook ads"]
    },
    {
        "action": "GENERATE_IMAGES",
        "description": "Generate images for ads and creatives",
        "category": "creative",
        "requires_auth": False,
        "keywords": ["image", "images", "picture", "photo", "visual", "generate image"]
    },
    {
        "action": "TEST_CREATIVE_ELEMENTS",
        "description": "Test different creative elements and variations",
        "category": "creative",
        "requires_auth": True,
        "keywords": ["test", "testing", "variations", "a/b test", "split test"]
    },
    {
        "action": "CHECK_CREATIVE_FATIGUE",
        "description": "Monitor creative fatigue and variety",
        "category": "creative",
        "requires_auth": True,
        "keywords": ["fatigue", "tired", "variety", "fresh", "new creative"]
    }
]

# === OPTIMIZATION ACTIONS ===
OPTIMIZATION_ACTIONS = [
    {
        "action": "OPTIMIZE_CAMPAIGN",
        "description": "Optimize campaign settings and performance",
        "category": "optimization",
        "requires_auth": True,
        "keywords": ["optimize", "optimization", "improve", "better", "enhance"]
    },
    {
        "action": "OPTIMIZE_ADSET",
        "description": "Optimize ad set performance",
        "category": "optimization",
        "requires_auth": True,
        "keywords": ["optimize ad set", "ad set optimization", "ad group optimization"]
    },
    {
        "action": "OPTIMIZE_AD",
        "description": "Optimize individual ad performance",
        "category": "optimization",
        "requires_auth": True,
        "keywords": ["optimize ad", "ad optimization", "improve ad"]
    },
    {
        "action": "OPTIMIZE_BUDGETS",
        "description": "Optimize budget allocation across campaigns",
        "category": "optimization",
        "requires_auth": True,
        "keywords": ["optimize budget", "budget optimization", "allocate budget"]
    },
    {
        "action": "OPTIMIZE_TCPA",
        "description": "Target CPA optimization recommendations",
        "category": "optimization",
        "requires_auth": True,
        "keywords": ["tCPA", "target CPA", "CPA optimization", "cost per acquisition"]
    },
    {
        "action": "OPTIMIZE_BUDGET_ALLOCATION",
        "description": "Campaign budget allocation optimization",
        "category": "optimization",
        "requires_auth": True,
        "keywords": ["budget allocation", "allocate", "distribution", "spread budget"]
    }
]

# === AUDIENCE & DEMOGRAPHICS ===
AUDIENCE_ACTIONS = [
    {
        "action": "ANALYZE_AUDIENCE",
        "description": "Analyze audience size, overlap, and quality",
        "category": "audience",
        "requires_auth": True,
        "keywords": ["audience", "audiences", "demographics", "people", "users"]
    },
    {
        "action": "ANALYZE_AUDIENCE_INSIGHTS",
        "description": "Get detailed audience insights and demographics",
        "category": "audience",
        "requires_auth": True,
        "keywords": ["audience insights", "demographics", "age", "gender", "location"]
    },
    {
        "action": "ANALYZE_DEMOGRAPHICS",
        "description": "Analyze demographic performance data",
        "category": "audience",
        "requires_auth": True,
        "keywords": ["demographics", "demographic", "age groups", "gender", "location"]
    }
]

# === TECHNICAL ANALYSIS ===
TECHNICAL_ACTIONS = [
    {
        "action": "CHECK_CAMPAIGN_CONSISTENCY",
        "description": "Check campaign consistency and best practices",
        "category": "technical",
        "requires_auth": True,
        "keywords": ["consistency", "best practices", "check", "audit", "review"]
    },
    {
        "action": "CHECK_SITELINKS",
        "description": "Check sitelinks and extensions",
        "category": "technical",
        "requires_auth": True,
        "keywords": ["sitelinks", "extensions", "site links", "ad extensions"]
    },
    {
        "action": "CHECK_LANDING_PAGE_URL",
        "description": "Check landing page URL compliance",
        "category": "technical",
        "requires_auth": True,
        "keywords": ["landing page", "URL", "compliance", "check URL"]
    },
    {
        "action": "CHECK_DUPLICATE_KEYWORDS",
        "description": "Check for duplicate keywords across campaigns",
        "category": "technical",
        "requires_auth": True,
        "keywords": ["duplicate keywords", "check duplicates", "keyword audit"]
    },
    {
        "action": "CHECK_TECHNICAL_COMPLIANCE",
        "description": "Check technical compliance and policy adherence",
        "category": "technical",
        "requires_auth": True,
        "keywords": ["compliance", "policy", "technical", "violations", "issues"]
    }
]

# === PERFORMANCE ANALYSIS ===
PERFORMANCE_ACTIONS = [
    {
        "action": "ANALYZE_VIDEO_PERFORMANCE",
        "description": "Analyze video completion rates and format performance",
        "category": "performance",
        "requires_auth": True,
        "keywords": ["video", "videos", "completion rate", "video performance"]
    },
    {
        "action": "ANALYZE_PLACEMENTS",
        "description": "Analyze placement performance",
        "category": "performance",
        "requires_auth": True,
        "keywords": ["placements", "placement", "where ads show", "sites"]
    },
    {
        "action": "ANALYZE_DEVICE_PERFORMANCE",
        "description": "Analyze device performance data",
        "category": "performance",
        "requires_auth": True,
        "keywords": ["device", "devices", "mobile", "desktop", "tablet"]
    },
    {
        "action": "ANALYZE_DEVICE_PERFORMANCE_DETAILED",
        "description": "Detailed device performance analysis",
        "category": "performance",
        "requires_auth": True,
        "keywords": ["detailed device", "device breakdown", "device analysis"]
    },
    {
        "action": "ANALYZE_TIME_PERFORMANCE",
        "description": "Analyze time-based performance patterns",
        "category": "performance",
        "requires_auth": True,
        "keywords": ["time", "hourly", "daily", "weekly", "schedule", "when"]
    },
    {
        "action": "ANALYZE_LOCATION_PERFORMANCE",
        "description": "Analyze location-based performance",
        "category": "performance",
        "requires_auth": True,
        "keywords": ["location", "locations", "geographic", "country", "city", "region"]
    },
    {
        "action": "ANALYZE_LANDING_PAGE_MOBILE",
        "description": "Analyze mobile landing page performance",
        "category": "performance",
        "requires_auth": True,
        "keywords": ["mobile landing page", "mobile performance", "mobile site"]
    }
]

# === KEYWORD ANALYSIS ===
KEYWORD_ACTIONS = [
    {
        "action": "ANALYZE_KEYWORD_TRENDS",
        "description": "Analyze keyword performance trends",
        "category": "keywords",
        "requires_auth": True,
        "keywords": ["keyword trends", "trending keywords", "keyword performance"]
    },
    {
        "action": "ANALYZE_AUCTION_INSIGHTS",
        "description": "Analyze auction insights and competition",
        "category": "keywords",
        "requires_auth": True,
        "keywords": ["auction insights", "competition", "competitors", "auction"]
    },
    {
        "action": "ANALYZE_SEARCH_TERMS",
        "description": "Analyze search terms performance",
        "category": "keywords",
        "requires_auth": True,
        "keywords": ["search terms", "queries", "search queries", "actual searches"]
    },
    {
        "action": "SUGGEST_NEGATIVE_KEYWORDS",
        "description": "Negative keyword exclusion suggestions",
        "category": "keywords",
        "requires_auth": True,
        "keywords": ["negative keywords", "exclude", "block", "filter out"]
    }
]

# === COMPETITIVE ANALYSIS ===
COMPETITIVE_ACTIONS = [
    {
        "action": "ANALYZE_COMPETITORS",
        "description": "Analyze competitor performance and strategies",
        "category": "competitive",
        "requires_auth": True,
        "keywords": ["competitors", "competition", "rivals", "other brands"]
    },
    {
        "action": "ANALYZE_ADS_SHOWING_TIME",
        "description": "Analyze when ads are showing and performance",
        "category": "competitive",
        "requires_auth": True,
        "keywords": ["when ads show", "ad schedule", "showing time", "impression share"]
    }
]

# === KNOWLEDGE BASE ===
KNOWLEDGE_BASE_ACTIONS = [
    {
        "action": "SEARCH_KB",
        "description": "Search knowledge base for information",
        "category": "knowledge_base",
        "requires_auth": False,
        "keywords": ["search", "find", "look up", "knowledge", "help", "documentation"]
    },
    {
        "action": "ADD_KB_DOCUMENT",
        "description": "Add documents to knowledge base",
        "category": "knowledge_base",
        "requires_auth": True,
        "keywords": ["add document", "upload", "save", "store", "knowledge base"]
    },
    {
        "action": "SEARCH_DB",
        "description": "Search local database",
        "category": "knowledge_base",
        "requires_auth": True,
        "keywords": ["search database", "query database", "look in database"]
    }
]

# === ANALYTICS ===
ANALYTICS_ACTIONS = [
    {
        "action": "GET_ANALYTICS",
        "description": "Get analytics data and insights",
        "category": "analytics",
        "requires_auth": True,
        "keywords": ["analytics", "data", "insights", "metrics", "reports"]
    }
]

# === FALLBACK ACTIONS ===
FALLBACK_ACTIONS = [
    {
        "action": "QUERY_WITHOUT_SOLUTION",
        "description": "Handle queries that have no solution by prompting user in right direction",
        "category": "fallback",
        "requires_auth": False,
        "keywords": []
    },
    {
        "action": "query_understanding_fallback",
        "description": "Fallback for query understanding errors",
        "category": "fallback",
        "requires_auth": False,
        "keywords": []
    }
]

# === ALL INTENT ACTIONS ===
ALL_INTENT_ACTIONS = (
    BASIC_OPERATIONS + 
    ANALYSIS_ACTIONS + 
    CREATIVE_ACTIONS + 
    OPTIMIZATION_ACTIONS + 
    AUDIENCE_ACTIONS + 
    TECHNICAL_ACTIONS + 
    PERFORMANCE_ACTIONS + 
    KEYWORD_ACTIONS + 
    COMPETITIVE_ACTIONS + 
    KNOWLEDGE_BASE_ACTIONS + 
    ANALYTICS_ACTIONS + 
    FALLBACK_ACTIONS
)

# === ACTION CATEGORIES ===
ACTION_CATEGORIES = {
    "basic_operations": len(BASIC_OPERATIONS),
    "analysis": len(ANALYSIS_ACTIONS),
    "creative": len(CREATIVE_ACTIONS),
    "optimization": len(OPTIMIZATION_ACTIONS),
    "audience": len(AUDIENCE_ACTIONS),
    "technical": len(TECHNICAL_ACTIONS),
    "performance": len(PERFORMANCE_ACTIONS),
    "keywords": len(KEYWORD_ACTIONS),
    "competitive": len(COMPETITIVE_ACTIONS),
    "knowledge_base": len(KNOWLEDGE_BASE_ACTIONS),
    "analytics": len(ANALYTICS_ACTIONS),
    "fallback": len(FALLBACK_ACTIONS)
}

# === TOTAL COUNT ===
TOTAL_ACTIONS = len(ALL_INTENT_ACTIONS)

def get_action_by_name(action_name: str):
    """Get action details by name"""
    for action in ALL_INTENT_ACTIONS:
        if action["action"] == action_name:
            return action
    return None

def get_actions_by_category(category: str):
    """Get all actions in a specific category"""
    return [action for action in ALL_INTENT_ACTIONS if action["category"] == category]

def get_actions_requiring_auth():
    """Get all actions that require authentication"""
    return [action for action in ALL_INTENT_ACTIONS if action["requires_auth"]]

def get_actions_not_requiring_auth():
    """Get all actions that don't require authentication"""
    return [action for action in ALL_INTENT_ACTIONS if not action["requires_auth"]]


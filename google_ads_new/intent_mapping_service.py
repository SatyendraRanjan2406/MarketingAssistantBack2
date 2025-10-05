"""
Intent Mapping Service
Maps user queries to intent actions using OpenAI with date range and filter extraction
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from openai import OpenAI

logger = logging.getLogger(__name__)

@dataclass
class DateRange:
    """Date range extracted from query"""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    period: Optional[str] = None  # 'last_7_days', 'last_30_days', 'this_month', etc.
    description: Optional[str] = None  # Human readable description
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "start_date": self.start_date,
            "end_date": self.end_date,
            "period": self.period,
            "description": self.description
        }

@dataclass
class Filter:
    """Filter extracted from query"""
    field: str
    operator: str  # 'equals', 'contains', 'greater_than', 'less_than', 'in', 'not_in'
    value: Any
    description: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "field": self.field,
            "operator": self.operator,
            "value": self.value,
            "description": self.description
        }

@dataclass
class IntentMappingResult:
    """Result of intent mapping"""
    actions: List[str]
    date_ranges: List[DateRange]  # Changed to array for multiple date ranges
    filters: List[Filter]
    confidence: float
    reasoning: str
    parameters: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "actions": self.actions,
            "date_ranges": [dr.to_dict() for dr in self.date_ranges],  # Array of date ranges
            "filters": [f.to_dict() for f in self.filters],
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "parameters": self.parameters
        }

@dataclass
class IntentDataMappingResult:
    """Result of intent data mapping with multiple action groups"""
    action_groups: List[Dict[str, Any]]  # Array of action groups with actions, date_ranges, and filters
    confidence: float
    reasoning: str
    total_actions: int
    query: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_groups": self.action_groups,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "total_actions": self.total_actions,
            "query": self.query
        }
    
    def get_all_actions(self) -> List[str]:
        """Get all unique actions from all action groups"""
        all_actions = []
        for group in self.action_groups:
            all_actions.extend(group.get('actions', []))
        return list(set(all_actions))  # Remove duplicates
    
    def get_all_date_ranges(self) -> List[str]:
        """Get all unique date ranges from all action groups"""
        all_date_ranges = []
        for group in self.action_groups:
            all_date_ranges.extend(group.get('date_ranges', []))
        return list(set(all_date_ranges))  # Remove duplicates
    
    def get_all_filters(self) -> List[Dict[str, Any]]:
        """Get all filters from all action groups"""
        all_filters = []
        for group in self.action_groups:
            all_filters.extend(group.get('filters', []))
        return all_filters

class IntentMappingService:
    """Service to map user queries to intent actions using OpenAI"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.intent_actions = self._load_intent_actions()
        
    def _load_intent_actions(self) -> List[Dict[str, Any]]:
        """Load the complete list of intent actions"""
        return [
            # === BASIC GOOGLE ADS OPERATIONS ===
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
            },
            {
                "action": "GET_ACCESSIBLE_CUSTOMERS",
                "description": "Get list of accessible Google Ads customer accounts",
                "category": "basic_operations",
                "requires_auth": True,
                "keywords": ["accessible customers", "customer accounts", "accounts", "customers", "list customers", "show customers", "my accounts", "available accounts", "customer list", "accessible accounts"]
            },

            # === ANALYSIS ACTIONS ===
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
            },

            # === AUDIENCE & DEMOGRAPHICS ===
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
            },

            # === CREATIVE ACTIONS ===
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
            },

            # === OPTIMIZATION ACTIONS ===
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
            },

            # === TECHNICAL ANALYSIS ===
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
            },

            # === PERFORMANCE ANALYSIS ===
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
            },

            # === KEYWORD ANALYSIS ===
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
            },

            # === COMPETITIVE ANALYSIS ===
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
            },

            # === KNOWLEDGE BASE ===
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
            },

            # === ANALYTICS ===
            {
                "action": "GET_ANALYTICS",
                "description": "Get analytics data and insights",
                "category": "analytics",
                "requires_auth": True,
                "keywords": ["analytics", "data", "insights", "metrics", "reports"]
            },

            # === FALLBACK ACTIONS ===
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
    
    def map_query_to_intents(self, query: str, user_context: Optional[Dict[str, Any]] = None) -> IntentMappingResult:
        """
        Map user query to intent actions using OpenAI
        
        Args:
            query: User's query string
            user_context: Optional user context (campaigns, account info, etc.)
            
        Returns:
            IntentMappingResult with actions, date range, filters, and confidence
        """
        try:
            # Create the prompt for OpenAI
            prompt = self._create_mapping_prompt(query, user_context)
            
            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert at mapping user queries to Google Ads intent actions and extracting date ranges and filters."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            # Parse the response
            result = self._parse_openai_response(response.choices[0].message.content, query)
            
            logger.info(f"Intent mapping successful for query: '{query}' -> {len(result.actions)} actions")
            return result
            
        except Exception as e:
            logger.error(f"Error in intent mapping: {e}")
            return self._create_fallback_result(query)
    
    def _create_mapping_prompt(self, query: str, user_context: Optional[Dict[str, Any]]) -> str:
        """Create the prompt for OpenAI intent mapping"""
        
        # Build available actions list
        actions_list = []
        for action in self.intent_actions:
            actions_list.append(f"- {action['action']}: {action['description']} (Keywords: {', '.join(action['keywords'])})")
        
        actions_text = "\n".join(actions_list)
        
        prompt = f"""
You are an expert at mapping user queries to Google and Meta  Ads intent actions. Analyze the user query and determine:

1. Which intent actions should be executed (can be multiple)
2. Extract ALL date ranges (start_date, end_date, period) - return as array for multiple ranges
3. Extract ALL filters (field, operator, value) - return as array for multiple filters
4. Provide confidence score and reasoning

Available Intent Actions:
{actions_text}

User Query: "{query}"

User Context: {json.dumps(user_context or {}, indent=2)}

Instructions:
1. Match the query to the most relevant intent actions based on keywords and context
2. Extract ALL date ranges from phrases like:
   - "last 7 days" -> period: "last_7_days"
   - "this month" -> period: "this_month"
   - "from Jan 1 to Jan 31" -> start_date: "2024-01-01", end_date: "2024-01-31"
   - "yesterday" -> start_date: "2024-01-15", end_date: "2024-01-15"
   - "from last week to this week" -> TWO date ranges: last week AND this week
   - "campaigns from Q1 and Q2" -> TWO date ranges: Q1 AND Q2
3. Extract ALL filters from phrases like:
   - "campaigns with status active" -> field: "status", operator: "equals", value: "ACTIVE"
   - "budget greater than $100" -> field: "budget", operator: "greater_than", value: 100
   - "campaigns containing 'summer'" -> field: "name", operator: "contains", value: "summer"
   - "status active AND budget > $100" -> TWO filters: status AND budget
   - "campaigns with status active or paused" -> TWO filters: status=ACTIVE OR status=PAUSED
4. Provide confidence score (0.0 to 1.0)
5. Explain your reasoning
6. If multiple date ranges are mentioned, return them as separate objects in the date_ranges array
7. If multiple filters are mentioned, return them as separate objects in the filters array

Return JSON format:
{{
  "actions": ["ACTION1", "ACTION2"],
  "date_ranges": [
    {{
      "start_date": "2024-01-01",
      "end_date": "2024-01-31",
      "period": "this_month",
      "description": "This month data"
    }},
    {{
      "start_date": "2023-12-01",
      "end_date": "2023-12-31",
      "period": "last_month",
      "description": "Last month data"
    }}
  ],
  "filters": [
    {{
      "field": "status",
      "operator": "equals",
      "value": "ACTIVE",
      "description": "Campaigns with active status"
    }},
    {{
      "field": "budget",
      "operator": "greater_than",
      "value": 100,
      "description": "Campaigns with budget greater than $100"
    }}
  ],
  "confidence": 0.95,
  "reasoning": "Query matches campaign analysis request with multiple date ranges and filters",
  "parameters": {{
    "limit": 50,
    "sort_by": "clicks",
    "order": "desc"
  }}
}}
"""
        return prompt
    
    def _parse_openai_response(self, content: str, original_query: str) -> IntentMappingResult:
        """Parse OpenAI response into IntentMappingResult"""
        try:
            # Extract JSON from response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = content[json_start:json_end]
            data = json.loads(json_str)
            
            # Parse date ranges (now an array)
            date_ranges = []
            date_ranges_data = data.get('date_ranges', [])
            
            # Handle backward compatibility with single date_range
            if not date_ranges_data and 'date_range' in data:
                date_ranges_data = [data['date_range']]
            
            for date_range_data in date_ranges_data:
                date_range = DateRange(
                    start_date=date_range_data.get('start_date'),
                    end_date=date_range_data.get('end_date'),
                    period=date_range_data.get('period'),
                    description=date_range_data.get('description', '')
                )
                date_ranges.append(date_range)
            
            # Parse filters
            filters = []
            for filter_data in data.get('filters', []):
                filter_obj = Filter(
                    field=filter_data.get('field', ''),
                    operator=filter_data.get('operator', 'equals'),
                    value=filter_data.get('value'),
                    description=filter_data.get('description', '')
                )
                filters.append(filter_obj)
            
            # Create result
            result = IntentMappingResult(
                actions=data.get('actions', []),
                date_ranges=date_ranges,
                filters=filters,
                confidence=data.get('confidence', 0.0),
                reasoning=data.get('reasoning', ''),
                parameters=data.get('parameters', {})
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing OpenAI response: {e}")
            return self._create_fallback_result(original_query)
    
    def _create_fallback_result(self, query: str) -> IntentMappingResult:
        """Create fallback result when mapping fails"""
        return IntentMappingResult(
            actions=["QUERY_WITHOUT_SOLUTION"],
            date_ranges=[],
            filters=[],
            confidence=0.1,
            reasoning="Failed to map query to specific actions",
            parameters={}
        )
    
    def extract_date_range_from_query(self, query: str) -> List[DateRange]:
        """Extract date ranges from query using simple pattern matching"""
        query_lower = query.lower()
        date_ranges = []
        
        # Common date patterns
        if "last 7 days" in query_lower or "past week" in query_lower:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            date_ranges.append(DateRange(start_date=start_date, end_date=end_date, period="last_7_days", description="Last 7 days"))
        
        elif "last 30 days" in query_lower or "past month" in query_lower:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            date_ranges.append(DateRange(start_date=start_date, end_date=end_date, period="last_30_days", description="Last 30 days"))
        
        elif "this month" in query_lower:
            now = datetime.now()
            start_date = now.replace(day=1).strftime("%Y-%m-%d")
            end_date = now.strftime("%Y-%m-%d")
            date_ranges.append(DateRange(start_date=start_date, end_date=end_date, period="this_month", description="This month"))
        
        elif "yesterday" in query_lower:
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            date_ranges.append(DateRange(start_date=yesterday, end_date=yesterday, period="yesterday", description="Yesterday"))
        
        elif "today" in query_lower:
            today = datetime.now().strftime("%Y-%m-%d")
            date_ranges.append(DateRange(start_date=today, end_date=today, period="today", description="Today"))
        
        return date_ranges
    
    def get_actions_by_category(self, category: str) -> List[str]:
        """Get all actions in a specific category"""
        return [action['action'] for action in self.intent_actions if action['category'] == category]
    
    def get_action_details(self, action_name: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific action"""
        for action in self.intent_actions:
            if action['action'] == action_name:
                return action
        return None



class IntentMappingToDataService:
    def __init__(self):
            self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            self.intent_actions = self._load_intent_actions()
    
    def _load_intent_actions(self) -> List[Dict[str, Any]]:
        """Load the complete list of intent actions"""
        return [
            # === BASIC GOOGLE ADS OPERATIONS ===
            {
                "action": "GET_OVERVIEW",
                "description": "Get account overview and summary",
                "category": "basic_operations",
                "requires_auth": True,
                "keywords": ["overview", "summary", "account", "dashboard", "home"]
            },
            {
                "action": "GET_CAMPAIGNS",
                "description": "Get campaign data and performance",
                "category": "campaign_management",
                "requires_auth": True,
                "keywords": ["campaigns", "campaign", "campaigns data", "campaign performance"]
            },
            {
                "action": "GET_AD_GROUPS",
                "description": "Get ad group data and performance",
                "category": "campaign_management",
                "requires_auth": True,
                "keywords": ["ad groups", "adgroups", "ad group", "ad groups data"]
            },
            {
                "action": "GET_KEYWORDS",
                "description": "Get keyword data and performance",
                "category": "keyword_management",
                "requires_auth": True,
                "keywords": ["keywords", "keyword", "keyword data", "keyword performance"]
            },
            {
                "action": "GET_ADS",
                "description": "Get ad data and performance",
                "category": "ad_management",
                "requires_auth": True,
                "keywords": ["ads", "ad", "ad data", "ad performance", "creatives"]
            },
            {
                "action": "GET_PERFORMANCE",
                "description": "Get performance metrics and analytics",
                "category": "analytics",
                "requires_auth": True,
                "keywords": ["performance", "metrics", "analytics", "stats", "statistics"]
            }
        ]

    def map_query_to_intents(self,query:str,user_context:Optional[Dict[str,Any]]=None,chat_history:Optional[List[Any]]=None)->IntentDataMappingResult:

            data_mapping_prompt = create_data_mapping_prompt(query , user_context)
  
            # Build messages for OpenAI API
            messages = []
            
            # Add chat history if provided
            if chat_history and len(chat_history) > 1:  # More than just system message
                messages.extend(chat_history)
            else:
                # Use default system message
                messages.append({
                    "role": "system",
                    "content": "You are a Google Ads and Meta Ads account expert assistant. You help users analyze their advertising campaigns and provide insights."
                })
            
            # Add the data mapping prompt as the user message
            messages.append({
                "role": "user",
                "content": data_mapping_prompt
            })
                
            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.3,
                max_tokens=3000
            )
            
            # Parse the response
            result = self._parse_openai_data_mapping_response(response.choices[0].message.content, query)
            
            logger.info(f"Intent mapping successful for query: '{query}' -> {len(result.get_all_actions())} actions")
            return result

    def _parse_openai_data_mapping_response(self, response_content: str, query: str) -> IntentDataMappingResult:
        """
        Parse OpenAI response into IntentDataMappingResult
        
        Expected JSON format:
        [{
            "actions": ["ACTION1"],
            "date_ranges": [DATE_RANGE1, DATE_RANGE2],
            "filters": [{"filter1_name": FILTER1_Value}, {"filter2_name": FILTER2_Value}]
        },
        {
            "actions": ["ACTION2"],
            "date_ranges": [DATE_RANGE1, DATE_RANGE2, DATE_RANGE3],
            "filters": [{"filter1_name": FILTER1_Value}, {"filter2_name": FILTER2_Value}, {"filter3_name": FILTER3_Value}]
        }]
        
        Args:
            response_content: Raw response from OpenAI
            query: Original user query
            
        Returns:
            IntentDataMappingResult with parsed action groups
        """
        try:
            # Clean the response content - remove any markdown formatting
            cleaned_content = response_content.strip()
            if cleaned_content.startswith('```json'):
                cleaned_content = cleaned_content[7:]
            if cleaned_content.endswith('```'):
                cleaned_content = cleaned_content[:-3]
            cleaned_content = cleaned_content.strip()
            
            # Extract JSON from response (handle cases where there's extra text)
            json_start = cleaned_content.find('[')
            json_end = cleaned_content.rfind(']') + 1
            
            if json_start != -1 and json_end > json_start:
                json_content = cleaned_content[json_start:json_end]
            else:
                json_content = cleaned_content
            
            # Parse JSON response
            action_groups = json.loads(json_content)
            
            # Validate that it's a list
            if not isinstance(action_groups, list):
                raise ValueError("Expected response to be a list of action groups")
            
            # Validate each action group
            validated_groups = []
            for group in action_groups:
                if not isinstance(group, dict):
                    logger.warning(f"Skipping invalid action group: {group}")
                    continue
                
                # Ensure required fields exist
                validated_group = {
                    "actions": group.get("actions", []),
                    "date_ranges": group.get("date_ranges", []),
                    "filters": group.get("filters", [])
                }
                
                # Validate actions is a list
                if not isinstance(validated_group["actions"], list):
                    validated_group["actions"] = []
                
                # Validate date_ranges is a list
                if not isinstance(validated_group["date_ranges"], list):
                    validated_group["date_ranges"] = []
                else:
                    # Convert date range objects to strings if needed
                    converted_date_ranges = []
                    for dr in validated_group["date_ranges"]:
                        if isinstance(dr, dict):
                            # Convert date range object to string
                            if "start_date" in dr and "end_date" in dr:
                                converted_date_ranges.append(f"{dr['start_date']} to {dr['end_date']}")
                            elif "period" in dr:
                                converted_date_ranges.append(dr["period"])
                            else:
                                converted_date_ranges.append(str(dr))
                        else:
                            converted_date_ranges.append(str(dr))
                    validated_group["date_ranges"] = converted_date_ranges
                
                # Validate filters is a list
                if not isinstance(validated_group["filters"], list):
                    validated_group["filters"] = []
                
                validated_groups.append(validated_group)
            
            # Calculate total actions
            total_actions = sum(len(group.get("actions", [])) for group in validated_groups)
            
            # Calculate confidence based on response quality
            confidence = self._calculate_confidence(validated_groups, query)
            
            # Generate reasoning
            reasoning = self._generate_reasoning(validated_groups, query)
            
            return IntentDataMappingResult(
                action_groups=validated_groups,
                confidence=confidence,
                reasoning=reasoning,
                total_actions=total_actions,
                query=query
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response content: {response_content}")
            
            # Return fallback result
            return IntentDataMappingResult(
                action_groups=[],
                confidence=0.0,
                reasoning=f"Failed to parse OpenAI response: {str(e)}",
                total_actions=0,
                query=query
            )
            
        except Exception as e:
            logger.error(f"Error parsing OpenAI response: {e}")
            logger.error(f"Response content: {response_content}")
            
            # Return fallback result
            return IntentDataMappingResult(
                action_groups=[],
                confidence=0.0,
                reasoning=f"Error parsing response: {str(e)}",
                total_actions=0,
                query=query
            )
    
    def _calculate_confidence(self, action_groups: List[Dict[str, Any]], query: str) -> float:
        """Calculate confidence score based on response quality"""
        if not action_groups:
            return 0.0
        
        # Base confidence
        confidence = 0.5
        
        # Increase confidence for more action groups (indicates thorough analysis)
        confidence += min(len(action_groups) * 0.1, 0.3)
        
        # Increase confidence for groups with multiple actions
        for group in action_groups:
            actions_count = len(group.get("actions", []))
            if actions_count > 1:
                confidence += 0.1
        
        # Increase confidence for groups with date ranges
        for group in action_groups:
            if group.get("date_ranges"):
                confidence += 0.05
        
        # Increase confidence for groups with filters
        for group in action_groups:
            if group.get("filters"):
                confidence += 0.05
        
        # Cap at 1.0
        return min(confidence, 1.0)
    
    def _generate_reasoning(self, action_groups: List[Dict[str, Any]], query: str) -> str:
        """Generate reasoning for the mapping result"""
        if not action_groups:
            return "No actions could be mapped from the query."
        
        reasoning_parts = []
        
        # Count total actions
        total_actions = sum(len(group.get("actions", [])) for group in action_groups)
        reasoning_parts.append(f"Mapped query to {total_actions} actions across {len(action_groups)} action groups.")
        
        # Describe each action group
        for i, group in enumerate(action_groups, 1):
            actions = group.get("actions", [])
            date_ranges = group.get("date_ranges", [])
            filters = group.get("filters", [])
            
            group_desc = f"Group {i}: {', '.join(actions)}"
            if date_ranges:
                group_desc += f" with date ranges {', '.join(date_ranges)}"
            if filters:
                group_desc += f" with {len(filters)} filters"
            
            reasoning_parts.append(group_desc)
        
        return " ".join(reasoning_parts)



def  create_data_mapping_prompt( query:str,user_context:Optional[Dict[str,Any]]=None)->str:
        """Create the prompt for OpenAI intent mapping"""
        return f"""
        You are an expert at mapping user queries to Google Ads and Meta Ads intent actions and extracting date ranges and filters.
        User query: {query}
        User context: {user_context}

        The intent actions currently available to get data from are:
        GET_CAMPAIGNS, GET_ADS, GET_ADSETS, GET_KEYWORDS - GET_BUDGETS, GET_PERFORMANCE, GET_OVERVIEW , GET_CREATIVES

        Analyse the user query and determine:
        1. Which all intent actions should be executed  out of the available intent actions to get the data. (can be multiple)
        2. Extract ALL date ranges (start_date, end_date, period) - return as array for multiple ranges
        3. Extract ALL filters (field, operator, value) - return as array for multiple filters
        4. Break the query intelligently as one query may break into or map to more than one intent query actions. 
        each intent query action may have multiple date ranges and filters.
        5. Provide confidence score and reasoning
        6. If further analysis is needed to reach output m then add a action "ASK_GPT" which basically asks LLM to resolve given the input 
         and add a prompt in the response.
        6. Return JSON format:
         if result from first n-1 actions is enough and doest need ASK_GPT then return:
         [
            {{
            "actions": ["ACTION1"],
                "date_ranges": ["DATE_RANGE1", "DATE_RANGE2"],
                "filters": [{{"filter1_name":"FILTER1_Value"}}, {{"filter2_name":"FILTER2_Value"}}]
            }},
            {{
            "actions": ["ACTION2"],
                "date_ranges": ["DATE_RANGE1", "DATE_RANGE2","DATE_RANGE3"],
                "filters": [{{"filter1_name":"FILTER1_Value"}}, {{"filter2_name":"FILTER2_Value"}},{{"filter3_name":"FILTER3_Value"}}]
            }}
        ]
        else return:
        [
            {{
                "actions": ["ACTION1"],
                "date_ranges": ["DATE_RANGE1", "DATE_RANGE2"],
                "filters": [{{"filter1_name":"FILTER1_Value"}}, {{"filter2_name":"FILTER2_Value"}}]
            }},
            {{
                "actions": ["ASK_GPT"],
                "date_ranges": [],
                "filters": [],
                "prompt": "PROMPT" 
            }}
    
        ]
            The PROMPT mentioned in the ASK_GPT action is the prompt to be used to by ASK_GPT action to ask LLM to resolve the query. It should be generated in the previous tool executed before ASK_GPT using response from the previous tools executed to complete the action . 
        7. If intent actions are not required to get the data or no intent is suitable then return empty array.
        8. If the query is not clear or not related to the intent actions then return a fallback result.
        """

# Global service instance
_intent_mapping_service = None

_intent_mapping_to_data_service = None




def get_intent_mapping_service():
    """Get the global intent mapping service instance"""
    global _intent_mapping_service
    if _intent_mapping_service is None:
        _intent_mapping_service = IntentMappingService()
    return _intent_mapping_service


def get_intent_mapping_to_data_service():
    """Get the global intent mapping to data service instance"""
    global _intent_mapping_to_data_service
    if _intent_mapping_to_data_service is None:
        _intent_mapping_to_data_service = IntentMappingToDataService()
    return _intent_mapping_to_data_service




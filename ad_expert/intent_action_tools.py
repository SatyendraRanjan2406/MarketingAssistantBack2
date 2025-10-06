# """
# Intent Action Tools for Ad Expert App
# Implements functions for each intent action with date ranges, filters, and ID support
# """

# import logging
# from typing import Dict, List, Any, Optional, Union
# from datetime import datetime, timedelta
# import json

# from .intent_actions_constants import ALL_INTENT_ACTIONS

# logger = logging.getLogger(__name__)

# class IntentActionTools:
#     """Tools for executing intent actions with comprehensive parameter support"""
    
#     def __init__(self, user_id: int = None):
#         self.tools = self._create_tool_definitions()
#         self.user_id = user_id
    
#     def _create_tool_definitions(self) -> List[Dict[str, Any]]:
#         """Create OpenAI tool definitions for all intent actions"""
#         tools = []
        
#         for action in ALL_INTENT_ACTIONS:
#             tool_def = self._create_tool_definition(action)
#             if tool_def:
#                 tools.append(tool_def)
        
#         return tools
    
#     def _create_tool_definition(self, action: Dict[str, Any]) -> Optional[Dict[str, Any]]:
#         """Create tool definition for a specific action"""
#         action_name = action["action"]
#         description = action["description"]
        
#         # Base parameters that all tools support
#         base_properties = {
#             "customer_id": {
#                 "type": "string",
#                 "description": "Google Ads customer ID"
#             },
#             "date_ranges": {
#                 "type": "array",
#                 "items": {
#                     "type": "object",
#                     "properties": {
#                         "start_date": {"type": "string", "format": "date"},
#                         "end_date": {"type": "string", "format": "date"},
#                         "period": {"type": "string", "enum": ["last_7_days", "last_30_days", "this_month", "last_month", "yesterday", "today"]},
#                         "description": {"type": "string"}
#                     }
#                 },
#                 "description": "Date ranges for data retrieval"
#             },
#             "filters": {
#                 "type": "array",
#                 "items": {
#                     "type": "object",
#                     "properties": {
#                         "field": {"type": "string"},
#                         "operator": {"type": "string", "enum": ["equals", "contains", "greater_than", "less_than", "in", "not_in", "between"]},
#                         "value": {"type": "string"},
#                         "description": {"type": "string"}
#                     }
#                 },
#                 "description": "Filters to apply to the data"
#             },
#             "limit": {
#                 "type": "integer",
#                 "description": "Maximum number of results to return",
#                 "default": 50
#             },
#             "sort_by": {
#                 "type": "string",
#                 "description": "Field to sort results by",
#                 "default": "clicks"
#             },
#             "order": {
#                 "type": "string",
#                 "enum": ["asc", "desc"],
#                 "description": "Sort order",
#                 "default": "desc"
#             }
#         }
        
#         # Add specific parameters based on action type
#         specific_properties = self._get_specific_properties(action_name)
#         properties = {**base_properties, **specific_properties}
        
#         return {
#             "type": "function",
#             "function": {
#                 "name": action_name.lower(),
#                 "description": description,
#                 "parameters": {
#                     "type": "object",
#                     "properties": properties,
#                     "required": self._get_required_parameters(action_name)
#                 }
#             }
#         }
    
#     def _get_specific_properties(self, action_name: str) -> Dict[str, Any]:
#         """Get specific properties for each action type"""
#         properties = {}
        
#         # ID-based actions
#         if "BY_ID" in action_name:
#             if "CAMPAIGN" in action_name:
#                 properties["campaign_id"] = {
#                     "type": "string",
#                     "description": "Specific campaign ID"
#                 }
#             elif "AD" in action_name and "GROUP" not in action_name:
#                 properties["ad_id"] = {
#                     "type": "string",
#                     "description": "Specific ad ID"
#                 }
#             elif "ADSET" in action_name or "AD_GROUP" in action_name:
#                 properties["ad_group_id"] = {
#                     "type": "string",
#                     "description": "Specific ad group ID"
#                 }
#             elif "BUDGET" in action_name:
#                 properties["budget_id"] = {
#                     "type": "string",
#                     "description": "Specific budget ID"
#                 }
        
#         # Campaign-related actions
#         if "CAMPAIGN" in action_name:
#             properties["campaign_ids"] = {
#                 "type": "array",
#                 "items": {"type": "string"},
#                 "description": "List of campaign IDs"
#             }
        
#         # Ad group-related actions
#         if "ADSET" in action_name or "AD_GROUP" in action_name:
#             properties["ad_group_ids"] = {
#                 "type": "array",
#                 "items": {"type": "string"},
#                 "description": "List of ad group IDs"
#             }
        
#         # Ad-related actions
#         if "AD" in action_name and "GROUP" not in action_name:
#             properties["ad_ids"] = {
#                 "type": "array",
#                 "items": {"type": "string"},
#                 "description": "List of ad IDs"
#             }
        
#         # Budget-related actions
#         if "BUDGET" in action_name:
#             properties["budget_ids"] = {
#                 "type": "array",
#                 "items": {"type": "string"}, 
#                 "description": "List of budget IDs"
#             }
        
#         # Analysis actions
#         if action_name in ["CAMPAIGN_SUMMARY_COMPARISON", "COMPARE_PERFORMANCE"]:
#             properties["comparison_metrics"] = {
#                 "type": "array",
#                 "items": {"type": "string"},
#                 "description": "Metrics to compare (clicks, impressions, cost, etc.)"
#             }
#             properties["group_by"] = {
#                 "type": "string",
#                 "description": "Group results by (campaign, ad_group, ad, etc.)"
#             }
        
#         # Creative actions
#         if action_name in ["GENERATE_AD_COPIES", "GENERATE_CREATIVES", "GENERATE_IMAGES"]:
#             properties["theme"] = {
#                 "type": "string",
#                 "description": "Theme or topic for creative generation"
#             }
#             properties["tone"] = {
#                 "type": "string",
#                 "description": "Tone of voice for creatives"
#             }
#             properties["count"] = {
#                 "type": "integer",
#                 "description": "Number of variations to generate",
#                 "default": 3
#             }
        
#         # Optimization actions
#         if "OPTIMIZE" in action_name:
#             properties["optimization_goal"] = {
#                 "type": "string",
#                 "description": "Optimization goal (clicks, conversions, cost, etc.)"
#             }
#             properties["budget_constraint"] = {
#                 "type": "number",
#                 "description": "Budget constraint for optimization"
#             }
        
#         return properties
    
#     def _get_required_parameters(self, action_name: str) -> List[str]:
#         """Get required parameters for each action"""
#         required = ["customer_id"]
        
#         # ID-based actions require specific ID
#         if "BY_ID" in action_name:
#             if "CAMPAIGN" in action_name:
#                 required.append("campaign_id")
#             elif "AD" in action_name and "GROUP" not in action_name:
#                 required.append("ad_id")
#             elif "ADSET" in action_name or "AD_GROUP" in action_name:
#                 required.append("ad_group_id")
#             elif "BUDGET" in action_name:
#                 required.append("budget_id")
        
#         # Creative actions require theme
#         if action_name in ["GENERATE_AD_COPIES", "GENERATE_CREATIVES", "GENERATE_IMAGES"]:
#             required.append("theme")
        
#         return required
    
#     async def execute_action(self, action_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         """Execute an intent action with given parameters"""
#         try:
#             # Get the action definition
#             action_def = next((a for a in ALL_INTENT_ACTIONS if a["action"] == action_name), None)
#             if not action_def:
#                 return {
#                     "success": False,
#                     "error": f"Action '{action_name}' not found"
#                 }
            
#             # Execute the specific action
#             if action_name.startswith("GET_"):
#                 return await self._execute_get_action(action_name, parameters)
#             elif action_name.startswith("CREATE_"):
#                 return self._execute_create_action(action_name, parameters)
#             elif action_name.startswith("ANALYZE_"):
#                 return self._execute_analyze_action(action_name, parameters)
#             elif action_name.startswith("OPTIMIZE_"):
#                 return self._execute_optimize_action(action_name, parameters)
#             elif action_name.startswith("GENERATE_"):
#                 return self._execute_generate_action(action_name, parameters)
#             elif action_name.startswith("CHECK_"):
#                 return self._execute_check_action(action_name, parameters)
#             elif action_name.startswith("PAUSE_") or action_name.startswith("RESUME_"):
#                 return self._execute_control_action(action_name, parameters)
#             else:
#                 return self._execute_fallback_action(action_name, parameters)
                
#         except Exception as e:
#             logger.error(f"Error executing action {action_name}: {e}")
#             return {
#                 "success": False,
#                 "error": str(e)
#             }
    
#     async def _execute_get_action(self, action_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         """Execute GET actions"""
#         customer_id = parameters.get("customer_id")
#         date_ranges = parameters.get("date_ranges", [])
#         filters = parameters.get("filters", [])
#         limit = parameters.get("limit", 50)
#         sort_by = parameters.get("sort_by", "clicks")
#         order = parameters.get("order", "desc")
        
#         # Build query parameters
#         query_params = {
#             "customer_id": customer_id,
#             "date_ranges": date_ranges,
#             "filters": filters,
#             "limit": limit,
#             "sort_by": sort_by,
#             "order": order
#         }
        
#         # Add specific ID parameters
#         if "BY_ID" in action_name:
#             if "CAMPAIGN" in action_name:
#                 query_params["campaign_id"] = parameters.get("campaign_id")
#             elif "AD" in action_name and "GROUP" not in action_name:
#                 query_params["ad_id"] = parameters.get("ad_id")
#             elif "ADSET" in action_name or "AD_GROUP" in action_name:
#                 query_params["ad_group_id"] = parameters.get("ad_group_id")
#             elif "BUDGET" in action_name:
#                 query_params["budget_id"] = parameters.get("budget_id")
        
#         # Add list parameters
#         if "CAMPAIGN" in action_name:
#             query_params["campaign_ids"] = parameters.get("campaign_ids", [])
#         if "ADSET" in action_name or "AD_GROUP" in action_name:
#             query_params["ad_group_ids"] = parameters.get("ad_group_ids", [])
#         if "AD" in action_name and "GROUP" not in action_name:
#             query_params["ad_ids"] = parameters.get("ad_ids", [])
#         if "BUDGET" in action_name:
#             query_params["budget_ids"] = parameters.get("budget_ids", [])
        
#         # Real Google Ads API call with RAG enhancement and ChatGPT analysis
#         return await self._execute_real_data_retrieval(action_name, query_params, user_id=getattr(self, 'user_id', None))
    
#     def _execute_create_action(self, action_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         """Execute CREATE actions"""
#         customer_id = parameters.get("customer_id")
        
#         # Simulate creation (replace with actual Google Ads API calls)
#         return {
#             "success": True,
#             "action": action_name,
#             "message": f"Successfully created {action_name.replace('CREATE_', '').lower()}",
#             "created_id": f"generated_{action_name.lower()}_id",
#             "parameters": parameters,
#             "timestamp": datetime.now().isoformat()
#         }
    
#     def _execute_analyze_action(self, action_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         """Execute ANALYZE actions"""
#         customer_id = parameters.get("customer_id")
#         date_ranges = parameters.get("date_ranges", [])
#         filters = parameters.get("filters", [])
        
#         # Simulate analysis (replace with actual analysis logic)
#         return {
#             "success": True,
#             "action": action_name,
#             "analysis": self._simulate_analysis(action_name, parameters),
#             "insights": self._generate_insights(action_name, parameters),
#             "parameters": parameters,
#             "timestamp": datetime.now().isoformat()
#         }
    
#     def _execute_optimize_action(self, action_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         """Execute OPTIMIZE actions"""
#         customer_id = parameters.get("customer_id")
#         optimization_goal = parameters.get("optimization_goal", "clicks")
        
#         # Simulate optimization (replace with actual optimization logic)
#         return {
#             "success": True,
#             "action": action_name,
#             "optimization": self._simulate_optimization(action_name, parameters),
#             "recommendations": self._generate_recommendations(action_name, parameters),
#             "parameters": parameters,
#             "timestamp": datetime.now().isoformat()
#         }
    
#     def _execute_generate_action(self, action_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         """Execute GENERATE actions"""
#         theme = parameters.get("theme", "general")
#         tone = parameters.get("tone", "professional")
#         count = parameters.get("count", 3)
        
#         # Simulate generation (replace with actual AI generation)
#         return {
#             "success": True,
#             "action": action_name,
#             "generated_content": self._simulate_content_generation(action_name, theme, tone, count),
#             "parameters": parameters,
#             "timestamp": datetime.now().isoformat()
#         }
    
#     def _execute_check_action(self, action_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         """Execute CHECK actions"""
#         customer_id = parameters.get("customer_id")
        
#         # Simulate check (replace with actual compliance checking)
#         return {
#             "success": True,
#             "action": action_name,
#             "check_results": self._simulate_compliance_check(action_name, parameters),
#             "issues": self._identify_issues(action_name, parameters),
#             "recommendations": self._generate_fix_recommendations(action_name, parameters),
#             "parameters": parameters,
#             "timestamp": datetime.now().isoformat()
#         }
    
#     def _execute_control_action(self, action_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         """Execute PAUSE/RESUME actions"""
#         customer_id = parameters.get("customer_id")
#         action_type = "pause" if "PAUSE" in action_name else "resume"
        
#         # Simulate control action (replace with actual Google Ads API calls)
#         return {
#             "success": True,
#             "action": action_name,
#             "message": f"Successfully {action_type}d campaigns",
#             "affected_campaigns": parameters.get("campaign_ids", []),
#             "parameters": parameters,
#             "timestamp": datetime.now().isoformat()
#         }
    
#     def _execute_fallback_action(self, action_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         """Execute fallback actions"""
#         return {
#             "success": True,
#             "action": action_name,
#             "message": f"Executed {action_name} action",
#             "parameters": parameters,
#             "timestamp": datetime.now().isoformat()
#         }
    
#     async def _execute_real_data_retrieval(self, action_name: str, query_params: Dict[str, Any], user_id: int = None) -> Dict[str, Any]:
#         """
#         Execute real Google Ads API calls with RAG enhancement and ChatGPT analysis
#         """
#         try:
#             customer_id = query_params.get("customer_id")
#             if not customer_id:
#                 return {
#                     "success": False,
#                     "error": "Customer ID is required for data retrieval",
#                     "action": action_name,
#                     "timestamp": datetime.now().isoformat()
#                 }
            
#             # Step 1: Fetch real data from Google Ads API
#             raw_data = await self._fetch_real_google_ads_data(action_name, query_params, user_id)
            
#             if not raw_data.get("success", False):
#                 return raw_data
            
#             # Step 2: Enhance data with RAG context
#             rag_enhanced_data = self._enhance_with_rag(raw_data["data"], action_name, query_params, user_id)
            
#             # Step 3: Generate comprehensive analysis with ChatGPT
#             analysis_result = self._generate_chatgpt_analysis(raw_data["data"], rag_enhanced_data, action_name, query_params)
            
#             return {
#                 "success": True,
#                 "action": action_name,
#                 "raw_data": raw_data["data"],
#                 "rag_enhanced_data": rag_enhanced_data,
#                 "analysis": analysis_result,
#                 "parameters": query_params,
#                 "timestamp": datetime.now().isoformat()
#             }
            
#         except Exception as e:
#             logger.error(f"Error in real data retrieval: {e}")
#             return {
#                 "success": False,
#                 "error": f"Data retrieval failed: {str(e)}",
#                 "action": action_name,
#                 "timestamp": datetime.now().isoformat()
#             }
    
#     async def _fetch_real_google_ads_data(self, action_name: str, query_params: Dict[str, Any], user_id: int = None) -> Dict[str, Any]:
#         """Fetch real data from Google Ads API"""
#         try:
#             customer_id = query_params.get("customer_id")
            
#             # Import Google Ads API service
#             import sys
#             import os
#             sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
#             from google_ads_new.google_ads_api_service import GoogleAdsAPIService
            
#             # Create API service instance with user_id
#             # Note: Using a simplified approach since GoogleAdsAPIService has dependency issues
#             api_service = self._create_simplified_api_service(user_id, customer_id)
            
#             # Determine date range
#             start_date, end_date = self._get_date_range(query_params)
            
#             # Extract additional parameters
#             filters = query_params.get("filters", [])
#             limit = query_params.get("limit", 50)
#             sort_by = query_params.get("sort_by", "clicks")
#             order = query_params.get("order", "desc")
            
#             # Fetch data based on action type
#             if "CAMPAIGN" in action_name:
#                 if "ADSET" in action_name or "AD_GROUP" in action_name:
#                     # Get ad groups for campaigns
#                     campaign_id = query_params.get("campaign_id") or (query_params.get("campaign_ids", [None])[0] if query_params.get("campaign_ids") else None)
#                     data = api_service.get_ad_groups(customer_id, campaign_id, filters, limit, sort_by, order)
#                 else:
#                     # Get campaigns - now async
#                     data = await api_service.get_campaigns(customer_id, filters, limit, sort_by, order)
#             elif "KEYWORD" in action_name:
#                 # Get keywords
#                 ad_group_id = query_params.get("ad_group_id") or (query_params.get("ad_group_ids", [None])[0] if query_params.get("ad_group_ids") else None)
#                 data = api_service.get_keywords(customer_id, ad_group_id, filters, limit, sort_by, order)
#             elif "PERFORMANCE" in action_name or "METRICS" in action_name:
#                 # Get performance data
#                 data = api_service.get_performance_data(customer_id, start_date, end_date, filters, limit, sort_by, order)
#             else:
#                 # Default to performance data
#                 data = api_service.get_performance_data(customer_id, start_date, end_date, filters, limit, sort_by, order)
            
#             return {
#                 "success": True,
#                 "data": data,
#                 "data_type": action_name,
#                 "customer_id": customer_id
#             }
            
#         except Exception as e:
#             logger.error(f"Error fetching Google Ads data: {e}")
#             return {
#                 "success": False,
#                 "error": f"Failed to fetch data from Google Ads API: {str(e)}"
#             }
    
#     def _enhance_with_rag(self, raw_data: List[Dict], action_name: str, query_params: Dict[str, Any], user_id: int = None) -> Dict[str, Any]:
#         """Enhance raw data with RAG context"""
#         try:
#             # Import RAG service
#             import sys
#             import os
#             sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
#             # Try to import RAG service, but handle missing dependencies gracefully
#             try:
#                 # Use Qdrant-based RAG service instead of Chroma-based - COMMENTED OUT
#                 # rag_context = self._get_qdrant_rag_context(action_name, raw_data, query_params)
#                 rag_context = {"context": "RAG context not available - Qdrant disabled"}
                
#                 return {
#                     "rag_context": rag_context.get("context", "No relevant context found"),
#                     "use_rag": rag_context.get("use_rag", False),
#                     "context_query": self._build_rag_query(action_name, raw_data, query_params),
#                     "enhanced_insights": self._extract_rag_insights(rag_context.get("context", ""), action_name)
#                 }
                
#             except Exception as rag_error:
#                 logger.warning(f"RAG service error: {rag_error}")
#                 return {
#                     "rag_context": "RAG service error - using basic context",
#                     "use_rag": False,
#                     "context_query": self._build_rag_query(action_name, raw_data, query_params),
#                     "enhanced_insights": ["RAG service error"]
#                 }
            
#         except Exception as e:
#             logger.error(f"Error enhancing with RAG: {e}")
#             return {
#                 "rag_context": "RAG enhancement failed",
#                 "use_rag": False,
#                 "error": str(e)
#             }
    
#     def _generate_chatgpt_analysis(self, raw_data: List[Dict], rag_data: Dict[str, Any], action_name: str, query_params: Dict[str, Any]) -> Dict[str, Any]:
#         """Generate comprehensive analysis using ChatGPT"""
#         try:
#             # Import OpenAI service
#             import sys
#             import os
#             sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
#             from google_ads_new.openai_service import GoogleAdsOpenAIService
            
#             # Create OpenAI service instance
#             openai_service = GoogleAdsOpenAIService()
            
#             # Build comprehensive prompt with raw data and RAG context
#             analysis_prompt = self._build_analysis_prompt(raw_data, rag_data, action_name, query_params)
            
#             # Generate analysis using ChatGPT
#             analysis_result = openai_service.generate_analysis_response(
#                 action=action_name,
#                 data={
#                     "raw_data": raw_data,
#                     "rag_context": rag_data.get("rag_context", ""),
#                     "query_params": query_params
#                 },
#                 user_context=analysis_prompt
#             )
            
#             return analysis_result
            
#         except Exception as e:
#             logger.error(f"Error generating ChatGPT analysis: {e}")
#             return {
#                 "error": f"Analysis generation failed: {str(e)}",
#                 "fallback_summary": f"Analysis for {action_name} with {len(raw_data)} data points",
#                 "response_type": "error"
#             }
    
#     def _get_date_range(self, query_params: Dict[str, Any]) -> tuple:
#         """Extract date range from query parameters"""
#         date_ranges = query_params.get("date_ranges", [])
        
#         if date_ranges:
#             date_range = date_ranges[0]  # Use first date range
#             if isinstance(date_range, dict):
#                 start_date = date_range.get("start_date")
#                 end_date = date_range.get("end_date")
#                 period = date_range.get("period")
                
#                 if period == "last_week":
#                     from datetime import timedelta
#                     end_date = datetime.now().strftime('%Y-%m-%d')
#                     start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
#                 elif period == "last_30_days":
#                     from datetime import timedelta
#                     end_date = datetime.now().strftime('%Y-%m-%d')
#                     start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
#                 elif not start_date or not end_date:
#                     # Default to last 14 days
#                     from datetime import timedelta
#                     end_date = datetime.now().strftime('%Y-%m-%d')
#                     start_date = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
#             else:
#                 # Default to last 14 days
#                 from datetime import timedelta
#                 end_date = datetime.now().strftime('%Y-%m-%d')
#                 start_date = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
#         else:
#             # Default to last 14 days
#             from datetime import timedelta
#             end_date = datetime.now().strftime('%Y-%m-%d')
#             start_date = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
        
#         return start_date, end_date
    
#     def _build_rag_query(self, action_name: str, raw_data: List[Dict], query_params: Dict[str, Any]) -> str:
#         """Build RAG query based on action and data"""
#         # Create more specific queries that match our sample data
#         if "CAMPAIGN" in action_name:
#             if "ADSET" in action_name or "AD_GROUP" in action_name:
#                 base_query = "Google Ads ad groups contain ads and keywords organization"
#             else:
#                 base_query = "Google Ads campaigns foundation advertising strategy budget settings targeting"
#         elif "KEYWORD" in action_name:
#             base_query = "Google Ads keywords words phrases trigger ads show relevant high-intent"
#         elif "PERFORMANCE" in action_name or "METRICS" in action_name:
#             base_query = "Google Ads performance metrics CTR CPC conversion rate ROAS monitor optimize"
#         else:
#             base_query = f"Google Ads {action_name.replace('GET_', '').replace('_', ' ').lower()}"
        
#         # Add context based on data
#         if raw_data:
#             data_summary = f" with {len(raw_data)} records"
#             if "campaign" in action_name.lower():
#                 data_summary += f", including campaigns like {raw_data[0].get('campaign_name', 'N/A') if raw_data else 'N/A'}"
#             base_query += data_summary
        
#         # Add date context
#         date_ranges = query_params.get("date_ranges", [])
#         if date_ranges:
#             period = date_ranges[0].get("period", "") if isinstance(date_ranges[0], dict) else ""
#             if period:
#                 base_query += f" for {period.replace('_', ' ')}"
        
#         return base_query
    
#     def _extract_rag_insights(self, rag_context: str, action_name: str) -> List[str]:
#         """Extract insights from RAG context"""
#         if not rag_context or rag_context == "No relevant context found":
#             return []
        
#         # Simple extraction - in a real implementation, this would be more sophisticated
#         insights = []
#         if "best practice" in rag_context.lower():
#             insights.append("RAG suggests following Google Ads best practices")
#         if "optimization" in rag_context.lower():
#             insights.append("RAG recommends optimization strategies")
#         if "performance" in rag_context.lower():
#             insights.append("RAG provides performance improvement guidance")
        
#         return insights
    
#     def _build_analysis_prompt(self, raw_data: List[Dict], rag_data: Dict[str, Any], action_name: str, query_params: Dict[str, Any]) -> str:
#         """Build comprehensive analysis prompt for ChatGPT"""
#         prompt = f"""
#         Analyze the following Google Ads data for action: {action_name}
        
#         Raw Data Summary:
#         - Number of records: {len(raw_data)}
#         - Data type: {action_name}
#         - Customer ID: {query_params.get('customer_id', 'N/A')}
        
#         RAG Context:
#         {rag_data.get('rag_context', 'No additional context available')}
        
#         Please provide:
#         1. Executive summary of the data
#         2. Key performance indicators and trends
#         3. Specific insights and recommendations
#         4. Actionable next steps
#         5. Potential optimization opportunities
        
#         Format the response as structured JSON with multiple UI blocks including charts, tables, and action items.
#         """
        
#         return prompt
    
#     # COMMENTED OUT - Qdrant not used in core functionality
#     def _get_qdrant_rag_context(self, action_name: str, raw_data: List[Dict], query_params: Dict[str, Any]) -> Dict[str, Any]:
#         """Get RAG context using Qdrant directly - COMMENTED OUT"""
#         return {
#             "context": "RAG context not available - Qdrant disabled",
#             "use_rag": False,
#             "sources": []
#         }
    
#     # COMMENTED OUT - Original Qdrant implementation (entire method commented out)
#     # def _get_qdrant_rag_context_original(self, action_name: str, raw_data: List[Dict], query_params: Dict[str, Any]) -> Dict[str, Any]:
#     #     """Get RAG context using Qdrant directly"""
#     #     # [ENTIRE METHOD COMMENTED OUT - Qdrant not used in core functionality]
#     #     pass
    
#     # COMMENTED OUT - Qdrant not used in core functionality
#     def _add_sample_rag_data(self, client, openai_client):
#         """Add sample Google Ads documentation to RAG collection - COMMENTED OUT"""
#         pass
    
#     # COMMENTED OUT - Original Qdrant implementation (entire method commented out)
#     # def _add_sample_rag_data_original(self, client, openai_client):
#     #     """Add sample Google Ads documentation to RAG collection"""
#     #     # [ENTIRE METHOD COMMENTED OUT - Qdrant not used in core functionality]
#     #     pass
    
#     def _create_simplified_api_service(self, user_id: int, customer_id: str):
#         """Create a simplified API service that works with existing OAuth setup"""
#         try:
#             # Import the existing API tools from ad_expert
#             from .api_tools import GoogleAdsAPITool
            
#             # Create the API tool instance
#             api_tool = GoogleAdsAPITool()
            
#             # Return a simplified service object with GAQL queries
#             class SimplifiedAPIService:
#                 def __init__(self, api_tool, customer_id, user_id):
#                     self.api_tool = api_tool
#                     self.customer_id = customer_id
#                     self.user_id = user_id
#                     self._google_ads_client = None
                
#                 def _get_google_ads_client(self):
#                     """Get Google Ads client with OAuth authentication"""
#                     if self._google_ads_client:
#                         return self._google_ads_client
#                 points=points
#             )
#             logger.info(f"Added {len(points)} sample documents to RAG collection")
            
#         except Exception as e:
#             logger.warning(f"Failed to add sample RAG data: {e}")
    
#     def _create_simplified_api_service(self, user_id: int, customer_id: str):
#         """Create a simplified API service that works with existing OAuth setup"""
#         try:
#             # Import the existing API tools from ad_expert
#             from .api_tools import GoogleAdsAPITool
            
#             # Create the API tool instance
#             api_tool = GoogleAdsAPITool()
            
#             # Return a simplified service object with GAQL queries
#             class SimplifiedAPIService:
#                 def __init__(self, api_tool, customer_id, user_id):
#                     self.api_tool = api_tool
#                     self.customer_id = customer_id
#                     self.user_id = user_id
#                     self._google_ads_client = None
                
#                 def _get_google_ads_client(self):
#                     """Get Google Ads client with OAuth authentication"""
#                     if self._google_ads_client:
#                         return self._google_ads_client
                    
#                     try:
#                         # Import Google Ads client
#                         from google.ads.googleads.client import GoogleAdsClient
                        
#                         # Import required modules
#                         from accounts.models import UserGoogleAuth
#                         import os
                        
#                         # Get user's OAuth tokens directly from database
#                         try:
#                             user_auth = UserGoogleAuth.objects.filter(
#                                 user_id=self.user_id,
#                                 is_active=True
#                             ).first()
                            
#                             if not user_auth:
#                                 logger.warning(f"No OAuth authentication found for user {self.user_id}")
#                                 return None
                            
#                             if not user_auth.refresh_token:
#                                 logger.warning(f"No refresh token found for user {self.user_id}")
#                                 return None
                                
#                         except Exception as auth_error:
#                             logger.error(f"Error accessing OAuth data: {auth_error}")
#                             return None
                        
#                         # Create Google Ads client configuration with environment variables
#                         config = {
#                             'developer_token': os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN', 'YOUR_DEVELOPER_TOKEN'),
#                             'client_id': os.getenv('GOOGLE_ADS_CLIENT_ID', 'YOUR_CLIENT_ID'),
#                             'client_secret': os.getenv('GOOGLE_ADS_CLIENT_SECRET', 'YOUR_CLIENT_SECRET'),
#                             'refresh_token': user_auth.refresh_token,
#                             'use_proto_plus': True
#                         }
                        
#                         # Validate configuration
#                         required_fields = ['developer_token', 'client_id', 'client_secret', 'refresh_token']
#                         missing_fields = [field for field in required_fields if not config.get(field) or config[field].startswith('YOUR_')]
                        
#                         if missing_fields:
#                             logger.warning(f"Missing or invalid Google Ads configuration: {missing_fields}")
#                             logger.info("Please set the following environment variables:")
#                             logger.info("- GOOGLE_ADS_DEVELOPER_TOKEN")
#                             logger.info("- GOOGLE_ADS_CLIENT_ID") 
#                             logger.info("- GOOGLE_ADS_CLIENT_SECRET")
#                             return None
                        
#                         self._google_ads_client = GoogleAdsClient.load_from_dict(config)
#                         return self._google_ads_client
                        
#                     except Exception as e:
#                         logger.error(f"Error creating Google Ads client: {e}")
#                         return None
                
#                 async def _get_access_token(self):
#                     """Get OAuth access token for REST API calls"""
#                     try:
#                         from accounts.google_oauth_service import UserGoogleAuthService
#                         from django.contrib.auth.models import User
#                         from asgiref.sync import sync_to_async
                        
#                         # Get user object using sync_to_async
#                         user = await sync_to_async(User.objects.get)(id=self.user_id)
                        
#                         # Get valid access token using sync_to_async
#                         access_token = await sync_to_async(UserGoogleAuthService.get_or_refresh_valid_token)(user)
#                         return access_token
                        
#                     except Exception as e:
#                         logger.error(f"Error getting access token: {e}")
#                         return None
                
#                 async def _execute_google_ads_search(self, customer_id, query, access_token):
#                     """Execute Google Ads search using REST API"""
#                     try:
#                         import requests
#                         import os
#                         import asyncio
                        
#                         # Prepare the request
#                         url = f"https://googleads.googleapis.com/v21/customers/{customer_id}/googleAds:search"
                        
#                         headers = {
#                             'Authorization': f'Bearer {access_token}',
#                             'Content-Type': 'application/json',
#                             'developer-token': os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN'),
#                             'login-customer-id': os.getenv('GOOGLE_ADS_LOGIN_CUSTOMER_ID', '9762343117')
#                         }
                        
#                         data = {
#                             'query': query
#                         }
                        
#                         # Make the API request in a thread pool to avoid blocking
#                         loop = asyncio.get_event_loop()
#                         response = await loop.run_in_executor(
#                             None, 
#                             lambda: requests.post(url, headers=headers, json=data)
#                         )
#                         response.raise_for_status()
                        
#                         result_data = response.json()
#                         results = result_data.get('results', [])
                        
#                         # Format results for consistency with existing structure
#                         campaigns = []
#                         for result in results:
#                             campaign_data = self._format_campaign_result(result)
#                             campaigns.append(campaign_data)
                        
#                         return campaigns
                        
#                     except requests.exceptions.RequestException as e:
#                         logger.error(f"Google Ads API request error: {str(e)}")
#                         return []
#                     except Exception as e:
#                         logger.error(f"Error executing Google Ads search: {e}")
#                     return []
                
#                 def _format_campaign_result(self, result):
#                     """Format Google Ads API result into campaign data structure"""
#                     formatted = {}
                    
#                     # Extract campaign data
#                     if 'campaign' in result:
#                         campaign = result['campaign']
#                         formatted.update({
#                             'campaign_id': campaign.get('id'),
#                             'campaign_name': campaign.get('name'),
#                             'status': campaign.get('status'),
#                             'advertising_channel_type': campaign.get('advertisingChannelType'),
#                             'start_date': campaign.get('startDate'),
#                             'end_date': campaign.get('endDate'),
#                             'budget_amount': None,  # Not available in basic campaign query
#                             'target_cpa': None,     # Not available in basic campaign query
#                             'target_roas': None,    # Not available in basic campaign query
#                             'created_at': None,     # Not available in basic campaign query
#                             'updated_at': None      # Not available in basic campaign query
#                         })
                    
#                     # Extract metrics data if present
#                     if 'metrics' in result:
#                         metrics = result['metrics']
                        
#                         # Safely convert to numbers
#                         impressions = int(metrics.get('impressions', 0)) if metrics.get('impressions') else 0
#                         clicks = int(metrics.get('clicks', 0)) if metrics.get('clicks') else 0
#                         conversions = int(metrics.get('conversions', 0)) if metrics.get('conversions') else 0
#                         cost_micros = int(metrics.get('costMicros', 0)) if metrics.get('costMicros') else 0
                        
#                         formatted.update({
#                             'impressions': impressions,
#                             'clicks': clicks,
#                             'ctr': float(metrics.get('ctr', 0)) if metrics.get('ctr') else 0,
#                             'conversions': conversions,
#                             'cost_micros': cost_micros,
#                             'cost': cost_micros / 1000000 if cost_micros else 0,
#                             'average_cpc': float(metrics.get('averageCpc', 0)) if metrics.get('averageCpc') else 0,
#                             'average_cpm': float(metrics.get('averageCpm', 0)) if metrics.get('averageCpm') else 0,
#                             'conversion_rate': (conversions / clicks) if clicks > 0 else 0
#                         })
                    
#                     # Extract segments data if present
#                     if 'segments' in result:
#                         segments = result['segments']
#                         formatted.update({
#                             'date': segments.get('date'),
#                             'device': segments.get('device'),
#                             'network': segments.get('network'),
#                             'ad_network_type': segments.get('adNetworkType')
#                         })
                    
#                     return formatted
                
#                 async def get_campaigns(self, customer_id, filters=None, limit=50, sort_by="name", order="asc"):
#                     """Get campaigns using Google Ads REST API with filters and state"""
#                     try:
#                         # Get OAuth access token
#                         access_token = await self._get_access_token()
#                         if not access_token:
#                             logger.warning(f"No OAuth access token available for user {self.user_id}")
#                             return []
                
#                         # Build GAQL query
#                         query = self._build_campaigns_gaql_query(filters, limit, sort_by, order)
                        
#                         # Execute REST API call
#                         campaigns = await self._execute_google_ads_search(customer_id, query, access_token)
                        
#                         logger.info(f"Retrieved {len(campaigns)} campaigns for customer {customer_id}")
#                         return campaigns
#                     except Exception as e:
#                         logger.error(f"Error fetching campaigns: {e}")
#                     return []
                
#                 def get_ad_groups(self, customer_id, campaign_id=None, filters=None, limit=50, sort_by="clicks", order="desc"):
#                     """Get ad groups using GAQL with filters and state"""
#                     try:
#                         client = self._get_google_ads_client()
#                         if not client:
#                             logger.warning("Google Ads client not available - returning empty ad groups data")
#                             return []
            
#                         # Build GAQL query
#                         query = self._build_ad_groups_gaql_query(campaign_id, filters, limit, sort_by, order)
                        
#                         # Execute query
#                         ga_service = client.get_service("GoogleAdsService")
#                         response = ga_service.search(customer_id=customer_id, query=query)
                        
#                         ad_groups = []
#                         for row in response:
#                             ad_group = row.ad_group
#                             campaigns = row.campaign
#                             ad_groups.append({
#                                 'ad_group_id': ad_group.id,
#                                 'ad_group_name': ad_group.name,
#                                 'status': ad_group.status.name,
#                                 'campaign_id': campaigns.id,
#                                 'campaign_name': campaigns.name,
#                                 'type': ad_group.type_.name,
#                                 'cpc_bid_micros': ad_group.cpc_bid_micros / 1000000 if ad_group.cpc_bid_micros else None,
#                                 'created_at': None,  # Not available in basic ad group query
#                                 'updated_at': None   # Not available in basic ad group query
#                             })
                        
#                         logger.info(f"Retrieved {len(ad_groups)} ad groups for customer {customer_id}")
#                         return ad_groups
                        
#                     except Exception as e:
#                         logger.error(f"Error fetching ad groups: {e}")
#                         return []
            
#                 def get_keywords(self, customer_id, ad_group_id=None, filters=None, limit=50, sort_by="clicks", order="desc"):
#                     """Get keywords using GAQL with filters and state"""
#                     try:
#                         client = self._get_google_ads_client()
#                         if not client:
#                             logger.warning("Google Ads client not available - returning empty keywords data")
#                             return []
                        
#                         # Build GAQL query
#                         query = self._build_keywords_gaql_query(ad_group_id, filters, limit, sort_by, order)
                        
#                         # Execute query
#                         ga_service = client.get_service("GoogleAdsService")
#                         response = ga_service.search(customer_id=customer_id, query=query)
                        
#                         keywords = []
#                         for row in response:
#                             ad_group_criterion = row.ad_group_criterion
#                             ad_group = row.ad_group
#                             campaigns = row.campaign
#                             keywords.append({
#                                 'keyword_id': ad_group_criterion.criterion_id,
#                                 'keyword_text': ad_group_criterion.keyword.text,
#                                 'match_type': ad_group_criterion.keyword.match_type.name,
#                                 'status': ad_group_criterion.status.name,
#                                 'ad_group_id': ad_group.id,
#                                 'ad_group_name': ad_group.name,
#                                 'campaign_id': campaigns.id,
#                                 'campaign_name': campaigns.name,
#                                 'quality_score': getattr(ad_group_criterion, 'quality_info', {}).get('quality_score', None),
#                                 'cpc_bid_micros': ad_group_criterion.cpc_bid_micros / 1000000 if ad_group_criterion.cpc_bid_micros else None,
#                                 'created_at': None,  # Not available in basic keyword query
#                                 'updated_at': None   # Not available in basic keyword query
#                             })
                        
#                         logger.info(f"Retrieved {len(keywords)} keywords for customer {customer_id}")
#                         return keywords
                        
#                     except Exception as e:
#                         logger.error(f"Error fetching keywords: {e}")
#                         return []
                
#                 def get_performance_data(self, customer_id, start_date, end_date, filters=None, limit=50, sort_by="clicks", order="desc"):
#                     """Get performance data using GAQL with filters and state"""
#                     try:
#                         client = self._get_google_ads_client()
#                         if not client:
#                             logger.warning("Google Ads client not available - returning empty performance data")
#                             return []
                        
#                         # Build GAQL query
#                         query = self._build_performance_gaql_query(start_date, end_date, filters, limit, sort_by, order)
                        
#                         # Execute query
#                         ga_service = client.get_service("GoogleAdsService")
#                         response = ga_service.search(customer_id=customer_id, query=query)
                        
#                         performance_data = []
#                         for row in response:
#                             metrics = row.metrics
#                             campaigns = row.campaign
#                             ad_group = row.ad_group
#                             ad_group_criterion = row.ad_group_criterion
                            
#                             performance_data.append({
#                                 'date': row.segments.date,
#                                 'campaign_id': campaigns.id,
#                                 'campaign_name': campaigns.name,
#                                 'ad_group_id': ad_group.id if ad_group else None,
#                                 'ad_group_name': ad_group.name if ad_group else None,
#                                 'keyword_id': ad_group_criterion.criterion_id if ad_group_criterion else None,
#                                 'keyword_text': ad_group_criterion.keyword.text if ad_group_criterion and ad_group_criterion.keyword else None,
#                                 'impressions': metrics.impressions,
#                                 'clicks': metrics.clicks,
#                                 'cost_micros': metrics.cost_micros,
#                                 'cost': metrics.cost_micros / 1000000 if metrics.cost_micros else 0,
#                                 'ctr': metrics.ctr,
#                                 'cpc': metrics.cpc,
#                                 'conversions': metrics.conversions,
#                                 'conversion_value': metrics.conversions_value,
#                                 'roas': metrics.conversions_value / (metrics.cost_micros / 1000000) if metrics.cost_micros and metrics.cost_micros > 0 else 0
#                             })
                        
#                         logger.info(f"Retrieved {len(performance_data)} performance records for customer {customer_id}")
#                         return performance_data
                        
#                     except Exception as e:
#                         logger.error(f"Error fetching performance data: {e}")
#                         return []
                
#                 def _build_campaigns_gaql_query(self, filters=None, limit=50, sort_by="clicks", order="desc"):
#                     """Build GAQL query for campaigns with metrics for REST API"""
#                     # Base query with metrics for REST API compatibility
#                     query = """
#                         SELECT
#                             campaign.id,
#                             campaign.name,
#                             campaign.status,
#                             campaign.advertising_channel_type,
#                             campaign.start_date,
#                             campaign.end_date,
#                             metrics.impressions,
#                             metrics.clicks,
#                             metrics.ctr,
#                             metrics.conversions,
#                             metrics.cost_micros,
#                             metrics.average_cpc,
#                             metrics.average_cpm,
#                             metrics.average_cpa
#                         FROM campaign
#                         WHERE campaign.status != 'REMOVED'
#                         AND segments.date DURING LAST_30_DAYS
#                     """
                    
#                     # Add filters
#                     if filters:
#                         filter_conditions = self._build_filter_conditions(filters, "campaign")
#                         if filter_conditions:
#                             query += f" AND {filter_conditions}"
                    
#                     # Add sorting - handle metrics fields
#                     if sort_by in ['clicks', 'impressions', 'conversions', 'ctr', 'cost']:
#                         if sort_by == 'cost':
#                             sort_field = "metrics.cost_micros"
#                         elif sort_by == 'ctr':
#                             sort_field = "metrics.ctr"
#                         else:
#                             sort_field = f"metrics.{sort_by}"
#                     else:
#                         sort_field = self._map_sort_field(sort_by, "campaign")
                    
#                     sort_order = "ASC" if order.lower() == "asc" else "DESC"
#                     query += f" ORDER BY {sort_field} {sort_order}"
                    
#                     # Add limit
#                     query += f" LIMIT {limit}"
                    
#                     return query
                
#                 def _build_ad_groups_gaql_query(self, campaign_id=None, filters=None, limit=50, sort_by="clicks", order="desc"):
#                     """Build GAQL query for ad groups"""
#                     # Base query - using only supported fields
#                     query = """
#                         SELECT
#                             ad_group.id,
#                             ad_group.name,
#                             ad_group.status,
#                             ad_group.type,
#                             ad_group.cpc_bid_micros,
#                             campaign.id,
#                             campaign.name
#                         FROM ad_group
#                         WHERE ad_group.status != 'REMOVED'
#                     """
                    
#                     # Add campaign filter
#                     if campaign_id:
#                         query += f" AND campaign.id = {campaign_id}"
                    
#                     # Add filters
#                     if filters:
#                         filter_conditions = self._build_filter_conditions(filters, "ad_group")
#                         if filter_conditions:
#                             query += f" AND {filter_conditions}"
                    
#                     # Add sorting
#                     sort_field = self._map_sort_field(sort_by, "ad_group")
#                     sort_order = "ASC" if order.lower() == "asc" else "DESC"
#                     query += f" ORDER BY {sort_field} {sort_order}"
                    
#                     # Add limit
#                     query += f" LIMIT {limit}"
                    
#                     return query
                
#                 def _build_keywords_gaql_query(self, ad_group_id=None, filters=None, limit=50, sort_by="clicks", order="desc"):
#                     """Build GAQL query for keywords"""
#                     # Base query - using only supported fields
#                     query = """
#                         SELECT
#                             ad_group_criterion.criterion_id,
#                             ad_group_criterion.keyword.text,
#                             ad_group_criterion.keyword.match_type,
#                             ad_group_criterion.status,
#                             ad_group_criterion.quality_info.quality_score,
#                             ad_group_criterion.cpc_bid_micros,
#                             ad_group.id,
#                             ad_group.name,
#                             campaign.id,
#                             campaign.name
#                         FROM keyword_view
#                         WHERE ad_group_criterion.status != 'REMOVED'
#                     """
                    
#                     # Add ad group filter
#                     if ad_group_id:
#                         query += f" AND ad_group.id = {ad_group_id}"
                    
#                     # Add filters
#                     if filters:
#                         filter_conditions = self._build_filter_conditions(filters, "ad_group_criterion")
#                         if filter_conditions:
#                             query += f" AND {filter_conditions}"
                    
#                     # Add sorting
#                     sort_field = self._map_sort_field(sort_by, "ad_group_criterion")
#                     sort_order = "ASC" if order.lower() == "asc" else "DESC"
#                     query += f" ORDER BY {sort_field} {sort_order}"
                    
#                     # Add limit
#                     query += f" LIMIT {limit}"
                    
#                     return query
                
#                 def _build_performance_gaql_query(self, start_date, end_date, filters=None, limit=50, sort_by="clicks", order="desc"):
#                     """Build GAQL query for performance data"""
#                     # Base query
#                     query = f"""
#                         SELECT
#                             segments.date,
#                             campaign.id,
#                             campaign.name,
#                             ad_group.id,
#                             ad_group.name,
#                             ad_group_criterion.criterion_id,
#                             ad_group_criterion.keyword.text,
#                             metrics.impressions,
#                             metrics.clicks,
#                             metrics.cost_micros,
#                             metrics.ctr,
#                             metrics.cpc,
#                             metrics.conversions,
#                             metrics.conversions_value
#                         FROM keyword_view
#                         WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
#                     """
                    
#                     # Add filters
#                     if filters:
#                         filter_conditions = self._build_filter_conditions(filters, "metrics")
#                         if filter_conditions:
#                             query += f" AND {filter_conditions}"
                    
#                     # Add sorting
#                     sort_field = self._map_sort_field(sort_by, "metrics")
#                     sort_order = "ASC" if order.lower() == "asc" else "DESC"
#                     query += f" ORDER BY {sort_field} {sort_order}"
                    
#                     # Add limit
#                     query += f" LIMIT {limit}"
                    
#                     return query
                
#                 def _build_filter_conditions(self, filters, entity_prefix):
#                     """Build filter conditions for GAQL query"""
#                     if not filters:
#                         return ""
                    
#                     conditions = []
#                     for filter_item in filters:
#                         field = filter_item.get("field", "")
#                         operator = filter_item.get("operator", "equals")
#                         value = filter_item.get("value", "")
                        
#                         if not field or not value:
#                             continue
                        
#                         # Map field to GAQL field
#                         gaql_field = self._map_filter_field(field, entity_prefix)
#                         if not gaql_field:
#                             continue
                        
#                         # Build condition based on operator
#                         if operator == "equals":
#                             conditions.append(f"{gaql_field} = '{value}'")
#                         elif operator == "contains":
#                             conditions.append(f"{gaql_field} CONTAINS '{value}'")
#                         elif operator == "greater_than":
#                             conditions.append(f"{gaql_field} > {value}")
#                         elif operator == "less_than":
#                             conditions.append(f"{gaql_field} < {value}")
#                         elif operator == "in":
#                             if isinstance(value, list):
#                                 value_list = "', '".join(str(v) for v in value)
#                                 conditions.append(f"{gaql_field} IN ('{value_list}')")
#                         elif operator == "not_in":
#                             if isinstance(value, list):
#                                 value_list = "', '".join(str(v) for v in value)
#                                 conditions.append(f"{gaql_field} NOT IN ('{value_list}')")
#                         elif operator == "between":
#                             if isinstance(value, list) and len(value) == 2:
#                                 conditions.append(f"{gaql_field} BETWEEN {value[0]} AND {value[1]}")
                    
#                     return " AND ".join(conditions)
                
#                 def _map_filter_field(self, field, entity_prefix):
#                     """Map filter field to GAQL field"""
#                     field_mapping = {
#                         "status": f"{entity_prefix}.status",
#                         "name": f"{entity_prefix}.name",
#                         "id": f"{entity_prefix}.id",
#                         "type": f"{entity_prefix}.type",
#                         "clicks": "metrics.clicks",
#                         "impressions": "metrics.impressions",
#                         "cost": "metrics.cost_micros",
#                         "ctr": "metrics.ctr",
#                         "cpc": "metrics.cpc",
#                         "conversions": "metrics.conversions",
#                         "roas": "metrics.conversions_value / (metrics.cost_micros / 1000000)"
#                     }
                    
#                     return field_mapping.get(field.lower())
                
#                 def _map_sort_field(self, sort_by, entity_prefix):
#                     """Map sort field to GAQL field"""
#                     # For campaigns and ad groups, only allow sorting by basic fields
#                     if entity_prefix in ["campaign", "ad_group"]:
#                         sort_mapping = {
#                             "name": f"{entity_prefix}.name",
#                             "id": f"{entity_prefix}.id",
#                             "status": f"{entity_prefix}.status",
#                             "type": f"{entity_prefix}.type",
#                             "start_date": f"{entity_prefix}.start_date",
#                             "end_date": f"{entity_prefix}.end_date"
#                         }
#                     else:
#                         # For performance data, allow metrics sorting
#                         sort_mapping = {
#                             "clicks": "metrics.clicks",
#                             "impressions": "metrics.impressions",
#                             "cost": "metrics.cost_micros",
#                             "ctr": "metrics.ctr",
#                             "cpc": "metrics.cpc",
#                             "conversions": "metrics.conversions",
#                             "roas": "metrics.conversions_value / (metrics.cost_micros / 1000000)",
#                             "name": f"{entity_prefix}.name",
#                             "id": f"{entity_prefix}.id",
#                             "status": f"{entity_prefix}.status"
#                         }
                    
#                     return sort_mapping.get(sort_by.lower(), f"{entity_prefix}.id")
            
#             return SimplifiedAPIService(api_tool, customer_id, user_id)
            
#         except Exception as e:
#             logger.error(f"Error creating simplified API service: {e}")
#             # Return a mock service that returns empty data
#             class MockAPIService:
#                 def get_campaigns(self, customer_id, filters=None, limit=50, sort_by="clicks", order="desc"): 
#                     return []
#                 def get_ad_groups(self, customer_id, campaign_id=None, filters=None, limit=50, sort_by="clicks", order="desc"): 
#                     return []
#                 def get_keywords(self, customer_id, ad_group_id=None, filters=None, limit=50, sort_by="clicks", order="desc"): 
#                     return []
#                 def get_performance_data(self, customer_id, start_date, end_date, filters=None, limit=50, sort_by="clicks", order="desc"): 
#                     return []
            
#             return MockAPIService()

#     # Simulation methods (replace with actual implementations)
#     def _simulate_data_retrieval(self, action_name: str, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
#         """Simulate data retrieval from Google Ads API"""
#         # This would be replaced with actual Google Ads API calls
#         return [
#             {
#                 "id": f"simulated_{action_name.lower()}_1",
#                 "name": f"Sample {action_name.replace('GET_', '').replace('_', ' ').title()}",
#                 "status": "ACTIVE",
#                 "clicks": 100,
#                 "impressions": 1000,
#                 "cost": 50.0,
#                 "ctr": 0.1,
#                 "cpc": 0.5
#             }
#         ]
    
#     def _simulate_analysis(self, action_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         """Simulate analysis results"""
#         return {
#             "summary": f"Analysis completed for {action_name}",
#             "metrics": {
#                 "total_clicks": 1000,
#                 "total_impressions": 10000,
#                 "total_cost": 500.0,
#                 "average_ctr": 0.1,
#                 "average_cpc": 0.5
#             },
#             "trends": {
#                 "clicks_trend": "increasing",
#                 "cost_trend": "stable",
#                 "performance_trend": "improving"
#             }
#         }
    
#     def _generate_insights(self, action_name: str, parameters: Dict[str, Any]) -> List[str]:
#         """Generate insights for analysis actions"""
#         return [
#             f"Key insight 1 for {action_name}",
#             f"Key insight 2 for {action_name}",
#             f"Recommendation for {action_name}"
#         ]
    
#     def _simulate_optimization(self, action_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         """Simulate optimization results"""
#         return {
#             "optimization_score": 0.85,
#             "improvements": [
#                 "Increased bid by 10%",
#                 "Paused underperforming keywords",
#                 "Adjusted budget allocation"
#             ],
#             "expected_impact": "15% increase in conversions"
#         }
    
#     def _generate_recommendations(self, action_name: str, parameters: Dict[str, Any]) -> List[str]:
#         """Generate optimization recommendations"""
#         return [
#             f"Optimization recommendation 1 for {action_name}",
#             f"Optimization recommendation 2 for {action_name}",
#             f"Budget optimization for {action_name}"
#         ]
    
#     def _simulate_content_generation(self, action_name: str, theme: str, tone: str, count: int) -> List[Dict[str, Any]]:
#         """Simulate content generation"""
#         content = []
#         for i in range(count):
#             content.append({
#                 "id": f"generated_{i+1}",
#                 "title": f"Generated {theme} content {i+1}",
#                 "description": f"This is a {tone} description for {theme}",
#                 "headline": f"Amazing {theme} headline {i+1}",
#                 "call_to_action": f"Learn more about {theme}"
#             })
#         return content
    
#     def _simulate_compliance_check(self, action_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         """Simulate compliance check results"""
#         return {
#             "overall_score": 0.9,
#             "checks_passed": 8,
#             "checks_failed": 1,
#             "compliance_status": "GOOD"
#         }
    
#     def _identify_issues(self, action_name: str, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
#         """Identify compliance issues"""
#         return [
#             {
#                 "issue": "Missing sitelinks",
#                 "severity": "medium",
#                 "description": "Campaign could benefit from sitelinks"
#             }
#         ]
    
#     def _generate_fix_recommendations(self, action_name: str, parameters: Dict[str, Any]) -> List[str]:
#         """Generate fix recommendations"""
#         return [
#             f"Fix recommendation 1 for {action_name}",
#             f"Fix recommendation 2 for {action_name}",
#             f"Improvement suggestion for {action_name}"
#         ]
    
#     def get_tool_definitions(self) -> List[Dict[str, Any]]:
#         """Get all tool definitions"""
#         return self.tools
    
#     def get_tool_by_name(self, tool_name: str) -> Optional[Dict[str, Any]]:
#         """Get tool definition by name"""
#         for tool in self.tools:
#             if tool["function"]["name"] == tool_name:
#                 return tool
#         return None


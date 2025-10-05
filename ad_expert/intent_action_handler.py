"""
Intent Action Handler for RAGChat2View
Handles execution of all Google Ads intent actions using GAQL queries
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class IntentActionHandler:
    """Handles execution of all Google Ads intent actions"""
    
    def __init__(self, mcp_service):
        self.mcp_service = mcp_service
    
    async def execute_intent_action(self, intent_result, customer_id: str, user_id: int, query: str) -> Dict[str, Any]:
        """Execute the appropriate intent action based on the intent result"""
        try:
            actions = intent_result.actions
            parameters = intent_result.parameters
            date_ranges = intent_result.date_ranges
            filters = intent_result.filters
            
            # Handle multiple actions if present
            if len(actions) > 1:
                return await self._handle_multiple_actions(actions, customer_id, user_id, query, parameters, date_ranges, filters)
            
            action = actions[0] if actions else "QUERY_WITHOUT_SOLUTION"
            
            # Route to specific action handler
            if action in self._get_basic_operations():
                return await self._handle_basic_operations(action, customer_id, user_id, parameters, date_ranges, filters)
            elif action in self._get_analysis_operations():
                return await self._handle_analysis_operations(action, customer_id, user_id, parameters, date_ranges, filters)
            elif action in self._get_creative_operations():
                return await self._handle_creative_operations(action, customer_id, user_id, parameters, date_ranges, filters)
            elif action in self._get_optimization_operations():
                return await self._handle_optimization_operations(action, customer_id, user_id, parameters, date_ranges, filters)
            elif action in self._get_audit_operations():
                return await self._handle_audit_operations(action, customer_id, user_id, parameters, date_ranges, filters)
            else:
                return await self._handle_fallback_action(action, customer_id, user_id, query, parameters)
                
        except Exception as e:
            logger.error(f"Error executing intent action: {e}")
            return {
                "content": f"I encountered an error processing your request: {str(e)}",
                "data": None,
                "type": "error"
            }
    
    def _get_basic_operations(self) -> List[str]:
        """Get list of basic Google Ads operations"""
        return [
            "GET_OVERVIEW", "GET_CAMPAIGNS", "GET_CAMPAIGN_BY_ID", "GET_CAMPAIGNS_WITH_FILTERS",
            "CREATE_CAMPAIGN", "GET_ADS", "GET_AD_BY_ID", "GET_ADS_WITH_FILTERS", "GET_ADS_BY_CAMPAIGN_ID",
            "GET_ADSETS", "GET_ADSET_BY_ID", "GET_ADSETS_WITH_FILTERS", "GET_ADSETS_BY_CAMPAIGN_ID",
            "CREATE_AD", "PAUSE_CAMPAIGN", "RESUME_CAMPAIGN", "GET_PERFORMANCE", "GET_KEYWORDS",
            "GET_BUDGETS", "GET_BUDGET_BY_ID", "GET_BUDGETS_WITH_FILTERS", "GET_BUDGETS_BY_CAMPAIGN_ID",
            "GET_ACCESSIBLE_CUSTOMERS"
        ]
    
    def _get_analysis_operations(self) -> List[str]:
        """Get list of analysis operations"""
        return [
            "CAMPAIGN_SUMMARY_COMPARISON", "PERFORMANCE_SUMMARY", "TREND_ANALYSIS", "LISTING_ANALYSIS",
            "PIE_CHART_DISPLAY", "DUPLICATE_KEYWORDS_ANALYSIS", "DIG_DEEPER_ANALYSIS", "COMPARE_PERFORMANCE",
            "ANALYZE_AUDIENCE", "ANALYZE_AUDIENCE_INSIGHTS", "ANALYZE_DEMOGRAPHICS", "ANALYZE_VIDEO_PERFORMANCE",
            "ANALYZE_PLACEMENTS", "ANALYZE_DEVICE_PERFORMANCE", "ANALYZE_DEVICE_PERFORMANCE_DETAILED",
            "ANALYZE_TIME_PERFORMANCE", "ANALYZE_LOCATION_PERFORMANCE", "ANALYZE_LANDING_PAGE_MOBILE",
            "ANALYZE_KEYWORD_TRENDS", "ANALYZE_AUCTION_INSIGHTS", "ANALYZE_SEARCH_TERMS",
            "ANALYZE_ADS_SHOWING_TIME", "ANALYZE_COMPETITORS"
        ]
    
    def _get_creative_operations(self) -> List[str]:
        """Get list of creative operations"""
        return [
            "GENERATE_AD_COPIES", "GENERATE_CREATIVES", "POSTER_GENERATOR", "META_ADS_CREATIVES",
            "GENERATE_IMAGES", "TEST_CREATIVE_ELEMENTS", "CHECK_CREATIVE_FATIGUE"
        ]
    
    def _get_optimization_operations(self) -> List[str]:
        """Get list of optimization operations"""
        return [
            "OPTIMIZE_CAMPAIGN", "OPTIMIZE_ADSET", "OPTIMIZE_AD", "OPTIMIZE_BUDGETS",
            "OPTIMIZE_TCPA", "OPTIMIZE_BUDGET_ALLOCATION", "SUGGEST_NEGATIVE_KEYWORDS"
        ]
    
    def _get_audit_operations(self) -> List[str]:
        """Get list of audit operations"""
        return [
            "CHECK_CAMPAIGN_CONSISTENCY", "CHECK_SITELINKS", "CHECK_LANDING_PAGE_URL",
            "CHECK_DUPLICATE_KEYWORDS", "CHECK_TECHNICAL_COMPLIANCE"
        ]
    
    async def _handle_multiple_actions(self, actions: List[str], customer_id: str, user_id: int, 
                                     query: str, parameters: Dict, date_ranges: List, filters: List) -> Dict[str, Any]:
        """Handle multiple actions in a single request"""
        results = []
        for action in actions:
            try:
                # Create a single action intent result
                from google_ads_new.intent_mapping_service import IntentMappingResult
                single_intent = IntentMappingResult(
                    actions=[action],
                    date_ranges=date_ranges,
                    filters=filters,
                    confidence=0.9,
                    reasoning=f"Part of multi-action request: {', '.join(actions)}",
                    parameters=parameters
                )
                
                result = await self.execute_intent_action(single_intent, customer_id, user_id, query)
                results.append({
                    "action": action,
                    "result": result
                })
            except Exception as e:
                logger.error(f"Error executing action {action}: {e}")
                results.append({
                    "action": action,
                    "error": str(e)
                })
        
        return {
            "content": f"I executed {len(actions)} actions for customer {customer_id}.",
            "data": {"multi_action_results": results},
            "type": "multi_action_results"
        }
    
    async def _handle_basic_operations(self, action: str, customer_id: str, user_id: int, 
                                     parameters: Dict, date_ranges: List, filters: List) -> Dict[str, Any]:
        """Handle basic Google Ads operations"""
        
        if action == "GET_OVERVIEW":
            result = await self.mcp_service.mcp_client.get_overview(customer_id, user_id)
            return {
                "content": f"I retrieved account overview for customer {customer_id}.",
                "data": result,
                "type": "overview_data"
            }
        
        elif action == "GET_CAMPAIGNS":
            campaign_ids = parameters.get("campaign_ids", [])
            if campaign_ids:
                campaign_id = campaign_ids[0]
                result = await self.mcp_service.mcp_client.get_campaign_by_id(customer_id, campaign_id, user_id)
                return {
                    "content": f"I retrieved campaign {campaign_id} details for customer {customer_id}.",
                    "data": result,
                    "type": "campaign_data"
                }
            else:
                if filters:
                    result = await self.mcp_service.mcp_client.get_campaigns_with_filters(customer_id, filters, user_id=user_id)
                else:
                    result = await self.mcp_service.get_campaign_data(customer_id, user_id)
                return {
                    "content": f"I retrieved {result.get('total_count', 0)} campaigns for customer {customer_id}.",
                    "data": result,
                    "type": "campaign_data"
                }
        
        elif action == "GET_CAMPAIGN_BY_ID":
            campaign_id = parameters.get("campaign_id")
            if not campaign_id:
                return {"content": "Campaign ID is required.", "data": None, "type": "error"}
            
            result = await self.mcp_service.mcp_client.get_campaign_by_id(customer_id, campaign_id, user_id)
            return {
                "content": f"I retrieved campaign {campaign_id} details for customer {customer_id}.",
                "data": result,
                "type": "campaign_data"
            }
        
        elif action == "GET_CAMPAIGNS_WITH_FILTERS":
            result = await self.mcp_service.mcp_client.get_campaigns_with_filters(customer_id, filters, user_id=user_id)
            return {
                "content": f"I retrieved filtered campaigns for customer {customer_id}.",
                "data": result,
                "type": "campaign_data"
            }
        
        elif action == "CREATE_CAMPAIGN":
            campaign_data = parameters.get("campaign_data", {})
            result = await self.mcp_service.mcp_client.create_campaign(customer_id, campaign_data, user_id)
            return {
                "content": f"I attempted to create a campaign for customer {customer_id}.",
                "data": result,
                "type": "campaign_creation"
            }
        
        elif action == "GET_ADS":
            ad_ids = parameters.get("ad_ids", [])
            campaign_ids = parameters.get("campaign_ids", [])
            
            if ad_ids:
                ad_id = ad_ids[0]
                result = await self.mcp_service.mcp_client.get_ad_by_id(customer_id, ad_id, user_id)
                return {
                    "content": f"I retrieved ad {ad_id} details for customer {customer_id}.",
                    "data": result,
                    "type": "ad_data"
                }
            elif campaign_ids:
                campaign_id = campaign_ids[0]
                result = await self.mcp_service.mcp_client.get_ads_by_campaign_id(customer_id, campaign_id, user_id)
                return {
                    "content": f"I retrieved ads for campaign {campaign_id}.",
                    "data": result,
                    "type": "ad_data"
                }
            else:
                if filters:
                    result = await self.mcp_service.mcp_client.get_ads_with_filters(customer_id, filters, user_id=user_id)
                else:
                    result = await self.mcp_service.mcp_client.get_ads(customer_id, user_id=user_id)
                return {
                    "content": f"I retrieved {result.get('total_count', 0)} ads for customer {customer_id}.",
                    "data": result,
                    "type": "ad_data"
                }
        
        elif action == "GET_AD_BY_ID":
            ad_id = parameters.get("ad_id")
            if not ad_id:
                return {"content": "Ad ID is required.", "data": None, "type": "error"}
            
            result = await self.mcp_service.mcp_client.get_ad_by_id(customer_id, ad_id, user_id)
            return {
                "content": f"I retrieved ad {ad_id} details for customer {customer_id}.",
                "data": result,
                "type": "ad_data"
            }
        
        elif action == "GET_ADS_WITH_FILTERS":
            result = await self.mcp_service.mcp_client.get_ads_with_filters(customer_id, filters, user_id=user_id)
            return {
                "content": f"I retrieved filtered ads for customer {customer_id}.",
                "data": result,
                "type": "ad_data"
            }
        
        elif action == "GET_ADS_BY_CAMPAIGN_ID":
            campaign_id = parameters.get("campaign_id")
            if not campaign_id:
                return {"content": "Campaign ID is required.", "data": None, "type": "error"}
            
            result = await self.mcp_service.mcp_client.get_ads_by_campaign_id(customer_id, campaign_id, user_id)
            return {
                "content": f"I retrieved ads for campaign {campaign_id}.",
                "data": result,
                "type": "ad_data"
            }
        
        elif action in ["GET_ADSETS", "GET_AD_GROUPS"]:
            ad_group_ids = parameters.get("ad_group_ids", [])
            campaign_ids = parameters.get("campaign_ids", [])
            
            if ad_group_ids:
                ad_group_id = ad_group_ids[0]
                result = await self.mcp_service.mcp_client.get_ad_group_by_id(customer_id, ad_group_id, user_id)
                return {
                    "content": f"I retrieved ad group {ad_group_id} details for customer {customer_id}.",
                    "data": result,
                    "type": "ad_group_data"
                }
            elif campaign_ids:
                campaign_id = campaign_ids[0]
                result = await self.mcp_service.mcp_client.get_ad_groups_by_campaign_id(customer_id, campaign_id, user_id)
                return {
                    "content": f"I retrieved ad groups for campaign {campaign_id}.",
                    "data": result,
                    "type": "ad_group_data"
                }
            else:
                if filters:
                    result = await self.mcp_service.mcp_client.get_ad_groups_with_filters(customer_id, filters, user_id=user_id)
                else:
                    result = await self.mcp_service.get_ad_group_data(customer_id, None, user_id)
                return {
                    "content": f"I retrieved {result.get('total_count', 0)} ad groups for customer {customer_id}.",
                    "data": result,
                    "type": "ad_group_data"
                }
        
        elif action == "GET_ADSET_BY_ID":
            ad_group_id = parameters.get("ad_group_id")
            if not ad_group_id:
                return {"content": "Ad Group ID is required.", "data": None, "type": "error"}
            
            result = await self.mcp_service.mcp_client.get_ad_group_by_id(customer_id, ad_group_id, user_id)
            return {
                "content": f"I retrieved ad group {ad_group_id} details for customer {customer_id}.",
                "data": result,
                "type": "ad_group_data"
            }
        
        elif action == "GET_ADSETS_WITH_FILTERS":
            result = await self.mcp_service.mcp_client.get_ad_groups_with_filters(customer_id, filters, user_id=user_id)
            return {
                "content": f"I retrieved filtered ad groups for customer {customer_id}.",
                "data": result,
                "type": "ad_group_data"
            }
        
        elif action == "GET_ADSETS_BY_CAMPAIGN_ID":
            campaign_id = parameters.get("campaign_id")
            if not campaign_id:
                return {"content": "Campaign ID is required.", "data": None, "type": "error"}
            
            result = await self.mcp_service.mcp_client.get_ad_groups_by_campaign_id(customer_id, campaign_id, user_id)
            return {
                "content": f"I retrieved ad groups for campaign {campaign_id}.",
                "data": result,
                "type": "ad_group_data"
            }
        
        elif action == "CREATE_AD":
            ad_data = parameters.get("ad_data", {})
            result = await self.mcp_service.mcp_client.create_ad(customer_id, ad_data, user_id)
            return {
                "content": f"I attempted to create an ad for customer {customer_id}.",
                "data": result,
                "type": "ad_creation"
            }
        
        elif action == "PAUSE_CAMPAIGN":
            campaign_ids = parameters.get("campaign_ids", [])
            result = await self.mcp_service.mcp_client.pause_campaign(customer_id, campaign_ids, user_id)
            return {
                "content": f"I attempted to pause campaigns {campaign_ids} for customer {customer_id}.",
                "data": result,
                "type": "campaign_pause"
            }
        
        elif action == "RESUME_CAMPAIGN":
            campaign_ids = parameters.get("campaign_ids", [])
            result = await self.mcp_service.mcp_client.resume_campaign(customer_id, campaign_ids, user_id)
            return {
                "content": f"I attempted to resume campaigns {campaign_ids} for customer {customer_id}.",
                "data": result,
                "type": "campaign_resume"
            }
        
        elif action in ["GET_PERFORMANCE", "GET_METRICS"]:
            # Determine date range
            start_date = None
            end_date = None
            
            if date_ranges:
                date_range = date_ranges[0]
                if date_range.period == "last_week":
                    end_date = datetime.now().strftime('%Y-%m-%d')
                    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                elif date_range.period == "last_30_days":
                    end_date = datetime.now().strftime('%Y-%m-%d')
                    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                elif date_range.start_date and date_range.end_date:
                    start_date = date_range.start_date
                    end_date = date_range.end_date
            
            result = await self.mcp_service.mcp_client.get_performance_data(
                customer_id=customer_id,
                start_date=start_date,
                end_date=end_date,
                resource_type="campaign",
                user_id=user_id
            )
            
            return {
                "content": f"I retrieved performance data for customer {customer_id}.",
                "data": result,
                "type": "performance_data"
            }
        
        elif action == "GET_KEYWORDS":
            ad_group_id = parameters.get("ad_group_id")
            result = await self.mcp_service.mcp_client.get_keywords(customer_id, ad_group_id, user_id)
            return {
                "content": f"I retrieved {result.get('total_count', 0)} keywords for customer {customer_id}.",
                "data": result,
                "type": "keyword_data"
            }
        
        elif action == "GET_BUDGETS":
            budget_ids = parameters.get("budget_ids", [])
            campaign_ids = parameters.get("campaign_ids", [])
            
            if budget_ids:
                budget_id = budget_ids[0]
                result = await self.mcp_service.mcp_client.get_budget_by_id(customer_id, budget_id, user_id)
                return {
                    "content": f"I retrieved budget {budget_id} details for customer {customer_id}.",
                    "data": result,
                    "type": "budget_data"
                }
            elif campaign_ids:
                campaign_id = campaign_ids[0]
                result = await self.mcp_service.mcp_client.get_budgets_by_campaign_id(customer_id, campaign_id, user_id)
                return {
                    "content": f"I retrieved budgets for campaign {campaign_id}.",
                    "data": result,
                    "type": "budget_data"
                }
            else:
                if filters:
                    result = await self.mcp_service.mcp_client.get_budgets_with_filters(customer_id, filters, user_id=user_id)
                else:
                    result = await self.mcp_service.mcp_client.get_budgets(customer_id, user_id=user_id)
                return {
                    "content": f"I retrieved {result.get('total_count', 0)} budgets for customer {customer_id}.",
                    "data": result,
                    "type": "budget_data"
                }
        
        elif action == "GET_BUDGET_BY_ID":
            budget_id = parameters.get("budget_id")
            if not budget_id:
                return {"content": "Budget ID is required.", "data": None, "type": "error"}
            
            result = await self.mcp_service.mcp_client.get_budget_by_id(customer_id, budget_id, user_id)
            return {
                "content": f"I retrieved budget {budget_id} details for customer {customer_id}.",
                "data": result,
                "type": "budget_data"
            }
        
        elif action == "GET_BUDGETS_WITH_FILTERS":
            result = await self.mcp_service.mcp_client.get_budgets_with_filters(customer_id, filters, user_id=user_id)
            return {
                "content": f"I retrieved filtered budgets for customer {customer_id}.",
                "data": result,
                "type": "budget_data"
            }
        
        elif action == "GET_BUDGETS_BY_CAMPAIGN_ID":
            campaign_id = parameters.get("campaign_id")
            if not campaign_id:
                return {"content": "Campaign ID is required.", "data": None, "type": "error"}
            
            result = await self.mcp_service.mcp_client.get_budgets_by_campaign_id(customer_id, campaign_id, user_id)
            return {
                "content": f"I retrieved budgets for campaign {campaign_id}.",
                "data": result,
                "type": "budget_data"
            }
        
        elif action == "GET_ACCESSIBLE_CUSTOMERS":
            result = await self.mcp_service.mcp_client.get_accessible_customers(user_id)
            return {
                "content": f"I retrieved {result.get('total_count', 0)} accessible customer accounts.",
                "data": result,
                "type": "accessible_customers"
            }
        
        # Default fallback for basic operations
        return await self._handle_fallback_action(action, customer_id, user_id, "", parameters)
    
    async def _handle_analysis_operations(self, action: str, customer_id: str, user_id: int, 
                                        parameters: Dict, date_ranges: List, filters: List) -> Dict[str, Any]:
        """Handle analysis operations"""
        
        if action == "CAMPAIGN_SUMMARY_COMPARISON":
            sort_by = parameters.get("sort_by", "spend")
            limit = parameters.get("limit", 10)
            result = await self.mcp_service.mcp_client.analyze_campaign_summary_comparison(
                customer_id, sort_by, limit, user_id
            )
            return {
                "content": f"I analyzed campaign summary comparison for customer {customer_id}.",
                "data": result,
                "type": "analysis_data"
            }
        
        elif action == "PERFORMANCE_SUMMARY":
            days = parameters.get("days", 30)
            result = await self.mcp_service.mcp_client.analyze_performance_summary(
                customer_id, days, user_id
            )
            return {
                "content": f"I analyzed performance summary for customer {customer_id}.",
                "data": result,
                "type": "analysis_data"
            }
        
        elif action == "TREND_ANALYSIS":
            metric = parameters.get("metric", "clicks")
            days = parameters.get("days", 30)
            result = await self.mcp_service.mcp_client.analyze_trends(
                customer_id, metric, days, user_id
            )
            return {
                "content": f"I analyzed {metric} trends for customer {customer_id}.",
                "data": result,
                "type": "analysis_data"
            }
        
        elif action == "LISTING_ANALYSIS":
            listing_type = parameters.get("listing_type", "campaigns")
            limit = parameters.get("limit", 10)
            sort_by = parameters.get("sort_by", "conversions")
            days = parameters.get("days", 14)
            result = await self.mcp_service.mcp_client.analyze_listing_performance(
                customer_id, listing_type, limit, sort_by, days, user_id
            )
            return {
                "content": f"I analyzed {listing_type} listing performance for customer {customer_id}.",
                "data": result,
                "type": "analysis_data"
            }
        
        elif action == "PIE_CHART_DISPLAY":
            chart_type = parameters.get("chart_type", "spend")
            days = parameters.get("days", 30)
            result = await self.mcp_service.mcp_client.analyze_pie_chart_data(
                customer_id, chart_type, days, user_id
            )
            return {
                "content": f"I analyzed {chart_type} pie chart data for customer {customer_id}.",
                "data": result,
                "type": "analysis_data"
            }
        
        elif action == "DUPLICATE_KEYWORDS_ANALYSIS":
            days = parameters.get("days", 7)
            result = await self.mcp_service.mcp_client.analyze_duplicate_keywords(
                customer_id, days, user_id
            )
            return {
                "content": f"I analyzed duplicate keywords for customer {customer_id}.",
                "data": result,
                "type": "analysis_data"
            }
        
        elif action == "DIG_DEEPER_ANALYSIS":
            base_analysis = parameters.get("base_analysis", {})
            depth = parameters.get("depth", 1)
            result = await self.mcp_service.mcp_client.dig_deeper_analysis(
                customer_id, base_analysis, depth, user_id
            )
            return {
                "content": f"I performed deeper analysis (level {depth}) for customer {customer_id}.",
                "data": result,
                "type": "analysis_data"
            }
        
        elif action == "COMPARE_PERFORMANCE":
            comparison_type = parameters.get("comparison_type", "M1_M2")
            result = await self.mcp_service.mcp_client.compare_performance(
                customer_id, comparison_type, user_id
            )
            return {
                "content": f"I compared performance ({comparison_type}) for customer {customer_id}.",
                "data": result,
                "type": "analysis_data"
            }
        
        elif action == "ANALYZE_AUDIENCE":
            result = await self.mcp_service.mcp_client.analyze_audience(customer_id, user_id)
            return {
                "content": f"I analyzed audience for customer {customer_id}.",
                "data": result,
                "type": "analysis_data"
            }
        
        elif action == "ANALYZE_AUDIENCE_INSIGHTS":
            result = await self.mcp_service.mcp_client.analyze_audience_insights(customer_id, user_id)
            return {
                "content": f"I analyzed audience insights for customer {customer_id}.",
                "data": result,
                "type": "analysis_data"
            }
        
        elif action == "ANALYZE_DEMOGRAPHICS":
            result = await self.mcp_service.mcp_client.analyze_demographics(customer_id, user_id)
            return {
                "content": f"I analyzed demographics for customer {customer_id}.",
                "data": result,
                "type": "analysis_data"
            }
        
        elif action == "ANALYZE_VIDEO_PERFORMANCE":
            result = await self.mcp_service.mcp_client.analyze_video_performance(customer_id, user_id)
            return {
                "content": f"I analyzed video performance for customer {customer_id}.",
                "data": result,
                "type": "analysis_data"
            }
        
        elif action == "ANALYZE_PLACEMENTS":
            result = await self.mcp_service.mcp_client.analyze_placements(customer_id, user_id)
            return {
                "content": f"I analyzed placements for customer {customer_id}.",
                "data": result,
                "type": "analysis_data"
            }
        
        elif action == "ANALYZE_DEVICE_PERFORMANCE":
            result = await self.mcp_service.mcp_client.analyze_device_performance(customer_id, user_id)
            return {
                "content": f"I analyzed device performance for customer {customer_id}.",
                "data": result,
                "type": "analysis_data"
            }
        
        elif action == "ANALYZE_DEVICE_PERFORMANCE_DETAILED":
            result = await self.mcp_service.mcp_client.analyze_device_performance_detailed(customer_id, user_id)
            return {
                "content": f"I analyzed detailed device performance for customer {customer_id}.",
                "data": result,
                "type": "analysis_data"
            }
        
        elif action == "ANALYZE_TIME_PERFORMANCE":
            result = await self.mcp_service.mcp_client.analyze_time_performance(customer_id, user_id)
            return {
                "content": f"I analyzed time performance for customer {customer_id}.",
                "data": result,
                "type": "analysis_data"
            }
        
        elif action == "ANALYZE_LOCATION_PERFORMANCE":
            result = await self.mcp_service.mcp_client.analyze_location_performance(customer_id, user_id)
            return {
                "content": f"I analyzed location performance for customer {customer_id}.",
                "data": result,
                "type": "analysis_data"
            }
        
        elif action == "ANALYZE_LANDING_PAGE_MOBILE":
            result = await self.mcp_service.mcp_client.analyze_landing_page_mobile(customer_id, user_id)
            return {
                "content": f"I analyzed mobile landing page performance for customer {customer_id}.",
                "data": result,
                "type": "analysis_data"
            }
        
        elif action == "ANALYZE_KEYWORD_TRENDS":
            result = await self.mcp_service.mcp_client.analyze_keyword_trends(customer_id, user_id)
            return {
                "content": f"I analyzed keyword trends for customer {customer_id}.",
                "data": result,
                "type": "analysis_data"
            }
        
        elif action == "ANALYZE_AUCTION_INSIGHTS":
            result = await self.mcp_service.mcp_client.analyze_auction_insights(customer_id, user_id)
            return {
                "content": f"I analyzed auction insights for customer {customer_id}.",
                "data": result,
                "type": "analysis_data"
            }
        
        elif action == "ANALYZE_SEARCH_TERMS":
            result = await self.mcp_service.mcp_client.analyze_search_terms(customer_id, user_id)
            return {
                "content": f"I analyzed search terms for customer {customer_id}.",
                "data": result,
                "type": "analysis_data"
            }
        
        elif action == "ANALYZE_ADS_SHOWING_TIME":
            result = await self.mcp_service.mcp_client.analyze_ads_showing_time(customer_id, user_id)
            return {
                "content": f"I analyzed ads showing time for customer {customer_id}.",
                "data": result,
                "type": "analysis_data"
            }
        
        elif action == "ANALYZE_COMPETITORS":
            result = await self.mcp_service.mcp_client.analyze_competitors(customer_id, user_id)
            return {
                "content": f"I analyzed competitors for customer {customer_id}.",
                "data": result,
                "type": "analysis_data"
            }
        
        # Default fallback for analysis operations
        return await self._handle_fallback_action(action, customer_id, user_id, "", parameters)
    
    async def _handle_creative_operations(self, action: str, customer_id: str, user_id: int, 
                                        parameters: Dict, date_ranges: List, filters: List) -> Dict[str, Any]:
        """Handle creative operations"""
        
        if action == "GENERATE_AD_COPIES":
            context = parameters.get("context", "")
            platform = parameters.get("platform", "google_ads")
            variations = parameters.get("variations", 4)
            result = await self.mcp_service.mcp_client.generate_ad_copies(
                customer_id, context, platform, variations, user_id
            )
            return {
                "content": f"I generated {variations} ad copy variations for customer {customer_id}.",
                "data": result,
                "type": "creative_data"
            }
        
        elif action == "GENERATE_CREATIVES":
            context = parameters.get("context", "")
            result = await self.mcp_service.mcp_client.generate_creatives(
                customer_id, context, user_id
            )
            return {
                "content": f"I generated creative content for customer {customer_id}.",
                "data": result,
                "type": "creative_data"
            }
        
        elif action == "POSTER_GENERATOR":
            context = parameters.get("context", "")
            target_audience = parameters.get("target_audience", "general")
            result = await self.mcp_service.mcp_client.generate_poster_templates(
                customer_id, context, target_audience, user_id
            )
            return {
                "content": f"I generated poster templates for customer {customer_id}.",
                "data": result,
                "type": "creative_data"
            }
        
        elif action == "META_ADS_CREATIVES":
            context = parameters.get("context", "")
            ad_format = parameters.get("ad_format", "all")
            result = await self.mcp_service.mcp_client.generate_meta_ads_creatives(
                customer_id, context, ad_format, user_id
            )
            return {
                "content": f"I generated Meta Ads creatives for customer {customer_id}.",
                "data": result,
                "type": "creative_data"
            }
        
        elif action == "GENERATE_IMAGES":
            product_type = parameters.get("product_type", "general")
            count = parameters.get("count", 3)
            styles = parameters.get("styles", ["professional", "lifestyle", "modern"])
            result = await self.mcp_service.mcp_client.generate_images(
                customer_id, product_type, count, styles, user_id
            )
            return {
                "content": f"I generated {count} images for customer {customer_id}.",
                "data": result,
                "type": "creative_data"
            }
        
        elif action == "TEST_CREATIVE_ELEMENTS":
            result = await self.mcp_service.mcp_client.test_creative_elements(customer_id, user_id)
            return {
                "content": f"I analyzed creative elements for customer {customer_id}.",
                "data": result,
                "type": "creative_data"
            }
        
        elif action == "CHECK_CREATIVE_FATIGUE":
            result = await self.mcp_service.mcp_client.check_creative_fatigue(customer_id, user_id)
            return {
                "content": f"I checked creative fatigue for customer {customer_id}.",
                "data": result,
                "type": "creative_data"
            }
        
        # Default fallback for creative operations
        return await self._handle_fallback_action(action, customer_id, user_id, "", parameters)
    
    async def _handle_optimization_operations(self, action: str, customer_id: str, user_id: int, 
                                            parameters: Dict, date_ranges: List, filters: List) -> Dict[str, Any]:
        """Handle optimization operations"""
        
        if action == "OPTIMIZE_CAMPAIGN":
            campaign_id = parameters.get("campaign_id")
            result = await self.mcp_service.mcp_client.optimize_campaign(customer_id, campaign_id, user_id)
            return {
                "content": f"I optimized campaign {campaign_id} for customer {customer_id}.",
                "data": result,
                "type": "optimization_data"
            }
        
        elif action == "OPTIMIZE_ADSET":
            ad_group_id = parameters.get("ad_group_id")
            result = await self.mcp_service.mcp_client.optimize_adset(customer_id, ad_group_id, user_id)
            return {
                "content": f"I optimized ad group {ad_group_id} for customer {customer_id}.",
                "data": result,
                "type": "optimization_data"
            }
        
        elif action == "OPTIMIZE_AD":
            ad_id = parameters.get("ad_id")
            result = await self.mcp_service.mcp_client.optimize_ad(customer_id, ad_id, user_id)
            return {
                "content": f"I optimized ad {ad_id} for customer {customer_id}.",
                "data": result,
                "type": "optimization_data"
            }
        
        elif action == "OPTIMIZE_BUDGETS":
            result = await self.mcp_service.mcp_client.optimize_budgets(customer_id, user_id)
            return {
                "content": f"I optimized budgets for customer {customer_id}.",
                "data": result,
                "type": "optimization_data"
            }
        
        elif action == "OPTIMIZE_TCPA":
            result = await self.mcp_service.mcp_client.optimize_tcpa(customer_id, user_id)
            return {
                "content": f"I optimized TCPA for customer {customer_id}.",
                "data": result,
                "type": "optimization_data"
            }
        
        elif action == "OPTIMIZE_BUDGET_ALLOCATION":
            result = await self.mcp_service.mcp_client.optimize_budget_allocation(customer_id, user_id)
            return {
                "content": f"I optimized budget allocation for customer {customer_id}.",
                "data": result,
                "type": "optimization_data"
            }
        
        elif action == "SUGGEST_NEGATIVE_KEYWORDS":
            result = await self.mcp_service.mcp_client.suggest_negative_keywords(customer_id, user_id)
            return {
                "content": f"I suggested negative keywords for customer {customer_id}.",
                "data": result,
                "type": "optimization_data"
            }
        
        # Default fallback for optimization operations
        return await self._handle_fallback_action(action, customer_id, user_id, "", parameters)
    
    async def _handle_audit_operations(self, action: str, customer_id: str, user_id: int, 
                                     parameters: Dict, date_ranges: List, filters: List) -> Dict[str, Any]:
        """Handle audit operations"""
        
        if action == "CHECK_CAMPAIGN_CONSISTENCY":
            result = await self.mcp_service.mcp_client.check_campaign_consistency(customer_id, user_id)
            return {
                "content": f"I checked campaign consistency for customer {customer_id}.",
                "data": result,
                "type": "audit_data"
            }
        
        elif action == "CHECK_SITELINKS":
            result = await self.mcp_service.mcp_client.check_sitelinks(customer_id, user_id)
            return {
                "content": f"I checked sitelinks for customer {customer_id}.",
                "data": result,
                "type": "audit_data"
            }
        
        elif action == "CHECK_LANDING_PAGE_URL":
            result = await self.mcp_service.mcp_client.check_landing_page_url(customer_id, user_id)
            return {
                "content": f"I checked landing page URLs for customer {customer_id}.",
                "data": result,
                "type": "audit_data"
            }
        
        elif action == "CHECK_DUPLICATE_KEYWORDS":
            result = await self.mcp_service.mcp_client.check_duplicate_keywords(customer_id, user_id)
            return {
                "content": f"I checked for duplicate keywords for customer {customer_id}.",
                "data": result,
                "type": "audit_data"
            }
        
        elif action == "CHECK_TECHNICAL_COMPLIANCE":
            result = await self.mcp_service.mcp_client.check_technical_compliance(customer_id, user_id)
            return {
                "content": f"I checked technical compliance for customer {customer_id}.",
                "data": result,
                "type": "audit_data"
            }
        
        # Default fallback for audit operations
        return await self._handle_fallback_action(action, customer_id, user_id, "", parameters)
    
    async def _handle_fallback_action(self, action: str, customer_id: str, user_id: int, 
                                    query: str, parameters: Dict) -> Dict[str, Any]:
        """Handle fallback for unmatched actions"""
        try:
            # Use RAG system for intelligent context selection
            from google_ads_new.rag_service import GoogleAdsRAGService
            from google_ads_new.data_service import GoogleAdsDataService
            
            # Get user's Google Ads data for context
            data_service = GoogleAdsDataService(user_id)
            account_data = data_service.get_campaign_data()
            
            # Initialize RAG service
            rag_service = GoogleAdsRAGService(user_id)
            
            # Create a meaningful query based on intent action
            fallback_query = f"information about {action.lower().replace('_', ' ')}"
            if parameters:
                # Add parameters to the query for better context
                param_str = ", ".join([f"{k}: {v}" for k, v in parameters.items()])
                fallback_query = f"{fallback_query} with parameters: {param_str}"
            
            # Get hybrid response using smart context selection
            hybrid_response = rag_service.get_hybrid_response(fallback_query, account_data)
            
            return {
                "content": f"I processed your request for {action.lower().replace('_', ' ')} using AI analysis.",
                "data": hybrid_response,
                "type": "rag_enhanced_response"
            }
            
        except Exception as e:
            logger.error(f"Error in fallback action handler: {e}")
            return {
                "content": f"I encountered an error processing your request: {str(e)}",
                "data": None,
                "type": "error"
            }

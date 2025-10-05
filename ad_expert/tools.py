"""
Google Ads Tools using GAQL (Google Ads Query Language)
Contains all Google Ads API operations as LangChain tools
"""

import logging
from typing import Dict, Any, List, Optional
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
import requests
import json
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class GoogleAdsAPI:
    """Google Ads API client for making GAQL requests with automatic token refresh"""
    
    def __init__(self):
        self.base_url = "https://googleads.googleapis.com/v21"
        self.developer_token = os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN')
        self.login_customer_id = os.getenv('GOOGLE_ADS_LOGIN_CUSTOMER_ID', '9762343117')
        
    def _get_headers(self, access_token: str) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'developer-token': self.developer_token,
            'login-customer-id': self.login_customer_id
        }
    
    def _refresh_token_for_user(self, user_id: int) -> Optional[str]:
        """Refresh access token for a user"""
        try:
            from accounts.google_oauth_service import UserGoogleAuthService
            from django.contrib.auth.models import User
            
            user = User.objects.get(id=user_id)
            auth_record = UserGoogleAuthService.refresh_user_tokens(user)
            
            if auth_record:
                logger.info(f"Successfully refreshed token for user {user_id}")
                return auth_record.access_token
            else:
                logger.error(f"Failed to refresh token for user {user_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error refreshing token for user {user_id}: {str(e)}")
            return None
    
    def search(self, customer_id: str, access_token: str, query: str, user_id: int = None) -> Dict[str, Any]:
        """Execute GAQL search query with automatic token refresh on 401 errors"""
        try:
            # Clean customer_id to remove 'customers/' prefix if present
            clean_customer_id = customer_id.replace('customers/', '') if customer_id.startswith('customers/') else customer_id
            url = f"{self.base_url}/customers/{clean_customer_id}/googleAds:search"
            headers = self._get_headers(access_token)
            
            payload = {"query": query}
            
            response = requests.post(url, headers=headers, json=payload)
            
            # Handle 401 Unauthorized - try to refresh token
            if response.status_code == 401 or response.status_code == 403 and user_id:
                logger.warning(f"401 Unauthorized error for user {user_id}, attempting token refresh")
                
                # Try to refresh the token
                new_access_token = self._refresh_token_for_user(user_id)
                logger.info("New access token: ", new_access_token)
                if new_access_token:
                    # Retry with new token
                    headers = self._get_headers(new_access_token)
                    response = requests.post(url, headers=headers, json=payload)
                    logger.info(f"Retried request with refreshed token for user {user_id}")
                else:
                    logger.error(f"Failed to refresh token for user {user_id}")
            
            response.raise_for_status()
            logger.info("Response: ", response.content.decode('utf-8'))
            return response.json()
            
        except Exception as e:
            logger.error(f"Error executing GAQL query: {e}")
            # Log the response content for debugging
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_content = e.response.content.decode('utf-8')
                    logger.error(f"Response content: {error_content}")
                except:
                    logger.error(f"Response content: {e.response.content}")

            return {"error": str(e)}

# Initialize API client
google_ads_api = GoogleAdsAPI()

# ============================================================================
# CAMPAIGN OPERATIONS
# ============================================================================

@tool
def get_campaigns(customer_id: str, access_token: str, status_filter: str = "ALL", user_id: int = None) -> Dict[str, Any]:
    """
    Get all campaigns for a customer.
    
    Args:
        customer_id: Google Ads customer ID (e.g., "9631603999")
        access_token: OAuth2 access token
        status_filter: Campaign status filter (ALL, ENABLED, PAUSED, REMOVED)
        user_id: User ID for token refresh on 401 errors
    
    Returns:
        Campaign data with metrics
    """
    try:
        # Build GAQL query
        query = f"""
        SELECT 
            campaign.id, 
            campaign.name, 
            campaign.status, 
            campaign.advertising_channel_type,
            campaign.advertising_channel_sub_type,
            campaign.start_date,
            campaign.end_date,
            metrics.impressions, 
            metrics.clicks, 
            metrics.ctr, 
            metrics.conversions,
            metrics.cost_micros,
            metrics.average_cpc,
            metrics.value_per_conversion
        FROM campaign 
        WHERE segments.date DURING LAST_30_DAYS
        """
        
        if status_filter != "ALL":
            query += f" AND campaign.status = {status_filter}"
        
        query += " ORDER BY metrics.impressions DESC"
        
        result = google_ads_api.search(customer_id, access_token, query, user_id)
        
        if "error" in result:
            return {"success": False, "error": result["error"]}
        
        campaigns = []
        for row in result.get("results", []):
            campaign_data = row.get("campaign", {})
            metrics_data = row.get("metrics", {})
            
            campaigns.append({
                "id": campaign_data.get("id"),
                "name": campaign_data.get("name"),
                "status": campaign_data.get("status"),
                "advertising_channel_type": campaign_data.get("advertisingChannelType"),
                "advertising_channel_sub_type": campaign_data.get("advertisingChannelSubType"),
                "start_date": campaign_data.get("startDate"),
                "end_date": campaign_data.get("endDate"),
                "impressions": metrics_data.get("impressions"),
                "clicks": metrics_data.get("clicks"),
                "ctr": metrics_data.get("ctr"),
                "conversions": metrics_data.get("conversions"),
                "cost_micros": metrics_data.get("costMicros"),
                "average_cpc": metrics_data.get("averageCpc"),
                "value_per_conversion": metrics_data.get("valuePerConversion")
            })
        
        return {
            "success": True,
            "campaigns": campaigns,
            "total_count": len(campaigns),
            "query": query
        }
        
    except Exception as e:
        logger.error(f"Error getting campaigns: {e}")
        return {"success": False, "error": str(e)}

@tool
def get_campaign_by_id(customer_id: str, access_token: str, campaign_id: str, user_id: int = None) -> Dict[str, Any]:
    """
    Get specific campaign by ID.
    
    Args:
        customer_id: Google Ads customer ID
        access_token: OAuth2 access token
        campaign_id: Campaign ID to retrieve
    
    Returns:
        Campaign details with metrics
    """
    try:
        query = f"""
        SELECT 
            campaign.id, 
            campaign.name, 
            campaign.status, 
            campaign.advertising_channel_type,
            campaign.advertising_channel_sub_type,
            campaign.start_date,
            campaign.end_date,
            campaign.budget,
            campaign.target_cpa.target_cpa_micros,
            campaign.target_roas.target_roas,
            metrics.impressions, 
            metrics.clicks, 
            metrics.ctr, 
            metrics.conversions,
            metrics.cost_micros,
            metrics.average_cpc,
            metrics.value_per_conversion,
            metrics.cost_per_conversion
        FROM campaign 
        WHERE campaign.id = {campaign_id}
        AND segments.date DURING LAST_30_DAYS
        """
        
        result = google_ads_api.search(customer_id, access_token, query, user_id)
        
        if "error" in result:
            return {"success": False, "error": result["error"]}
        
        campaigns = result.get("results", [])
        if not campaigns:
            return {"success": False, "error": f"Campaign {campaign_id} not found"}
        
        row = campaigns[0]
        campaign_data = row.get("campaign", {})
        metrics_data = row.get("metrics", {})
        
        return {
            "success": True,
            "campaign": {
                "id": campaign_data.get("id"),
                "name": campaign_data.get("name"),
                "status": campaign_data.get("status"),
                "advertising_channel_type": campaign_data.get("advertisingChannelType"),
                "advertising_channel_sub_type": campaign_data.get("advertisingChannelSubType"),
                "start_date": campaign_data.get("startDate"),
                "end_date": campaign_data.get("endDate"),
                "budget": campaign_data.get("budget"),
                "target_cpa": campaign_data.get("targetCpa", {}).get("targetCpaMicros"),
                "target_roas": campaign_data.get("targetRoas", {}).get("targetRoas"),
                "impressions": metrics_data.get("impressions"),
                "clicks": metrics_data.get("clicks"),
                "ctr": metrics_data.get("ctr"),
                "conversions": metrics_data.get("conversions"),
                "cost_micros": metrics_data.get("costMicros"),
                "average_cpc": metrics_data.get("averageCpc"),
                "value_per_conversion": metrics_data.get("valuePerConversion"),
                "cost_per_conversion": metrics_data.get("costPerConversion")
            },
            "query": query
        }
        
    except Exception as e:
        logger.error(f"Error getting campaign by ID: {e}")
        return {"success": False, "error": str(e)}

# ============================================================================
# AD GROUP OPERATIONS
# ============================================================================

@tool
def get_ad_groups(customer_id: str, access_token: str, campaign_id: Optional[str] = None, user_id: int = None) -> Dict[str, Any]:
    """
    Get all ad groups for a customer or specific campaign.
    
    Args:
        customer_id: Google Ads customer ID
        access_token: OAuth2 access token
        campaign_id: Optional campaign ID to filter ad groups
    
    Returns:
        Ad group data with metrics
    """
    try:
        query = """
        SELECT 
            ad_group.id, 
            ad_group.name, 
            ad_group.status,
            ad_group.campaign,
            ad_group.type,
            ad_group.cpc_bid_micros,
            ad_group.target_cpa.target_cpa_micros,
            metrics.impressions, 
            metrics.clicks, 
            metrics.ctr, 
            metrics.conversions,
            metrics.cost_micros,
            metrics.average_cpc,
            metrics.value_per_conversion
        FROM ad_group 
        WHERE segments.date DURING LAST_30_DAYS
        """
        
        if campaign_id:
            query += f" AND ad_group.campaign = 'customers/{customer_id}/campaigns/{campaign_id}'"
        
        query += " ORDER BY metrics.impressions DESC"
        
        result = google_ads_api.search(customer_id, access_token, query, user_id)
        
        if "error" in result:
            return {"success": False, "error": result["error"]}
        
        ad_groups = []
        for row in result.get("results", []):
            ad_group_data = row.get("adGroup", {})
            metrics_data = row.get("metrics", {})
            
            ad_groups.append({
                "id": ad_group_data.get("id"),
                "name": ad_group_data.get("name"),
                "status": ad_group_data.get("status"),
                "campaign": ad_group_data.get("campaign"),
                "type": ad_group_data.get("type"),
                "cpc_bid_micros": ad_group_data.get("cpcBidMicros"),
                "target_cpa": ad_group_data.get("targetCpa", {}).get("targetCpaMicros"),
                "impressions": metrics_data.get("impressions"),
                "clicks": metrics_data.get("clicks"),
                "ctr": metrics_data.get("ctr"),
                "conversions": metrics_data.get("conversions"),
                "cost_micros": metrics_data.get("costMicros"),
                "average_cpc": metrics_data.get("averageCpc"),
                "value_per_conversion": metrics_data.get("valuePerConversion")
            })
        
        return {
            "success": True,
            "ad_groups": ad_groups,
            "total_count": len(ad_groups),
            "query": query
        }
        
    except Exception as e:
        logger.error(f"Error getting ad groups: {e}")
        return {"success": False, "error": str(e)}

# ============================================================================
# AD OPERATIONS
# ============================================================================

@tool
def get_ads(customer_id: str, access_token: str, ad_group_id: Optional[str] = None, user_id: int = None) -> Dict[str, Any]:
    """
    Get all ads for a customer or specific ad group.
    
    Args:
        customer_id: Google Ads customer ID
        access_token: OAuth2 access token
        ad_group_id: Optional ad group ID to filter ads
    
    Returns:
        Ad data with metrics
    """
    try:
        query = """
        SELECT 
            ad_group_ad.ad.id, 
            ad_group_ad.ad.name,
            ad_group_ad.ad.type,
            ad_group_ad.ad.final_urls,
            ad_group_ad.status,
            ad_group_ad.ad_group,
            metrics.impressions, 
            metrics.clicks, 
            metrics.ctr, 
            metrics.conversions,
            metrics.cost_micros,
            metrics.average_cpc,
            metrics.value_per_conversion
        FROM ad_group_ad 
        WHERE segments.date DURING LAST_30_DAYS
        """
        
        if ad_group_id:
            query += f" AND ad_group_ad.ad_group = 'customers/{customer_id}/adGroups/{ad_group_id}'"
        
        query += " ORDER BY metrics.impressions DESC"
        
        result = google_ads_api.search(customer_id, access_token, query, user_id)
        
        if "error" in result:
            return {"success": False, "error": result["error"]}
        
        ads = []
        for row in result.get("results", []):
            ad_group_ad_data = row.get("adGroupAd", {})
            ad_data = ad_group_ad_data.get("ad", {})
            metrics_data = row.get("metrics", {})
            
            ads.append({
                "id": ad_data.get("id"),
                "name": ad_data.get("name"),
                "type": ad_data.get("type"),
                "final_urls": ad_data.get("finalUrls", []),
                "status": ad_group_ad_data.get("status"),
                "ad_group": ad_group_ad_data.get("adGroup"),
                "impressions": metrics_data.get("impressions"),
                "clicks": metrics_data.get("clicks"),
                "ctr": metrics_data.get("ctr"),
                "conversions": metrics_data.get("conversions"),
                "cost_micros": metrics_data.get("costMicros"),
                "average_cpc": metrics_data.get("averageCpc"),
                "value_per_conversion": metrics_data.get("valuePerConversion")
            })
        
        return {
            "success": True,
            "ads": ads,
            "total_count": len(ads),
            "query": query
        }
        
    except Exception as e:
        logger.error(f"Error getting ads: {e}")
        return {"success": False, "error": str(e)}

# ============================================================================
# KEYWORD OPERATIONS
# ============================================================================

@tool
def get_keywords(customer_id: str, access_token: str, ad_group_id: Optional[str] = None, user_id: int = None) -> Dict[str, Any]:
    """
    Get all keywords for a customer or specific ad group.
    
    Args:
        customer_id: Google Ads customer ID
        access_token: OAuth2 access token
        ad_group_id: Optional ad group ID to filter keywords
    
    Returns:
        Keyword data with metrics
    """
    try:
        query = """
        SELECT 
            ad_group_criterion.criterion_id,
            ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type,
            ad_group_criterion.status,
            ad_group_criterion.quality_info.quality_score,
            ad_group_criterion.quality_info.search_predicted_ctr,
            ad_group_criterion.quality_info.creative_quality_score,
            ad_group_criterion.quality_info.post_click_quality_score,
            ad_group_criterion.cpc_bid_micros,
            ad_group_criterion.effective_cpc_bid_micros,
            metrics.impressions, 
            metrics.clicks, 
            metrics.ctr, 
            metrics.conversions,
            metrics.cost_micros,
            metrics.average_cpc,
            metrics.value_per_conversion,
            metrics.search_absolute_top_impression_share,
            metrics.search_top_impression_share
        FROM keyword_view 
        WHERE segments.date DURING LAST_30_DAYS
        """
        
        if ad_group_id:
            query += f" AND ad_group_criterion.ad_group = 'customers/{customer_id}/adGroups/{ad_group_id}'"
        
        query += " ORDER BY metrics.impressions DESC"
        
        result = google_ads_api.search(customer_id, access_token, query, user_id)
        
        if "error" in result:
            return {"success": False, "error": result["error"]}
        
        keywords = []
        for row in result.get("results", []):
            ad_group_criterion_data = row.get("adGroupCriterion", {})
            keyword_data = ad_group_criterion_data.get("keyword", {})
            quality_info = ad_group_criterion_data.get("qualityInfo", {})
            metrics_data = row.get("metrics", {})
            
            keywords.append({
                "criterion_id": ad_group_criterion_data.get("criterionId"),
                "text": keyword_data.get("text"),
                "match_type": keyword_data.get("matchType"),
                "status": ad_group_criterion_data.get("status"),
                "quality_score": quality_info.get("qualityScore"),
                "search_predicted_ctr": quality_info.get("searchPredictedCtr"),
                "creative_quality_score": quality_info.get("creativeQualityScore"),
                "post_click_quality_score": quality_info.get("postClickQualityScore"),
                "cpc_bid_micros": ad_group_criterion_data.get("cpcBidMicros"),
                "effective_cpc_bid_micros": ad_group_criterion_data.get("effectiveCpcBidMicros"),
                "impressions": metrics_data.get("impressions"),
                "clicks": metrics_data.get("clicks"),
                "ctr": metrics_data.get("ctr"),
                "conversions": metrics_data.get("conversions"),
                "cost_micros": metrics_data.get("costMicros"),
                "average_cpc": metrics_data.get("averageCpc"),
                "value_per_conversion": metrics_data.get("valuePerConversion"),
                "search_absolute_top_impression_share": metrics_data.get("searchAbsoluteTopImpressionShare"),
                "search_top_impression_share": metrics_data.get("searchTopImpressionShare")
            })
        
        return {
            "success": True,
            "keywords": keywords,
            "total_count": len(keywords),
            "query": query
        }
        
    except Exception as e:
        logger.error(f"Error getting keywords: {e}")
        return {"success": False, "error": str(e)}

# ============================================================================
# PERFORMANCE OPERATIONS
# ============================================================================

@tool
def get_performance_data(customer_id: str, access_token: str, date_range: str = "LAST_30_DAYS", 
                        campaign_id: Optional[str] = None, ad_group_id: Optional[str] = None, user_id: int = None) -> Dict[str, Any]:
    """
    Get performance data for campaigns, ad groups, or overall account.
    
    Args:
        customer_id: Google Ads customer ID
        access_token: OAuth2 access token
        date_range: Date range (LAST_7_DAYS, LAST_30_DAYS, LAST_90_DAYS, etc.)
        campaign_id: Optional campaign ID to filter
        ad_group_id: Optional ad group ID to filter
    
    Returns:
        Performance metrics and data
    """
    try:
        if ad_group_id:
            # Ad group level performance
            query = f"""
            SELECT 
                ad_group.id,
                ad_group.name,
                ad_group.status,
                ad_group.campaign,
                segments.date,
                segments.device,
                metrics.impressions,
                metrics.clicks,
                metrics.ctr,
                metrics.conversions,
                metrics.cost_micros,
                metrics.average_cpc,
                metrics.value_per_conversion,
                metrics.cost_per_conversion,
                metrics.search_impression_share,
                metrics.search_rank_lost_impression_share
            FROM ad_group 
            WHERE segments.date DURING {date_range}
            AND ad_group.id = {ad_group_id}
            ORDER BY segments.date DESC
            """
            
        elif campaign_id:
            # Campaign level performance
            query = f"""
            SELECT 
                campaign.id,
                campaign.name,
                campaign.status,
                campaign.advertising_channel_type,
                segments.date,
                segments.device,
                metrics.impressions,
                metrics.clicks,
                metrics.ctr,
                metrics.conversions,
                metrics.cost_micros,
                metrics.average_cpc,
                metrics.value_per_conversion,
                metrics.cost_per_conversion,
                metrics.search_impression_share,
                metrics.search_rank_lost_impression_share
            FROM campaign 
            WHERE segments.date DURING {date_range}
            AND campaign.id = {campaign_id}
            ORDER BY segments.date DESC
            """
            
        else:
            # Account level performance
            query = f"""
            SELECT 
                customer.id,
                customer.descriptive_name,
                segments.date,
                segments.device,
                metrics.impressions,
                metrics.clicks,
                metrics.ctr,
                metrics.conversions,
                metrics.cost_micros,
                metrics.average_cpc,
                metrics.value_per_conversion,
                metrics.cost_per_conversion,
                metrics.search_impression_share,
                metrics.search_rank_lost_impression_share
            FROM customer 
            WHERE segments.date DURING {date_range}
            ORDER BY segments.date DESC
            """
        
        result = google_ads_api.search(customer_id, access_token, query, user_id)
        
        if "error" in result:
            return {"success": False, "error": result["error"]}
        
        performance_data = []
        for row in result.get("results", []):
            metrics_data = row.get("metrics", {})
            segments_data = row.get("segments", {})
            
            # Get entity data (campaign, ad_group, or customer)
            entity_data = {}
            if "campaign" in row:
                entity_data = row.get("campaign", {})
            elif "adGroup" in row:
                entity_data = row.get("adGroup", {})
            elif "customer" in row:
                entity_data = row.get("customer", {})
            
            performance_data.append({
                "entity_id": entity_data.get("id"),
                "entity_name": entity_data.get("name") or entity_data.get("descriptiveName"),
                "entity_status": entity_data.get("status"),
                "advertising_channel_type": entity_data.get("advertisingChannelType"),
                "date": segments_data.get("date"),
                "device": segments_data.get("device"),
                "network_type": segments_data.get("networkType"),
                "impressions": metrics_data.get("impressions"),
                "clicks": metrics_data.get("clicks"),
                "ctr": metrics_data.get("ctr"),
                "conversions": metrics_data.get("conversions"),
                "cost_micros": metrics_data.get("costMicros"),
                "average_cpc": metrics_data.get("averageCpc"),
                "value_per_conversion": metrics_data.get("valuePerConversion"),
                "cost_per_conversion": metrics_data.get("costPerConversion"),
                "search_impression_share": metrics_data.get("searchImpressionShare"),
                "search_rank_lost_impression_share": metrics_data.get("searchRankLostImpressionShare")
            })
        
        return {
            "success": True,
            "performance_data": performance_data,
            "total_count": len(performance_data),
            "date_range": date_range,
            "query": query
        }
        
    except Exception as e:
        logger.error(f"Error getting performance data: {e}")
        return {"success": False, "error": str(e)}

# ============================================================================
# BUDGET OPERATIONS
# ============================================================================

@tool
def get_budgets(customer_id: str, access_token: str, user_id: int = None) -> Dict[str, Any]:
    """
    Get all budgets for a customer.
    
    Args:
        customer_id: Google Ads customer ID
        access_token: OAuth2 access token
    
    Returns:
        Budget data with usage information
    """
    try:
        query = """
        SELECT 
            campaign_budget.id,
            campaign_budget.name,
            campaign_budget.delivery_method,
            campaign_budget.period,
            campaign_budget.amount_micros,
            campaign_budget.type,
            campaign_budget.reference_count,
            campaign_budget.has_recommended_budget,
            campaign_budget.recommended_budget_amount_micros,
            campaign_budget.status,
            campaign_budget.explicitly_shared
        FROM campaign_budget 
        ORDER BY campaign_budget.id
        """
        
        result = google_ads_api.search(customer_id, access_token, query, user_id)
        
        if "error" in result:
            return {"success": False, "error": result["error"]}
        
        budgets = []
        for row in result.get("results", []):
            budget_data = row.get("campaignBudget", {})
            
            budgets.append({
                "id": budget_data.get("id"),
                "name": budget_data.get("name"),
                "delivery_method": budget_data.get("deliveryMethod"),
                "period": budget_data.get("period"),
                "amount_micros": budget_data.get("amountMicros"),
                "type": budget_data.get("type"),
                "reference_count": budget_data.get("referenceCount"),
                "has_recommended_budget": budget_data.get("hasRecommendedBudget"),
                "recommended_budget_amount_micros": budget_data.get("recommendedBudgetAmountMicros"),
                "status": budget_data.get("status"),
                "explicitly_shared": budget_data.get("explicitlyShared")
            })
        
        return {
            "success": True,
            "budgets": budgets,
            "total_count": len(budgets),
            "query": query
        }
        
    except Exception as e:
        logger.error(f"Error getting budgets: {e}")
        return {"success": False, "error": str(e)}

# ============================================================================
# ACCOUNT OPERATIONS
# ============================================================================

@tool
def get_account_overview(customer_id: str, access_token: str, user_id: int = None) -> Dict[str, Any]:
    """
    Get account overview with key metrics and information.
    
    Args:
        customer_id: Google Ads customer ID
        access_token: OAuth2 access token
    
    Returns:
        Account overview data
    """
    try:
        # Get customer information
        customer_query = """
        SELECT 
            customer.id,
            customer.descriptive_name,
            customer.currency_code,
            customer.time_zone,
            customer.tracking_url_template,
            customer.final_url_suffix,
            customer.auto_tagging_enabled,
            customer.has_partners_badge,
            customer.manager,
            customer.test_account
        FROM customer
        """
        
        customer_result = google_ads_api.search(customer_id, access_token, customer_query, user_id)
        
        # Get account performance metrics
        metrics_query = """
        SELECT 
            metrics.impressions,
            metrics.clicks,
            metrics.ctr,
            metrics.conversions,
            metrics.cost_micros,
            metrics.average_cpc,
            metrics.value_per_conversion,
            metrics.cost_per_conversion,
            metrics.search_impression_share,
            metrics.search_rank_lost_impression_share,
        FROM customer 
        WHERE segments.date DURING LAST_30_DAYS
        """
        
        metrics_result = google_ads_api.search(customer_id, access_token, metrics_query, user_id)
        
        if "error" in customer_result:
            return {"success": False, "error": customer_result["error"]}
        
        if "error" in metrics_result:
            return {"success": False, "error": metrics_result["error"]}
        
        # Process customer data
        customer_data = {}
        if customer_result.get("results"):
            customer_row = customer_result["results"][0]
            customer_info = customer_row.get("customer", {})
            customer_data = {
                "id": customer_info.get("id"),
                "descriptive_name": customer_info.get("descriptiveName"),
                "currency_code": customer_info.get("currencyCode"),
                "time_zone": customer_info.get("timeZone"),
                "tracking_url_template": customer_info.get("trackingUrlTemplate"),
                "final_url_suffix": customer_info.get("finalUrlSuffix"),
                "auto_tagging_enabled": customer_info.get("autoTaggingEnabled"),
                "has_partners_badge": customer_info.get("hasPartnersBadge"),
                "manager": customer_info.get("manager"),
                "test_account": customer_info.get("testAccount")
            }
        
        # Process metrics data
        metrics_data = {}
        total_metrics = {}
        for row in metrics_result.get("results", []):
            metrics = row.get("metrics", {})
            for key, value in metrics.items():
                if value is not None:
                    total_metrics[key] = total_metrics.get(key, 0) + value
        
        metrics_data = {
            "impressions": total_metrics.get("impressions", 0),
            "clicks": total_metrics.get("clicks", 0),
            "ctr": total_metrics.get("ctr", 0),
            "conversions": total_metrics.get("conversions", 0),
            "cost_micros": total_metrics.get("costMicros", 0),
            "average_cpc": total_metrics.get("averageCpc", 0),
            "value_per_conversion": total_metrics.get("valuePerConversion", 0),
            "cost_per_conversion": total_metrics.get("costPerConversion", 0),
            "search_impression_share": total_metrics.get("searchImpressionShare", 0),
            "search_rank_lost_impression_share": total_metrics.get("searchRankLostImpressionShare", 0),
        }
        
        return {
            "success": True,
            "customer": customer_data,
            "metrics": metrics_data,
            "query": customer_query + " | " + metrics_query
        }
        
    except Exception as e:
        logger.error(f"Error getting account overview: {e}")
        return {"success": False, "error": str(e)}

# ============================================================================
# SEARCH TERM OPERATIONS
# ============================================================================

@tool
def get_search_terms(customer_id: str, access_token: str, campaign_id: Optional[str] = None, 
                    ad_group_id: Optional[str] = None, user_id: int = None) -> Dict[str, Any]:
    """
    Get search terms that triggered ads.
    
    Args:
        customer_id: Google Ads customer ID
        access_token: OAuth2 access token
        campaign_id: Optional campaign ID to filter
        ad_group_id: Optional ad group ID to filter
    
    Returns:
        Search term data with metrics
    """
    try:
        query = """
        SELECT 
            search_term_view.search_term,
            search_term_view.status,
            search_term_view.ad_group,
            search_term_view.campaign,
            metrics.impressions,
            metrics.clicks,
            metrics.ctr,
            metrics.conversions,
            metrics.cost_micros,
            metrics.average_cpc,
            metrics.value_per_conversion,
            metrics.cost_per_conversion
        FROM search_term_view 
        WHERE segments.date DURING LAST_30_DAYS
        """
        
        if campaign_id:
            query += f" AND search_term_view.campaign = 'customers/{customer_id}/campaigns/{campaign_id}'"
        
        if ad_group_id:
            query += f" AND search_term_view.ad_group = 'customers/{customer_id}/adGroups/{ad_group_id}'"
        
        query += " ORDER BY metrics.impressions DESC"
        
        result = google_ads_api.search(customer_id, access_token, query, user_id)
        
        if "error" in result:
            return {"success": False, "error": result["error"]}
        
        search_terms = []
        for row in result.get("results", []):
            search_term_view_data = row.get("searchTermView", {})
            metrics_data = row.get("metrics", {})
            
            search_terms.append({
                "search_term": search_term_view_data.get("searchTerm"),
                "status": search_term_view_data.get("status"),
                "ad_group": search_term_view_data.get("adGroup"),
                "campaign": search_term_view_data.get("campaign"),
                "impressions": metrics_data.get("impressions"),
                "clicks": metrics_data.get("clicks"),
                "ctr": metrics_data.get("ctr"),
                "conversions": metrics_data.get("conversions"),
                "cost_micros": metrics_data.get("costMicros"),
                "average_cpc": metrics_data.get("averageCpc"),
                "value_per_conversion": metrics_data.get("valuePerConversion"),
                "cost_per_conversion": metrics_data.get("costPerConversion")
            })
        
        return {
            "success": True,
            "search_terms": search_terms,
            "total_count": len(search_terms),
            "query": query
        }
        
    except Exception as e:
        logger.error(f"Error getting search terms: {e}")
        return {"success": False, "error": str(e)}

# ============================================================================
# DEMOGRAPHIC OPERATIONS
# ============================================================================

@tool
def get_demographic_data(customer_id: str, access_token: str, campaign_id: Optional[str] = None, user_id: int = None) -> Dict[str, Any]:
    """
    Get demographic performance data.
    
    Args:
        customer_id: Google Ads customer ID
        access_token: OAuth2 access token
        campaign_id: Optional campaign ID to filter
    
    Returns:
        Demographic data with metrics
    """
    try:
        query = """
        SELECT 
            campaign.id,
            campaign.name,
            segments.date,
            metrics.impressions,
            metrics.clicks,
            metrics.ctr,
            metrics.conversions,
            metrics.cost_micros,
            metrics.average_cpc,
            metrics.value_per_conversion,
            metrics.cost_per_conversion
        FROM campaign 
        WHERE segments.date DURING LAST_30_DAYS
        """
        
        if campaign_id:
            query += f" AND campaign.id = {campaign_id}"
        
        query += " ORDER BY metrics.impressions DESC"
        
        result = google_ads_api.search(customer_id, access_token, query, user_id)
        
        if "error" in result:
            return {"success": False, "error": result["error"]}
        
        demographic_data = []
        for row in result.get("results", []):
            segments_data = row.get("segments", {})
            campaign_data = row.get("campaign", {})
            metrics_data = row.get("metrics", {})
            
            demographic_data.append({
                "date": segments_data.get("date"),
                "campaign_id": campaign_data.get("id"),
                "campaign_name": campaign_data.get("name"),
                "impressions": metrics_data.get("impressions"),
                "clicks": metrics_data.get("clicks"),
                "ctr": metrics_data.get("ctr"),
                "conversions": metrics_data.get("conversions"),
                "cost_micros": metrics_data.get("costMicros"),
                "average_cpc": metrics_data.get("averageCpc"),
                "value_per_conversion": metrics_data.get("valuePerConversion"),
                "cost_per_conversion": metrics_data.get("costPerConversion")
            })
        
        return {
            "success": True,
            "demographic_data": demographic_data,
            "total_count": len(demographic_data),
            "query": query
        }
        
    except Exception as e:
        logger.error(f"Error getting demographic data: {e}")
        return {"success": False, "error": str(e)}

# ============================================================================
# GEOGRAPHIC OPERATIONS
# ============================================================================

@tool
def get_geographic_data(customer_id: str, access_token: str, campaign_id: Optional[str] = None, user_id: int = None) -> Dict[str, Any]:
    """
    Get campaign performance data by date (simplified geographic data function).
    
    Args:
        customer_id: Google Ads customer ID
        access_token: OAuth2 access token
        campaign_id: Optional campaign ID to filter
    
    Returns:
        Campaign performance data with metrics by date
    """
    try:
        query = """
        SELECT 
            campaign.id,
            campaign.name,
            segments.date,
            metrics.impressions,
            metrics.clicks,
            metrics.ctr,
            metrics.conversions,
            metrics.cost_micros,
            metrics.average_cpc,
            metrics.value_per_conversion,
            metrics.cost_per_conversion
        FROM campaign 
        WHERE segments.date DURING LAST_30_DAYS
        """
        
        if campaign_id:
            query += f" AND campaign.id = {campaign_id}"
        
        query += " ORDER BY metrics.impressions DESC"
        
        result = google_ads_api.search(customer_id, access_token, query, user_id)
        
        if "error" in result:
            return {"success": False, "error": result["error"]}
        
        geographic_data = []
        for row in result.get("results", []):
            segments_data = row.get("segments", {})
            campaign_data = row.get("campaign", {})
            metrics_data = row.get("metrics", {})
            
            geographic_data.append({
                "campaign_id": campaign_data.get("id"),
                "campaign_name": campaign_data.get("name"),
                "date": segments_data.get("date"),
                "impressions": metrics_data.get("impressions"),
                "clicks": metrics_data.get("clicks"),
                "ctr": metrics_data.get("ctr"),
                "conversions": metrics_data.get("conversions"),
                "cost_micros": metrics_data.get("costMicros"),
                "average_cpc": metrics_data.get("averageCpc"),
                "value_per_conversion": metrics_data.get("valuePerConversion"),
                "cost_per_conversion": metrics_data.get("costPerConversion")
            })
        
        return {
            "success": True,
            "geographic_data": geographic_data,
            "total_count": len(geographic_data),
            "query": query
        }
        
    except Exception as e:
        logger.error(f"Error getting geographic data: {e}")
        return {"success": False, "error": str(e)}

# ============================================================================
# IMAGE GENERATION OPERATIONS
# ============================================================================

@tool
def generate_image(query: str, previous_image_url: str = None, user_id: int = None) -> Dict[str, Any]:
    """
    Generate images using OpenAI's image generation API.
    
    Args:
        query: Description of the image to generate
        previous_image_url: Optional URL of previous image for improvements/edits
        user_id: User ID for tracking
    
    Returns:
        Generated image data with URL and metadata
    """
    try:
        from openai import OpenAI
        import base64
        import os
        from datetime import datetime
        
        # Initialize OpenAI client
        client = OpenAI()
        
        # Prepare the input for image generation
        if previous_image_url:
            # If we have a previous image, we're doing an improvement/edit
            image_input = f"Improve this image: {previous_image_url}. User request: {query}"
        else:
            # New image generation
            image_input = query
        
        logger.info(f"Generating image with query: {image_input}")
        
        # Generate image using OpenAI API
        # Note: Using DALL-E 3 for image generation as GPT-5 requires organization verification
        try:
            response = client.responses.create(
                model="gpt-5",
                input=image_input,
                tools=[{"type": "image_generation"}],
            )
        except Exception as e:
            if "gpt-5" in str(e) or "organization must be verified" in str(e):
                # Fallback to DALL-E 3 if GPT-5 is not available
                logger.info("GPT-5 not available, using DALL-E 3 for image generation")
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=image_input,
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
                
                # Convert DALL-E response to expected format
                if response.data and len(response.data) > 0:
                    # Get the direct DALL-E image URL (this is the ChatGPT image URL)
                    dalle_image_url = response.data[0].url
                    
                    # Also save a local copy for backup
                    import requests
                    img_response = requests.get(dalle_image_url)
                    image_base64 = base64.b64encode(img_response.content).decode('utf-8')
                    
                    # Generate unique filename for local backup
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"generated_image_{timestamp}.png"
                    
                    # Create images directory if it doesn't exist
                    images_dir = "generated_images"
                    os.makedirs(images_dir, exist_ok=True)
                    
                    # Save image to file as backup
                    image_path = os.path.join(images_dir, filename)
                    with open(image_path, "wb") as f:
                        f.write(base64.b64decode(image_base64))
                    
                    return {
                        "success": True,
                        "image_url": dalle_image_url,  # Return the direct DALL-E URL
                        "local_backup_url": f"/static/{images_dir}/{filename}",  # Local backup URL
                        "image_path": image_path,
                        "filename": filename,
                        "query": query,
                        "previous_image_url": previous_image_url,
                        "generated_at": datetime.now().isoformat(),
                        "user_id": user_id,
                        "model_used": "dall-e-3"
                    }
                else:
                    return {
                        "success": False,
                        "error": "No image data received from DALL-E 3 API"
                    }
            else:
                raise e
        
        # Extract image data from response
        image_data = [
            output.result
            for output in response.output
            if output.type == "image_generation_call"
        ]
        
        if not image_data:
            return {
                "success": False,
                "error": "No image data received from OpenAI API"
            }
        
        # Get the base64 image data
        image_base64 = image_data[0]
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_image_{timestamp}.png"
        
        # Create images directory if it doesn't exist
        images_dir = "generated_images"
        os.makedirs(images_dir, exist_ok=True)
        
        # Save image to file
        image_path = os.path.join(images_dir, filename)
        with open(image_path, "wb") as f:
            f.write(base64.b64decode(image_base64))
        
        # For GPT-5, we'll use the local URL since it returns base64 data
        # But we'll also provide a way to get the direct URL if available
        image_url = f"/static/{images_dir}/{filename}"
        
        return {
            "success": True,
            "image_url": image_url,
            "image_path": image_path,
            "filename": filename,
            "query": query,
            "previous_image_url": previous_image_url,
            "generated_at": datetime.now().isoformat(),
            "user_id": user_id
        }
        
    except ImportError:
        return {
            "success": False,
            "error": "OpenAI library not installed. Please install with: pip install openai"
        }
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@tool
def improve_image(improvement_query: str, original_image_url: str, user_id: int = None) -> Dict[str, Any]:
    """
    Improve or modify an existing generated image based on user feedback.
    
    Args:
        improvement_query: Description of improvements to make
        original_image_url: URL of the original image to improve
        user_id: User ID for tracking
    
    Returns:
        Improved image data with URL and metadata
    """
    try:
        # Use the generate_image tool with the previous image URL
        return generate_image.invoke({
            "query": improvement_query,
            "previous_image_url": original_image_url,
            "user_id": user_id
        })
        
    except Exception as e:
        logger.error(f"Error improving image: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@tool
def create_data_visualization(data: str, visualization_type: str, title: str = None, user_id: int = None) -> Dict[str, Any]:
    """
    Create data visualizations (pie charts, bar graphs, tables) using ChatGPT's visualization capabilities.
    
    Args:
        data: The data to visualize (JSON string, CSV, or structured text)
        visualization_type: Type of visualization ('pie_chart', 'bar_graph', 'table', 'line_chart')
        title: Optional title for the visualization
        user_id: User ID for tracking
    
    Returns:
        Visualization data with image URL and metadata
    """
    try:
        from openai import OpenAI
        import json
        from datetime import datetime
        
        # Initialize OpenAI client
        client = OpenAI()
        
        # Create visualization prompt based on type
        if visualization_type == "pie_chart":
            prompt = f"Create a professional pie chart visualization for the following data. Make it colorful and easy to read. Title: {title or 'Data Distribution'}\n\nData: {data}"
        elif visualization_type == "bar_graph":
            prompt = f"Create a professional bar graph visualization for the following data. Use different colors for each bar. Title: {title or 'Data Comparison'}\n\nData: {data}"
        elif visualization_type == "line_chart":
            prompt = f"Create a professional line chart visualization for the following data. Show trends clearly. Title: {title or 'Data Trends'}\n\nData: {data}"
        elif visualization_type == "table":
            prompt = f"Create a well-formatted table visualization for the following data. Make it clean and professional. Title: {title or 'Data Table'}\n\nData: {data}"
        else:
            prompt = f"Create a professional {visualization_type} visualization for the following data. Title: {title or 'Data Visualization'}\n\nData: {data}"
        
        logger.info(f"Creating {visualization_type} visualization with title: {title}")
        
        # Generate visualization using DALL-E 3
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        if response.data and len(response.data) > 0:
            # Get the direct DALL-E image URL
            visualization_url = response.data[0].url
            
            # Also save a local copy for backup
            import requests
            img_response = requests.get(visualization_url)
            import base64
            image_base64 = base64.b64encode(img_response.content).decode('utf-8')
            
            # Generate unique filename for local backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"visualization_{visualization_type}_{timestamp}.png"
            
            # Create visualizations directory if it doesn't exist
            viz_dir = "generated_visualizations"
            os.makedirs(viz_dir, exist_ok=True)
            
            # Save image to file as backup
            image_path = os.path.join(viz_dir, filename)
            with open(image_path, "wb") as f:
                f.write(base64.b64decode(image_base64))
            
            return {
                "success": True,
                "visualization_url": visualization_url,
                "local_backup_url": f"/static/{viz_dir}/{filename}",
                "image_path": image_path,
                "filename": filename,
                "visualization_type": visualization_type,
                "title": title,
                "data": data,
                "generated_at": datetime.now().isoformat(),
                "user_id": user_id,
                "model_used": "dall-e-3"
            }
        else:
            return {
                "success": False,
                "error": "No visualization data received from DALL-E 3 API"
            }
        
    except ImportError:
        return {
            "success": False,
            "error": "OpenAI library not installed. Please install with: pip install openai"
        }
    except Exception as e:
        logger.error(f"Error creating visualization: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@tool
def format_tabular_data(data: str, format_type: str = "markdown", title: str = None, user_id: int = None) -> Dict[str, Any]:
    """
    Format data into well-structured tables using ChatGPT's formatting capabilities.
    
    Args:
        data: The data to format (JSON string, CSV, or structured text)
        format_type: Output format ('markdown', 'html', 'json', 'csv')
        title: Optional title for the table
        user_id: User ID for tracking
    
    Returns:
        Formatted table data
    """
    try:
        from openai import OpenAI
        import json
        from datetime import datetime
        
        # Initialize OpenAI client
        client = OpenAI()
        
        # Create formatting prompt
        prompt = f"""Format the following data into a well-structured {format_type} table. 
        Make it clean, professional, and easy to read. 
        Title: {title or 'Data Table'}
        
        Data to format:
        {data}
        
        Please provide only the formatted table, no additional text."""
        
        logger.info(f"Formatting data as {format_type} table with title: {title}")
        
        # Use ChatGPT to format the data
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a data formatting expert. Format data into clean, professional tables."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.1
        )
        
        formatted_table = response.choices[0].message.content.strip()
        
        return {
            "success": True,
            "formatted_table": formatted_table,
            "format_type": format_type,
            "title": title,
            "original_data": data,
            "generated_at": datetime.now().isoformat(),
            "user_id": user_id,
            "model_used": "gpt-4o"
        }
        
    except ImportError:
        return {
            "success": False,
            "error": "OpenAI library not installed. Please install with: pip install openai"
        }
    except Exception as e:
        logger.error(f"Error formatting tabular data: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# ============================================================================
# EXPORT ALL TOOLS
# ============================================================================

# List of all available tools
ALL_TOOLS = [
    get_campaigns,
    get_campaign_by_id,
    get_ad_groups,
    get_ads,
    get_keywords,
    get_performance_data,
    get_budgets,
    get_account_overview,
    get_search_terms,
    get_demographic_data,
    get_geographic_data,
    generate_image,
    improve_image,
    create_data_visualization,
    format_tabular_data
]

# Tool mapping for easy access
TOOL_MAPPING = {
    "get_campaigns": get_campaigns,
    "get_campaign_by_id": get_campaign_by_id,
    "get_ad_groups": get_ad_groups,
    "get_ads": get_ads,
    "get_keywords": get_keywords,
    "get_performance_data": get_performance_data,
    "get_budgets": get_budgets,
    "get_account_overview": get_account_overview,
    "get_search_terms": get_search_terms,
    "get_demographic_data": get_demographic_data,
    "get_geographic_data": get_geographic_data,
    "generate_image": generate_image,
    "improve_image": improve_image,
    "create_data_visualization": create_data_visualization,
    "format_tabular_data": format_tabular_data
}

logger.info(f"Loaded {len(ALL_TOOLS)} Google Ads tools with GAQL queries")

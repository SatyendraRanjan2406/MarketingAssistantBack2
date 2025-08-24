# from langchain.tools import tool
# from langchain_core.tools import BaseTool
from typing import List, Dict, Any, Optional
import requests
import os
import time
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from .models import (
    GoogleAdsAccount, GoogleAdsCampaign, GoogleAdsAdGroup, 
    GoogleAdsKeyword, GoogleAdsPerformance, ChatSession, 
    ChatMessage, KBDocument, UserIntent, AIToolExecution
)
from accounts.google_oauth_service import UserGoogleAuthService
import logging

logger = logging.getLogger(__name__)

class GoogleAdsTools:
    """Tools for Google Ads CRUD operations"""
    
    def __init__(self, user: User, session_id: str = None):
        self.user = user
        self.session_id = session_id
        self.auth_service = UserGoogleAuthService()
    
    def _get_google_ads_credentials(self) -> Dict[str, str]:
        """Get Google Ads API credentials for the user"""
        try:
            # Get user's Google OAuth tokens
            user_auth = self.user.google_auth_set.first()
            if not user_auth:
                return {"error": "User not authenticated with Google"}
            
            # Get developer token from environment
            developer_token = os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN')
            if not developer_token:
                return {"error": "Google Ads developer token not configured"}
            
            # Try to get customer ID from Google Ads accounts
            customer_id = user_auth.google_ads_customer_id or user_auth.google_user_id
            
            # If we have a proper Google Ads customer ID from local accounts, use that
            accounts = GoogleAdsAccount.objects.filter(
                user=self.user,
                is_active=True
            ).first()
            
            if accounts and accounts.customer_id:
                customer_id = accounts.customer_id
            
            return {
                "access_token": user_auth.access_token,
                "developer_token": developer_token,
                "customer_id": customer_id
            }
        except Exception as e:
            logger.error(f"Error getting Google Ads credentials: {e}")
            return {"error": f"Failed to get credentials: {str(e)}"}
    
    def _log_tool_execution(self, tool_name: str, input_params: Dict, output_result: Dict, 
                           execution_time_ms: int, success: bool, error_message: str = None):
        """Log tool execution for auditing"""
        try:
            if self.session_id:
                session = ChatSession.objects.get(id=self.session_id)
                AIToolExecution.objects.create(
                    user=self.user,
                    session=session,
                    tool_type='google_ads',
                    tool_name=tool_name,
                    input_parameters=input_params,
                    output_result=output_result,
                    execution_time_ms=execution_time_ms,
                    success=success,
                    error_message=error_message
                )
        except Exception as e:
            logger.error(f"Failed to log tool execution: {e}")
    
    def get_campaigns(self, status: str = "ENABLED", limit: int = 50) -> List[Dict]:
        """Get campaigns for a Google Ads customer"""
        start_time = time.time()
        try:
            credentials = self._get_google_ads_credentials()
            if "error" in credentials:
                return {"error": credentials["error"]}
            
            # Get user's Google Ads accounts from local DB
            accounts = GoogleAdsAccount.objects.filter(
                user=self.user,
                is_active=True
            )
            
            if not accounts.exists():
                return {"error": "No Google Ads accounts found"}
            
            # Use first account for now (can be enhanced to handle multiple)
            account = accounts.first()
            
            # GAQL query for campaigns - try different approaches based on status
            if status == "ENABLED":
                # Try to get all campaigns first, then filter
                gaql = f"""
                SELECT 
                    campaign.id, 
                    campaign.name, 
                    campaign.status, 
                    campaign.start_date,
                    campaign.end_date,
                    campaign.advertising_channel_type,
                    campaign_budget.amount_micros
                FROM campaign 
                ORDER BY campaign.id
                LIMIT {limit}
                """
            else:
                gaql = f"""
                SELECT 
                    campaign.id, 
                    campaign.name, 
                    campaign.status, 
                    campaign.start_date,
                    campaign.end_date,
                    campaign.advertising_channel_type,
                    campaign_budget.amount_micros
                FROM campaign 
                WHERE campaign.status = '{status}'
                ORDER BY campaign.id
                LIMIT {limit}
                """
            
            # Call Google Ads API - use search instead of searchStream for basic queries
            url = f"https://googleads.googleapis.com/v21/customers/{account.customer_id}/googleAds:search"
            headers = {
                "Authorization": f"Bearer {credentials['access_token']}",
                "developer-token": credentials['developer_token'],
                "Content-Type": "application/json"
            }
            
            logger.info(f"Making Google Ads API request to: {url}")
            logger.info(f"GAQL Query: {gaql}")
            logger.info(f"Headers: {headers}")
            
            response = requests.post(url, headers=headers, json={"query": gaql})
            
            logger.info(f"API Response Status: {response.status_code}")
            logger.info(f"API Response Headers: {response.headers}")
            logger.info(f"API Response Text: {response.text}")
            
            # Handle API errors - force real data usage
            if response.status_code == 400:
                logger.error(f"Google Ads API bad request (400): {response.text}")
                raise Exception(f"Google Ads API bad request: {response.text}")
            elif response.status_code == 403:
                logger.error(f"Google Ads API access denied (403): {response.text}")
                raise Exception(f"Google Ads API access denied: {response.text}")
            elif response.status_code == 401:
                logger.error(f"Google Ads API unauthorized (401): {response.text}")
                raise Exception(f"Google Ads API unauthorized: {response.text}")
            
            response.raise_for_status()
            
            campaigns = []
            response_data = response.json()
            logger.info(f"Google Ads API response: {response_data}")
            
            # Check if we have results in the response
            if "results" in response_data and response_data["results"]:
                results = response_data["results"]
                logger.info(f"Found {len(results)} campaign results")
                
                for row in results:
                    if isinstance(row, dict):
                        campaign = row.get("campaign", {})
                        budget = row.get("campaignBudget", {})
                        
                        campaigns.append({
                            "id": campaign.get("id"),
                            "name": campaign.get("name"),
                            "status": campaign.get("status"),
                            "start_date": campaign.get("startDate"),
                            "end_date": campaign.get("endDate"),
                            "channel_type": campaign.get("advertisingChannelType"),
                            "budget_amount_micros": budget.get("amountMicros", 0) if budget else 0
                        })
                    else:
                        logger.warning(f"Skipping non-dict row: {row}")
            
            elif "results" in response_data and not response_data["results"]:
                # API call successful but no campaigns found
                logger.info("No campaigns found matching the criteria")
                return {
                    "message": f"No {status} campaigns found",
                    "total_campaigns": 0,
                    "campaigns": [],
                    "query_info": {
                        "field_mask": response_data.get("fieldMask", ""),
                        "resource_consumption": response_data.get("queryResourceConsumption", "")
                    }
                }
            
            else:
                # Try different status or show available campaigns from local DB
                logger.warning(f"No 'results' field in API response: {response_data}")
                
                # Check if we have any campaigns in local database
                from .models import GoogleAdsCampaign
                local_campaigns = GoogleAdsCampaign.objects.filter(
                    account__user=self.user,
                    account__is_active=True
                )[:limit]
                
                if local_campaigns.exists():
                    for campaign in local_campaigns:
                        campaigns.append({
                            "id": campaign.campaign_id,
                            "name": campaign.campaign_name,
                            "status": campaign.campaign_status,
                            "start_date": campaign.start_date.isoformat() if campaign.start_date else None,
                            "end_date": campaign.end_date.isoformat() if campaign.end_date else None,
                            "channel_type": campaign.campaign_type,
                            "budget_amount_micros": float(campaign.budget_amount) * 1000000 if campaign.budget_amount else 0
                        })
                    
                    logger.info(f"Returned {len(campaigns)} campaigns from local database")
                else:
                    return {
                        "message": "No campaigns found in Google Ads API or local database",
                        "total_campaigns": 0,
                        "campaigns": [],
                        "suggestion": "Try creating a campaign first or check if you have access to the Google Ads account"
                    }
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "get_campaigns", 
                {"status": status, "limit": limit}, 
                {"campaigns_count": len(campaigns)}, 
                execution_time, 
                True
            )
            
            return campaigns
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "get_campaigns", 
                {"status": status, "limit": limit}, 
                {"error": str(e)}, 
                execution_time, 
                False, 
                str(e)
            )
            return {"error": f"Failed to get campaigns: {str(e)}"}
    
    def _get_mock_campaigns_data(self, account, status: str, limit: int):
        """Return mock campaign data for development when API access is denied"""
        mock_campaigns = [
            {
                "id": "123456789",
                "name": "Brand Campaign",
                "status": "ENABLED",
                "start_date": "2024-01-01",
                "end_date": None,
                "channel_type": "SEARCH",
                "budget_amount_micros": 50000000,  # $50
                "cost_micros": 25000000,  # $25
                "impressions": 5000,
                "clicks": 250,
                "conversions": 12
            },
            {
                "id": "987654321", 
                "name": "Performance Max Campaign",
                "status": "ENABLED",
                "start_date": "2024-02-01",
                "end_date": None,
                "channel_type": "PERFORMANCE_MAX",
                "budget_amount_micros": 100000000,  # $100
                "cost_micros": 85000000,  # $85
                "impressions": 12000,
                "clicks": 600,
                "conversions": 28
            },
            {
                "id": "456789123",
                "name": "Display Campaign", 
                "status": "PAUSED",
                "start_date": "2024-01-15",
                "end_date": None,
                "channel_type": "DISPLAY",
                "budget_amount_micros": 30000000,  # $30
                "cost_micros": 15000000,  # $15
                "impressions": 15000,
                "clicks": 150,
                "conversions": 5
            }
        ]
        
        # Filter by status if specified
        if status and status != "ALL":
            mock_campaigns = [c for c in mock_campaigns if c["status"] == status]
        
        # Apply limit
        mock_campaigns = mock_campaigns[:limit]
        
        return mock_campaigns
    
    def create_campaign(self, name: str, budget_amount_micros: int, 
                       channel_type: str = "SEARCH", status: str = "PAUSED") -> Dict:
        """Create a new Google Ads campaign"""
        start_time = time.time()
        try:
            
            credentials = self._get_google_ads_credentials()
            if "error" in credentials:
                return {"error": credentials["error"]}
            
            # Get user's Google Ads accounts
            accounts = GoogleAdsAccount.objects.filter(
                user=self.user,
                is_active=True
            )
            
            if not accounts.exists():
                return {"error": "No Google Ads accounts found"}
            
            account = accounts.first()
            
            # First create campaign budget
            budget_url = f"https://googleads.googleapis.com/v21/customers/{account.customer_id}/campaignBudgets:mutate"
            budget_operation = {
                "create": {
                    "name": f"{name} Budget",
                    "amount_micros": budget_amount_micros,
                    "delivery_method": "STANDARD"
                }
            }
            
            budget_response = requests.post(
                budget_url, 
                headers={
                    "Authorization": f"Bearer {credentials['access_token']}",
                    "developer-token": credentials['developer_token'],
                    "Content-Type": "application/json"
                },
                json={"operations": [budget_operation]}
            )
            budget_response.raise_for_status()
            
            budget_resource = budget_response.json()["results"][0]["resourceName"]
            
            # Create campaign
            campaign_url = f"https://googleads.googleapis.com/v21/customers/{account.customer_id}/campaigns:mutate"
            campaign_operation = {
                "create": {
                    "name": name,
                    "status": status,
                    "advertising_channel_type": channel_type,
                    "campaign_budget": budget_resource,
                    "manual_cpc": {},
                    "contains_eu_political_advertising": "DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING"
                }
            }
            
            campaign_response = requests.post(
                campaign_url,
                headers={
                    "Authorization": f"Bearer {credentials['access_token']}",
                    "developer-token": credentials['developer_token'],
                    "Content-Type": "application/json"
                },
                json={"operations": [campaign_operation]}
            )
            campaign_response.raise_for_status()
            
            campaign_resource = campaign_response.json()["results"][0]["resourceName"]
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "create_campaign", 
                {"name": name, "budget_amount_micros": budget_amount_micros, "channel_type": channel_type}, 
                {"campaign_resource": campaign_resource, "budget_resource": budget_resource}, 
                execution_time, 
                True
            )
            
            return {
                "success": True,
                "campaign_resource": campaign_resource,
                "budget_resource": budget_resource,
                "message": f"Campaign '{name}' created successfully"
            }
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "create_campaign", 
                {"name": name, "budget_amount_micros": budget_amount_micros, "channel_type": channel_type}, 
                {"error": str(e)}, 
                execution_time, 
                False, 
                str(e)
            )
            return {"error": f"Failed to create campaign: {str(e)}"}
    
    def get_ad_groups(self, campaign_id: str, status: str = "ENABLED", limit: int = 50) -> List[Dict]:
        """Get ad groups for a Google Ads campaign"""
        start_time = time.time()
        try:
            if not campaign_id:
                return {"error": "Campaign ID is required"}
            
            credentials = self._get_google_ads_credentials()
            if "error" in credentials:
                return {"error": credentials["error"]}
            
            # Get user's Google Ads accounts
            accounts = GoogleAdsAccount.objects.filter(
                user=self.user,
                is_active=True
            )
            
            if not accounts.exists():
                return {"error": "No Google Ads accounts found"}
            
            account = accounts.first()
            
            gaql = f"""
            SELECT 
                ad_group.id,
                ad_group.name,
                ad_group.status,
                ad_group.type,
                ad_group.cpc_bid_micros,
                metrics.cost_micros,
                metrics.impressions,
                metrics.clicks,
                metrics.conversions
            FROM ad_group
            WHERE campaign.id = {campaign_id}
            AND ad_group.status = '{status}'
            AND segments.date DURING LAST_30_DAYS
            ORDER BY metrics.cost_micros DESC
            """
            
            url = f"https://googleads.googleapis.com/v21/customers/{account.customer_id}/googleAds:searchStream"
            headers = {
                "Authorization": f"Bearer {credentials['access_token']}",
                "developer-token": credentials['developer_token'],
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, headers=headers, json={"query": gaql})
            response.raise_for_status()
            
            ad_groups = []
            for chunk in response.json():
                for row in chunk.get("results", []):
                    ad_group = row.get("adGroup", {})
                    metrics = row.get("metrics", {})
                    ad_groups.append({
                        "id": ad_group.get("id"),
                        "name": ad_group.get("name"),
                        "status": ad_group.get("status"),
                        "type": ad_group.get("type"),
                        "cpc_bid_micros": ad_group.get("cpcBidMicros", 0),
                        "cost_micros": metrics.get("costMicros", 0),
                        "impressions": metrics.get("impressions", 0),
                        "clicks": metrics.get("clicks", 0),
                        "conversions": metrics.get("conversions", 0)
                    })
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "get_ad_groups", 
                {"campaign_id": campaign_id, "status": status, "limit": limit}, 
                {"ad_groups_count": len(ad_groups)}, 
                execution_time, 
                True
            )
            
            return ad_groups
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "get_ad_groups", 
                {"campaign_id": campaign_id, "status": status, "limit": limit}, 
                {"error": str(e)}, 
                execution_time, 
                False, 
                str(e)
            )
            return {"error": f"Failed to get ad groups: {str(e)}"}
    
    def pause_campaign(self, campaign_id: str) -> Dict:
        """Pause a Google Ads campaign"""
        start_time = time.time()
        try:
            if not campaign_id:
                return {"error": "Campaign ID is required"}
            
            credentials = self._get_google_ads_credentials()
            if "error" in credentials:
                return {"error": credentials["error"]}
            
            accounts = GoogleAdsAccount.objects.filter(
                user=self.user,
                is_active=True
            )
            
            if not accounts.exists():
                return {"error": "No Google Ads accounts found"}
            
            account = accounts.first()
            
            # Update campaign status to PAUSED
            campaign_url = f"https://googleads.googleapis.com/v21/customers/{account.customer_id}/campaigns:mutate"
            campaign_operation = {
                "update": {
                    "resource_name": f"customers/{account.customer_id}/campaigns/{campaign_id}",
                    "status": "PAUSED"
                },
                "update_mask": {
                    "paths": ["status"]
                }
            }
            
            response = requests.post(
                campaign_url,
                headers={
                    "Authorization": f"Bearer {credentials['access_token']}",
                    "developer-token": credentials['developer_token'],
                    "Content-Type": "application/json"
                },
                json={"operations": [campaign_operation]}
            )
            response.raise_for_status()
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "pause_campaign", 
                {"campaign_id": campaign_id}, 
                {"success": True}, 
                execution_time, 
                True
            )
            
            return {
                "success": True,
                "message": f"Campaign {campaign_id} paused successfully"
            }
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "pause_campaign", 
                {"campaign_id": campaign_id}, 
                {"error": str(e)}, 
                execution_time, 
                False, 
                str(e)
            )
            return {"error": f"Failed to pause campaign: {str(e)}"}
    
    def resume_campaign(self, campaign_id: str) -> Dict:
        """Resume a paused Google Ads campaign"""
        start_time = time.time()
        try:
            if not campaign_id:
                return {"error": "Campaign ID is required"}
            
            credentials = self._get_google_ads_credentials()
            if "error" in credentials:
                return {"error": credentials["error"]}
            
            accounts = GoogleAdsAccount.objects.filter(
                user=self.user,
                is_active=True
            )
            
            if not accounts.exists():
                return {"error": "No Google Ads accounts found"}
            
            account = accounts.first()
            
            # Update campaign status to ENABLED
            campaign_url = f"https://googleads.googleapis.com/v21/customers/{account.customer_id}/campaigns:mutate"
            campaign_operation = {
                "update": {
                    "resource_name": f"customers/{account.customer_id}/campaigns/{campaign_id}",
                    "status": "ENABLED"
                },
                "update_mask": {
                    "paths": ["status"]
                }
            }
            
            response = requests.post(
                campaign_url,
                headers={
                    "Authorization": f"Bearer {credentials['access_token']}",
                    "developer-token": credentials['developer_token'],
                    "Content-Type": "application/json"
                },
                json={"operations": [campaign_operation]}
            )
            response.raise_for_status()
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "resume_campaign", 
                {"campaign_id": campaign_id}, 
                {"success": True}, 
                execution_time, 
                True
            )
            
            return {
                "success": True,
                "message": f"Campaign {campaign_id} resumed successfully"
            }
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "resume_campaign", 
                {"campaign_id": campaign_id}, 
                {"error": str(e)}, 
                execution_time, 
                False, 
                str(e)
            )
            return {"error": f"Failed to resume campaign: {str(e)}"}


class DatabaseTools:
    """Tools for database operations"""
    
    def __init__(self, user: User, session_id: str = None):
        self.user = user
        self.session_id = session_id
    
    def _log_tool_execution(self, tool_name: str, input_params: Dict, output_result: Dict, 
                           execution_time_ms: int, success: bool, error_message: str = None):
        """Log tool execution for auditing"""
        try:
            if self.session_id:
                session = ChatSession.objects.get(id=self.session_id)
                AIToolExecution.objects.create(
                    user=self.user,
                    session=session,
                    tool_type='database',
                    tool_name=tool_name,
                    input_parameters=input_params,
                    output_result=output_result,
                    execution_time_ms=execution_time_ms,
                    success=success,
                    error_message=error_message
                )
        except Exception as e:
            logger.error(f"Failed to log tool execution: {e}")
    
    def search_campaigns_db(self, query: str, status: str = None) -> List[Dict]:
        """Search campaigns in local database"""
        start_time = time.time()
        try:
            # Get user's Google Ads accounts
            accounts = GoogleAdsAccount.objects.filter(
                user=self.user,
                is_active=True
            )
            
            campaigns_query = GoogleAdsCampaign.objects.filter(
                account__in=accounts
            )
            
            if query:
                campaigns_query = campaigns_query.filter(
                    campaign_name__icontains=query
                )
            
            if status:
                campaigns_query = campaigns_query.filter(campaign_status=status)
            
            campaigns = campaigns_query.select_related('account').order_by('-created_at')
            
            results = []
            for campaign in campaigns:
                results.append({
                    "id": campaign.campaign_id,
                    "name": campaign.campaign_name,
                    "status": campaign.campaign_status,
                    "type": campaign.campaign_type,
                    "account_name": campaign.account.account_name,
                    "start_date": campaign.start_date,
                    "end_date": campaign.end_date,
                    "budget_amount": float(campaign.budget_amount) if campaign.budget_amount else None
                })
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "search_campaigns_db", 
                {"query": query, "status": status}, 
                {"results_count": len(results)}, 
                execution_time, 
                True
            )
            
            return results
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "search_campaigns_db", 
                {"query": query, "status": status}, 
                {"error": str(e)}, 
                execution_time, 
                False, 
                str(e)
            )
            return {"error": f"Database search failed: {str(e)}"}
    
    def get_account_summary(self) -> Dict:
        """Get summary of user's Google Ads accounts"""
        start_time = time.time()
        try:
            accounts = GoogleAdsAccount.objects.filter(
                user=self.user,
                is_active=True
            )
            
            total_accounts = accounts.count()
            total_campaigns = GoogleAdsCampaign.objects.filter(
                account__in=accounts
            ).count()
            
            total_ad_groups = GoogleAdsAdGroup.objects.filter(
                campaign__account__in=accounts
            ).count()
            
            total_keywords = GoogleAdsKeyword.objects.filter(
                ad_group__campaign__account__in=accounts
            ).count()
            
            # Get performance summary for last 30 days
            from django.utils import timezone
            from datetime import timedelta
            
            thirty_days_ago = timezone.now().date() - timedelta(days=30)
            performance_data = GoogleAdsPerformance.objects.filter(
                account__in=accounts,
                date__gte=thirty_days_ago
            ).aggregate(
                total_impressions=models.Sum('impressions'),
                total_clicks=models.Sum('clicks'),
                total_cost_micros=models.Sum('cost_micros'),
                total_conversions=models.Sum('conversions')
            )
            
            summary = {
                "total_accounts": total_accounts,
                "total_campaigns": total_campaigns,
                "total_ad_groups": total_ad_groups,
                "total_keywords": total_keywords,
                "accounts": [
                    {
                        "id": acc.customer_id,
                        "name": acc.account_name,
                        "status": acc.sync_status,
                        "is_manager": acc.is_manager,
                        "is_test": acc.is_test_account
                    } for acc in accounts
                ],
                "performance_30_days": {
                    "impressions": performance_data['total_impressions'] or 0,
                    "clicks": performance_data['total_clicks'] or 0,
                    "cost_micros": performance_data['total_cost_micros'] or 0,
                    "conversions": performance_data['total_conversions'] or 0
                }
            }
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "get_account_summary", 
                {}, 
                {"summary": summary}, 
                execution_time, 
                True
            )
            
            return summary
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "get_account_summary", 
                {}, 
                {"error": str(e)}, 
                execution_time, 
                False, 
                str(e)
            )
            return {"error": f"Failed to get account summary: {str(e)}"}
    
    def get_campaign_performance(self, campaign_id: str = None, days: int = 30) -> List[Dict]:
        """Get performance data for campaigns"""
        start_time = time.time()
        try:
            from django.utils import timezone
            from datetime import timedelta
            
            accounts = GoogleAdsAccount.objects.filter(
                user=self.user,
                is_active=True
            )
            
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days)
            
            performance_query = GoogleAdsPerformance.objects.filter(
                account__in=accounts,
                date__gte=start_date,
                date__lte=end_date
            )
            
            if campaign_id:
                performance_query = performance_query.filter(campaign__campaign_id=campaign_id)
            
            performance_data = performance_query.select_related(
                'account', 'campaign', 'ad_group'
            ).order_by('-date')
            
            results = []
            for perf in performance_data:
                results.append({
                    "date": perf.date.isoformat(),
                    "account_name": perf.account.account_name,
                    "campaign_name": perf.campaign.campaign_name if perf.campaign else None,
                    "ad_group_name": perf.ad_group.ad_group_name if perf.ad_group else None,
                    "impressions": perf.impressions,
                    "clicks": perf.clicks,
                    "cost_micros": perf.cost_micros,
                    "conversions": float(perf.conversions) if perf.conversions else 0,
                    "conversion_value": float(perf.conversion_value) if perf.conversion_value else 0,
                    "ctr": float(perf.ctr) if perf.ctr else 0,
                    "cpc": float(perf.cpc) if perf.cpc else 0,
                    "roas": float(perf.roas) if perf.roas else 0
                })
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "get_campaign_performance", 
                {"campaign_id": campaign_id, "days": days}, 
                {"results_count": len(results)}, 
                execution_time, 
                True
            )
            
            return results
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "get_campaign_performance", 
                {"campaign_id": campaign_id, "days": days}, 
                {"error": str(e)}, 
                execution_time, 
                False, 
                str(e)
            )
            return {"error": f"Failed to get campaign performance: {str(e)}"}
    
    def search_keywords(self, query: str, status: str = None) -> List[Dict]:
        """Search keywords in local database"""
        start_time = time.time()
        try:
            accounts = GoogleAdsAccount.objects.filter(
                user=self.user,
                is_active=True
            )
            
            keywords_query = GoogleAdsKeyword.objects.filter(
                ad_group__campaign__account__in=accounts
            )
            
            if query:
                keywords_query = keywords_query.filter(
                    keyword_text__icontains=query
                )
            
            if status:
                keywords_query = keywords_query.filter(status=status)
            
            keywords = keywords_query.select_related(
                'ad_group__campaign__account'
            ).order_by('-created_at')
            
            results = []
            for keyword in keywords:
                results.append({
                    "id": keyword.keyword_id,
                    "text": keyword.keyword_text,
                    "match_type": keyword.match_type,
                    "status": keyword.status,
                    "quality_score": keyword.quality_score,
                    "ad_group_name": keyword.ad_group.ad_group_name,
                    "campaign_name": keyword.ad_group.campaign.campaign_name,
                    "account_name": keyword.ad_group.campaign.account.account_name
                })
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "search_keywords", 
                {"query": query, "status": status}, 
                {"results_count": len(results)}, 
                execution_time, 
                True
            )
            
            return results
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "search_keywords", 
                {"query": query, "status": status}, 
                {"error": str(e)}, 
                execution_time, 
                False, 
                str(e)
            )
            return {"error": f"Failed to search keywords: {str(e)}"}


class KnowledgeBaseTools:
    """Tools for company knowledge base operations"""
    
    def __init__(self, user: User, session_id: str = None):
        self.user = user
        self.session_id = session_id
    
    def _log_tool_execution(self, tool_name: str, input_params: Dict, output_result: Dict, 
                           execution_time_ms: int, success: bool, error_message: str = None):
        """Log tool execution for auditing"""
        try:
            if self.session_id:
                session = ChatSession.objects.get(id=self.session_id)
                AIToolExecution.objects.create(
                    user=self.user,
                    session=session,
                    tool_type='knowledge_base',
                    tool_name=tool_name,
                    input_parameters=input_params,
                    output_result=output_result,
                    execution_time_ms=execution_time_ms,
                    success=success,
                    error_message=error_message
                )
        except Exception as e:
            logger.error(f"Failed to log tool execution: {e}")
    
    def search_kb(self, query: str, company_id: int = 1, top_k: int = 5) -> List[Dict]:
        """Search company knowledge base using vector similarity"""
        start_time = time.time()
        try:
            from sentence_transformers import SentenceTransformer
            import numpy as np
            
            # Load embedding model
            model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Generate query embedding
            query_embedding = model.encode(query)
            
            # Search in database using vector similarity
            documents = KBDocument.objects.filter(company_id=company_id)
            
            # Calculate similarity scores
            results = []
            for doc in documents:
                if doc.embedding:
                    # Convert binary embedding back to numpy array
                    doc_embedding = np.frombuffer(doc.embedding, dtype=np.float32)
                    similarity = np.dot(query_embedding, doc_embedding) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
                    )
                    results.append({
                        "id": doc.id,
                        "title": doc.title,
                        "content": doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                        "similarity": float(similarity),
                        "url": doc.url,
                        "document_type": doc.document_type
                    })
            
            # Sort by similarity and return top_k
            results.sort(key=lambda x: x["similarity"], reverse=True)
            results = results[:top_k]
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "search_kb", 
                {"query": query, "company_id": company_id, "top_k": top_k}, 
                {"results_count": len(results)}, 
                execution_time, 
                True
            )
            
            return results
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "search_kb", 
                {"query": query, "company_id": company_id, "top_k": top_k}, 
                {"error": str(e)}, 
                execution_time, 
                False, 
                str(e)
            )
            return {"error": f"Knowledge base search failed: {str(e)}"}
    
    def add_kb_document(self, company_id: int, title: str, content: str, 
                         url: str = None, document_type: str = "general") -> Dict:
        """Add a new document to the knowledge base"""
        start_time = time.time()
        try:
            from sentence_transformers import SentenceTransformer
            import numpy as np
            
            # Load embedding model
            model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Generate embedding
            embedding = model.encode(content)
            
            # Save to database
            doc = KBDocument.objects.create(
                company_id=company_id,
                title=title,
                content=content,
                url=url,
                document_type=document_type,
                embedding=embedding.tobytes()  # Store as binary
            )
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "add_kb_document", 
                {"company_id": company_id, "title": title, "document_type": document_type}, 
                {"document_id": doc.id}, 
                execution_time, 
                True
            )
            
            return {
                "success": True,
                "id": doc.id,
                "message": f"Document '{title}' added to knowledge base"
            }
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "add_kb_document", 
                {"company_id": company_id, "title": title, "document_type": document_type}, 
                {"error": str(e)}, 
                execution_time, 
                False, 
                str(e)
            )
            return {"error": f"Failed to add document: {str(e)}"}
    
    def get_kb_documents(self, company_id: int = 1, document_type: str = None) -> List[Dict]:
        """Get documents from knowledge base"""
        start_time = time.time()
        try:
            documents_query = KBDocument.objects.filter(company_id=company_id)
            
            if document_type:
                documents_query = documents_query.filter(document_type=document_type)
            
            documents = documents_query.order_by('-updated_at')
            
            results = []
            for doc in documents:
                results.append({
                    "id": doc.id,
                    "title": doc.title,
                    "content": doc.content[:100] + "..." if len(doc.content) > 100 else doc.content,
                    "url": doc.url,
                    "document_type": doc.document_type,
                    "created_at": doc.created_at.isoformat(),
                    "updated_at": doc.updated_at.isoformat()
                })
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "get_kb_documents", 
                {"company_id": company_id, "document_type": document_type}, 
                {"results_count": len(results)}, 
                execution_time, 
                True
            )
            
            return results
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "get_kb_documents", 
                {"company_id": company_id, "document_type": document_type}, 
                {"error": str(e)}, 
                execution_time, 
                False, 
                str(e)
            )
            return {"error": f"Failed to get documents: {str(e)}"}


class AnalyticsTools:
    """Tools for generating analytics and insights"""
    
    def __init__(self, user: User, session_id: str = None):
        self.user = user
        self.session_id = session_id
    
    def _log_tool_execution(self, tool_name: str, input_params: Dict, output_result: Dict, 
                           execution_time_ms: int, success: bool, error_message: str = None):
        """Log tool execution for auditing"""
        try:
            if self.session_id:
                session = ChatSession.objects.get(id=self.session_id)
                AIToolExecution.objects.create(
                    user=self.user,
                    session=session,
                    tool_type='analytics',
                    tool_name=tool_name,
                    input_parameters=input_params,
                    output_result=output_result,
                    execution_time_ms=execution_time_ms,
                    success=success,
                    error_message=error_message
                )
        except Exception as e:
            logger.error(f"Failed to log tool execution: {e}")
    
    def generate_performance_report(self, days: int = 30) -> Dict:
        """Generate comprehensive performance report"""
        start_time = time.time()
        try:
            from django.utils import timezone
            from datetime import timedelta
            from django.db.models import Sum, Avg, Count
            
            accounts = GoogleAdsAccount.objects.filter(
                user=self.user,
                is_active=True
            )
            
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days)
            
            # Get performance data
            performance_data = GoogleAdsPerformance.objects.filter(
                account__in=accounts,
                date__gte=start_date,
                date__lte=end_date
            )
            
            # Aggregate metrics
            total_metrics = performance_data.aggregate(
                total_impressions=Sum('impressions'),
                total_clicks=Sum('clicks'),
                total_cost_micros=Sum('cost_micros'),
                total_conversions=Sum('conversions'),
                total_conversion_value=Sum('conversion_value')
            )
            
            # Calculate averages
            avg_metrics = performance_data.aggregate(
                avg_ctr=Avg('ctr'),
                avg_cpc=Avg('cpc'),
                avg_cpm=Avg('cpm'),
                avg_conversion_rate=Avg('conversion_rate'),
                avg_roas=Avg('roas')
            )
            
            # Campaign performance
            campaign_performance = performance_data.values(
                'campaign__campaign_name'
            ).annotate(
                impressions=Sum('impressions'),
                clicks=Sum('clicks'),
                cost_micros=Sum('cost_micros'),
                conversions=Sum('conversions')
            ).order_by('-cost_micros')[:10]
            
            # Daily trends
            daily_trends = performance_data.values('date').annotate(
                impressions=Sum('impressions'),
                clicks=Sum('clicks'),
                cost_micros=Sum('cost_micros')
            ).order_by('date')
            
            report = {
                "period": f"Last {days} days",
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "total_metrics": {
                    "impressions": total_metrics['total_impressions'] or 0,
                    "clicks": total_metrics['total_clicks'] or 0,
                    "cost_micros": total_metrics['total_cost_micros'] or 0,
                    "conversions": total_metrics['total_conversions'] or 0,
                    "conversion_value": total_metrics['total_conversion_value'] or 0
                },
                "average_metrics": {
                    "ctr": float(avg_metrics['avg_ctr']) if avg_metrics['avg_ctr'] else 0,
                    "cpc": float(avg_metrics['avg_cpc']) if avg_metrics['avg_cpc'] else 0,
                    "cpm": float(avg_metrics['avg_cpm']) if avg_metrics['avg_cpm'] else 0,
                    "conversion_rate": float(avg_metrics['avg_conversion_rate']) if avg_metrics['avg_conversion_rate'] else 0,
                    "roas": float(avg_metrics['avg_roas']) if avg_metrics['avg_roas'] else 0
                },
                "top_campaigns": list(campaign_performance),
                "daily_trends": list(daily_trends)
            }
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "generate_performance_report", 
                {"days": days}, 
                {"report": report}, 
                execution_time, 
                True
            )
            
            return report
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "generate_performance_report", 
                {"days": days}, 
                {"error": str(e)}, 
                execution_time, 
                False, 
                str(e)
            )
            return {"error": f"Failed to generate performance report: {str(e)}"}
    
    def get_budget_insights(self) -> Dict:
        """Get budget insights and recommendations"""
        start_time = time.time()
        try:
            from django.db.models import Sum, Avg
            
            accounts = GoogleAdsAccount.objects.filter(
                user=self.user,
                is_active=True
            )
            
            # Get campaign budgets and spending
            campaigns = GoogleAdsCampaign.objects.filter(
                account__in=accounts,
                campaign_status='ENABLED'
            )
            
            total_budget = sum([
                float(campaign.budget_amount or 0) 
                for campaign in campaigns 
                if campaign.budget_amount
            ])
            
            # Get actual spending from performance data
            from django.utils import timezone
            from datetime import timedelta
            
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
            
            total_spent = GoogleAdsPerformance.objects.filter(
                account__in=accounts,
                date__gte=start_date,
                date__lte=end_date
            ).aggregate(
                total_cost_micros=Sum('cost_micros')
            )['total_cost_micros'] or 0
            
            total_spent = total_spent / 1000000  # Convert from micros
            
            # Calculate budget utilization
            budget_utilization = (total_spent / total_budget * 100) if total_budget > 0 else 0
            
            # Get campaigns near budget limit
            near_budget_campaigns = []
            for campaign in campaigns:
                if campaign.budget_amount:
                    campaign_spent = GoogleAdsPerformance.objects.filter(
                        campaign=campaign,
                        date__gte=start_date,
                        date__lte=end_date
                    ).aggregate(
                        total_cost_micros=Sum('cost_micros')
                    )['total_cost_micros'] or 0
                    
                    campaign_spent = campaign_spent / 1000000
                    utilization = (campaign_spent / float(campaign.budget_amount) * 100)
                    
                    if utilization > 80:  # Near budget limit
                        near_budget_campaigns.append({
                            "campaign_name": campaign.campaign_name,
                            "budget_amount": float(campaign.budget_amount),
                            "spent": campaign_spent,
                            "utilization_percent": utilization
                        })
            
            insights = {
                "total_budget": total_budget,
                "total_spent_30_days": total_spent,
                "budget_utilization_percent": budget_utilization,
                "budget_status": "Over Budget" if budget_utilization > 100 else "Under Budget",
                "near_budget_campaigns": near_budget_campaigns,
                "recommendations": []
            }
            
            # Generate recommendations
            if budget_utilization > 100:
                insights["recommendations"].append("Consider increasing overall budget or pausing low-performing campaigns")
            
            if near_budget_campaigns:
                insights["recommendations"].append("Monitor campaigns near budget limits")
            
            if budget_utilization < 50:
                insights["recommendations"].append("Budget underutilized - consider expanding campaigns or increasing bids")
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "get_budget_insights", 
                {}, 
                {"insights": insights}, 
                execution_time, 
                True
            )
            
            return insights
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "get_budget_insights", 
                {}, 
                {"error": str(e)}, 
                execution_time, 
                False, 
                str(e)
            )
            return {"error": f"Failed to get budget insights: {str(e)}"}


# Function to get all available tools for a user
def get_all_tools(user: User, session_id: str = None) -> List:
    """Get all available tools for a user"""
    google_ads_tools = GoogleAdsTools(user, session_id)
    database_tools = DatabaseTools(user, session_id)
    kb_tools = KnowledgeBaseTools(user, session_id)
    analytics_tools = AnalyticsTools(user, session_id)
    
    return [
        # Google Ads tools
        google_ads_tools.get_campaigns,
        google_ads_tools.create_campaign,
        google_ads_tools.get_ad_groups,
        google_ads_tools.pause_campaign,
        google_ads_tools.resume_campaign,
        
        # Database tools
        database_tools.search_campaigns_db,
        database_tools.get_account_summary,
        database_tools.get_campaign_performance,
        database_tools.search_keywords,
        
        # Knowledge base tools
        kb_tools.search_kb,
        kb_tools.add_kb_document,
        kb_tools.get_kb_documents,
        
        # Analytics tools
        analytics_tools.generate_performance_report,
        analytics_tools.get_budget_insights,
    ]

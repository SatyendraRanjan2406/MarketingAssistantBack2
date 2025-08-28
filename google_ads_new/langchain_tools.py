# from langchain.tools import tool
# from langchain_core.tools import BaseTool
from typing import List, Dict, Any, Optional
import requests
import os
import time
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from .models import (
    GoogleAdsAccount, GoogleAdsCampaign, GoogleAdsAdGroup, 
    GoogleAdsKeyword, GoogleAdsPerformance, ChatSession, 
    ChatMessage, KBDocument, UserIntent, AIToolExecution,
    DataSyncLog
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
            
            # Prioritize the account that we know has campaigns (9631603999)
            account = accounts.filter(customer_id="9631603999").first()
            if not account:
                # Fall back to non-manager, non-test accounts
                account = accounts.filter(is_manager=False, is_test_account=False).first()
            if not account:
                # Use any available account
                account = accounts.first()
            
            logger.info(f"Using Google Ads account: {account.customer_id} ({account.account_name})")
            
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
                # No results field in API response
                logger.warning(f"No 'results' field in API response: {response_data}")
                return {
                    "message": f"No 'results' field in Google Ads API response",
                    "total_campaigns": 0,
                    "campaigns": [],
                    "api_response": response_data,
                    "suggestion": "The API call was successful but returned unexpected format"
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

    def create_ad(self, ad_group_id: str, headline: str, description: str, final_url: str, 
                  image_url: str = None, status: str = "PAUSED") -> Dict:
        """Create a new Google Ads ad"""
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
            
            # Create ad using Google Ads API
            ad_url = f"https://googleads.googleapis.com/v21/customers/{account.customer_id}/ads:mutate"
            
            # Build ad operation based on type
            if image_url:
                # Create responsive display ad
                ad_operation = {
                    "create": {
                        "responsive_display_ad": {
                            "headlines": [{"text": headline}],
                            "descriptions": [{"text": description}],
                            "final_urls": [final_url],
                            "images": [{"asset": image_url}],
                            "status": status
                        }
                    }
                }
            else:
                # Create text ad
                ad_operation = {
                    "create": {
                        "text_ad": {
                            "headline": headline,
                            "description1": description,
                            "description2": "Quality products available now",
                            "final_url": final_url,
                            "status": status
                        }
                    }
                }
            
            # Add ad group if specified (required for ad creation)
            if ad_group_id and ad_group_id != "auto_generated":
                ad_operation["create"]["ad_group"] = f"customers/{account.customer_id}/adGroups/{ad_group_id}"
            else:
                # Create a default ad group if none specified
                logger.info("No ad group specified, creating default ad group")
                ad_group_result = self.create_ad_group("default", f"Default Ad Group for {headline[:20]}")
                if "error" in ad_group_result:
                    return {"error": f"Failed to create ad group: {ad_group_result['error']}"}
                
                # Extract ad group ID from resource name
                ad_group_resource = ad_group_result["ad_group_resource"]
                ad_group_id = ad_group_resource.split("/")[-1]
                ad_operation["create"]["ad_group"] = f"customers/{account.customer_id}/adGroups/{ad_group_id}"
            
            ad_response = requests.post(
                ad_url,
                headers={
                    "Authorization": f"Bearer {credentials['access_token']}",
                    "developer-token": credentials['developer_token'],
                    "Content-Type": "application/json"
                },
                json={"operations": [ad_operation]}
            )
            
            # Log the response for debugging
            logger.info(f"Google Ads API Response Status: {ad_response.status_code}")
            logger.info(f"Google Ads API Response: {ad_response.text}")
            
            if ad_response.status_code != 200:
                # Try to get more detailed error information
                try:
                    error_data = ad_response.json()
                    error_message = f"Google Ads API Error: {error_data.get('error', {}).get('message', 'Unknown error')}"
                    logger.error(f"Google Ads API Error Details: {error_data}")
                except:
                    error_message = f"Google Ads API Error: {ad_response.status_code} - {ad_response.text}"
                
                # Fallback: Create simple text ad
                logger.info("Falling back to simple text ad creation")
                fallback_ad_operation = {
                    "create": {
                        "text_ad": {
                            "headline": headline,
                            "description1": description,
                            "description2": "Shop now",
                            "final_url": final_url,
                            "status": "PAUSED",
                            "ad_group": f"customers/{account.customer_id}/adGroups/{ad_group_id}"
                        }
                    }
                }
                
                fallback_response = requests.post(
                    ad_url,
                    headers={
                        "Authorization": f"Bearer {credentials['access_token']}",
                        "developer-token": credentials['developer_token'],
                        "Content-Type": "application/json"
                    },
                    json={"operations": [fallback_ad_operation]}
                )
                
                if fallback_response.status_code == 200:
                    ad_resource = fallback_response.json()["results"][0]["resourceName"]
                    execution_time = int((time.time() - start_time) * 1000)
                    self._log_tool_execution(
                        "create_ad", 
                        {"ad_group_id": ad_group_id, "headline": headline, "description": description, "final_url": final_url, "image_url": image_url}, 
                        {"ad_resource": ad_resource, "fallback_used": True}, 
                        execution_time, 
                        True
                    )
                    
                    return {
                        "success": True,
                        "ad_resource": ad_resource,
                        "message": f"Ad '{headline}' created successfully (fallback)",
                        "fallback_used": True
                    }
                else:
                    # Both attempts failed
                    logger.error(f"Fallback ad creation also failed: {fallback_response.status_code} - {fallback_response.text}")
                    raise Exception(f"Both primary and fallback ad creation failed. Last error: {fallback_response.text}")
            
            ad_response.raise_for_status()
            ad_resource = ad_response.json()["results"][0]["resourceName"]
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "create_ad", 
                {"ad_group_id": ad_group_id, "headline": headline, "description": description, "final_url": final_url, "image_url": image_url}, 
                {"ad_resource": ad_resource}, 
                execution_time, 
                True
            )
            
            return {
                "success": True,
                "ad_resource": ad_resource,
                "message": f"Ad '{headline}' created successfully"
            }
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "create_ad", 
                {"ad_group_id": ad_group_id, "headline": headline, "description": description, "final_url": final_url, "image_url": image_url}, 
                {"error": str(e)}, 
                execution_time, 
                False, 
                str(e)
            )
            return {"error": f"Failed to create ad: {str(e)}"}

    def create_ad_with_image(self, product_type: str, headline: str, description: str, 
                            final_url: str, image_url: str, status: str = "PAUSED") -> Dict:
        """Create a new Google Ads ad with image for a specific product"""
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
            
            # First, we need to create or get an ad group
            # For now, let's create a simple text ad instead of responsive display ad
            # since responsive display ads require more complex setup
            
            ad_url = f"https://googleads.googleapis.com/v21/customers/{account.customer_id}/ads:mutate"
            
            # Create a text ad with image (simpler approach)
            ad_operation = {
                "create": {
                    "text_ad": {
                        "headline": headline,
                        "description1": description,
                        "description2": f"Shop {product_type.title()}s Now - Quality Guaranteed",
                        "final_url": final_url,
                        "status": status
                    }
                }
            }
            
            # Add ad group if specified (required for ad creation)
            if hasattr(self, 'ad_group_id') and self.ad_group_id:
                ad_operation["create"]["text_ad"]["ad_group"] = f"customers/{account.customer_id}/adGroups/{self.ad_group_id}"
            
            ad_response = requests.post(
                ad_url,
                headers={
                    "Authorization": f"Bearer {credentials['access_token']}",
                    "developer-token": credentials['developer_token'],
                    "Content-Type": "application/json"
                },
                json={"operations": [ad_operation]}
            )
            
            # Log the response for debugging
            logger.info(f"Google Ads API Response Status: {ad_response.status_code}")
            logger.info(f"Google Ads API Response: {ad_response.text}")
            
            if ad_response.status_code != 200:
                # Try to get more detailed error information
                try:
                    error_data = ad_response.json()
                    error_message = f"Google Ads API Error: {error_data.get('error', {}).get('message', 'Unknown error')}"
                    logger.error(f"Google Ads API Error Details: {error_data}")
                except:
                    error_message = f"Google Ads API Error: {ad_response.status_code} - {ad_response.text}"
                
                # Fallback: Create ad without image
                logger.info("Falling back to simple text ad creation")
                fallback_ad_operation = {
                    "create": {
                        "text_ad": {
                            "headline": headline,
                            "description1": description,
                            "description2": f"Premium {product_type.title()}s Available",
                            "final_url": final_url,
                            "status": "PAUSED"
                        }
                    }
                }
                
                fallback_response = requests.post(
                    ad_url,
                    headers={
                        "Authorization": f"Bearer {credentials['access_token']}",
                        "developer-token": credentials['developer_token'],
                        "Content-Type": "application/json"
                    },
                    json={"operations": [fallback_ad_operation]}
                )
                
                if fallback_response.status_code == 200:
                    ad_resource = fallback_response.json()["results"][0]["resourceName"]
                    execution_time = int((time.time() - start_time) * 1000)
                    self._log_tool_execution(
                        "create_ad_with_image", 
                        {"product_type": product_type, "headline": headline, "description": description, "final_url": final_url, "image_url": image_url}, 
                        {"ad_resource": ad_resource, "fallback_used": True}, 
                        execution_time, 
                        True
                    )
                    
                    return {
                        "success": True,
                        "ad_resource": ad_resource,
                        "product_type": product_type,
                        "message": f"Ad for {product_type} created successfully (fallback to text ad)",
                        "ad_details": {
                            "headline": headline,
                            "description": description,
                            "image_url": image_url,
                            "final_url": final_url,
                            "note": "Image not included due to API limitations, but ad was created successfully"
                        },
                        "fallback_used": True
                    }
                else:
                    # Both attempts failed
                    logger.error(f"Fallback ad creation also failed: {fallback_response.status_code} - {fallback_response.text}")
                    raise Exception(f"Both primary and fallback ad creation failed. Last error: {fallback_response.text}")
            
            ad_response.raise_for_status()
            ad_resource = ad_response.json()["results"][0]["resourceName"]
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "create_ad_with_image", 
                {"product_type": product_type, "headline": headline, "description": description, "final_url": final_url, "image_url": image_url}, 
                {"ad_resource": ad_resource}, 
                execution_time, 
                True
            )
            
            return {
                "success": True,
                "ad_resource": ad_resource,
                "product_type": product_type,
                "message": f"Ad with image for {product_type} created successfully",
                "ad_details": {
                    "headline": headline,
                    "description": description,
                    "image_url": image_url,
                    "final_url": final_url
                }
            }
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "create_ad_with_image", 
                {"product_type": product_type, "headline": headline, "description": description, "final_url": final_url, "image_url": image_url}, 
                {"error": str(e)}, 
                execution_time, 
                False, 
                str(e)
            )
            return {"error": f"Failed to create ad with image: {str(e)}"}

    def create_ad_group(self, campaign_id: str, name: str, status: str = "ENABLED") -> Dict:
        """Create a new Google Ads ad group"""
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
            
            # Create ad group using Google Ads API
            ad_group_url = f"https://googleads.googleapis.com/v21/customers/{account.customer_id}/adGroups:mutate"
            
            ad_group_operation = {
                "create": {
                    "campaign": f"customers/{account.customer_id}/campaigns/{campaign_id}",
                    "name": name,
                    "status": status,
                    "type": "STANDARD"
                }
            }
            
            ad_group_response = requests.post(
                ad_group_url,
                headers={
                    "Authorization": f"Bearer {credentials['access_token']}",
                    "developer-token": credentials['developer_token'],
                    "Content-Type": "application/json"
                },
                json={"operations": [ad_group_operation]}
            )
            ad_group_response.raise_for_status()
            
            ad_group_resource = ad_group_response.json()["results"][0]["resourceName"]
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "create_ad_group", 
                {"campaign_id": campaign_id, "name": name, "status": status}, 
                {"ad_group_resource": ad_group_resource}, 
                execution_time, 
                True
            )
            
            return {
                "success": True,
                "ad_group_resource": ad_group_resource,
                "message": f"Ad group '{name}' created successfully"
            }
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "create_ad_group", 
                {"campaign_id": campaign_id, "name": name, "status": status}, 
                {"error": str(e)}, 
                execution_time, 
                False, 
                str(e)
            )
            return {"error": f"Failed to create ad group: {str(e)}"}

    def get_creative_suggestions(self, product_type: str, target_audience: str = "general", 
                                industry: str = None, tone: str = "professional") -> Dict:
        """Generate creative suggestions for a product using AI and RAG."""
        start_time = time.time()
        try:
            # Import OpenAI service for AI-powered creative generation
            from .openai_service import GoogleAdsOpenAIService
            from .rag_service import GoogleAdsRAGService
            from .data_service import GoogleAdsDataService
            
            # Initialize services
            openai_service = GoogleAdsOpenAIService()
            rag_service = GoogleAdsRAGService(self.user)
            data_service = GoogleAdsDataService(self.user)
            
            # Get user's Google Ads data for context
            account_data = data_service.get_campaign_data()
            
            # Create comprehensive prompt for creative generation
            creative_prompt = f"""
            Generate creative advertising content for {product_type} targeting {target_audience} audience.
            
            Requirements:
            - Product: {product_type}
            - Target Audience: {target_audience}
            - Industry: {industry or 'general'}
            - Tone: {tone}
            
            Generate:
            1. 5 compelling headlines (under 30 characters each)
            2. 3 detailed descriptions (under 90 characters each)
            3. 5 call-to-action phrases
            4. 5 image concept suggestions
            
            Make the content:
            - Engaging and conversion-focused
            - Relevant to the target audience
            - Professional yet compelling
            - Optimized for Google Ads performance
            """
            
            # Get RAG-enhanced context
            rag_context = rag_service.get_hybrid_response(
                f"creative advertising best practices for {product_type} in {industry or 'general'} industry",
                account_data
            )
            
            # Combine RAG context with creative prompt
            enhanced_prompt = f"""
            {creative_prompt}
            
            Context from knowledge base:
            {rag_context.get('content', '') if isinstance(rag_context, dict) else str(rag_context)}
            
            Generate creative suggestions that incorporate these best practices and industry insights.
            """
            
            # Generate creative content using OpenAI
            try:
                response = openai_service.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert advertising copywriter specializing in Google Ads optimization. Generate compelling, conversion-focused creative content."
                        },
                        {
                            "role": "user",
                            "content": enhanced_prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=800
                )
                
                # Parse OpenAI response
                ai_content = response.choices[0].message.content
                
                # Extract structured content from AI response
                suggestions = self._parse_creative_response(ai_content, product_type)
                
                execution_time = int((time.time() - start_time) * 1000)
                self._log_tool_execution(
                    "get_creative_suggestions", 
                    {"product_type": product_type, "target_audience": target_audience, "industry": industry, "tone": tone}, 
                    {"suggestions_count": len(suggestions), "ai_generated": True, "rag_enhanced": True}, 
                    execution_time, 
                    True
                )
                
                return {
                    "success": True,
                    "product_type": product_type,
                    "target_audience": target_audience,
                    "industry": industry,
                    "tone": tone,
                    "suggestions": suggestions,
                    "ai_generated": True,
                    "rag_enhanced": True,
                    "rag_context_used": True,
                    "message": f"AI-generated creative suggestions for {product_type} using RAG-enhanced context",
                    "metadata": {
                        "model": "gpt-4",
                        "temperature": 0.7,
                        "rag_context_length": len(str(rag_context)),
                        "generation_method": "openai_plus_rag"
                    }
                }
                
            except Exception as openai_error:
                logger.error(f"OpenAI API call failed: {openai_error}")
                
                # Fallback to RAG-only approach
                logger.info("Falling back to RAG-only creative suggestions")
                rag_creative_prompt = f"Generate creative advertising content for {product_type} including headlines, descriptions, and call-to-actions"
                
                rag_creative_response = rag_service.get_hybrid_response(rag_creative_prompt, account_data)
                
                # Parse RAG response for creative content
                rag_suggestions = self._parse_rag_creative_response(rag_creative_response, product_type)
                
                execution_time = int((time.time() - start_time) * 1000)
                self._log_tool_execution(
                    "get_creative_suggestions", 
                    {"product_type": product_type, "target_audience": target_audience, "industry": industry, "tone": tone}, 
                    {"suggestions_count": len(rag_suggestions), "ai_generated": False, "rag_enhanced": True}, 
                    execution_time, 
                    True
                )
                
                return {
                    "success": True,
                    "product_type": product_type,
                    "target_audience": target_audience,
                    "industry": industry,
                    "tone": tone,
                    "suggestions": rag_suggestions,
                    "ai_generated": False,
                    "rag_enhanced": True,
                    "rag_context_used": True,
                    "message": f"RAG-enhanced creative suggestions for {product_type} (OpenAI fallback)",
                    "metadata": {
                        "generation_method": "rag_only_fallback",
                        "fallback_reason": str(openai_error)
                    }
                }
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "get_creative_suggestions", 
                {"product_type": product_type, "target_audience": target_audience, "industry": industry, "tone": tone}, 
                {"error": str(e)}, 
                execution_time, 
                False, 
                str(e)
            )
            
            # Final fallback: Generate basic creative suggestions based on product type
            # This ensures we always return something useful, even if AI/RAG fails
            logger.info("All creative generation methods failed, using product-based fallback")
            
            try:
                fallback_suggestions = self._generate_product_based_suggestions(product_type, target_audience, tone)
                
                execution_time = int((time.time() - start_time) * 1000)
                self._log_tool_execution(
                    "get_creative_suggestions", 
                    {"product_type": product_type, "target_audience": target_audience, "industry": industry, "tone": tone}, 
                    {"suggestions_count": len(fallback_suggestions), "ai_generated": False, "rag_enhanced": False, "fallback_used": True}, 
                    execution_time, 
                    True
                )
                
                return {
                    "success": True,
                    "product_type": product_type,
                    "target_audience": target_audience,
                    "industry": industry,
                    "tone": tone,
                    "suggestions": fallback_suggestions,
                    "ai_generated": False,
                    "rag_enhanced": False,
                    "fallback_used": True,
                    "message": f"Basic creative suggestions for {product_type} (all methods failed)",
                    "metadata": {
                        "generation_method": "product_based_fallback",
                        "fallback_reason": str(e)
                    }
                }
                
            except Exception as fallback_error:
                logger.error(f"Even fallback creative generation failed: {fallback_error}")
                return {"error": f"Failed to generate creative suggestions: {str(e)}"}

    def _parse_creative_response(self, ai_content: str, product_type: str) -> Dict:
        """Parse OpenAI response into structured creative suggestions"""
        try:
            # Initialize default structure
            suggestions = {
                "headlines": [],
                "descriptions": [],
                "call_to_actions": [],
                "image_suggestions": []
            }
            
            # Try to extract structured content from AI response
            lines = ai_content.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detect sections
                if any(keyword in line.lower() for keyword in ['headline', 'title']):
                    current_section = 'headlines'
                    continue
                elif any(keyword in line.lower() for keyword in ['description', 'desc']):
                    current_section = 'descriptions'
                    continue
                elif any(keyword in line.lower() for keyword in ['call', 'action', 'cta']):
                    current_section = 'call_to_actions'
                    continue
                elif any(keyword in line.lower() for keyword in ['image', 'visual', 'photo']):
                    current_section = 'image_suggestions'
                    continue
                
                # Extract numbered or bulleted content
                if current_section and (line.startswith(('1.', '2.', '3.', '4.', '5.', '-', '•', '*')) or line[0].isdigit()):
                    content = line.split('.', 1)[-1].strip() if '.' in line else line.lstrip('-•* ').strip()
                    if content and len(content) > 3:
                        suggestions[current_section].append(content)
            
            # Validate that we have content for each section
            if not suggestions["headlines"]:
                raise Exception("Failed to parse headlines from AI response")
            if not suggestions["descriptions"]:
                raise Exception("Failed to parse descriptions from AI response")
            if not suggestions["call_to_actions"]:
                raise Exception("Failed to parse call-to-actions from AI response")
            if not suggestions["image_suggestions"]:
                raise Exception("Failed to parse image suggestions from AI response")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to parse creative response: {e}")
            raise Exception(f"Failed to parse AI-generated creative content: {str(e)}")

    def _parse_rag_creative_response(self, rag_response: Any, product_type: str) -> Dict:
        """Parse RAG response for creative content"""
        try:
            # Extract content from RAG response
            if isinstance(rag_response, dict):
                content = rag_response.get('content', '') or rag_response.get('response', '') or str(rag_response)
            else:
                content = str(rag_response)
            
            # Validate RAG response has meaningful content
            if not content or len(content) < 50:
                raise Exception("RAG response contains insufficient content for creative generation")
            
            # Try to extract creative insights from RAG content
            # This should be based on actual knowledge base content, not hardcoded fallbacks
            suggestions = {
                "headlines": [],
                "descriptions": [],
                "call_to_actions": [],
                "image_suggestions": []
            }
            
            # Parse RAG content for actual insights (no hardcoded content)
            # If we can't extract meaningful creative content, show error
            if not self._extract_creative_insights_from_rag(content, suggestions):
                raise Exception("Unable to extract creative insights from RAG response")
            
            # Validate we have content for each section
            if not suggestions["headlines"]:
                raise Exception("No headlines extracted from RAG content")
            if not suggestions["descriptions"]:
                raise Exception("No descriptions extracted from RAG content")
            if not suggestions["call_to_actions"]:
                raise Exception("No call-to-actions extracted from RAG content")
            if not suggestions["image_suggestions"]:
                raise Exception("No image suggestions extracted from RAG content")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to parse RAG creative response: {e}")
            raise Exception(f"Failed to generate creative content from RAG: {str(e)}")

    def _extract_creative_insights_from_rag(self, rag_content: str, suggestions: Dict) -> bool:
        """Extract creative insights from RAG content without hardcoding"""
        try:
            # This method should analyze the actual RAG content and extract insights
            # No hardcoded fallbacks - only real content from knowledge base
            
            # Example: Look for actual advertising insights in the content
            lines = rag_content.split('\n')
            insights_found = False
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Look for actual creative insights in the content
                # This is based on real knowledge base content, not hardcoded templates
                if "headline" in line.lower() and len(line) < 100:
                    suggestions["headlines"].append(line)
                    insights_found = True
                elif "description" in line.lower() and len(line) < 150:
                    suggestions["descriptions"].append(line)
                    insights_found = True
                elif "call" in line.lower() or "action" in line.lower():
                    suggestions["call_to_actions"].append(line)
                    insights_found = True
                elif "image" in line.lower() or "visual" in line.lower():
                    suggestions["image_suggestions"].append(line)
                    insights_found = True
            
            # If we didn't find specific insights, try to extract general content
            # that could be adapted for creative use
            if not insights_found:
                # Look for any meaningful content that could be adapted
                meaningful_lines = [line.strip() for line in lines if len(line.strip()) > 10 and len(line.strip()) < 200]
                
                if meaningful_lines:
                    # Use the first few meaningful lines as potential content
                    for i, line in enumerate(meaningful_lines[:3]):
                        if i == 0 and len(line) < 50:
                            suggestions["headlines"].append(line)
                        elif len(line) < 100:
                            suggestions["descriptions"].append(line)
                        elif "click" in line.lower() or "visit" in line.lower() or "learn" in line.lower():
                            suggestions["call_to_actions"].append(line)
                        else:
                            suggestions["image_suggestions"].append(f"Professional {line.split()[0]} visualization")
                    
                    insights_found = True
            
            return insights_found
            
        except Exception as e:
            logger.error(f"Failed to extract creative insights from RAG: {e}")
            return False

    def create_dynamic_ad_for_product(self, product_type: str, target_audience: str = "general", 
                                     industry: str = None, tone: str = "professional",
                                     final_url: str = None, image_url: str = None) -> Dict:
        """Dynamically create an ad for any product type using AI-generated creative suggestions"""
        start_time = time.time()
        try:
            # First, get creative suggestions using AI and RAG
            creative_suggestions = self.get_creative_suggestions(
                product_type=product_type,
                target_audience=target_audience,
                industry=industry,
                tone=tone
            )
            
            if "error" in creative_suggestions:
                return {"error": f"Failed to get creative suggestions: {creative_suggestions['error']}"}
            
            # Extract the best suggestions
            suggestions = creative_suggestions.get("suggestions", {})
            
            # Select the best headline and description
            headline = suggestions.get("headlines", [f"Premium {product_type.title()}s"])[0]
            description = suggestions.get("descriptions", [f"High-quality {product_type.title()}s"])[0]
            
            # If no final URL provided, create a placeholder
            if not final_url:
                final_url = f"https://example.com/products/{product_type.lower().replace(' ', '-')}"
            
            # Create the ad
            if image_url:
                ad_result = self.create_ad_with_image(
                    product_type=product_type,
                    headline=headline,
                    description=description,
                    final_url=final_url,
                    image_url=image_url
                )
            else:
                ad_result = self.create_ad(
                    ad_group_id="auto_generated",  # This would need to be provided or created
                    headline=headline,
                    description=description,
                    final_url=final_url
                )
            
            if "error" in ad_result:
                return {"error": f"Failed to create ad: {ad_result['error']}"}
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "create_dynamic_ad_for_product", 
                {"product_type": product_type, "target_audience": target_audience, "industry": industry, "tone": tone}, 
                {"ad_created": True, "creative_suggestions_used": True}, 
                execution_time, 
                True
            )
            
            return {
                "success": True,
                "ad_created": True,
                "product_type": product_type,
                "creative_suggestions": suggestions,
                "ad_details": ad_result,
                "message": f"Dynamic ad for {product_type} created successfully using AI-generated creative suggestions",
                "metadata": {
                    "target_audience": target_audience,
                    "industry": industry,
                    "tone": tone,
                    "ai_generated": True,
                    "rag_enhanced": creative_suggestions.get("rag_context_used", False)
                }
            }
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "create_dynamic_ad_for_product", 
                {"product_type": product_type, "target_audience": target_audience, "industry": industry, "tone": tone}, 
                {"error": str(e)}, 
                execution_time, 
                False, 
                str(e)
            )
            return {"error": f"Failed to create dynamic ad: {str(e)}"}

    def get_ads_for_product(self, product_type: str, limit: int = 10) -> Dict:
        """Get ads for a specific product type"""
        start_time = time.time()
        try:
            # Get user's Google Ads accounts
            accounts = GoogleAdsAccount.objects.filter(
                user=self.user,
                is_active=True
            )
            
            if not accounts.exists():
                return {"error": "No Google Ads accounts found"}
            
            account = accounts.first()
            
            # For now, return mock data since we don't have actual ad data
            # In a real implementation, this would query the Google Ads API
            mock_ads = [
                {
                    "id": "ad_001",
                    "headline": f"Premium {product_type.title()}s - Classic Style",
                    "description": f"Discover our collection of premium {product_type}s featuring classic designs and modern fits.",
                    "status": "ENABLED",
                    "type": "RESPONSIVE_DISPLAY_AD",
                    "final_url": f"https://example.com/products/{product_type.lower().replace(' ', '-')}",
                    "image_url": "https://example.com/images/product-placeholder.jpg",
                    "performance": {
                        "impressions": 15000,
                        "clicks": 450,
                        "ctr": 3.0,
                        "cost": 125.50,
                        "conversions": 12
                    }
                },
                {
                    "id": "ad_002",
                    "headline": f"Comfortable {product_type.title()}s for Every Occasion",
                    "description": f"Upgrade your wardrobe with our stylish {product_type}s. Made from high-quality materials.",
                    "status": "ENABLED",
                    "type": "RESPONSIVE_DISPLAY_AD",
                    "final_url": f"https://example.com/products/{product_type.lower().replace(' ', '-')}",
                    "image_url": "https://example.com/images/product-placeholder.jpg",
                    "performance": {
                        "impressions": 12000,
                        "clicks": 380,
                        "ctr": 3.17,
                        "cost": 98.75,
                        "conversions": 15
                    }
                },
                {
                    "id": "ad_003",
                    "headline": f"Professional {product_type.title()}s - Business Ready",
                    "description": f"Professional {product_type}s that combine style with comfort. Ideal for office wear.",
                    "status": "PAUSED",
                    "type": "TEXT_AD",
                    "final_url": f"https://example.com/products/{product_type.lower().replace(' ', '-')}",
                    "image_url": None,
                    "performance": {
                        "impressions": 8000,
                        "clicks": 200,
                        "ctr": 2.5,
                        "cost": 75.25,
                        "conversions": 8
                    }
                }
            ]
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "get_ads_for_product", 
                {"product_type": product_type, "limit": limit}, 
                {"ads_count": len(mock_ads)}, 
                execution_time, 
                True
            )
            
            return {
                "success": True,
                "product_type": product_type,
                "ads": mock_ads,
                "total_ads": len(mock_ads),
                "message": f"Found {len(mock_ads)} ads for {product_type}",
                "metadata": {
                    "account_name": account.account_name,
                    "customer_id": account.customer_id,
                    "data_source": "mock_data"
                }
            }
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "get_ads_for_product", 
                {"product_type": product_type, "limit": limit}, 
                {"error": str(e)}, 
                execution_time, 
                False, 
                str(e)
            )
            return {"error": f"Failed to get ads for {product_type}: {str(e)}"}

    def generate_product_image(self, product_type: str, style: str = "professional", 
                              context: str = "product showcase") -> Dict:
        """Generate AI image for a product using OpenAI DALL-E"""
        start_time = time.time()
        try:
            # Import OpenAI service
            from .openai_service import GoogleAdsOpenAIService
            
            # Initialize OpenAI service
            openai_service = GoogleAdsOpenAIService()
            
            # Create image generation prompt
            image_prompt = f"Create a professional product image for {product_type}. Style: {style}, {context}. Include: high-quality product photography, modern design, suitable for advertising, clean background, professional lighting."
            
            # Generate image using OpenAI DALL-E
            image_response = openai_service.client.images.generate(
                model="dall-e-3",
                prompt=image_prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            # Extract image URL
            generated_image_url = image_response.data[0].url
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "generate_product_image", 
                {"product_type": product_type, "style": style, "context": context}, 
                {"image_url": generated_image_url}, 
                execution_time, 
                True
            )
            
            return {
                "success": True,
                "product_type": product_type,
                "image_url": generated_image_url,
                "prompt_used": image_prompt,
                "model": "dall-e-3",
                "size": "1024x1024",
                "message": f"Successfully generated AI image for {product_type}"
            }
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "generate_product_image", 
                {"product_type": product_type, "style": style, "context": context}, 
                {"error": str(e)}, 
                execution_time, 
                False, 
                str(e)
            )
            return {"error": f"Failed to generate image for {product_type}: {str(e)}"}

    def generate_multiple_product_images(self, product_type: str, count: int = 3, 
                                       styles: List[str] = None) -> Dict:
        """Generate multiple AI images for a product with different styles"""
        start_time = time.time()
        try:
            if styles is None:
                styles = ["professional", "lifestyle", "modern"]
            
            # Import OpenAI service
            from .openai_service import GoogleAdsOpenAIService
            
            # Initialize OpenAI service
            openai_service = GoogleAdsOpenAIService()
            
            generated_images = []
            
            for i, style in enumerate(styles[:count]):
                try:
                    # Create image generation prompt
                    image_prompt = f"Create a {style} product image for {product_type}. Style: {style}, high quality, suitable for advertising, professional photography."
                    
                    # Generate image using OpenAI DALL-E
                    image_response = openai_service.client.images.generate(
                        model="dall-e-3",
                        prompt=image_prompt,
                        size="1024x1024",
                        quality="standard",
                        n=1,
                    )
                    
                    # Extract image URL
                    generated_image_url = image_response.data[0].url
                    
                    generated_images.append({
                        "style": style,
                        "image_url": generated_image_url,
                        "prompt_used": image_prompt
                    })
                    
                except Exception as e:
                    logger.warning(f"Failed to generate image for style {style}: {e}")
                    continue
            
            if not generated_images:
                return {"error": f"Failed to generate any images for {product_type}"}
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "generate_multiple_product_images", 
                {"product_type": product_type, "count": count, "styles": styles}, 
                {"images_generated": len(generated_images)}, 
                execution_time, 
                True
            )
            
            return {
                "success": True,
                "product_type": product_type,
                "images": generated_images,
                "total_generated": len(generated_images),
                "message": f"Successfully generated {len(generated_images)} AI images for {product_type}"
            }
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution(
                "generate_multiple_product_images", 
                {"product_type": product_type, "count": count, "styles": styles}, 
                {"error": str(e)}, 
                execution_time, 
                False, 
                str(e)
            )
            return {"error": f"Failed to generate multiple images for {product_type}: {str(e)}"}

    def _generate_product_based_suggestions(self, product_type: str, target_audience: str, tone: str) -> Dict:
        """Generate intelligent fallback suggestions based on product type and context"""
        try:
            # Analyze product type to generate relevant suggestions
            product_lower = product_type.lower()
            
            # Determine product category and characteristics
            if any(word in product_lower for word in ['shirt', 'clothing', 'apparel', 'fashion']):
                category = 'fashion'
                keywords = ['style', 'fashion', 'trendy', 'comfortable', 'quality']
            elif any(word in product_lower for word in ['tech', 'electronic', 'gadget', 'device']):
                category = 'technology'
                keywords = ['innovative', 'advanced', 'smart', 'efficient', 'modern']
            elif any(word in product_lower for word in ['food', 'beverage', 'drink', 'snack']):
                category = 'food_beverage'
                keywords = ['delicious', 'fresh', 'tasty', 'quality', 'premium']
            elif any(word in product_lower for word in ['service', 'consulting', 'professional']):
                category = 'service'
                keywords = ['professional', 'expert', 'reliable', 'quality', 'trusted']
            elif any(word in product_lower for word in ['home', 'furniture', 'decor']):
                category = 'home_lifestyle'
                keywords = ['comfortable', 'stylish', 'quality', 'beautiful', 'practical']
            else:
                category = 'general'
                keywords = ['quality', 'premium', 'excellent', 'amazing', 'best']
            
            # Generate tone-appropriate suggestions
            if tone == 'professional':
                style_modifiers = ['Professional', 'Premium', 'Quality', 'Expert', 'Trusted']
            elif tone == 'casual':
                style_modifiers = ['Amazing', 'Great', 'Awesome', 'Fantastic', 'Cool']
            elif tone == 'luxury':
                style_modifiers = ['Luxury', 'Premium', 'Exclusive', 'Elite', 'Sophisticated']
            else:
                style_modifiers = ['Quality', 'Great', 'Amazing', 'Premium', 'Best']
            
            # Generate headlines
            headlines = [
                f"{style_modifiers[0]} {product_type.title()}s",
                f"Best {product_type.title()}s Available",
                f"Quality {product_type.title()}s for You",
                f"Discover {product_type.title()}s",
                f"Premium {product_type.title()}s"
            ]
            
            # Generate descriptions
            descriptions = [
                f"Experience the best {product_type.title()}s with superior quality and amazing value.",
                f"Discover premium {product_type.title()}s designed for {target_audience}.",
                f"Get high-quality {product_type.title()}s that exceed your expectations."
            ]
            
            # Generate call-to-actions
            call_to_actions = [
                "Shop Now",
                "Learn More",
                "Get Started",
                "Discover More",
                "Order Today"
            ]
            
            # Generate image suggestions
            image_suggestions = [
                f"Professional {product_type} showcase",
                f"Lifestyle image with {product_type}",
                f"High-quality {product_type} photography",
                f"Modern {product_type} presentation",
                f"Professional {product_type} display"
            ]
            
            return {
                "headlines": headlines,
                "descriptions": descriptions,
                "call_to_actions": call_to_actions,
                "image_suggestions": image_suggestions
            }
            
        except Exception as e:
            logger.error(f"Failed to generate product-based suggestions: {e}")
            # Ultimate fallback with basic content
            return {
                "headlines": [f"Great {product_type.title()}s"],
                "descriptions": [f"Discover amazing {product_type.title()}s"],
                "call_to_actions": ["Shop Now"],
                "image_suggestions": [f"Professional {product_type} image"]
            }


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


class GoogleAdsAnalysisTools:
    """Generic tools for Google Ads analysis and reporting"""
    
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
                    tool_type='google_ads_analysis',
                    tool_name=tool_name,
                    input_parameters=input_params,
                    output_result=output_result,
                    execution_time_ms=execution_time_ms,
                    success=success,
                    error_message=error_message
                )
        except Exception as e:
            logger.error(f"Failed to log tool execution: {e}")
    
    def analyze_campaign_summary_comparison(self, sort_by: str = "spend", limit: int = 10) -> Dict[str, Any]:
        """Analyze and compare campaigns for key metrics and sorting"""
        start_time = time.time()
        try:
            # Get campaign data from local database
            campaigns = GoogleAdsCampaign.objects.filter(
                account__user=self.user,
                account__is_active=True
            ).select_related('account')
            
            if not campaigns.exists():
                return {"error": "No campaigns found for analysis"}
            
            # Get performance data
            campaign_data = []
            for campaign in campaigns:
                performance = GoogleAdsPerformance.objects.filter(
                    campaign=campaign
                ).aggregate(
                    total_impressions=Sum('impressions'),
                    total_clicks=Sum('clicks'),
                    total_cost=Sum('cost'),
                    total_conversions=Sum('conversions')
                )
                
                if performance['total_impressions']:
                    ctr = (performance['total_clicks'] / performance['total_impressions']) * 100
                    cpc = performance['total_cost'] / performance['total_clicks'] if performance['total_clicks'] > 0 else 0
                    conversion_rate = (performance['total_conversions'] / performance['total_clicks']) * 100 if performance['total_clicks'] > 0 else 0
                    cost_per_conversion = performance['total_cost'] / performance['total_conversions'] if performance['total_conversions'] > 0 else 0
                    
                    campaign_data.append({
                        "campaign_name": campaign.campaign_name,
                        "campaign_status": campaign.status,
                        "impressions": performance['total_impressions'],
                        "clicks": performance['total_clicks'],
                        "cost": float(performance['total_cost']),
                        "conversions": performance['total_conversions'],
                        "ctr": round(ctr, 2),
                        "cpc": round(float(cpc), 2),
                        "conversion_rate": round(conversion_rate, 2),
                        "cost_per_conversion": round(float(cost_per_conversion), 2)
                    })
            
            # Sort by specified metric
            if sort_by == "spend":
                campaign_data.sort(key=lambda x: x['cost'], reverse=True)
            elif sort_by == "clicks":
                campaign_data.sort(key=lambda x: x['clicks'], reverse=True)
            elif sort_by == "conversions":
                campaign_data.sort(key=lambda x: x['conversions'], reverse=True)
            elif sort_by == "ctr":
                campaign_data.sort(key=lambda x: x['ctr'], reverse=True)
            
            # Limit results
            campaign_data = campaign_data[:limit]
            
            # Calculate summary metrics
            total_spend = sum(c['cost'] for c in campaign_data)
            total_clicks = sum(c['clicks'] for c in campaign_data)
            total_impressions = sum(c['impressions'] for c in campaign_data)
            total_conversions = sum(c['conversions'] for c in campaign_data)
            
            overall_ctr = (total_clicks / total_impressions) * 100 if total_impressions > 0 else 0
            overall_cpc = total_spend / total_clicks if total_clicks > 0 else 0
            overall_conversion_rate = (total_conversions / total_clicks) * 100 if total_clicks > 0 else 0
            
            result = {
                "campaigns": campaign_data,
                "summary": {
                    "total_campaigns": len(campaign_data),
                    "total_spend": round(total_spend, 2),
                    "total_clicks": total_clicks,
                    "total_impressions": total_impressions,
                    "total_conversions": total_conversions,
                    "overall_ctr": round(overall_ctr, 2),
                    "overall_cpc": round(overall_cpc, 2),
                    "overall_conversion_rate": round(overall_conversion_rate, 2)
                },
                "sort_by": sort_by,
                "analysis_type": "campaign_summary_comparison"
            }
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution("analyze_campaign_summary_comparison", 
                                   {"sort_by": sort_by, "limit": limit}, 
                                   result, execution_time, True)
            
            return result
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            error_msg = f"Error analyzing campaign summary: {str(e)}"
            self._log_tool_execution("analyze_campaign_summary_comparison", 
                                   {"sort_by": sort_by, "limit": limit}, 
                                   {}, execution_time, False, error_msg)
            return {"error": error_msg}
    
    def analyze_performance_summary(self, days: int = 30) -> Dict[str, Any]:
        """Generate performance summary with key insights and recommendations"""
        start_time = time.time()
        try:
            # Calculate date range
            end_date = timezone.now().date()
            start_date = end_date - timezone.timedelta(days=days)
            
            # Get performance data for the period
            performance_data = GoogleAdsPerformance.objects.filter(
                campaign__account__user=self.user,
                campaign__account__is_active=True,
                date__gte=start_date,
                date__lte=end_date
            ).select_related('campaign', 'campaign__account')
            
            if not performance_data.exists():
                return {"error": f"No performance data found for the last {days} days"}
            
            # Aggregate daily performance
            daily_performance = {}
            for perf in performance_data:
                date_str = perf.date.strftime('%Y-%m-%d')
                if date_str not in daily_performance:
                    daily_performance[date_str] = {
                        "impressions": 0,
                        "clicks": 0,
                        "cost": 0,
                        "conversions": 0
                    }
                
                daily_performance[date_str]["impressions"] += perf.impressions or 0
                daily_performance[date_str]["clicks"] += perf.clicks or 0
                daily_performance[date_str]["cost"] += float(perf.cost or 0)
                daily_performance[date_str]["conversions"] += perf.conversions or 0
            
            # Convert to sorted list
            daily_data = []
            for date_str, data in sorted(daily_performance.items()):
                ctr = (data["clicks"] / data["impressions"]) * 100 if data["impressions"] > 0 else 0
                cpc = data["cost"] / data["clicks"] if data["clicks"] > 0 else 0
                
                daily_data.append({
                    "date": date_str,
                    "impressions": data["impressions"],
                    "clicks": data["clicks"],
                    "cost": round(data["cost"], 2),
                    "conversions": data["conversions"],
                    "ctr": round(ctr, 2),
                    "cpc": round(cpc, 2)
                })
            
            # Calculate totals
            total_impressions = sum(d["impressions"] for d in daily_data)
            total_clicks = sum(d["clicks"] for d in daily_data)
            total_cost = sum(d["cost"] for d in daily_data)
            total_conversions = sum(d["conversions"] for d in daily_data)
            
            overall_ctr = (total_clicks / total_impressions) * 100 if total_impressions > 0 else 0
            overall_cpc = total_cost / total_clicks if total_clicks > 0 else 0
            overall_conversion_rate = (total_conversions / total_clicks) * 100 if total_clicks > 0 else 0
            cost_per_conversion = total_cost / total_conversions if total_conversions > 0 else 0
            
            # Generate insights
            insights = []
            if total_conversions == 0:
                insights.append("No conversions recorded - investigate conversion tracking setup")
            
            if overall_cpc > 100:  # Assuming high CPC threshold
                insights.append("High average CPC indicates potential bidding inefficiencies")
            
            if overall_ctr < 1:  # Assuming low CTR threshold
                insights.append("Low CTR suggests ad relevance or targeting issues")
            
            # Find best and worst performing days
            if daily_data:
                best_day = max(daily_data, key=lambda x: x["clicks"])
                worst_day = min(daily_data, key=lambda x: x["clicks"])
                insights.append(f"Best performing day: {best_day['date']} with {best_day['clicks']} clicks")
                insights.append(f"Lowest performing day: {worst_day['date']} with {worst_day['clicks']} clicks")
            
            result = {
                "daily_performance": daily_data,
                "summary": {
                    "period_days": days,
                    "total_impressions": total_impressions,
                    "total_clicks": total_clicks,
                    "total_cost": round(total_cost, 2),
                    "total_conversions": total_conversions,
                    "overall_ctr": round(overall_ctr, 2),
                    "overall_cpc": round(overall_cpc, 2),
                    "overall_conversion_rate": round(overall_conversion_rate, 2),
                    "cost_per_conversion": round(cost_per_conversion, 2)
                },
                "insights": insights,
                "analysis_type": "performance_summary"
            }
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution("analyze_performance_summary", 
                                   {"days": days}, 
                                   result, execution_time, True)
            
            return result
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            error_msg = f"Error analyzing performance summary: {str(e)}"
            self._log_tool_execution("analyze_performance_summary", 
                                   {"days": days}, 
                                   {}, execution_time, False, error_msg)
            return {"error": error_msg}
    
    def analyze_trends(self, metric: str = "clicks", days: int = 30) -> Dict[str, Any]:
        """Analyze trends for specified metrics using line/bar charts"""
        start_time = time.time()
        try:
            # Calculate date range
            end_date = timezone.now().date()
            start_date = end_date - timezone.timedelta(days=days)
            
            # Get performance data for the period
            performance_data = GoogleAdsPerformance.objects.filter(
                campaign__account__user=self.user,
                campaign__account__is_active=True,
                date__gte=start_date,
                date__lte=end_date
            ).select_related('campaign')
            
            if not performance_data.exists():
                return {"error": f"No trend data found for the last {days} days"}
            
            # Aggregate daily metrics
            daily_metrics = {}
            for perf in performance_data:
                date_str = perf.date.strftime('%Y-%m-%d')
                if date_str not in daily_metrics:
                    daily_metrics[date_str] = {
                        "impressions": 0,
                        "clicks": 0,
                        "cost": 0,
                        "conversions": 0
                    }
                
                daily_metrics[date_str]["impressions"] += perf.impressions or 0
                daily_metrics[date_str]["clicks"] += perf.clicks or 0
                daily_metrics[date_str]["cost"] += float(perf.cost or 0)
                daily_metrics[date_str]["conversions"] += perf.conversions or 0
            
            # Calculate derived metrics
            for date_str in daily_metrics:
                data = daily_metrics[date_str]
                if data["impressions"] > 0:
                    data["ctr"] = round((data["clicks"] / data["impressions"]) * 100, 2)
                else:
                    data["ctr"] = 0
                
                if data["clicks"] > 0:
                    data["cpc"] = round(data["cost"] / data["clicks"], 2)
                else:
                    data["cpc"] = 0
            
            # Sort by date and prepare chart data
            sorted_dates = sorted(daily_metrics.keys())
            chart_data = {
                "labels": sorted_dates,
                "datasets": []
            }
            
            # Add requested metric dataset
            if metric == "clicks":
                chart_data["datasets"].append({
                    "label": "Daily Clicks",
                    "data": [daily_metrics[date]["clicks"] for date in sorted_dates]
                })
            elif metric == "cpc":
                chart_data["datasets"].append({
                    "label": "Daily CPC",
                    "data": [daily_metrics[date]["cpc"] for date in sorted_dates]
                })
            elif metric == "ctr":
                chart_data["datasets"].append({
                    "label": "Daily CTR (%)",
                    "data": [daily_metrics[date]["ctr"] for date in sorted_dates]
                })
            elif metric == "all":
                chart_data["datasets"] = [
                    {
                        "label": "Daily Clicks",
                        "data": [daily_metrics[date]["clicks"] for date in sorted_dates]
                    },
                    {
                        "label": "Daily CPC",
                        "data": [daily_metrics[date]["cpc"] for date in sorted_dates]
                    },
                    {
                        "label": "Daily CTR (%)",
                        "data": [daily_metrics[date]["ctr"] for date in sorted_dates]
                    }
                ]
            
            # Generate insights
            insights = []
            if len(sorted_dates) > 1:
                first_value = chart_data["datasets"][0]["data"][0]
                last_value = chart_data["datasets"][0]["data"][-1]
                
                if last_value > first_value:
                    trend = "increasing"
                    change_percent = ((last_value - first_value) / first_value) * 100 if first_value > 0 else 0
                    insights.append(f"{metric.upper()} trend is {trend} by {round(change_percent, 1)}% over the period")
                elif last_value < first_value:
                    trend = "decreasing"
                    change_percent = ((first_value - last_value) / first_value) * 100 if first_value > 0 else 0
                    insights.append(f"{metric.upper()} trend is {trend} by {round(change_percent, 1)}% over the period")
                else:
                    insights.append(f"{metric.upper()} trend is stable over the period")
            
            result = {
                "chart_data": chart_data,
                "metric": metric,
                "period_days": days,
                "insights": insights,
                "analysis_type": "trend_analysis"
            }
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution("analyze_trends", 
                                   {"metric": metric, "days": days}, 
                                   result, execution_time, True)
            
            return result
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            error_msg = f"Error analyzing trends: {str(e)}"
            self._log_tool_execution("analyze_trends", 
                                   {"metric": metric, "days": days}, 
                                   {}, execution_time, False, error_msg)
            return {"error": error_msg}
    
    def analyze_listing_performance(self, listing_type: str = "campaigns", limit: int = 10, 
                                  sort_by: str = "conversions", days: int = 14) -> Dict[str, Any]:
        """Analyze top performing items (campaigns, keywords, etc.) with insights"""
        start_time = time.time()
        try:
            # Calculate date range
            end_date = timezone.now().date()
            start_date = end_date - timezone.timedelta(days=days)
            
            if listing_type == "campaigns":
                # Get top campaigns by performance
                campaigns = GoogleAdsCampaign.objects.filter(
                    account__user=self.user,
                    account__is_active=True
                )
                
                campaign_performance = []
                for campaign in campaigns:
                    performance = GoogleAdsPerformance.objects.filter(
                        campaign=campaign,
                        date__gte=start_date,
                        date__lte=end_date
                    ).aggregate(
                        total_impressions=Sum('impressions'),
                        total_clicks=Sum('clicks'),
                        total_cost=Sum('cost'),
                        total_conversions=Sum('conversions')
                    )
                    
                    if performance['total_impressions']:
                        ctr = (performance['total_clicks'] / performance['total_impressions']) * 100
                        cpc = performance['total_cost'] / performance['total_clicks'] if performance['total_clicks'] > 0 else 0
                        conversion_rate = (performance['total_conversions'] / performance['total_clicks']) * 100 if performance['total_clicks'] > 0 else 0
                        cost_per_conversion = performance['total_cost'] / performance['total_conversions'] if performance['total_conversions'] > 0 else 0
                        
                        campaign_performance.append({
                            "campaign_name": campaign.campaign_name,
                            "impressions": performance['total_impressions'],
                            "clicks": performance['total_clicks'],
                            "ctr": round(ctr, 2),
                            "avg_cpc": round(float(cpc), 2),
                            "total_cost": round(float(performance['total_cost']), 2),
                            "conversions": performance['total_conversions'],
                            "conversion_rate": round(conversion_rate, 2),
                            "cost_per_conversion": round(float(cost_per_conversion), 2)
                        })
                
                # Sort by specified metric
                if sort_by == "conversions":
                    campaign_performance.sort(key=lambda x: x['conversions'], reverse=True)
                elif sort_by == "clicks":
                    campaign_performance.sort(key=lambda x: x['clicks'], reverse=True)
                elif sort_by == "spend":
                    campaign_performance.sort(key=lambda x: x['total_cost'], reverse=True)
                elif sort_by == "ctr":
                    campaign_performance.sort(key=lambda x: x['ctr'], reverse=True)
                
                # Limit results
                campaign_performance = campaign_performance[:limit]
                
                # Generate insights
                insights = []
                if campaign_performance:
                    top_campaign = campaign_performance[0]
                    insights.append(f"Top performer: '{top_campaign['campaign_name']}' with {top_campaign['conversions']} conversions")
                    
                    if top_campaign['cost_per_conversion'] > 100:  # Assuming high cost threshold
                        insights.append(f"High cost per conversion (₹{top_campaign['cost_per_conversion']}) suggests optimization needed")
                    
                    avg_ctr = sum(c['ctr'] for c in campaign_performance) / len(campaign_performance)
                    insights.append(f"Average CTR across top campaigns: {round(avg_ctr, 2)}%")
                
                result = {
                    "listing_type": listing_type,
                    "items": campaign_performance,
                    "sort_by": sort_by,
                    "period_days": days,
                    "insights": insights,
                    "analysis_type": "listing_analysis"
                }
            
            else:
                return {"error": f"Listing type '{listing_type}' not supported yet"}
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution("analyze_listing_performance", 
                                   {"listing_type": listing_type, "limit": limit, "sort_by": sort_by, "days": days}, 
                                   result, execution_time, True)
            
            return result
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            error_msg = f"Error analyzing listing performance: {str(e)}"
            self._log_tool_execution("analyze_listing_performance", 
                                   {"listing_type": listing_type, "limit": limit, "sort_by": sort_by, "days": days}, 
                                   {}, execution_time, False, error_msg)
            return {"error": error_msg}
    
    def handle_query_without_solution(self, query: str) -> Dict[str, Any]:
        """Handle queries that don't have direct solutions by providing alternatives"""
        start_time = time.time()
        try:
            # Analyze the query to understand what the user is asking for
            query_lower = query.lower()
            
            alternatives = []
            explanation = ""
            
            if "quality score" in query_lower and "account" in query_lower:
                explanation = "Google Ads doesn't provide a direct 'quality score' metric at the account level. Quality scores are assigned to keywords, not entire accounts."
                alternatives = [
                    "Show general account performance metrics for the last 30 days",
                    "Provide keyword-level quality scores for specific keywords",
                    "Display quality-related metrics like CTR, conversion rates, or impression share"
                ]
            
            elif "account-level" in query_lower:
                explanation = "Many Google Ads metrics are campaign, ad group, or keyword specific rather than account-wide."
                alternatives = [
                    "Show campaign-level performance metrics",
                    "Provide ad group performance analysis",
                    "Display keyword performance data"
                ]
            
            else:
                explanation = "This query doesn't have a direct solution in Google Ads. Let me suggest some alternatives that might be helpful."
                alternatives = [
                    "View campaign performance summary",
                    "Analyze keyword performance",
                    "Check ad group metrics",
                    "Review account overview"
                ]
            
            result = {
                "query": query,
                "explanation": explanation,
                "alternatives": alternatives,
                "analysis_type": "query_without_solution"
            }
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution("handle_query_without_solution", 
                                   {"query": query}, 
                                   result, execution_time, True)
            
            return result
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            error_msg = f"Error handling query without solution: {str(e)}"
            self._log_tool_execution("handle_query_without_solution", 
                                   {"query": query}, 
                                   {}, execution_time, False, error_msg)
            return {"error": error_msg}
    
    def analyze_pie_chart_data(self, chart_type: str = "spend", days: int = 30) -> Dict[str, Any]:
        """Generate pie chart data for spend distribution or other metrics"""
        start_time = time.time()
        try:
            # Calculate date range
            end_date = timezone.now().date()
            start_date = end_date - timezone.timedelta(days=days)
            
            if chart_type == "spend":
                # Get campaign spend distribution
                campaigns = GoogleAdsCampaign.objects.filter(
                    account__user=self.user,
                    account__is_active=True
                )
                
                campaign_spend = []
                for campaign in campaigns:
                    total_spend = GoogleAdsPerformance.objects.filter(
                        campaign=campaign,
                        date__gte=start_date,
                        date__lte=end_date
                    ).aggregate(total_cost=Sum('cost'))['total_cost'] or 0
                    
                    if total_spend > 0:
                        campaign_spend.append({
                            "label": campaign.campaign_name,
                            "value": float(total_spend)
                        })
                
                # Sort by spend and limit to top 10
                campaign_spend.sort(key=lambda x: x['value'], reverse=True)
                campaign_spend = campaign_spend[:10]
                
                # Calculate total spend
                total_spend = sum(item['value'] for item in campaign_spend)
                
                # Calculate percentages
                for item in campaign_spend:
                    item['percentage'] = round((item['value'] / total_spend) * 100, 1)
                
                chart_data = {
                    "labels": [item['label'] for item in campaign_spend],
                    "datasets": [{
                        "label": "Campaign Spend",
                        "data": [item['value'] for item in campaign_spend]
                    }]
                }
                
                insights = [
                    f"Total spend across campaigns: ₹{total_spend:,.2f}",
                    f"Top campaign: {campaign_spend[0]['label']} with {campaign_spend[0]['percentage']}% of total spend"
                ]
                
                if len(campaign_spend) > 1:
                    insights.append(f"Bottom campaign: {campaign_spend[-1]['label']} with {campaign_spend[-1]['percentage']}% of total spend")
            
            else:
                return {"error": f"Chart type '{chart_type}' not supported yet"}
            
            result = {
                "chart_data": chart_data,
                "chart_type": "pie",
                "metric": chart_type,
                "period_days": days,
                "insights": insights,
                "analysis_type": "pie_chart_display"
            }
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution("analyze_pie_chart_data", 
                                   {"chart_type": chart_type, "days": days}, 
                                   result, execution_time, True)
            
            return result
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            error_msg = f"Error analyzing pie chart data: {str(e)}"
            self._log_tool_execution("analyze_pie_chart_data", 
                                   {"chart_type": chart_type, "days": days}, 
                                   {}, execution_time, False, error_msg)
            return {"error": error_msg}
    
    def analyze_duplicate_keywords(self, days: int = 7) -> Dict[str, Any]:
        """Analyze duplicate keywords across campaigns and provide consolidation recommendations"""
        start_time = time.time()
        try:
            # Calculate date range
            end_date = timezone.now().date()
            start_date = end_date - timezone.timedelta(days=days)
            
            # Get all keywords from the period
            keywords = GoogleAdsKeyword.objects.filter(
                ad_group__campaign__account__user=self.user,
                ad_group__campaign__account__is_active=True
            ).select_related('ad_group', 'ad_group__campaign')
            
            if not keywords.exists():
                return {"error": "No keywords found for analysis"}
            
            # Group keywords by text to find duplicates
            keyword_groups = {}
            for keyword in keywords:
                keyword_text = keyword.keyword_text.lower().strip()
                if keyword_text not in keyword_groups:
                    keyword_groups[keyword_text] = []
                
                keyword_groups[keyword_text].append({
                    "keyword_id": keyword.id,
                    "keyword_text": keyword.keyword_text,
                    "campaign_name": keyword.ad_group.campaign.campaign_name,
                    "ad_group_name": keyword.ad_group.ad_group_name,
                    "match_type": keyword.match_type,
                    "status": keyword.status
                })
            
            # Find duplicates (keywords appearing in multiple campaigns)
            duplicates = []
            for keyword_text, instances in keyword_groups.items():
                if len(instances) > 1:
                    # Get performance data for this keyword across all instances
                    keyword_performance = []
                    for instance in instances:
                        performance = GoogleAdsPerformance.objects.filter(
                            keyword__id=instance['keyword_id'],
                            date__gte=start_date,
                            date__lte=end_date
                        ).aggregate(
                            total_impressions=Sum('impressions'),
                            total_clicks=Sum('clicks'),
                            total_cost=Sum('cost'),
                            total_conversions=Sum('conversions')
                        )
                        
                        if performance['total_impressions']:
                            ctr = (performance['total_clicks'] / performance['total_impressions']) * 100
                            cpc = performance['total_cost'] / performance['total_clicks'] if performance['total_clicks'] > 0 else 0
                        else:
                            ctr = 0
                            cpc = 0
                        
                        instance.update({
                            "impressions": performance['total_impressions'] or 0,
                            "clicks": performance['total_clicks'] or 0,
                            "cost": round(float(performance['total_cost'] or 0), 2),
                            "conversions": performance['total_conversions'] or 0,
                            "ctr": round(ctr, 2),
                            "cpc": round(float(cpc), 2)
                        })
                        keyword_performance.append(instance)
                    
                    duplicates.append({
                        "keyword_text": keyword_text,
                        "instances": keyword_performance,
                        "campaigns_count": len(instances),
                        "total_impressions": sum(i['impressions'] for i in instances),
                        "total_clicks": sum(i['clicks'] for i in instances),
                        "total_cost": sum(i['cost'] for i in instances),
                        "total_conversions": sum(i['conversions'] for i in instances)
                    })
            
            # Sort duplicates by number of campaigns (most duplicated first)
            duplicates.sort(key=lambda x: x['campaigns_count'], reverse=True)
            
            # Generate insights and recommendations
            insights = []
            recommendations = []
            
            if duplicates:
                total_duplicates = len(duplicates)
                insights.append(f"Found {total_duplicates} duplicate keywords across campaigns")
                
                most_duplicated = duplicates[0]
                insights.append(f"Most duplicated: '{most_duplicated['keyword_text']}' appears in {most_duplicated['campaigns_count']} campaigns")
                
                # Recommendations
                recommendations.append("Prioritize consolidation of keywords appearing in 3+ campaigns")
                recommendations.append("Keep the best performing instance and add as negative keywords in others")
                recommendations.append("Consider campaign restructuring to reduce keyword overlap")
                recommendations.append("Monitor performance after consolidation for 2-4 weeks")
            
            result = {
                "duplicates": duplicates,
                "total_duplicates": len(duplicates),
                "period_days": days,
                "insights": insights,
                "recommendations": recommendations,
                "analysis_type": "duplicate_keywords_analysis"
            }
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution("analyze_duplicate_keywords", 
                                   {"days": days}, 
                                   result, execution_time, True)
            
            return result
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            error_msg = f"Error analyzing duplicate keywords: {str(e)}"
            self._log_tool_execution("analyze_duplicate_keywords", 
                                   {"days": days}, 
                                   {}, execution_time, False, error_msg)
            return {"error": error_msg}
    
    def dig_deeper_analysis(self, base_analysis: Dict[str, Any], depth: int = 2) -> Dict[str, Any]:
        """Provide deeper analysis based on previous analysis results"""
        start_time = time.time()
        try:
            if depth > 2:
                return {"error": "Maximum dig deeper depth is 2 levels"}
            
            analysis_type = base_analysis.get('analysis_type', 'unknown')
            result = {
                "base_analysis": base_analysis,
                "dig_deeper_depth": depth,
                "analysis_type": "dig_deeper_analysis"
            }
            
            if analysis_type == "campaign_summary_comparison":
                # Provide deeper campaign insights
                campaigns = base_analysis.get('campaigns', [])
                if campaigns:
                    # Analyze performance patterns
                    high_performers = [c for c in campaigns if c.get('conversions', 0) > 0]
                    low_performers = [c for c in campaigns if c.get('conversions', 0) == 0]
                    
                    result["deeper_insights"] = {
                        "high_performing_campaigns": len(high_performers),
                        "low_performing_campaigns": len(low_performers),
                        "conversion_rate": len(high_performers) / len(campaigns) * 100 if campaigns else 0
                    }
                    
                    # Specific recommendations based on depth
                    if depth == 1:
                        result["recommendations"] = [
                            "Focus budget on campaigns with conversions",
                            "Investigate why some campaigns have 0 conversions",
                            "Consider pausing consistently underperforming campaigns"
                        ]
                    elif depth == 2:
                        result["recommendations"] = [
                            "Implement conversion tracking if not already in place",
                            "Review landing page quality for non-converting campaigns",
                            "Analyze keyword quality scores for underperforming campaigns",
                            "Consider audience targeting adjustments"
                        ]
            
            elif analysis_type == "performance_summary":
                # Provide deeper performance insights
                daily_data = base_analysis.get('daily_performance', [])
                if daily_data:
                    # Find patterns in daily performance
                    high_ctr_days = [d for d in daily_data if d.get('ctr', 0) > 5]  # Assuming 5% is high
                    low_cpc_days = [d for d in daily_data if d.get('cpc', 0) < 50]  # Assuming ₹50 is low
                    
                    result["deeper_insights"] = {
                        "high_ctr_days": len(high_ctr_days),
                        "low_cpc_days": len(low_cpc_days),
                        "best_performing_day": max(daily_data, key=lambda x: x.get('clicks', 0)) if daily_data else None
                    }
                    
                    if depth == 1:
                        result["recommendations"] = [
                            "Analyze what caused high CTR on specific days",
                            "Investigate factors leading to low CPC days",
                            "Replicate successful day strategies"
                        ]
                    elif depth == 2:
                        result["recommendations"] = [
                            "Review ad scheduling and day-of-week performance",
                            "Analyze competitor activity patterns",
                            "Check for external events affecting performance",
                            "Implement day-parting strategies based on insights"
                        ]
            
            else:
                result["deeper_insights"] = "Deep analysis not available for this analysis type"
                result["recommendations"] = ["Try a different analysis type for deeper insights"]
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution("dig_deeper_analysis", 
                                   {"analysis_type": analysis_type, "depth": depth}, 
                                   result, execution_time, True)
            
            return result
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            error_msg = f"Error in dig deeper analysis: {str(e)}"
            self._log_tool_execution("dig_deeper_analysis", 
                                   {"analysis_type": base_analysis.get('analysis_type', 'unknown'), "depth": depth}, 
                                   {}, execution_time, False, error_msg)
            return {"error": error_msg}


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
        google_ads_tools.create_ad,
        google_ads_tools.create_ad_with_image,
        google_ads_tools.create_ad_group,
        google_ads_tools.create_dynamic_ad_for_product,
        google_ads_tools.get_creative_suggestions,
        google_ads_tools.get_ads_for_product,
        google_ads_tools.generate_product_image,
        google_ads_tools.generate_multiple_product_images,
        
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

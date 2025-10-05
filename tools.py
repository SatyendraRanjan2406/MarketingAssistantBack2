"""
Marketing Tools - Unified API for Google Ads and Meta Marketing
Provides standardized functions for campaign management across platforms
"""

import os
import sys
import django
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import json
from asgiref.sync import sync_to_async

# Add the project directory to Python path
sys.path.insert(0, '/Users/satyendra/marketing_assistant_back')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

from django.conf import settings
from accounts.google_oauth_service import UserGoogleAuthService
from django.contrib.auth.models import User
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import requests

logger = logging.getLogger(__name__)

class MarketingTools:
    """Unified marketing tools for Google Ads and Meta Marketing APIs"""
    
    def __init__(self):
        self.google_ads_client = None
        self.meta_access_token = None
    
    async def GET_CAMPAIGNS(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch campaign metadata & status for an account.
        
        Parameters:
        - provider: 'google' | 'meta'
        - accountId: string (Google customerId or Meta adAccountId)
        - fields?: string[] (requested fields)
        - status?: string[] (e.g., ['ENABLED','PAUSED'])
        - dateRange?: { from: 'YYYY-MM-DD'; to: 'YYYY-MM-DD' }
        - includeMetrics?: boolean
        - metrics?: string[] (if includeMetrics)
        - limit?: number, cursor?: string
        - filters?: Record<string, any>
        
        Returns:
        - campaigns: Array<any>
        - nextCursor?: string|null
        """
        try:
            provider = params.get('provider', '').lower()
            account_id = params.get('accountId')
            
            if not provider or not account_id:
                raise ValueError("provider and accountId are required")
            
            if provider == 'google':
                return await self._get_google_campaigns(params)
            elif provider == 'meta':
                return await self._get_meta_campaigns(params)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
                
        except Exception as e:
            logger.error(f"Error in GET_CAMPAIGNS: {str(e)}")
            return {
                "campaigns": [],
                "nextCursor": None,
                "error": str(e)
            }
    
    async def _get_google_campaigns(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get campaigns from Google Ads API"""
        try:
            # Get Google Ads client
            client = await self._get_google_ads_client()
            if not client:
                raise Exception("Google Ads client not available")
            
            account_id = params['accountId']
            fields = params.get('fields', [])
            status = params.get('status', [])
            date_range = params.get('dateRange')
            include_metrics = params.get('includeMetrics', False)
            metrics = params.get('metrics', [])
            limit = params.get('limit', 50)
            filters = params.get('filters', {})
            
            # Build GAQL query
            query = self._build_google_campaigns_query(
                fields, status, date_range, include_metrics, metrics, filters, limit
            )
            
            # Execute query
            ga_service = client.get_service("GoogleAdsService")
            response = ga_service.search(customer_id=account_id, query=query)
            
            campaigns = []
            for row in response:
                campaign_data = self._parse_google_campaign_row(row, include_metrics)
                campaigns.append(campaign_data)
            
            return {
                "campaigns": campaigns,
                "nextCursor": None  # Google Ads doesn't use cursor pagination
            }
            
        except Exception as e:
            logger.error(f"Error fetching Google campaigns: {str(e)}")
            raise
    
    async def _get_meta_campaigns(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get campaigns from Meta Marketing API"""
        try:
            # Get Meta access token
            access_token = await self._get_meta_access_token()
            if not access_token:
                raise Exception("Meta access token not available")
            
            account_id = params['accountId']
            fields = params.get('fields', [])
            status = params.get('status', [])
            date_range = params.get('dateRange')
            include_metrics = params.get('includeMetrics', False)
            metrics = params.get('metrics', [])
            limit = params.get('limit', 50)
            cursor = params.get('cursor')
            filters = params.get('filters', {})
            
            # Build Meta API request
            url = f"https://graph.facebook.com/v18.0/act_{account_id}/campaigns"
            
            # Prepare fields
            if not fields:
                fields = ['id', 'name', 'status', 'start_time', 'stop_time', 'created_time', 'updated_time']
            
            if include_metrics and metrics:
                # Add insights for metrics
                insights_fields = ','.join(metrics)
                fields.append(f'insights{{{insights_fields}}}')
            
            # Prepare parameters
            api_params = {
                'access_token': access_token,
                'fields': ','.join(fields),
                'limit': min(limit, 100)  # Meta API limit
            }
            
            if cursor:
                api_params['after'] = cursor
            
            if status:
                # Meta status mapping
                status_mapping = {
                    'ENABLED': 'ACTIVE',
                    'PAUSED': 'PAUSED',
                    'REMOVED': 'DELETED'
                }
                meta_status = [status_mapping.get(s, s) for s in status]
                api_params['status'] = ','.join(meta_status)
            
            if date_range and include_metrics:
                api_params['time_range'] = json.dumps({
                    'since': date_range['from'],
                    'until': date_range['to']
                })
            
            # Apply filters
            for key, value in filters.items():
                api_params[key] = value
            
            # Make API request
            response = requests.get(url, params=api_params)
            response.raise_for_status()
            
            data = response.json()
            campaigns = data.get('data', [])
            
            # Parse campaigns
            parsed_campaigns = []
            for campaign in campaigns:
                campaign_data = self._parse_meta_campaign(campaign, include_metrics)
                parsed_campaigns.append(campaign_data)
            
            # Get next cursor
            next_cursor = None
            paging = data.get('paging', {})
            if 'next' in paging:
                next_cursor = paging['cursors'].get('after')
            
            return {
                "campaigns": parsed_campaigns,
                "nextCursor": next_cursor
            }
            
        except Exception as e:
            logger.error(f"Error fetching Meta campaigns: {str(e)}")
            raise
    
    def _build_google_campaigns_query(self, fields: List[str], status: List[str], 
                                    date_range: Dict, include_metrics: bool, 
                                    metrics: List[str], filters: Dict, limit: int) -> str:
        """Build GAQL query for Google Ads campaigns"""
        
        # Default fields if none specified
        if not fields:
            fields = ['campaign.id', 'campaign.name', 'campaign.status', 
                     'campaign.start_date', 'campaign.end_date', 'campaign.advertising_channel_type']
        
        # Add metrics if requested
        if include_metrics and metrics:
            # Map common metric names to GAQL fields
            metric_mapping = {
                'impressions': 'metrics.impressions',
                'clicks': 'metrics.clicks',
                'cost': 'metrics.cost_micros',
                'conversions': 'metrics.conversions',
                'ctr': 'metrics.ctr',
                'cpc': 'metrics.average_cpc',
                'cpm': 'metrics.average_cpm',
                'cpa': 'metrics.average_cpa'
            }
            
            for metric in metrics:
                if metric in metric_mapping:
                    fields.append(metric_mapping[metric])
        
        # Build SELECT clause
        select_clause = f"SELECT {', '.join(fields)}"
        
        # Build FROM clause
        from_clause = "FROM campaign"
        
        # Build WHERE clause
        where_conditions = []
        
        if status:
            # Use IN clause instead of OR with parentheses
            status_list = "', '".join(status)
            where_conditions.append(f"campaign.status IN ('{status_list}')")
        else:
            where_conditions.append("campaign.status != 'REMOVED'")
        
        if date_range and include_metrics:
            from_date = date_range['from'].replace('-', '')
            to_date = date_range['to'].replace('-', '')
            where_conditions.append(f"segments.date BETWEEN '{from_date}' AND '{to_date}'")
        
        # Add custom filters
        for key, value in filters.items():
            if isinstance(value, list):
                # Use IN clause for list values
                value_list = "', '".join(str(v) for v in value)
                where_conditions.append(f"{key} IN ('{value_list}')")
            else:
                where_conditions.append(f"{key} = '{value}'")
        
        where_clause = f"WHERE {' AND '.join(where_conditions)}" if where_conditions else ""
        
        # Build ORDER BY clause
        order_clause = "ORDER BY campaign.name"
        
        # Build LIMIT clause
        limit_clause = f"LIMIT {limit}"
        
        # Combine all clauses
        query = f"{select_clause} {from_clause} {where_clause} {order_clause} {limit_clause}"
        
        return query
    
    def _parse_google_campaign_row(self, row, include_metrics: bool) -> Dict[str, Any]:
        """Parse Google Ads campaign row into standardized format"""
        campaign = row.campaign
        
        campaign_data = {
            "id": str(campaign.id),
            "name": campaign.name,
            "status": campaign.status.name,
            "advertisingChannelType": campaign.advertising_channel_type.name,
            "startDate": campaign.start_date,
            "endDate": campaign.end_date if campaign.end_date else None
        }
        
        if include_metrics and hasattr(row, 'metrics'):
            metrics = row.metrics
            campaign_data.update({
                "impressions": getattr(metrics, 'impressions', 0),
                "clicks": getattr(metrics, 'clicks', 0),
                "cost": getattr(metrics, 'cost_micros', 0) / 1000000,  # Convert from micros
                "conversions": getattr(metrics, 'conversions', 0),
                "ctr": getattr(metrics, 'ctr', 0),
                "cpc": getattr(metrics, 'average_cpc', 0) / 1000000,  # Convert from micros
                "cpm": getattr(metrics, 'average_cpm', 0) / 1000000,  # Convert from micros
                "cpa": getattr(metrics, 'average_cpa', 0) / 1000000   # Convert from micros
            })
        
        return campaign_data
    
    def _parse_meta_campaign(self, campaign: Dict, include_metrics: bool) -> Dict[str, Any]:
        """Parse Meta campaign into standardized format"""
        campaign_data = {
            "id": campaign.get('id'),
            "name": campaign.get('name'),
            "status": campaign.get('status'),
            "startDate": campaign.get('start_time'),
            "endDate": campaign.get('stop_time'),
            "createdTime": campaign.get('created_time'),
            "updatedTime": campaign.get('updated_time')
        }
        
        if include_metrics and 'insights' in campaign:
            insights = campaign['insights']
            if insights and 'data' in insights:
                metrics_data = insights['data'][0] if insights['data'] else {}
                campaign_data.update({
                    "impressions": metrics_data.get('impressions', 0),
                    "clicks": metrics_data.get('clicks', 0),
                    "cost": metrics_data.get('spend', 0),
                    "conversions": metrics_data.get('conversions', 0),
                    "ctr": metrics_data.get('ctr', 0),
                    "cpc": metrics_data.get('cpc', 0),
                    "cpm": metrics_data.get('cpm', 0),
                    "cpa": metrics_data.get('cpa', 0)
                })
        
        return campaign_data
    
    async def _get_google_ads_client(self) -> Optional[GoogleAdsClient]:
        """Get Google Ads client with OAuth authentication"""
        try:
            if self.google_ads_client:
                return self.google_ads_client
            
            from accounts.models import UserGoogleAuth
            
            # Get the first active user auth (in production, you'd pass user_id)
            user_auth = await sync_to_async(UserGoogleAuth.objects.filter(is_active=True).first)()
            
            if not user_auth or not user_auth.refresh_token:
                logger.warning("No OAuth authentication found")
                return None
            
            config = {
                'developer_token': os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN'),
                'client_id': os.getenv('GOOGLE_ADS_CLIENT_ID'),
                'client_secret': os.getenv('GOOGLE_ADS_CLIENT_SECRET'),
                'refresh_token': user_auth.refresh_token,
                'use_proto_plus': True
            }
            
            required_fields = ['developer_token', 'client_id', 'client_secret', 'refresh_token']
            missing_fields = [field for field in required_fields if not config.get(field)]
            
            if missing_fields:
                logger.warning(f"Missing Google Ads configuration: {missing_fields}")
                return None
            
            self.google_ads_client = GoogleAdsClient.load_from_dict(config)
            return self.google_ads_client
            
        except Exception as e:
            logger.error(f"Error creating Google Ads client: {e}")
            return None
    
    async def _get_meta_access_token(self) -> Optional[str]:
        """Get Meta access token"""
        try:
            if self.meta_access_token:
                return self.meta_access_token
            
            # In production, you'd get this from user's stored tokens
            self.meta_access_token = os.getenv('META_ACCESS_TOKEN')
            
            if not self.meta_access_token:
                logger.warning("No Meta access token found")
                return None
            
            return self.meta_access_token
            
        except Exception as e:
            logger.error(f"Error getting Meta access token: {e}")
            return None
    
    async def GOOGLE_ADS_SEARCH(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a Google Ads search query using the REST API.
        
        Parameters:
        - customer_id: string (Google Ads customer ID)
        - query: string (GAQL query)
        - access_token: string (OAuth access token)
        - login_customer_id?: string (Login customer ID, defaults to env variable)
        
        Returns:
        - results: Array of search results
        - total_results: Number of total results
        - next_page_token: Next page token if available
        """
        try:
            customer_id = params.get('customer_id')
            query = params.get('query')
            access_token = params.get('access_token')
            login_customer_id = params.get('login_customer_id', os.getenv('GOOGLE_ADS_LOGIN_CUSTOMER_ID'))
            
            if not all([customer_id, query, access_token]):
                raise ValueError("customer_id, query, and access_token are required")
            
            if not login_customer_id:
                raise ValueError("login_customer_id is required (set GOOGLE_ADS_LOGIN_CUSTOMER_ID in .env)")
            
            # Prepare the request
            url = f"https://googleads.googleapis.com/v21/customers/{customer_id}/googleAds:search"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
                'developer-token': os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN'),
                'login-customer-id': login_customer_id
            }
            
            data = {
                'query': query
            }
            
            # Make the API request
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result_data = response.json()
            
            # Parse the results
            results = result_data.get('results', [])
            total_results = len(results)
            
            # Check for next page token
            next_page_token = result_data.get('nextPageToken')
            
            # Format results for easier consumption
            formatted_results = []
            for result in results:
                formatted_result = self._format_google_ads_result(result)
                formatted_results.append(formatted_result)
            
            return {
                'results': formatted_results,
                'total_results': total_results,
                'next_page_token': next_page_token,
                'success': True
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Google Ads API request error: {str(e)}")
            return {
                'results': [],
                'total_results': 0,
                'next_page_token': None,
                'success': False,
                'error': f"API request failed: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error in GOOGLE_ADS_SEARCH: {str(e)}")
            return {
                'results': [],
                'total_results': 0,
                'next_page_token': None,
                'success': False,
                'error': str(e)
            }
    
    def _format_google_ads_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format a Google Ads search result for easier consumption"""
        formatted = {}
        
        # Extract campaign data
        if 'campaign' in result:
            campaign = result['campaign']
            formatted.update({
                'campaign_id': campaign.get('id'),
                'campaign_name': campaign.get('name'),
                'campaign_status': campaign.get('status'),
                'advertising_channel_type': campaign.get('advertisingChannelType'),
                'start_date': campaign.get('startDate'),
                'end_date': campaign.get('endDate')
            })
        
        # Extract metrics data
        if 'metrics' in result:
            metrics = result['metrics']
            
            # Safely convert to numbers
            impressions = int(metrics.get('impressions', 0)) if metrics.get('impressions') else 0
            clicks = int(metrics.get('clicks', 0)) if metrics.get('clicks') else 0
            conversions = int(metrics.get('conversions', 0)) if metrics.get('conversions') else 0
            cost_micros = int(metrics.get('costMicros', 0)) if metrics.get('costMicros') else 0
            
            formatted.update({
                'impressions': impressions,
                'clicks': clicks,
                'ctr': float(metrics.get('ctr', 0)) if metrics.get('ctr') else 0,
                'conversions': conversions,
                'cost_micros': cost_micros,
                'cost': cost_micros / 1000000 if cost_micros else 0,
                'average_cpc': float(metrics.get('averageCpc', 0)) if metrics.get('averageCpc') else 0,
                'average_cpm': float(metrics.get('averageCpm', 0)) if metrics.get('averageCpm') else 0,
                'conversion_rate': (conversions / clicks) if clicks > 0 else 0
            })
        
        # Extract segments data
        if 'segments' in result:
            segments = result['segments']
            formatted.update({
                'date': segments.get('date'),
                'device': segments.get('device'),
                'network': segments.get('network'),
                'ad_network_type': segments.get('adNetworkType')
            })
        
        # Extract ad group data if present
        if 'adGroup' in result:
            ad_group = result['adGroup']
            formatted.update({
                'ad_group_id': ad_group.get('id'),
                'ad_group_name': ad_group.get('name'),
                'ad_group_status': ad_group.get('status')
            })
        
        # Extract keyword data if present
        if 'keywordView' in result:
            keyword = result['keywordView']
            formatted.update({
                'keyword_id': keyword.get('resourceName'),
                'keyword_text': keyword.get('keywordText'),
                'keyword_match_type': keyword.get('matchType')
            })
        
        return formatted

# Example usage and testing
async def test_get_campaigns():
    """Test function for GET_CAMPAIGNS"""
    tools = MarketingTools()
    
    # Test Google Ads
    google_params = {
        "provider": "google",
        "accountId": "9631603999",  # Replace with actual customer ID
        "fields": ["campaign.id", "campaign.name", "campaign.status", "campaign.start_date"],
        "status": ["ENABLED"],
        "includeMetrics": True,
        "metrics": ["impressions", "clicks", "cost"],
        "limit": 10
    }
    
    print("Testing Google Ads campaigns...")
    google_result = await tools.GET_CAMPAIGNS(google_params)
    print(f"Google result: {json.dumps(google_result, indent=2)}")
    
    # Test Meta
    meta_params = {
        "provider": "meta",
        "accountId": "123456789",  # Replace with actual ad account ID
        "fields": ["id", "name", "status", "start_time"],
        "status": ["ACTIVE"],
        "includeMetrics": True,
        "metrics": ["impressions", "clicks", "spend"],
        "limit": 10
    }
    
    print("\nTesting Meta campaigns...")
    meta_result = await tools.GET_CAMPAIGNS(meta_params)
    print(f"Meta result: {json.dumps(meta_result, indent=2)}")

async def test_google_ads_search():
    """Test function for GOOGLE_ADS_SEARCH"""
    tools = MarketingTools()
    
    # Test Google Ads Search API
    search_params = {
        "customer_id": "3048406696",  # Replace with actual customer ID
        "query": "SELECT campaign.id, campaign.name, campaign.status, metrics.impressions, metrics.clicks, metrics.ctr, metrics.conversions, metrics.cost_micros FROM campaign WHERE segments.date DURING LAST_30_DAYS ORDER BY metrics.impressions DESC",
        "access_token": "ya29.a0AQQ_BDTrAhNSuriWeucHovdKS17oUvrHOIYGm-8dYet6-eNTcdR9hn8yDv_YLncPEfuOcA8Fe0j2FaGdHRt2XYIUdsEVYrxwg2-0-6BwuH0E7FQhMQXPBRQ2gveX4wsgUmuejqLmlJ4eLYclWl1pW-m1BnmXv5sAAgDk3xq49H-uRgGQaw_bsYb3jqfa0Vt5HdrSwMIaCgYKAVQSARISFQHGX2MiY4AbxEZNXKASvwEJx6MUeg0206",  # Replace with actual token
        "login_customer_id": "9762343117"  # Optional, will use env variable if not provided
    }
    
    print("Testing Google Ads Search API...")
    search_result = await tools.GOOGLE_ADS_SEARCH(search_params)
    print(f"Search result: {json.dumps(search_result, indent=2)}")

if __name__ == "__main__":
    # Run tests
    print("=== Testing GET_CAMPAIGNS ===")
    asyncio.run(test_get_campaigns())
    
    print("\n=== Testing GOOGLE_ADS_SEARCH ===")
    asyncio.run(test_google_ads_search())

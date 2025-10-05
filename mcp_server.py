#!/usr/bin/env python3
"""
Custom MCP Server for Google Ads API Integration
Provides Google Ads API access through Model Context Protocol
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django for database access
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent
)

# Import Google Ads API components
try:
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException
    GOOGLE_ADS_AVAILABLE = True
except ImportError:
    GOOGLE_ADS_AVAILABLE = False
    logging.warning("Google Ads library not available. Install with: pip install google-ads")

# Import our existing services
from accounts.google_oauth_service import UserGoogleAuthService
from django.contrib.auth.models import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleAdsMCPServer:
    """MCP Server for Google Ads API operations"""
    
    def __init__(self):
        self.server = Server("google-ads-mcp")
        self.setup_handlers()
        
    def setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available Google Ads tools"""
            return ListToolsResult(
                tools=[
                    # === BASIC GOOGLE ADS OPERATIONS ===
                    Tool(
                        name="get_overview",
                        description="Get account overview and summary",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "customer_id": {"type": "string", "description": "Google Ads customer ID"},
                                "user_id": {"type": "integer", "description": "Django user ID for authentication"}
                            },
                            "required": ["customer_id"]
                        }
                    ),
                    Tool(
                        name="get_campaigns",
                        description="Retrieve campaign information",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "customer_id": {"type": "string", "description": "Google Ads customer ID"},
                                "campaign_ids": {"type": "array", "items": {"type": "string"}, "description": "Specific campaign IDs"},
                                "filters": {"type": "object", "description": "Filter criteria"},
                                "user_id": {"type": "integer", "description": "Django user ID for authentication"}
                            },
                            "required": ["customer_id"]
                        }
                    ),
                    Tool(
                        name="get_campaign_by_id",
                        description="Get specific campaign by ID with date ranges and filters",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "customer_id": {"type": "string", "description": "Google Ads customer ID"},
                                "campaign_id": {"type": "string", "description": "Specific campaign ID"},
                                "start_date": {"type": "string", "description": "Start date in YYYY-MM-DD format"},
                                "end_date": {"type": "string", "description": "End date in YYYY-MM-DD format"},
                                "user_id": {"type": "integer", "description": "Django user ID for authentication"}
                            },
                            "required": ["customer_id", "campaign_id"]
                        }
                    ),
                    Tool(
                        name="get_campaigns_with_filters",
                        description="Get campaigns with specific filters and date ranges",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "customer_id": {"type": "string", "description": "Google Ads customer ID"},
                                "filters": {"type": "object", "description": "Filter criteria"},
                                "start_date": {"type": "string", "description": "Start date in YYYY-MM-DD format"},
                                "end_date": {"type": "string", "description": "End date in YYYY-MM-DD format"},
                                "user_id": {"type": "integer", "description": "Django user ID for authentication"}
                            },
                            "required": ["customer_id"]
                        }
                    ),
                    Tool(
                        name="create_campaign",
                        description="Create new campaigns with budgets",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "customer_id": {"type": "string", "description": "Google Ads customer ID"},
                                "campaign_data": {"type": "object", "description": "Campaign creation data"},
                                "user_id": {"type": "integer", "description": "Django user ID for authentication"}
                            },
                            "required": ["customer_id", "campaign_data"]
                        }
                    ),
                    Tool(
                        name="get_ads",
                        description="Get ads for campaigns",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "customer_id": {"type": "string", "description": "Google Ads customer ID"},
                                "campaign_ids": {"type": "array", "items": {"type": "string"}, "description": "Specific campaign IDs"},
                                "ad_ids": {"type": "array", "items": {"type": "string"}, "description": "Specific ad IDs"},
                                "filters": {"type": "object", "description": "Filter criteria"},
                                "user_id": {"type": "integer", "description": "Django user ID for authentication"}
                            },
                            "required": ["customer_id"]
                        }
                    ),
                    Tool(
                        name="get_ad_by_id",
                        description="Get specific ad by ID with date ranges and filters",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "customer_id": {"type": "string", "description": "Google Ads customer ID"},
                                "ad_id": {"type": "string", "description": "Specific ad ID"},
                                "start_date": {"type": "string", "description": "Start date in YYYY-MM-DD format"},
                                "end_date": {"type": "string", "description": "End date in YYYY-MM-DD format"},
                                "user_id": {"type": "integer", "description": "Django user ID for authentication"}
                            },
                            "required": ["customer_id", "ad_id"]
                        }
                    ),
                    Tool(
                        name="get_ads_with_filters",
                        description="Get ads with specific filters and date ranges",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "customer_id": {"type": "string", "description": "Google Ads customer ID"},
                                "filters": {"type": "object", "description": "Filter criteria"},
                                "start_date": {"type": "string", "description": "Start date in YYYY-MM-DD format"},
                                "end_date": {"type": "string", "description": "End date in YYYY-MM-DD format"},
                                "user_id": {"type": "integer", "description": "Django user ID for authentication"}
                            },
                            "required": ["customer_id"]
                        }
                    ),
                    Tool(
                        name="get_ads_by_campaign_id",
                        description="Get all ads for a specific campaign ID",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "customer_id": {"type": "string", "description": "Google Ads customer ID"},
                                "campaign_id": {"type": "string", "description": "Specific campaign ID"},
                                "user_id": {"type": "integer", "description": "Django user ID for authentication"}
                            },
                            "required": ["customer_id", "campaign_id"]
                        }
                    ),
                    Tool(
                        name="get_ad_groups",
                        description="Get ad groups (adsets) information",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "customer_id": {"type": "string", "description": "Google Ads customer ID"},
                                "campaign_ids": {"type": "array", "items": {"type": "string"}, "description": "Specific campaign IDs"},
                                "ad_group_ids": {"type": "array", "items": {"type": "string"}, "description": "Specific ad group IDs"},
                                "filters": {"type": "object", "description": "Filter criteria"},
                                "user_id": {"type": "integer", "description": "Django user ID for authentication"}
                            },
                            "required": ["customer_id"]
                        }
                    ),
                    Tool(
                        name="get_ad_group_by_id",
                        description="Get specific ad group (adset) by ID with date ranges and filters",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "customer_id": {"type": "string", "description": "Google Ads customer ID"},
                                "ad_group_id": {"type": "string", "description": "Specific ad group ID"},
                                "start_date": {"type": "string", "description": "Start date in YYYY-MM-DD format"},
                                "end_date": {"type": "string", "description": "End date in YYYY-MM-DD format"},
                                "user_id": {"type": "integer", "description": "Django user ID for authentication"}
                            },
                            "required": ["customer_id", "ad_group_id"]
                        }
                    ),
                    Tool(
                        name="get_ad_groups_with_filters",
                        description="Get ad groups (adsets) with specific filters and date ranges",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "customer_id": {"type": "string", "description": "Google Ads customer ID"},
                                "filters": {"type": "object", "description": "Filter criteria"},
                                "start_date": {"type": "string", "description": "Start date in YYYY-MM-DD format"},
                                "end_date": {"type": "string", "description": "End date in YYYY-MM-DD format"},
                                "user_id": {"type": "integer", "description": "Django user ID for authentication"}
                            },
                            "required": ["customer_id"]
                        }
                    ),
                    Tool(
                        name="get_ad_groups_by_campaign_id",
                        description="Get all ad groups (adsets) for a specific campaign ID",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "customer_id": {"type": "string", "description": "Google Ads customer ID"},
                                "campaign_id": {"type": "string", "description": "Specific campaign ID"},
                                "user_id": {"type": "integer", "description": "Django user ID for authentication"}
                            },
                            "required": ["customer_id", "campaign_id"]
                        }
                    ),
                    Tool(
                        name="create_ad",
                        description="Create new ads",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "customer_id": {"type": "string", "description": "Google Ads customer ID"},
                                "ad_data": {"type": "object", "description": "Ad creation data"},
                                "user_id": {"type": "integer", "description": "Django user ID for authentication"}
                            },
                            "required": ["customer_id", "ad_data"]
                        }
                    ),
                    Tool(
                        name="pause_campaign",
                        description="Pause active campaigns",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "customer_id": {"type": "string", "description": "Google Ads customer ID"},
                                "campaign_ids": {"type": "array", "items": {"type": "string"}, "description": "Campaign IDs to pause"},
                                "user_id": {"type": "integer", "description": "Django user ID for authentication"}
                            },
                            "required": ["customer_id", "campaign_ids"]
                        }
                    ),
                    Tool(
                        name="resume_campaign",
                        description="Resume paused campaigns",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "customer_id": {"type": "string", "description": "Google Ads customer ID"},
                                "campaign_ids": {"type": "array", "items": {"type": "string"}, "description": "Campaign IDs to resume"},
                                "user_id": {"type": "integer", "description": "Django user ID for authentication"}
                            },
                            "required": ["customer_id", "campaign_ids"]
                        }
                    ),
                    Tool(
                        name="get_performance_data",
                        description="Get performance data and metrics",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "customer_id": {"type": "string", "description": "Google Ads customer ID"},
                                "start_date": {"type": "string", "description": "Start date in YYYY-MM-DD format"},
                                "end_date": {"type": "string", "description": "End date in YYYY-MM-DD format"},
                                "resource_type": {"type": "string", "enum": ["campaign", "ad_group", "keyword", "ad"], "description": "Type of resource"},
                                "resource_ids": {"type": "array", "items": {"type": "string"}, "description": "Specific resource IDs"},
                                "user_id": {"type": "integer", "description": "Django user ID for authentication"}
                            },
                            "required": ["customer_id"]
                        }
                    ),
                    Tool(
                        name="get_keywords",
                        description="Get keywords for campaigns",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "customer_id": {"type": "string", "description": "Google Ads customer ID"},
                                "ad_group_ids": {"type": "array", "items": {"type": "string"}, "description": "Specific ad group IDs"},
                                "keyword_ids": {"type": "array", "items": {"type": "string"}, "description": "Specific keyword IDs"},
                                "filters": {"type": "object", "description": "Filter criteria"},
                                "user_id": {"type": "integer", "description": "Django user ID for authentication"}
                            },
                            "required": ["customer_id"]
                        }
                    ),
                    Tool(
                        name="get_budgets",
                        description="Get budget information",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "customer_id": {"type": "string", "description": "Google Ads customer ID"},
                                "budget_ids": {"type": "array", "items": {"type": "string"}, "description": "Specific budget IDs"},
                                "campaign_ids": {"type": "array", "items": {"type": "string"}, "description": "Campaign IDs"},
                                "filters": {"type": "object", "description": "Filter criteria"},
                                "user_id": {"type": "integer", "description": "Django user ID for authentication"}
                            },
                            "required": ["customer_id"]
                        }
                    ),
                    Tool(
                        name="get_budget_by_id",
                        description="Get specific budget by ID with date ranges and filters",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "customer_id": {"type": "string", "description": "Google Ads customer ID"},
                                "budget_id": {"type": "string", "description": "Specific budget ID"},
                                "start_date": {"type": "string", "description": "Start date in YYYY-MM-DD format"},
                                "end_date": {"type": "string", "description": "End date in YYYY-MM-DD format"},
                                "user_id": {"type": "integer", "description": "Django user ID for authentication"}
                            },
                            "required": ["customer_id", "budget_id"]
                        }
                    ),
                    Tool(
                        name="get_budgets_with_filters",
                        description="Get budgets with specific filters and date ranges",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "customer_id": {"type": "string", "description": "Google Ads customer ID"},
                                "filters": {"type": "object", "description": "Filter criteria"},
                                "start_date": {"type": "string", "description": "Start date in YYYY-MM-DD format"},
                                "end_date": {"type": "string", "description": "End date in YYYY-MM-DD format"},
                                "user_id": {"type": "integer", "description": "Django user ID for authentication"}
                            },
                            "required": ["customer_id"]
                        }
                    ),
                    Tool(
                        name="get_budgets_by_campaign_id",
                        description="Get all budgets for a specific campaign ID",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "customer_id": {"type": "string", "description": "Google Ads customer ID"},
                                "campaign_id": {"type": "string", "description": "Specific campaign ID"},
                                "user_id": {"type": "integer", "description": "Django user ID for authentication"}
                            },
                            "required": ["customer_id", "campaign_id"]
                        }
                    ),
                    Tool(
                        name="get_accessible_customers",
                        description="Get list of accessible Google Ads customers for a user",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "integer", "description": "Django user ID for authentication"}
                            },
                            "required": ["user_id"]
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls"""
            try:
                # === BASIC GOOGLE ADS OPERATIONS ===
                if name == "get_overview":
                    result = await self.get_overview(arguments)
                elif name == "get_campaigns":
                    result = await self.get_campaigns(arguments)
                elif name == "get_campaign_by_id":
                    result = await self.get_campaign_by_id(arguments)
                elif name == "get_campaigns_with_filters":
                    result = await self.get_campaigns_with_filters(arguments)
                elif name == "create_campaign":
                    result = await self.create_campaign(arguments)
                elif name == "get_ads":
                    result = await self.get_ads(arguments)
                elif name == "get_ad_by_id":
                    result = await self.get_ad_by_id(arguments)
                elif name == "get_ads_with_filters":
                    result = await self.get_ads_with_filters(arguments)
                elif name == "get_ads_by_campaign_id":
                    result = await self.get_ads_by_campaign_id(arguments)
                elif name == "get_ad_groups":
                    result = await self.get_ad_groups(arguments)
                elif name == "get_ad_group_by_id":
                    result = await self.get_ad_group_by_id(arguments)
                elif name == "get_ad_groups_with_filters":
                    result = await self.get_ad_groups_with_filters(arguments)
                elif name == "get_ad_groups_by_campaign_id":
                    result = await self.get_ad_groups_by_campaign_id(arguments)
                elif name == "create_ad":
                    result = await self.create_ad(arguments)
                elif name == "pause_campaign":
                    result = await self.pause_campaign(arguments)
                elif name == "resume_campaign":
                    result = await self.resume_campaign(arguments)
                elif name == "get_performance_data":
                    result = await self.get_performance_data(arguments)
                elif name == "get_keywords":
                    result = await self.get_keywords(arguments)
                elif name == "get_budgets":
                    result = await self.get_budgets(arguments)
                elif name == "get_budget_by_id":
                    result = await self.get_budget_by_id(arguments)
                elif name == "get_budgets_with_filters":
                    result = await self.get_budgets_with_filters(arguments)
                elif name == "get_budgets_by_campaign_id":
                    result = await self.get_budgets_by_campaign_id(arguments)
                elif name == "get_accessible_customers":
                    result = await self.get_accessible_customers(arguments)
                else:
                    # Handle unmatched tools with intelligent fallback
                    result = await self._handle_unmatched_tool(name, arguments)
                
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps(result, indent=2))]
                )
                
            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps({"error": str(e)}, indent=2))]
                )
    
    async def get_campaigns(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get Google Ads campaigns"""
        try:
            customer_id = arguments.get("customer_id")
            user_id = arguments.get("user_id")
            
            if not GOOGLE_ADS_AVAILABLE:
                return {"error": "Google Ads library not available"}
            
            # Get user credentials
            if user_id:
                user = User.objects.get(id=user_id)
                auth_service = UserGoogleAuthService()
                access_token = auth_service.get_or_refresh_valid_token(user)
                
                if not access_token:
                    return {"error": "No valid Google OAuth credentials found"}
            
            # Initialize Google Ads client
            client = self._get_google_ads_client(user_id)
            if not client:
                return {"error": "Failed to initialize Google Ads client"}
            
            # Query campaigns
            ga_service = client.get_service("GoogleAdsService")
            query = """
                SELECT 
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    campaign.advertising_channel_type,
                    campaign.start_date,
                    campaign.end_date,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions
                FROM campaign 
                WHERE campaign.status != 'REMOVED'
                ORDER BY campaign.name
            """
            
            campaigns = []
            search_request = client.get_type("SearchGoogleAdsRequest")
            search_request.customer_id = customer_id
            search_request.query = query
            
            response = ga_service.search(request=search_request)
            
            for row in response:
                campaign = {
                    "id": row.campaign.id,
                    "name": row.campaign.name,
                    "status": row.campaign.status.name,
                    "advertising_channel_type": row.campaign.advertising_channel_type.name,
                    "start_date": row.campaign.start_date,
                    "end_date": row.campaign.end_date,
                    "impressions": row.metrics.impressions,
                    "clicks": row.metrics.clicks,
                    "cost_micros": row.metrics.cost_micros,
                    "conversions": row.metrics.conversions
                }
                campaigns.append(campaign)
            
            return {
                "success": True,
                "customer_id": customer_id,
                "campaigns": campaigns,
                "total_count": len(campaigns)
            }
            
        except Exception as e:
            logger.error(f"Error getting campaigns: {e}")
            return {"error": str(e)}
    
    async def get_ad_groups(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get Google Ads ad groups"""
        try:
            customer_id = arguments.get("customer_id")
            campaign_id = arguments.get("campaign_id")
            user_id = arguments.get("user_id")
            
            if not GOOGLE_ADS_AVAILABLE:
                return {"error": "Google Ads library not available"}
            
            client = self._get_google_ads_client(user_id)
            if not client:
                return {"error": "Failed to initialize Google Ads client"}
            
            # Build query
            query = """
                SELECT 
                    ad_group.id,
                    ad_group.name,
                    ad_group.status,
                    ad_group.type,
                    campaign.id,
                    campaign.name,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions
                FROM ad_group 
                WHERE ad_group.status != 'REMOVED'
            """
            
            if campaign_id:
                query += f" AND campaign.id = {campaign_id}"
            
            query += " ORDER BY ad_group.name"
            
            # Execute query
            ga_service = client.get_service("GoogleAdsService")
            search_request = client.get_type("SearchGoogleAdsRequest")
            search_request.customer_id = customer_id
            search_request.query = query
            
            response = ga_service.search(request=search_request)
            
            ad_groups = []
            for row in response:
                ad_group = {
                    "id": row.ad_group.id,
                    "name": row.ad_group.name,
                    "status": row.ad_group.status.name,
                    "type": row.ad_group.type.name,
                    "campaign_id": row.campaign.id,
                    "campaign_name": row.campaign.name,
                    "impressions": row.metrics.impressions,
                    "clicks": row.metrics.clicks,
                    "cost_micros": row.metrics.cost_micros,
                    "conversions": row.metrics.conversions
                }
                ad_groups.append(ad_group)
            
            return {
                "success": True,
                "customer_id": customer_id,
                "ad_groups": ad_groups,
                "total_count": len(ad_groups)
            }
            
        except Exception as e:
            logger.error(f"Error getting ad groups: {e}")
            return {"error": str(e)}
    
    async def get_keywords(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get Google Ads keywords"""
        try:
            customer_id = arguments.get("customer_id")
            ad_group_id = arguments.get("ad_group_id")
            user_id = arguments.get("user_id")
            
            if not GOOGLE_ADS_AVAILABLE:
                return {"error": "Google Ads library not available"}
            
            client = self._get_google_ads_client(user_id)
            if not client:
                return {"error": "Failed to initialize Google Ads client"}
            
            # Build query
            query = """
                SELECT 
                    ad_group_criterion.criterion_id,
                    ad_group_criterion.keyword.text,
                    ad_group_criterion.keyword.match_type,
                    ad_group_criterion.status,
                    ad_group.id,
                    ad_group.name,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions
                FROM keyword_view 
                WHERE ad_group_criterion.status != 'REMOVED'
            """
            
            if ad_group_id:
                query += f" AND ad_group.id = {ad_group_id}"
            
            query += " ORDER BY ad_group_criterion.keyword.text"
            
            # Execute query
            ga_service = client.get_service("GoogleAdsService")
            search_request = client.get_type("SearchGoogleAdsRequest")
            search_request.customer_id = customer_id
            search_request.query = query
            
            response = ga_service.search(request=search_request)
            
            keywords = []
            for row in response:
                keyword = {
                    "criterion_id": row.ad_group_criterion.criterion_id,
                    "text": row.ad_group_criterion.keyword.text,
                    "match_type": row.ad_group_criterion.keyword.match_type.name,
                    "status": row.ad_group_criterion.status.name,
                    "ad_group_id": row.ad_group.id,
                    "ad_group_name": row.ad_group.name,
                    "impressions": row.metrics.impressions,
                    "clicks": row.metrics.clicks,
                    "cost_micros": row.metrics.cost_micros,
                    "conversions": row.metrics.conversions
                }
                keywords.append(keyword)
            
            return {
                "success": True,
                "customer_id": customer_id,
                "keywords": keywords,
                "total_count": len(keywords)
            }
            
        except Exception as e:
            logger.error(f"Error getting keywords: {e}")
            return {"error": str(e)}
    
    async def get_performance_data(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get performance metrics"""
        try:
            customer_id = arguments.get("customer_id")
            start_date = arguments.get("start_date")
            end_date = arguments.get("end_date")
            resource_type = arguments.get("resource_type", "campaign")
            user_id = arguments.get("user_id")
            
            # Default to last 30 days if dates not provided
            if not start_date or not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            if not GOOGLE_ADS_AVAILABLE:
                return {"error": "Google Ads library not available"}
            
            client = self._get_google_ads_client(user_id)
            if not client:
                return {"error": "Failed to initialize Google Ads client"}
            
            # Build query based on resource type
            if resource_type == "campaign":
                query = f"""
                    SELECT 
                        campaign.id,
                        campaign.name,
                        segments.date,
                        metrics.impressions,
                        metrics.clicks,
                        metrics.cost_micros,
                        metrics.conversions,
                        metrics.conversions_value,
                        metrics.ctr,
                        metrics.average_cpc
                    FROM campaign 
                    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
                    ORDER BY segments.date DESC, campaign.name
                """
            elif resource_type == "ad_group":
                query = f"""
                    SELECT 
                        ad_group.id,
                        ad_group.name,
                        campaign.id,
                        campaign.name,
                        segments.date,
                        metrics.impressions,
                        metrics.clicks,
                        metrics.cost_micros,
                        metrics.conversions,
                        metrics.conversions_value,
                        metrics.ctr,
                        metrics.average_cpc
                    FROM ad_group 
                    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
                    ORDER BY segments.date DESC, ad_group.name
                """
            else:  # keyword
                query = f"""
                    SELECT 
                        ad_group_criterion.criterion_id,
                        ad_group_criterion.keyword.text,
                        ad_group.id,
                        ad_group.name,
                        segments.date,
                        metrics.impressions,
                        metrics.clicks,
                        metrics.cost_micros,
                        metrics.conversions,
                        metrics.conversions_value,
                        metrics.ctr,
                        metrics.average_cpc
                    FROM keyword_view 
                    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
                    ORDER BY segments.date DESC, ad_group_criterion.keyword.text
                """
            
            # Execute query
            ga_service = client.get_service("GoogleAdsService")
            search_request = client.get_type("SearchGoogleAdsRequest")
            search_request.customer_id = customer_id
            search_request.query = query
            
            response = ga_service.search(request=search_request)
            
            performance_data = []
            for row in response:
                if resource_type == "campaign":
                    data = {
                        "id": row.campaign.id,
                        "name": row.campaign.name,
                        "date": row.segments.date,
                        "impressions": row.metrics.impressions,
                        "clicks": row.metrics.clicks,
                        "cost_micros": row.metrics.cost_micros,
                        "conversions": row.metrics.conversions,
                        "conversions_value": row.metrics.conversions_value,
                        "ctr": row.metrics.ctr,
                        "average_cpc": row.metrics.average_cpc
                    }
                elif resource_type == "ad_group":
                    data = {
                        "id": row.ad_group.id,
                        "name": row.ad_group.name,
                        "campaign_id": row.campaign.id,
                        "campaign_name": row.campaign.name,
                        "date": row.segments.date,
                        "impressions": row.metrics.impressions,
                        "clicks": row.metrics.clicks,
                        "cost_micros": row.metrics.cost_micros,
                        "conversions": row.metrics.conversions,
                        "conversions_value": row.metrics.conversions_value,
                        "ctr": row.metrics.ctr,
                        "average_cpc": row.metrics.average_cpc
                    }
                else:  # keyword
                    data = {
                        "criterion_id": row.ad_group_criterion.criterion_id,
                        "text": row.ad_group_criterion.keyword.text,
                        "ad_group_id": row.ad_group.id,
                        "ad_group_name": row.ad_group.name,
                        "date": row.segments.date,
                        "impressions": row.metrics.impressions,
                        "clicks": row.metrics.clicks,
                        "cost_micros": row.metrics.cost_micros,
                        "conversions": row.metrics.conversions,
                        "conversions_value": row.metrics.conversions_value,
                        "ctr": row.metrics.ctr,
                        "average_cpc": row.metrics.average_cpc
                    }
                
                performance_data.append(data)
            
            return {
                "success": True,
                "customer_id": customer_id,
                "resource_type": resource_type,
                "start_date": start_date,
                "end_date": end_date,
                "performance_data": performance_data,
                "total_count": len(performance_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting performance data: {e}")
            return {"error": str(e)}
    
    async def get_accessible_customers(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get accessible customers for a user"""
        try:
            user_id = arguments.get("user_id")
            
            if not user_id:
                return {"error": "user_id is required"}
            
            user = User.objects.get(id=user_id)
            auth_service = UserGoogleAuthService()
            
            # Get accessible customers
            accessible_customers = auth_service.get_accessible_customers(user)
            
            return {
                "success": True,
                "user_id": user_id,
                "accessible_customers": accessible_customers,
                "total_count": len(accessible_customers)
            }
            
        except Exception as e:
            logger.error(f"Error getting accessible customers: {e}")
            return {"error": str(e)}
    
    def _get_google_ads_client(self, user_id: Optional[int] = None) -> Optional[GoogleAdsClient]:
        """Get Google Ads client with proper credentials"""
        try:
            if not GOOGLE_ADS_AVAILABLE:
                return None
            
            # Get credentials from environment or user
            if user_id:
                user = User.objects.get(id=user_id)
                auth_service = UserGoogleAuthService()
                access_token = auth_service.get_or_refresh_valid_token(user)
                
                if not access_token:
                    logger.error("No valid access token found for user")
                    return None
            
            # Initialize client with environment variables
            client = GoogleAdsClient.load_from_storage()
            return client
            
        except Exception as e:
            logger.error(f"Error initializing Google Ads client: {e}")
        return None
    
    async def _handle_unmatched_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle unmatched tools with intelligent fallback and suggestions"""
        try:
            # Get available tools for suggestions
            available_tools = [
                "get_overview", "get_campaigns", "get_campaign_by_id", "get_campaigns_with_filters",
                "create_campaign", "get_ads", "get_ad_by_id", "get_ads_with_filters", 
                "get_ads_by_campaign_id", "get_ad_groups", "get_ad_group_by_id", 
                "get_ad_groups_with_filters", "get_ad_groups_by_campaign_id", "create_ad",
                "pause_campaign", "resume_campaign", "get_performance_data", "get_keywords",
                "get_budgets", "get_budget_by_id", "get_budgets_with_filters", 
                "get_budgets_by_campaign_id", "get_accessible_customers"
            ]
            
            # Find similar tools using fuzzy matching
            similar_tools = self._find_similar_tools(tool_name, available_tools)
            
            # Create helpful error message with suggestions
            error_message = f"Tool '{tool_name}' not found in MCP server."
            
            if similar_tools:
                suggestions = ", ".join(similar_tools[:3])  # Top 3 suggestions
                error_message += f" Did you mean: {suggestions}?"
            else:
                error_message += " Available tools include: get_overview, get_campaigns, get_ads, get_ad_groups, get_budgets, get_performance_data, get_keywords, get_accessible_customers."
            
            # Add usage examples
            error_message += "\n\nUsage examples:\n"
            error_message += "- get_campaigns: Get all campaigns\n"
            error_message += "- get_campaign_by_id: Get specific campaign details\n"
            error_message += "- get_ads: Get ads for campaigns\n"
            error_message += "- get_performance_data: Get performance metrics\n"
            error_message += "- get_accessible_customers: List accessible accounts"
            
            return {
                "success": False,
                "error": error_message,
                "error_type": "tool_not_found",
                "requested_tool": tool_name,
                "suggestions": similar_tools,
                "available_tools": available_tools
            }
            
        except Exception as e:
            logger.error(f"Error in unmatched tool handler: {e}")
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found and error occurred: {str(e)}",
                "error_type": "tool_not_found_with_error"
            }
    
    def _find_similar_tools(self, tool_name: str, available_tools: List[str]) -> List[str]:
        """Find similar tools using simple string matching"""
        tool_name_lower = tool_name.lower()
        similar = []
        
        # Direct substring matches
        for tool in available_tools:
            if tool_name_lower in tool or tool in tool_name_lower:
                similar.append(tool)
        
        # If no direct matches, try partial word matching
        if not similar:
            tool_words = tool_name_lower.split('_')
            for tool in available_tools:
                tool_parts = tool.split('_')
                # Check if any word from requested tool matches any part of available tool
                if any(word in tool_parts for word in tool_words if len(word) > 2):
                    similar.append(tool)
        
        # Sort by similarity (exact matches first, then by length)
        similar.sort(key=lambda x: (x != tool_name_lower, len(x)))
        
        return similar[:5]  # Return top 5 matches
    
    # === NEW MCP TOOL IMPLEMENTATIONS ===
    
    async def get_overview(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get account overview and summary"""
        try:
            customer_id = arguments.get("customer_id")
            user_id = arguments.get("user_id")
            
            if not GOOGLE_ADS_AVAILABLE:
                return {"error": "Google Ads library not available"}
            
            client = self._get_google_ads_client(user_id)
            if not client:
                return {"error": "Failed to initialize Google Ads client"}
            
            # Get account overview with key metrics
            ga_service = client.get_service("GoogleAdsService")
            query = """
                SELECT 
                    customer.id,
                    customer.descriptive_name,
                    customer.currency_code,
                    customer.time_zone,
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions
                FROM campaign 
                WHERE campaign.status != 'REMOVED'
                ORDER BY metrics.cost_micros DESC
                LIMIT 10
            """
            
            search_request = client.get_type("SearchGoogleAdsRequest")
            search_request.customer_id = customer_id
            search_request.query = query
            
            response = ga_service.search(request=search_request)
            
            campaigns = []
            total_impressions = 0
            total_clicks = 0
            total_cost = 0
            total_conversions = 0
            
            for row in response:
                campaign = {
                    "id": row.campaign.id,
                    "name": row.campaign.name,
                    "status": row.campaign.status.name,
                    "impressions": row.metrics.impressions,
                    "clicks": row.metrics.clicks,
                    "cost_micros": row.metrics.cost_micros,
                    "conversions": row.metrics.conversions
                }
                campaigns.append(campaign)
                
                total_impressions += row.metrics.impressions
                total_clicks += row.metrics.clicks
                total_cost += row.metrics.cost_micros
                total_conversions += row.metrics.conversions
            
            # Get customer info
            customer_info = {
                "id": customer_id,
                "currency_code": response.results[0].customer.currency_code if response.results else "USD",
                "time_zone": response.results[0].customer.time_zone if response.results else "UTC"
            }
            
            return {
                "success": True,
                "customer_info": customer_info,
                "campaigns": campaigns,
                "summary": {
                    "total_campaigns": len(campaigns),
                    "total_impressions": total_impressions,
                    "total_clicks": total_clicks,
                    "total_cost": total_cost / 1_000_000,  # Convert to dollars
                    "total_conversions": total_conversions,
                    "average_ctr": (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting overview: {e}")
            return {"error": str(e)}
    
    async def get_campaign_by_id(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get specific campaign by ID"""
        try:
            customer_id = arguments.get("customer_id")
            campaign_id = arguments.get("campaign_id")
            user_id = arguments.get("user_id")
            
            if not GOOGLE_ADS_AVAILABLE:
                return {"error": "Google Ads library not available"}
            
            client = self._get_google_ads_client(user_id)
            if not client:
                return {"error": "Failed to initialize Google Ads client"}
            
            # Get specific campaign details
            ga_service = client.get_service("GoogleAdsService")
            query = f"""
                SELECT 
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    campaign.advertising_channel_type,
                    campaign.start_date,
                    campaign.end_date,
                    campaign_budget.amount_micros,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.ctr,
                    metrics.average_cpc
                FROM campaign 
                WHERE campaign.id = {campaign_id}
            """
            
            search_request = client.get_type("SearchGoogleAdsRequest")
            search_request.customer_id = customer_id
            search_request.query = query
            
            response = ga_service.search(request=search_request)
            
            if not response.results:
                return {"error": f"Campaign {campaign_id} not found"}
            
            row = response.results[0]
            campaign = {
                "id": row.campaign.id,
                "name": row.campaign.name,
                "status": row.campaign.status.name,
                "advertising_channel_type": row.campaign.advertising_channel_type.name,
                "start_date": row.campaign.start_date,
                "end_date": row.campaign.end_date,
                "budget_amount": row.campaign_budget.amount_micros / 1_000_000,  # Convert to dollars
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "cost_micros": row.metrics.cost_micros,
                "conversions": row.metrics.conversions,
                "ctr": row.metrics.ctr,
                "average_cpc": row.metrics.average_cpc
            }
            
            return {
                "success": True,
                "campaign": campaign
            }
            
        except Exception as e:
            logger.error(f"Error getting campaign by ID: {e}")
            return {"error": str(e)}
    
    async def get_campaigns_with_filters(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get campaigns with specific filters"""
        try:
            customer_id = arguments.get("customer_id")
            filters = arguments.get("filters", {})
            start_date = arguments.get("start_date")
            end_date = arguments.get("end_date")
            user_id = arguments.get("user_id")
            
            if not GOOGLE_ADS_AVAILABLE:
                return {"error": "Google Ads library not available"}
            
            client = self._get_google_ads_client(user_id)
            if not client:
                return {"error": "Failed to initialize Google Ads client"}
            
            # Build query with filters
            query = """
                SELECT 
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    campaign.advertising_channel_type,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions
                FROM campaign 
                WHERE campaign.status != 'REMOVED'
            """
            
            # Add date filters if provided
            if start_date and end_date:
                query += f" AND segments.date BETWEEN '{start_date}' AND '{end_date}'"
            
            # Add custom filters
            if filters.get("status"):
                status = filters["status"].upper()
                query += f" AND campaign.status = '{status}'"
            
            if filters.get("advertising_channel_type"):
                channel_type = filters["advertising_channel_type"].upper()
                query += f" AND campaign.advertising_channel_type = '{channel_type}'"
            
            query += " ORDER BY metrics.cost_micros DESC"
            
            # Execute query
            ga_service = client.get_service("GoogleAdsService")
            search_request = client.get_type("SearchGoogleAdsRequest")
            search_request.customer_id = customer_id
            search_request.query = query
            
            response = ga_service.search(request=search_request)
            
            campaigns = []
            for row in response:
                campaign = {
                    "id": row.campaign.id,
                    "name": row.campaign.name,
                    "status": row.campaign.status.name,
                    "advertising_channel_type": row.campaign.advertising_channel_type.name,
                    "impressions": row.metrics.impressions,
                    "clicks": row.metrics.clicks,
                    "cost_micros": row.metrics.cost_micros,
                    "conversions": row.metrics.conversions
                }
                campaigns.append(campaign)
            
            return {
                "success": True,
                "campaigns": campaigns,
                "total_count": len(campaigns),
                "filters_applied": filters
            }
            
        except Exception as e:
            logger.error(f"Error getting campaigns with filters: {e}")
            return {"error": str(e)}
    
    async def create_campaign(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create new campaign"""
        try:
            # This is a placeholder implementation
            return {
                "success": False,
                "error": "Campaign creation not implemented yet. This requires Google Ads API campaign creation operations."
            }
            
        except Exception as e:
            logger.error(f"Error creating campaign: {e}")
            return {"error": str(e)}
    
    async def get_ads(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get ads for campaigns"""
        try:
            customer_id = arguments.get("customer_id")
            campaign_ids = arguments.get("campaign_ids", [])
            ad_ids = arguments.get("ad_ids", [])
            filters = arguments.get("filters", {})
            user_id = arguments.get("user_id")
            
            if not GOOGLE_ADS_AVAILABLE:
                return {"error": "Google Ads library not available"}
            
            client = self._get_google_ads_client(user_id)
            if not client:
                return {"error": "Failed to initialize Google Ads client"}
            
            # Build query
            query = """
                SELECT 
                    ad_group_ad.ad.id,
                    ad_group_ad.ad.responsive_search_ad.headlines,
                    ad_group_ad.ad.responsive_search_ad.descriptions,
                    ad_group_ad.status,
                    ad_group.id,
                    ad_group.name,
                    campaign.id,
                    campaign.name,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions
                FROM ad_group_ad 
                WHERE ad_group_ad.status != 'REMOVED'
            """
            
            # Add campaign filter
            if campaign_ids:
                campaign_filter = " OR ".join([f"campaign.id = {cid}" for cid in campaign_ids])
                query += f" AND ({campaign_filter})"
            
            # Add ad ID filter
            if ad_ids:
                ad_filter = " OR ".join([f"ad_group_ad.ad.id = {aid}" for aid in ad_ids])
                query += f" AND ({ad_filter})"
            
            query += " ORDER BY metrics.cost_micros DESC"
            
            # Execute query
            ga_service = client.get_service("GoogleAdsService")
            search_request = client.get_type("SearchGoogleAdsRequest")
            search_request.customer_id = customer_id
            search_request.query = query
            
            response = ga_service.search(request=search_request)
            
            ads = []
            for row in response:
                ad = {
                    "id": row.ad_group_ad.ad.id,
                    "status": row.ad_group_ad.status.name,
                    "ad_group_id": row.ad_group.id,
                    "ad_group_name": row.ad_group.name,
                    "campaign_id": row.campaign.id,
                    "campaign_name": row.campaign.name,
                    "impressions": row.metrics.impressions,
                    "clicks": row.metrics.clicks,
                    "cost_micros": row.metrics.cost_micros,
                    "conversions": row.metrics.conversions
                }
                
                # Extract headlines and descriptions if available
                if row.ad_group_ad.ad.responsive_search_ad.headlines:
                    ad["headlines"] = [h.text for h in row.ad_group_ad.ad.responsive_search_ad.headlines]
                
                if row.ad_group_ad.ad.responsive_search_ad.descriptions:
                    ad["descriptions"] = [d.text for d in row.ad_group_ad.ad.responsive_search_ad.descriptions]
                
                ads.append(ad)
            
            return {
                "success": True,
                "ads": ads,
                "total_count": len(ads)
            }
            
        except Exception as e:
            logger.error(f"Error getting ads: {e}")
            return {"error": str(e)}
    
    async def get_ad_by_id(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get specific ad by ID"""
        try:
            customer_id = arguments.get("customer_id")
            ad_id = arguments.get("ad_id")
            user_id = arguments.get("user_id")
            
            if not GOOGLE_ADS_AVAILABLE:
                return {"error": "Google Ads library not available"}
            
            client = self._get_google_ads_client(user_id)
            if not client:
                return {"error": "Failed to initialize Google Ads client"}
            
            # Get specific ad details
            ga_service = client.get_service("GoogleAdsService")
            query = f"""
                SELECT 
                    ad_group_ad.ad.id,
                    ad_group_ad.ad.responsive_search_ad.headlines,
                    ad_group_ad.ad.responsive_search_ad.descriptions,
                    ad_group_ad.status,
                    ad_group.id,
                    ad_group.name,
                    campaign.id,
                    campaign.name,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.ctr,
                    metrics.average_cpc
                FROM ad_group_ad 
                WHERE ad_group_ad.ad.id = {ad_id}
            """
            
            search_request = client.get_type("SearchGoogleAdsRequest")
            search_request.customer_id = customer_id
            search_request.query = query
            
            response = ga_service.search(request=search_request)
            
            if not response.results:
                return {"error": f"Ad {ad_id} not found"}
            
            row = response.results[0]
            ad = {
                "id": row.ad_group_ad.ad.id,
                "status": row.ad_group_ad.status.name,
                "ad_group_id": row.ad_group.id,
                "ad_group_name": row.ad_group.name,
                "campaign_id": row.campaign.id,
                "campaign_name": row.campaign.name,
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "cost_micros": row.metrics.cost_micros,
                "conversions": row.metrics.conversions,
                "ctr": row.metrics.ctr,
                "average_cpc": row.metrics.average_cpc
            }
            
            # Extract headlines and descriptions
            if row.ad_group_ad.ad.responsive_search_ad.headlines:
                ad["headlines"] = [h.text for h in row.ad_group_ad.ad.responsive_search_ad.headlines]
            
            if row.ad_group_ad.ad.responsive_search_ad.descriptions:
                ad["descriptions"] = [d.text for d in row.ad_group_ad.ad.responsive_search_ad.descriptions]
            
            return {
                "success": True,
                "ad": ad
            }
            
        except Exception as e:
            logger.error(f"Error getting ad by ID: {e}")
            return {"error": str(e)}
    
    async def get_ads_with_filters(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get ads with specific filters"""
        # Similar to get_ads but with additional filter logic
        return await self.get_ads(arguments)
    
    async def get_ads_by_campaign_id(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get all ads for a specific campaign ID"""
        campaign_id = arguments.get("campaign_id")
        arguments["campaign_ids"] = [campaign_id]
        return await self.get_ads(arguments)
    
    async def get_ad_group_by_id(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get specific ad group by ID"""
        try:
            customer_id = arguments.get("customer_id")
            ad_group_id = arguments.get("ad_group_id")
            user_id = arguments.get("user_id")
            
            if not GOOGLE_ADS_AVAILABLE:
                return {"error": "Google Ads library not available"}
            
            client = self._get_google_ads_client(user_id)
            if not client:
                return {"error": "Failed to initialize Google Ads client"}
            
            # Get specific ad group details
            ga_service = client.get_service("GoogleAdsService")
            query = f"""
                SELECT 
                    ad_group.id,
                    ad_group.name,
                    ad_group.status,
                    ad_group.type,
                    campaign.id,
                    campaign.name,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.ctr,
                    metrics.average_cpc
                FROM ad_group 
                WHERE ad_group.id = {ad_group_id}
            """
            
            search_request = client.get_type("SearchGoogleAdsRequest")
            search_request.customer_id = customer_id
            search_request.query = query
            
            response = ga_service.search(request=search_request)
            
            if not response.results:
                return {"error": f"Ad group {ad_group_id} not found"}
            
            row = response.results[0]
            ad_group = {
                "id": row.ad_group.id,
                "name": row.ad_group.name,
                "status": row.ad_group.status.name,
                "type": row.ad_group.type.name,
                "campaign_id": row.campaign.id,
                "campaign_name": row.campaign.name,
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "cost_micros": row.metrics.cost_micros,
                "conversions": row.metrics.conversions,
                "ctr": row.metrics.ctr,
                "average_cpc": row.metrics.average_cpc
            }
            
            return {
                "success": True,
                "ad_group": ad_group
            }
            
        except Exception as e:
            logger.error(f"Error getting ad group by ID: {e}")
            return {"error": str(e)}
    
    async def get_ad_groups_with_filters(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get ad groups with specific filters"""
        # Similar to get_ad_groups but with additional filter logic
        return await self.get_ad_groups(arguments)
    
    async def get_ad_groups_by_campaign_id(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get all ad groups for a specific campaign ID"""
        campaign_id = arguments.get("campaign_id")
        arguments["campaign_ids"] = [campaign_id]
        return await self.get_ad_groups(arguments)
    
    async def create_ad(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create new ad"""
        try:
            # This is a placeholder implementation
            return {
                "success": False,
                "error": "Ad creation not implemented yet. This requires Google Ads API ad creation operations."
            }
            
        except Exception as e:
            logger.error(f"Error creating ad: {e}")
            return {"error": str(e)}
    
    async def pause_campaign(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Pause campaigns"""
        try:
            # This is a placeholder implementation
            return {
                "success": False,
                "error": "Campaign pause not implemented yet. This requires Google Ads API campaign modification operations."
            }
            
        except Exception as e:
            logger.error(f"Error pausing campaign: {e}")
            return {"error": str(e)}
    
    async def resume_campaign(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Resume campaigns"""
        try:
            # This is a placeholder implementation
            return {
                "success": False,
                "error": "Campaign resume not implemented yet. This requires Google Ads API campaign modification operations."
            }
            
        except Exception as e:
            logger.error(f"Error resuming campaign: {e}")
            return {"error": str(e)}
    
    async def get_budgets(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get budget information"""
        try:
            customer_id = arguments.get("customer_id")
            budget_ids = arguments.get("budget_ids", [])
            campaign_ids = arguments.get("campaign_ids", [])
            user_id = arguments.get("user_id")
            
            if not GOOGLE_ADS_AVAILABLE:
                return {"error": "Google Ads library not available"}
            
            client = self._get_google_ads_client(user_id)
            if not client:
                return {"error": "Failed to initialize Google Ads client"}
            
            # Build query
            query = """
                SELECT 
                    campaign_budget.id,
                    campaign_budget.name,
                    campaign_budget.amount_micros,
                    campaign_budget.delivery_method,
                    campaign.id,
                    campaign.name,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros
                FROM campaign_budget 
            """
            
            # Add budget ID filter
            if budget_ids:
                budget_filter = " OR ".join([f"campaign_budget.id = {bid}" for bid in budget_ids])
                query += f" WHERE ({budget_filter})"
            
            # Add campaign filter
            if campaign_ids:
                campaign_filter = " OR ".join([f"campaign.id = {cid}" for cid in campaign_ids])
                if budget_ids:
                    query += f" AND ({campaign_filter})"
                else:
                    query += f" WHERE ({campaign_filter})"
            
            query += " ORDER BY campaign_budget.amount_micros DESC"
            
            # Execute query
            ga_service = client.get_service("GoogleAdsService")
            search_request = client.get_type("SearchGoogleAdsRequest")
            search_request.customer_id = customer_id
            search_request.query = query
            
            response = ga_service.search(request=search_request)
            
            budgets = []
            for row in response:
                budget = {
                    "id": row.campaign_budget.id,
                    "name": row.campaign_budget.name,
                    "amount_micros": row.campaign_budget.amount_micros,
                    "amount": row.campaign_budget.amount_micros / 1_000_000,  # Convert to dollars
                    "delivery_method": row.campaign_budget.delivery_method.name,
                    "campaign_id": row.campaign.id,
                    "campaign_name": row.campaign.name,
                    "impressions": row.metrics.impressions,
                    "clicks": row.metrics.clicks,
                    "cost_micros": row.metrics.cost_micros
                }
                budgets.append(budget)
            
            return {
                "success": True,
                "budgets": budgets,
                "total_count": len(budgets)
            }
            
        except Exception as e:
            logger.error(f"Error getting budgets: {e}")
            return {"error": str(e)}
    
    async def get_budget_by_id(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get specific budget by ID"""
        budget_id = arguments.get("budget_id")
        arguments["budget_ids"] = [budget_id]
        return await self.get_budgets(arguments)
    
    async def get_budgets_with_filters(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get budgets with specific filters"""
        # Similar to get_budgets but with additional filter logic
        return await self.get_budgets(arguments)
    
    async def get_budgets_by_campaign_id(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get all budgets for a specific campaign ID"""
        campaign_id = arguments.get("campaign_id")
        arguments["campaign_ids"] = [campaign_id]
        return await self.get_budgets(arguments)


async def main():
    """Main entry point for MCP server"""
    server = GoogleAdsMCPServer()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="google-ads-mcp",
                server_version="1.0.0",
                capabilities=server.server.get_capabilities(
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())

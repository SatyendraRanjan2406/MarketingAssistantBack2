"""
MCP Client for Google Ads API Integration
Handles communication with MCP server for Google Ads operations
"""

import asyncio
import json
import logging
import subprocess
import tempfile
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class GoogleAdsMCPClient:
    """MCP Client for Google Ads API operations"""
    
    def __init__(self):
        self.server_process = None
        self.load_mcp_config()
    
    def load_mcp_config(self):
        """Load MCP configuration from mcp.json"""
        try:
            import json
            with open('/Users/satyendra/marketing_assistant_back/mcp.json', 'r') as f:
                config = json.load(f)
            
            # Use the google-ads-custom server configuration
            self.server_config = config["mcpServers"]["google-ads-custom"]
            
            # Replace environment variable placeholders with actual values
            env = {}
            for key, value in self.server_config["env"].items():
                if value.startswith("${") and value.endswith("}"):
                    env_var = value[2:-1]  # Remove ${ and }
                    env[key] = os.getenv(env_var, "")
                else:
                    env[key] = value
            
            self.server_config["env"] = env
            
        except Exception as e:
            logger.error(f"Error loading mcp.json: {e}")
            # Fallback to default configuration
            self.server_config = {
                "command": "python",
                "args": ["mcp_server.py"],
                "cwd": "/Users/satyendra/marketing_assistant_back",
                "env": {
                    "GOOGLE_ADS_DEVELOPER_TOKEN": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN", ""),
                    "GOOGLE_ADS_CLIENT_ID": os.getenv("GOOGLE_ADS_CLIENT_ID", ""),
                    "GOOGLE_ADS_CLIENT_SECRET": os.getenv("GOOGLE_ADS_CLIENT_SECRET", ""),
                    "GOOGLE_ADS_REFRESH_TOKEN": os.getenv("GOOGLE_ADS_REFRESH_TOKEN", ""),
                    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", "")
                }
            }
    
    async def start_server(self):
        """Start the MCP server"""
        try:
            if self.server_process and self.server_process.poll() is None:
                logger.info("MCP server already running")
                return True
            
            # Start the MCP server using configuration from mcp.json
            env = os.environ.copy()
            env.update(self.server_config["env"])
            
            self.server_process = subprocess.Popen(
                [self.server_config["command"]] + self.server_config["args"],
                cwd=self.server_config["cwd"],
                env=env,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            logger.info("MCP server started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error starting MCP server: {e}")
            return False
    
    async def stop_server(self):
        """Stop the MCP server"""
        try:
            if self.server_process:
                self.server_process.terminate()
                self.server_process.wait()
                self.server_process = None
                logger.info("MCP server stopped")
        except Exception as e:
            logger.error(f"Error stopping MCP server: {e}")
    
    async def initialize_server(self):
        """Initialize the MCP server with proper handshake"""
        try:
            if not self.server_process or self.server_process.poll() is not None:
                await self.start_server()
            
            # Send initialization request
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "roots": {
                            "listChanged": True
                        },
                        "sampling": {}
                    },
                    "clientInfo": {
                        "name": "google-ads-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            # Send initialization request
            init_json = json.dumps(init_request) + "\n"
            self.server_process.stdin.write(init_json)
            self.server_process.stdin.flush()
            
            # Read initialization response
            init_response_line = self.server_process.stdout.readline()
            if init_response_line:
                init_response = json.loads(init_response_line.strip())
                logger.info(f"MCP server initialized: {init_response}")
                
                # Send initialized notification
                initialized_notification = {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized"
                }
                
                initialized_json = json.dumps(initialized_notification) + "\n"
                self.server_process.stdin.write(initialized_json)
                self.server_process.stdin.flush()
                
                return True
            else:
                logger.error("No response to initialization request")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing MCP server: {e}")
            return False

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server"""
        try:
            if not self.server_process or self.server_process.poll() is not None:
                await self.start_server()
                await self.initialize_server()
            
            # Prepare the tool call request
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            # Send request to server
            request_json = json.dumps(request) + "\n"
            self.server_process.stdin.write(request_json)
            self.server_process.stdin.flush()
            
            # Read response
            response_line = self.server_process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                
                if "result" in response:
                    # Parse the content from the result
                    content = response["result"].get("content", [])
                    if content and len(content) > 0:
                        return json.loads(content[0]["text"])
                
                return {"error": "Invalid response format"}
            else:
                return {"error": "No response from MCP server"}
                
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}")
            return {"error": str(e)}
    
    async def get_campaigns(self, customer_id: str, user_id: int) -> Dict[str, Any]:
        """Get Google Ads campaigns via MCP"""
        return await self.call_tool("get_campaigns", {
            "customer_id": customer_id,
            "user_id": user_id
        })
    
    async def get_ad_groups(self, customer_id: str, campaign_id: str = None, user_id: int = None) -> Dict[str, Any]:
        """Get Google Ads ad groups via MCP"""
        args = {"customer_id": customer_id}
        if campaign_id:
            args["campaign_id"] = campaign_id
        if user_id:
            args["user_id"] = user_id
        
        return await self.call_tool("get_ad_groups", args)
    
    async def get_keywords(self, customer_id: str, ad_group_id: str = None, user_id: int = None) -> Dict[str, Any]:
        """Get Google Ads keywords via MCP"""
        args = {"customer_id": customer_id}
        if ad_group_id:
            args["ad_group_id"] = ad_group_id
        if user_id:
            args["user_id"] = user_id
        
        return await self.call_tool("get_keywords", args)
    
    async def get_performance_data(self, customer_id: str, start_date: str = None, 
                                 end_date: str = None, resource_type: str = "campaign", 
                                 user_id: int = None) -> Dict[str, Any]:
        """Get performance data via MCP"""
        args = {
            "customer_id": customer_id,
            "resource_type": resource_type
        }
        
        if start_date:
            args["start_date"] = start_date
        if end_date:
            args["end_date"] = end_date
        if user_id:
            args["user_id"] = user_id
        
        return await self.call_tool("get_performance_data", args)
    
    async def get_accessible_customers(self, user_id: int) -> Dict[str, Any]:
        """Get accessible customers via MCP"""
        return await self.call_tool("get_accessible_customers", {
            "user_id": user_id
        })
    
    # === NEW MCP TOOL METHODS ===
    
    async def get_overview(self, customer_id: str, user_id: int) -> Dict[str, Any]:
        """Get account overview via MCP"""
        return await self.call_tool("get_overview", {
            "customer_id": customer_id,
            "user_id": user_id
        })
    
    async def get_campaign_by_id(self, customer_id: str, campaign_id: str, user_id: int = None) -> Dict[str, Any]:
        """Get specific campaign by ID via MCP"""
        args = {"customer_id": customer_id, "campaign_id": campaign_id}
        if user_id:
            args["user_id"] = user_id
        return await self.call_tool("get_campaign_by_id", args)
    
    async def get_campaigns_with_filters(self, customer_id: str, filters: Dict = None, 
                                       start_date: str = None, end_date: str = None, 
                                       user_id: int = None) -> Dict[str, Any]:
        """Get campaigns with filters via MCP"""
        args = {"customer_id": customer_id}
        if filters:
            args["filters"] = filters
        if start_date:
            args["start_date"] = start_date
        if end_date:
            args["end_date"] = end_date
        if user_id:
            args["user_id"] = user_id
        return await self.call_tool("get_campaigns_with_filters", args)
    
    async def create_campaign(self, customer_id: str, campaign_data: Dict, user_id: int = None) -> Dict[str, Any]:
        """Create campaign via MCP"""
        args = {"customer_id": customer_id, "campaign_data": campaign_data}
        if user_id:
            args["user_id"] = user_id
        return await self.call_tool("create_campaign", args)
    
    async def get_ads(self, customer_id: str, campaign_ids: List[str] = None, 
                     ad_ids: List[str] = None, filters: Dict = None, 
                     user_id: int = None) -> Dict[str, Any]:
        """Get ads via MCP"""
        args = {"customer_id": customer_id}
        if campaign_ids:
            args["campaign_ids"] = campaign_ids
        if ad_ids:
            args["ad_ids"] = ad_ids
        if filters:
            args["filters"] = filters
        if user_id:
            args["user_id"] = user_id
        return await self.call_tool("get_ads", args)
    
    async def get_ad_by_id(self, customer_id: str, ad_id: str, user_id: int = None) -> Dict[str, Any]:
        """Get specific ad by ID via MCP"""
        args = {"customer_id": customer_id, "ad_id": ad_id}
        if user_id:
            args["user_id"] = user_id
        return await self.call_tool("get_ad_by_id", args)
    
    async def get_ads_with_filters(self, customer_id: str, filters: Dict = None,
                                 start_date: str = None, end_date: str = None,
                                 user_id: int = None) -> Dict[str, Any]:
        """Get ads with filters via MCP"""
        args = {"customer_id": customer_id}
        if filters:
            args["filters"] = filters
        if start_date:
            args["start_date"] = start_date
        if end_date:
            args["end_date"] = end_date
        if user_id:
            args["user_id"] = user_id
        return await self.call_tool("get_ads_with_filters", args)
    
    async def get_ads_by_campaign_id(self, customer_id: str, campaign_id: str, user_id: int = None) -> Dict[str, Any]:
        """Get ads by campaign ID via MCP"""
        args = {"customer_id": customer_id, "campaign_id": campaign_id}
        if user_id:
            args["user_id"] = user_id
        return await self.call_tool("get_ads_by_campaign_id", args)
    
    async def get_ad_group_by_id(self, customer_id: str, ad_group_id: str, user_id: int = None) -> Dict[str, Any]:
        """Get specific ad group by ID via MCP"""
        args = {"customer_id": customer_id, "ad_group_id": ad_group_id}
        if user_id:
            args["user_id"] = user_id
        return await self.call_tool("get_ad_group_by_id", args)
    
    async def get_ad_groups_with_filters(self, customer_id: str, filters: Dict = None,
                                       start_date: str = None, end_date: str = None,
                                       user_id: int = None) -> Dict[str, Any]:
        """Get ad groups with filters via MCP"""
        args = {"customer_id": customer_id}
        if filters:
            args["filters"] = filters
        if start_date:
            args["start_date"] = start_date
        if end_date:
            args["end_date"] = end_date
        if user_id:
            args["user_id"] = user_id
        return await self.call_tool("get_ad_groups_with_filters", args)
    
    async def get_ad_groups_by_campaign_id(self, customer_id: str, campaign_id: str, user_id: int = None) -> Dict[str, Any]:
        """Get ad groups by campaign ID via MCP"""
        args = {"customer_id": customer_id, "campaign_id": campaign_id}
        if user_id:
            args["user_id"] = user_id
        return await self.call_tool("get_ad_groups_by_campaign_id", args)
    
    async def create_ad(self, customer_id: str, ad_data: Dict, user_id: int = None) -> Dict[str, Any]:
        """Create ad via MCP"""
        args = {"customer_id": customer_id, "ad_data": ad_data}
        if user_id:
            args["user_id"] = user_id
        return await self.call_tool("create_ad", args)
    
    async def pause_campaign(self, customer_id: str, campaign_ids: List[str], user_id: int = None) -> Dict[str, Any]:
        """Pause campaigns via MCP"""
        args = {"customer_id": customer_id, "campaign_ids": campaign_ids}
        if user_id:
            args["user_id"] = user_id
        return await self.call_tool("pause_campaign", args)
    
    async def resume_campaign(self, customer_id: str, campaign_ids: List[str], user_id: int = None) -> Dict[str, Any]:
        """Resume campaigns via MCP"""
        args = {"customer_id": customer_id, "campaign_ids": campaign_ids}
        if user_id:
            args["user_id"] = user_id
        return await self.call_tool("resume_campaign", args)
    
    async def get_budgets(self, customer_id: str, budget_ids: List[str] = None,
                         campaign_ids: List[str] = None, filters: Dict = None,
                         user_id: int = None) -> Dict[str, Any]:
        """Get budgets via MCP"""
        args = {"customer_id": customer_id}
        if budget_ids:
            args["budget_ids"] = budget_ids
        if campaign_ids:
            args["campaign_ids"] = campaign_ids
        if filters:
            args["filters"] = filters
        if user_id:
            args["user_id"] = user_id
        return await self.call_tool("get_budgets", args)
    
    async def get_budget_by_id(self, customer_id: str, budget_id: str, user_id: int = None) -> Dict[str, Any]:
        """Get specific budget by ID via MCP"""
        args = {"customer_id": customer_id, "budget_id": budget_id}
        if user_id:
            args["user_id"] = user_id
        return await self.call_tool("get_budget_by_id", args)
    
    async def get_budgets_with_filters(self, customer_id: str, filters: Dict = None,
                                     start_date: str = None, end_date: str = None,
                                     user_id: int = None) -> Dict[str, Any]:
        """Get budgets with filters via MCP"""
        args = {"customer_id": customer_id}
        if filters:
            args["filters"] = filters
        if start_date:
            args["start_date"] = start_date
        if end_date:
            args["end_date"] = end_date
        if user_id:
            args["user_id"] = user_id
        return await self.call_tool("get_budgets_with_filters", args)
    
    async def get_budgets_by_campaign_id(self, customer_id: str, campaign_id: str, user_id: int = None) -> Dict[str, Any]:
        """Get budgets by campaign ID via MCP"""
        args = {"customer_id": customer_id, "campaign_id": campaign_id}
        if user_id:
            args["user_id"] = user_id
        return await self.call_tool("get_budgets_by_campaign_id", args)

class MCPGoogleAdsService:
    """High-level service for Google Ads operations via MCP"""
    
    def __init__(self):
        self.mcp_client = GoogleAdsMCPClient()
    
    async def initialize(self):
        """Initialize the MCP service"""
        return await self.mcp_client.start_server()
    
    async def cleanup(self):
        """Cleanup the MCP service"""
        await self.mcp_client.stop_server()
    
    async def get_campaign_data(self, customer_id: str, user_id: int) -> Dict[str, Any]:
        """Get comprehensive campaign data"""
        try:
            # Get campaigns
            campaigns_result = await self.mcp_client.get_campaigns(customer_id, user_id)
            
            if not campaigns_result.get("success"):
                return campaigns_result
            
            campaigns = campaigns_result.get("campaigns", [])
            
            # Get performance data for campaigns
            performance_result = await self.mcp_client.get_performance_data(
                customer_id=customer_id,
                resource_type="campaign",
                user_id=user_id
            )
            
            performance_data = performance_result.get("performance_data", []) if performance_result.get("success") else []
            
            # Combine campaigns with performance data
            enhanced_campaigns = []
            for campaign in campaigns:
                campaign_performance = [
                    p for p in performance_data 
                    if p.get("id") == campaign["id"]
                ]
                
                campaign["performance"] = campaign_performance
                enhanced_campaigns.append(campaign)
            
            return {
                "success": True,
                "customer_id": customer_id,
                "campaigns": enhanced_campaigns,
                "total_count": len(enhanced_campaigns),
                "performance_summary": self._summarize_performance(performance_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting campaign data: {e}")
            return {"error": str(e)}
    
    async def get_ad_group_data(self, customer_id: str, campaign_id: str = None, user_id: int = None) -> Dict[str, Any]:
        """Get comprehensive ad group data"""
        try:
            # Get ad groups
            ad_groups_result = await self.mcp_client.get_ad_groups(customer_id, campaign_id, user_id)
            
            if not ad_groups_result.get("success"):
                return ad_groups_result
            
            ad_groups = ad_groups_result.get("ad_groups", [])
            
            # Get performance data for ad groups
            performance_result = await self.mcp_client.get_performance_data(
                customer_id=customer_id,
                resource_type="ad_group",
                user_id=user_id
            )
            
            performance_data = performance_result.get("performance_data", []) if performance_result.get("success") else []
            
            # Combine ad groups with performance data
            enhanced_ad_groups = []
            for ad_group in ad_groups:
                ad_group_performance = [
                    p for p in performance_data 
                    if p.get("id") == ad_group["id"]
                ]
                
                ad_group["performance"] = ad_group_performance
                enhanced_ad_groups.append(ad_group)
            
            return {
                "success": True,
                "customer_id": customer_id,
                "ad_groups": enhanced_ad_groups,
                "total_count": len(enhanced_ad_groups),
                "performance_summary": self._summarize_performance(performance_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting ad group data: {e}")
            return {"error": str(e)}
    
    def _summarize_performance(self, performance_data: List[Dict]) -> Dict[str, Any]:
        """Summarize performance data"""
        if not performance_data:
            return {}
        
        total_impressions = sum(p.get("impressions", 0) for p in performance_data)
        total_clicks = sum(p.get("clicks", 0) for p in performance_data)
        total_cost = sum(p.get("cost_micros", 0) for p in performance_data) / 1_000_000  # Convert to dollars
        total_conversions = sum(p.get("conversions", 0) for p in performance_data)
        
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        avg_cpc = (total_cost / total_clicks) if total_clicks > 0 else 0
        
        return {
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "total_cost": total_cost,
            "total_conversions": total_conversions,
            "average_ctr": avg_ctr,
            "average_cpc": avg_cpc
        }

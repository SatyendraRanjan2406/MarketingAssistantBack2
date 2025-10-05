"""
Fallback handlers for unmatched queries in MCP server
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def handle_unmatched_intent(intent_result, customer_id: str, user_id: int, mcp_service) -> Dict[str, Any]:
    """Handle unmatched intents with intelligent fallback and suggestions"""
    try:
        actions = intent_result.actions
        confidence = intent_result.confidence
        reasoning = intent_result.reasoning
        
        # Check if it's a fallback action
        if "QUERY_WITHOUT_SOLUTION" in actions or "query_understanding_fallback" in actions:
            return await handle_no_solution_fallback(intent_result, customer_id, user_id, mcp_service)
        
        # Check confidence level
        if confidence < 0.3:
            return await handle_low_confidence_fallback(intent_result, customer_id, user_id)
        
        # Try to provide helpful suggestions based on the actions
        return await handle_unsupported_actions_fallback(intent_result, customer_id, user_id, mcp_service)
        
    except Exception as e:
        logger.error(f"Error in unmatched intent handler: {e}")
        return {
            "content": f"I couldn't process your request: {str(e)}. Please try rephrasing your question.",
            "data": None,
            "type": "error"
        }

async def handle_no_solution_fallback(intent_result, customer_id: str, user_id: int, mcp_service) -> Dict[str, Any]:
    """Handle queries that have no clear solution"""
    try:
        # Get accessible customers to show what's available
        result = await mcp_service.mcp_client.get_accessible_customers(user_id)
        
        content = "I couldn't find a specific solution for your request. Here are some things I can help you with:\n\n"
        content += "**📊 Data Retrieval:**\n"
        content += "• Show me my campaigns\n"
        content += "• Get campaign details for ID 12345\n"
        content += "• Show me ads for campaign X\n"
        content += "• Get performance data for last 30 days\n\n"
        content += "**📈 Analysis:**\n"
        content += "• Compare campaign performance\n"
        content += "• Show trends over time\n"
        content += "• Analyze keyword performance\n\n"
        content += "**⚙️ Management:**\n"
        content += "• Pause/resume campaigns\n"
        content += "• Get budget information\n"
        content += "• Show ad group details\n\n"
        content += "Please try rephrasing your question or ask about one of these topics."
        
        return {
            "content": content,
            "data": result,
            "type": "no_solution_fallback",
            "suggestions": [
                "Show me my campaigns",
                "Get performance data",
                "Compare campaign metrics",
                "Show budget information"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in no solution fallback: {e}")
        return {
            "content": "I couldn't process your request. Please try asking about campaigns, ads, performance, or budgets.",
            "data": None,
            "type": "error"
        }

async def handle_low_confidence_fallback(intent_result, customer_id: str, user_id: int) -> Dict[str, Any]:
    """Handle queries with low confidence mapping"""
    try:
        actions = intent_result.actions
        reasoning = intent_result.reasoning
        
        content = f"I'm not sure I understood your request correctly (confidence: {intent_result.confidence:.1%}).\n\n"
        content += f"**What I think you want:** {', '.join(actions)}\n"
        content += f"**Reasoning:** {reasoning}\n\n"
        content += "**Please clarify by asking:**\n"
        content += "• 'Show me my campaigns' - to see all campaigns\n"
        content += "• 'Get performance data' - for metrics and analytics\n"
        content += "• 'Show me ads' - to see your advertisements\n"
        content += "• 'Get budget info' - for spending information\n\n"
        content += "Or be more specific about what data you need."
        
        return {
            "content": content,
            "data": None,
            "type": "low_confidence_fallback",
            "detected_actions": actions,
            "confidence": intent_result.confidence
        }
        
    except Exception as e:
        logger.error(f"Error in low confidence fallback: {e}")
        return {
            "content": "I'm not sure what you're asking for. Please try being more specific about what Google Ads data you need.",
            "data": None,
            "type": "error"
        }

async def handle_unsupported_actions_fallback(intent_result, customer_id: str, user_id: int, mcp_service) -> Dict[str, Any]:
    """Handle queries with actions not supported by MCP server"""
    try:
        actions = intent_result.actions
        unsupported_actions = []
        supported_actions = []
        
        # Check which actions are supported by MCP
        mcp_supported = [
            "GET_OVERVIEW", "GET_CAMPAIGNS", "GET_CAMPAIGN_BY_ID", "GET_CAMPAIGNS_WITH_FILTERS",
            "CREATE_CAMPAIGN", "GET_ADS", "GET_AD_BY_ID", "GET_ADS_WITH_FILTERS", 
            "GET_ADS_BY_CAMPAIGN_ID", "GET_ADSETS", "GET_ADSET_BY_ID", 
            "GET_ADSETS_WITH_FILTERS", "GET_ADSETS_BY_CAMPAIGN_ID", "CREATE_AD",
            "PAUSE_CAMPAIGN", "RESUME_CAMPAIGN", "GET_PERFORMANCE", "GET_KEYWORDS",
            "GET_BUDGETS", "GET_BUDGET_BY_ID", "GET_BUDGETS_WITH_FILTERS", 
            "GET_BUDGETS_BY_CAMPAIGN_ID"
        ]
        
        for action in actions:
            if action in mcp_supported:
                supported_actions.append(action)
            else:
                unsupported_actions.append(action)
        
        if supported_actions:
            # Some actions are supported, try to execute them
            content = f"I can help with some of your request. Let me process the supported actions: {', '.join(supported_actions)}"
            
            # Try to execute the first supported action
            if "GET_OVERVIEW" in supported_actions:
                result = await mcp_service.mcp_client.get_overview(customer_id, user_id)
            elif "GET_CAMPAIGNS" in supported_actions:
                result = await mcp_service.mcp_client.get_campaigns(customer_id, user_id=user_id)
            elif "GET_ADS" in supported_actions:
                result = await mcp_service.mcp_client.get_ads(customer_id, user_id=user_id)
            else:
                result = await mcp_service.mcp_client.get_accessible_customers(user_id)
            
            if unsupported_actions:
                content += f"\n\n**Note:** I couldn't process these actions: {', '.join(unsupported_actions)}. These features are not yet available in the MCP server."
            
            return {
                "content": content,
                "data": result,
                "type": "partial_support",
                "supported_actions": supported_actions,
                "unsupported_actions": unsupported_actions
            }
        else:
            # No supported actions
            content = f"I understand you want to: {', '.join(actions)}\n\n"
            content += "However, these specific actions are not yet supported by the MCP server.\n\n"
            content += "**Available actions include:**\n"
            content += "• GET_OVERVIEW - Account overview\n"
            content += "• GET_CAMPAIGNS - Campaign data\n"
            content += "• GET_ADS - Ad information\n"
            content += "• GET_PERFORMANCE - Performance metrics\n"
            content += "• GET_BUDGETS - Budget information\n"
            content += "• GET_KEYWORDS - Keyword data\n\n"
            content += "Please try asking about one of these supported actions."
            
            return {
                "content": content,
                "data": None,
                "type": "unsupported_actions",
                "requested_actions": actions,
                "available_actions": mcp_supported
            }
            
    except Exception as e:
        logger.error(f"Error in unsupported actions fallback: {e}")
        return {
            "content": f"I couldn't process your request: {str(e)}. Please try asking about campaigns, ads, or performance data.",
            "data": None,
            "type": "error"
        }

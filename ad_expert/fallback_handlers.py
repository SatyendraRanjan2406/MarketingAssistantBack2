"""
Fallback handlers for unmatched queries in MCP server
Enhanced with RAG + ChatGPT pipeline
"""

import logging
from typing import Dict, Any
import asyncio
from openai import OpenAI
import os

logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

async def get_rag_response(query: str, user_id: int) -> Dict[str, Any]:
    """Get response from RAG system"""
    try:
        # Import RAG service
        from google_ads_new.rag_service import RAGService
        
        rag_service = RAGService()
        rag_result = await rag_service.query_rag(query, user_id)
        
        return {
            "success": True,
            "content": rag_result.get("response", ""),
            "sources": rag_result.get("sources", []),
            "confidence": rag_result.get("confidence", 0.0)
        }
    except Exception as e:
        logger.error(f"Error in RAG query: {e}")
        return {
            "success": False,
            "content": "",
            "sources": [],
            "confidence": 0.0,
            "error": str(e)
        }

async def get_chatgpt_response(query: str, context: str = "", mcp_data: Dict = None) -> Dict[str, Any]:
    """Get enhanced response from ChatGPT with quota handling"""
    try:
        # Import quota handler
        from .openai_quota_handler import quota_handler
        
        # Build context for ChatGPT
        system_prompt = """You are an expert Google Ads consultant and marketing assistant. 
        Provide helpful, actionable advice for Google Ads management, optimization, and strategy.
        Be specific, practical, and include relevant metrics and recommendations."""
        
        user_prompt = f"User Query: {query}\n\n"
        
        if context:
            user_prompt += f"Context: {context}\n\n"
        
        if mcp_data:
            user_prompt += f"Available Data: {mcp_data}\n\n"
        
        user_prompt += "Please provide a comprehensive response with actionable insights and recommendations."
        
        # Use quota handler for API call
        response = await quota_handler.generate_chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="gpt-4o",
            temperature=0.7,
            max_tokens=1000
        )
        
        if response and "error" not in response:
            return {
                "success": True,
                "content": response["content"],
                "model": response.get("model", "gpt-4o"),
                "usage": response.get("usage")
            }
        else:
            # Handle quota or other errors
            error_msg = response.get("error", "Unknown error") if response else "No response"
            
            if quota_handler.is_quota_error(error_msg):
                logger.warning(f"Quota exceeded in ChatGPT: {error_msg}")
                return {
                    "success": False,
                    "content": quota_handler.get_fallback_response(query, "quota_exceeded")["content"],
                    "quota_exceeded": True,
                    "error": error_msg
                }
            else:
                logger.error(f"Error in ChatGPT query: {error_msg}")
                return {
                    "success": False,
                    "content": f"I apologize, but I'm having trouble processing your request right now. Please try again later.",
                    "error": error_msg
                }
    except Exception as e:
        logger.error(f"Unexpected error in ChatGPT query: {e}")
        return {
            "success": False,
            "content": f"I apologize, but I'm having trouble processing your request right now. Please try again later.",
            "error": str(e)
        }

async def enhance_mcp_result_with_chatgpt(mcp_result: Dict[str, Any], query: str) -> Dict[str, Any]:
    """Enhance MCP tool results with ChatGPT analysis"""
    try:
        # Extract data from MCP result
        data = mcp_result.get("data", {})
        content = mcp_result.get("content", "")
        
        # Create context for ChatGPT
        context = f"Google Ads Data Retrieved:\n{content}\n\n"
        if isinstance(data, dict):
            context += f"Data Details: {data}\n"
        
        # Get ChatGPT enhancement
        chatgpt_result = await get_chatgpt_response(query, context, data)
        
        if chatgpt_result["success"]:
            # Combine MCP result with ChatGPT enhancement
            enhanced_content = f"{content}\n\n**🤖 AI Analysis & Recommendations:**\n{chatgpt_result['content']}"
            
            return {
                **mcp_result,
                "content": enhanced_content,
                "ai_enhanced": True,
                "ai_analysis": chatgpt_result["content"],
                "original_content": content
            }
        else:
            # Return original MCP result if ChatGPT fails
            return mcp_result
            
    except Exception as e:
        logger.error(f"Error enhancing MCP result with ChatGPT: {e}")
        return mcp_result

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
    """Handle queries that have no clear solution - RAG + ChatGPT pipeline"""
    try:
        # Get the original query from intent result
        original_query = getattr(intent_result, 'original_query', 'your request')
        
        # Step 1: Try RAG first
        logger.info("No solution fallback: Trying RAG system")
        rag_result = await get_rag_response(original_query, user_id)
        
        if rag_result["success"] and rag_result["confidence"] > 0.3:
            # RAG provided a good response
            logger.info(f"RAG provided response with confidence: {rag_result['confidence']}")
            return {
                "content": f"**📚 Knowledge Base Response:**\n{rag_result['content']}",
                "data": {"sources": rag_result.get("sources", [])},
                "type": "rag_response",
                "confidence": rag_result["confidence"],
                "sources": rag_result.get("sources", [])
            }
        
        # Step 2: RAG didn't provide good response, try ChatGPT
        logger.info("RAG didn't provide good response, trying ChatGPT")
        
        # Get accessible customers for context
        accessible_customers = await mcp_service.mcp_client.get_accessible_customers(user_id)
        
        context = f"User has access to Google Ads accounts: {accessible_customers}\n"
        context += "Available operations: campaigns, ads, ad groups, keywords, budgets, performance data\n"
        context += "User query couldn't be mapped to specific Google Ads operations."
        
        chatgpt_result = await get_chatgpt_response(original_query, context)
        
        if chatgpt_result["success"]:
            # Combine ChatGPT response with helpful suggestions
            content = f"**🤖 AI Assistant Response:**\n{chatgpt_result['content']}\n\n"
            content += "**📊 Available Google Ads Operations:**\n"
            content += "• Show me my campaigns\n"
            content += "• Get campaign details for ID 12345\n"
            content += "• Show me ads for campaign X\n"
            content += "• Get performance data for last 30 days\n"
            content += "• Compare campaign performance\n"
            content += "• Get budget information\n"
            content += "• Show ad group details\n\n"
            content += "Please try rephrasing your question or ask about one of these topics."
            
            return {
                "content": content,
                "data": accessible_customers,
                "type": "chatgpt_fallback",
                "ai_enhanced": True,
                "suggestions": [
                    "Show me my campaigns",
                    "Get performance data",
                    "Compare campaign metrics",
                    "Show budget information"
                ]
            }
        else:
            # Both RAG and ChatGPT failed, return basic fallback
            return {
                "content": "I couldn't process your request. Please try asking about campaigns, ads, performance, or budgets.",
                "data": accessible_customers,
                "type": "basic_fallback"
            }
        
    except Exception as e:
        logger.error(f"Error in no solution fallback: {e}")
        return {
            "content": "I couldn't process your request. Please try asking about campaigns, ads, performance, or budgets.",
            "data": None,
            "type": "error"
        }

async def handle_low_confidence_fallback(intent_result, customer_id: str, user_id: int) -> Dict[str, Any]:
    """Handle queries with low confidence mapping - RAG + ChatGPT pipeline"""
    try:
        actions = intent_result.actions
        reasoning = intent_result.reasoning
        original_query = getattr(intent_result, 'original_query', 'your request')
        
        # Step 1: Try RAG first
        logger.info("Low confidence fallback: Trying RAG system")
        rag_result = await get_rag_response(original_query, user_id)
        
        if rag_result["success"] and rag_result["confidence"] > 0.3:
            # RAG provided a good response
            logger.info(f"RAG provided response with confidence: {rag_result['confidence']}")
            return {
                "content": f"**📚 Knowledge Base Response:**\n{rag_result['content']}",
                "data": {"sources": rag_result.get("sources", [])},
                "type": "rag_response",
                "confidence": rag_result["confidence"],
                "sources": rag_result.get("sources", [])
            }
        
        # Step 2: RAG didn't provide good response, try ChatGPT
        logger.info("RAG didn't provide good response, trying ChatGPT")
        
        context = f"Intent mapping confidence: {intent_result.confidence:.1%}\n"
        context += f"Detected actions: {', '.join(actions)}\n"
        context += f"Reasoning: {reasoning}\n"
        context += "The system is not confident about the user's intent."
        
        chatgpt_result = await get_chatgpt_response(original_query, context)
        
        if chatgpt_result["success"]:
            # Combine ChatGPT response with clarification
            content = f"**🤖 AI Assistant Response:**\n{chatgpt_result['content']}\n\n"
            content += f"**⚠️ Low Confidence Detection:**\n"
            content += f"I'm not sure I understood your request correctly (confidence: {intent_result.confidence:.1%}).\n\n"
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
                "type": "chatgpt_low_confidence_fallback",
                "detected_actions": actions,
                "confidence": intent_result.confidence,
                "ai_enhanced": True
            }
        else:
            # Both RAG and ChatGPT failed, return basic fallback
            return {
                "content": "I'm not sure what you're asking for. Please try being more specific about what Google Ads data you need.",
                "data": None,
                "type": "basic_fallback"
            }
        
    except Exception as e:
        logger.error(f"Error in low confidence fallback: {e}")
        return {
            "content": "I'm not sure what you're asking for. Please try being more specific about what Google Ads data you need.",
            "data": None,
            "type": "error"
        }

async def handle_unsupported_actions_fallback(intent_result, customer_id: str, user_id: int, mcp_service) -> Dict[str, Any]:
    """Handle queries with actions not supported by MCP server - RAG + ChatGPT pipeline"""
    try:
        actions = intent_result.actions
        original_query = getattr(intent_result, 'original_query', 'your request')
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
            
            # Enhance with ChatGPT
            mcp_result = {
                "content": content,
                "data": result,
                "type": "partial_support",
                "supported_actions": supported_actions,
                "unsupported_actions": unsupported_actions
            }
            
            enhanced_result = await enhance_mcp_result_with_chatgpt(mcp_result, original_query)
            return enhanced_result
        else:
            # No supported actions - try RAG + ChatGPT
            logger.info("Unsupported actions fallback: Trying RAG system")
            rag_result = await get_rag_response(original_query, user_id)
            
            if rag_result["success"] and rag_result["confidence"] > 0.3:
                # RAG provided a good response
                logger.info(f"RAG provided response with confidence: {rag_result['confidence']}")
                return {
                    "content": f"**📚 Knowledge Base Response:**\n{rag_result['content']}",
                    "data": {"sources": rag_result.get("sources", [])},
                    "type": "rag_response",
                    "confidence": rag_result["confidence"],
                    "sources": rag_result.get("sources", [])
                }
            
            # RAG didn't provide good response, try ChatGPT
            logger.info("RAG didn't provide good response, trying ChatGPT")
            
            context = f"Requested actions: {', '.join(actions)}\n"
            context += "These actions are not supported by the MCP server.\n"
            context += "Available actions: campaigns, ads, ad groups, keywords, budgets, performance data"
            
            chatgpt_result = await get_chatgpt_response(original_query, context)
            
            if chatgpt_result["success"]:
                content = f"**🤖 AI Assistant Response:**\n{chatgpt_result['content']}\n\n"
                content += f"**⚠️ Unsupported Actions:**\n"
                content += f"I understand you want to: {', '.join(actions)}\n\n"
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
                    "type": "chatgpt_unsupported_actions",
                    "requested_actions": actions,
                    "available_actions": mcp_supported,
                    "ai_enhanced": True
                }
            else:
                # Both RAG and ChatGPT failed, return basic fallback
                return {
                    "content": f"I understand you want to: {', '.join(actions)}\n\nHowever, these specific actions are not yet supported by the MCP server.\n\nPlease try asking about campaigns, ads, or performance data.",
                    "data": None,
                    "type": "basic_fallback"
                }
            
    except Exception as e:
        logger.error(f"Error in unsupported actions fallback: {e}")
        return {
            "content": f"I couldn't process your request: {str(e)}. Please try asking about campaigns, ads, or performance data.",
            "data": None,
            "type": "error"
        }

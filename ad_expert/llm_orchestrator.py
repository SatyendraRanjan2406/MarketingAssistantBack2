"""
LLM Orchestrator using OpenAI Responses API with tool calling
Privacy-first: no campaign data at rest, structured outputs for multiple formats
"""
import json
import logging
from typing import Dict, List, Any, Optional
import openai
from django.conf import settings
from .api_tools import GoogleAdsAPITool, MetaMarketingAPITool

logger = logging.getLogger(__name__)


class LLMOrchestrator:
    """LLM Orchestrator with tool calling and structured outputs"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.google_ads_tool = GoogleAdsAPITool()
        self.meta_tool = MetaMarketingAPITool()
        
        # Tool definitions for OpenAI
        self.tool_definitions = [
            {
                "type": "function",
                "function": {
                    "name": "get_google_insights",
                    "description": "Fetch summary metrics from Google Ads campaigns",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "customerId": {
                                "type": "string",
                                "description": "Google Ads customer ID"
                            },
                            "dateRange": {
                                "type": "string",
                                "enum": ["LAST_7_DAYS", "LAST_14_DAYS", "LAST_30_DAYS"],
                                "description": "Date range for the analysis"
                            },
                            "segments": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Segmentation options: device, network, placement"
                            }
                        },
                        "required": ["customerId", "dateRange"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_meta_insights",
                    "description": "Fetch summary metrics from Meta Marketing campaigns",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "adAccountId": {
                                "type": "string",
                                "description": "Meta Ad Account ID"
                            },
                            "dateRange": {
                                "type": "string",
                                "enum": ["LAST_7_DAYS", "LAST_14_DAYS", "LAST_30_DAYS"],
                                "description": "Date range for the analysis"
                            },
                            "breakdowns": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Breakdown options: device_platform, publisher_platform, placement"
                            }
                        },
                        "required": ["adAccountId", "dateRange"]
                    }
                }
            }
        ]
        
        # Response format schema for structured outputs
        self.response_schema = {
            "type": "object",
            "properties": {
                "response_type": {
                    "type": "string",
                    "enum": [
                        "text", "bullets", "table", "comparison_table",
                        "bar_chart", "pie_chart", "line_chart", "histogram",
                        "action_items", "links"
                    ],
                    "description": "The format best suited for this response"
                },
                "title": {
                    "type": "string",
                    "description": "Title for the response"
                },
                "content": {
                    "type": "string",
                    "description": "Main content/explanation"
                },
                "data": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "label": {"type": "string"},
                            "value": {"type": "number"},
                            "url": {"type": "string"},
                            "description": {"type": "string"}
                        },
                        "required": ["label", "value"]
                    },
                    "description": "Data for charts, tables, action items, etc."
                },
                "insights": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Key insights and recommendations"
                }
            },
            "required": ["response_type", "content"]
        }
    
    async def process_query(self, user_message: str, user_id: int, 
                          conversation_context: List[Dict] = None) -> Dict[str, Any]:
        """
        Process user query with tool calling and structured outputs
        """
        try:
            # Build conversation context
            messages = self._build_conversation_context(user_message, conversation_context)
            
            # First call to determine if tools are needed
            response = await self._call_llm_with_tools(messages)
            
            # Process tool calls if any
            if response.get('tool_calls'):
                logger.info(f"Processing {len(response['tool_calls'])} tool calls")
                tool_results = await self._execute_tools(response['tool_calls'], user_id)
                
                # Second call with tool results - format tool messages correctly
                assistant_content = response.get('content', '') or "I'll fetch the data for you."
                assistant_message = {"role": "assistant", "content": assistant_content}
                
                # Add tool_calls to the assistant message if they exist
                if response.get('tool_calls'):
                    assistant_message["tool_calls"] = [
                        {
                            "id": tc["id"],
                            "type": "function",
                            "function": {
                                "name": tc["name"],
                                "arguments": json.dumps(tc["arguments"])
                            }
                        }
                        for tc in response['tool_calls']
                    ]
                
                final_messages = messages + [assistant_message]
                
                # Add tool results with proper tool_call_id
                for tool_call in response['tool_calls']:
                    tool_call_id = tool_call['id']
                    tool_result = tool_results.get(tool_call_id, {})
                    final_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": json.dumps(tool_result)
                    })
                
                logger.info(f"Final messages count: {len(final_messages)}")
                final_response = await self._call_llm_final(final_messages)
                return self._format_structured_response(final_response, tool_results)
            else:
                logger.info("No tool calls detected, returning direct response")
                return self._format_structured_response(response)
                
        except Exception as e:
            logger.error(f"LLM Orchestrator error: {str(e)}")
            return {
                "response_type": "text",
                "content": f"I encountered an error processing your request: {str(e)}",
                "title": "Error"
            }
    
    def _build_conversation_context(self, user_message: str, 
                                  conversation_context: List[Dict] = None) -> List[Dict]:
        """Build conversation context for LLM"""
        system_prompt = """You are an expert advertising co-pilot that helps users analyze their Google Ads and Meta Marketing campaigns. 

Key principles:
- Only fetch campaign data when explicitly requested by the user
- Never store or persist campaign data - process everything in memory
- Provide actionable insights and recommendations
- Use the most appropriate response format (text, charts, tables, action items)
- Focus on performance optimization and strategic guidance

Available tools:
- get_google_insights: Fetch Google Ads campaign data
- get_meta_insights: Fetch Meta Marketing campaign data

When users ask about campaign performance, use the appropriate tools to fetch live data and provide comprehensive analysis.

IMPORTANT: Always respond in valid JSON format with the following structure:
{
  "response_type": "text|table|chart|action_items|etc",
  "title": "Response Title",
  "content": "Main content",
  "data": [...],
  "insights": [...]
}"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation context if available
        if conversation_context:
            for msg in conversation_context[-10:]:  # Last 10 messages for context
                messages.append({
                    "role": msg.get('role', 'user'),
                    "content": msg.get('content', '')
                })
        
        # Add "json" to the user message to satisfy OpenAI's requirement
        user_message_with_json = f"{user_message}\n\nPlease respond in JSON format."
        messages.append({"role": "user", "content": user_message_with_json})
        return messages
    
    async def _call_llm_with_tools(self, messages: List[Dict]) -> Dict[str, Any]:
        """Call LLM with tool calling enabled"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=self.tool_definitions,
                tool_choice="auto",
                temperature=0.1
            )
            
            message = response.choices[0].message
            content = message.content or ""
            tool_calls = message.tool_calls or []
            
            # Parse tool calls properly
            parsed_tool_calls = []
            for tc in tool_calls:
                try:
                    parsed_tool_calls.append({
                        "id": tc.id,
                        "name": tc.function.name,
                        "arguments": json.loads(tc.function.arguments)
                    })
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse tool call arguments: {e}")
                    continue
            
            return {
                "content": content,
                "tool_calls": parsed_tool_calls
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    async def _call_llm_final(self, messages: List[Dict]) -> Dict[str, Any]:
        """Final LLM call with tool results"""
        try:
            # Create a new messages list with JSON instruction at the beginning
            final_messages = [
                {
                    "role": "system", 
                    "content": "Please provide your final response in valid JSON format with response_type, title, content, data, and insights fields. Always respond in JSON format."
                }
            ] + messages
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=final_messages,
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            content = response.choices[0].message.content or "{}"
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"OpenAI final call error: {str(e)}")
            raise
    
    async def _execute_tools(self, tool_calls: List[Dict], user_id: int) -> Dict[str, Any]:
        """Execute tool calls and return results"""
        results = {}
        
        for tool_call in tool_calls:
            try:
                tool_name = tool_call['name']
                arguments = tool_call['arguments']
                
                if tool_name == 'get_google_insights':
                    # Get user's Google OAuth connection from accounts app
                    from accounts.google_oauth_service import UserGoogleAuthService
                    from django.contrib.auth.models import User
                    from asgiref.sync import sync_to_async
                    
                    try:
                        user = await sync_to_async(User.objects.get)(id=user_id)
                    except User.DoesNotExist:
                        results[tool_call['id']] = {
                            "error": "User not found."
                        }
                        continue
                    
                    # Get valid access token (will refresh if needed)
                    access_token = await sync_to_async(UserGoogleAuthService.get_or_refresh_valid_token)(user)
                    
                    if not access_token:
                        results[tool_call['id']] = {
                            "error": "Google Ads account not connected. Please connect your Google Ads account first."
                        }
                        continue
                    
                    # Get Google Ads customer ID
                    customer_id = await sync_to_async(UserGoogleAuthService.get_google_ads_customer_id)(user)
                    if not customer_id:
                        results[tool_call['id']] = {
                            "error": "No Google Ads customer ID found. Please ensure your Google Ads account is properly connected."
                        }
                        continue
                    
                    result = await self.google_ads_tool.get_insights(
                        customer_id=arguments.get('customerId', customer_id),
                        access_token=access_token,
                        date_range=arguments.get('dateRange', 'LAST_14_DAYS'),
                        segments=arguments.get('segments', []),
                        user_id=user_id
                    )
                    results[tool_call['id']] = result
                
                elif tool_name == 'get_meta_insights':
                    # Meta OAuth not yet centralized - return error for now
                    results[tool_call['id']] = {
                        "error": "Meta Marketing API integration is not yet available. Please use Google Ads for now."
                    }
                
            except Exception as e:
                logger.error(f"Tool execution error for {tool_call['name']}: {str(e)}")
                results[tool_call['id']] = {"error": f"Tool execution failed: {str(e)}"}
        
        return results
    
    def _format_structured_response(self, llm_response: Dict[str, Any], 
                                  tool_results: Dict[str, Any] = None) -> Dict[str, Any]:
        """Format LLM response into structured output"""
        try:
            # Parse LLM response
            if isinstance(llm_response, str):
                try:
                    response_data = json.loads(llm_response)
                except json.JSONDecodeError:
                    # If JSON parsing fails, create a basic response
                    response_data = {
                        "response_type": "text",
                        "content": llm_response,
                        "title": "Response"
                    }
            else:
                response_data = llm_response
            
            # Ensure required fields
            response_type = response_data.get('response_type', 'text')
            content = response_data.get('content', '')
            title = response_data.get('title', '')
            data = response_data.get('data', [])
            insights = response_data.get('insights', [])
            
            # Enhance data with tool results if available
            if tool_results and not data:
                data = self._extract_data_from_tool_results(tool_results, response_type)
            
            return {
                "response_type": response_type,
                "title": title,
                "content": content,
                "data": data,
                "insights": insights
            }
            
        except Exception as e:
            logger.error(f"Response formatting error: {str(e)}")
            return {
                "response_type": "text",
                "content": "I processed your request but encountered a formatting issue. Please try again.",
                "title": "Response",
                "data": [],
                "insights": []
            }
    
    def _extract_data_from_tool_results(self, tool_results: Dict[str, Any], 
                                      response_type: str) -> List[Dict[str, Any]]:
        """Extract structured data from tool results based on response type"""
        data = []
        
        for tool_id, result in tool_results.items():
            if 'error' in result:
                continue
            
            if response_type == 'line_chart' and 'by_date' in result:
                # Format for line chart
                for date, metrics in result['by_date'].items():
                    data.append({
                        "label": date,
                        "value": metrics.get('spend', 0),
                        "description": f"Spend: ${metrics.get('spend', 0):.2f}"
                    })
            
            elif response_type == 'bar_chart' and 'by_campaign' in result:
                # Format for bar chart
                for campaign, metrics in result['by_campaign'].items():
                    data.append({
                        "label": campaign[:30],  # Truncate long names
                        "value": metrics.get('spend', 0),
                        "description": f"CTR: {metrics.get('ctr', 0):.2f}%"
                    })
            
            elif response_type == 'table' and 'summary' in result:
                # Format for table
                summary = result['summary']
                data.extend([
                    {"label": "Total Spend", "value": summary.get('total_spend', 0)},
                    {"label": "Total Impressions", "value": summary.get('total_impressions', 0)},
                    {"label": "Total Clicks", "value": summary.get('total_clicks', 0)},
                    {"label": "CTR", "value": summary.get('ctr', 0)},
                    {"label": "CPC", "value": summary.get('cpc', 0)},
                    {"label": "CPA", "value": summary.get('cpa', 0)}
                ])
        
        return data

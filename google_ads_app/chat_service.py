import logging
import json
import re
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from .services import GoogleAdsService
from .models import GoogleAdsAccount, GoogleAdsCampaign, GoogleAdsPerformance

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ChartData(BaseModel):
    """Schema for chart data output"""
    chart_type: str = Field(description="Type of chart: line, bar, pie, table")
    title: str = Field(description="Chart title")
    data: Dict[str, Any] = Field(description="Chart data in appropriate format", default={})
    description: str = Field(description="Text description of the chart", default="")


class ChatResponse(BaseModel):
    """Schema for chat response output"""
    text_response: str = Field(description="Text response to user query")
    charts: List[ChartData] = Field(description="List of charts to display", default=[])
    actions: List[str] = Field(description="List of suggested actions", default=[])
    data_summary: str = Field(description="Summary of relevant data", default="")
    insights: List[str] = Field(description="Key insights in bullet points", default=[])
    metrics: Dict[str, Any] = Field(description="Key performance metrics", default={})


class GoogleAdsChatService:
    """Chat service for Google Ads data analysis using LangChain"""
    
    def __init__(self, user_id: int, openai_api_key: str = None):
        self.user_id = user_id
        
        # Get API key from parameter, environment variable, or use None
        if openai_api_key:
            self.openai_api_key = openai_api_key
        else:
            self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        print(f"🔍 DEBUG: Initializing GoogleAdsChatService for user_id: {user_id}")
        print(f"🔍 DEBUG: OpenAI API key provided: {bool(self.openai_api_key)}")
        
        # Initialize LLM only if API key is provided
        if self.openai_api_key:
            try:
                print(f"🔍 DEBUG: Initializing OpenAI LLM...")
                self.llm = ChatOpenAI(
                    model="gpt-3.5-turbo",
                    temperature=0.1,
                    openai_api_key=self.openai_api_key
                )
                self.parser = PydanticOutputParser(pydantic_object=ChatResponse)
                print(f"🔍 DEBUG: OpenAI LLM initialized successfully")
            except Exception as e:
                print(f"❌ DEBUG: Failed to initialize OpenAI client: {e}")
                logger.warning(f"Failed to initialize OpenAI client: {e}")
                self.llm = None
                self.parser = None
        else:
            print(f"🔍 DEBUG: No OpenAI API key provided, skipping LLM initialization")
            self.llm = None
            self.parser = None
            
        # Initialize Google Ads service only if needed
        try:
            print(f"🔍 DEBUG: Attempting to initialize GoogleAdsService...")
            self.google_ads_service = GoogleAdsService()
            print(f"✅ DEBUG: GoogleAdsService initialized successfully")
        except Exception as e:
            print(f"❌ DEBUG: Failed to initialize GoogleAdsService: {e}")
            print(f"❌ DEBUG: Error type: {type(e)}")
            print(f"❌ DEBUG: Error details: {str(e)}")
            logger.warning(f"Failed to initialize Google Ads service: {e}")
            self.google_ads_service = None
        
        # System prompt for the AI
        self.system_prompt = """You are a Google Ads data analyst assistant. You help users understand their advertising performance data.

Your capabilities:
1. Analyze campaign performance, keywords, ad groups
2. Generate insights from data
3. Create charts and visualizations
4. Suggest optimization actions
5. Answer questions about Google Ads metrics

CRITICAL: You MUST respond in EXACT JSON format that matches this structure:

{
  "text_response": "Your conversational explanation here",
  "insights": [
    "First insight point",
    "Second insight point", 
    "Third insight point"
  ],
  "metrics": {
    "CTR": "2.5%",
    "CPC": "$1.25",
    "Spend": "$500.00"
  },
  "charts": [
    {
      "chart_type": "line",
      "title": "Performance Over Time",
      "data": {
        "data": [
          {"date": "2024-01", "impressions": 1000, "clicks": 50, "cost": 100},
          {"date": "2024-02", "impressions": 1200, "clicks": 60, "cost": 120}
        ]
      }
    }
  ],
  "actions": [
    "First action recommendation",
    "Second action recommendation",
    "Third action recommendation"
  ],
  "data_summary": "Brief summary of analysis"
}

IMPORTANT RULES:
- insights MUST be an array of strings, NOT a single string with bullet points
- metrics MUST be a JSON object with key-value pairs, NOT bullet points
- actions MUST be an array of strings, NOT a single string with bullet points
- charts MUST include sample data in the data.data array for visualization
- Use proper JSON syntax with quotes around all strings
- Do NOT include bullet points (•) in the JSON values"""
    
    def get_user_data_context(self) -> Dict[str, Any]:
        """Get user's Google Ads data for context"""
        try:
            # Check if Google Ads service is available
            if not self.google_ads_service:
                return {
                    "error": "Google Ads service not available",
                    "accounts_count": 0,
                    "total_spend": 0,
                    "total_impressions": 0,
                    "total_clicks": 0,
                    "total_conversions": 0,
                    "ctr": 0,
                    "cpc": 0,
                    "campaigns": [],
                    "date_range": "Service unavailable"
                }
            
            # Get user's accounts
            accounts = GoogleAdsAccount.objects.filter(user_id=self.user_id, is_active=True)
            if not accounts.exists():
                return {"error": "No active Google Ads accounts found"}
            
            # Get recent performance data
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
            
            performance_data = GoogleAdsPerformance.objects.filter(
                account__in=accounts,
                date__range=[start_date, end_date]
            ).select_related('campaign', 'ad_group', 'keyword')
            
            # Aggregate data
            total_spend = sum(p.cost_micros for p in performance_data) / 1000000
            total_impressions = sum(p.impressions for p in performance_data)
            total_clicks = sum(p.clicks for p in performance_data)
            total_conversions = sum(p.conversions for p in performance_data)
            
            # Campaign performance
            from django.db import models
            campaign_data = performance_data.values('campaign__campaign_name').annotate(
                spend=models.Sum('cost_micros'),
                impressions=models.Sum('impressions'),
                clicks=models.Sum('clicks'),
                conversions=models.Sum('conversions')
            )
            
            return {
                "accounts_count": accounts.count(),
                "total_spend": total_spend,
                "total_impressions": total_impressions,
                "total_clicks": total_clicks,
                "total_conversions": total_conversions,
                "ctr": total_clicks / total_impressions if total_impressions > 0 else 0,
                "cpc": total_spend / total_clicks if total_clicks > 0 else 0,
                "campaigns": list(campaign_data),
                "date_range": f"{start_date} to {end_date}"
            }
        except Exception as e:
            logger.error(f"Error getting user data context: {e}")
            return {"error": str(e)}
    
    def create_performance_chart(self, data: List[Dict], chart_type: str = "line", title: str = None) -> Dict[str, Any]:
        """Create a chart using Plotly Graph Objects"""
        try:
            print(f"🔍 DEBUG: Creating {chart_type} chart with {len(data)} data points")
            print(f"🔍 DEBUG: Chart data: {data}")
            
            if not data:
                return {"error": "No data provided for chart"}
            
            # Handle nested data structure (data.data format)
            if isinstance(data, dict) and 'data' in data:
                print(f"🔍 DEBUG: Found nested data structure, extracting data.data")
                data = data['data']
            
            print(f"🔍 DEBUG: Final data structure: {data}")
            df = pd.DataFrame(data)
            print(f"🔍 DEBUG: DataFrame columns: {list(df.columns)}")
            print(f"🔍 DEBUG: DataFrame shape: {df.shape}")
            
            if chart_type == "line":
                # Time series chart
                fig = go.Figure()
                
                # Add traces for different metrics
                if 'date' in df.columns and 'impressions' in df.columns:
                    fig.add_trace(go.Scatter(x=df['date'], y=df['impressions'], 
                                           name='Impressions', mode='lines+markers'))
                if 'date' in df.columns and 'clicks' in df.columns:
                    fig.add_trace(go.Scatter(x=df['date'], y=df['clicks'], 
                                           name='Clicks', mode='lines+markers'))
                if 'date' in df.columns and 'cost' in df.columns:
                    fig.add_trace(go.Scatter(x=df['date'], y=df['cost'], 
                                           name='Cost', mode='lines+markers'))
                
                fig.update_layout(
                    title=title or 'Performance Over Time',
                    xaxis_title='Date',
                    yaxis_title='Value',
                    hovermode='x unified'
                )
                
            elif chart_type == "bar":
                # Bar chart for campaigns
                if 'campaign__campaign_name' in df.columns and 'spend' in df.columns:
                    fig = go.Figure(data=[go.Bar(x=df['campaign__campaign_name'], y=df['spend'])])
                elif 'campaign__campaign_name' in df.columns and 'impressions' in df.columns:
                    fig = go.Figure(data=[go.Bar(x=df['campaign__campaign_name'], y=df['impressions'])])
                else:
                    # Use first two columns as x and y
                    cols = list(df.columns)
                    if len(cols) >= 2:
                        fig = go.Figure(data=[go.Bar(x=df[cols[0]], y=df[cols[1]])])
                    else:
                        return {"error": "Insufficient data for bar chart"}
                
                fig.update_layout(
                    title=title or 'Performance Comparison',
                    xaxis_title='Category',
                    yaxis_title='Value'
                )
                
            elif chart_type == "pie":
                # Pie chart for distribution
                print(f"🔍 DEBUG: Creating pie chart with data: {df.head()}")
                print(f"🔍 DEBUG: DataFrame columns for pie chart: {list(df.columns)}")
                
                # Handle the specific data structure from your response
                if 'metric' in df.columns and 'value' in df.columns:
                    print(f"🔍 DEBUG: Using metric/value columns for pie chart")
                    fig = go.Figure(data=[go.Pie(labels=df['metric'], values=df['value'])])
                elif 'campaign__campaign_name' in df.columns and 'spend' in df.columns:
                    fig = go.Figure(data=[go.Pie(labels=df['campaign__campaign_name'], 
                                               values=df['spend'])])
                elif 'campaign__campaign_name' in df.columns and 'impressions' in df.columns:
                    fig = go.Figure(data=[go.Pie(labels=df['campaign__campaign_name'], 
                                               values=df['impressions'])])
                else:
                    # Use first two columns as labels and values
                    cols = list(df.columns)
                    if len(cols) >= 2:
                        print(f"🔍 DEBUG: Using columns {cols[0]} and {cols[1]} for pie chart")
                        fig = go.Figure(data=[go.Pie(labels=df[cols[0]], values=df[cols[1]])])
                    else:
                        return {"error": "Insufficient data for pie chart"}
                
                fig.update_layout(title=title or 'Distribution Chart')
                
            elif chart_type == "table":
                # Table format
                fig = go.Figure(data=[go.Table(
                    header=dict(values=list(df.columns), fill_color='lightblue'),
                    cells=dict(values=[df[col] for col in df.columns], fill_color='white')
                )])
                fig.update_layout(title=title or 'Data Table')
                
            else:
                # Default to line chart
                fig = go.Figure()
                if 'date' in df.columns and len(df.columns) > 1:
                    for col in df.columns:
                        if col != 'date':
                            fig.add_trace(go.Scatter(x=df['date'], y=df[col], name=col, mode='lines+markers'))
                    fig.update_layout(title=title or 'Performance Data', xaxis_title='Date', yaxis_title='Value')
                else:
                    return {"error": "Cannot create chart with available data"}
            
            # Convert to JSON
            chart_json = json.loads(fig.to_json())
            print(f"🔍 DEBUG: Chart created successfully: {chart_type}")
            return chart_json
            
        except Exception as e:
            print(f"❌ DEBUG: Error creating chart: {e}")
            logger.error(f"Error creating chart: {e}")
            return {"error": f"Failed to create chart: {str(e)}"}
    
    def chat(self, user_message: str) -> Dict[str, Any]:
        """Process user chat message and return response"""
        print(f"🔍 DEBUG: ===== CHAT METHOD BREAKPOINT =====")
        print(f"🔍 DEBUG: Chat method called with message: {user_message}")
        print(f"🔍 DEBUG: User ID: {self.user_id}")
        print(f"🔍 DEBUG: LLM available: {bool(self.llm)}")
        print(f"🔍 DEBUG: Google Ads service available: {bool(self.google_ads_service)}")
        
        try:
            # Check if LLM is available
            if not self.llm:
                print(f"❌ DEBUG: LLM not available, returning fallback response")
                return {
                    "text_response": "OpenAI API key not configured or quota exceeded. Please check your OpenAI account billing and set a valid OPENAI_API_KEY environment variable.",
                    "insights": [],
                    "metrics": {},
                    "charts": [],
                    "actions": ["Check OpenAI account billing and quota", "Set valid OPENAI_API_KEY environment variable", "Restart the Django server"],
                    "data_summary": "AI features temporarily unavailable"
                }
            
            # Get user's data context
            print(f"🔍 DEBUG: ===== GETTING USER DATA CONTEXT =====")
            user_context = self.get_user_data_context()
            print(f"🔍 DEBUG: User context retrieved: {bool(user_context)}")
            print(f"🔍 DEBUG: User context keys: {list(user_context.keys()) if isinstance(user_context, dict) else 'Not a dict'}")
            
            # Create prompt template - using simple text to avoid template variable conflicts
            print(f"🔍 DEBUG: ===== CREATING PROMPT TEMPLATE =====")
            
            # Create a simple text prompt without complex template variables
            prompt_text = f"""User Context: {json.dumps(user_context, indent=2)}

User Question: {user_message}

CRITICAL: You MUST respond with valid JSON that exactly matches this structure:

{{
  "text_response": "Your conversational explanation here",
  "insights": [
    "First insight point",
    "Second insight point",
    "Third insight point"
  ],
  "metrics": {{
    "CTR": "2.5%",
    "CPC": "$1.25",
    "Spend": "$500.00"
  }},
  "charts": [
    {{
      "chart_type": "line",
      "title": "Performance Over Time",
      "data": {{
        "data": [
          {{"date": "2024-01", "impressions": 1000, "clicks": 50, "cost": 100}},
          {{"date": "2024-02", "impressions": 1200, "clicks": 60, "cost": 120}}
        ]
      }}
    }}
  ],
  "actions": [
    "First action recommendation",
    "Second action recommendation",
    "Third action recommendation"
  ],
  "data_summary": "Brief summary of analysis"
}}

IMPORTANT: For charts, you MUST include sample data in the data.data array so charts can be rendered. Use realistic values based on the user's context."""

            # Create messages manually to avoid template formatting issues
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt_text}
            ]
            

            
            # Get LLM response
            print(f"🔍 DEBUG: ===== INVOKING LLM =====")
            print(f"🔍 DEBUG: About to call OpenAI API...")
            print(f"🔍 DEBUG: Messages being sent: {messages}")
            
            # Convert messages to LangChain format
            from langchain_core.messages import SystemMessage, HumanMessage
            langchain_messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=prompt_text)
            ]
            
            response = self.llm.invoke(langchain_messages)
            print(f"🔍 DEBUG: LLM response received: {type(response)}")
            print(f"🔍 DEBUG: Response content: {response.content[:200]}...")
            
            # Parse response
            print(f"🔍 DEBUG: ===== PARSING RESPONSE =====")
            print(f"🔍 DEBUG: Raw LLM response: {response.content}")
            
            try:
                parsed_response = self.parser.parse(response.content)
                result = parsed_response.dict()
                print(f"🔍 DEBUG: Successfully parsed response: {result}")
            except Exception as parse_error:
                print(f"❌ DEBUG: Failed to parse structured response: {parse_error}")
                print(f"❌ DEBUG: Attempting to extract JSON from response...")
                
                # Try to extract JSON from the response
                try:
                    print(f"🔍 DEBUG: Attempting to extract JSON from response...")
                    # Look for the complete JSON response - find the outermost JSON object
                    json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group()
                        print(f"🔍 DEBUG: Found JSON string: {json_str[:500]}...")
                        
                        # Try to parse the full JSON
                        try:
                            extracted_json = json.loads(json_str)
                            print(f"🔍 DEBUG: Successfully extracted full JSON: {extracted_json}")
                            result = extracted_json
                        except json.JSONDecodeError as decode_error:
                            print(f"❌ DEBUG: JSON decode error: {decode_error}")
                            # Try to find and extract individual fields
                            result = self._extract_fields_from_text(response.content)
                    else:
                        print(f"❌ DEBUG: No JSON pattern found in response")
                        result = self._extract_fields_from_text(response.content)
                except Exception as json_error:
                    print(f"❌ DEBUG: Failed to extract JSON: {json_error}")
                    print(f"❌ DEBUG: Response content: {response.content[:500]}...")
                    result = self._extract_fields_from_text(response.content)
            
            # Generate charts if requested
            if result.get("charts"):
                print(f"🔍 DEBUG: Processing {len(result['charts'])} charts...")
                for i, chart in enumerate(result["charts"]):
                    print(f"🔍 DEBUG: Processing chart {i+1}: {chart}")
                    
                    # Check if chart already has chart_data (from LLM)
                    if chart.get("chart_data") and isinstance(chart["chart_data"], dict):
                        print(f"🔍 DEBUG: Chart {i+1} already has chart_data from LLM")
                        # Always regenerate chart_data to ensure it's valid
                        print(f"🔄 DEBUG: Regenerating chart_data for chart {i+1} to ensure validity")
                        chart["chart_data"] = self._regenerate_chart_data(chart)
                    elif chart.get("data") and isinstance(chart["data"], dict):
                        # Create actual chart data from user data
                        print(f"🔍 DEBUG: Chart {i+1} creating from user data")
                        chart_data = self.create_performance_chart(
                            data=chart["data"],
                            chart_type=chart["chart_type"],
                            title=chart.get("title", f"Chart {i+1}")
                        )
                        chart["chart_data"] = chart_data
                        print(f"🔍 DEBUG: Chart {i+1} created: {bool(chart_data.get('error'))}")
                    else:
                        print(f"❌ DEBUG: Chart {i+1} has no data or invalid data structure")
                        # Generate sample data for demonstration
                        sample_data = self._generate_sample_chart_data(chart.get("chart_type", "line"))
                        chart_data = self.create_performance_chart(
                            data=sample_data,
                            chart_type=chart["chart_type"],
                            title=chart.get("title", f"Sample {chart['chart_type'].title()} Chart")
                        )
                        chart["chart_data"] = chart_data
            
            return result
            
        except Exception as e:
            print(f"❌ DEBUG: ===== ERROR IN CHAT METHOD =====")
            print(f"❌ DEBUG: Error in chat method: {e}")
            print(f"❌ DEBUG: Error type: {type(e)}")
            print(f"❌ DEBUG: Error details: {str(e)}")
            import traceback
            print(f"❌ DEBUG: Full traceback:")
            traceback.print_exc()
            logger.error(f"Error in chat service: {e}")
            return {
                "text_response": f"Sorry, I encountered an error: {str(e)}",
                "insights": [],
                "metrics": {},
                "charts": [],
                "actions": [],
                "data_summary": "Error occurred while processing request"
            }
    
    def _extract_fields_from_text(self, text: str) -> Dict[str, Any]:
        """Extract structured fields from text response when JSON parsing fails"""
        print(f"🔍 DEBUG: Extracting fields from text: {text[:200]}...")
        
        result = {
            "text_response": text,
            "insights": [],
            "metrics": {},
            "charts": [],
            "actions": [],
            "data_summary": "Extracted from text response"
        }
        
        try:
            # Try to extract insights (lines starting with • or -)
            insights = re.findall(r'[•\-]\s*(.+?)(?=\n|$)', text, re.MULTILINE)
            if insights:
                result["insights"] = [insight.strip() for insight in insights]
            
            # Try to extract metrics (key: value patterns)
            metrics = re.findall(r'([A-Za-z\s]+):\s*([^,\n]+)', text)
            if metrics:
                result["metrics"] = {key.strip(): value.strip() for key, value in metrics}
            
            # Try to extract actions (lines with action keywords)
            action_keywords = ['create', 'optimize', 'improve', 'consider', 'implement', 'monitor', 'analyze']
            actions = []
            for line in text.split('\n'):
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in action_keywords):
                    actions.append(line.strip())
            if actions:
                result["actions"] = actions[:5]  # Limit to 5 actions
            
            print(f"🔍 DEBUG: Extracted fields: {result}")
            
        except Exception as e:
            print(f"❌ DEBUG: Error extracting fields: {e}")
        
        return result
    
    def get_quick_insights(self) -> Dict[str, Any]:
        """Get quick insights without user input"""
        try:
            user_context = self.get_user_data_context()
            
            if "error" in user_context:
                return {"error": user_context["error"]}
            
            # Generate insights based on data
            insights = []
            actions = []
            
            # CTR analysis
            ctr = user_context.get("ctr", 0)
            if ctr < 0.02:  # Less than 2%
                insights.append("Your click-through rate is below industry average. Consider improving ad relevance and targeting.")
                actions.append("Review and optimize ad copy and targeting parameters")
            
            # Cost analysis
            total_spend = user_context.get("total_spend", 0)
            if total_spend > 1000:  # High spend
                insights.append("You have significant ad spend. Focus on optimizing for better ROAS.")
                actions.append("Analyze conversion data and adjust bidding strategies")
            
            # Campaign diversity
            campaigns_count = len(user_context.get("campaigns", []))
            if campaigns_count < 3:
                insights.append("Consider diversifying your campaign strategy with more targeted campaigns.")
                actions.append("Create new campaigns for different audience segments")
            
            return {
                "text_response": "Here are your quick insights based on your Google Ads performance data.",
                "insights": insights,
                "actions": actions,
                "metrics": {
                    "Total Spend": f"${user_context.get('total_spend', 0):.2f}",
                    "CTR": f"{ctr:.2%}",
                    "Campaigns": campaigns_count,
                    "Total Impressions": user_context.get("total_impressions", 0),
                    "Total Clicks": user_context.get("total_clicks", 0)
                },
                "charts": [],
                "data_summary": f"Analysis of {campaigns_count} campaigns with ${user_context.get('total_spend', 0):.2f} total spend"
            }
            
        except Exception as e:
            logger.error(f"Error getting quick insights: {e}")
            return {"error": str(e)}
    
    def _is_valid_chart_data(self, chart_data: Dict) -> bool:
        """Check if chart_data has valid Plotly structure"""
        try:
            if not isinstance(chart_data, dict):
                return False
            
            # Check if it has data and layout
            if 'data' not in chart_data or 'layout' not in chart_data:
                return False
            
            # Check if data is a list
            if not isinstance(chart_data['data'], list):
                return False
            
            # Check if each data item has valid structure
            for item in chart_data['data']:
                if not isinstance(item, dict):
                    return False
                if 'type' not in item:
                    return False
                
                # For pie charts, check if values are valid
                if item['type'] == 'pie':
                    if 'values' in item:
                        values = item['values']
                        # Check if values is a list of numbers or a simple array
                        if isinstance(values, dict) and ('dtype' in values or 'bdata' in values):
                            return False  # This is encoded data, not valid
                        if not isinstance(values, (list, tuple)):
                            return False
            
            return True
        except Exception as e:
            print(f"❌ DEBUG: Error validating chart data: {e}")
            return False
    
    def _regenerate_chart_data(self, chart: Dict) -> Dict:
        """Regenerate chart data when the LLM provides invalid data"""
        try:
            print(f"🔍 DEBUG: Regenerating chart data for {chart.get('chart_type', 'unknown')} chart")
            
            # Try to use the original data if available
            if chart.get("data") and isinstance(chart["data"], dict):
                print(f"🔍 DEBUG: Using original data for chart regeneration")
                chart_data = self.create_performance_chart(
                    data=chart["data"],
                    chart_type=chart["chart_type"],
                    title=chart.get("title", "Chart")
                )
                if "error" not in chart_data:
                    print(f"✅ DEBUG: Chart regenerated successfully from original data")
                    return chart_data
                else:
                    print(f"❌ DEBUG: Error creating chart from original data: {chart_data.get('error')}")
            
            # Fallback to sample data
            print(f"🔄 DEBUG: Falling back to sample data for {chart.get('chart_type', 'line')} chart")
            sample_data = self._generate_sample_chart_data(chart.get("chart_type", "line"))
            chart_data = self.create_performance_chart(
                data=sample_data,
                chart_type=chart["chart_type"],
                title=chart.get("title", f"Sample {chart['chart_type'].title()} Chart")
            )
            print(f"✅ DEBUG: Sample chart created successfully")
            return chart_data
            
        except Exception as e:
            print(f"❌ DEBUG: Error regenerating chart data: {e}")
            import traceback
            traceback.print_exc()
            # Return a simple error chart
            return {
                "data": [{"type": "pie", "labels": ["Error"], "values": [1]}],
                "layout": {"title": "Chart Error"}
            }
    
    def _generate_sample_chart_data(self, chart_type: str) -> List[Dict]:
        """Generate sample data for charts when no real data is available"""
        print(f"🔍 DEBUG: Generating sample data for {chart_type} chart")
        
        if chart_type == "pie":
            return [
                {"category": "Campaign A", "value": 40},
                {"category": "Campaign B", "value": 30},
                {"category": "Campaign C", "value": 20},
                {"category": "Campaign D", "value": 10}
            ]
        elif chart_type == "bar":
            return [
                {"campaign": "Campaign A", "spend": 500, "clicks": 100},
                {"campaign": "Campaign B", "spend": 300, "clicks": 80},
                {"campaign": "Campaign C", "spend": 200, "clicks": 60}
            ]
        elif chart_type == "line":
            return [
                {"date": "2024-01", "impressions": 1000, "clicks": 50, "cost": 100},
                {"date": "2024-02", "impressions": 1200, "clicks": 60, "cost": 120},
                {"date": "2024-03", "impressions": 1100, "clicks": 55, "cost": 110}
            ]
        else:
            return [
                {"metric": "CTR", "value": "2.5%"},
                {"metric": "CPC", "value": "$1.25"},
                {"metric": "Spend", "value": "$500.00"}
            ]

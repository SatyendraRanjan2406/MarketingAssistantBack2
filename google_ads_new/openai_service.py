"""
OpenAI Service for Google Ads Analysis
Generates dynamic responses using OpenAI API for all analysis actions
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from openai import OpenAI
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

class GoogleAdsOpenAIService:
    """OpenAI service for generating dynamic Google Ads analysis responses"""
    
    def __init__(self):
        # Load API key from environment variable
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is not set. "
                "Please set it in your .env file or environment variables."
            )
        
        self.client = OpenAI(api_key=api_key)
        self.logger = logging.getLogger(__name__)
    
    def generate_analysis_response(self, action: str, data: Dict[str, Any], user_context: str = "") -> Dict[str, Any]:
        """Generate dynamic analysis response using OpenAI"""
        try:
            # Create context-aware prompt
            prompt = self._create_analysis_prompt(action, data, user_context)
            
            # Generate response using OpenAI
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use accessible model
                messages=[
                    {
                        "role": "system",
                        "content": """You are a Google Ads expert analyst. Generate comprehensive, actionable insights and recommendations. 
                        Always structure your response with multiple UI blocks including charts, tables, lists, actions, and text.
                        Use real data when available, provide specific recommendations, and include actionable next steps."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parse the response and structure it into UI blocks
            content = response.choices[0].message.content
            return self._parse_openai_response(content, action, data)
            
        except Exception as e:
            self.logger.error(f"Error generating OpenAI response: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return self._generate_fallback_response(action, data, str(e))
    
    def _create_analysis_prompt(self, action: str, data: Dict[str, Any], user_context: str) -> str:
        """Create context-aware prompt for OpenAI"""
        
        base_prompt = f"""
        You are analyzing Google Ads data for the action: {action}
        
        Available data: {json.dumps(data, indent=2)}
        User context: {user_context}
        
        Generate a comprehensive analysis response that includes:
        1. A text summary of findings
        2. A chart (pie/bar) showing key metrics
        3. A table with detailed data
        4. A dotted list of recommendations
        5. Action buttons for next steps
        6. Relevant insights and observations
        
        Make the response specific, actionable, and data-driven. Use the actual data provided when possible.
        Structure the response as JSON with the following format:
        {{
            "blocks": [
                {{
                    "type": "text",
                    "content": "Summary text",
                    "style": "heading"
                }},
                {{
                    "type": "chart",
                    "chart_type": "pie|bar",
                    "title": "Chart Title",
                    "data": {{
                        "labels": ["Label1", "Label2"],
                        "datasets": [{{
                            "data": [value1, value2],
                            "backgroundColor": ["#FF6384", "#36A2EB"]
                        }}]
                    }}
                }},
                {{
                    "type": "table",
                    "title": "Table Title",
                    "headers": ["Header1", "Header2"],
                    "rows": [["Row1Col1", "Row1Col2"], ["Row2Col1", "Row2Col2"]]
                }},
                {{
                    "type": "list",
                    "title": "Recommendations",
                    "items": ["Item 1", "Item 2"],
                    "style": "dotted"
                }},
                {{
                    "type": "actions",
                    "title": "Next Steps",
                    "items": [
                        {{"id": "action1", "label": "Action 1"}},
                        {{"id": "action2", "label": "Action 2"}}
                    ]
                }}
            ]
        }}
        """
        
        # Add action-specific context
        action_contexts = {
            "CHECK_CAMPAIGN_CONSISTENCY": "Focus on keyword-ad alignment, ad group organization, and campaign structure consistency. Identify inconsistencies and provide specific fixes.",
            "CHECK_SITELINKS": "Analyze sitelink presence, count, and optimization. Suggest improvements for better user experience and conversion.",
            "CHECK_LANDING_PAGE_URL": "Evaluate landing page functionality, keyword relevance, and user experience. Provide specific optimization recommendations.",
            "CHECK_DUPLICATE_KEYWORDS": "Identify duplicate keywords that could cause bidding conflicts. Suggest consolidation strategies and negative keyword implementations.",
            "ANALYZE_KEYWORD_TRENDS": "Analyze keyword performance trends, identify high-potential keywords, and suggest expansion opportunities.",
            "ANALYZE_AUCTION_INSIGHTS": "Analyze competitive landscape, market share, and competitor strategies. Provide competitive positioning insights.",
            "ANALYZE_SEARCH_TERMS": "Review search term performance, identify negative keyword opportunities, and suggest exclusion strategies.",
            "ANALYZE_ADS_SHOWING_TIME": "Analyze time-based performance patterns and suggest bid timing optimizations.",
            "ANALYZE_DEVICE_PERFORMANCE_DETAILED": "Compare device performance and suggest bid adjustment strategies.",
            "ANALYZE_LOCATION_PERFORMANCE": "Analyze geographic performance and suggest location targeting optimizations.",
            "ANALYZE_LANDING_PAGE_MOBILE": "Evaluate mobile landing page performance and suggest mobile optimization strategies.",
            "OPTIMIZE_TCPA": "Provide Target CPA optimization recommendations based on performance data and campaign goals.",
            "OPTIMIZE_BUDGET_ALLOCATION": "Analyze budget performance and suggest allocation optimizations across campaigns.",
            "SUGGEST_NEGATIVE_KEYWORDS": "Identify poor-performing search terms and suggest negative keyword exclusions.",
            "ANALYZE_AUDIENCE": "Analyze audience size, overlap, and quality. Provide audience optimization recommendations.",
            "CHECK_CREATIVE_FATIGUE": "Analyze creative performance and suggest refresh strategies.",
            "ANALYZE_VIDEO_PERFORMANCE": "Evaluate video ad performance and suggest optimization strategies.",
            "COMPARE_PERFORMANCE": "Compare performance across time periods and identify trends and anomalies.",
            "OPTIMIZE_CAMPAIGN": "Provide campaign-level optimization recommendations.",
            "OPTIMIZE_ADSET": "Provide ad set-level optimization recommendations.",
            "OPTIMIZE_AD": "Provide ad-level optimization recommendations.",
            "ANALYZE_PLACEMENTS": "Analyze placement performance and suggest optimization strategies.",
            "ANALYZE_DEVICE_PERFORMANCE": "Compare device performance and suggest bid adjustments.",
            "ANALYZE_TIME_PERFORMANCE": "Analyze time-based performance patterns.",
            "ANALYZE_DEMOGRAPHICS": "Analyze demographic performance and suggest targeting optimizations.",
            "ANALYZE_COMPETITORS": "Analyze competitor strategies and provide competitive insights.",
            "TEST_CREATIVE_ELEMENTS": "Suggest creative testing strategies and frameworks.",
            "CHECK_TECHNICAL_COMPLIANCE": "Evaluate technical implementation and compliance status.",
            "ANALYZE_AUDIENCE_INSIGHTS": "Analyze audience insights and suggest optimization strategies.",
            "OPTIMIZE_BUDGETS": "Provide budget optimization recommendations."
        }
        
        action_context = action_contexts.get(action, "Provide comprehensive analysis and actionable recommendations.")
        base_prompt += f"\n\nSpecific focus for this action: {action_context}"
        
        return base_prompt
    
    def _parse_openai_response(self, content: str, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse OpenAI response and structure it into UI blocks"""
        try:
            # Try to parse JSON response
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_content = content[json_start:json_end].strip()
                parsed_response = json.loads(json_content)
            elif "{" in content and "}" in content:
                # Extract JSON from the response
                start = content.find("{")
                end = content.rfind("}") + 1
                json_content = content[start:end]
                parsed_response = json.loads(json_content)
            else:
                # Fallback to text-only response
                parsed_response = {
                    "blocks": [
                        {
                            "type": "text",
                            "content": content,
                            "style": "paragraph"
                        }
                    ]
                }
            
            # Ensure the response has the required structure
            if "blocks" not in parsed_response:
                parsed_response = {"blocks": [parsed_response]}
            
            # Add metadata
            parsed_response["action"] = action
            parsed_response["timestamp"] = timezone.now().isoformat()
            parsed_response["data_source"] = "openai"
            
            return parsed_response
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing OpenAI response: {e}")
            return self._generate_fallback_response(action, data)
    
    def _generate_fallback_response(self, action: str, data: Dict[str, Any], error_details: str = "") -> Dict[str, Any]:
        """Generate fallback response when OpenAI fails"""
        return {
            "blocks": [
                {
                    "type": "text",
                    "content": f"Analysis for {action}",
                    "style": "heading"
                },
                {
                    "type": "text",
                    "content": f"Unable to generate dynamic analysis at this time. Error: {error_details}",
                    "style": "paragraph"
                },
                {
                    "type": "text",
                    "content": "Please check your OpenAI API key and try again later.",
                    "style": "highlight"
                },
                {
                    "type": "actions",
                    "title": "Retry Analysis",
                    "items": [
                        {"id": "retry", "label": "Retry Analysis"}
                    ]
                }
            ],
            "action": action,
            "timestamp": timezone.now().isoformat(),
            "data_source": "fallback",
            "error_details": error_details
        }
    
    def generate_campaign_analysis(self, campaigns_data: List[Dict], action: str) -> Dict[str, Any]:
        """Generate campaign-specific analysis"""
        prompt = f"""
        Analyze the following Google Ads campaign data for action: {action}
        
        Campaign data: {json.dumps(campaigns_data, indent=2)}
        
        Provide insights on:
        - Performance metrics
        - Budget utilization
        - Optimization opportunities
        - Specific recommendations
        
        Structure as UI blocks with charts, tables, and actionable insights.
        """
        
        return self.generate_analysis_response(action, {"campaigns": campaigns_data})
    
    def generate_keyword_analysis(self, keywords_data: List[Dict], action: str) -> Dict[str, Any]:
        """Generate keyword-specific analysis"""
        prompt = f"""
        Analyze the following Google Ads keyword data for action: {action}
        
        Keyword data: {json.dumps(keywords_data, indent=2)}
        
        Provide insights on:
        - Performance trends
        - Optimization opportunities
        - Negative keyword suggestions
        - Bid strategy recommendations
        
        Structure as UI blocks with charts, tables, and actionable insights.
        """
        
        return self.generate_analysis_response(action, {"keywords": keywords_data})
    
    def generate_performance_analysis(self, performance_data: Dict, action: str) -> Dict[str, Any]:
        """Generate performance analysis"""
        prompt = f"""
        Analyze the following Google Ads performance data for action: {action}
        
        Performance data: {json.dumps(performance_data, indent=2)}
        
        Provide insights on:
        - Performance trends
        - Anomalies and issues
        - Optimization opportunities
        - Actionable recommendations
        
        Structure as UI blocks with charts, tables, and actionable insights.
        """
        
        return self.generate_analysis_response(action, performance_data)
    
    def generate_budget_analysis(self, budget_data: Dict, action: str) -> Dict[str, Any]:
        """Generate budget analysis"""
        prompt = f"""
        Analyze the following Google Ads budget data for action: {action}
        
        Budget data: {json.dumps(budget_data, indent=2)}
        
        Provide insights on:
        - Budget utilization
        - Allocation efficiency
        - Optimization opportunities
        - Budget strategy recommendations
        
        Structure as UI blocks with charts, tables, and actionable insights.
        """
        
        return self.generate_analysis_response(action, budget_data)

from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Any, Dict, Union
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import os
import logging

logger = logging.getLogger(__name__)

# Response schema for frontend UI blocks
class ChartBlock(BaseModel):
    type: Literal["chart"] = "chart"
    chart_type: Literal["pie", "bar", "line"]
    title: str
    labels: List[str]
    datasets: List[Dict[str, Any]]
    options: Optional[Dict[str, Any]] = None

class TableBlock(BaseModel):
    type: Literal["table"] = "table"
    title: str
    columns: List[str]
    rows: List[List[Any]]
    sortable: bool = True

class ListBlock(BaseModel):
    type: Literal["list"] = "list"
    style: Literal["dotted", "numbered", "bulleted"] = "dotted"
    title: Optional[str] = None
    items: List[str]

class ActionBlock(BaseModel):
    type: Literal["actions"] = "actions"
    title: Optional[str] = None
    items: List[Dict[str, str]]  # [{"id": "action_id", "label": "Action Label"}]

class TextBlock(BaseModel):
    type: Literal["text"] = "text"
    content: str
    style: Literal["paragraph", "heading", "highlight"] = "paragraph"

class ImageBlock(BaseModel):
    type: Literal["image"] = "image"
    url: str
    caption: Optional[str] = None
    alt_text: str

class MetricBlock(BaseModel):
    type: Literal["metric"] = "metric"
    title: str
    value: str
    change: Optional[str] = None
    trend: Optional[Literal["up", "down", "neutral"]] = None

class DigDeeperBlock(BaseModel):
    type: Literal["dig_deeper"] = "dig_deeper"
    title: str
    description: str
    action_id: str
    max_depth: int = 2
    current_depth: int = 1

class CreativeBlock(BaseModel):
    type: Literal["creative"] = "creative"
    title: str
    description: str
    template_type: str
    features: List[str]
    advantages: List[str]
    cta_suggestions: List[str]
    color_scheme: Optional[str] = None
    target_audience: Optional[str] = None

class WorkflowBlock(BaseModel):
    type: Literal["workflow"] = "workflow"
    title: str
    steps: List[Dict[str, str]]  # [{"step": "1", "action": "Action description"}]
    tools: List[str]
    tips: List[str]

# Union type for all block types
UIBlock = Union[TextBlock, ChartBlock, TableBlock, ListBlock, ActionBlock, ImageBlock, MetricBlock, DigDeeperBlock, CreativeBlock, WorkflowBlock]

class UIResponse(BaseModel):
    """Complete UI response with blocks"""
    blocks: List[UIBlock]
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    dig_deeper_context: Optional[Dict[str, Any]] = None

# Intent classification schema for Google Ads specific use cases
class GoogleAdsIntent(BaseModel):
    """Google Ads specific user intent classification"""
    action: Literal[
        "CAMPAIGN_SUMMARY_COMPARISON", "PERFORMANCE_SUMMARY", "TREND_ANALYSIS",
        "LISTING_ANALYSIS", "QUERY_WITHOUT_SOLUTION", "PIE_CHART_DISPLAY",
        "DUPLICATE_KEYWORDS_ANALYSIS", "DIG_DEEPER_ANALYSIS", "GENERATE_AD_COPIES",
        "GENERATE_CREATIVES", "POSTER_GENERATOR", "META_ADS_CREATIVES"
    ]
    confidence: float = Field(ge=0.0, le=1.0)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    requires_auth: bool = True
    dig_deeper_depth: int = Field(default=1, ge=1, le=3)

class LLMSetup:
    """LangChain LLM setup and configuration for Google Ads chatbot"""
    
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Initialize OpenAI model
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",  # Use gpt-4o-mini for cost efficiency
            temperature=0.1,
            openai_api_key=self.openai_api_key
        )
        
        # Create structured output parsers
        self.intent_parser = JsonOutputParser(pydantic_object=GoogleAdsIntent)
        self.ui_parser = JsonOutputParser(pydantic_object=UIResponse)
        
        # Google Ads specific intent prompt
        self.intent_prompt = ChatPromptTemplate.from_template("""
        You are an AI assistant that helps users analyze Google Ads campaigns and performance data, and generate ad copies and creatives.
        Classify the user's intent from their message.
        
        User message: {user_message}
        
        Available Google Ads analysis and creative actions:
        - CAMPAIGN_SUMMARY_COMPARISON: Compare campaigns, ad groups, adsets, ads for key metrics and sorting
        - PERFORMANCE_SUMMARY: Show performance summary in tables with key insights and recommendations
        - TREND_ANALYSIS: Display trends using line graphs or bar graphs for metrics like clicks, CPC, CTR
        - LISTING_ANALYSIS: Show listings in tables with additional key insights based on data
        - QUERY_WITHOUT_SOLUTION: Handle queries that have no solution by prompting user in right direction
        - PIE_CHART_DISPLAY: Display data in pie charts when requested
        - DUPLICATE_KEYWORDS_ANALYSIS: Analyze duplicate keywords across campaigns and provide consolidation recommendations
        - DIG_DEEPER_ANALYSIS: Handle follow-up analysis requests with hierarchical depth tracking
        - GENERATE_AD_COPIES: Generate multiple ad copy variations for Google Ads
        - GENERATE_CREATIVES: Generate creative ideas and designs for ads
        - POSTER_GENERATOR: Generate poster templates and design suggestions
        - META_ADS_CREATIVES: Generate creative ideas specifically for Meta/Facebook ads
        
        INTENT DETECTION RULES:
        - If user asks to "compare", "sort", "analyze" campaigns → CAMPAIGN_SUMMARY_COMPARISON
        - If user asks for "performance summary", "metrics", "ROAS" → PERFORMANCE_SUMMARY
        - If user asks for "trends", "daily trends", "graphs" → TREND_ANALYSIS
        - If user asks for "top 10", "list", "ranking" → LISTING_ANALYSIS
        - If user asks for "quality score", "account-level" metrics not available → QUERY_WITHOUT_SOLUTION
        - If user asks for "pie chart", "spend distribution" → PIE_CHART_DISPLAY
        - If user asks for "duplicate keywords", "consolidation" → DUPLICATE_KEYWORDS_ANALYSIS
        - If user says "dig deeper", "more details", "expand" → DIG_DEEPER_ANALYSIS
        - If user asks for "ad copies", "ad variations", "copywriting" → GENERATE_AD_COPIES
        - If user asks for "creative ideas", "design suggestions", "visual concepts" → GENERATE_CREATIVES
        - If user asks for "poster", "flyer", "banner" design → POSTER_GENERATOR
        - If user asks for "Facebook ads", "Meta ads", "social media creatives" → META_ADS_CREATIVES
        
        Return a JSON object with:
        - action: the detected Google Ads analysis or creative action
        - confidence: confidence score (0.0 to 1.0)
        - parameters: any relevant parameters from the user message
        - requires_auth: whether this action requires Google Ads authentication
        - dig_deeper_depth: current depth level (1-3, default 1)
        """)
        
        # Enhanced UI prompt for Google Ads specific responses including creative generation
        self.ui_prompt = ChatPromptTemplate.from_template("""
        You are an AI assistant that creates rich UI responses for a Google Ads analysis and creative generation application.
        Convert the given information into UI blocks that can be rendered in React.
        
        Information: {information}
        User query: {user_query}
        Dig deeper context: {dig_deeper_context}
        
        IMPORTANT: You MUST use ONLY these exact block types with correct structure:
        
        1. TEXT BLOCK (type: "text"):
           {{"type": "text", "content": "Your text here", "style": "paragraph"}}
           Styles: "paragraph", "heading", "highlight"
        
        2. CHART BLOCK (type: "chart"):
           {{"type": "chart", "chart_type": "bar", "title": "Chart Title", "labels": ["A", "B", "C"], "datasets": [{{"label": "Data", "data": [1, 2, 3]}}]}}
           Chart types: "pie", "bar", "line"
        
        3. TABLE BLOCK (type: "table"):
           {{"type": "table", "title": "Table Title", "columns": ["Col1", "Col2"], "rows": [["Row1", "Row2"]]}}
        
        4. LIST BLOCK (type: "list"):
           {{"type": "list", "style": "dotted", "items": ["Item 1", "Item 2"]}}
           Styles: "dotted", "numbered", "bulleted"
        
        5. ACTION BLOCK (type: "actions"):
           {{"type": "actions", "items": [{{"id": "action_id", "label": "Action Label"}}]}}
        
        6. METRIC BLOCK (type: "metric"):
           {{"type": "metric", "title": "Metric Title", "value": "100", "change": "+5%", "trend": "up"}}
           Trends: "up", "down", "neutral"
        
        7. DIG DEEPER BLOCK (type: "dig_deeper"):
           {{"type": "dig_deeper", "title": "Dig Deeper", "description": "Get more detailed analysis", "action_id": "dig_deeper_action", "max_depth": 2, "current_depth": 1}}
        
        8. CREATIVE BLOCK (type: "creative"):
           {{"type": "creative", "title": "Creative Title", "description": "Description", "template_type": "Type", "features": ["Feature 1", "Feature 2"], "advantages": ["Advantage 1"], "cta_suggestions": ["CTA 1"], "color_scheme": "Scheme", "target_audience": "Audience"}}
        
        9. WORKFLOW BLOCK (type: "workflow"):
           {{"type": "workflow", "title": "Workflow Title", "steps": [{{"step": "1", "action": "Action description"}}], "tools": ["Tool 1"], "tips": ["Tip 1"]}}
        
        GOOGLE ADS RESPONSE PATTERNS:
        
        For CAMPAIGN_SUMMARY_COMPARISON:
        - Start with TextBlock with summary and key insights
        - Add TableBlock with campaign comparison data
        - Include DigDeeperBlock for "Dig Deeper" action
        - Add ActionBlock with relevant next steps
        
        For PERFORMANCE_SUMMARY:
        - Start with TextBlock with key insights
        - Add TableBlock with performance metrics
        - Include recommendations in TextBlock
        - Add ActionBlock with optimization actions
        
        For TREND_ANALYSIS:
        - Start with TextBlock explaining trends
        - Add ChartBlock with line/bar charts
        - Include insights in TextBlock
        - Add ActionBlock for further analysis
        
        For LISTING_ANALYSIS:
        - Start with TextBlock with summary
        - Add TableBlock with listing data
        - Include key insights in TextBlock
        - Add ActionBlock for next steps
        
        For QUERY_WITHOUT_SOLUTION:
        - Start with TextBlock explaining the limitation
        - Provide alternative suggestions in TextBlock
        - Add ActionBlock with available alternatives
        
        For PIE_CHART_DISPLAY:
        - Start with TextBlock explaining the data
        - Add ChartBlock with pie chart
        - Include insights in TextBlock
        
        For DUPLICATE_KEYWORDS_ANALYSIS:
        - Start with TextBlock with summary
        - Add TableBlock with duplicate keywords
        - Include recommendations in TextBlock
        - Add ActionBlock for consolidation steps
        
        For GENERATE_AD_COPIES:
        - Start with TextBlock explaining the ad copy strategy
        - Add multiple TextBlocks for each ad copy variation
        - Include CreativeBlock for design suggestions
        - Add ActionBlock for next steps
        
        For GENERATE_CREATIVES:
        - Start with TextBlock with creative concept overview
        - Add multiple CreativeBlocks for different creative ideas
        - Include WorkflowBlock for implementation steps
        - Add ActionBlock for design tools
        
        For POSTER_GENERATOR:
        - Start with TextBlock with poster concept overview
        - Add multiple CreativeBlocks for poster templates
        - Include WorkflowBlock for creation steps
        - Add ActionBlock for design tools and next steps
        
        For META_ADS_CREATIVES:
        - Start with TextBlock with Meta ads strategy
        - Add multiple CreativeBlocks for different ad formats
        - Include WorkflowBlock for Meta ads implementation
        - Add ActionBlock for Meta ads tools
        
        CRITICAL RULES:
        - Use EXACTLY these block types and field names
        - Always include a DigDeeperBlock for analysis responses (max_depth: 2, current_depth: 1)
        - For charts, use "chart_type" not "kind" or other variations
        - For tables, use "columns" and "rows" arrays
        - Limit DigDeeperBlock to maximum depth of 2 levels
        - For creative generation, always include WorkflowBlock with implementation steps
        - Include multiple CreativeBlocks to show variety and options
        
        Return a JSON object with a "blocks" array containing the UI blocks.
        """)
    
    def classify_intent(self, user_message: str) -> GoogleAdsIntent:
        """Classify user intent from message for Google Ads analysis and creative generation"""
        try:
            chain = self.intent_prompt | self.llm | self.intent_parser
            result = chain.invoke({"user_message": user_message})
            return GoogleAdsIntent(**result)
        except Exception as e:
            logger.error(f"Error classifying intent: {e}")
            # Fallback to default intent
            return GoogleAdsIntent(
                action="CAMPAIGN_SUMMARY_COMPARISON",
                confidence=0.5,
                parameters={},
                requires_auth=False,
                dig_deeper_depth=1
            )
    
    def generate_ui_response(self, information: Dict[str, Any], user_query: str, dig_deeper_context: Dict[str, Any] = None) -> UIResponse:
        """Generate UI response blocks from information with dig deeper and creative support"""
        try:
            chain = self.ui_prompt | self.llm | self.ui_parser
            result = chain.invoke({
                "information": str(information),
                "user_query": user_query,
                "dig_deeper_context": str(dig_deeper_context) if dig_deeper_context else "None"
            })
            return UIResponse(**result)
        except Exception as e:
            logger.error(f"Error generating UI response: {e}")
            # Fallback to simple text response with proper error handling
            try:
                # Try to create a structured response from the information
                blocks = []
                
                # Add main text block
                blocks.append(TextBlock(
                    content=f"Here's what I found: {str(information)}",
                    style="paragraph"
                ))
                
                # If we have campaign data, try to create a table
                if 'campaigns' in information and isinstance(information['campaigns'], list):
                    if information['campaigns'] and len(information['campaigns']) > 0:
                        # Create table from campaign data
                        sample_campaign = information['campaigns'][0]
                        columns = list(sample_campaign.keys())
                        rows = []
                        for campaign in information['campaigns'][:5]:  # Limit to 5 rows
                            row = [str(campaign.get(col, '')) for col in columns]
                            rows.append(row)
                        
                        blocks.append(TableBlock(
                            title="Campaign Data",
                            columns=columns,
                            rows=rows
                        ))
                
                # Add Dig Deeper block
                blocks.append(DigDeeperBlock(
                    title="Dig Deeper",
                    description="Get more detailed analysis of this data",
                    action_id="dig_deeper_analysis",
                    max_depth=2,
                    current_depth=1
                ))
                
                # Add action buttons for common next steps
                blocks.append(ActionBlock(
                    items=[
                        {"id": "refresh_data", "label": "Refresh Data"},
                        {"id": "create_campaign", "label": "Create Campaign"},
                        {"id": "view_analytics", "label": "View Analytics"},
                        {"id": "create_ad", "label": "Create Ad"},
                        {"id": "create_adgroup", "label": "Create Ad Group"},
                        {"id": "get_campaigns", "label": "View Campaigns"},
                        {"id": "get_ads", "label": "View Ads"},
                        {"id": "get_creative_suggestions", "label": "Get Creative Ideas"},
                        {"id": "generate_images", "label": "Generate Images"},
                        {"id": "optimize_campaign", "label": "Optimize Campaign"},
                        {"id": "set_budget", "label": "Set Budget"},
                        {"id": "get_performance", "label": "View Performance"},
                        {"id": "generate_ad_copies", "label": "Generate Ad Copies"},
                        {"id": "create_posters", "label": "Create Posters"},
                        {"id": "meta_ads_creatives", "label": "Meta Ads Creatives"},
                        {"id": "retry_action", "label": "Retry Action"},
                        {"id": "contact_support", "label": "Contact Support"}
                    ]
                ))
                
                return UIResponse(blocks=blocks, dig_deeper_context=dig_deeper_context)
                
            except Exception as fallback_error:
                logger.error(f"Fallback response generation failed: {fallback_error}")
                # Ultimate fallback - just text
                return UIResponse(
                    blocks=[
                        TextBlock(
                            content=f"Here's what I found: {str(information)}",
                            style="paragraph"
                        )
                    ],
                    dig_deeper_context=dig_deeper_context
                )

# Initialize LLM setup
try:
    llm_setup = LLMSetup()
except ValueError as e:
    logger.warning(f"LLM setup failed: {e}")
    llm_setup = None

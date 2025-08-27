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
    items: List[Dict[str, str]]  # [{"id": "create_campaign", "label": "Create Campaign"}]

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

# Union type for all block types
UIBlock = Union[TextBlock, ChartBlock, TableBlock, ListBlock, ActionBlock, ImageBlock, MetricBlock]

class UIResponse(BaseModel):
    """Complete UI response with blocks"""
    blocks: List[UIBlock]
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

# Intent classification schema
class Intent(BaseModel):
    """User intent classification"""
    action: Literal[
        "GET_OVERVIEW", "GET_CAMPAIGNS", "CREATE_CAMPAIGN", "UPDATE_CAMPAIGN",
        "GET_ADGROUPS", "GET_ADS", "CREATE_ADGROUP", "CREATE_AD",
        "SEARCH_KB", "SEARCH_DB", "GET_ANALYTICS", "GET_BUDGETS",
        "PAUSE_CAMPAIGN", "RESUME_CAMPAIGN", "DELETE_CAMPAIGN",
        "GET_PERFORMANCE", "GET_KEYWORDS", "ADD_KB_DOCUMENT",
        "GENERATE_IMAGES", "CREATE_DYNAMIC_AD", "GET_CREATIVE_SUGGESTIONS"
    ]
    confidence: float = Field(ge=0.0, le=1.0)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    requires_auth: bool = True

class LLMSetup:
    """LangChain LLM setup and configuration"""
    
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
        self.intent_parser = JsonOutputParser(pydantic_object=Intent)
        self.ui_parser = JsonOutputParser(pydantic_object=UIResponse)
        
        # System prompts
        self.intent_prompt = ChatPromptTemplate.from_template("""
        You are an AI assistant that helps users manage Google Ads campaigns. 
        Classify the user's intent from their message.
        
        User message: {user_message}
        
        Available actions:
        - GET_OVERVIEW: Get account overview and summary
        - GET_CAMPAIGNS: Retrieve campaign information
        - CREATE_CAMPAIGN: Create new campaigns
        - UPDATE_CAMPAIGN: Modify existing campaigns
        - GET_ADGROUPS: Get ad group information
        - GET_ADS: Get ad information
        - CREATE_ADGROUP: Create new ad groups
        - CREATE_AD: Create new ads (including with images)
        - GENERATE_IMAGES: Generate AI images for products using DALL-E
        - CREATE_DYNAMIC_AD: Create ads with AI-generated creative suggestions
        - GET_CREATIVE_SUGGESTIONS: Get AI-powered creative suggestions for ads
        - SEARCH_KB: Search company knowledge base
        - SEARCH_DB: Search local database
        - GET_ANALYTICS: Get performance analytics
        - GET_BUDGETS: Get budget information
        - PAUSE_CAMPAIGN: Pause campaigns
        - RESUME_CAMPAIGN: Resume campaigns
        - DELETE_CAMPAIGN: Delete campaigns
        - GET_PERFORMANCE: Get performance data
        - GET_KEYWORDS: Get keyword information
        - ADD_KB_DOCUMENT: Add document to knowledge base
        
        IMPORTANT: 
        - If user mentions "images", "photos", "pictures", "visuals" → use GENERATE_IMAGES
        - If user mentions "creative", "suggestions", "ideas" → use GET_CREATIVE_SUGGESTIONS
        - If user mentions "create ad" with images → use CREATE_AD
        - If user mentions "share images" → use GENERATE_IMAGES
        
        Return a JSON object with:
        - action: the detected action
        - confidence: confidence score (0.0 to 1.0)
        - parameters: any relevant parameters from the user message
        - requires_auth: whether this action requires Google Ads authentication
        """)
        
        self.ui_prompt = ChatPromptTemplate.from_template("""
        You are an AI assistant that creates rich UI responses for a Google Ads management application.
        Convert the given information into UI blocks that can be rendered in React.
        
        Information: {information}
        User query: {user_query}
        
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
        
        CRITICAL RULES:
        - Use EXACTLY these block types and field names
        - Never use types like "list", "button", "metrics", "barChart", "lineChart"
        - Always include required fields for each block type
        - For charts, use "chart_type" not "kind" or other variations
        - For tables, use "columns" and "rows" arrays
        
        Return a JSON object with a "blocks" array containing the UI blocks.
        """)
    
    def classify_intent(self, user_message: str) -> Intent:
        """Classify user intent from message"""
        try:
            chain = self.intent_prompt | self.llm | self.intent_parser
            result = chain.invoke({"user_message": user_message})
            return Intent(**result)
        except Exception as e:
            logger.error(f"Error classifying intent: {e}")
            # Fallback to default intent
            return Intent(
                action="GET_OVERVIEW",
                confidence=0.5,
                parameters={},
                requires_auth=False
            )
    
    def generate_ui_response(self, information: Dict[str, Any], user_query: str) -> UIResponse:
        """Generate UI response blocks from information"""
        try:
            chain = self.ui_prompt | self.llm | self.ui_parser
            result = chain.invoke({
                "information": str(information),
                "user_query": user_query
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
                        {"id": "retry_action", "label": "Retry Action"},
                        {"id": "contact_support", "label": "Contact Support"}
                    ]
                ))
                
                return UIResponse(blocks=blocks)
                
            except Exception as fallback_error:
                logger.error(f"Fallback response generation failed: {fallback_error}")
                # Ultimate fallback - just text
                return UIResponse(
                    blocks=[
                        TextBlock(
                            content=f"Here's what I found: {str(information)}",
                            style="paragraph"
                        )
                    ]
                )

# Initialize LLM setup
try:
    llm_setup = LLMSetup()
except ValueError as e:
    logger.warning(f"LLM setup failed: {e}")
    llm_setup = None

from typing import Dict, Any, List, Optional
from django.contrib.auth.models import User
from django.utils import timezone
from .models import (
    ChatSession, ChatMessage, UserIntent, AIToolExecution,
    GoogleAdsAccount, GoogleAdsCampaign, GoogleAdsAdGroup
)
from .llm_setup import llm_setup
from .langchain_tools import get_all_tools
import json
import logging
from datetime import datetime, date
from decimal import Decimal

import os
import requests

logger = logging.getLogger(__name__)

class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle date and decimal objects"""
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

class ImageGenerator:
    """Handles image generation using OpenAI DALL-E API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/images/generations"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_image(self, prompt: str, size: str = "1024x1024", quality: str = "standard", style: str = "vivid") -> Optional[str]:
        """Generate an image using DALL-E and return the URL"""
        try:
            payload = {
                "model": "dall-e-3",
                "prompt": prompt,
                "size": size,
                "quality": quality,
                "style": style,
                "n": 1
            }
            
            response = requests.post(self.base_url, headers=self.headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            if result.get("data") and len(result["data"]) > 0:
                image_url = result["data"][0]["url"]
                return image_url
            
            return None
            
        except Exception as e:
            print(f"❌ Error generating image: {e}")
            return None
    
    def generate_poster_image(self, title: str, description: str, template_type: str, color_scheme: str, target_audience: str) -> Optional[str]:
        """Generate a poster image based on creative specifications"""
        prompt = f"""Create a professional poster design for "{title}". 
        
        Description: {description}
        Template Type: {template_type}
        Color Scheme: {color_scheme}
        Target Audience: {target_audience}
        
        Style: Modern, professional, educational poster with clean typography, balanced layout, and visual hierarchy. 
        Include placeholder elements for text and imagery that would be added later.
        Make it suitable for printing and digital use."""
        
        return self.generate_image(prompt, size="1024x1024", quality="standard", style="vivid")

class ChatService:
    """Enhanced chat service with image generation for creative content"""
    
    def __init__(self, user: User):
        self.user = user
        self.session = None
        self.memory_window = 10  # Remember last 10 messages
        self.image_generator = None
        self.initialize_image_generator()
    
    def initialize_image_generator(self):
        """Initialize the image generator with OpenAI API key"""
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            try:
                self.image_generator = ImageGenerator(openai_api_key)
                print("✅ Image generator initialized successfully")
            except Exception as e:
                print(f"❌ Error initializing image generator: {e}")
                self.image_generator = None
        else:
            print("⚠️  OPENAI_API_KEY not found - image generation disabled")
    
    def enhance_creative_blocks_with_images(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add image URLs to creative blocks in the response"""
        if not self.image_generator:
            print("⚠️  Image generator not available - skipping image generation")
            return response_data
        
        try:
            if "response" in response_data and "blocks" in response_data["response"]:
                blocks = response_data["response"]["blocks"]
                
                for block in blocks:
                    if block.get("type") == "creative":
                        print(f"🎨 Generating image for: {block.get('title', 'Unknown')}")
                        
                        # Generate image for this creative block
                        image_url = self.image_generator.generate_poster_image(
                            title=block.get("title", ""),
                            description=block.get("description", ""),
                            template_type=block.get("template_type", ""),
                            color_scheme=block.get("color_scheme", ""),
                            target_audience=block.get("target_audience", "")
                        )
                        
                        if image_url:
                            block["image_url"] = image_url
                            print(f"✅ Image generated: {image_url[:50]}...")
                        else:
                            block["image_url"] = None
                            print(f"⚠️  Failed to generate image for: {block.get('title')}")
            
            return response_data
            
        except Exception as e:
            print(f"❌ Error enhancing creative blocks with images: {e}")
            return response_data
    
    def start_session(self, title: str = None) -> str:
        """Start a new chat session"""
        self.session = ChatSession.objects.create(
            user=self.user,
            title=title or f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        return str(self.session.id)
    
    def load_session(self, session_id: str) -> bool:
        """Load an existing chat session"""
        try:
            self.session = ChatSession.objects.get(id=session_id, user=self.user)
            return True
        except ChatSession.DoesNotExist:
            return False
    
    def get_chat_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get chat history for current session"""
        if not self.session:
            return []
        
        messages = ChatMessage.objects.filter(session=self.session)
        if limit:
            messages = messages.order_by('-created_at')[:limit]
        else:
            messages = messages.order_by('created_at')
        
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "metadata": msg.metadata,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]
    
    def add_message(self, role: str, content: str, metadata: Dict = None) -> ChatMessage:
        """Add a message to the current session"""
        if not self.session:
            raise ValueError("No active session")
        
        return ChatMessage.objects.create(
            session=self.session,
            role=role,
            content=content,
            metadata=metadata or {}
        )
    
    def get_context_messages(self) -> List[Dict[str, Any]]:
        """Get recent messages for context (memory)"""
        if not self.session:
            return []
        
        messages = ChatMessage.objects.filter(
            session=self.session
        ).order_by('-created_at')[:self.memory_window]
        
        # Reverse to get chronological order
        messages = list(reversed(messages))
        
        context = []
        for msg in messages:
            if msg.role in ['user', 'assistant']:
                context.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        return context
    
    def process_message(self, user_message: str) -> Dict[str, Any]:
        """Process user message and generate response"""
        try:
            # Add user message to chat
            self.add_message("user", user_message)
            
            # Check if LLM is available
            if not llm_setup:
                return {
                    "success": False,
                    "error": "AI service not available. Please check OpenAI API configuration.",
                    "blocks": [
                        {
                            "type": "text",
                            "content": "AI service is currently unavailable. Please check your OpenAI API configuration.",
                            "style": "highlight"
                        }
                    ]
                }
            
            # Classify intent
            intent = llm_setup.classify_intent(user_message)
            
            # Log intent for fine-tuning
            UserIntent.objects.create(
                user=self.user,
                user_query=user_message,
                detected_intent=intent.action,
                intent_confidence=intent.confidence,
                tool_calls=intent.parameters
            )
            
            # Execute tools based on intent
            tool_results = self._execute_tools(intent)
            
            # Generate UI response
            ui_response = llm_setup.generate_ui_response(tool_results, user_message)
            
            # Check if this is a creative content request that needs image generation
            creative_actions = ["POSTER_GENERATOR", "GENERATE_CREATIVE", "GENERATE_AD_COPIES", "GENERATE_CREATIVES", "META_ADS_CREATIVES"]
            
            if intent.action in creative_actions:
                print(f"🎨 Creative content detected ({intent.action}) - enhancing with images...")
                
                # Convert UI response to dict for image enhancement
                ui_response_dict = ui_response.dict()
                
                # Enhance creative blocks with images
                enhanced_response = self.enhance_creative_blocks_with_images({
                    "response": ui_response_dict
                })
                
                # Update the UI response with enhanced data
                ui_response_dict = enhanced_response["response"]
                
                # Add assistant response to chat with enhanced data
                response_content = json.dumps(ui_response_dict, indent=2, cls=CustomJSONEncoder)
                self.add_message("assistant", response_content, {
                    "intent": intent.dict(),
                    "tool_results": tool_results,
                    "ui_blocks": ui_response_dict
                })
                
                # Update session
                self.session.updated_at = timezone.now()
                self.session.save()
                
                return {
                    "success": True,
                    "session_id": str(self.session.id),
                    "response": ui_response_dict,
                    "intent": intent.dict()
                }
            else:
                # Regular processing without image generation
                # Add assistant response to chat
                response_content = json.dumps(ui_response.dict(), indent=2, cls=CustomJSONEncoder)
                self.add_message("assistant", response_content, {
                    "intent": intent.dict(),
                    "tool_results": tool_results,
                    "ui_blocks": ui_response.dict()
                })
                
                # Update session
                self.session.updated_at = timezone.now()
                self.session.save()
                
                return {
                    "success": True,
                    "session_id": str(self.session.id),
                    "response": ui_response.dict(),
                    "intent": intent.dict()
                }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            error_response = {
                "success": False,
                "error": str(e),
                "blocks": [
                    {
                        "type": "text",
                        "content": f"I encountered an error: {str(e)}",
                        "style": "highlight"
                    }
                ]
            }
            
            # Log error message
            if self.session:
                self.add_message("assistant", json.dumps(error_response, cls=CustomJSONEncoder), {"error": True})
            
            return error_response
    
    def _execute_tools(self, intent: Any) -> Dict[str, Any]:
        """Execute tools based on detected intent"""
        results = {}
        
        try:
            if intent.action == "GET_OVERVIEW":
                # Get account summary
                from .langchain_tools import DatabaseTools
                db_tools = DatabaseTools(self.user, str(self.session.id) if self.session else None)
                results["account_summary"] = db_tools.get_account_summary()
                
            elif intent.action == "GET_CAMPAIGNS":
                # Get campaigns from Google Ads
                from .langchain_tools import GoogleAdsTools
                ga_tools = GoogleAdsTools(self.user, str(self.session.id) if self.session else None)
                
                # Get user's Google Ads accounts
                accounts = GoogleAdsAccount.objects.filter(
                    user=self.user,
                    is_active=True
                )
                
                if accounts.exists():
                    account = accounts.first()
                    results["campaigns"] = ga_tools.get_campaigns(
                        status=intent.parameters.get("status", "ENABLED"),
                        limit=intent.parameters.get("limit", 50)
                    )
                else:
                    results["error"] = "No Google Ads accounts connected"
                    
            elif intent.action == "CREATE_CAMPAIGN":
                # Create new campaign
                from .langchain_tools import GoogleAdsTools
                ga_tools = GoogleAdsTools(self.user, str(self.session.id) if self.session else None)
                
                if "name" in intent.parameters and "budget_amount_micros" in intent.parameters:
                    # User provided campaign details, create the campaign
                    try:
                        results["campaign_creation"] = ga_tools.create_campaign(
                            name=intent.parameters["name"],
                            budget_amount_micros=intent.parameters["budget_amount_micros"],
                            channel_type=intent.parameters.get("channel_type", "SEARCH"),
                            status=intent.parameters.get("status", "PAUSED")
                        )
                        results["success_message"] = f"Campaign '{intent.parameters['name']}' created successfully!"
                    except Exception as e:
                        results["error"] = f"Failed to create campaign: {str(e)}"
                else:
                    # User wants to create a campaign but hasn't provided details yet
                    # Show campaign creation form
                    results["show_campaign_form"] = True
                    results["campaign_form"] = {
                        "title": "Create New Campaign",
                        "description": "Please provide the following details to create your campaign:",
                        "fields": [
                            {
                                "name": "name",
                                "label": "Campaign Name",
                                "type": "text",
                                "required": True,
                                "placeholder": "e.g., Summer Sale Campaign"
                            },
                            {
                                "name": "budget_amount_micros",
                                "label": "Daily Budget (USD)",
                                "type": "number",
                                "required": True,
                                "placeholder": "25.00",
                                "step": "0.01",
                                "min": "0.01"
                            },
                            {
                                "name": "channel_type",
                                "label": "Campaign Type",
                                "type": "select",
                                "required": False,
                                "options": [
                                    {"value": "SEARCH", "label": "Search"},
                                    {"value": "DISPLAY", "label": "Display"},
                                    {"value": "VIDEO", "label": "Video"},
                                    {"value": "SHOPPING", "label": "Shopping"},
                                    {"value": "PERFORMANCE_MAX", "label": "Performance Max"}
                                ],
                                "default": "SEARCH"
                            },
                            {
                                "name": "status",
                                "label": "Initial Status",
                                "type": "select",
                                "required": False,
                                "options": [
                                    {"value": "PAUSED", "label": "Paused (Recommended)"},
                                    {"value": "ENABLED", "label": "Enabled"}
                                ],
                                "default": "PAUSED"
                            }
                        ]
                    }
                    results["message"] = "I'll help you create a new campaign. Please fill out the form below with your campaign details."
                    
            elif intent.action == "SEARCH_KB":
                # Search knowledge base
                from .langchain_tools import KnowledgeBaseTools
                kb_tools = KnowledgeBaseTools(self.user, str(self.session.id) if self.session else None)
                
                company_id = intent.parameters.get("company_id", 1)  # Default company ID
                query = intent.parameters.get("query", user_message)
                
                results["kb_search"] = kb_tools.search_kb(query, company_id)
                
            elif intent.action == "SEARCH_DB":
                # Search local database
                from .langchain_tools import DatabaseTools
                db_tools = DatabaseTools(self.user, str(self.session.id) if self.session else None)
                
                query = intent.parameters.get("query", "")
                results["db_search"] = db_tools.search_campaigns_db(query)
                
            elif intent.action == "GET_ANALYTICS":
                # Get performance analytics
                from .langchain_tools import AnalyticsTools
                analytics_tools = AnalyticsTools(self.user, str(self.session.id) if self.session else None)
                
                days = intent.parameters.get("days", 30)
                results["performance_report"] = analytics_tools.generate_performance_report(days)
                
            elif intent.action == "GET_BUDGETS":
                # Get budget insights
                from .langchain_tools import AnalyticsTools
                analytics_tools = AnalyticsTools(self.user, str(self.session.id) if self.session else None)
                
                results["budget_insights"] = analytics_tools.get_budget_insights()
                
            elif intent.action == "PAUSE_CAMPAIGN":
                # Pause campaign
                from .langchain_tools import GoogleAdsTools
                ga_tools = GoogleAdsTools(self.user, str(self.session.id) if self.session else None)
                
                if "campaign_id" in intent.parameters:
                    results["pause_result"] = ga_tools.pause_campaign(
                        intent.parameters["campaign_id"]
                    )
                else:
                    results["error"] = "Missing campaign ID"
                    
            elif intent.action == "RESUME_CAMPAIGN":
                # Resume campaign
                from .langchain_tools import GoogleAdsTools
                ga_tools = GoogleAdsTools(self.user, str(self.session.id) if self.session else None)
                
                if "campaign_id" in intent.parameters:
                    results["resume_result"] = ga_tools.resume_campaign(
                        intent.parameters["campaign_id"]
                    )
                else:
                    results["error"] = "Missing campaign ID"
                    
            elif intent.action == "GET_PERFORMANCE":
                # Get campaign performance
                from .langchain_tools import DatabaseTools
                db_tools = DatabaseTools(self.user, str(self.session.id) if self.session else None)
                
                campaign_id = intent.parameters.get("campaign_id")
                days = intent.parameters.get("days", 30)
                results["performance_data"] = db_tools.get_campaign_performance(campaign_id, days)
                
            elif intent.action == "GET_KEYWORDS":
                # Get keyword information
                from .langchain_tools import DatabaseTools
                db_tools = DatabaseTools(self.user, str(self.session.id) if self.session else None)
                
                query = intent.parameters.get("query", "")
                status = intent.parameters.get("status")
                results["keywords"] = db_tools.search_keywords(query, status)
                
            elif intent.action == "ADD_KB_DOCUMENT":
                # Add document to knowledge base
                from .langchain_tools import KnowledgeBaseTools
                kb_tools = KnowledgeBaseTools(self.user, str(self.session.id) if self.session else None)
                
                if all(key in intent.parameters for key in ["title", "content"]):
                    results["kb_document"] = kb_tools.add_kb_document(
                        company_id=intent.parameters.get("company_id", 1),
                        title=intent.parameters["title"],
                        content=intent.parameters["content"],
                        url=intent.parameters.get("url"),
                        document_type=intent.parameters.get("document_type", "general")
                    )
                else:
                    results["error"] = "Missing required parameters for document creation"
            
            # New comprehensive analysis actions
            elif intent.action == "ANALYZE_AUDIENCE":
                from .analysis_service import GoogleAdsAnalysisService
                analysis_service = GoogleAdsAnalysisService(self.user)
                
                results["audience_analysis"] = analysis_service.analyze_audience()
                
            elif intent.action == "OPTIMIZE_CAMPAIGN":
                from .analysis_service import GoogleAdsAnalysisService
                analysis_service = GoogleAdsAnalysisService(self.user)
                
                campaign_id = intent.parameters.get("campaign_id")
                results["optimization_suggestions"] = analysis_service.optimize_campaign(campaign_id)
                
            elif intent.action == "CHECK_CAMPAIGN_CONSISTENCY":
                from .analysis_service import GoogleAdsAnalysisService
                analysis_service = GoogleAdsAnalysisService(self.user)
                
                results["consistency_check"] = analysis_service.check_campaign_consistency()
                
            elif intent.action == "CHECK_SITELINKS":
                from .analysis_service import GoogleAdsAnalysisService
                analysis_service = GoogleAdsAnalysisService(self.user)
                
                results["sitelinks_analysis"] = analysis_service.check_sitelinks()
                
            # Google Ads analysis tools
            elif intent.action == "CAMPAIGN_SUMMARY_COMPARISON":
                from .google_ads_analysis_tools import GoogleAdsAnalysisTools
                analysis_tools = GoogleAdsAnalysisTools(self.user, str(self.session.id) if self.session else None)
                
                sort_by = intent.parameters.get("sort_by", "spend")
                limit = intent.parameters.get("limit", 10)
                results.update(analysis_tools.analyze_campaign_summary_comparison(sort_by, limit))
                
            elif intent.action == "PERFORMANCE_SUMMARY":
                from .google_ads_analysis_tools import GoogleAdsAnalysisTools
                analysis_tools = GoogleAdsAnalysisTools(self.user, str(self.session.id) if self.session else None)
                
                days = intent.parameters.get("days", 30)
                results.update(analysis_tools.analyze_performance_summary(days))
                
            elif intent.action == "TREND_ANALYSIS":
                from .google_ads_analysis_tools import GoogleAdsAnalysisTools
                analysis_tools = GoogleAdsAnalysisTools(self.user, str(self.session.id) if self.session else None)
                
                metric = intent.parameters.get("metric", "clicks")
                days = intent.parameters.get("days", 30)
                results.update(analysis_tools.analyze_trends(metric, days))
                
            elif intent.action == "LISTING_ANALYSIS":
                from .google_ads_analysis_tools import GoogleAdsAnalysisTools
                analysis_tools = GoogleAdsAnalysisTools(self.user, str(self.session.id) if self.session else None)
                
                listing_type = intent.parameters.get("listing_type", "campaigns")
                limit = intent.parameters.get("limit", 10)
                sort_by = intent.parameters.get("sort_by", "conversions")
                days = intent.parameters.get("days", 14)
                results.update(analysis_tools.analyze_listing_performance(listing_type, limit, sort_by, days))
                
            elif intent.action == "QUERY_WITHOUT_SOLUTION":
                from .google_ads_analysis_tools import GoogleAdsAnalysisTools
                analysis_tools = GoogleAdsAnalysisTools(self.user, str(self.session.id) if self.session else None)
                
                query = intent.parameters.get("query", "")
                results.update(analysis_tools.handle_query_without_solution(query))
                
            elif intent.action == "PIE_CHART_DISPLAY":
                from .google_ads_analysis_tools import GoogleAdsAnalysisTools
                analysis_tools = GoogleAdsAnalysisTools(self.user, str(self.session.id) if self.session else None)
                
                chart_type = intent.parameters.get("chart_type", "spend")
                days = intent.parameters.get("days", 30)
                results.update(analysis_tools.analyze_pie_chart_data(chart_type, days))
                
            elif intent.action == "DUPLICATE_KEYWORDS_ANALYSIS":
                from .google_ads_analysis_tools import GoogleAdsAnalysisTools
                analysis_tools = GoogleAdsAnalysisTools(self.user, str(self.session.id) if self.session else None)
                
                days = intent.parameters.get("days", 7)
                results.update(analysis_tools.analyze_duplicate_keywords(days))
                
            elif intent.action == "DIG_DEEPER_ANALYSIS":
                from .google_ads_analysis_tools import GoogleAdsAnalysisTools
                analysis_tools = GoogleAdsAnalysisTools(self.user, str(self.session.id) if self.session else None)
                
                base_analysis = intent.parameters.get("base_analysis", {})
                depth = intent.parameters.get("depth", 1)
                results.update(analysis_tools.dig_deeper_analysis(base_analysis, depth))
                
            # Creative generation tools
            elif intent.action == "GENERATE_AD_COPIES":
                from .google_ads_analysis_tools import GoogleAdsAnalysisTools
                analysis_tools = GoogleAdsAnalysisTools(self.user, str(self.session.id) if self.session else None)
                
                context = intent.parameters.get("context", "")
                platform = intent.parameters.get("platform", "google_ads")
                variations = intent.parameters.get("variations", 4)
                results.update(analysis_tools.generate_ad_copies(context, platform, variations))
                
            elif intent.action == "GENERATE_CREATIVES":
                from .google_ads_analysis_tools import GoogleAdsAnalysisTools
                analysis_tools = GoogleAdsAnalysisTools(self.user, str(self.session.id) if self.session else None)
                
                context = intent.parameters.get("context", "")
                results.update(analysis_tools.generate_ad_copies(context, "google_ads", 4))
                
            elif intent.action == "POSTER_GENERATOR":
                from .google_ads_analysis_tools import GoogleAdsAnalysisTools
                analysis_tools = GoogleAdsAnalysisTools(self.user, str(self.session.id) if self.session else None)
                
                context = intent.parameters.get("context", "")
                target_audience = intent.parameters.get("target_audience", "students")
                results.update(analysis_tools.generate_poster_templates(context, target_audience))
                
            elif intent.action == "META_ADS_CREATIVES":
                from .google_ads_analysis_tools import GoogleAdsAnalysisTools
                analysis_tools = GoogleAdsAnalysisTools(self.user, str(self.session.id) if self.session else None)
                
                context = intent.parameters.get("context", "")
                ad_format = intent.parameters.get("ad_format", "all")
                results.update(analysis_tools.generate_meta_ads_creatives(context, ad_format))
                
            elif intent.action == "CHECK_CREATIVE_FATIGUE":
                from .analysis_service import GoogleAdsAnalysisService
                analysis_service = GoogleAdsAnalysisService(self.user)
                account_id = intent.parameters.get("account_id")
                results["creative_fatigue_analysis"] = analysis_service.check_creative_fatigue(account_id)
                
            elif intent.action == "ANALYZE_VIDEO_PERFORMANCE":
                from .analysis_service import GoogleAdsAnalysisService
                analysis_service = GoogleAdsAnalysisService(self.user)
                account_id = intent.parameters.get("account_id")
                results["video_performance_analysis"] = analysis_service.analyze_video_performance(account_id)
                
            elif intent.action == "COMPARE_PERFORMANCE":
                from .analysis_service import GoogleAdsAnalysisService
                analysis_service = GoogleAdsAnalysisService(self.user)
                comparison_type = intent.parameters.get("comparison_type", "M1_M2")
                account_id = intent.parameters.get("account_id")
                results["performance_comparison"] = analysis_service.compare_performance(comparison_type, account_id)
                
            elif intent.action == "OPTIMIZE_ADSET":
                # Use RAG system for ad set optimization queries
                from .rag_service import GoogleAdsRAGService
                from .data_service import GoogleAdsDataService
                
                # Get user's Google Ads data for context
                data_service = GoogleAdsDataService(self.user)
                account_data = data_service.get_campaign_data()
                
                # Initialize RAG service
                rag_service = GoogleAdsRAGService(self.user)
                
                # Get hybrid response using smart context selection
                rag_response = rag_service.get_hybrid_response("how to optimize Google Ads ad sets", account_data)
                
                # Store the RAG-enhanced response
                results["rag_enhanced_response"] = rag_response
                results["response_type"] = rag_response.get("response_type", "unknown")
                results["rag_metadata"] = rag_response.get("rag_metadata", {})
                
            elif intent.action == "OPTIMIZE_AD":
                # Use RAG system for ad optimization queries
                from .rag_service import GoogleAdsRAGService
                from .data_service import GoogleAdsDataService
                
                # Get user's Google Ads data for context
                data_service = GoogleAdsDataService(self.user)
                account_data = data_service.get_campaign_data()
                
                # Initialize RAG service
                rag_service = GoogleAdsRAGService(self.user)
                
                # Get hybrid response using smart context selection
                rag_response = rag_service.get_hybrid_response("how to optimize Google Ads ads", account_data)
                
                # Store the RAG-enhanced response
                results["rag_enhanced_response"] = rag_response
                results["response_type"] = rag_response.get("response_type", "unknown")
                results["rag_metadata"] = rag_response.get("rag_metadata", {})
                
            elif intent.action == "ANALYZE_PLACEMENTS":
                from .analysis_service import GoogleAdsAnalysisService
                analysis_service = GoogleAdsAnalysisService(self.user)
                account_id = intent.parameters.get("account_id")
                results["placement_analysis"] = analysis_service.analyze_placements(account_id)
                
            elif intent.action == "ANALYZE_DEVICE_PERFORMANCE":
                from .analysis_service import GoogleAdsAnalysisService
                analysis_service = GoogleAdsAnalysisService(self.user)
                account_id = intent.parameters.get("account_id")
                results["device_performance_analysis"] = analysis_service.analyze_device_performance(account_id)
                
            elif intent.action == "ANALYZE_TIME_PERFORMANCE":
                from .analysis_service import GoogleAdsAnalysisService
                analysis_service = GoogleAdsAnalysisService(self.user)
                account_id = intent.parameters.get("account_id")
                results["time_performance_analysis"] = analysis_service.analyze_time_performance(account_id)
                
            elif intent.action == "ANALYZE_DEMOGRAPHICS":
                from .analysis_service import GoogleAdsAnalysisService
                analysis_service = GoogleAdsAnalysisService(self.user)
                account_id = intent.parameters.get("account_id")
                results["demographic_analysis"] = analysis_service.analyze_demographics(account_id)
                
            elif intent.action == "ANALYZE_COMPETITORS":
                from .analysis_service import GoogleAdsAnalysisService
                analysis_service = GoogleAdsAnalysisService(self.user)
                account_id = intent.parameters.get("account_id")
                results["competitor_analysis"] = analysis_service.analyze_competitors(account_id)
                
            elif intent.action == "TEST_CREATIVE_ELEMENTS":
                from .analysis_service import GoogleAdsAnalysisService
                analysis_service = GoogleAdsAnalysisService(self.user)
                account_id = intent.parameters.get("account_id")
                results["creative_testing"] = analysis_service.test_creative_elements(account_id)
                
            elif intent.action == "CHECK_TECHNICAL_COMPLIANCE":
                from .analysis_service import GoogleAdsAnalysisService
                analysis_service = GoogleAdsAnalysisService(self.user)
                account_id = intent.parameters.get("account_id")
                results["technical_compliance"] = analysis_service.check_technical_compliance(account_id)
                
            elif intent.action == "ANALYZE_AUDIENCE_INSIGHTS":
                from .analysis_service import GoogleAdsAnalysisService
                analysis_service = GoogleAdsAnalysisService(self.user)
                account_id = intent.parameters.get("account_id")
                results["audience_insights"] = analysis_service.analyze_audience_insights(account_id)
                
            elif intent.action == "OPTIMIZE_BUDGETS":
                # Use RAG system for budget optimization queries
                from .rag_service import GoogleAdsRAGService
                from .data_service import GoogleAdsDataService
                
                # Get user's Google Ads data for context
                data_service = GoogleAdsDataService(self.user)
                account_data = data_service.get_campaign_data()
                
                # Initialize RAG service
                rag_service = GoogleAdsRAGService(self.user)
                
                # Get hybrid response using smart context selection
                rag_response = rag_service.get_hybrid_response("how to optimize Google Ads budgets", account_data)
                
                # Store the RAG-enhanced response
                results["rag_enhanced_response"] = rag_response
                results["response_type"] = rag_response.get("response_type", "unknown")
                results["rag_metadata"] = rag_response.get("rag_metadata", {})
            
            # Additional Google Ads analysis actions
            elif intent.action == "CHECK_CAMPAIGN_CONSISTENCY":
                from .analysis_service import GoogleAdsAnalysisService
                analysis_service = GoogleAdsAnalysisService(self.user)
                account_id = intent.parameters.get("account_id")
                results["campaign_consistency_analysis"] = analysis_service.check_campaign_consistency(account_id)
                
            elif intent.action == "CHECK_SITELINKS":
                from .analysis_service import GoogleAdsAnalysisService
                analysis_service = GoogleAdsAnalysisService(self.user)
                account_id = intent.parameters.get("account_id")
                results["sitelink_analysis"] = analysis_service.check_sitelinks(account_id)
                
            elif intent.action == "CHECK_LANDING_PAGE_URL":
                from .analysis_service import GoogleAdsAnalysisService
                analysis_service = GoogleAdsAnalysisService(self.user)
                account_id = intent.parameters.get("account_id")
                results["landing_page_analysis"] = analysis_service.check_landing_page_url(account_id)
                
            elif intent.action == "CHECK_DUPLICATE_KEYWORDS":
                from .analysis_service import GoogleAdsAnalysisService
                analysis_service = GoogleAdsAnalysisService(self.user)
                account_id = intent.parameters.get("account_id")
                results["duplicate_keyword_analysis"] = analysis_service.check_duplicate_keywords(account_id)
                
            elif intent.action == "ANALYZE_KEYWORD_TRENDS":
                from .analysis_service import GoogleAdsAnalysisService
                analysis_service = GoogleAdsAnalysisService(self.user)
                account_id = intent.parameters.get("account_id")
                results["keyword_trends_analysis"] = analysis_service.analyze_keyword_trends(account_id)
                
            elif intent.action == "ANALYZE_AUCTION_INSIGHTS":
                from .analysis_service import GoogleAdsAnalysisService
                analysis_service = GoogleAdsAnalysisService(self.user)
                account_id = intent.parameters.get("account_id")
                results["auction_insights_analysis"] = analysis_service.analyze_auction_insights(account_id)
                
            elif intent.action == "ANALYZE_SEARCH_TERMS":
                from .analysis_service import GoogleAdsAnalysisService
                analysis_service = GoogleAdsAnalysisService(self.user)
                account_id = intent.parameters.get("account_id")
                results["search_term_analysis"] = analysis_service.analyze_search_terms(account_id)
                
            elif intent.action == "ANALYZE_ADS_SHOWING_TIME":
                from .analysis_service import GoogleAdsAnalysisService
                analysis_service = GoogleAdsAnalysisService(self.user)
                account_id = intent.parameters.get("account_id")
                results["ads_showing_time_analysis"] = analysis_service.analyze_ads_showing_time(account_id)
                
            elif intent.action == "ANALYZE_DEVICE_PERFORMANCE_DETAILED":
                from .analysis_service import GoogleAdsAnalysisService
                analysis_service = GoogleAdsAnalysisService(self.user)
                account_id = intent.parameters.get("account_id")
                results["device_performance_detailed_analysis"] = analysis_service.analyze_device_performance_detailed(account_id)
                
            elif intent.action == "ANALYZE_LOCATION_PERFORMANCE":
                from .analysis_service import GoogleAdsAnalysisService
                analysis_service = GoogleAdsAnalysisService(self.user)
                account_id = intent.parameters.get("account_id")
                results["location_performance_analysis"] = analysis_service.analyze_location_performance(account_id)
                
            elif intent.action == "ANALYZE_LANDING_PAGE_MOBILE":
                from .analysis_service import GoogleAdsAnalysisService
                analysis_service = GoogleAdsAnalysisService(self.user)
                account_id = intent.parameters.get("account_id")
                results["landing_page_mobile_analysis"] = analysis_service.analyze_landing_page_mobile(account_id)
                
            elif intent.action == "OPTIMIZE_TCPA":
                from .analysis_service import GoogleAdsAnalysisService
                analysis_service = GoogleAdsAnalysisService(self.user)
                account_id = intent.parameters.get("account_id")
                results["tcpa_optimizations"] = analysis_service.optimize_tcpa(account_id)
                
            elif intent.action == "OPTIMIZE_BUDGET_ALLOCATION":
                from .analysis_service import GoogleAdsAnalysisService
                analysis_service = GoogleAdsAnalysisService(self.user)
                account_id = intent.parameters.get("account_id")
                results["budget_allocation_optimizations"] = analysis_service.optimize_budget_allocation(account_id)
                
            elif intent.action == "SUGGEST_NEGATIVE_KEYWORDS":
                from .analysis_service import GoogleAdsAnalysisService
                analysis_service = GoogleAdsAnalysisService(self.user)
                account_id = intent.parameters.get("account_id")
                results["negative_keyword_suggestions"] = analysis_service.suggest_negative_keywords(account_id)
                
            elif intent.action == "GET_ADS":
                # Get ads for a specific product
                from .langchain_tools import GoogleAdsTools
                
                product_type = intent.parameters.get("product", "general")
                
                # Initialize Google Ads tools
                google_ads_tools = GoogleAdsTools(self.user, str(self.session.id) if self.session else None)
                
                # Get ads for the product
                ads_result = google_ads_tools.get_ads_for_product(product_type)
                
                if "error" not in ads_result:
                    results["ads_data"] = ads_result
                    results["success_message"] = f"Successfully retrieved ads for {product_type}"
                else:
                    results["error"] = ads_result["error"]
                    results["fallback_message"] = f"Unable to retrieve ads for {product_type}. Using RAG-enhanced response instead."
                    
                    # Fallback to RAG system
                    from .rag_service import GoogleAdsRAGService
                    from .data_service import GoogleAdsDataService
                    
                    # Get user's Google Ads data for context
                    data_service = GoogleAdsDataService(self.user)
                    account_data = data_service.get_campaign_data()
                    
                    # Initialize RAG service
                    rag_service = GoogleAdsRAGService(self.user)
                    
                    # Get hybrid response using smart context selection
                    hybrid_response = rag_service.get_hybrid_response(f"ads for {product_type}", account_data)
                    
                    # Store the RAG-enhanced response
                    results["rag_enhanced_response"] = hybrid_response
                    results["fallback_action"] = intent.action
                    results["fallback_message"] = f"Action '{intent.action}' not found. Generated RAG-enhanced AI response instead."
                    results["response_type"] = hybrid_response.get("response_type", "unknown")
                
            elif intent.action == "CREATE_AD":
                # Create ad with optional image generation
                from .langchain_tools import GoogleAdsTools
                
                # Check if user wants images
                wants_images = intent.parameters.get("image", False)
                product_type = intent.parameters.get("product", "general product")
                
                # Initialize Google Ads tools
                google_ads_tools = GoogleAdsTools(self.user, str(self.session.id) if self.session else None)
                
                # Generate creative suggestions first
                creative_suggestions = google_ads_tools.get_creative_suggestions(
                    product_type=product_type,
                    target_audience="general",
                    tone="professional"
                )
                
                if "error" not in creative_suggestions:
                    # Generate AI images if requested
                    if wants_images:
                        from .openai_service import GoogleAdsOpenAIService
                        openai_service = GoogleAdsOpenAIService()
                        
                        # Generate image prompts based on creative suggestions
                        image_prompts = creative_suggestions.get("suggestions", {}).get("image_suggestions", [])
                        
                        # Create image generation request
                        image_generation_prompt = f"Create a professional product image for {product_type}. Style: modern, clean, professional. Include: product showcase, lifestyle context, high quality, suitable for advertising."
                        
                        try:
                            # Generate image using OpenAI DALL-E
                            image_response = openai_service.client.images.generate(
                                model="dall-e-3",
                                prompt=image_generation_prompt,
                                size="1024x1024",
                                quality="standard",
                                n=1,
                            )
                            
                            # Extract image URL
                            generated_image_url = image_response.data[0].url
                            
                            # Create ad with the generated image
                            ad_result = google_ads_tools.create_ad_with_image(
                                product_type=product_type,
                                headline=creative_suggestions["suggestions"]["headlines"][0],
                                description=creative_suggestions["suggestions"]["descriptions"][0],
                                final_url=f"https://example.com/products/{product_type.lower().replace(' ', '-')}",
                                image_url=generated_image_url
                            )
                            
                            if "error" not in ad_result:
                                results["ad_created"] = True
                                results["ad_data"] = ad_result
                                results["generated_image_url"] = generated_image_url
                                results["creative_suggestions"] = creative_suggestions
                                results["success_message"] = f"Successfully created ad for {product_type} with AI-generated image"
                            else:
                                results["error"] = ad_result["error"]
                                results["fallback_message"] = f"Ad creation failed, but here are creative suggestions for {product_type}"
                                results["creative_suggestions"] = creative_suggestions
                                
                        except Exception as e:
                            logger.error(f"Image generation failed: {e}")
                            # Fallback to ad creation without image
                            ad_result = google_ads_tools.create_ad(
                                ad_group_id="auto_generated",
                                headline=creative_suggestions["suggestions"]["headlines"][0],
                                description=creative_suggestions["suggestions"]["descriptions"][0],
                                final_url=f"https://example.com/products/{product_type.lower().replace(' ', '-')}"
                            )
                            
                            if "error" not in ad_result:
                                results["ad_created"] = True
                                results["ad_data"] = ad_result
                                results["creative_suggestions"] = creative_suggestions
                                results["success_message"] = f"Successfully created ad for {product_type} (image generation failed)"
                            else:
                                results["error"] = ad_result["error"]
                                results["fallback_message"] = f"Ad creation failed, but here are creative suggestions for {product_type}"
                                results["creative_suggestions"] = creative_suggestions
                    else:
                        # Create ad without image
                        ad_result = google_ads_tools.create_ad(
                            ad_group_id="auto_generated",
                            headline=creative_suggestions["suggestions"]["headlines"][0],
                            description=creative_suggestions["suggestions"]["descriptions"][0],
                            final_url=f"https://example.com/products/{product_type.lower().replace(' ', '-')}"
                        )
                        
                        if "error" not in ad_result:
                            results["ad_created"] = True
                            results["ad_data"] = ad_result
                            results["creative_suggestions"] = creative_suggestions
                            results["success_message"] = f"Successfully created ad for {product_type}"
                        else:
                            results["error"] = ad_result["error"]
                            results["fallback_message"] = f"Ad creation failed, but here are creative suggestions for {product_type}"
                            results["creative_suggestions"] = creative_suggestions
                else:
                    results["error"] = creative_suggestions["error"]
                    results["fallback_message"] = f"Unable to generate creative suggestions for {product_type}. Using RAG-enhanced response instead."
                    
                    # Even if creative suggestions fail, try to provide some basic ad creation guidance
                    try:
                        # Provide basic ad creation guidance
                        basic_guidance = {
                            "headlines": [f"Quality {product_type.title()}s", f"Best {product_type.title()}s", f"Premium {product_type.title()}s"],
                            "descriptions": [f"Discover amazing {product_type.title()}s with superior quality.", f"Get the best {product_type.title()}s available."],
                            "call_to_actions": ["Shop Now", "Learn More", "Get Started"],
                            "image_suggestions": [f"Professional {product_type} showcase", f"High-quality {product_type} photography"]
                        }
                        
                        results["basic_creative_guidance"] = basic_guidance
                        results["message"] = f"Creative suggestions failed, but here's basic guidance for creating ads for {product_type}"
                        
                    except Exception as guidance_error:
                        logger.error(f"Failed to provide basic guidance: {guidance_error}")
                    
                    # Fallback to RAG system
                    from .rag_service import GoogleAdsRAGService
                    from .data_service import GoogleAdsDataService
                    
                    # Get user's Google Ads data for context
                    data_service = GoogleAdsDataService(self.user)
                    account_data = data_service.get_campaign_data()
                    
                    # Initialize RAG service
                    rag_service = GoogleAdsRAGService(self.user)
                    
                    # Get hybrid response using smart context selection
                    hybrid_response = rag_service.get_hybrid_response(f"create ad for {product_type}", account_data)
                    
                    # Store the RAG-enhanced response
                    results["rag_enhanced_response"] = hybrid_response
                    results["fallback_action"] = intent.action
                    results["fallback_message"] = f"Action '{intent.action}' partially failed. Generated RAG-enhanced AI response instead."
                    results["response_type"] = hybrid_response.get("response_type", "unknown")
                
            elif intent.action == "GENERATE_IMAGES":
                # Generate AI images for a product
                from .langchain_tools import GoogleAdsTools
                
                product_type = intent.parameters.get("product", "general product")
                image_count = intent.parameters.get("count", 3)
                styles = intent.parameters.get("styles", ["professional", "lifestyle", "modern"])
                
                # Initialize Google Ads tools
                google_ads_tools = GoogleAdsTools(self.user, str(self.session.id) if self.session else None)
                
                # Generate multiple images
                images_result = google_ads_tools.generate_multiple_product_images(
                    product_type=product_type,
                    count=image_count,
                    styles=styles
                )
                
                if "error" not in images_result:
                    results["images_generated"] = True
                    results["images_data"] = images_result
                    results["success_message"] = f"Successfully generated {images_result['total_generated']} AI images for {product_type}"
                else:
                    # Try single image generation as fallback
                    single_image_result = google_ads_tools.generate_product_image(product_type)
                    
                    if "error" not in single_image_result:
                        results["images_generated"] = True
                        results["images_data"] = {
                            "images": [single_image_result],
                            "total_generated": 1
                        }
                        results["success_message"] = f"Successfully generated 1 AI image for {product_type}"
                    else:
                        results["error"] = single_image_result["error"]
                        results["fallback_message"] = f"Image generation failed for {product_type}. Using RAG-enhanced response instead."
                        
                        # Fallback to RAG system
                        from .rag_service import GoogleAdsRAGService
                        from .data_service import GoogleAdsDataService
                        
                        # Get user's Google Ads data for context
                        data_service = GoogleAdsDataService(self.user)
                        account_data = data_service.get_campaign_data()
                        
                        # Initialize RAG service
                        rag_service = GoogleAdsRAGService(self.user)
                        
                        # Get hybrid response using smart context selection
                        hybrid_response = rag_service.get_hybrid_response(f"generate images for {product_type}", account_data)
                        
                        # Store the RAG-enhanced response
                        results["rag_enhanced_response"] = hybrid_response
                        results["fallback_action"] = intent.action
                        results["fallback_message"] = f"Action '{intent.action}' not found. Generated RAG-enhanced AI response instead."
                        results["response_type"] = hybrid_response.get("response_type", "unknown")
                
            # Fallback to RAG-enhanced OpenAI service for unmatched actions
            else:
                # Use RAG system for intelligent context selection
                from .rag_service import GoogleAdsRAGService
                from .data_service import GoogleAdsDataService
                
                # Get user's Google Ads data for context
                data_service = GoogleAdsDataService(self.user)
                account_data = data_service.get_campaign_data()
                
                # Initialize RAG service
                rag_service = GoogleAdsRAGService(self.user)
                
                # Create a meaningful query based on intent action
                fallback_query = f"information about {intent.action.lower().replace('_', ' ')}"
                if intent.parameters:
                    # Add parameters to the query for better context
                    param_str = ", ".join([f"{k}: {v}" for k, v in intent.parameters.items()])
                    fallback_query = f"{fallback_query} with parameters: {param_str}"
                
                # Get hybrid response using smart context selection
                hybrid_response = rag_service.get_hybrid_response(fallback_query, account_data)
                
                # Store the RAG-enhanced response
                results["rag_enhanced_response"] = hybrid_response
                results["fallback_action"] = intent.action
                results["fallback_message"] = f"Action '{intent.action}' not found. Generated RAG-enhanced AI response instead."
                results["response_type"] = hybrid_response.get("response_type", "unknown")
                
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            results["error"] = f"Tool execution failed: {str(e)}"
        
        return results
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session"""
        if not self.session:
            return {}
        
        messages = ChatMessage.objects.filter(session=self.session)
        user_messages = messages.filter(role="user").count()
        assistant_messages = messages.filter(role="assistant").count()
        
        return {
            "session_id": str(self.session.id),
            "title": self.session.title,
            "created_at": self.session.created_at.isoformat(),
            "updated_at": self.session.updated_at.isoformat(),
            "total_messages": messages.count(),
            "user_messages": user_messages,
            "assistant_messages": assistant_messages
        }
    
    def end_session(self):
        """End current chat session"""
        if self.session:
            self.session.updated_at = timezone.now()
            self.session.save()
            self.session = None
    
    def get_quick_insights(self) -> Dict[str, Any]:
        """Get quick insights for the user"""
        try:
            from .langchain_tools import DatabaseTools, AnalyticsTools
            
            db_tools = DatabaseTools(self.user)
            analytics_tools = AnalyticsTools(self.user)
            
            # Get account summary
            account_summary = db_tools.get_account_summary()
            
            # Get budget insights
            budget_insights = analytics_tools.get_budget_insights()
            
            # Get recent performance
            performance_data = db_tools.get_campaign_performance(days=7)
            
            insights = {
                "account_summary": account_summary,
                "budget_insights": budget_insights,
                "recent_performance": performance_data[:5] if performance_data else [],
                "recommendations": []
            }
            
            # Generate recommendations based on data
            if account_summary.get("total_campaigns", 0) == 0:
                insights["recommendations"].append("Create your first campaign to get started")
            
            if budget_insights.get("budget_utilization_percent", 0) > 90:
                insights["recommendations"].append("Budget utilization is high - consider increasing budget or pausing low-performing campaigns")
            
            if budget_insights.get("budget_utilization_percent", 0) < 30:
                insights["recommendations"].append("Budget underutilized - consider expanding campaigns or increasing bids")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting quick insights: {e}")
            return {"error": f"Failed to get insights: {str(e)}"}
    
    def get_user_data_context(self) -> Dict[str, Any]:
        """Get user's data context for better AI responses"""
        try:
            # Get user's Google Ads accounts
            accounts = GoogleAdsAccount.objects.filter(
                user=self.user,
                is_active=True
            )
            
            # Get recent campaigns
            campaigns = GoogleAdsCampaign.objects.filter(
                account__in=accounts
            ).order_by('-created_at')[:10]
            
            # Get recent performance
            from django.utils import timezone
            from datetime import timedelta
            
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=7)
            
            recent_performance = GoogleAdsPerformance.objects.filter(
                account__in=accounts,
                date__gte=start_date
            ).aggregate(
                total_impressions=models.Sum('impressions'),
                total_clicks=models.Sum('clicks'),
                total_cost_micros=models.Sum('cost_micros')
            )
            
            context = {
                "user_id": self.user.id,
                "username": self.user.username,
                "accounts_count": accounts.count(),
                "active_campaigns": campaigns.filter(campaign_status='ENABLED').count(),
                "paused_campaigns": campaigns.filter(campaign_status='PAUSED').count(),
                "recent_performance": {
                    "impressions": recent_performance['total_impressions'] or 0,
                    "clicks": recent_performance['total_clicks'] or 0,
                    "cost_micros": recent_performance['total_cost_micros'] or 0
                },
                "account_names": [acc.account_name for acc in accounts]
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting user data context: {e}")
            return {"error": f"Failed to get user context: {str(e)}"}

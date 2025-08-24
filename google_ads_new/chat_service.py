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

class ChatService:
    """Main chat service that orchestrates the AI assistant"""
    
    def __init__(self, user: User):
        self.user = user
        self.session = None
        self.memory_window = 10  # Remember last 10 messages
    
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
                    results["campaign_creation"] = ga_tools.create_campaign(
                        name=intent.parameters["name"],
                        budget_amount_micros=intent.parameters["budget_amount_micros"],
                        channel_type=intent.parameters.get("channel_type", "SEARCH"),
                        status=intent.parameters.get("status", "PAUSED")
                    )
                else:
                    results["error"] = "Missing required parameters for campaign creation"
                    
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
                    
            else:
                results["message"] = f"Action {intent.action} not yet implemented"
                
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

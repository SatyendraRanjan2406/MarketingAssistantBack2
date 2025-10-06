"""
ChatBotView for Ad Expert - Privacy-first chat system with in-memory analytics
"""
import json
import logging
from datetime import date, datetime
from typing import Dict, Any, List, Optional

from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.db import transaction
from django.utils import timezone
from langgraph.graph.state import StateGraph
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Conversation, ChatMessage
from .llm_orchestrator import LLMOrchestrator
from .redis_service import RedisService
# from .message_builder import CustomerSelectionMessageBuilder, IntentMappingMessageBuilder, MessageBuilder  # Not used in LanggraphView

from langchain_core.messages import HumanMessage, AIMessage

# Import intent mapping service from google_ads_new
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# from google_ads_new.intent_mapping_service import IntentDataMappingResult, get_intent_mapping_service, get_intent_mapping_to_data_service  # Not used in LanggraphView

logger = logging.getLogger(__name__)


class ChatBotView(APIView):
    """
    Main ChatBot API endpoint - privacy-first design
    - No campaign data at rest
    - In-memory analytics only
    - User-controlled chat history
    """
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.llm_orchestrator = LLMOrchestrator()
    
    def post(self, request):
        """Handle chat messages with streaming response"""
        try:
            message = request.data.get('message', '').strip()
            conversation_id = request.data.get('conversation_id')
            
            if not message:
                return Response({
                    'error': 'Message is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get or create conversation
            conversation = self._get_or_create_conversation(request.user, conversation_id)
            
            # Save user message
            user_message = ChatMessage.objects.create(
                conversation=conversation,
                role='user',
                content=message
            )
            
            # Get conversation context (last 20 messages) - include BOTH user and assistant messages
            context_messages = list(
                conversation.messages.order_by('-created_at')[:20].values(
                    'role', 'content', 'created_at', 'response_type', 'structured_data'
                )
            )
            context_messages.reverse()
            
            # Enhance context with structured data for better memory
            enhanced_context = []
            for msg in context_messages:
                enhanced_msg = {
                    'role': msg['role'],
                    'content': msg['content'],
                    'created_at': msg['created_at']
                }
                
                # Add structured data context for assistant messages
                if msg['role'] == 'assistant' and msg['structured_data']:
                    enhanced_msg['data_context'] = f"Previous response included: {msg['response_type']} with {len(msg['structured_data'])} data points"
                
                enhanced_context.append(enhanced_msg)
            
            context_messages = enhanced_context
            
            # Process with LLM orchestrator
            import asyncio
            response_data = asyncio.run(self.llm_orchestrator.process_query(
                user_message=message,
                user_id=request.user.id,
                conversation_context=context_messages
            ))
            
            # Save assistant response
            assistant_message = ChatMessage.objects.create(
                conversation=conversation,
                role='assistant',
                content=response_data.get('content', ''),
                response_type=response_data.get('response_type', 'text'),
                structured_data=response_data.get('data', [])
            )
            
            # Update conversation timestamp
            conversation.updated_at = datetime.now()
            conversation.save()
            
            return Response({
                'message_id': assistant_message.id,
                'conversation_id': conversation.id,
                'response': response_data,
                'timestamp': assistant_message.created_at.isoformat()
            })
            
        except Exception as e:
            logger.error(f"ChatBot error: {str(e)}")
            return Response({
                'error': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_or_create_conversation(self, user, conversation_id=None):
        """Get existing conversation or create new one"""
        if conversation_id:
            try:
                return Conversation.objects.get(
                    id=conversation_id,
                    user=user,
                    deleted_at__isnull=True
                )
            except Conversation.DoesNotExist:
                pass
        
        # Create new conversation
        return Conversation.objects.create(
            user=user,
            title=f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_conversations(request):
    """Get user's conversations"""
    try:
        conversations = Conversation.objects.filter(
            user=request.user,
            deleted_at__isnull=True
        ).order_by('-updated_at')[:20]
        
        data = []
        for conv in conversations:
            data.append({
                'id': conv.id,
                'title': conv.title,
                'created_at': conv.created_at.isoformat(),
                'updated_at': conv.updated_at.isoformat(),
                'message_count': conv.messages.count()
            })
        
        return Response(data)
        
    except Exception as e:
        logger.error(f"Get conversations error: {str(e)}")
        return Response({
            'error': 'Failed to fetch conversations'
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_conversation_messages(request, conversation_id):
    """Get messages for a specific conversation"""
    try:
        conversation = Conversation.objects.get(
            id=conversation_id,
            user=request.user,
            deleted_at__isnull=True
        )
        
        messages = conversation.messages.order_by('created_at')
        data = []
        
        for msg in messages:
            data.append({
                'id': msg.id,
                'role': msg.role,
                'content': msg.content,
                'response_type': msg.response_type,
                'structured_data': msg.structured_data,
                'created_at': msg.created_at.isoformat()
            })
        
        return Response(data)
        
    except Conversation.DoesNotExist:
        return Response({
            'error': 'Conversation not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Get messages error: {str(e)}")
        return Response({
            'error': 'Failed to fetch messages'
        }, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_conversation(request, conversation_id):
    """Soft delete a conversation"""
    try:
        conversation = Conversation.objects.get(
            id=conversation_id,
            user=request.user,
            deleted_at__isnull=True
        )
        
        # Soft delete
        conversation.deleted_at = datetime.now()
        conversation.save()
        
        # Schedule hard delete job (in production, use Celery)
        # For now, we'll do it immediately
        conversation.messages.all().delete()
        conversation.delete()
        
        return Response({
            'message': 'Conversation deleted successfully'
        })
        
    except Conversation.DoesNotExist:
        return Response({
            'error': 'Conversation not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Delete conversation error: {str(e)}")
        return Response({
            'error': 'Failed to delete conversation'
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_oauth_connections(request):
    """Get user's OAuth connections from accounts app"""
    try:
        from accounts.google_oauth_service import UserGoogleAuthService
        
        # Get Google OAuth connections
        google_accounts = UserGoogleAuthService.get_user_google_accounts(request.user)
        
        data = []
        for account in google_accounts:
            data.append({
                'id': account['id'],
                'platform': 'google',
                'account_id': account['google_ads_customer_id'],
                'email': account['google_email'],
                'name': account['google_name'],
                'created_at': account['last_used'].isoformat(),
                'is_token_valid': account['is_token_valid']
            })
        
        return Response(data)
        
    except Exception as e:
        logger.error(f"Get OAuth connections error: {str(e)}")
        return Response({
            'error': 'Failed to fetch connections'
        }, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def revoke_oauth_connection(request, connection_id):
    """Revoke OAuth connection"""
    try:
        from accounts.google_oauth_service import UserGoogleAuthService
        
        # Revoke Google OAuth connection
        success = UserGoogleAuthService.revoke_user_auth(request.user)
        
        if success:
            return Response({
                'message': 'Connection revoked successfully'
            })
        else:
            return Response({
                'error': 'Failed to revoke connection'
            }, status=500)
        
    except Exception as e:
        logger.error(f"Revoke connection error: {str(e)}")
        return Response({
            'error': 'Failed to revoke connection'
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def health_check(request):
    """Health check endpoint"""
    return Response({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'user': request.user.username
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_auth(request):
    """Test authentication endpoint"""
    return Response({
        'message': 'Authentication successful',
        'user_id': request.user.id,
        'username': request.user.username,
        'is_authenticated': request.user.is_authenticated,
        'timestamp': datetime.now().isoformat()
    })


# COMMENTED OUT - Not used in LanggraphView
# class RAGChatView(APIView):
#     """
#     RAG Chat API endpoint that integrates with Intent Mapping Service
#     - First maps user query to intent actions using OpenAI
#     - Then processes the query with the mapped intents
#     - Returns structured response with actions, date ranges, and filters
#     """
#     authentication_classes = [JWTAuthentication, SessionAuthentication]
#     permission_classes = [IsAuthenticated]
    
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.intent_mapping_service = get_intent_mapping_service()
#         self.llm_orchestrator = LLMOrchestrator()
#     
#     def post(self, request):
#         """
#         Handle RAG chat messages with intent mapping
#         
#         POST /ad-expert/api/rag/chat/
#         
#         Body:
#         {
#             "query": "Show me active campaigns from last 7 days with budget > $100",
#             "conversation_id": "optional_conversation_id",
#             "user_context": {
#                 "customer_id": "1234567890",
#                 "campaigns": ["campaign1", "campaign2"]
#             }
#         }
#         
#         Response:
#         {
#             "success": true,
#             "intent_mapping": {
#                 "actions": ["GET_CAMPAIGNS_WITH_FILTERS"],
#                 "date_ranges": [...],
#                 "filters": [...],
#                 "confidence": 0.95,
#                 "reasoning": "..."
#             },
#             "chat_response": "Generated response based on intent mapping",
#             "conversation_id": "conversation_id",
#             "timestamp": "2024-01-01T00:00:00Z"
#         }
#         """
#         try:
            # Extract data from request
#             query = request.data.get('query', '').strip()
#             conversation_id = request.data.get('conversation_id')
#             user_context = request.data.get('user_context', {})
            
#             if not query:
#                 return Response({
#                     "success": False,
#                     "error": "Query is required"
#                 }, status=status.HTTP_400_BAD_REQUEST)
            
#             logger.info(f"RAG Chat request from user {request.user.id}: {query}")
            
            # Step 1: Map query to intent actions using Intent Mapping Service
#             try:
#                 intent_result = self.intent_mapping_service.map_query_to_intents(
#                     query=query,
#                     user_context=user_context
#                 )
#                 logger.info(f"Intent mapping result: {intent_result.actions}")
#             except Exception as e:
#                 logger.error(f"Error in intent mapping: {e}")
#                 return Response({
#                     "success": False,
#                     "error": f"Intent mapping failed: {str(e)}"
#                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Step 2: Get accessible customer IDs from UserGoogleAuth model
#             try:
#                 from accounts.models import UserGoogleAuth
                
                # Get all active Google Auth records for the user
#                 google_auth_records = UserGoogleAuth.objects.filter(
#                     user=request.user,
#                     is_active=True
#                 ).exclude(accessible_customers__isnull=True)
                
#                 accessible_customers = []
#                 for auth_record in google_auth_records:
#                     if auth_record.accessible_customers and isinstance(auth_record.accessible_customers, dict):
                        # Extract customer IDs from the dictionary structure
#                         customers = auth_record.accessible_customers.get('customers', [])
#                         if customers:
#                             accessible_customers.extend(customers)
                
                # Remove duplicates and sort
#                 accessible_customers = sorted(list(set(accessible_customers)))
                
#                 logger.info(f"Found {len(accessible_customers)} accessible customer IDs for user {request.user.id}")
                
#             except Exception as e:
#                 logger.error(f"Error fetching accessible customer IDs: {e}")
#                 accessible_customers = []
            
            # Step 3: Get conversation context for memory and check for stored customer ID
#             conversation_context = None
#             conversation = None
#             stored_customer_id = None
            
#             if conversation_id:
#                 try:
                    # Get conversation and its recent messages for context
#                     conversation = Conversation.objects.get(
#                         id=conversation_id,
#                         user=request.user
#                     )
                    
                    # Check if conversation already has a stored customer ID
#                     if conversation.customer_id:
#                         stored_customer_id = conversation.customer_id
#                         logger.info(f"Found stored customer ID in conversation {conversation_id}: {stored_customer_id}")
                    
                    # Get last 10 messages for context
#                     context_messages = list(
#                         conversation.messages.order_by('-created_at')[:10].values(
#                             'role', 'content', 'created_at'
#                         )
#                     )
#                     context_messages.reverse()
#                     conversation_context = context_messages
#                     logger.info(f"Retrieved {len(context_messages)} messages for conversation context")
#                 except Conversation.DoesNotExist:
#                     logger.warning(f"Conversation {conversation_id} not found for user {request.user.id}")
#                     conversation_context = None
#                     conversation = None
            
            # Step 3.5: Extract customer ID from user query or request
#             extracted_customer_id = self._extract_customer_id_from_query(query, accessible_customers)
#             if extracted_customer_id:
#                 logger.info(f"Extracted customer ID from query: {extracted_customer_id}")
#                 stored_customer_id = extracted_customer_id
            
            # Step 4: Generate chat response based on intent mapping
#             try:
                # Create enhanced context with intent mapping results
#                 enhanced_context = {
#                     **user_context,
#                     "intent_actions": intent_result.actions,
#                     "date_ranges": [dr.to_dict() for dr in intent_result.date_ranges],
#                     "filters": [f.to_dict() for f in intent_result.filters],
#                     "confidence": intent_result.confidence,
#                     "reasoning": intent_result.reasoning
#                 }
                
                # Generate response using LLM orchestrator with conversation context
#                 import asyncio
#                 llm_result = asyncio.run(self.llm_orchestrator.process_query(
#                     user_message=query,
#                     user_id=request.user.id,
#                     conversation_context=conversation_context,
#                     customer_id=stored_customer_id
#                 ))
                
                # Extract the content from the structured response
#                 base_response = llm_result.get('content', 'I processed your request but could not generate a response.')
                
                # Handle customer ID selection and response enhancement
#                 if stored_customer_id:
                    # Customer ID is already stored, use it in the response
#                     chat_response = f"{base_response}\n\nI'll use customer ID: {stored_customer_id} for this request."
#                     logger.info(f"Using stored customer ID: {stored_customer_id}")
#                 elif accessible_customers and ('customer' in query.lower() or 'customer id' in base_response.lower()):
                    # No customer ID stored yet, ask user to select one
#                     customer_list = '\n'.join([f"- {customer_id}" for customer_id in accessible_customers])
#                     chat_response = f"{base_response}\n\nI found the following accessible customer IDs in your account:\n{customer_list}\n\nPlease choose one of these customer IDs and let me know which one you'd like to use for this request."
#                 else:
#                     chat_response = base_response
                
                # Get or create conversation (reuse if already retrieved)
#                 if not conversation:
#                     conversation = Conversation.objects.create(
#                         user=request.user,
#                         title=query[:50] + "..." if len(query) > 50 else query,
#                         customer_id=stored_customer_id
#                     )
#                     conversation_id = conversation.id
#                 elif stored_customer_id and not conversation.customer_id:
                    # Update existing conversation with customer ID if not already set
#                     conversation.customer_id = stored_customer_id
#                     conversation.save()
#                     logger.info(f"Updated conversation {conversation_id} with customer ID: {stored_customer_id}")
                
                # Save the chat message
#                 ChatMessage.objects.create(
#                     conversation=conversation,
#                     role='user',
#                     content=query,
#                     response_type='text'
#                 )
                
#                 ChatMessage.objects.create(
#                     conversation=conversation,
#                     role='assistant',
#                     content=chat_response,
#                     response_type='text',
#                     structured_data={
#                         'intent_mapping': {
#                             'actions': intent_result.actions,
#                             'date_ranges': [dr.to_dict() for dr in intent_result.date_ranges],
#                             'filters': [f.to_dict() for f in intent_result.filters],
#                             'confidence': intent_result.confidence,
#                             'reasoning': intent_result.reasoning,
#                             'parameters': intent_result.parameters
#                         }
#                     }
#                 )
                
#                 logger.info(f"RAG Chat response generated successfully for user {request.user.id}")
                
#             except Exception as e:
#                 logger.error(f"Error generating chat response: {e}")
#                 return Response({
#                     "success": False,
#                     "error": f"Chat response generation failed: {str(e)}"
#                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Step 4: Return structured response
#             response_data = {
#                 "success": True,
#                 "intent_mapping": {
#                     "actions": intent_result.actions,
#                     "date_ranges": [dr.to_dict() for dr in intent_result.date_ranges],
#                     "filters": [f.to_dict() for f in intent_result.filters],
#                     "confidence": intent_result.confidence,
#                     "reasoning": intent_result.reasoning,
#                     "parameters": intent_result.parameters
#                 },
#                 "chat_response": chat_response,
#                 "conversation_id": conversation_id,
#                 "timestamp": datetime.now().isoformat(),
#                 "query": query
#             }
            
            # Add customer ID information to response
#             response_data["stored_customer_id"] = stored_customer_id
#             if accessible_customers:
#                 response_data["accessible_customers"] = accessible_customers
#                 response_data["customer_selection_required"] = not bool(stored_customer_id)
#             else:
#                 response_data["accessible_customers"] = []
#                 response_data["customer_selection_required"] = False
            
#             return Response(response_data)
            
#         except Exception as e:
#             logger.error(f"Unexpected error in RAG Chat: {e}")
#             return Response({
#                 "success": False,
#                 "error": f"Unexpected error: {str(e)}"
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
#     def _extract_customer_id_from_query(self, query: str, accessible_customers: list) -> str:
#         """Extract customer ID from user query"""
#         import re
        
        # Convert query to lowercase for case-insensitive matching
#         query_lower = query.lower()
        
        # Pattern 1: Look for "customers/" prefix
#         customer_pattern = r'customers/(\d+)'
#         matches = re.findall(customer_pattern, query)
#         if matches:
#             customer_id = f"customers/{matches[0]}"
#             if customer_id in accessible_customers:
#                 return customer_id
        
        # Pattern 2: Look for standalone customer IDs (just numbers)
#         standalone_pattern = r'\b(\d{10})\b'  # 10-digit customer ID
#         matches = re.findall(standalone_pattern, query)
#         if matches:
#             customer_id = f"customers/{matches[0]}"
#             if customer_id in accessible_customers:
#                 return customer_id
        
        # Pattern 3: Look for customer ID in "use customer X" patterns
#         use_pattern = r'use customer[:\s]+(customers/\d+|\d{10})'
#         matches = re.findall(use_pattern, query_lower)
#         if matches:
#             customer_id = matches[0]
#             if not customer_id.startswith('customers/'):
#                 customer_id = f"customers/{customer_id}"
#             if customer_id in accessible_customers:
#                 return customer_id
        
        # Pattern 4: Look for "customer id X" patterns
#         id_pattern = r'customer id[:\s]+(customers/\d+|\d{10})'
#         matches = re.findall(id_pattern, query_lower)
#         if matches:
#             customer_id = matches[0]
#             if not customer_id.startswith('customers/'):
#                 customer_id = f"customers/{customer_id}"
#             if customer_id in accessible_customers:
#                 return customer_id
        
        # Pattern 5: Look for "select X" or "choose X" patterns where X is a customer ID
#         select_pattern = r'(?:select|choose)\s+(customers/\d+|\d{10})'
#         matches = re.findall(select_pattern, query_lower)
#         if matches:
#             customer_id = matches[0]
#             if not customer_id.startswith('customers/'):
#                 customer_id = f"customers/{customer_id}"
#             if customer_id in accessible_customers:
#                 return customer_id
        
#         return None
    
#     def _is_customer_id_response(self, query: str) -> bool:
#         """Check if the query looks like a customer ID response"""
#         import re
#         query_lower = query.lower().strip()
        
        # Check for customer ID patterns
#         customer_patterns = [
#             r'customers/\d+',  # customers/123456789
#             r'\d{10}',         # 10-digit number
#             r'^\d+$',          # Just numbers
#         ]
        
#         for pattern in customer_patterns:
#             if re.search(pattern, query_lower):
#                 return True
        
        # Check if it's a simple response that could be a customer ID
#         if len(query_lower) < 20 and (query_lower.isdigit() or 'customer' in query_lower):
#             return True
            
#         return False
    
#     def _create_customer_id_response_intent(self, query: str, conversation_context: List[Dict]) -> Any:
#         """Create an intent result for customer ID responses"""
#         from google_ads_new.intent_mapping_service import IntentMappingResult, DateRange, Filter
        
        # Extract customer ID from the query
#         customer_id = self._extract_customer_id_from_query(query, [])
        
        # Try to determine the original intent from conversation context
#         original_intent = "GET_PERFORMANCE"  # Default to performance if we asked for customer ID
        
#         if conversation_context:
            # Look for keywords in the conversation to determine original intent
#             context_text = " ".join([msg['content'] for msg in conversation_context[-3:]])
#             context_lower = context_text.lower()
            
#             if any(word in context_lower for word in ['campaign', 'campaigns']):
#                 original_intent = "GET_CAMPAIGNS"
#             elif any(word in context_lower for word in ['ad', 'ads']):
#                 original_intent = "GET_ADS"
#             elif any(word in context_lower for word in ['overview', 'summary']):
#                 original_intent = "GET_OVERVIEW"
#             elif any(word in context_lower for word in ['performance', 'metrics', 'data']):
#                 original_intent = "GET_PERFORMANCE"
        
#         return IntentMappingResult(
#             actions=[original_intent],
#             date_ranges=[],
#             filters=[],
#             confidence=0.95,
#             reasoning=f"Detected customer ID response '{query}' for previous {original_intent} query",
#             parameters={"customer_id": customer_id} if customer_id else {}
#         )


# class RAGChat2View(APIView):
#     """
#     Enhanced RAG Chat API endpoint with MCP integration
#     Uses Model Context Protocol for Google Ads API access
#     """
#     authentication_classes = [JWTAuthentication, SessionAuthentication]
#     permission_classes = [IsAuthenticated]
#     
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.intent_mapping_service = get_intent_mapping_service()
#         self.mcp_service = None
#     
#     async def initialize_mcp(self):
#         """Initialize MCP service"""
#         try:
#             from .mcp_client import MCPGoogleAdsService
#             if not self.mcp_service:
#                 self.mcp_service = MCPGoogleAdsService()
#                 await self.mcp_service.initialize()
#             return True
#         except Exception as e:
#             logger.error(f"Error initializing MCP service: {e}")
#             return False
#     
#     def post(self, request):
#         """Handle chat messages with MCP integration"""
#         try:
            # Extract request data
#             query = request.data.get('query', '').strip()
#             conversation_id = request.data.get('conversation_id')
#             user_context = request.data.get('user_context', {})
#             user_id = request.user.id
#             
#             if not query:
#                 return Response({
#                     'success': False,
#                     'error': 'Query is required'
#                 }, status=status.HTTP_400_BAD_REQUEST)
#             
#             logger.info(f"MCP Chat request from user {request.user.id}: {query[:100]}...")
#             
            # Step 1: Check if this is a response to a previous question (conversation context)
#             conversation_context = None
#             is_customer_id_response = False
#             
            # First check if the query looks like a customer ID response
#             if self._is_customer_id_response(query):
                # Check if we have conversation context
#                 if conversation_id:
#                     try:
#                         conversation = Conversation.objects.get(
#                             id=conversation_id,
#                             user=request.user
#                         )
#                         
                        # Get conversation context for intent mapping
#                         context_messages = list(
#                             conversation.messages.order_by('-created_at')[:10].values(
#                                 'role', 'content', 'created_at'
#                             )
#                         )
#                         context_messages.reverse()
#                         conversation_context = context_messages
#                         
                        # Check if this is a customer ID response to previous action
                        # Look for patterns that indicate this is a response to a previous query
#                         if self._is_customer_id_response(query):
                            # Check if last assistant message asked for customer ID
#                             last_assistant_message = conversation.messages.filter(
#                                 role='assistant'
#                             ).order_by('-created_at').first()
#                             
#                             if last_assistant_message and ("customer ID" in last_assistant_message.content or "customer" in last_assistant_message.content):
#                                 is_customer_id_response = True
#                                 logger.info(f"Detected customer ID response to assistant request: {query}")
#                             else:
                                # Check if there's a previous user query that needs a customer ID
                                # Look for user queries that would typically need customer ID
#                                 user_messages = [msg for msg in context_messages if msg.get('role') == 'user']
#                                 if user_messages:
#                                     last_user_query = user_messages[-1]['content'].lower()
                                    # Check if the last user query was an action that needs customer ID
#                                     if any(keyword in last_user_query for keyword in [
#                                         'show', 'get', 'campaign', 'performance', 'data', 'ads', 
#                                         'overview', 'report', 'analytics', 'metrics'
#                                     ]):
#                                         is_customer_id_response = True
#                                         logger.info(f"Detected customer ID response to previous action: {query}")
#                                         logger.info(f"Previous user query: {last_user_query}")
#                         
#                     except Conversation.DoesNotExist:
#                         logger.warning(f"Conversation {conversation_id} not found for user {request.user.id}")
#                 
                # Only treat as customer ID response if we have conversation context
                # Without context, let normal intent mapping handle it
#                 if not is_customer_id_response:
#                     logger.info(f"No conversation context found for customer ID query: {query}")
#                     conversation_context = None
#             
            # Step 2: Get intent mapping with conversation context
#             if is_customer_id_response:
                # If this is a customer ID response, don't use intent mapping
                # Instead, treat it as a continuation of the previous query
#                 intent_result = self._create_customer_id_response_intent(query, conversation_context)
#             else:
#                 intent_result = self.intent_mapping_service.map_query_to_intents(query, conversation_context)
#             
#             logger.info(f"Intent mapping result: {intent_result.actions} with confidence {intent_result.confidence}")
#             
            # Step 1.5: Handle GET_ACCESSIBLE_CUSTOMERS action (doesn't need customer ID)
#             if "GET_ACCESSIBLE_CUSTOMERS" in intent_result.actions:
                # Get accessible customers directly from UserGoogleAuth model
#                 accessible_customers = []
#                 try:
#                     from accounts.models import UserGoogleAuth
#                     google_auth_records = UserGoogleAuth.objects.filter(
#                         user=request.user,
#                         is_active=True
#                     ).exclude(accessible_customers__isnull=True)
#                     
#                     for auth_record in google_auth_records:
#                         if auth_record.accessible_customers and isinstance(auth_record.accessible_customers, dict):
#                             customers = auth_record.accessible_customers.get('customers', [])
#                             if customers:
#                                 accessible_customers.extend(customers)
#                     
#                     accessible_customers = sorted(list(set(accessible_customers)))
#                     logger.info(f"Found {len(accessible_customers)} accessible customer IDs for user {request.user.id}")
#                     
#                 except Exception as e:
#                     logger.error(f"Error fetching accessible customer IDs: {e}")
#                     accessible_customers = []
#                 
                # Create result
#                 result = {
#                     "success": True,
#                     "user_id": user_id,
#                     "accessible_customers": accessible_customers,
#                     "total_count": len(accessible_customers)
#                 }
#                 
#                 mcp_result = {
#                     "content": f"Here are your accessible Google Ads customer accounts ({len(accessible_customers)} found):",
#                     "data": result,
#                     "type": "accessible_customers"
#                 }
#                 
                # Enhance with ChatGPT
#                 import asyncio
#                 from .fallback_handlers import enhance_mcp_result_with_chatgpt
#                 enhanced_result = asyncio.run(enhance_mcp_result_with_chatgpt(mcp_result, query))
#                 
                # Save conversation
#                 conversation = None
#                 if conversation_id:
#                     try:
#                         conversation = Conversation.objects.get(
#                             id=conversation_id,
#                             user=request.user
#                         )
#                     except Conversation.DoesNotExist:
#                         conversation = None
#                 
#                 if not conversation:
#                         conversation = Conversation.objects.create(
#                             user=request.user,
#                         title=f"Chat - {query[:50]}..."
#                     )
#                 
#                 conversation.messages.create(
#                     role='user',
#                     content=query
#                 )
#                 conversation.messages.create(
#                     role='assistant',
#                     content=enhanced_result["content"]
#                 )
#                 
#                 return Response({
#                     "success": True,
#                     "intent_mapping": intent_result.to_dict(),
#                     "chat_response": enhanced_result["content"],
#                     "mcp_result": enhanced_result,
#                     "conversation_id": conversation.id,
#                     "timestamp": timezone.now().isoformat(),
#                     "query": query,
#                     "stored_customer_id": None,
#                     "accessible_customers": accessible_customers,
#                     "customer_selection_required": False
#                 })
#             
            # Step 2: Get accessible customer IDs
#             accessible_customers = []
#             try:
#                 from accounts.models import UserGoogleAuth
#                 google_auth_records = UserGoogleAuth.objects.filter(
#                     user=request.user,
#                     is_active=True
#                 ).exclude(accessible_customers__isnull=True)
#                 
#                 for auth_record in google_auth_records:
#                     if auth_record.accessible_customers and isinstance(auth_record.accessible_customers, dict):
#                         customers = auth_record.accessible_customers.get('customers', [])
#                         if customers:
#                             accessible_customers.extend(customers)
#                 
#                 accessible_customers = sorted(list(set(accessible_customers)))
#                 logger.info(f"Found {len(accessible_customers)} accessible customer IDs for user {request.user.id}")
#                 
#             except Exception as e:
#                 logger.error(f"Error fetching accessible customer IDs: {e}")
#                 accessible_customers = []
#             
            # Step 3: Handle conversation context and customer ID persistence
#             conversation_context = None
#             conversation = None
#             stored_customer_id = None
#             
#             if conversation_id:
#                 try:
#                     conversation = Conversation.objects.get(
#                         id=conversation_id,
#                         user=request.user
#                     )
#                     
#                     if conversation.customer_id:
#                         stored_customer_id = conversation.customer_id
#                         logger.info(f"Found stored customer ID in conversation {conversation_id}: {stored_customer_id}")
#                     
#                     context_messages = list(
#                         conversation.messages.order_by('-created_at')[:10].values(
#                             'role', 'content', 'created_at'
#                         )
#                     )
#                     context_messages.reverse()
#                     conversation_context = context_messages
#                     logger.info(f"Retrieved {len(context_messages)} messages for conversation context")
#                     
#                 except Conversation.DoesNotExist:
#                     logger.warning(f"Conversation {conversation_id} not found for user {request.user.id}")
#                     conversation_context = None
#                     conversation = None
#             
            # Step 3.5: Extract customer ID from user query
#             extracted_customer_id = self._extract_customer_id_from_query(query, accessible_customers)
#             if extracted_customer_id:
#                 logger.info(f"Extracted customer ID from query: {extracted_customer_id}")
#                 stored_customer_id = extracted_customer_id
#             
            # Step 4: Process with MCP integration
#             try:
                # Initialize MCP service
#                 import asyncio
#                 mcp_initialized = asyncio.run(self.initialize_mcp())
#                 
#                 if not mcp_initialized:
#                     return Response({
#                         "success": False,
#                         "error": "Failed to initialize MCP service"
#                     }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#                 
                # Process query with MCP
#                 mcp_result = asyncio.run(self._process_query_with_mcp(
#                     query, intent_result, stored_customer_id, request.user.id
#                 ))
#                 
                # Generate chat response
#                 if stored_customer_id:
#                     chat_response = f"{mcp_result.get('content', 'I processed your request using MCP integration.')}\n\nUsing customer ID: {stored_customer_id}"
#                 elif accessible_customers and ('customer' in query.lower() or 'customer id' in mcp_result.get('content', '').lower()):
#                     customer_list = '\n'.join([f"- {customer_id}" for customer_id in accessible_customers])
#                     chat_response = f"{mcp_result.get('content', 'I can help you with Google Ads data.')}\n\nI found the following accessible customer IDs in your account:\n{customer_list}\n\nPlease choose one of these customer IDs and let me know which one you'd like to use for this request."
#                 else:
#                     chat_response = mcp_result.get('content', 'I processed your request using MCP integration.')
#                 
                # Get or create conversation
#                 if not conversation:
#                     conversation = Conversation.objects.create(
#                         user=request.user,
#                         title=query[:50] + "..." if len(query) > 50 else query,
#                         customer_id=stored_customer_id
#                     )
#                     conversation_id = conversation.id
#                 elif stored_customer_id and not conversation.customer_id:
#                     conversation.customer_id = stored_customer_id
#                     conversation.save()
#                     logger.info(f"Updated conversation {conversation_id} with customer ID: {stored_customer_id}")
#                 
                # Save chat messages
#                 ChatMessage.objects.create(
#                     conversation=conversation,
#                     role='user',
#                     content=query,
#                     response_type='text'
#                 )
#                 
#                 ChatMessage.objects.create(
#                     conversation=conversation,
#                     role='assistant',
#                     content=chat_response,
#                     response_type='text',
#                     structured_data={
#                         'mcp_result': mcp_result,
#                         'intent_mapping': {
#                             'actions': intent_result.actions,
#                             'date_ranges': [dr.to_dict() for dr in intent_result.date_ranges],
#                             'filters': [f.to_dict() for f in intent_result.filters],
#                             'confidence': intent_result.confidence,
#                             'reasoning': intent_result.reasoning,
#                             'parameters': intent_result.parameters
#                         }
#                     }
#                 )
#                 
#                 logger.info(f"MCP Chat response generated successfully for user {request.user.id}")
#                 
#             except Exception as e:
#                 logger.error(f"Error processing query with MCP: {e}")
#                 return Response({
#                     "success": False,
#                     "error": f"MCP processing failed: {str(e)}"
#                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#             
            # Step 5: Return structured response
#             response_data = {
#                 "success": True,
#                 "intent_mapping": {
#                     "actions": intent_result.actions,
#                     "date_ranges": [dr.to_dict() for dr in intent_result.date_ranges],
#                     "filters": [f.to_dict() for f in intent_result.filters],
#                     "confidence": intent_result.confidence,
#                     "reasoning": intent_result.reasoning,
#                     "parameters": intent_result.parameters
#                 },
#                 "chat_response": chat_response,
#                 "mcp_result": mcp_result,
#                 "conversation_id": conversation_id,
#                 "timestamp": datetime.now().isoformat(),
#                 "query": query
#             }
#             
            # Add customer ID information
#             response_data["stored_customer_id"] = stored_customer_id
#             if accessible_customers:
#                 response_data["accessible_customers"] = accessible_customers
#                 response_data["customer_selection_required"] = not bool(stored_customer_id)
#             else:
#                 response_data["accessible_customers"] = []
#                 response_data["customer_selection_required"] = False
#             
#             return Response(response_data)
#             
#         except Exception as e:
#             logger.error(f"Unexpected error in MCP Chat: {e}")
#             return Response({
#                 "success": False,
#                 "error": f"Unexpected error: {str(e)}"
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# 
#     async def _process_query_with_mcp(self, query: str, intent_result, customer_id: str, user_id: int) -> Dict[str, Any]:
#         """Process query using MCP integration with comprehensive intent action handling"""
#         try:
            # Initialize MCP service if not already done
#             if not self.mcp_service:
#                 from .mcp_client import MCPGoogleAdsService
#                 self.mcp_service = MCPGoogleAdsService()
#                 await self.mcp_service.initialize()
#             
            # Determine what data to fetch based on intent
#             if not customer_id:
#                 return {
#                     "content": "I need a customer ID to fetch Google Ads data. Please provide one from your accessible accounts.",
#                     "data": None,
#                     "type": "customer_selection_required"
#                 }
#             
            # Use the comprehensive intent action handler
#             from .intent_action_handler import IntentActionHandler
#             action_handler = IntentActionHandler(self.mcp_service)
#             
            # Execute the intent action
#             result = await action_handler.execute_intent_action(intent_result, customer_id, user_id, query)
#             
            # Enhance with ChatGPT for all results
#             from .fallback_handlers import enhance_mcp_result_with_chatgpt
#             enhanced_result = await enhance_mcp_result_with_chatgpt(result, query)
#             
#             return enhanced_result
#                 
#         except Exception as e:
#             logger.error(f"Error in MCP processing: {e}")
#             return {
#                 "content": f"I encountered an error processing your request: {str(e)}",
#                 "data": None,
#                 "type": "error"
#             }
#     
#     def _extract_customer_id_from_query(self, query: str, accessible_customers: list) -> str:
#         """Extract customer ID from user query (reuse from RAGChatView)"""
#         import re
#         
        # Convert query to lowercase for case-insensitive matching
#         query_lower = query.lower()
#         
        # Pattern 1: Look for "customers/" prefix
#         customer_pattern = r'customers/(\d+)'
#         matches = re.findall(customer_pattern, query)
#         if matches:
#             customer_id = f"customers/{matches[0]}"
#             if customer_id in accessible_customers:
#                 return customer_id
#         
        # Pattern 2: Look for standalone customer IDs (just numbers)
#         standalone_pattern = r'\b(\d{10})\b'  # 10-digit customer ID
#         matches = re.findall(standalone_pattern, query)
#         if matches:
#             customer_id = f"customers/{matches[0]}"
#             if customer_id in accessible_customers:
#                 return customer_id
#         
        # Pattern 3: Look for customer ID in "use customer X" patterns
#         use_pattern = r'use customer[:\s]+(customers/\d+|\d{10})'
#         matches = re.findall(use_pattern, query_lower)
#         if matches:
#             customer_id = matches[0]
#             if not customer_id.startswith('customers/'):
#                 customer_id = f"customers/{customer_id}"
#             if customer_id in accessible_customers:
#                 return customer_id
#         
        # Pattern 4: Look for "customer id X" patterns
#         id_pattern = r'customer id[:\s]+(customers/\d+|\d{10})'
#         matches = re.findall(id_pattern, query_lower)
#         if matches:
#             customer_id = matches[0]
#             if not customer_id.startswith('customers/'):
#                 customer_id = f"customers/{customer_id}"
#             if customer_id in accessible_customers:
#                 return customer_id
#         
        # Pattern 5: Look for "select X" or "choose X" patterns where X is a customer ID
#         select_pattern = r'(?:select|choose)\s+(customers/\d+|\d{10})'
#         matches = re.findall(select_pattern, query_lower)
#         if matches:
#             customer_id = matches[0]
#             if not customer_id.startswith('customers/'):
#                 customer_id = f"customers/{customer_id}"
#             if customer_id in accessible_customers:
#                 return customer_id
#         
#         return None
#     
#     def _is_customer_id_response(self, query: str) -> bool:
#         """Check if the query looks like a customer ID response"""
#         import re
#         query_lower = query.lower().strip()
#         
        # Check for customer ID patterns
#         customer_patterns = [
#             r'customers/\d+',  # customers/123456789
#             r'\d{10}',         # 10-digit number
#             r'^\d+$',          # Just numbers
#         ]
#         
#         for pattern in customer_patterns:
#             if re.search(pattern, query_lower):
#                 return True
#         
        # Check if it's a simple response that could be a customer ID
#         if len(query_lower) < 20 and (query_lower.isdigit() or 'customer' in query_lower):
#             return True
#             
#         return False
#     
#     def _create_customer_id_response_intent(self, query: str, conversation_context: List[Dict]) -> Any:
#         """Create an intent result for customer ID responses"""
#         from google_ads_new.intent_mapping_service import IntentMappingResult, DateRange, Filter
#         
        # Extract customer ID from the query
#         customer_id = self._extract_customer_id_from_query(query, [])
#         
        # Try to determine the original intent from conversation context
#         original_intent = "GET_PERFORMANCE"  # Default to performance if we asked for customer ID
#         
#         if conversation_context:
            # Look for keywords in the conversation to determine original intent
#             context_text = " ".join([msg['content'] for msg in conversation_context[-3:]])
#             context_lower = context_text.lower()
#             
#             if any(word in context_lower for word in ['campaign', 'campaigns']):
#                 original_intent = "GET_CAMPAIGNS"
#             elif any(word in context_lower for word in ['ad', 'ads']):
#                 original_intent = "GET_ADS"
#             elif any(word in context_lower for word in ['overview', 'summary']):
#                 original_intent = "GET_OVERVIEW"
#             elif any(word in context_lower for word in ['performance', 'metrics', 'data']):
#                 original_intent = "GET_PERFORMANCE"
#         
#         return IntentMappingResult(
#             actions=[original_intent],
#             date_ranges=[],
#             filters=[],
#             confidence=0.95,
#             reasoning=f"Detected customer ID response '{query}' for previous {original_intent} query",
#             parameters={"customer_id": customer_id} if customer_id else {}
#         )
# 
#     def _get_accessible_customers(self, user) -> List[str]:
#         """Get accessible customers for a user"""
#         accessible_customers = []
#         try:
#             from accounts.models import UserGoogleAuth
#             google_auth_records = UserGoogleAuth.objects.filter(
#                 user=user,
#                 is_active=True
#             ).exclude(accessible_customers__isnull=True)
#             
#             for auth_record in google_auth_records:
#                 if auth_record.accessible_customers and isinstance(auth_record.accessible_customers, dict):
#                     customers = auth_record.accessible_customers.get("customers", [])
#                     if customers:
#                         accessible_customers.extend(customers)
#             
#             accessible_customers = sorted(list(set(accessible_customers)))
#             
#         except Exception as e:
#             logger.error(f"Error fetching accessible customer IDs: {e}")
#             
#         return accessible_customers
# 
# 
# 
# 
# In RagChat3View , 
# we will take the user query
#  -> then send it to chat gpt with tools to map the query to intent actions
#       -> intent actions are GET_CAMPAIGNS, GET_AD_GROUPS, GET_KEYWORDS, GET_PERFORMANCE and all the GET or UPDATE or POST actions with date_range , and various filters . 
#       -> then we will use the LLMOrchestrator to handle the chat messages
#       -> the LLMOrchestrator will use the intent actions to fetch the data from the Google Ads API
#       -> then we will return the data to the user
#       -> the data will be returned in a structured format
#       -> the data will be returned in a structured form;;;;;;;'[///////////////////////////////////////////////
# class RagChat3View(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]
# 
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.intent_mapping_to_data_service = get_intent_mapping_to_data_service()
#         self.llm_orchestrator = LLMOrchestrator()
# 
#     def post(self, request):
#         """Handle chat messages with conversation persistence"""
#         try:
            # Extract request data
#             query = request.data.get('query', '').strip()
#             conversation_id = request.data.get('conversation_id', None)
#             
#             if not query:
#                 return Response({
#                     "error": "Query is required"
#                 }, status=400)
# 
            # Get or create conversation
#             if conversation_id:
#                 try:
#                     conversation = Conversation.objects.get(
#                         id=conversation_id, 
#                         user=request.user
#                     )
#                 except Conversation.DoesNotExist:
#                     conversation = None
#             else:
#                 conversation = None
#                 
#             if not conversation:
#                 conversation = Conversation.objects.create(
#                     user=request.user,
#                     title=f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
#                     customer_id=None
#                 )
#             
#             
            # Get conversation history for context
#             chat_history = self._build_chat_history(conversation)
#             
            # Check if this is a context question that should be handled directly
#             context_response = self._handle_context_question(query, conversation, chat_history)
#             if context_response:
#                 return Response(context_response)
#             
            # Call intent mapping service with chat history
#             data_intent_mapping_result = self.intent_mapping_to_data_service.map_query_to_intents(
#                 query, 
#                 user_context=None, 
#                 chat_history=chat_history
#             )
#             
            # Save assistant response
#             assistant_message = ChatMessage.objects.create(
#                 conversation=conversation,
#                 role='assistant',
#                 content=json.dumps(data_intent_mapping_result.to_dict()),
#                 response_type='intent_mapping',
#                 structured_data=data_intent_mapping_result.to_dict()
#             )
#             
            # Check if customer_id is already selected in this conversation
#             customer_id_selected = self._is_customer_id_selected(conversation)
#             
            # use the data intent mapping result to fetch the data from the Google Ads API via tools
#             result = self.llm_orchestrator.process_query(query, request.user.id, data_intent_mapping_result.to_dict())
# 
            # Get accessible customers for potential selection
#             accessible_customers = self._get_accessible_customers(request.user)
#             
            # Check if user input is a customer selection
#             customer_selection_processed = False
#             pending_task_executed = False
#             
#             if not customer_id_selected and accessible_customers:
#                 customer_selection_processed = self._process_customer_selection(conversation, query, accessible_customers)
#                 if customer_selection_processed:
                    # Refresh the conversation to get updated customer_id
#                     conversation.refresh_from_db()
#                     customer_id_selected = True
#                     
                    # Check if there's a pending task to execute
#                     if conversation.pending_query and conversation.pending_intent_result:
                        # Execute the pending task
#                         pending_task_executed = True
                        # Update the intent mapping result with the pending one
#                         data_intent_mapping_result = self.intent_mapping_to_data_service._parse_openai_data_mapping_response(
#                             json.dumps(conversation.pending_intent_result), 
#                             conversation.pending_query
#                         )
                        # Clear the pending task
#                         conversation.pending_query = None
#                         conversation.pending_intent_result = None
#                         conversation.save()
#             
            # Build the main message content based on customer selection status
#             if customer_selection_processed:
#                 if pending_task_executed:
                    # Customer was selected and pending task executed - show intent mapping message
#                     main_message = IntentMappingMessageBuilder.build_intent_mapping_message(
#                         data_intent_mapping_result.to_dict()
#                     )
                    # Add a note about customer selection
#                     main_message['content'].insert(0, {
#                         "type": "alert",
#                         "content": {
#                             "message": f"Account {conversation.customer_id} selected. Executing your previous request...",
#                             "type": "success"
#                         },
#                         "order": 0,
#                         "metadata": {}
#                     })
                    # Reorder all items
#                     for i, item in enumerate(main_message['content']):
#                         item['order'] = i
#                 else:
                    # Customer was just selected - show confirmation message
#                     main_message = CustomerSelectionMessageBuilder.build_selection_confirmation_message(conversation.customer_id)
#                 
#                 response_data = {
#                     'conversation_id': conversation.id,
#                     'intent_mapping_result': data_intent_mapping_result.to_dict(),
#                     'message_id': assistant_message.id,
#                     'message': main_message,
#                     'customer_selection_required': False,
#                     'selected_customer_id': conversation.customer_id
#                 }
#             elif not customer_id_selected:
                # No customer selected yet - store pending task and show selection message
                # Store the pending query and intent result for later execution
#                 conversation.pending_query = query
#                 conversation.pending_intent_result = data_intent_mapping_result.to_dict()
#                 conversation.save()
#                 
#                 if accessible_customers:
#                     main_message = self._format_customer_selection_message(accessible_customers)
#                     response_data = {
#                         'conversation_id': conversation.id,
#                         'intent_mapping_result': data_intent_mapping_result.to_dict(),
#                         'message_id': assistant_message.id,
#                         'message': main_message,
#                         'customer_selection_required': True,
#                         'accessible_customers': accessible_customers
#                     }
#                 else:
#                     main_message = CustomerSelectionMessageBuilder.build_no_accounts_message()
#                     response_data = {
#                         'conversation_id': conversation.id,
#                         'intent_mapping_result': data_intent_mapping_result.to_dict(),
#                         'message_id': assistant_message.id,
#                         'message': main_message,
#                         'customer_selection_required': True
#                     }
#             else:
                # Customer already selected - clear any pending tasks and show intent mapping message
#                 if conversation.pending_query or conversation.pending_intent_result:
#                     conversation.pending_query = None
#                     conversation.pending_intent_result = None
#                     conversation.save()
#                 
#                 main_message = IntentMappingMessageBuilder.build_intent_mapping_message(
#                     data_intent_mapping_result.to_dict()
#                 )
#                 
                # Get selected customer ID from Redis or database
#                 selected_customer_id = conversation.customer_id
#                 redis_data = RedisService.get_customer_id(conversation.user.id, conversation.id)
#                 if redis_data and redis_data.get('customer_id'):
#                     selected_customer_id = redis_data['customer_id']
#                 
#                 response_data = {
#                     'conversation_id': conversation.id,
#                     'intent_mapping_result': data_intent_mapping_result.to_dict(),
#                     'message_id': assistant_message.id,
#                     'message': main_message,
#                     'customer_selection_required': False,
#                     'selected_customer_id': selected_customer_id
#                 }
#             
#             return Response(response_data)
#             
#         except Exception as e:
#             logger.error(f"Error in RagChat3View: {str(e)}")
#             return Response({
#                 'error': 'An error occurred while processing your request',
#                 'details': str(e)
#             }, status=500)
#     
#     def _build_chat_history(self, conversation: Conversation) -> List[Dict[str, Any]]:
#         """Build chat history from conversation messages"""
#         try:
            # Get last 20 messages from the conversation
#             messages = conversation.messages.order_by('-created_at')[:100]
#             
            # Build chat history in the format expected by OpenAI
#             chat_history = [
#                 {
#                     "role": "system",
#                     "content": "You are a Google Ads and Meta Ads account expert assistant. You help users analyze their advertising campaigns and provide insights."
#                 }
#             ]
#             
            # Add conversation messages in chronological order
#             for message in reversed(messages):
#                 if message.role in ['user', 'assistant']:
#                     chat_history.append({
#                         "role": message.role,
#                         "content": message.content
#                     })
#             
#             return chat_history
#             
#         except Exception as e:
#             logger.error(f"Error building chat history: {e}")
#             return [
#                 {
#                     "role": "system",
#                     "content": "You are a Google Ads and Meta Ads account expert assistant."
#                 }
#             ]
#     
#     def _get_accessible_customers(self, user) -> List[str]:
#         """Get accessible customer IDs for the user"""
#         try:
            # First check Redis cache
#             cached_customers = RedisService.get_accessible_customers(user.id)
#             if cached_customers is not None:
#                 logger.info(f"Retrieved {len(cached_customers)} accessible customers from Redis for user {user.id}")
#                 return cached_customers
#             
            # If not in cache, fetch from database
#             from accounts.models import UserGoogleAuth
#             
            # Get all active Google Auth records for the user
#             google_auth_records = UserGoogleAuth.objects.filter(
#                 user=user,
#                 is_active=True
#             ).exclude(accessible_customers__isnull=True)
#             
#             accessible_customers = []
#             for auth_record in google_auth_records:
#                 if auth_record.accessible_customers and isinstance(auth_record.accessible_customers, dict):
                    # Extract customer IDs from the dictionary structure
#                     customers = auth_record.accessible_customers.get('customers', [])
#                     if customers:
#                         accessible_customers.extend(customers)
#             
            # Remove duplicates and sort
#             accessible_customers = sorted(list(set(accessible_customers)))
#             
            # Cache the results in Redis
#             RedisService.save_accessible_customers(user.id, accessible_customers)
#             
#             logger.info(f"Found {len(accessible_customers)} accessible customer IDs for user {user.id} and cached in Redis")
#             return accessible_customers
#             
#         except Exception as e:
#             logger.error(f"Error fetching accessible customer IDs: {e}")
#             return []
#     
#     def _is_customer_id_selected(self, conversation: Conversation) -> bool:
#         """Check if a customer_id has been selected for this conversation"""
        # First check Redis for faster access
#         redis_data = RedisService.get_customer_id(conversation.user.id, conversation.id)
#         if redis_data and redis_data.get('customer_id'):
#             return True
#         
        # Fallback to database check
#         return conversation.customer_id is not None and conversation.customer_id.strip() != ""
#     
#     def _format_customer_selection_message(self, accessible_customers: List[str]) -> Dict[str, Any]:
#         """Format accessible customers into a structured message"""
#         if not accessible_customers:
#             return CustomerSelectionMessageBuilder.build_no_accounts_message()
#         
#         if len(accessible_customers) == 1:
#             return CustomerSelectionMessageBuilder.build_single_account_message(accessible_customers[0])
#         
#         return CustomerSelectionMessageBuilder.build_multiple_accounts_message(accessible_customers)
#     
#     def _handle_context_question(self, query: str, conversation: Conversation, chat_history: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
#         """Handle context questions about the current conversation state"""
#         query_lower = query.lower().strip()
#         
        # Check if asking about selected customer ID
#         customer_questions = [
#             "what customer", "which customer", "selected customer", "chosen customer",
#             "what account", "which account", "selected account", "chosen account",
#             "customer id", "account id", "what is the customer", "what is the account",
#             "show me the customer", "show me the account", "tell me the customer", "tell me the account"
#         ]
#         
#         if any(phrase in query_lower for phrase in customer_questions):
#             return self._handle_customer_context_question(conversation, query)
#         
        # Check if asking about conversation state
#         state_questions = [
#             "what did we", "what was", "previous", "earlier", "before", "last", "recent",
#             "what happened", "what did you", "what did i", "show me what", "tell me what"
#         ]
#         
#         if any(phrase in query_lower for phrase in state_questions):
#             return self._handle_conversation_state_question(conversation, chat_history, query)
#         
        # Check if asking about available actions or help
#         help_questions = [
#             "what can you", "what can i", "help", "how to", "how do i", "what should i",
#             "available", "options", "commands", "what are the"
#         ]
#         
#         if any(phrase in query_lower for phrase in help_questions):
#             return self._handle_help_question(conversation, query)
#         
#         return None
#     
#     def _handle_customer_context_question(self, conversation: Conversation, query: str) -> Dict[str, Any]:
#         """Handle questions about the selected customer ID"""
        # Get selected customer ID from Redis or database
#         customer_id = conversation.customer_id
#         redis_data = RedisService.get_customer_id(conversation.user.id, conversation.id)
#         if redis_data and redis_data.get('customer_id'):
#             customer_id = redis_data['customer_id']
#         
#         if customer_id:
            # Build response message
#             builder = MessageBuilder()
#             builder.add_alert(
#                 f"The selected Google Ads account for this conversation is: **{customer_id}**",
#                 alert_type="info",
#                 order=1
#             )
#             builder.add_text(
#                 "You can ask me to analyze campaigns, keywords, or performance data for this account.",
#                 order=2
#             )
#             
#             main_message = builder.to_dict(message_type="info", title="Selected Account")
#             
            # Save assistant message
#             assistant_message = ChatMessage.objects.create(
#                 conversation=conversation,
#                 role='assistant',
#                 content=f"Selected customer ID: {customer_id}",
#                 response_type='context_response',
#                 structured_data={"customer_id": customer_id}
#             )
#             
#             return {
#                 'conversation_id': conversation.id,
#                 'intent_mapping_result': {
#                     "action_groups": [],
#                     "confidence": 1.0,
#                     "reasoning": "Context question about selected customer",
#                     "total_actions": 0,
#                     "query": query
#                 },
#                 'message_id': assistant_message.id,
#                 'message': main_message,
#                 'customer_selection_required': False,
#                 'selected_customer_id': customer_id
#             }
#         else:
            # No customer selected
#             builder = MessageBuilder()
#             builder.add_alert(
#                 "No Google Ads account has been selected for this conversation yet.",
#                 alert_type="warning",
#                 order=1
#             )
#             builder.add_text(
#                 "Please select an account first by asking me to analyze your campaigns or other data.",
#                 order=2
#             )
#             
#             main_message = builder.to_dict(message_type="info", title="No Account Selected")
#             
            # Save assistant message
#             assistant_message = ChatMessage.objects.create(
#                 conversation=conversation,
#                 role='assistant',
#                 content="No customer ID selected",
#                 response_type='context_response',
#                 structured_data={"customer_id": None}
#             )
#             
#             return {
#                 'conversation_id': conversation.id,
#                 'intent_mapping_result': {
#                     "action_groups": [],
#                     "confidence": 1.0,
#                     "reasoning": "Context question about selected customer",
#                     "total_actions": 0,
#                     "query": query
#                 },
#                 'message_id': assistant_message.id,
#                 'message': main_message,
#                 'customer_selection_required': True
#             }
#     
#     def _handle_conversation_state_question(self, conversation: Conversation, chat_history: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
#         """Handle questions about conversation state and history"""
        # Extract recent actions from chat history
#         recent_actions = []
#         recent_queries = []
#         
#         for message in reversed(chat_history[-10:]):  # Last 10 messages
#             if message.get("role") == "user":
#                 recent_queries.append(message.get("content", ""))
#             elif message.get("role") == "assistant" and message.get("content"):
#                 try:
#                     content = json.loads(message["content"]) if isinstance(message["content"], str) else message["content"]
#                     if isinstance(content, dict) and "action_groups" in content:
#                         actions = content.get("action_groups", [])
#                         for group in actions:
#                             recent_actions.extend(group.get("actions", []))
#                 except:
#                     pass
#         
#         builder = MessageBuilder()
#         
#         if recent_actions:
#             builder.add_heading("Recent Actions", level=2, order=1)
#             builder.add_text("Here are the recent actions from our conversation:", order=2)
#             builder.add_bullet_list([f"• {action}" for action in set(recent_actions)], order=3)
#         else:
#             builder.add_text("I don't have any recent actions to show from our conversation.", order=1)
#         
#         if recent_queries:
#             builder.add_subheading("Recent Queries", order=4)
#             builder.add_bullet_list([f"• {q}" for q in recent_queries[-5:]], order=5)  # Last 5 queries
#         
#         main_message = builder.to_dict(message_type="info", title="Conversation History")
#         
        # Save assistant message
#         assistant_message = ChatMessage.objects.create(
#             conversation=conversation,
#             role='assistant',
#             content="Context question about conversation history",
#             response_type='context_response',
#             structured_data={"recent_actions": recent_actions, "recent_queries": recent_queries}
#         )
#         
#         return {
#             'conversation_id': conversation.id,
#             'intent_mapping_result': {
#                 "action_groups": [],
#                 "confidence": 1.0,
#                 "reasoning": "Context question about conversation history",
#                 "total_actions": 0,
#                 "query": query
#             },
#             'message_id': assistant_message.id,
#             'message': main_message,
#             'customer_selection_required': False,
#             'selected_customer_id': conversation.customer_id
#         }
#     
#     def _handle_help_question(self, conversation: Conversation, query: str) -> Dict[str, Any]:
#         """Handle help and guidance questions"""
#         builder = MessageBuilder()
#         
#         builder.add_heading("How I Can Help You", level=2, order=1)
#         builder.add_text("I can help you analyze your Google Ads and Meta Ads data. Here's what you can ask me:", order=2)
#         
#         builder.add_subheading("Campaign Analysis", order=3)
#         builder.add_bullet_list([
#             "Show me my campaign performance",
#             "Which campaigns are performing best?",
#             "Compare campaign performance over time"
#         ], order=4)
#         
#         builder.add_subheading("Keyword Analysis", order=5)
#         builder.add_bullet_list([
#             "Show me my top keywords",
#             "Which keywords have the highest CTR?",
#             "Find underperforming keywords"
#         ], order=6)
#         
#         builder.add_subheading("Account Management", order=7)
#         builder.add_bullet_list([
#             "What customer ID is selected?",
#             "Show me available accounts",
#             "Switch to a different account"
#         ], order=8)
#         
#         main_message = builder.to_dict(message_type="info", title="Help & Guidance")
#         
        # Save assistant message
#         assistant_message = ChatMessage.objects.create(
#             conversation=conversation,
#             role='assistant',
#             content="Help question answered",
#             response_type='context_response',
#             structured_data={"help_type": "general"}
#         )
#         
#         return {
#             'conversation_id': conversation.id,
#             'intent_mapping_result': {
#                 "action_groups": [],
#                 "confidence": 1.0,
#                 "reasoning": "Help question about available actions",
#                 "total_actions": 0,
#                 "query": query
#             },
#             'message_id': assistant_message.id,
#             'message': main_message,
#             'customer_selection_required': False,
#             'selected_customer_id': conversation.customer_id
#         }
#     
#     def _process_customer_selection(self, conversation: Conversation, user_input: str, accessible_customers: List[str]) -> bool:
#         """Process customer selection from user input"""
#         try:
#             selected_customer = None
#             
            # Try to parse as number (1, 2, 3, etc.)
#             if user_input.strip().isdigit():
#                 selection_index = int(user_input.strip()) - 1
#                 if 0 <= selection_index < len(accessible_customers):
#                     selected_customer = accessible_customers[selection_index]
#             
            # Try to match full customer ID
#             elif user_input.strip() in accessible_customers:
#                 selected_customer = user_input.strip()
#             
#             if selected_customer:
                # Save to database
#                 conversation.customer_id = selected_customer
#                 conversation.save()
#                 
                # Save to Redis for faster access
#                 RedisService.save_customer_id(
#                     user_id=conversation.user.id,
#                     conversation_id=conversation.id,
#                     customer_id=selected_customer,
#                     accessible_customers=accessible_customers
#                 )
#                 
#                 logger.info(f"Customer {selected_customer} selected and saved to Redis for conversation {conversation.id}")
#                 return True
#             
#             return False
#             
#         except Exception as e:
#             logger.error(f"Error processing customer selection: {e}")
#             return False
# 
# 
class ConversationHistoryView(APIView):
    """API endpoint to retrieve conversation history"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, conversation_id=None):
        """Get conversation history"""
        try:
            if conversation_id:
                # Get specific conversation
                try:
                    conversation = Conversation.objects.get(
                        id=conversation_id,
                        user=request.user
                    )
                    conversations = [conversation]
                except Conversation.DoesNotExist:
                    return Response({
                        'error': 'Conversation not found'
                    }, status=404)
            else:
                # Get all conversations for the user
                conversations = Conversation.objects.filter(
                    user=request.user
                ).order_by('-updated_at')[:50]  # Limit to last 50 conversations
            
            # Serialize conversations
            conversation_data = []
            for conv in conversations:
                messages = conv.messages.order_by('created_at')
                conversation_data.append({
                    'id': conv.id,
                    'title': conv.title,
                    'customer_id': conv.customer_id,
                    'created_at': conv.created_at.isoformat(),
                    'updated_at': conv.updated_at.isoformat(),
                    'message_count': messages.count(),
                    'messages': [
                        {
                            'id': msg.id,
                            'role': msg.role,
                            'content': msg.content,
                            'response_type': msg.response_type,
                            'structured_data': msg.structured_data,
                            'created_at': msg.created_at.isoformat()
                        }
                        for msg in messages
                    ]
                })
            
            return Response({
                'conversations': conversation_data,
                'total_count': len(conversation_data)
            })
            
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {str(e)}")
            return Response({
                'error': 'An error occurred while retrieving conversation history',
                'details': str(e)
            }, status=500)
    
    def delete(self, request, conversation_id):
        """Delete a conversation"""
        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
                user=request.user
            )
            conversation.delete()
            
            return Response({
                'message': 'Conversation deleted successfully'
            })
            
        except Conversation.DoesNotExist:
            return Response({
                'error': 'Conversation not found'
            }, status=404)
        except Exception as e:
            logger.error(f"Error deleting conversation: {str(e)}")
            return Response({
                'error': 'An error occurred while deleting the conversation',
                'details': str(e)
            }, status=500)




#using langchain
from typing import Annotated, TypedDict, Dict, Any, List, Optional
import os
import json

from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from langgraph.prebuilt import tools_condition, ToolNode
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END

# Try to import PostgresSaver, but make it optional
try:
    from langgraph.checkpoint.postgres import PostgresSaver
    POSTGRES_SAVER_AVAILABLE = True
except ImportError:
    PostgresSaver = None
    POSTGRES_SAVER_AVAILABLE = False
    logger.warning("PostgresSaver not available. Long-term memory will use Redis and database only.")
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

class State(TypedDict):
    messages : Annotated[list, add_messages]
    

# Import all Google Ads tools
from .tools import ALL_TOOLS, TOOL_MAPPING

tools = ALL_TOOLS

# Try to import IPython display functions, but make them optional
try:
    from IPython.display import Image, display
    IPYTHON_AVAILABLE = True
except ImportError:
    # Create dummy functions if IPython is not available
    def Image(*args, **kwargs):
        return None
    def display(*args, **kwargs):
        pass
    IPYTHON_AVAILABLE = False

class LangChainView(APIView):  
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.llm = init_chat_model("gpt-4o")
        self.llm_with_tools = self.llm.bind_tools(tools)

        def chat_node(state: State) -> State:
            return {"message": self.llm_with_tools.invoke(state["messages"])}

        self.builder = StateGraph(State)
        self.builder.add_node(chat_node);
        self.builder.add_node("tools", ToolNode(tools))
        self.builder.add_edge(START,"chat_node")
        self.builder.add_conditional_edges( "chat_node", tools_condition)
        self.builder.add_edge("tools", "chat_node")

        self.graph = self.builder.compile()

        if IPYTHON_AVAILABLE:
            try:
                display(Image(self.graph.get_graph().draw_mermaid_png()))
            except Exception:
                # This requires some extra dependencies and is optional
                pass
        


    def post(self, request):
        """Handle LangChain request"""
        try:
            data = request.data
            print(f"🔍 DEBUG: LangChain request data: {data}")
            query = data.get('query', '')
            conversation_id = data.get('conversation_id', '')
            user_id = data.get('user_id', '')
            
            message ={
                "role":"user",
                "content":query
            }
            response = self.graph.invoke({"messages":[message]})
            return Response({"message": response}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in LangChain request: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LangGraphState(TypedDict):
    """State for LangGraph workflow"""
    messages: Annotated[List[Any], add_messages]
    user_id: int
    conversation_id: Optional[str]
    customer_id: Optional[str]
    accessible_customers: List[str]
    user_context: Dict[str, Any]
    current_step: str
    error_count: int
    max_retries: int


class LanggraphView(APIView):
    """
    Advanced LangGraph view with continuous feedback loops, 
    short-term memory (checkpoints), and long-term memory (PostgresStore)
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.llm = init_chat_model("gpt-4o")
        self.llm_with_tools = self.llm.bind_tools(ALL_TOOLS)
        
        # Initialize checkpointer for short-term memory
        self.checkpointer = MemorySaver()
        
        # Initialize PostgresStore for long-term memory
        self._init_postgres_store()
        
        # Build the state graph
        self._build_graph()
    
    def _init_postgres_store(self):
        """Initialize PostgresStore for long-term memory"""
        try:
            if not POSTGRES_SAVER_AVAILABLE:
                self.postgres_store = None
                logger.info("PostgresSaver not available, using Redis and database for long-term memory")
                return
            
            # Get database URL from Django settings
            from django.conf import settings
            
            # Use Django's database configuration
            db_config = settings.DATABASES['default']
            if db_config['ENGINE'] == 'django.db.backends.postgresql':
                db_url = f"postgresql://{db_config['USER']}:{db_config['PASSWORD']}@{db_config['HOST']}:{db_config['PORT']}/{db_config['NAME']}"
                self.postgres_store = PostgresSaver.from_conn_string(db_url)
                logger.info("PostgresStore initialized successfully for long-term memory")
            else:
                # Fallback to in-memory store if not PostgreSQL
                self.postgres_store = None
                logger.warning("PostgresStore not available, using Redis and database for long-term memory")
                
        except Exception as e:
            logger.error(f"Error initializing PostgresStore: {e}")
            self.postgres_store = None
    
    def _build_graph(self):
        """Build the LangGraph state graph with nodes and edges"""
        # Define nodes
        def chat_node(state: LangGraphState) -> LangGraphState:
            """Main chat node that processes user messages with LLM"""
            try:
                # Add system message with context at the beginning
                system_message = SystemMessage(content=self._build_system_prompt(state))
                
                # Combine system message with conversation history
                # Don't duplicate system messages if they already exist
                messages = state["messages"].copy()  # Make a copy to avoid modifying the original
                if not messages or not isinstance(messages[0], SystemMessage):
                    messages = [system_message] + messages
                else:
                    # Update existing system message with current context
                    messages[0] = system_message
                
                # Log conversation context for debugging
                logger.info(f"Chat node processing {len(messages)} messages")
                logger.info(f"Current customer_id: {state.get('customer_id')}")
                logger.info(f"User query context preserved: {any('analyze' in str(msg.content).lower() or 'campaign' in str(msg.content).lower() for msg in messages if hasattr(msg, 'content'))}")
                
                # Get LLM response
                response = self.llm_with_tools.invoke(messages)
                
                return {
                    "messages": [response],  # This will be appended to existing messages by add_messages
                    "current_step": "chat_completed"
                }
            except Exception as e:
                logger.error(f"Error in chat_node: {e}")
                error_message = AIMessage(content=f"I encountered an error: {str(e)}")
                return {
                    "messages": [error_message],
                    "current_step": "error",
                    "error_count": state.get("error_count", 0) + 1
                }
        
        def tool_node(state: LangGraphState) -> LangGraphState:
            """Tool execution node with user_id injection for token refresh"""
            try:
                # Get the last message which should contain tool calls
                last_message = state["messages"][-1]
                
                if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                    # Create a custom tool node that injects user_id
                    user_id = state.get("user_id")
                    
                    # Create tools with user_id injection
                    enhanced_tools = self._create_enhanced_tools_with_user_id(user_id)
                    tool_node_instance = ToolNode(enhanced_tools)
                    tool_response = tool_node_instance.invoke({"messages": [last_message]})
                    
                    return {
                        "messages": tool_response["messages"],
                        "current_step": "tools_completed"
                    }
                else:
                    # No tool calls, return as is
                    return {
                        "current_step": "no_tools"
                    }
            except Exception as e:
                logger.error(f"Error in tool_node: {e}")
                error_message = AIMessage(content=f"Tool execution error: {str(e)}")
                return {
                    "messages": [error_message],
                    "current_step": "error",
                    "error_count": state.get("error_count", 0) + 1
                }
        
        def context_node(state: LangGraphState) -> LangGraphState:
            """Node to enrich context with user-specific data and ensure accessible customers are in long-term memory"""
            try:
                # Get user context from long-term memory (this may already include accessible customers)
                user_context = self._get_user_context(state["user_id"])
                
                # Check if we already have accessible customers in long-term memory
                accessible_customers = user_context.get("accessible_customers", [])
                
                if not accessible_customers:
                    # If not in long-term memory, get from database
                    logger.info(f"No accessible customers in long-term memory for user {state['user_id']}, fetching from database")
                    accessible_customers = self._get_accessible_customers(state["user_id"])
                    
                    # Save accessible customers to long-term memory if found
                    if accessible_customers:
                        success = self._save_accessible_customers_to_long_term_memory(
                            state["user_id"], 
                            accessible_customers
                        )
                        if success:
                            logger.info(f"Successfully saved {len(accessible_customers)} accessible customers to long-term memory for user {state['user_id']}")
                        else:
                            logger.warning(f"Failed to save accessible customers to long-term memory for user {state['user_id']}")
                    else:
                        logger.warning(f"No accessible customers found in database for user {state['user_id']}")
                else:
                    logger.info(f"Retrieved {len(accessible_customers)} accessible customers from long-term memory for user {state['user_id']}")
                
                return {
                    "user_context": user_context,
                    "accessible_customers": accessible_customers,
                    "current_step": "context_enriched"
                }
            except Exception as e:
                logger.error(f"Error in context_node: {e}")
                return {
                    "current_step": "context_error",
                    "error_count": state.get("error_count", 0) + 1
                }
        
        def data_analysis_node(state: LangGraphState) -> LangGraphState:
            """Node to analyze fetched data using GPT-4o and generate insights/reports"""
            try:
                # Get the last tool results from the conversation
                tool_results = []
                for msg in reversed(state["messages"]):
                    if hasattr(msg, 'content') and isinstance(msg, AIMessage):
                        # Look for tool call results in the message content
                        if "tool_call" in str(msg.content) or "campaign" in str(msg.content).lower():
                            tool_results.append(msg.content)
                        if len(tool_results) >= 3:  # Get last few tool results
                            break
                
                # Always provide analysis, even without tool results
                if not tool_results:
                    # No tool results - provide general analysis based on user query
                    analysis_prompt = f"""
                    The user asked: "{user_query}"

                    Since no specific data was retrieved, provide a comprehensive analysis and recommendations based on your expertise:

                    Please provide:
                    1. **General Analysis** - What this query typically involves
                    2. **Best Practices** - Industry standards and recommendations
                    3. **Strategic Insights** - How to approach this topic
                    4. **Actionable Steps** - What the user should consider
                    5. **Additional Considerations** - Other factors to keep in mind

                    Format your response as a helpful guide with clear sections and actionable advice.
                    """
                else:
                    # Create analysis prompt with tool results
                    analysis_prompt = f"""
                    You are an expert Google Ads data analyst. Analyze the following data and provide comprehensive insights based on the user's request.

                    User Request: "{user_query}"

                    Data to Analyze:
                    {chr(10).join(tool_results)}

                    Please provide a detailed analysis including:
                    1. Key Performance Metrics
                    2. Trends and Patterns
                    3. Insights and Recommendations
                    4. Actionable Strategies
                    5. Data Summary (present data in clear text format and tables)

                    Format your response as a comprehensive report with clear sections, bullet points, and specific recommendations.
                    """
                
                # Get user query for analysis
                user_query = ""
                for msg in state["messages"]:
                    if isinstance(msg, HumanMessage):
                        user_query = msg.content
                        break
                
                # Use GPT-4o for analysis
                analysis_messages = [
                    SystemMessage(content="You are an expert Google Ads data analyst. Provide detailed, actionable insights based on the data provided."),
                    HumanMessage(content=analysis_prompt)
                ]
                
                analysis_response = self.llm.invoke(analysis_messages)
                
                return {
                    "messages": [analysis_response],
                    "current_step": "analysis_completed"
                }
                
            except Exception as e:
                logger.error(f"Error in data_analysis_node: {e}")
                error_message = AIMessage(content=f"Error analyzing data: {str(e)}")
                return {
                    "messages": [error_message],
                    "current_step": "analysis_error",
                    "error_count": state.get("error_count", 0) + 1
                }
        
        def report_generation_node(state: LangGraphState) -> LangGraphState:
            """Node to generate formatted reports, charts, and visualizations"""
            try:
                # Get the analysis from previous step
                analysis_content = ""
                for msg in reversed(state["messages"]):
                    if isinstance(msg, AIMessage) and "analysis" in str(msg.content).lower():
                        analysis_content = msg.content
                        break
                
                if not analysis_content:
                    return {
                        "current_step": "no_analysis_to_format",
                        "messages": [AIMessage(content="No analysis available to format into a report.")]
                    }
                
                # Create report generation prompt
                report_prompt = f"""
Based on the following analysis, create a comprehensive report with the following sections:

Analysis Content:
{analysis_content}

Please format this into a professional report with:

1. **Executive Summary** - Key findings in 2-3 bullet points
2. **Performance Overview** - Main metrics and KPIs
3. **Detailed Analysis** - In-depth insights
4. **Recommendations** - Actionable next steps
5. **Data Summary** - Present key metrics in clear text and table format

IMPORTANT: Only create visualizations (charts, graphs, images) when specifically requested by the user. 
Use text descriptions and tables as the primary way to present data.

Use clear formatting with headers, bullet points, and structured sections.
Include specific metrics, percentages, and data points in text format.
"""
                
                # Use GPT-4o for report generation
                report_messages = [
                    SystemMessage(content="You are a professional marketing report writer. Create clear, actionable reports with proper formatting."),
                    HumanMessage(content=report_prompt)
                ]
                
                report_response = self.llm.invoke(report_messages)
                
                return {
                    "messages": [report_response],
                    "current_step": "report_completed"
                }
                
            except Exception as e:
                logger.error(f"Error in report_generation_node: {e}")
                error_message = AIMessage(content=f"Error generating report: {str(e)}")
                return {
                    "messages": [error_message],
                    "current_step": "report_error",
                    "error_count": state.get("error_count", 0) + 1
                }
        
        def decision_node(state: LangGraphState) -> str:
            """Decision node to determine next step using LLM intelligence"""
            error_count = state.get("error_count", 0)
            max_retries = state.get("max_retries", 3)
            
            if error_count >= max_retries:
                return "end"
            
            current_step = state.get("current_step", "start")
            
            if current_step == "start":
                return "context"
            elif current_step == "context_enriched":
                return "chat"
            elif current_step == "chat_completed":
                # Check if LLM wants to use tools
                last_message = state["messages"][-1]
                if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                    return "tools"
                else:
                    return "end"
            elif current_step == "tools_completed":
                # After tools are executed, let LLM decide next step
                return "chat"  # Always go back to chat for LLM to decide
            elif current_step == "analysis_completed":
                return "report_generation"  # Generate formatted report after analysis
            elif current_step == "report_completed":
                return "end"  # Analysis and report complete
            elif current_step in ["error", "context_error", "analysis_error", "report_error"]:
                return "chat"  # Try to recover
            else:
                return "end"
        
        # Build the graph
        self.workflow = StateGraph(LangGraphState)
        
        # Add nodes
        self.workflow.add_node("context", context_node)
        self.workflow.add_node("chat", chat_node)
        self.workflow.add_node("tools", tool_node)
        self.workflow.add_node("data_analysis", data_analysis_node)
        self.workflow.add_node("report_generation", report_generation_node)
        
        # Add edges
        self.workflow.add_edge(START, "context")
        
        # Add conditional edges
        self.workflow.add_conditional_edges(
            "context",
            decision_node,
            {
                "chat": "chat",
                "end": END
            }
        )
        
        self.workflow.add_conditional_edges(
            "chat",
            decision_node,
            {
                "tools": "tools",
                "end": END
            }
        )
        
        self.workflow.add_conditional_edges(
            "tools",
            decision_node,
            {
                "chat": "chat",
                "data_analysis": "data_analysis",
                "end": END
            }
        )
        
        self.workflow.add_conditional_edges(
            "data_analysis",
            decision_node,
            {
                "report_generation": "report_generation",
                "chat": "chat",
                "end": END
            }
        )
        
        self.workflow.add_conditional_edges(
            "report_generation",
            decision_node,
            {
                "chat": "chat",
                "end": END
            }
        )
        
        # Compile the graph with checkpointer
        if self.postgres_store:
            self.graph = self.workflow.compile(
                checkpointer=self.checkpointer,
                store=self.postgres_store
            )
            logger.info("Graph compiled with PostgresStore for long-term memory")
        else:
            self.graph = self.workflow.compile(checkpointer=self.checkpointer)
            logger.info("Graph compiled with MemorySaver checkpointer only")
    
    def _create_enhanced_tools_with_user_id(self, user_id: int):
        """Create enhanced tools that automatically inject user_id for token refresh"""
        from langchain_core.tools import StructuredTool
        
        enhanced_tools = []
        
        for original_tool in ALL_TOOLS:
            # Create a wrapper function that injects user_id
            def create_enhanced_tool(original_tool, user_id):
                def enhanced_tool_func(*args, **kwargs):
                    """Enhanced tool function with automatic user_id injection for token refresh"""
                    # Inject user_id if not already present
                    if 'user_id' not in kwargs and user_id is not None:
                        kwargs['user_id'] = user_id
                    return original_tool.func(*args, **kwargs)
                
                # Create new tool with same metadata but enhanced function
                enhanced_tool = StructuredTool.from_function(
                    enhanced_tool_func,
                    name=original_tool.name,
                    description=original_tool.description,
                    args_schema=original_tool.args_schema
                )
                
                return enhanced_tool
            
            enhanced_tool = create_enhanced_tool(original_tool, user_id)
            enhanced_tools.append(enhanced_tool)
        
        return enhanced_tools
    
    def _build_system_prompt(self, state: LangGraphState) -> str:
        """Build system prompt with user context and conversation awareness"""
        # Count messages to understand conversation length
        message_count = len(state.get("messages", []))
        customer_id = state.get("customer_id", "not selected")
        accessible_customers = state.get("accessible_customers", [])
        
        # Extract original user intent from conversation history
        original_intent = ""
        for msg in state.get("messages", []):
            if isinstance(msg, HumanMessage) and not msg.content.startswith("customers/"):
                original_intent = msg.content
                break
        
        # Build customer context
        if customer_id and customer_id != "not selected":
            customer_context = f"SELECTED CUSTOMER: {customer_id} (use this for ALL data requests - DO NOT ask for customer selection again)"
        elif accessible_customers:
            customer_context = f"NO CUSTOMER SELECTED YET. Available customers: {', '.join(accessible_customers)}"
        else:
            customer_context = "NO CUSTOMER INFORMATION AVAILABLE"
        
        # Build original intent context
        intent_context = ""
        if original_intent and not original_intent.startswith("customers/"):
            intent_context = f"ORIGINAL USER REQUEST: '{original_intent}' - You MUST remember and fulfill this request after customer selection."
        
        prompt = """You are an expert Google Ads and Meta Ads assistant. You help users analyze their advertising campaigns and provide comprehensive insights.

CRITICAL RULES:
1. If a customer ID is already selected in the conversation, use it immediately for all data requests. NEVER ask for customer selection again.
2. ALWAYS remember the original user request and fulfill it after any customer selection. Do NOT ask the user to repeat their request.

INTELLIGENT WORKFLOW DECISION:
You have access to 15 powerful tools, but you should use them intelligently:

**USE TOOLS WHEN:**
- User asks for specific Google Ads data (campaigns, ads, keywords, performance, etc.)
- User requests data analysis, comparisons, or insights that require actual data
- User wants images, visualizations, or formatted tables created
- User asks questions that can be answered with concrete data from their accounts

**DON'T USE TOOLS WHEN:**
- User asks general questions about Google Ads concepts, strategies, or best practices
- User asks for explanations, definitions, or educational content
- User asks questions that don't require specific account data
- User asks for general advice or recommendations without data analysis

**WORKFLOW CAPABILITIES:**
1. **Data Fetching**: Use tools to get raw data from Google Ads API
2. **Data Analysis**: Automatically analyze fetched data using GPT-4o for insights
3. **Report Generation**: Create formatted reports with charts, graphs, and recommendations
4. **Image Generation**: Create custom images, posters, and visual content using OpenAI's image generation
5. **Image Improvement**: Modify and enhance existing generated images based on user feedback
6. **Data Visualization**: Create pie charts, bar graphs, line charts, and tables using ChatGPT
7. **Tabular Formatting**: Format data into professional tables with ChatGPT
8. **General Queries**: Answer general questions directly without tools when appropriate

Available tools:
- get_campaigns: Get campaign data
- get_campaign_by_id: Get specific campaign details
- get_ad_groups: Get ad group data
- get_ads: Get ad data
- get_keywords: Get keyword data
- get_performance_data: Get performance metrics
- get_budgets: Get budget information
- get_account_overview: Get account overview
- get_search_terms: Get search terms data
- get_demographic_data: Get demographic insights
- get_geographic_data: Get geographic data
- generate_image: Generate images using OpenAI's image generation API
- improve_image: Improve or modify existing generated images
- create_data_visualization: Create pie charts, bar graphs, line charts using ChatGPT
- format_tabular_data: Format data into professional tables using ChatGPT


When responding, use the appropriate tools to fetch live data and provide comprehensive analysis.

RESPONSE FORMAT: Structure your responses clearly with:
- Clear headings and sections
- Bullet points for key information
- Data tables when presenting metrics
- Action items and recommendations

VISUALIZATION GUIDELINES:
- Only create charts/graphs when specifically requested by the user
- Only suggest visualizations when they would genuinely help explain the data
- Don't automatically create pie charts, bar graphs, or line charts unless asked
- Use text descriptions and tables as the primary way to present data
- Only use create_data_visualization tool when user explicitly asks for charts

INTELLIGENT WORKFLOW DECISION:
You decide when to use tools vs. when to provide direct responses:

**FOR DATA-DRIVEN QUERIES:**
1. Use appropriate tools to fetch data from Google Ads API
2. Analyze the data and provide insights
3. Generate reports, visualizations, or formatted tables as needed
4. Examples: "show my campaigns", "analyze performance", "create a chart"

**FOR GENERAL QUERIES:**
1. Provide direct, helpful responses without tools
2. Share knowledge, best practices, and strategies
3. Answer conceptual questions about Google Ads
4. Examples: "what is ROAS?", "how to improve CTR?", "best practices for campaigns"

**AFTER TOOL EXECUTION:**
- If tools provide data: Analyze and provide insights
- If tools don't provide data: Still provide helpful response using your knowledge
- Always be helpful regardless of tool results

User Context:
- User ID: {user_id}
- {customer_context}
- {intent_context}
- Conversation Length: {message_count} messages

Instructions:
1. **INTELLIGENT TOOL USAGE**: Use tools only when they add value to the response
2. **GENERAL QUERIES**: Answer general questions directly without tools
3. **DATA QUERIES**: Use tools to fetch specific account data when needed
4. **CUSTOMER ID**: If selected, use it for ALL data requests - NEVER ask again
5. **CONTINUITY**: Remember conversation context and build upon it
6. **HELPFULNESS**: Always provide value, whether using tools or not
7. **ERROR RECOVERY**: If tools fail, still provide helpful response
8. **ORIGINAL INTENT**: Fulfill the user's original request completely

WORKFLOW EXAMPLES:
- "What is ROAS?" → Direct answer (no tools needed)
- "Show my campaigns" → Use get_campaigns tool + text analysis
- "How to improve CTR?" → Direct advice (no tools needed)
- "Analyze my performance" → Use tools + text analysis
- "Create a pie chart of my spend" → Use create_data_visualization tool
- "Create a marketing poster" → Use generate_image tool
- "What's my budget?" → Use get_budgets tool + text summary

Current conversation step: {current_step}

IMPORTANT: You have access to the full conversation history. Use it to provide contextually relevant responses and maintain continuity. NEVER ask the user to repeat their original request after customer selection."""

        return prompt.format(
            user_id=state.get("user_id", "unknown"),
            customer_context=customer_context,
            intent_context=intent_context,
            message_count=message_count,
            current_step=state.get("current_step", "start")
        )
    
    def _get_user_context(self, user_id: int) -> Dict[str, Any]:
        """Get user-specific context from long-term memory"""
        try:
            # Try to get context from PostgresStore if available
            if self.postgres_store:
                try:
                    # Check if we have stored accessible customers in long-term memory
                    stored_customers = self._get_accessible_customers_from_long_term_memory(user_id)
                    if stored_customers:
                        logger.info(f"Retrieved {len(stored_customers)} accessible customers from long-term memory for user {user_id}")
                        return {
                            "user_id": user_id,
                            "preferences": {},
                            "recent_queries": [],
                            "favorite_customers": [],
                            "accessible_customers": stored_customers,
                            "from_long_term_memory": True
                        }
                except Exception as e:
                    logger.warning(f"Could not retrieve from long-term memory: {e}")
            
            # Fallback to basic context
            return {
                "user_id": user_id,
                "preferences": {},
                "recent_queries": [],
                "favorite_customers": [],
                "accessible_customers": [],
                "from_long_term_memory": False
            }
        except Exception as e:
            logger.error(f"Error getting user context: {e}")
            return {}
    
    def _get_accessible_customers(self, user_id: int) -> List[str]:
        """Get accessible customer IDs for the user"""
        try:
            from accounts.models import UserGoogleAuth
            
            google_auth_records = UserGoogleAuth.objects.filter(
                user_id=user_id,
                is_active=True
            ).exclude(accessible_customers__isnull=True)
            
            accessible_customers = []
            for auth_record in google_auth_records:
                if auth_record.accessible_customers and isinstance(auth_record.accessible_customers, dict):
                    customers = auth_record.accessible_customers.get('customers', [])
                    if customers:
                        accessible_customers.extend(customers)
            
            return sorted(list(set(accessible_customers)))
            
        except Exception as e:
            logger.error(f"Error getting accessible customers: {e}")
            return []
    
    def _save_accessible_customers_to_long_term_memory(self, user_id: int, accessible_customers: List[str]) -> bool:
        """Save accessible customers to long-term memory using Redis and database"""
        try:
            # First, try to save to Redis for fast access
            try:
                from .redis_service import RedisService
                RedisService.save_accessible_customers(user_id, accessible_customers)
                logger.info(f"Saved {len(accessible_customers)} accessible customers to Redis for user {user_id}")
            except Exception as e:
                logger.warning(f"Could not save to Redis: {e}")
            
            # Also save to database for persistence
            try:
                from django.contrib.auth.models import User
                user = User.objects.get(id=user_id)
                
                # Create or update a UserProfile or similar model to store accessible customers
                # For now, we'll use a simple approach with the existing UserGoogleAuth model
                from accounts.models import UserGoogleAuth
                
                # Get the most recent UserGoogleAuth record for this user
                latest_auth = UserGoogleAuth.objects.filter(
                    user=user,
                    is_active=True
                ).order_by('-created_at').first()
                
                if latest_auth:
                    # Update the existing record with accessible customers
                    if not latest_auth.accessible_customers:
                        latest_auth.accessible_customers = {"customers": accessible_customers}
                        latest_auth.save()
                        logger.info(f"Updated UserGoogleAuth with {len(accessible_customers)} accessible customers for user {user_id}")
                    else:
                        # Merge with existing customers
                        existing_customers = latest_auth.accessible_customers.get('customers', [])
                        all_customers = list(set(existing_customers + accessible_customers))
                        latest_auth.accessible_customers = {"customers": all_customers}
                        latest_auth.save()
                        logger.info(f"Merged and updated UserGoogleAuth with {len(all_customers)} accessible customers for user {user_id}")
                
                # If PostgresStore is available, also save there
                if self.postgres_store:
                    self._save_to_postgres_store(user_id, accessible_customers)
                
                return True
                
            except Exception as e:
                logger.error(f"Error saving to database: {e}")
                return False
            
        except Exception as e:
            logger.error(f"Error saving accessible customers to long-term memory: {e}")
            return False
    
    def _get_accessible_customers_from_long_term_memory(self, user_id: int) -> List[str]:
        """Get accessible customers from long-term memory (Redis, database, PostgresStore)"""
        try:
            # First, try to get from Redis for fast access
            try:
                from .redis_service import RedisService
                cached_customers = RedisService.get_accessible_customers(user_id)
                if cached_customers:
                    logger.info(f"Retrieved {len(cached_customers)} accessible customers from Redis for user {user_id}")
                    return cached_customers
            except Exception as e:
                logger.warning(f"Could not retrieve from Redis: {e}")
            
            # Fallback to database
            try:
                from django.contrib.auth.models import User
                user = User.objects.get(id=user_id)
                
                from accounts.models import UserGoogleAuth
                latest_auth = UserGoogleAuth.objects.filter(
                    user=user,
                    is_active=True
                ).order_by('-created_at').first()
                
                if latest_auth and latest_auth.accessible_customers:
                    customers = latest_auth.accessible_customers.get('customers', [])
                    if customers:
                        logger.info(f"Retrieved {len(customers)} accessible customers from database for user {user_id}")
                        return customers
                        
            except Exception as e:
                logger.warning(f"Could not retrieve from database: {e}")
            
            # If PostgresStore is available, try to get from there
            if self.postgres_store:
                try:
                    customers = self._get_from_postgres_store(user_id)
                    if customers:
                        logger.info(f"Retrieved {len(customers)} accessible customers from PostgresStore for user {user_id}")
                        return customers
                except Exception as e:
                    logger.warning(f"Could not retrieve from PostgresStore: {e}")
            
            return []
            
        except Exception as e:
            logger.error(f"Error retrieving accessible customers from long-term memory: {e}")
            return []
    
    def _save_to_postgres_store(self, user_id: int, accessible_customers: List[str]) -> bool:
        """Save accessible customers to PostgresStore"""
        try:
            if not self.postgres_store:
                return False
            
            # Create a unique key for this user's accessible customers
            user_key = f"user_{user_id}_accessible_customers"
            
            # Prepare data to store
            customer_data = {
                "user_id": user_id,
                "accessible_customers": accessible_customers,
                "timestamp": datetime.now().isoformat(),
                "count": len(accessible_customers)
            }
            
            # Save to PostgresStore using its API
            # Note: The exact API depends on the PostgresStore implementation
            # This is a conceptual implementation
            logger.info(f"Saving {len(accessible_customers)} accessible customers to PostgresStore for user {user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving to PostgresStore: {e}")
            return False
    
    def _get_from_postgres_store(self, user_id: int) -> List[str]:
        """Get accessible customers from PostgresStore"""
        try:
            if not self.postgres_store:
                return []
            
            # Create a unique key for this user's accessible customers
            user_key = f"user_{user_id}_accessible_customers"
            
            # Retrieve from PostgresStore using its API
            # Note: The exact API depends on the PostgresStore implementation
            # This is a conceptual implementation
            logger.info(f"Retrieving accessible customers from PostgresStore for user {user_id}")
            
            return []
            
        except Exception as e:
            logger.error(f"Error retrieving from PostgresStore: {e}")
            return []
    
    def post(self, request):
        """Handle LangGraph requests with conversation persistence"""
        try:
            # Extract request data
            query = request.data.get('query', '').strip()
            conversation_id = request.data.get('conversation_id')
            customer_id = request.data.get('customer_id')
            
            # Debug logging
            logger.info(f"LanggraphView request - User: {request.user.id}, Query: {query[:50]}...")
            logger.info(f"Request data - conversation_id: {conversation_id} (type: {type(conversation_id)}), customer_id: {customer_id}")
            logger.info(f"Request data keys: {list(request.data.keys())}")
            logger.info(f"Full request data: {request.data}")
            
            if not query:
                return Response({
                    'error': 'Query is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get or create conversation
            logger.info(f"Looking up conversation - conversation_id: {conversation_id}, user: {request.user.id}")
            conversation = self._get_or_create_conversation(request.user, conversation_id)
            logger.info(f"Using conversation - ID: {conversation.id}, customer_id: {conversation.customer_id}")
            
            # Load conversation history for context (before saving current message)
            conversation_messages = self._load_conversation_history(conversation)
            
            # Add current user message to the conversation
            conversation_messages.append(HumanMessage(content=query))
            
            # Check if user is selecting a customer ID
            detected_customer_id = self._detect_customer_id_selection(query, conversation_messages)
            if detected_customer_id:
                # Update conversation with selected customer ID
                conversation.customer_id = detected_customer_id
                conversation.save()
                logger.info(f"Updated conversation {conversation.id} with customer ID: {detected_customer_id}")
            
            # Save user message to database
            user_message = ChatMessage.objects.create(
                conversation=conversation,
                role='user',
                content=query
            )
            
            # Get accessible customers for the initial state
            accessible_customers = self._get_accessible_customers(request.user.id)
            
            # Prepare initial state with full conversation history
            initial_state = {
                "messages": conversation_messages,
                "user_id": request.user.id,
                "conversation_id": str(conversation.id),
                "customer_id": conversation.customer_id or customer_id,  # Prioritize stored customer_id
                "accessible_customers": accessible_customers,
                "user_context": {},
                "current_step": "start",
                "error_count": 0,
                "max_retries": 3
            }
            
            # Configure with consistent thread ID for checkpointing
            # Use a stable thread ID that doesn't change with conversation ID
            config: RunnableConfig = {
                "configurable": {
                    "thread_id": f"user_{request.user.id}_langgraph"
                }
            }
            
            # Log the initial state for debugging
            logger.info(f"LangGraph initial state - User: {request.user.id}, Conversation: {conversation.id}")
            logger.info(f"Customer ID: {initial_state['customer_id']}")
            logger.info(f"Accessible Customers: {len(initial_state['accessible_customers'])}")
            logger.info(f"Messages: {len(initial_state['messages'])}")
            
            # Invoke the graph
            logger.info(f"Invoking LangGraph for user {request.user.id}, conversation {conversation.id}")
            result = self.graph.invoke(initial_state, config=config)
            
            # Extract final response
            final_messages = result.get("messages", [])
            if final_messages:
                # Get the last AI message
                last_ai_message = None
                for msg in reversed(final_messages):
                    if isinstance(msg, AIMessage):
                        last_ai_message = msg
                        break
                
                if last_ai_message:
                    response_content = last_ai_message.content
                else:
                    response_content = "I processed your request but couldn't generate a response."
            else:
                response_content = "I processed your request but couldn't generate a response."
            
            # Save assistant response
            assistant_message = ChatMessage.objects.create(
                conversation=conversation,
                role='assistant',
                content=response_content,
                response_type='langgraph_response',
                structured_data={
                    'langgraph_result': {
                        'current_step': result.get('current_step'),
                        'error_count': result.get('error_count', 0),
                        'user_context': result.get('user_context', {}),
                        'accessible_customers': result.get('accessible_customers', [])
                    }
                }
            )
            
            # Update conversation
            conversation.updated_at = datetime.now()
            if customer_id and not conversation.customer_id:
                conversation.customer_id = customer_id
            conversation.save()
            
            return Response({
                'message_id': assistant_message.id,
                'conversation_id': conversation.id,
                'response': response_content,
                'langgraph_state': {
                    'current_step': result.get('current_step'),
                    'error_count': result.get('error_count', 0),
                    'accessible_customers': result.get('accessible_customers', [])
                },
                'timestamp': assistant_message.created_at.isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error in LanggraphView: {e}")
            return Response({
                'error': f'An error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _detect_customer_id_selection(self, query: str, conversation_messages: List) -> Optional[str]:
        """Detect if user is selecting a customer ID from a list"""
        try:
            # Check if the query looks like a customer ID selection
            query_lower = query.lower().strip()
            
            # Pattern 1: Direct customer ID format (customers/1234567890)
            if query_lower.startswith('customers/'):
                return query_lower
            
            # Pattern 2: Just the customer ID number
            if query_lower.isdigit() and len(query_lower) >= 8:
                return f"customers/{query_lower}"
            
            # Pattern 3: Check if previous assistant message asked for customer selection
            if conversation_messages:
                last_assistant_message = None
                for msg in reversed(conversation_messages):
                    if isinstance(msg, AIMessage):
                        last_assistant_message = msg.content
                        break
                
                if last_assistant_message:
                    # Check if assistant asked for customer selection
                    if any(phrase in last_assistant_message.lower() for phrase in [
                        'select one of your accessible customer',
                        'please specify which customer',
                        'choose one of these customer',
                        'which customer account you'
                    ]):
                        # Check if user response matches a customer ID pattern
                        if 'customers/' in query_lower or query_lower.isdigit():
                            if query_lower.startswith('customers/'):
                                return query_lower
                            elif query_lower.isdigit():
                                return f"customers/{query_lower}"
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting customer ID selection: {e}")
            return None
    
    def _load_conversation_history(self, conversation):
        """Load conversation history as LangChain messages"""
        try:
            # Get last 20 messages from the conversation for context
            messages = conversation.messages.all().order_by('created_at')[:20]
            
            conversation_messages = []
            
            for msg in messages:
                if msg.role == 'user':
                    conversation_messages.append(HumanMessage(content=msg.content))
                elif msg.role == 'assistant':
                    conversation_messages.append(AIMessage(content=msg.content))
                elif msg.role == 'system':
                    conversation_messages.append(SystemMessage(content=msg.content))
            
            logger.info(f"Loaded {len(conversation_messages)} messages from conversation history")
            return conversation_messages
            
        except Exception as e:
            logger.error(f"Error loading conversation history: {e}")
            return []
    
    def _get_or_create_conversation(self, user, conversation_id=None):
        """Get existing conversation or create new one"""
        if conversation_id:
            try:
                # Convert to int if it's a string
                if isinstance(conversation_id, str):
                    conversation_id = int(conversation_id)
                
                conversation = Conversation.objects.get(
                    id=conversation_id,
                    user=user,
                    deleted_at__isnull=True
                )
                logger.info(f"Found existing conversation {conversation.id} with customer_id: {conversation.customer_id}")
                return conversation
            except (Conversation.DoesNotExist, ValueError) as e:
                logger.warning(f"Could not find conversation {conversation_id}: {e}")
                pass
        
        # Create new conversation
        new_conversation = Conversation.objects.create(
            user=user,
            title=f"LangGraph Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        logger.info(f"Created new conversation {new_conversation.id}")
        return new_conversation


class RecentConversationsView(APIView):
    """
    API endpoint to get top 10 recent conversations with 2 chat messages each
    for the frontend's previous conversations tab
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get recent conversations with preview messages"""
        try:
            user = request.user
            
            # Get top 10 recent conversations for the user
            recent_conversations = Conversation.objects.filter(
                user=user
            ).order_by('-created_at')[:10]
            
            conversations_data = []
            
            for conversation in recent_conversations:
                # Get the first 2 messages for preview
                preview_messages = ChatMessage.objects.filter(
                    conversation=conversation
                ).order_by('created_at')[:2]
                
                # Format messages for frontend
                messages_preview = []
                for msg in preview_messages:
                    messages_preview.append({
                        'id': msg.id,
                        'role': msg.role,
                        'content': msg.content[:200] + '...' if len(msg.content) > 200 else msg.content,
                        'created_at': msg.created_at.isoformat(),
                        'is_truncated': len(msg.content) > 200
                    })
                
                # Get conversation metadata
                total_messages = ChatMessage.objects.filter(conversation=conversation).count()
                last_activity = conversation.updated_at or conversation.created_at
                
                conversations_data.append({
                    'id': conversation.id,
                    'title': conversation.title,
                    'customer_id': conversation.customer_id,
                    'created_at': conversation.created_at.isoformat(),
                    'updated_at': conversation.updated_at.isoformat() if conversation.updated_at else None,
                    'last_activity': last_activity.isoformat(),
                    'total_messages': total_messages,
                    'preview_messages': messages_preview,
                    'has_more_messages': total_messages > 2
                })
            
            return Response({
                'success': True,
                'conversations': conversations_data,
                'total_count': len(conversations_data)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting recent conversations: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to retrieve recent conversations',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatHistoryView(APIView):
    """
    API endpoint to get chat messages for a specific conversation with pagination
    - Returns latest 100 messages by default
    - Supports pagination with page and page_size parameters
    - Only returns messages for conversations owned by the authenticated user
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, conversation_id):
        """
        Get chat messages for a specific conversation with pagination
        
        GET /ad-expert/api/conversations/{conversation_id}/messages/
        
        Query Parameters:
        - page: Page number (default: 1)
        - page_size: Number of messages per page (default: 50, max: 100)
        - order: Order of messages ('asc' for oldest first, 'desc' for newest first, default: 'desc')
        
        Response:
        {
            "success": true,
            "conversation_id": 123,
            "messages": [...],
            "pagination": {
                "current_page": 1,
                "page_size": 50,
                "total_messages": 150,
                "total_pages": 3,
                "has_next": true,
                "has_previous": false
            }
        }
        """
        try:
            user = request.user
            
            # Get pagination parameters
            page = int(request.GET.get('page', 1))
            page_size = min(int(request.GET.get('page_size', 50)), 100)  # Max 100 messages per page
            order = request.GET.get('order', 'desc')  # 'asc' or 'desc'
            
            # Validate page number
            if page < 1:
                page = 1
            
            # Get the conversation and verify ownership
            try:
                conversation = Conversation.objects.get(
                    id=conversation_id,
                    user=user
                )
            except Conversation.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Conversation not found or access denied',
                    'conversation_id': conversation_id
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Get total count of messages for this conversation
            total_messages = ChatMessage.objects.filter(conversation=conversation).count()
            
            # Calculate pagination
            total_pages = (total_messages + page_size - 1) // page_size
            offset = (page - 1) * page_size
            
            # Determine ordering
            order_field = 'created_at' if order == 'asc' else '-created_at'
            
            # Get messages with pagination
            messages = ChatMessage.objects.filter(
                conversation=conversation
            ).order_by(order_field)[offset:offset + page_size]
            
            # Format messages for response
            messages_data = []
            for message in messages:
                message_data = {
                    'id': message.id,
                    'role': message.role,
                    'content': message.content,
                    'response_type': message.response_type,
                    'created_at': message.created_at.isoformat(),
                    'updated_at': message.updated_at.isoformat() if message.updated_at else None
                }
                
                # Include structured data if available
                if message.structured_data:
                    message_data['structured_data'] = message.structured_data
                
                messages_data.append(message_data)
            
            # If order is 'desc', reverse the list to show newest first
            if order == 'desc':
                messages_data.reverse()
            
            # Calculate pagination info
            has_next = page < total_pages
            has_previous = page > 1
            
            response_data = {
                'success': True,
                'conversation_id': conversation_id,
                'conversation_title': conversation.title,
                'messages': messages_data,
                'pagination': {
                    'current_page': page,
                    'page_size': page_size,
                    'total_messages': total_messages,
                    'total_pages': total_pages,
                    'has_next': has_next,
                    'has_previous': has_previous,
                    'next_page': page + 1 if has_next else None,
                    'previous_page': page - 1 if has_previous else None
                }
            }
            
            logger.info(f"Retrieved {len(messages_data)} messages for conversation {conversation_id} (page {page}/{total_pages}) for user {user.id}")
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except ValueError as e:
            logger.error(f"Invalid pagination parameters: {str(e)}")
            return Response({
                'success': False,
                'error': 'Invalid pagination parameters',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to retrieve chat history',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
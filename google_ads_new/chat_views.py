from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import serializers
import json
from .chat_service import ChatService
from .models import ChatSession, ChatMessage, KBDocument
from django.contrib.auth.models import User
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

# Serializers for API responses
class ChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'created_at', 'updated_at']

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'metadata', 'created_at']

class KBDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = KBDocument
        fields = ['id', 'title', 'content', 'url', 'document_type', 'created_at', 'updated_at']

# Chat API Views
class ChatMessageView(APIView):
    """Process chat message and return AI response"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            data = request.data
            user_message = data.get('message', '').strip()
            session_id = data.get('session_id')
            
            if not user_message:
                return Response({
                    'success': False,
                    'error': 'Message is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Initialize chat service
            chat_service = ChatService(request.user)
            
            # Load or create session
            if session_id:
                if not chat_service.load_session(session_id):
                    return Response({
                        'success': False,
                        'error': 'Invalid session ID'
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                session_id = chat_service.start_session()
            
            # Process message
            result = chat_service.process_message(user_message)
            result['session_id'] = session_id
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in chat message view: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChatSessionsView(APIView):
    """Get user's chat sessions"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            sessions = ChatSession.objects.filter(user=request.user).order_by('-updated_at')
            
            session_list = []
            for session in sessions:
                session_list.append({
                    'id': str(session.id),
                    'title': session.title,
                    'created_at': session.created_at.isoformat(),
                    'updated_at': session.updated_at.isoformat(),
                    'message_count': ChatMessage.objects.filter(session=session).count()
                })
            
            return Response({
                'success': True,
                'sessions': session_list
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting chat sessions: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChatHistoryView(APIView):
    """Get chat history for a specific session"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, session_id):
        try:
            # Verify session belongs to user
            session = ChatSession.objects.get(id=session_id, user=request.user)
            
            messages = ChatMessage.objects.filter(session=session).order_by('created_at')
            
            message_list = []
            for message in messages:
                message_list.append({
                    'id': message.id,
                    'role': message.role,
                    'content': message.content,
                    'metadata': message.metadata,
                    'created_at': message.created_at.isoformat()
                })
            
            return Response({
                'success': True,
                'session': {
                    'id': str(session.id),
                    'title': session.title,
                    'created_at': session.created_at.isoformat()
                },
                'messages': message_list
            }, status=status.HTTP_200_OK)
            
        except ChatSession.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Session not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error getting chat history: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CreateSessionView(APIView):
    """Create a new chat session"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            data = request.data
            title = data.get('title', '').strip()
            
            chat_service = ChatService(request.user)
            session_id = chat_service.start_session(title)
            
            return Response({
                'success': True,
                'session_id': session_id,
                'message': 'Session created successfully'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating chat session: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteSessionView(APIView):
    """Delete a chat session"""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, session_id):
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
            session.delete()
            
            return Response({
                'success': True,
                'message': 'Session deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except ChatSession.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Session not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting chat session: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Knowledge Base API Views
class AddKBDocumentView(APIView):
    """Add document to knowledge base"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            data = request.data
            title = data.get('title', '').strip()
            content = data.get('content', '').strip()
            url = data.get('url', '').strip()
            company_id = data.get('company_id', 1)
            document_type = data.get('document_type', 'general')
            
            if not title or not content:
                return Response({
                    'success': False,
                    'error': 'Title and content are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            from .langchain_tools import KnowledgeBaseTools
            kb_tools = KnowledgeBaseTools(request.user)
            result = kb_tools.add_kb_document(company_id, title, content, url, document_type)
            
            return Response(result, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error adding KB document: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SearchKBView(APIView):
    """Search knowledge base"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            query = request.GET.get('q', '').strip()
            company_id = int(request.GET.get('company_id', 1))
            top_k = int(request.GET.get('top_k', 5))
            
            if not query:
                return Response({
                    'success': False,
                    'error': 'Query parameter is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            from .langchain_tools import KnowledgeBaseTools
            kb_tools = KnowledgeBaseTools(request.user)
            results = kb_tools.search_kb(query, company_id, top_k)
            
            return Response({
                'success': True,
                'query': query,
                'results': results
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error searching KB: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetKBDocumentsView(APIView):
    """Get documents from knowledge base"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            company_id = int(request.GET.get('company_id', 1))
            document_type = request.GET.get('document_type')
            
            documents_query = KBDocument.objects.filter(company_id=company_id)
            
            if document_type:
                documents_query = documents_query.filter(document_type=document_type)
            
            documents = documents_query.order_by('-updated_at')
            serializer = KBDocumentSerializer(documents, many=True)
            
            return Response({
                'success': True,
                'documents': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting KB documents: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Analytics and Insights Views
class QuickInsightsView(APIView):
    """Get quick insights for the user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            chat_service = ChatService(request.user)
            insights = chat_service.get_quick_insights()
            
            return Response({
                'success': True,
                'insights': insights
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting quick insights: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserContextView(APIView):
    """Get user's data context"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            chat_service = ChatService(request.user)
            context = chat_service.get_user_data_context()
            
            return Response({
                'success': True,
                'context': context
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting user context: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Tool Execution Views
class ToolExecutionView(APIView):
    """Execute a specific tool directly"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            data = request.data
            tool_name = data.get('tool_name')
            parameters = data.get('parameters', {})
            session_id = data.get('session_id')
            
            if not tool_name:
                return Response({
                    'success': False,
                    'error': 'Tool name is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get the appropriate tool class
            from .langchain_tools import GoogleAdsTools, DatabaseTools, KnowledgeBaseTools, AnalyticsTools
            
            if tool_name.startswith('google_ads_'):
                tool_instance = GoogleAdsTools(request.user, session_id)
                method_name = tool_name.replace('google_ads_', '')
            elif tool_name.startswith('db_'):
                tool_instance = DatabaseTools(request.user, session_id)
                method_name = tool_name.replace('db_', '')
            elif tool_name.startswith('kb_'):
                tool_instance = KnowledgeBaseTools(request.user, session_id)
                method_name = tool_name.replace('kb_', '')
            elif tool_name.startswith('analytics_'):
                tool_instance = AnalyticsTools(request.user, session_id)
                method_name = tool_name.replace('analytics_', '')
            else:
                return Response({
                    'success': False,
                    'error': f'Unknown tool: {tool_name}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Execute the tool method
            if hasattr(tool_instance, method_name):
                method = getattr(tool_instance, method_name)
                result = method(**parameters)
                
                return Response({
                    'success': True,
                    'result': result
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'error': f'Method {method_name} not found in {tool_name}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error executing tool: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Health Check View
class HealthCheckView(APIView):
    """Health check for the chat service"""
    
    def get(self, request):
        try:
            # Check if LLM is available
            from .llm_setup import llm_setup
            llm_status = "available" if llm_setup else "unavailable"
            
            # Check database connection
            try:
                ChatSession.objects.count()
                db_status = "connected"
            except Exception:
                db_status = "disconnected"
            
            return Response({
                'success': True,
                'service': 'Google Ads Chat Service',
                'status': 'healthy',
                'llm': llm_status,
                'database': db_status,
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return Response({
                'success': False,
                'service': 'Google Ads Chat Service',
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

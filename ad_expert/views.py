"""
ChatBotView for Ad Expert - Privacy-first chat system with in-memory analytics
"""
import json
import logging
from datetime import datetime
from typing import Dict, Any

from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Conversation, ChatMessage
from .llm_orchestrator import LLMOrchestrator

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
            
            # Get conversation context (last 10 messages)
            context_messages = list(
                conversation.messages.order_by('-created_at')[:10].values(
                    'role', 'content', 'created_at'
                )
            )
            context_messages.reverse()
            
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

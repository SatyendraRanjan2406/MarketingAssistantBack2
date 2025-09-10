from django.urls import path
from . import views

app_name = 'ad_expert'

urlpatterns = [
    # Chat endpoints
    path('api/chat/message/', views.ChatBotView.as_view(), name='chat_message'),
    path('api/conversations/', views.get_conversations, name='conversations'),
    path('api/conversations/<int:conversation_id>/', views.get_conversation_messages, name='conversation_messages'),
    path('api/conversations/<int:conversation_id>/delete/', views.delete_conversation, name='delete_conversation'),
    
    # OAuth endpoints
    path('api/oauth/connections/', views.get_oauth_connections, name='oauth_connections'),
    path('api/oauth/connections/<int:connection_id>/revoke/', views.revoke_oauth_connection, name='revoke_oauth'),
    
    # Health check and test endpoints
    path('api/health/', views.health_check, name='health_check'),
    path('api/test-auth/', views.test_auth, name='test_auth'),
]

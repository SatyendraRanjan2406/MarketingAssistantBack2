from django.urls import path
from . import views

app_name = 'ad_expert'

urlpatterns = [
    # Chat endpoints - COMMENTED OUT (not used)
    # path('api/chat/message/', views.ChatBotView.as_view(), name='chat_message'),
    path('api/conversations/', views.get_conversations, name='conversations'),
    path('api/conversations/<int:conversation_id>/', views.get_conversation_messages, name='conversation_messages'),
    path('api/conversations/<int:conversation_id>/delete/', views.delete_conversation, name='delete_conversation'),
    
    # RAG Chat endpoint with Intent Mapping
    path('api/rag/chat/', views.LanggraphView.as_view(), name='rag_chat'),
    
    # LangChain Chat endpoint - COMMENTED OUT (not used)
    # path('api/langchain/chat/', views.LangChainView.as_view(), name='langchain_chat'),
    
    # LangGraph Chat endpoint with advanced state management
    path('api/langgraph/chat/', views.LanggraphView.as_view(), name='langgraph_chat'),
    
    # Conversation History endpoints
    path('api/conversations/history/', views.ConversationHistoryView.as_view(), name='conversation_history'),
    path('api/conversations/history/<int:conversation_id>/', views.ConversationHistoryView.as_view(), name='conversation_detail'),
    
    # Recent Conversations endpoint for frontend
    path('api/conversations/recent/', views.RecentConversationsView.as_view(), name='recent_conversations'),
    
    # Chat History endpoint with pagination
    path('api/conversations/<int:conversation_id>/messages/', views.ChatHistoryView.as_view(), name='chat_history'),
    
    # MCP Chat endpoint - COMMENTED OUT (view not used)
    # path('api/chat2/', views.RAGChat2View.as_view(), name='mcp_chat'),
    
    # OAuth endpoints
    path('api/oauth/connections/', views.get_oauth_connections, name='oauth_connections'),
    path('api/oauth/connections/<int:connection_id>/revoke/', views.revoke_oauth_connection, name='revoke_oauth'),
    
    # Health check and test endpoints
    path('api/health/', views.health_check, name='health_check'),
    path('api/test-auth/', views.test_auth, name='test_auth'),
]

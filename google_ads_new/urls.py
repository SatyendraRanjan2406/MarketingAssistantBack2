from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import chat_views
from . import live_monitoring_views
from . import rag_views
from . import embedding_views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'accounts', views.GoogleAdsAccountViewSet, basename='google-ads-account')
router.register(r'campaigns', views.GoogleAdsCampaignViewSet, basename='google-ads-campaign')
router.register(r'ad-groups', views.GoogleAdsAdGroupViewSet, basename='google-ads-ad-group')
router.register(r'keywords', views.GoogleAdsKeywordViewSet, basename='google-ads-keyword')
router.register(r'performance', views.GoogleAdsPerformanceViewSet, basename='google-ads-performance')
router.register(r'sync-logs', views.DataSyncLogViewSet, basename='data-sync-log')

# URL patterns
urlpatterns = [
    # Include router URLs
    path('api/', include(router.urls)),
    
    # Sync operations
    path('api/sync-status/', views.sync_status_view, name='google-ads-sync-status'),
    path('api/sync-data/', views.sync_data_view, name='google-ads-sync-data'),
    path('api/synced-data/', views.get_synced_data_view, name='google-ads-synced-data'),
    path('api/dashboard-summary/', views.dashboard_summary_view, name='google-ads-dashboard-summary'),
    path('api/account-summary/', views.account_summary_view, name='google-ads-account-summary'),
    path('api/test-connection/', views.test_connection_view, name='google-ads-test-connection'),
    path('api/sync-logs/', views.get_sync_logs_view, name='google-ads-sync-logs'),
    
    # Account access management endpoints
    path('api/request-account-access/', views.request_account_access_view, name='google-ads-request-account-access'),
    path('api/pending-access-requests/', views.get_pending_access_requests_view, name='google-ads-pending-access-requests'),
    path('api/list-accessible-customers/', views.list_accessible_customers_view, name='google-ads-list-accessible-customers'),
    path('api/saved-accessible-customers/', views.get_saved_accessible_customers_view, name='google-ads-saved-accessible-customers'),
    
    # Legacy endpoints for backward compatibility
    path('api/legacy/sync-status/', views.sync_status_legacy_view, name='google-ads-legacy-sync-status'),
    path('api/legacy/sync-data/', views.sync_data_legacy_view, name='google-ads-legacy-sync-data'),
    path('api/legacy/synced-data/', views.get_synced_data_legacy_view, name='google-ads-legacy-synced-data'),
]


# Live Monitoring API endpoints
urlpatterns += [
    # Main live monitoring endpoint
    path('api/live-monitoring/', live_monitoring_views.LiveMonitoringView.as_view(), name='live_monitoring'),
    
    # Account-specific live monitoring
    path('api/live-monitoring/account/<int:account_id>/', live_monitoring_views.AccountLiveMonitoringView.as_view(), name='account_live_monitoring'),
    
    # Specific insights and metrics
    path('api/live-monitoring/account/<int:account_id>/insights/', live_monitoring_views.LiveMonitoringInsightsView.as_view(), name='live_monitoring_insights'),
    path('api/live-monitoring/account/<int:account_id>/quick-stats/', live_monitoring_views.LiveMonitoringQuickStatsView.as_view(), name='live_monitoring_quick_stats'),
    path('api/live-monitoring/account/<int:account_id>/performance/', live_monitoring_views.LiveMonitoringPerformanceView.as_view(), name='live_monitoring_performance'),
]

# Chat and AI Assistant endpoints
urlpatterns += [
    # Chat functionality
    path('api/chat/message/', chat_views.ChatMessageView.as_view(), name='chat_message'),
    path('api/chat/sessions/', chat_views.ChatSessionsView.as_view(), name='chat_sessions'),
    path('api/chat/sessions/create/', chat_views.CreateSessionView.as_view(), name='create_session'),
    path('api/chat/sessions/<str:session_id>/', chat_views.ChatHistoryView.as_view(), name='chat_history'),
    path('api/chat/sessions/<str:session_id>/delete/', chat_views.DeleteSessionView.as_view(), name='delete_session'),
    
    # Knowledge base
    path('api/kb/add/', chat_views.AddKBDocumentView.as_view(), name='add_kb_document'),
    path('api/kb/search/', chat_views.SearchKBView.as_view(), name='search_kb'),
    path('api/kb/documents/', chat_views.GetKBDocumentsView.as_view(), name='get_kb_documents'),
    
    # Analytics and insights
    path('api/insights/quick/', chat_views.QuickInsightsView.as_view(), name='quick_insights'),
    path('api/insights/context/', chat_views.UserContextView.as_view(), name='user_context'),
    
    # Tool execution
    path('api/tools/execute/', chat_views.ToolExecutionView.as_view(), name='execute_tool'),
    
    # Health check
    path('api/health/', chat_views.HealthCheckView.as_view(), name='health_check'),
]

# RAG (Retrieval-Augmented Generation) endpoints
urlpatterns += [
    # Basic RAG endpoints (no authentication required for testing)
    path('api/rag/query/', rag_views.query_rag, name='rag_query'),
    path('api/rag/search/', rag_views.search_documents, name='rag_search'),
    path('api/rag/status/', rag_views.rag_status, name='rag_status'),
    path('api/rag/rebuild/', rag_views.rebuild_vector_store, name='rag_rebuild'),
    
    # REST API RAG endpoints (authentication required)
    path('api/rag/api/query/', rag_views.api_query_rag, name='api_rag_query'),
    path('api/rag/api/search/', rag_views.api_search_documents, name='api_rag_search'),
    path('api/rag/api/status/', rag_views.api_rag_status, name='api_rag_status'),
    
    # Embedding dashboard
    path('embedding-dashboard/', embedding_views.embedding_dashboard, name='embedding_dashboard'),
    path('api/rag/embedding-search/', embedding_views.search_embeddings, name='embedding_search'),
    path('api/rag/embedding-stats/', embedding_views.embedding_stats, name='embedding_stats'),
]

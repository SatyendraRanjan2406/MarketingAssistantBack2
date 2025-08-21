from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, sync_views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'accounts', views.GoogleAdsAccountViewSet, basename='google-ads-account')
router.register(r'campaigns', views.GoogleAdsCampaignViewSet, basename='google-ads-campaign')
router.register(r'ad-groups', views.GoogleAdsAdGroupViewSet, basename='google-ads-ad-group')
router.register(r'keywords', views.GoogleAdsKeywordViewSet, basename='google-ads-keyword')
router.register(r'performance', views.GoogleAdsPerformanceViewSet, basename='google-ads-performance')
router.register(r'reports', views.GoogleAdsReportViewSet, basename='google-ads-report')
router.register(r'alerts', views.GoogleAdsAlertViewSet, basename='google-ads-alert')
router.register(r'sync', sync_views.DataSyncViewSet, basename='data-sync')

# URL patterns
urlpatterns = [
    # Dashboard view
    path('dashboard/', views.dashboard_view, name='google-ads-dashboard-view'),
    
    # Chat functionality
    path('chat/', views.chat_dashboard, name='google-ads-chat'),
    path('chat/api/', views.chat_api, name='google-ads-chat-api'),
    path('chat/insights/', views.get_quick_insights, name='google-ads-quick-insights'),
    
    # Test endpoints
    path('test-csrf/', views.test_csrf, name='test-csrf'),
    
    # Include router URLs
    path('api/', include(router.urls)),
    
    # Dashboard API
    path('api/dashboard/', views.DashboardView.as_view(), name='google-ads-dashboard'),
    
    # Account management
    path('api/sync-account/', views.AccountSyncView.as_view(), name='google-ads-sync-account'),
    
    # Data synchronization
    path('api/sync-account/<int:account_id>/', sync_views.SyncAccountView.as_view(), name='google-ads-sync-specific-account'),
    path('api/sync-log/<int:log_id>/', sync_views.SyncLogView.as_view(), name='google-ads-sync-log'),
    path('api/force-sync/', sync_views.force_sync_api, name='google-ads-force-sync'),
    
    # Dashboard sync features
    path('api/sync-status/', views.sync_status_view, name='google-ads-sync-status'),
    path('api/sync-data/', views.sync_data_view, name='google-ads-sync-data'),
    path('api/synced-data/', views.get_synced_data_view, name='google-ads-synced-data'),
    
    # Campaign management
    path('api/create-campaign/', views.CampaignCreateView.as_view(), name='google-ads-create-campaign'),
    
    # Keyword management
    path('api/create-keyword/', views.KeywordCreateView.as_view(), name='google-ads-create-keyword'),
    
    # Performance export
    path('api/export-performance/', views.PerformanceExportView.as_view(), name='google-ads-export-performance'),
]

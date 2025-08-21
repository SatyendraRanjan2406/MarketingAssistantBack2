from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

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
    
    # Legacy endpoints for backward compatibility
    path('api/legacy/sync-status/', views.sync_status_legacy_view, name='google-ads-legacy-sync-status'),
    path('api/legacy/sync-data/', views.sync_data_legacy_view, name='google-ads-legacy-sync-data'),
    path('api/legacy/synced-data/', views.get_synced_data_legacy_view, name='google-ads-legacy-synced-data'),
]

# API endpoints
urlpatterns += [
    path('api/sync-status/', views.sync_status_view, name='sync_status'),
    path('api/sync-data/', views.sync_data_view, name='sync_data'),
    path('api/get-synced-data/', views.get_synced_data_view, name='get_synced_data'),
    path('api/dashboard-summary/', views.dashboard_summary_view, name='dashboard_summary'),
    path('api/account-summary/', views.account_summary_view, name='account_summary'),
    path('api/test-connection/', views.test_connection_view, name='test_connection'),
    path('api/sync-logs/', views.get_sync_logs_view, name='get_sync_logs'),
    path('api/request-account-access/', views.request_account_access_view, name='request_account_access'),
    path('api/pending-access-requests/', views.get_pending_access_requests_view, name='get_pending_access_requests'),
    path('api/comprehensive-sync/', views.comprehensive_sync_view, name='comprehensive_sync'),
    path('api/sync-single-client/', views.sync_single_client_account, name='sync_single_client_account'),
    path('api/test-single-client-sync/', views.test_single_client_sync, name='test_single_client_sync'),
]

]

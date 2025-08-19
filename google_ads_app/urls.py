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
router.register(r'reports', views.GoogleAdsReportViewSet, basename='google-ads-report')
router.register(r'alerts', views.GoogleAdsAlertViewSet, basename='google-ads-alert')

# URL patterns
urlpatterns = [
    # Dashboard view
    path('dashboard/', views.dashboard_view, name='google-ads-dashboard-view'),
    
    # Include router URLs
    path('api/', include(router.urls)),
    
    # Dashboard API
    path('api/dashboard/', views.DashboardView.as_view(), name='google-ads-dashboard'),
    
    # Account management
    path('api/sync-account/', views.AccountSyncView.as_view(), name='google-ads-sync-account'),
    
    # Campaign management
    path('api/create-campaign/', views.CampaignCreateView.as_view(), name='google-ads-create-campaign'),
    
    # Keyword management
    path('api/create-keyword/', views.KeywordCreateView.as_view(), name='google-ads-create-keyword'),
    
    # Performance export
    path('api/export-performance/', views.PerformanceExportView.as_view(), name='google-ads-export-performance'),
]

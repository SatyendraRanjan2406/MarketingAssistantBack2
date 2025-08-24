from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # JWT Authentication endpoints
    path('api/signup/', views.api_signup, name='api_signup'),
    path('api/signin/', views.api_signin, name='api_signin'),
    path('api/refresh-token/', views.api_refresh_token, name='api_refresh_token'),
    path('api/logout/', views.api_logout, name='api_logout'),
    
    # User management endpoints
    path('api/profile/update/', views.api_profile_update, name='api_profile_update'),
    path('api/google-account/status/', views.api_google_account_status, name='api_google_account_status'),
    path('api/dashboard/', views.dashboard_view, name='dashboard'),
    
    # Google OAuth endpoints
    path('api/google-oauth/initiate/', views.google_oauth_initiate, name='google_oauth_initiate'),
    path('api/google-oauth/callback/', views.google_oauth_callback, name='google_oauth_callback'),
    path('api/google-oauth/exchange-tokens/', views.google_oauth_exchange_tokens, name='google_oauth_exchange_tokens'),
    path('api/google-oauth/status/', views.google_oauth_status, name='google_oauth_status'),
    path('api/google-oauth/disconnect/', views.google_oauth_disconnect, name='google_oauth_disconnect'),
    path('api/google-oauth/ads-accounts/', views.google_ads_accounts, name='google_ads_accounts'),
]

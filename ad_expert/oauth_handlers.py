"""
OAuth handlers for Google Ads and Meta Marketing API
Privacy-first: minimal token storage, just-in-time access
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.urls import reverse

from .models import OAuthConnection

logger = logging.getLogger(__name__)


class GoogleOAuthHandler:
    """Google OAuth handler for Google Ads API"""
    
    def __init__(self):
        self.client_id = settings.GOOGLE_OAUTH_CONFIG.get('client_id')
        self.client_secret = settings.GOOGLE_OAUTH_CONFIG.get('client_secret')
        self.redirect_uri = settings.GOOGLE_OAUTH_CONFIG.get('redirect_uri')
        self.scope = 'https://www.googleapis.com/auth/adwords'
    
    def get_auth_url(self, state: str = None) -> str:
        """Generate Google OAuth authorization URL"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': self.scope,
            'response_type': 'code',
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        if state:
            params['state'] = state
        
        base_url = 'https://accounts.google.com/o/oauth2/v2/auth'
        query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
        return f'{base_url}?{query_string}'
    
    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        try:
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri
            }
            
            response = requests.post(
                'https://oauth2.googleapis.com/token',
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Google OAuth token exchange error: {str(e)}")
            raise
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Google"""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers=headers
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Google user info error: {str(e)}")
            raise
    
    def get_customer_ids(self, access_token: str) -> list:
        """Get Google Ads customer IDs accessible to the user"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'developer-token': settings.GOOGLE_ADS_CONFIG.get('developer_token')
            }
            
            # Get accessible customers
            response = requests.get(
                'https://googleads.googleapis.com/v19/customers:listAccessibleCustomers',
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get('resourceNames', [])
            
        except Exception as e:
            logger.error(f"Google Ads customer list error: {str(e)}")
            return []
    
    def save_connection(self, user: User, token_data: Dict[str, Any], 
                       customer_id: str = None) -> OAuthConnection:
        """Save OAuth connection to database"""
        expires_at = datetime.now() + timedelta(seconds=token_data.get('expires_in', 3600))
        
        # Encrypt access token in production
        access_token = token_data.get('access_token')
        
        connection = OAuthConnection.objects.create(
            user=user,
            platform='google',
            access_token=access_token,
            token_expires_at=expires_at,
            scope=self.scope,
            account_id=customer_id or 'default'
        )
        
        return connection


class MetaOAuthHandler:
    """Meta OAuth handler for Marketing API"""
    
    def __init__(self):
        self.app_id = settings.META_OAUTH_CONFIG.get('app_id')
        self.app_secret = settings.META_OAUTH_CONFIG.get('app_secret')
        self.redirect_uri = settings.META_OAUTH_CONFIG.get('redirect_uri')
        self.scope = 'ads_read,ads_management'
    
    def get_auth_url(self, state: str = None) -> str:
        """Generate Meta OAuth authorization URL"""
        params = {
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'scope': self.scope,
            'response_type': 'code',
            'state': state or 'default'
        }
        
        base_url = 'https://www.facebook.com/v20.0/dialog/oauth'
        query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
        return f'{base_url}?{query_string}'
    
    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        try:
            data = {
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'code': code,
                'redirect_uri': self.redirect_uri
            }
            
            response = requests.post(
                'https://graph.facebook.com/v20.0/oauth/access_token',
                data=data
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Meta OAuth token exchange error: {str(e)}")
            raise
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Meta"""
        try:
            response = requests.get(
                f'https://graph.facebook.com/v20.0/me?access_token={access_token}'
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Meta user info error: {str(e)}")
            raise
    
    def get_ad_accounts(self, access_token: str) -> list:
        """Get Meta ad accounts accessible to the user"""
        try:
            response = requests.get(
                f'https://graph.facebook.com/v20.0/me/adaccounts?access_token={access_token}'
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get('data', [])
            
        except Exception as e:
            logger.error(f"Meta ad accounts error: {str(e)}")
            return []
    
    def save_connection(self, user: User, token_data: Dict[str, Any], 
                       ad_account_id: str = None) -> OAuthConnection:
        """Save OAuth connection to database"""
        # Meta tokens don't have explicit expiry, assume 60 days
        expires_at = datetime.now() + timedelta(days=60)
        
        access_token = token_data.get('access_token')
        
        connection = OAuthConnection.objects.create(
            user=user,
            platform='meta',
            access_token=access_token,
            token_expires_at=expires_at,
            scope=self.scope,
            account_id=ad_account_id or 'default'
        )
        
        return connection


class OAuthManager:
    """Unified OAuth manager for both platforms"""
    
    def __init__(self):
        self.google_handler = GoogleOAuthHandler()
        self.meta_handler = MetaOAuthHandler()
    
    def get_auth_url(self, platform: str, state: str = None) -> str:
        """Get authorization URL for platform"""
        if platform == 'google':
            return self.google_handler.get_auth_url(state)
        elif platform == 'meta':
            return self.meta_handler.get_auth_url(state)
        else:
            raise ValueError(f"Unsupported platform: {platform}")
    
    def handle_callback(self, platform: str, code: str, user: User, 
                       account_id: str = None) -> OAuthConnection:
        """Handle OAuth callback and save connection"""
        if platform == 'google':
            token_data = self.google_handler.exchange_code_for_token(code)
            return self.google_handler.save_connection(user, token_data, account_id)
        elif platform == 'meta':
            token_data = self.meta_handler.exchange_code_for_token(code)
            return self.meta_handler.save_connection(user, token_data, account_id)
        else:
            raise ValueError(f"Unsupported platform: {platform}")
    
    def refresh_token(self, connection: OAuthConnection) -> bool:
        """Refresh OAuth token if needed"""
        if connection.platform == 'google':
            # Google tokens are typically long-lived, but we can implement refresh logic
            return True
        elif connection.platform == 'meta':
            # Meta tokens are long-lived by default
            return True
        else:
            return False
    
    def revoke_token(self, connection: OAuthConnection) -> bool:
        """Revoke OAuth token with provider"""
        try:
            if connection.platform == 'google':
                # Revoke Google token
                requests.post(
                    'https://oauth2.googleapis.com/revoke',
                    data={'token': connection.access_token}
                )
            elif connection.platform == 'meta':
                # Revoke Meta token
                requests.delete(
                    f'https://graph.facebook.com/v20.0/me/permissions?access_token={connection.access_token}'
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Token revocation error: {str(e)}")
            return False


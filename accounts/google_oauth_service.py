"""
Google OAuth Service for handling Google authentication and Google Ads integration
"""
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urlencode

from django.utils import timezone
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .models import UserGoogleAuth

logger = logging.getLogger(__name__)


class GoogleOAuthService:
    """Service class for handling Google OAuth authentication"""
    
    def __init__(self):
        # Read configuration from environment variables
        self.client_id = os.getenv('GOOGLE_OAUTH_CLIENT_ID', '')
        self.client_secret = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET', '')
        
        # Debug: Show what we're reading from environment
        raw_redirect_uri = os.getenv('GOOGLE_OAUTH_REDIRECT_URI', 'NOT_SET')
        logger.info(f"DEBUG: Raw GOOGLE_OAUTH_REDIRECT_URI from env: {raw_redirect_uri}")
        
        self.redirect_uri = os.getenv('GOOGLE_OAUTH_REDIRECT_URI', 'http://localhost:8000/accounts/api/google-oauth/callback/')
        
        # Import Django settings to get scopes
        from django.conf import settings
        self.scopes = getattr(settings, 'GOOGLE_OAUTH_CONFIG', {}).get('scopes', [
            'https://www.googleapis.com/auth/userinfo.profile',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/adwords',
            'https://www.googleapis.com/auth/analytics.readonly',
        ])
        
        # Log configuration for debugging
        logger.info(f"Google OAuth Service initialized with:")
        logger.info(f"  Client ID: {self.client_id[:10]}..." if self.client_id else "  Client ID: NOT SET")
        logger.info(f"  Client Secret: {'SET' if self.client_secret else 'NOT SET'}")
        logger.info(f"  Raw env redirect_uri: {raw_redirect_uri}")
        logger.info(f"  Final redirect_uri: {self.redirect_uri}")
        logger.info(f"  Scopes: {len(self.scopes)} scopes configured")
        logger.info(f"  Scopes: {self.scopes}")
    
    def get_authorization_url(self, state: str = None) -> tuple[str, str]:
        """
        Generate Google OAuth authorization URL
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            Tuple of (authorization_url, state) where state is the actual state used by Google OAuth
        """
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri],
                    }
                },
                scopes=self.scopes
            )
            
            flow.redirect_uri = self.redirect_uri
            
            authorization_url, state_used = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent',
                state=state
            )
            
            return authorization_url, state_used
            
        except Exception as e:
            logger.error(f"Error generating authorization URL: {str(e)}")
            raise
    
    def exchange_code_for_tokens(self, authorization_code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens
        
        Args:
            authorization_code: Authorization code from Google OAuth callback
            
        Returns:
            Dictionary containing tokens and user info
        """
        try:
            import requests
            
            # Exchange authorization code for tokens directly with Google
            token_url = "https://oauth2.googleapis.com/token"
            token_data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': authorization_code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri,
            }
            
            response = requests.post(token_url, data=token_data)
            response.raise_for_status()
            
            token_response = response.json()
            
            # Log the response for debugging
            logger.info(f"Token exchange response: {token_response}")
            
            # Extract tokens
            access_token = token_response.get('access_token')
            refresh_token = token_response.get('refresh_token')
            expires_in = token_response.get('expires_in')
            scope = token_response.get('scope', '')
            
            if not access_token:
                raise Exception("No access token received from Google")
            
            # Calculate expiry time
            from django.utils import timezone
            token_expiry = timezone.now() + timezone.timedelta(seconds=expires_in)
            
            # Create credentials object for user info retrieval
            credentials = Credentials(
                token=access_token,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=scope.split() if scope else []
            )
            
            # Log the actual scopes returned by Google
            logger.info(f"Requested scopes: {self.scopes}")
            logger.info(f"Actual scopes returned: {scope.split() if scope else []}")
            
            # Accept any scopes that Google returns, as long as they include our required ones
            required_scopes = set(self.scopes)
            actual_scopes = set(scope.split() if scope else [])
            
            # Check if all required scopes are present (ignore additional ones like 'openid')
            if not required_scopes.issubset(actual_scopes):
                missing_scopes = required_scopes - actual_scopes
                logger.warning(f"Missing required scopes: {missing_scopes}")
                raise Exception(f"Missing required scopes: {missing_scopes}")
            
            # Log any additional scopes that Google added
            additional_scopes = actual_scopes - required_scopes
            if additional_scopes:
                logger.info(f"Google added additional scopes: {additional_scopes}")
            
            # Get user information
            user_info = self._get_user_info(credentials)
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_expiry': token_expiry,
                'scopes': scope,  # Use actual scopes from Google
                'user_info': user_info
            }
            
        except Exception as e:
            logger.error(f"Error exchanging code for tokens: {str(e)}")
            
            # Check if this is a scope change error and provide a helpful message
            if "Scope has changed" in str(e):
                logger.warning("Google OAuth scope change detected - this is normal and expected")
                # Try to extract the actual error details
                raise Exception("Google OAuth scope changed. This is normal and expected. Please try the connection again.")
            else:
                raise
    
    def _get_user_info(self, credentials: Credentials) -> Dict[str, Any]:
        """
        Get user information from Google
        
        Args:
            credentials: Google OAuth credentials
            
        Returns:
            User information dictionary
        """
        try:
            service = build('oauth2', 'v2', credentials=credentials)
            user_info = service.userinfo().get().execute()
            
            return {
                'google_user_id': user_info.get('id'),
                'google_email': user_info.get('email'),
                'google_name': user_info.get('name', ''),
            }
            
        except HttpError as e:
            logger.error(f"Error getting user info: {str(e)}")
            raise
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Refresh token to use
            
        Returns:
            New access token information
        """
        try:
            credentials = Credentials(
                None,  # No access token initially
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=self.scopes
            )
            
            # Refresh the credentials
            credentials.refresh(Request())
            
            return {
                'access_token': credentials.token,
                'token_expiry': credentials.expiry,
            }
            
        except Exception as e:
            logger.error(f"Error refreshing access token: {str(e)}")
            raise
    
    def get_google_ads_accounts(self, access_token: str) -> list:
        """
        Get Google Ads accounts accessible to the user
        
        Args:
            access_token: Valid access token
            
        Returns:
            List of Google Ads accounts
        """
        try:
            credentials = Credentials(access_token)
            service = build('adwords', 'v201809', credentials=credentials)
            
            # Get customer list
            customer_service = service.CustomerService()
            customers = customer_service.getCustomers()
            
            accounts = []
            for customer in customers:
                accounts.append({
                    'customer_id': customer['customerId'],
                    'name': customer.get('name', ''),
                    'currency_code': customer.get('currencyCode', ''),
                    'time_zone': customer.get('timeZone', ''),
                    'can_manage_clients': customer.get('canManageClients', False),
                })
            
            return accounts
            
        except HttpError as e:
            logger.error(f"Error getting Google Ads accounts: {str(e)}")
            raise
    
    def validate_token(self, access_token: str) -> bool:
        """
        Validate if access token is still valid
        
        Args:
            access_token: Access token to validate
            
        Returns:
            True if token is valid, False otherwise
        """
        try:
            credentials = Credentials(access_token)
            service = build('oauth2', 'v2', credentials=credentials)
            
            # Try to get user info to validate token
            service.userinfo().get().execute()
            return True
            
        except HttpError:
            return False
        except Exception as e:
            logger.error(f"Error validating token: {str(e)}")
            return False


class UserGoogleAuthService:
    """Service class for managing UserGoogleAuth model"""
    
    @staticmethod
    def create_or_update_auth(user, access_token, refresh_token, token_expiry, scopes, user_info) -> UserGoogleAuth:
        """
        Create or update Google OAuth authentication record
        
        Args:
            user: Django User instance
            access_token: Google OAuth access token
            refresh_token: Google OAuth refresh token
            token_expiry: When access token expires
            scopes: Comma-separated OAuth scopes
            user_info: Google user information
            
        Returns:
            UserGoogleAuth instance
        """
        try:
            # Try to get existing auth record for this user and Google account
            auth_record, created = UserGoogleAuth.objects.get_or_create(
                user=user,
                google_user_id=user_info['google_user_id'],  # Include google_user_id in lookup
                defaults={
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'token_expiry': token_expiry,
                    'scopes': scopes,
                    'google_email': user_info['google_email'],
                    'google_name': user_info['google_name'],
                    'is_active': True,
                    'error_count': 0,
                    'last_error': None,
                }
            )
            
            if not created:
                # Update existing record
                auth_record.access_token = access_token
                auth_record.refresh_token = refresh_token
                auth_record.token_expiry = token_expiry
                auth_record.scopes = scopes
                auth_record.google_email = user_info['google_email']
                auth_record.google_name = user_info['google_name']
                auth_record.is_active = True
                auth_record.error_count = 0
                auth_record.last_error = None
                auth_record.save()
            
            return auth_record
            
        except Exception as e:
            logger.error(f"Error creating/updating UserGoogleAuth: {str(e)}")
            raise
    
    @staticmethod
    def get_valid_auth(user) -> Optional[UserGoogleAuth]:
        """
        Get valid Google auth record for user
        
        Args:
            user: Django User instance
            
        Returns:
            UserGoogleAuth instance if valid, None otherwise
        """
        try:
            auth_record = UserGoogleAuth.objects.filter(
                user=user,
                is_active=True
            ).first()
            
            if not auth_record:
                return None
            
            # Check if token is expired
            if auth_record.is_token_expired():
                return None
            
            return auth_record
            
        except Exception as e:
            logger.error(f"Error getting valid auth: {str(e)}")
            return None
    
    @staticmethod
    def refresh_user_tokens(user) -> Optional[UserGoogleAuth]:
        """
        Refresh access token for user
        
        Args:
            user: Django User instance
            
        Returns:
            Updated UserGoogleAuth instance if successful, None otherwise
        """
        try:
            auth_record = UserGoogleAuth.objects.filter(
                user=user,
                is_active=True
            ).first()
            
            if not auth_record:
                return None
            
            # Use Google OAuth service to refresh token
            oauth_service = GoogleOAuthService()
            new_tokens = oauth_service.refresh_access_token(auth_record.refresh_token)
            
            # Update the record
            auth_record.access_token = new_tokens['access_token']
            auth_record.token_expiry = new_tokens['token_expiry']
            auth_record.error_count = 0
            auth_record.last_error = None
            auth_record.save()
            
            return auth_record
            
        except Exception as e:
            logger.error(f"Error refreshing user tokens: {str(e)}")
            
            # Update error tracking
            if auth_record:
                auth_record.error_count += 1
                auth_record.last_error = str(e)
                auth_record.save()
            
            return None

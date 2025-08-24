from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm, UserProfileUpdateForm
# Remove direct model imports to avoid circular import issues
# from .models import UserProfile, UserGoogleAuth
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .google_oauth_service import GoogleOAuthService, UserGoogleAuthService
from django.utils import timezone


def get_google_account_info(user):
    """Helper function to get Google account details for a user"""
    try:
        # Get all Google auth connections for the user
        google_auths = getattr(user, 'google_auth_set', None)
        
        if google_auths and google_auths.exists():
            # Return list of all connected Google accounts
            accounts = []
            for google_auth in google_auths.filter(is_active=True):
                accounts.append({
                    'id': google_auth.id,
                    'google_email': google_auth.google_email,
                    'google_name': google_auth.google_name,
                    'google_ads_customer_id': google_auth.google_ads_customer_id,
                    'google_ads_account_name': google_auth.google_ads_account_name,
                    'is_connected': True,
                    'last_used': google_auth.last_used.isoformat() if google_auth.last_used else None,
                    'scopes': google_auth.scopes.split(',') if google_auth.scopes else [],
                    'token_expiry': google_auth.token_expiry.isoformat() if google_auth.token_expiry else None,
                    'is_token_expired': google_auth.is_token_expired(),
                    'needs_refresh': google_auth.needs_refresh()
                })
            
            return {
                'is_connected': True,
                'accounts': accounts,
                'total_accounts': len(accounts)
            }
        else:
            return {
                'is_connected': False,
                'accounts': [],
                'total_accounts': 0,
                'message': 'No Google accounts connected'
            }
    except Exception as e:
        return {
            'is_connected': False,
            'accounts': [],
            'total_accounts': 0,
            'message': f'Error retrieving Google account info: {str(e)}'
        }


# API Views for JWT-based authentication
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def api_signup(request):
    """API endpoint for user registration with JWT tokens"""
    try:
        # Create form data with password1 and password2
        data = request.data.copy()
        password = data.get('password')
        if password:
            data['password1'] = password
            data['password2'] = password
        
        form = UserRegistrationForm(data)
        
        if form.is_valid():
            user = form.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            # Get user profile info
            profile = getattr(user, 'profile', None)
            
            # Get Google account details (will be false for new users)
            google_account_info = get_google_account_info(user)
            
            response_data = {
                'success': True,
                'message': 'Account created successfully!',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'company_name': profile.company_name if profile else None,
                },
                'google_account': google_account_info
            }
            
            response = Response(response_data, status=status.HTTP_201_CREATED)
            response["Access-Control-Allow-Credentials"] = "true"
            return response
        else:
            errors = {}
            for field, field_errors in form.errors.items():
                errors[field] = [str(error) for error in field_errors]
            
            response_data = {
                'success': False,
                'errors': errors
            }
            
            response = Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            response["Access-Control-Allow-Credentials"] = "true"
            return response
            
    except Exception as e:
        response_data = {
            'success': False,
            'error': str(e)
        }
        
        response = Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        response["Access-Control-Allow-Credentials"] = "true"
        return response


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def api_signin(request):
    """API endpoint for user login with JWT tokens"""
    try:
        data = request.data
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            response_data = {
                'success': False,
                'error': 'Username and password are required.'
            }
            
            response = Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            response["Access-Control-Allow-Credentials"] = "true"
            return response
        
        user = authenticate(username=username, password=password)
        if user is not None:
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            # Get user profile info
            profile = getattr(user, 'profile', None)
            
            # Get Google account details if connected
            google_account_info = get_google_account_info(user)
            
            response_data = {
                'success': True,
                'message': 'Login successful!',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'company_name': profile.company_name if profile else None,
                },
                'google_account': google_account_info
            }
            
            response = Response(response_data, status=status.HTTP_200_OK)
            response["Access-Control-Allow-Credentials"] = "true"
            return response
        else:
            response_data = {
                'success': False,
                'error': 'Invalid username or password.'
            }
            
            response = Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            response["Access-Control-Allow-Credentials"] = "true"
            return response
            
    except Exception as e:
        response_data = {
            'success': False,
            'error': str(e)
        }
        
        response = Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        response["Access-Control-Allow-Credentials"] = "true"
        return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_google_account_status(request):
    """API endpoint to get Google account connection status for authenticated user"""
    try:
        google_account_info = get_google_account_info(request.user)
        
        response_data = {
            'success': True,
            'google_account': google_account_info
        }
        
        response = Response(response_data, status=status.HTTP_200_OK)
        response["Access-Control-Allow-Credentials"] = "true"
        return response
        
    except Exception as e:
        response_data = {
            'success': False,
            'error': str(e)
        }
        
        response = Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        response["Access-Control-Allow-Credentials"] = "true"
        return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_profile_update(request):
    """API endpoint for profile updates (requires JWT token)"""
    try:
        profile = getattr(request.user, 'profile', None)
        form = UserProfileUpdateForm(request.data, instance=profile)
        
        if form.is_valid():
            form.save()
            response_data = {
                'success': True,
                'message': 'Profile updated successfully!'
            }
            
            response = Response(response_data, status=status.HTTP_200_OK)
            response["Access-Control-Allow-Credentials"] = "true"
            return response
        else:
            errors = {}
            for field, field_errors in form.errors.items():
                errors[field] = [str(error) for error in field_errors]
            
            response_data = {
                'success': False,
                'errors': errors
            }
            
            response = Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            response["Access-Control-Allow-Credentials"] = "true"
            return response
            
    except Exception as e:
        response_data = {
            'success': False,
            'error': str(e)
        }
        
        response = Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        response["Access-Control-Allow-Credentials"] = "true"
        return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_view(request):
    """Dashboard view - requires JWT token"""
    try:
        profile = getattr(request.user, 'profile', None)
        
        response_data = {
            'success': True,
            'message': 'Welcome to your dashboard!',
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'company_name': profile.company_name if profile else None,
                'phone_number': profile.phone_number if profile else None,
                'address': profile.address if profile else None,
            }
        }
        
        response = Response(response_data, status=status.HTTP_200_OK)
        response["Access-Control-Allow-Credentials"] = "true"
        return response
        
    except Exception as e:
        response_data = {
            'success': False,
            'error': str(e)
        }
        
        response = Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        response["Access-Control-Allow-Credentials"] = "true"
        return response


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def api_refresh_token(request):
    """API endpoint to refresh JWT access token"""
    try:
        refresh_token = request.data.get('refresh_token')
        
        if not refresh_token:
            response_data = {
                'success': False,
                'error': 'Refresh token is required.'
            }
            
            response = Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            response["Access-Control-Allow-Credentials"] = "true"
            return response
        
        # Validate and refresh token
        refresh = RefreshToken(refresh_token)
        access_token = str(refresh.access_token)
        
        response_data = {
            'success': True,
            'message': 'Token refreshed successfully!',
            'access_token': access_token,
        }
        
        response = Response(response_data, status=status.HTTP_200_OK)
        response["Access-Control-Allow-Credentials"] = "true"
        return response
        
    except Exception as e:
        response_data = {
            'success': False,
            'error': 'Invalid refresh token.'
        }
        
        response = Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        response["Access-Control-Allow-Credentials"] = "true"
        return response


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    """API endpoint to logout (blacklist refresh token)"""
    try:
        refresh_token = request.data.get('refresh_token')
        
        if refresh_token:
            # Blacklist the refresh token
            refresh = RefreshToken(refresh_token)
            refresh.blacklist()
        
        response_data = {
            'success': True,
            'message': 'Logged out successfully!'
        }
        
        response = Response(response_data, status=status.HTTP_200_OK)
        response["Access-Control-Allow-Credentials"] = "true"
        return response
        
    except Exception as e:
        response_data = {
            'success': False,
            'error': str(e)
        }
        
        response = Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        response["Access-Control-Allow-Credentials"] = "true"
        return response


# Google OAuth API endpoints
@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def google_oauth_initiate(request):
    """Initiate Google OAuth flow - returns authorization URL"""
    try:
        oauth_service = GoogleOAuthService()
        
        # Generate state parameter for CSRF protection
        local_state = f"user_{request.user.id}_{int(timezone.now().timestamp())}"
        
        # Get authorization URL and state from Google OAuth
        authorization_url, google_state = oauth_service.get_authorization_url(state=local_state)
        
        response_data = {
            'success': True,
            'authorization_url': authorization_url,
            'state': google_state,  # Use the Google OAuth state
            'local_state': local_state,  # Keep local state for reference
        }
        
        response = Response(response_data, status=status.HTTP_200_OK)
        response["Access-Control-Allow-Credentials"] = "true"
        return response
        
    except Exception as e:
        response_data = {
            'success': False,
            'error': str(e)
        }
        
        response = Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        response["Access-Control-Allow-Credentials"] = "true"
        return response


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])  # Changed from IsAuthenticated to AllowAny
def google_oauth_callback(request):
    """Handle Google OAuth callback and exchange code for tokens"""
    try:
        authorization_code = request.GET.get('code')
        state = request.GET.get('state')
        error = request.GET.get('error')
        
        if error:
            response_data = {
                'success': False,
                'error': f'OAuth error: {error}'
            }
            
            response = Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            response["Access-Control-Allow-Credentials"] = "true"
            return response
        
        if not authorization_code:
            response_data = {
                'success': False,
                'error': 'Authorization code not provided'
            }
            
            response = Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            response["Access-Control-Allow-Credentials"] = "true"
            return response
        
        # Exchange code for tokens
        oauth_service = GoogleOAuthService()
        token_data = oauth_service.exchange_code_for_tokens(authorization_code)
        
        # Extract user ID from state parameter
        # State format: user_{user_id}_{timestamp}
        try:
            state_parts = state.split('_')
            if len(state_parts) >= 2 and state_parts[0] == 'user':
                user_id = int(state_parts[1])
                user = User.objects.get(id=user_id)
            else:
                raise ValueError("Invalid state parameter format")
        except (ValueError, User.DoesNotExist):
            response_data = {
                'success': False,
                'error': 'Invalid state parameter or user not found'
            }
            
            response = Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            response["Access-Control-Allow-Credentials"] = "true"
            return response
        
        # Save tokens to database
        auth_service = UserGoogleAuthService()
        auth_record = auth_service.create_or_update_auth(
            user=user,
            access_token=token_data['access_token'],
            refresh_token=token_data['refresh_token'],
            token_expiry=token_data['token_expiry'],
            scopes=token_data['scopes'],
            user_info=token_data['user_info']
        )
        
        response_data = {
            'success': True,
            'message': 'Google OAuth successful!',
            'google_auth': {
                'id': auth_record.id,
                'google_email': auth_record.google_email,
                'google_name': auth_record.google_name,
                'scopes': auth_record.scopes,
                'is_active': auth_record.is_active,
            }
        }
        
        response = Response(response_data, status=status.HTTP_200_OK)
        response["Access-Control-Allow-Credentials"] = "true"
        return response
        
    except Exception as e:
        response_data = {
            'success': False,
            'error': str(e)
        }
        
        response = Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        response["Access-Control-Allow-Credentials"] = "true"
        return response


@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def google_oauth_status(request):
    """Get current Google OAuth status for user"""
    try:
        auth_service = UserGoogleAuthService()
        auth_record = auth_service.get_valid_auth(request.user)
        
        if not auth_record:
            response_data = {
                'success': True,
                'connected': False,
                'message': 'No active Google OAuth connection'
            }
        else:
            response_data = {
                'success': True,
                'connected': True,
                'google_auth': {
                    'id': auth_record.id,
                    'google_email': auth_record.google_email,
                    'google_name': auth_record.google_name,
                    'scopes': auth_record.scopes,
                    'is_active': auth_record.is_active,
                    'last_used': auth_record.last_used,
                    'token_expiry': auth_record.token_expiry,
                }
            }
        
        response = Response(response_data, status=status.HTTP_200_OK)
        response["Access-Control-Allow-Credentials"] = "true"
        return response
        
    except Exception as e:
        response_data = {
            'success': False,
            'error': str(e)
        }
        
        response = Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        response["Access-Control-Allow-Credentials"] = "true"
        return response


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def google_oauth_disconnect(request):
    """Disconnect Google OAuth connection"""
    try:
        auth_service = UserGoogleAuthService()
        auth_record = auth_service.get_valid_auth(request.user)
        
        if auth_record:
            auth_record.is_active = False
            auth_record.save()
            
            response_data = {
                'success': True,
                'message': 'Google OAuth disconnected successfully!'
            }
        else:
            response_data = {
                'success': False,
                'error': 'No active Google OAuth connection found'
            }
        
        response = Response(response_data, status=status.HTTP_200_OK)
        response["Access-Control-Allow-Credentials"] = "true"
        return response
        
    except Exception as e:
        response_data = {
            'success': False,
            'error': str(e)
        }
        
        response = Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        response["Access-Control-Allow-Credentials"] = "true"
        return response


@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def google_ads_accounts(request):
    """Get Google Ads accounts accessible to the user"""
    try:
        auth_service = UserGoogleAuthService()
        auth_record = auth_service.get_valid_auth(request.user)
        
        if not auth_record:
            response_data = {
                'success': False,
                'error': 'No valid Google OAuth connection found'
            }
            
            response = Response(response_data, status=status.HTTP_401_UNAUTHORIZED)
            response["Access-Control-Allow-Credentials"] = "true"
            return response
        
        # Check if token needs refresh
        if auth_record.needs_refresh():
            auth_record = auth_service.refresh_user_tokens(request.user)
            if not auth_record:
                response_data = {
                    'success': False,
                    'error': 'Failed to refresh Google OAuth token'
                }
                
                response = Response(response_data, status=status.HTTP_401_UNAUTHORIZED)
                response["Access-Control-Allow-Credentials"] = "true"
                return response
        
        # Get Google Ads accounts
        oauth_service = GoogleOAuthService()
        accounts = oauth_service.get_google_ads_accounts(auth_record.access_token)
        
        response_data = {
            'success': True,
            'accounts': accounts,
            'count': len(accounts)
        }
        
        response = Response(response_data, status=status.HTTP_200_OK)
        response["Access-Control-Allow-Credentials"] = "true"
        return response
        
    except Exception as e:
        response_data = {
            'success': False,
            'error': str(e)
        }
        
        response = Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        response["Access-Control-Allow-Credentials"] = "true"
        return response


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def google_oauth_exchange_tokens(request):
    """API endpoint for frontend to exchange OAuth code for tokens"""
    try:
        code = request.data.get('code')
        state = request.data.get('state')
        
        if not code or not state:
            response_data = {
                'success': False,
                'error': 'Code and state are required'
            }
            
            response = Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            response["Access-Control-Allow-Credentials"] = "true"
            return response
        
        # Extract user ID from state parameter
        # State format: user_{user_id}_{timestamp}
        try:
            state_parts = state.split('_')
            if len(state_parts) >= 2 and state_parts[0] == 'user':
                user_id = int(state_parts[1])
                user = User.objects.get(id=user_id)
            else:
                raise ValueError("Invalid state parameter format")
        except (ValueError, User.DoesNotExist):
            response_data = {
                'success': False,
                'error': 'Invalid state parameter or user not found'
            }
            
            response = Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            response["Access-Control-Allow-Credentials"] = "true"
            return response
        
        # Exchange code for tokens
        try:
            oauth_service = GoogleOAuthService()
            token_data = oauth_service.exchange_code_for_tokens(code)
        except Exception as oauth_error:
            # Log the specific OAuth error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"OAuth token exchange failed: {str(oauth_error)}")
            
            response_data = {
                'success': False,
                'error': f'Token exchange failed: {str(oauth_error)}'
            }
            
            response = Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            response["Access-Control-Allow-Credentials"] = "true"
            return response
        
        # Save tokens to database
        try:
            auth_service = UserGoogleAuthService()
            auth_record = auth_service.create_or_update_auth(
                user=user,
                access_token=token_data['access_token'],
                refresh_token=token_data['refresh_token'],
                token_expiry=token_data['token_expiry'],
                scopes=token_data['scopes'],
                user_info=token_data['user_info']
            )
        except Exception as db_error:
            # Log the database error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Database save failed: {str(db_error)}")
            
            response_data = {
                'success': False,
                'error': f'Failed to save tokens: {str(db_error)}'
            }
            
            response = Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            response["Access-Control-Allow-Credentials"] = "true"
            return response
        
        response_data = {
            'success': True,
            'message': 'Google OAuth successful!',
            'google_auth': {
                'id': auth_record.id,
                'google_email': auth_record.google_email,
                'google_name': auth_record.google_name,
                'scopes': auth_record.scopes,
                'is_active': auth_record.is_active,
            }
        }
        
        response = Response(response_data, status=status.HTTP_200_OK)
        response["Access-Control-Allow-Credentials"] = "true"
        return response
        
    except Exception as e:
        # Log the general error
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error in google_oauth_exchange_tokens: {str(e)}")
        
        response_data = {
            'success': False,
            'error': str(e)
        }
        
        response = Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        response["Access-Control-Allow-Credentials"] = "true"
        return response

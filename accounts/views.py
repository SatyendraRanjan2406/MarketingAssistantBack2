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
        data = request.data
        email = data.get('email')
        password = data.get('password')
        name = data.get('name', '')
        
        # Validate required fields
        if not email or not password:
            response_data = {
                'success': False,
                'error': 'Email and password are required.'
            }
            response = Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            response["Access-Control-Allow-Credentials"] = "true"
            return response
        
        # Check if email is already used by a regular user
        if User.objects.filter(email=email).exists():
            response_data = {
                'success': False,
                'error': 'This email address is already in use.'
            }
            response = Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            response["Access-Control-Allow-Credentials"] = "true"
            return response
        
        # Check if email is already used for Google auth
        from .models import UserGoogleAuth
        if UserGoogleAuth.objects.filter(google_email=email, is_active=True).exists():
            response_data = {
                'success': False,
                'error': 'Email used for google auth. use another email'
            }
            response = Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            response["Access-Control-Allow-Credentials"] = "true"
            return response
        
        # Parse name into first_name and last_name
        name_parts = name.strip().split(' ', 1) if name else ['', '']
        first_name = name_parts[0] if len(name_parts) > 0 else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        # Generate username from email (before @ symbol)
        username = email.split('@')[0]
        # Ensure username is unique
        original_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{original_username}{counter}"
            counter += 1
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        # Calculate token expiry (1 hour from now)
        from datetime import datetime, timedelta
        expires_in = 3600  # 1 hour in seconds
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        
        # Check if user has Google OAuth connection (should be False for new users)
        auth_service = UserGoogleAuthService()
        google_auth_record = auth_service.get_valid_auth(user)
        has_google_oauth = google_auth_record is not None
        
        response_data = {
            'success': True,
            'message': 'Account created successfully',
            'data': {
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'name': name,
                    'provider': 'email',
                    'created_at': user.date_joined.isoformat() + 'Z',
                    'updated_at': user.date_joined.isoformat() + 'Z'
                },
                'tokens': {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'expires_in': expires_in
                },
                'google_oauth_connected': has_google_oauth
            }
        }
        
        response = Response(response_data, status=status.HTTP_201_CREATED)
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
        username_or_email = data.get('username') or data.get('email')
        password = data.get('password')
        
        if not username_or_email or not password:
            response_data = {
                'success': False,
                'error': 'Username/email and password are required.'
            }
            
            response = Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            response["Access-Control-Allow-Credentials"] = "true"
            return response
        
        # Try to authenticate with username first, then email
        user = authenticate(username=username_or_email, password=password)
        
        # If username authentication fails, try email authentication
        if user is None and '@' in username_or_email:
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
        if user is not None:
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            # Get user profile info
            profile = getattr(user, 'profile', None)
            
            # Check if user has Google OAuth connection
            auth_service = UserGoogleAuthService()
            google_auth_record = auth_service.get_valid_auth(user)
            has_google_oauth = google_auth_record is not None
            
            # Get accessible customers if Google OAuth is connected
            accessible_customers = None
            if has_google_oauth and google_auth_record.accessible_customers:
                accessible_customers = {
                    'customers': google_auth_record.accessible_customers.get('customers', []),
                    'total_count': google_auth_record.accessible_customers.get('total_count', 0),
                    'last_updated': google_auth_record.accessible_customers.get('last_updated'),
                    'raw_response': google_auth_record.accessible_customers.get('raw_response', {})
                }
            
            # Derive name from first_name and last_name
            name = f"{user.first_name} {user.last_name}".strip()
            if not name:
                name = user.username
            
            response_data = {
                'success': True,
                'message': 'Login successful',
                'data': {
                    'user': {
                        'id': str(user.id),
                        'email': user.email,
                        'name': name,
                        'provider': 'email',
                        'created_at': user.date_joined.isoformat() + 'Z',
                        'updated_at': user.last_login.isoformat() + 'Z' if user.last_login else user.date_joined.isoformat() + 'Z'
                    },
                    'tokens': {
                        'access_token': access_token,
                        'refresh_token': refresh_token,
                        'expires_in': 3600
                    },
                    'google_oauth_connected': has_google_oauth,
                    'accessible_customers': accessible_customers
                }
            }
            
            response = Response(response_data, status=status.HTTP_200_OK)
            response["Access-Control-Allow-Credentials"] = "true"
            return response
        else:
            response_data = {
                'success': False,
                'error': 'Invalid username/email or password.'
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


@api_view(['GET', 'OPTIONS'])
@permission_classes([IsAuthenticated])
def google_oauth_connect(request):
    """Complete Google OAuth connection - check existing or initiate new flow"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = Response(status=status.HTTP_200_OK)
        return response
    
    try:
        auth_service = UserGoogleAuthService()
        
        # Check if user already has a valid Google OAuth connection
        auth_record = auth_service.get_valid_auth(request.user)
        
        if auth_record:
            # Check if token is expired
            if auth_record.is_token_expired():
                # Try to refresh the token
                try:
                    refreshed_record = auth_service.refresh_user_tokens(request.user)
                    if refreshed_record:
                        response_data = {
                            'success': True,
                            'connected': True,
                            'message': 'Google OAuth connection refreshed successfully',
                            'google_auth': {
                                'id': refreshed_record.id,
                                'google_email': refreshed_record.google_email,
                                'google_name': refreshed_record.google_name,
                                'scopes': refreshed_record.scopes,
                                'is_active': refreshed_record.is_active,
                                'last_used': refreshed_record.last_used.isoformat() + 'Z',
                                'token_expiry': refreshed_record.token_expiry.isoformat() + 'Z',
                                'is_token_expired': refreshed_record.is_token_expired(),
                                'needs_refresh': refreshed_record.needs_refresh()
                            }
                        }
                    else:
                        # Refresh failed, return 401
                        response_data = {
                            'success': False,
                            'connected': False,
                            'error': 'Google OAuth token refresh failed. Please reconnect your Google account.',
                            'requires_reauth': True
                        }
                        response = Response(response_data, status=status.HTTP_401_UNAUTHORIZED)
                        return response
                except Exception as refresh_error:
                    # Refresh failed, return 401
                    response_data = {
                        'success': False,
                        'connected': False,
                        'error': f'Google OAuth token refresh failed: {str(refresh_error)}. Please reconnect your Google account.',
                        'requires_reauth': True
                    }
                    response = Response(response_data, status=status.HTTP_401_UNAUTHORIZED)
                    response["Access-Control-Allow-Credentials"] = "true"
                    return response
            else:
                # Token is still valid
                response_data = {
                    'success': True,
                    'connected': True,
                    'message': 'Google OAuth connection is active and valid',
                    'google_auth': {
                        'id': auth_record.id,
                        'google_email': auth_record.google_email,
                        'google_name': auth_record.google_name,
                        'scopes': auth_record.scopes,
                        'is_active': auth_record.is_active,
                        'last_used': auth_record.last_used.isoformat() + 'Z',
                        'token_expiry': auth_record.token_expiry.isoformat() + 'Z',
                        'is_token_expired': auth_record.is_token_expired(),
                        'needs_refresh': auth_record.needs_refresh()
                    }
                }
        else:
            # No Google OAuth connection found - initiate OAuth flow
            from django.conf import settings
            import secrets
            import urllib.parse
            
            # Generate state parameter for CSRF protection with user ID
            import time
            timestamp = int(time.time())
            state = f"user_{request.user.id}_{timestamp}_{secrets.token_urlsafe(16)}"
            
            # Store state in session for validation
            request.session['google_oauth_state'] = state
            
            # Build Google OAuth URL
            scopes = settings.GOOGLE_OAUTH_CONFIG['scopes']
            if isinstance(scopes, list):
                scopes = ' '.join(scopes)
            
            google_oauth_url = (
                f"https://accounts.google.com/o/oauth2/v2/auth?"
                f"client_id={settings.GOOGLE_OAUTH_CONFIG['client_id']}&"
                f"redirect_uri={urllib.parse.quote(settings.GOOGLE_OAUTH_CONFIG['redirect_uri'])}&"
                f"scope={urllib.parse.quote(scopes)}&"
                f"response_type=code&"
                f"state={state}&"
                f"access_type=offline&"
                f"prompt=consent"
            )
            
            response_data = {
                'success': True,
                'connected': False,
                'message': 'No Google OAuth connection found. OAuth flow initiated.',
                'authorization_url': google_oauth_url,
                'state': state,
                'requires_reauth': False
            }
        
        response = Response(response_data, status=status.HTTP_200_OK)
        return response
        
    except Exception as e:
        response_data = {
            'success': False,
            'connected': False,
            'error': str(e),
            'requires_reauth': True
        }
        
        response = Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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
        # State format: user_{user_id}_{timestamp}_{random_string}
        try:
            state_parts = state.split('_')
            if len(state_parts) >= 3 and state_parts[0] == 'user':
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


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_accessible_customers(request):
    """Refresh accessible customers for the authenticated user"""
    try:
        auth_service = UserGoogleAuthService()
        success = auth_service.refresh_accessible_customers(request.user)
        
        if success:
            # Get updated auth record to return customer info
            from .models import UserGoogleAuth
            auth_record = UserGoogleAuth.objects.filter(
                user=request.user,
                is_active=True
            ).first()
            
            if auth_record and auth_record.accessible_customers:
                customers = auth_record.accessible_customers.get('customers', [])
                response_data = {
                    'success': True,
                    'message': f'Successfully refreshed {len(customers)} accessible customers',
                    'accessible_customers': customers,
                    'total_count': len(customers),
                    'last_updated': auth_record.accessible_customers.get('last_updated')
                }
            else:
                response_data = {
                    'success': True,
                    'message': 'Accessible customers refreshed (no customers found)',
                    'accessible_customers': [],
                    'total_count': 0
                }
        else:
            response_data = {
                'success': False,
                'error': 'Failed to refresh accessible customers'
            }
        
        response = Response(response_data, status=status.HTTP_200_OK if success else status.HTTP_400_BAD_REQUEST)
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

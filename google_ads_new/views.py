import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Avg
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import ModelSerializer
from django.utils import timezone
from google.ads.googleads.errors import GoogleAdsException
import requests
import os

from .models import (
    GoogleAdsAccount, GoogleAdsCampaign, GoogleAdsAdGroup,
    GoogleAdsKeyword, GoogleAdsPerformance, DataSyncLog
)
from .google_ads_api_service import GoogleAdsAPIService, list_accessible_customers
from .sync_service import GoogleAdsSyncService
from .tasks import (
    daily_sync_task, weekly_sync_task, force_sync_task,
    sync_from_api_task, sync_campaigns_task, sync_ad_groups_task, sync_keywords_task
)

logger = logging.getLogger(__name__)


# Serializers
class GoogleAdsAccountSerializer(ModelSerializer):
    class Meta:
        model = GoogleAdsAccount
        fields = '__all__'


class GoogleAdsCampaignSerializer(ModelSerializer):
    class Meta:
        model = GoogleAdsCampaign
        fields = '__all__'


class GoogleAdsAdGroupSerializer(ModelSerializer):
    class Meta:
        model = GoogleAdsAdGroup
        fields = '__all__'


class GoogleAdsKeywordSerializer(ModelSerializer):
    class Meta:
        model = GoogleAdsKeyword
        fields = '__all__'


class GoogleAdsPerformanceSerializer(ModelSerializer):
    class Meta:
        model = GoogleAdsPerformance
        fields = '__all__'


class DataSyncLogSerializer(ModelSerializer):
    class Meta:
        model = DataSyncLog
        fields = '__all__'


# ViewSets
class GoogleAdsAccountViewSet(ModelViewSet):
    queryset = GoogleAdsAccount.objects.all()
    serializer_class = GoogleAdsAccountSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return GoogleAdsAccount.objects.filter(user=self.request.user)


class GoogleAdsCampaignViewSet(ModelViewSet):
    queryset = GoogleAdsCampaign.objects.all()
    serializer_class = GoogleAdsCampaignSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return GoogleAdsCampaign.objects.filter(account__user=self.request.user)


class GoogleAdsAdGroupViewSet(ModelViewSet):
    queryset = GoogleAdsAdGroup.objects.all()
    serializer_class = GoogleAdsAdGroupSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return GoogleAdsAdGroup.objects.filter(campaign__account__user=self.request.user)


class GoogleAdsKeywordViewSet(ModelViewSet):
    queryset = GoogleAdsKeyword.objects.all()
    serializer_class = GoogleAdsKeywordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return GoogleAdsKeyword.objects.filter(ad_group__campaign__account__user=self.request.user)


class GoogleAdsPerformanceViewSet(ModelViewSet):
    queryset = GoogleAdsPerformance.objects.all()
    serializer_class = GoogleAdsPerformanceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return GoogleAdsPerformance.objects.filter(account__user=self.request.user)


class DataSyncLogViewSet(ModelViewSet):
    queryset = DataSyncLog.objects.all()
    serializer_class = DataSyncLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return DataSyncLog.objects.filter(account__user=self.request.user)


# API Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sync_status_view(request):
    """Get sync status for user's accounts"""
    try:
        user_accounts = GoogleAdsAccount.objects.filter(user=request.user, is_active=True)
        
        sync_status = []
        for account in user_accounts:
            latest_sync = DataSyncLog.objects.filter(account=account).order_by('-created_at').first()
            
            status_data = {
                'account_id': account.id,
                'account_name': account.account_name,
                'customer_id': account.customer_id,
                'sync_status': account.sync_status,
                'last_sync_at': account.last_sync_at.isoformat() if account.last_sync_at else None,
                'latest_sync_log': {
                    'sync_type': latest_sync.sync_type if latest_sync else None,
                    'status': latest_sync.status if latest_sync else None,
                    'created_at': latest_sync.created_at.isoformat() if latest_sync else None,
                    'results': latest_sync.results if latest_sync else {}
                } if latest_sync else None
            }
            sync_status.append(status_data)
        
        return Response({
            'success': True,
            'accounts': sync_status
        })
        
    except Exception as e:
        logger.error(f"Error in sync status view: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_data_view(request):
    """Trigger data sync operations"""
    try:
        sync_type = request.data.get('sync_type')
        account_id = request.data.get('account_id')
        weeks = request.data.get('weeks', 10)
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        if not sync_type:
            return Response({
                'success': False,
                'error': 'sync_type is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get account
        account = None
        if account_id:
            try:
                account = GoogleAdsAccount.objects.get(id=account_id, user=request.user, is_active=True)
            except GoogleAdsAccount.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Account not found or inactive'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            # Get first active account
            account = GoogleAdsAccount.objects.filter(user=request.user, is_active=True).first()
        
        # Check if we have a valid account for sync types that require it
        if sync_type in ['daily', 'weekly', 'force', 'api_sync', 'campaigns', 'ad_groups', 'keywords'] and not account:
            return Response({
                'success': False,
                'error': 'No active accounts found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Trigger appropriate sync task
        if sync_type == 'daily':
            task = daily_sync_task.delay(account.id)
            message = 'Daily sync task queued successfully'
            
        elif sync_type == 'weekly':
            task = weekly_sync_task.delay(account.id, weeks)
            message = f'Weekly sync task for {weeks} weeks queued successfully'
            
        elif sync_type == 'force':
            task = force_sync_task.delay(account.id, weeks)
            message = f'Force sync task for {weeks} weeks queued successfully'
            
        elif sync_type == 'api_sync':
            if not start_date or not end_date:
                return Response({
                    'success': False,
                    'error': 'start_date and end_date are required for API sync'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            task = sync_from_api_task.delay(account.id, start_date, end_date)
            message = f'API sync task from {start_date} to {end_date} queued successfully'
            
        elif sync_type == 'campaigns':
            task = sync_campaigns_task.delay(account.id)
            message = 'Campaigns sync task queued successfully'
            
        elif sync_type == 'ad_groups':
            task = sync_ad_groups_task.delay(account.id)
            message = 'Ad groups sync task queued successfully'
            
        elif sync_type == 'keywords':
            task = sync_keywords_task.delay(account.id)
            message = 'Keywords sync task queued successfully'
            
        elif sync_type == 'google_ads_api':
            try:
                # Import Google OAuth service to get access token
                from accounts.google_oauth_service import UserGoogleAuthService
                
                # Get user's Google OAuth tokens
                auth_service = UserGoogleAuthService()
                user_auth = auth_service.get_valid_auth(request.user)
                
                if not user_auth:
                    return Response({
                        'success': False,
                        'error': 'Google OAuth not connected. Please connect your Google account first.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Get access token and developer token
                access_token = user_auth.access_token
                developer_token = os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN', '')
                
                if not developer_token:
                    return Response({
                        'success': False,
                        'error': 'Developer token not configured'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                # Step 1: Get accessible customers
                customers_url = "https://googleads.googleapis.com/v21/customers:listAccessibleCustomers"
                customers_headers = {
                    "Authorization": f"Bearer {access_token}",
                    "developer-token": developer_token
                }
                
                customers_response = requests.get(customers_url, headers=customers_headers)
                customers_response.raise_for_status()
                customers_data = customers_response.json()
                
                logger.info(f"Accessible customers: {customers_data}")
                
                # Step 2: Get customer details and campaigns for each customer
                customer_details = []
                disabled_customers = []
                all_campaigns = []
                saved_accounts = []
                
                for resource_name in customers_data.get('resourceNames', []):
                    customer_id = resource_name.split('/')[-1]
                    
                    try:
                        # Get customer details
                        customer_url = f"https://googleads.googleapis.com/v21/customers/{customer_id}/googleAds:search"
                        customer_headers = {
                            "Authorization": f"Bearer {access_token}",
                            "developer-token": developer_token,
                            "Content-Type": "application/json"
                        }
                        
                        customer_payload = {
                            "query": "SELECT customer.id, customer.descriptive_name, customer.currency_code, customer.time_zone, customer.manager, customer.test_account FROM customer"
                        }
                        
                        customer_response = requests.post(customer_url, headers=customer_headers, json=customer_payload)
                        
                        # Check if customer is enabled
                        if customer_response.status_code == 403:
                            error_data = customer_response.json()
                            if 'error' in error_data and 'details' in error_data['error']:
                                for detail in error_data['error']['details']:
                                    if 'errors' in detail:
                                        for error in detail['errors']:
                                            if error.get('errorCode', {}).get('authorizationError') == 'CUSTOMER_NOT_ENABLED':
                                                logger.warning(f"Customer {customer_id} is not enabled: {error.get('message', 'Unknown error')}")
                                                disabled_customers.append({
                                                    'customer_id': customer_id,
                                                    'reason': 'CUSTOMER_NOT_ENABLED',
                                                    'message': error.get('message', 'Customer account is not yet enabled or has been deactivated')
                                                })
                                                # Skip to next customer - don't process this one further
                                                continue
                        
                        # If we get here, customer is enabled, so proceed with normal processing
                        customer_response.raise_for_status()
                        customer_data = customer_response.json()
                        
                        logger.info(f"Customer {customer_id} details: {customer_data}")
                        
                        # Extract customer info
                        customer_info = None
                        if 'results' in customer_data and customer_data['results']:
                            customer_info = customer_data['results'][0]
                        
                        if customer_info:
                            # Save/update Google Ads account in database
                            account, created = GoogleAdsAccount.objects.get_or_create(
                                customer_id=customer_id,
                                defaults={
                                    'user': request.user,
                                    'account_name': customer_info.get('customer', {}).get('descriptiveName', f'Account {customer_id}'),
                                    'currency_code': customer_info.get('customer', {}).get('currencyCode', 'USD'),
                                    'time_zone': customer_info.get('customer', {}).get('timeZone', 'America/New_York'),
                                    'is_active': True,
                                    'is_manager': customer_info.get('customer', {}).get('manager', False),
                                    'is_test_account': customer_info.get('customer', {}).get('testAccount', False),
                                    'sync_status': 'active',
                                    'last_sync_at': timezone.now()
                                }
                            )
                            
                            if not created:
                                # Update existing account
                                account.account_name = customer_info.get('customer', {}).get('descriptiveName', f'Account {customer_id}')
                                account.currency_code = customer_info.get('customer', {}).get('currencyCode', 'USD')
                                account.time_zone = customer_info.get('customer', {}).get('timeZone', 'America/New_York')
                                account.is_active = True
                                account.is_manager = customer_info.get('customer', {}).get('manager', False)
                                account.is_test_account = customer_info.get('customer', {}).get('testAccount', False)
                                account.sync_status = 'active'
                                account.last_sync_at = timezone.now()
                                account.save()
                            
                            saved_accounts.append({
                                'customer_id': customer_id,
                                'account_name': account.account_name,
                                'created': created,
                                'updated': not created
                            })
                            
                            # Get campaigns for this customer
                            try:
                                campaigns_url = f"https://googleads.googleapis.com/v21/customers/{customer_id}/googleAds:search"
                                
                                # For manager accounts, use the manager's customer ID as login-customer-id
                                # For sub-accounts, use the manager's customer ID
                                login_customer_id = customer_id
                                if customer_info and customer_info.get('customer', {}).get('manager', False):
                                    # This is a manager account, use its own ID
                                    login_customer_id = customer_id
                                else:
                                    # This is a sub-account, we need to find the manager account
                                    # For now, use the current customer ID, but this might need adjustment
                                    login_customer_id = customer_id
                                
                                # Add login-customer-id header for manager accounts
                                campaigns_headers = {
                                    "Authorization": f"Bearer {access_token}",
                                    "developer-token": developer_token,
                                    "Content-Type": "application/json",
                                    "login-customer-id": str(login_customer_id)  # Convert to string
                                }
                                
                                campaigns_payload = {
                                    "query": """
                                        SELECT 
                                            campaign.id, 
                                            campaign.name, 
                                            campaign.status, 
                                            campaign.start_date, 
                                            campaign.end_date, 
                                            campaign.advertising_channel_type,
                                            metrics.impressions, 
                                            metrics.clicks,
                                            metrics.cost_micros
                                        FROM campaign
                                    """
                                }
                                
                                logger.info(f"Fetching campaigns for customer {customer_id}")
                                logger.info(f"Campaigns URL: {campaigns_url}")
                                logger.info(f"Login customer ID: {login_customer_id}")
                                logger.info(f"Campaigns headers: {campaigns_headers}")
                                logger.info(f"Campaigns payload: {campaigns_payload}")
                                
                                campaigns_response = requests.post(campaigns_url, headers=campaigns_headers, json=campaigns_payload)
                                logger.info(f"Campaigns response status: {campaigns_response.status_code}")
                                
                                # If first attempt fails, try without login-customer-id header
                                if campaigns_response.status_code != 200:
                                    logger.info(f"First attempt failed, trying without login-customer-id header")
                                    campaigns_headers_fallback = {
                                        "Authorization": f"Bearer {access_token}",
                                        "developer-token": developer_token,
                                        "Content-Type": "application/json"
                                    }
                                    
                                    campaigns_response = requests.post(campaigns_url, headers=campaigns_headers_fallback, json=campaigns_payload)
                                    logger.info(f"Fallback campaigns response status: {campaigns_response.status_code}")
                                
                                campaigns_response.raise_for_status()
                                campaigns_data = campaigns_response.json()
                                
                                logger.info(f"Campaigns for customer {customer_id}: {campaigns_data}")
                                
                                # Save campaigns to database
                                if 'results' in campaigns_data and campaigns_data['results']:
                                    logger.info(f"Found {len(campaigns_data['results'])} campaigns for customer {customer_id}")
                                    for campaign_result in campaigns_data['results']:
                                        campaign_info = campaign_result.get('campaign', {})
                                        metrics_info = campaign_result.get('metrics', {})
                                        
                                        logger.info(f"Processing campaign: {campaign_info}")
                                        
                                        # Handle date conversion from Google Ads API format
                                        start_date = None
                                        end_date = None
                                        
                                        if campaign_info.get('startDate'):
                                            try:
                                                start_date = datetime.strptime(campaign_info.get('startDate'), '%Y-%m-%d').date()
                                            except (ValueError, TypeError):
                                                start_date = None
                                        
                                        if campaign_info.get('endDate'):
                                            try:
                                                end_date = datetime.strptime(campaign_info.get('endDate'), '%Y-%m-%d').date()
                                            except (ValueError, TypeError):
                                                end_date = None
                                        
                                        # Only save campaign if we have a valid start_date (required field)
                                        if start_date:
                                            campaign, campaign_created = GoogleAdsCampaign.objects.get_or_create(
                                                campaign_id=campaign_info.get('id'),
                                                account=account,
                                                defaults={
                                                    'campaign_name': campaign_info.get('name', 'Unnamed Campaign'),
                                                    'campaign_status': campaign_info.get('status', 'ENABLED'),
                                                    'campaign_type': campaign_info.get('advertisingChannelType', 'SEARCH'),
                                                    'start_date': start_date,
                                                    'end_date': end_date,
                                                    'budget_amount': (campaign_info.get('budgetAmountMicros', 0) / 1000000) if campaign_info.get('budgetAmountMicros') else None,
                                                    'budget_type': 'DAILY',  # Default value
                                                    'created_at': timezone.now(),
                                                    'updated_at': timezone.now()
                                                }
                                            )
                                            
                                            if not campaign_created:
                                                # Update existing campaign
                                                campaign.campaign_name = campaign_info.get('name', 'Unnamed Campaign')
                                                campaign.campaign_status = campaign_info.get('status', 'ENABLED')
                                                campaign.campaign_type = campaign_info.get('advertisingChannelType', 'SEARCH')
                                                campaign.start_date = start_date
                                                campaign.end_date = end_date
                                                campaign.budget_amount = (campaign_info.get('budgetAmountMicros', 0) / 1000000) if campaign_info.get('budgetAmountMicros') else None
                                                campaign.updated_at = timezone.now()
                                                campaign.save()
                                            
                                            all_campaigns.append({
                                                'campaign_id': campaign_info.get('id'),
                                                'name': campaign.campaign_name,
                                                'status': campaign.campaign_status,
                                                'account_id': customer_id,
                                                'created': campaign_created,
                                                'updated': not campaign_created,
                                                'metrics': {
                                                    'impressions': metrics_info.get('impressions', 0),
                                                    'clicks': metrics_info.get('clicks', 0),
                                                    'cost_micros': metrics_info.get('costMicros', 0)
                                                }
                                            })
                                            
                                            logger.info(f"Successfully saved campaign {campaign_info.get('id')}: {campaign.campaign_name}")
                                        else:
                                            logger.warning(f"Skipping campaign {campaign_info.get('id')} - no valid start_date")
                                else:
                                    logger.warning(f"No campaigns found for customer {customer_id}. Response: {campaigns_data}")
                                
                            except Exception as campaign_error:
                                logger.error(f"Error fetching campaigns for customer {customer_id}: {campaign_error}")
                                logger.error(f"Campaign error details: {type(campaign_error).__name__}: {str(campaign_error)}")
                        
                        customer_details.append({
                            'customer_id': customer_id,
                            'details': customer_data,
                            'status': 'enabled',
                            'campaigns_count': len([c for c in all_campaigns if c['account_id'] == customer_id])
                        })
                        
                    except requests.exceptions.RequestException as e:
                        # This will only catch errors that weren't already handled above
                        logger.error(f"Error fetching customer {customer_id}: {e}")
                        # Only add to disabled_customers if not already added for CUSTOMER_NOT_ENABLED
                        if not any(c['customer_id'] == customer_id and c['reason'] == 'CUSTOMER_NOT_ENABLED' for c in disabled_customers):
                            disabled_customers.append({
                                'customer_id': customer_id,
                                'reason': 'API_ERROR',
                                'message': str(e)
                            })
                    except Exception as e:
                        logger.error(f"Unexpected error with customer {customer_id}: {e}")
                        # Only add to disabled_customers if not already added
                        if not any(c['customer_id'] == customer_id for c in disabled_customers):
                            disabled_customers.append({
                                'customer_id': customer_id,
                                'reason': 'UNKNOWN_ERROR',
                                'message': str(e)
                            })
                
                # Log sync operation
                try:
                    from .models import DataSyncLog
                    DataSyncLog.objects.create(
                        user=request.user,
                        sync_type='google_ads_api',
                        status='SUCCESS',
                        accounts_processed=len(saved_accounts),
                        campaigns_processed=len(all_campaigns),
                        details=f"Synced {len(saved_accounts)} accounts and {len(all_campaigns)} campaigns from Google Ads API"
                    )
                except Exception as log_error:
                    logger.error(f"Error logging sync operation: {log_error}")
                
                # Return Google Ads API sync results
                return Response({
                    'success': True,
                    'message': f'Google Ads API sync completed successfully. {len(customer_details)} enabled customers, {len(disabled_customers)} disabled/inactive customers, {len(all_campaigns)} campaigns processed',
                    'sync_type': 'google_ads_api',
                    'accessible_customers': customers_data,
                    'enabled_customers': customer_details,
                    'disabled_customers': disabled_customers,
                    'saved_accounts': saved_accounts,
                    'campaigns': all_campaigns,
                    'total_customers': len(customer_details),
                    'total_disabled': len(disabled_customers),
                    'total_campaigns': len(all_campaigns),
                    'summary': {
                        'enabled': len(customer_details),
                        'disabled': len(disabled_customers),
                        'total_accessible': len(customers_data.get('resourceNames', [])),
                        'accounts_saved': len(saved_accounts),
                        'campaigns_saved': len(all_campaigns)
                    }
                })
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Google Ads API request failed: {e}")
                return Response({
                    'success': False,
                    'error': f'Google Ads API request failed: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                logger.error(f"Error in Google Ads API sync: {e}")
                return Response({
                    'success': False,
                    'error': f'Google Ads API sync failed: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        else:
            return Response({
                'success': False,
                'error': f'Invalid sync_type: {sync_type}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': True,
            'message': message,
            'task_id': task.id,
            'account_id': account.id,
            'sync_type': sync_type
        })
        
    except Exception as e:
        logger.error(f"Error in sync data view: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_synced_data_view(request):
    """Get paginated performance data for the last week"""
    try:
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 50))
        
        # Get last week's data
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=7)
        
        # Get user's accounts
        user_accounts = GoogleAdsAccount.objects.filter(user=request.user, is_active=True)
        
        if not user_accounts.exists():
            return Response({
                'success': True,
                'data': [],
                'pagination': {
                    'current_page': page,
                    'total_pages': 0,
                    'total_records': 0,
                    'has_next': False
                },
                'date_range': f"{start_date} to {end_date}"
            })
        
        # Get performance data
        performance_data = GoogleAdsPerformance.objects.filter(
            account__in=user_accounts,
            date__range=[start_date, end_date]
        ).select_related('account', 'campaign', 'ad_group', 'keyword').order_by('-date')
        
        # Paginate
        paginator = Paginator(performance_data, page_size)
        page_obj = paginator.get_page(page)
        
        # Serialize data
        data = []
        for record in page_obj:
            record_data = {
                'id': record.id,
                'date': record.date.isoformat(),
                'account_name': record.account.account_name,
                'campaign_name': record.campaign.campaign_name if record.campaign else None,
                'ad_group_name': record.ad_group.ad_group_name if record.ad_group else None,
                'keyword_text': record.keyword.keyword_text if record.keyword else None,
                'impressions': record.impressions,
                'clicks': record.clicks,
                'ctr': float(record.ctr) if record.ctr else None,
                'cost': record.cost_micros / 1000000 if record.cost_micros else 0,
                'cpc': float(record.cpc) if record.cpc else None,
                'conversions': float(record.conversions) if record.conversions else 0,
                'conversion_value': float(record.conversion_value) if record.conversion_value else 0
            }
            data.append(record_data)
        
        return Response({
            'success': True,
            'data': data,
            'pagination': {
                'current_page': page,
                'total_pages': paginator.num_pages,
                'total_records': paginator.count,
                'has_next': page_obj.has_next()
            },
            'date_range': f"{start_date} to {end_date}"
        })
        
    except Exception as e:
        logger.error(f"Error in get synced data view: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary_view(request):
    """Get dashboard summary data"""
    try:
        # Get user's accounts
        user_accounts = GoogleAdsAccount.objects.filter(user=request.user, is_active=True)
        
        if not user_accounts.exists():
            return Response({
                'success': True,
                'summary': {
                    'total_accounts': 0,
                    'total_campaigns': 0,
                    'total_ad_groups': 0,
                    'total_keywords': 0,
                    'total_performance_records': 0,
                    'recent_performance': {
                        'impressions': 0,
                        'clicks': 0,
                        'cost': 0,
                        'conversions': 0,
                        'conversion_value': 0
                    }
                }
            })
        
        # Get last 7 days
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=7)
        
        # Get summary data
        total_campaigns = GoogleAdsCampaign.objects.filter(account__in=user_accounts).count()
        total_ad_groups = GoogleAdsAdGroup.objects.filter(campaign__account__in=user_accounts).count()
        total_keywords = GoogleAdsKeyword.objects.filter(ad_group__campaign__account__in=user_accounts).count()
        
        # Get recent performance
        recent_performance = GoogleAdsPerformance.objects.filter(
            account__in=user_accounts,
            date__range=[start_date, end_date]
        ).aggregate(
            total_impressions=Sum('impressions'),
            total_clicks=Sum('clicks'),
            total_cost=Sum('cost_micros'),
            total_conversions=Sum('conversions'),
            total_conversion_value=Sum('conversion_value')
        )
        
        summary = {
            'total_accounts': user_accounts.count(),
            'total_campaigns': total_campaigns,
            'total_ad_groups': total_ad_groups,
            'total_keywords': total_keywords,
            'total_performance_records': GoogleAdsPerformance.objects.filter(account__in=user_accounts).count(),
            'recent_performance': {
                'impressions': recent_performance['total_impressions'] or 0,
                'clicks': recent_performance['total_clicks'] or 0,
                'cost': (recent_performance['total_cost'] or 0) / 1000000,
                'conversions': float(recent_performance['total_conversions'] or 0),
                'conversion_value': float(recent_performance['total_conversion_value'] or 0)
            }
        }
        
        return Response({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        logger.error(f"Error in dashboard summary view: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_connection_view(request):
    """Test Google Ads API connection"""
    try:
        account_id = request.data.get('account_id')
        
        if not account_id:
            return Response({
                'success': False,
                'error': 'account_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get account
        try:
            account = GoogleAdsAccount.objects.get(id=account_id, user=request.user, is_active=True)
        except GoogleAdsAccount.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Account not found or inactive'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Test connection
        api_service = GoogleAdsAPIService()
        connection_result = api_service.test_connection(account.customer_id)
        
        return Response({
            'success': True,
            'connection_result': connection_result,
            'account_id': account.id,
            'customer_id': account.customer_id
        })
        
    except Exception as e:
        logger.error(f"Error in test connection view: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sync_logs_view(request):
    """Get sync logs for user's accounts"""
    try:
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        account_id = request.GET.get('account_id')
        sync_type = request.GET.get('sync_type')
        
        # Build queryset
        queryset = DataSyncLog.objects.filter(account__user=request.user)
        
        if account_id:
            queryset = queryset.filter(account_id=account_id)
        
        if sync_type:
            queryset = queryset.filter(sync_type=sync_type)
        
        # Order by creation date
        queryset = queryset.order_by('-created_at')
        
        # Paginate
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        # Serialize data
        logs = []
        for log in page_obj:
            log_data = {
                'id': log.id,
                'sync_type': log.sync_type,
                'account_name': log.account.account_name if log.account else None,
                'status': log.status,
                'start_date': log.start_date.isoformat() if log.start_date else None,
                'end_date': log.end_date.isoformat() if log.end_date else None,
                'results': log.results,
                'error_message': log.error_message,
                'created_at': log.created_at.isoformat(),
                'completed_at': log.completed_at.isoformat() if log.completed_at else None,
                'duration_seconds': float(log.duration_seconds) if log.duration_seconds else None
            }
            logs.append(log_data)
        
        return Response({
            'success': True,
            'logs': logs,
            'pagination': {
                'current_page': page,
                'total_pages': paginator.num_pages,
                'total_records': paginator.count,
                'has_next': page_obj.has_next()
            }
        })
        
    except Exception as e:
        logger.error(f"Error in get sync logs view: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([])  # No permissions required
@csrf_exempt
def request_account_access_view(request):
    """Request access to another Google Ads account via CustomerClientLinkService"""
    try:
        # Get parameters from request
        manager_customer_id = request.data.get('manager_customer_id')
        client_customer_id = request.data.get('client_customer_id')
        
        if not manager_customer_id or not client_customer_id:
            return Response({
                'success': False,
                'error': 'Both manager_customer_id and client_customer_id are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # For testing purposes, skip user validation
        # In production, you should validate user permissions here
        # manager_account = get_object_or_404(
        #     GoogleAdsAccount, 
        #     customer_id=manager_customer_id,
        #     user=request.user
        # )
        
        # Initialize Google Ads API service
        api_service = GoogleAdsAPIService()
        if not api_service.initialize_client():
            return Response({
                'success': False,
                'error': 'Failed to initialize Google Ads API client'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Request access using CustomerClientLinkService
        result = api_service.request_account_access(
            manager_customer_id=manager_customer_id,
            client_customer_id=client_customer_id
        )
        
        if result.get('success'):
            return Response({
                'success': True,
                'message': 'Access request sent successfully',
                'resource_name': result.get('resource_name'),
                'manager_customer_id': manager_customer_id,
                'client_customer_id': client_customer_id
            })
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Failed to request access')
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except GoogleAdsAccount.DoesNotExist:
        return Response({
            'success': False,
            'error': f'Manager account with customer ID {manager_customer_id} not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in request account access view: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([])  # No permissions required
@csrf_exempt
def get_pending_access_requests_view(request):
    """Get pending access requests for manager accounts"""
    try:
        manager_customer_id = request.GET.get('manager_customer_id')
        
        if not manager_customer_id:
            return Response({
                'success': False,
                'error': 'manager_customer_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # For testing purposes, skip user validation
        # In production, you should validate user permissions here
        # manager_account = get_object_or_404(
        #     GoogleAdsAccount, 
        #     customer_id=manager_customer_id,
        #     user=request.user
        # )
        
        # Initialize Google Ads API service
        api_service = GoogleAdsAPIService()
        if not api_service.initialize_client():
            return Response({
                'success': False,
                'error': 'Failed to initialize Google Ads API client'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Get pending access requests
        result = api_service.get_pending_access_requests(manager_customer_id)
        
        if result.get('success'):
            return Response({
                'success': True,
                'pending_requests': result.get('pending_requests', []),
                'manager_customer_id': manager_customer_id
            })
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Failed to get pending access requests')
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except GoogleAdsAccount.DoesNotExist:
        return Response({
            'success': False,
            'error': f'Manager account with customer ID {manager_customer_id} not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in get pending access requests view: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@csrf_exempt
@permission_classes([])
def comprehensive_sync_view(request):
    """Trigger comprehensive Google Ads sync"""
    try:
        data = request.data
        manager_customer_id = data.get('manager_customer_id')
        days_back = data.get('days_back', 7)
        incremental = data.get('incremental', False)
        
        if not manager_customer_id:
            return Response({
                'success': False,
                'error': 'manager_customer_id is required'
            }, status=400)
        
        # Import the sync service
        from .comprehensive_sync_service import ComprehensiveGoogleAdsSyncService
        
        # Initialize and run sync
        sync_service = ComprehensiveGoogleAdsSyncService()
        
        if incremental:
            result = sync_service.incremental_daily_sync(manager_customer_id)
        else:
            result = sync_service.comprehensive_sync(manager_customer_id, days_back)
        
        if result['success']:
            return Response({
                'success': True,
                'message': 'Sync completed successfully',
                'summary': result['summary']
            })
        else:
            return Response({
                'success': False,
                'error': result['error']
            }, status=400)
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in sync_single_client_account: {e}")
        print(f"Traceback: {error_details}")
        return Response({
            'success': False,
            'error': str(e),
            'details': error_details
        }, status=500)


@api_view(['POST'])
@csrf_exempt
@permission_classes([])
def sync_single_client_account(request):
    """Sync a single client Google Ads account"""
    try:
        data = request.data
        client_customer_id = data.get('client_customer_id')
        days_back = data.get('days_back', 7)
        sync_types = data.get('sync_types', ['campaigns', 'ad_groups', 'keywords', 'performance'])
        
        if not client_customer_id:
            return Response({
                'success': False,
                'error': 'client_customer_id is required'
            }, status=400)
        
        # Validate sync types
        valid_sync_types = ['campaigns', 'ad_groups', 'keywords', 'performance']
        if not isinstance(sync_types, list):
            sync_types = [sync_types]
        
        invalid_types = [t for t in sync_types if t not in valid_sync_types]
        if invalid_types:
            return Response({
                'success': False,
                'error': f'Invalid sync types: {invalid_types}. Valid types: {valid_sync_types}'
            }, status=400)
        
        # Import the simple sync service for testing
        from .simple_sync_service import SimpleGoogleAdsSyncService
        
        # Initialize sync service
        sync_service = SimpleGoogleAdsSyncService()
        
        # Sync single client account
        print(f"Calling sync_single_client_account with: {client_customer_id}, {days_back}, {sync_types}")
        result = sync_service.sync_single_client_account(
            client_customer_id, 
            days_back=days_back,
            sync_types=sync_types
        )
        print(f"Sync result: {result}")
        
        if result['success']:
            return Response({
                'success': True,
                'message': 'Client account sync completed successfully',
                'summary': result['summary']
            })
        else:
            return Response({
                'success': False,
                'error': result['error']
            }, status=400)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@csrf_exempt
@permission_classes([])
def test_single_client_sync(request):
    """Test endpoint for debugging single client sync"""
    try:
        return Response({
            'success': True,
            'message': 'Test endpoint working',
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# Legacy function-based views for backward compatibility
@login_required
def sync_status_legacy_view(request):
    """Legacy sync status view"""
    return sync_status_view(request)


@login_required
def sync_data_legacy_view(request):
    """Legacy sync data view"""
    return sync_data_view(request)


@login_required
def get_synced_data_legacy_view(request):
    """Legacy get synced data view"""
    return get_synced_data_view(request)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def account_summary_view(request):
    """Get focused account summary with key metrics"""
    try:
        # Get user's accounts
        user_accounts = GoogleAdsAccount.objects.filter(user=request.user, is_active=True)
        
        if not user_accounts.exists():
            return Response({
                'success': True,
                'summary': {
                    'connected_accounts': 0,
                    'active_campaigns': 0,
                    'monthly_spend': 0,
                    'message': 'No Google Ads accounts connected'
                }
            })
        
        # Get last 30 days for monthly spend
        monthly_end_date = timezone.now().date()
        monthly_start_date = monthly_end_date - timedelta(days=30)
        
        # Count active campaigns
        active_campaigns = GoogleAdsCampaign.objects.filter(
            account__in=user_accounts,
            campaign_status='ENABLED'
        ).count()
        
        # Get monthly spend
        monthly_performance = GoogleAdsPerformance.objects.filter(
            account__in=user_accounts,
            date__range=[monthly_start_date, monthly_end_date]
        ).aggregate(
            total_cost=Sum('cost_micros')
        )
        
        monthly_spend = (monthly_performance['total_cost'] or 0) / 1000000  # Convert from micros to dollars
        
        summary = {
            'connected_accounts': user_accounts.count(),
            'active_campaigns': active_campaigns,
            'monthly_spend': round(monthly_spend, 2),
            'message': f'{user_accounts.count()} accounts connected • {active_campaigns} active campaigns • ${round(monthly_spend, 2):,.0f} monthly spend'
        }
        
        return Response({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        logger.error(f"Error in account summary view: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_accessible_customers_view(request):
    """Get list of accessible Google Ads customers for the authenticated user and save to database"""
    try:
        # Use the wrapper function to get accessible customers
        result = list_accessible_customers(user_id=request.user.id)
        
        if result['success']:
            # Save accessible customers to UserGoogleAuth table
            try:
                from accounts.models import UserGoogleAuth
                
                # Get the user's active Google Auth record
                user_auth = UserGoogleAuth.objects.filter(
                    user=request.user, 
                    is_active=True
                ).first()
                
                if user_auth:
                    # Update the accessible_customers field
                    user_auth.accessible_customers = {
                        'customers': result['customers'],
                        'total_count': result['total_count'],
                        'last_updated': timezone.now().isoformat(),
                        'raw_response': result['raw_response']
                    }
                    user_auth.save()
                    logger.info(f"Saved {result['total_count']} accessible customers for user {request.user.id}")
                else:
                    logger.warning(f"No active Google Auth record found for user {request.user.id}")
                    
            except Exception as save_error:
                logger.error(f"Error saving accessible customers to database: {save_error}")
                # Don't fail the API call if saving fails, just log the error
            
            return Response({
                'success': True,
                'customers': result['customers'],
                'total_count': result['total_count'],
                'raw_response': result['raw_response'],
                'message': f'Found {result["total_count"]} accessible customers',
                'saved_to_db': True
            })
        else:
            return Response({
                'success': False,
                'error': result['error']
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error in list_accessible_customers_view: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_saved_accessible_customers_view(request):
    """Get saved accessible customers from the database for the authenticated user"""
    try:
        from accounts.models import UserGoogleAuth
        
        # Get the user's active Google Auth record
        user_auth = UserGoogleAuth.objects.filter(
            user=request.user, 
            is_active=True
        ).first()
        
        if not user_auth:
            return Response({
                'success': False,
                'error': 'No active Google Auth record found. Please authenticate with Google first.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if not user_auth.accessible_customers:
            return Response({
                'success': False,
                'error': 'No accessible customers saved. Please call the list-accessible-customers endpoint first.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': True,
            'customers': user_auth.accessible_customers.get('customers', []),
            'total_count': user_auth.accessible_customers.get('total_count', 0),
            'last_updated': user_auth.accessible_customers.get('last_updated'),
            'raw_response': user_auth.accessible_customers.get('raw_response', {}),
            'message': f'Retrieved {user_auth.accessible_customers.get("total_count", 0)} saved accessible customers'
        })
        
    except Exception as e:
        logger.error(f"Error in get_saved_accessible_customers_view: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

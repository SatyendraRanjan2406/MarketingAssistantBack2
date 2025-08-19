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

from .models import (
    GoogleAdsAccount, GoogleAdsCampaign, GoogleAdsAdGroup,
    GoogleAdsKeyword, GoogleAdsPerformance, DataSyncLog
)
from .google_ads_api_service import GoogleAdsAPIService
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
            if not account:
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

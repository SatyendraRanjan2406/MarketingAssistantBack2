from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.db.models import Q, Sum, Avg, Count
from django.utils import timezone
from datetime import datetime, timedelta
import json
import logging

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import (
    GoogleAdsAccount, GoogleAdsCampaign, GoogleAdsAdGroup,
    GoogleAdsKeyword, GoogleAdsPerformance, GoogleAdsReport, GoogleAdsAlert
)
from .serializers import (
    GoogleAdsAccountSerializer, GoogleAdsCampaignSerializer,
    GoogleAdsAdGroupSerializer, GoogleAdsKeywordSerializer,
    GoogleAdsPerformanceSerializer, GoogleAdsReportSerializer,
    GoogleAdsAlertSerializer, DashboardMetricsSerializer,
    AccountSyncSerializer, CampaignCreateSerializer,
    KeywordCreateSerializer, PerformanceFilterSerializer
)
from .services import GoogleAdsService

logger = logging.getLogger(__name__)


@login_required
def dashboard_view(request):
    """Simple dashboard view that renders the HTML template"""
    return render(request, 'google_ads_app/dashboard.html')


class GoogleAdsAccountViewSet(viewsets.ModelViewSet):
    """ViewSet for Google Ads Account management"""
    serializer_class = GoogleAdsAccountSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return GoogleAdsAccount.objects.filter(user=self.request.user, is_active=True)
    
    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """Sync account data from Google Ads"""
        try:
            account = self.get_object()
            service = GoogleAdsService()
            
            result = service.sync_account_data(account.customer_id, request.user.id)
            
            if result['success']:
                return Response({
                    'success': True,
                    'message': result['message']
                })
            else:
                return Response({
                    'success': False,
                    'error': result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Account sync failed: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def campaigns(self, request, pk=None):
        """Get campaigns for an account"""
        try:
            account = self.get_object()
            campaigns = GoogleAdsCampaign.objects.filter(account=account)
            serializer = GoogleAdsCampaignSerializer(campaigns, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to get campaigns: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        """Get performance data for an account"""
        try:
            account = self.get_object()
            
            # Get date range from query params
            days = int(request.query_params.get('days', 30))
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days)
            
            performance_data = GoogleAdsPerformance.objects.filter(
                account=account,
                date__range=[start_date, end_date]
            ).order_by('-date')
            
            serializer = GoogleAdsPerformanceSerializer(performance_data, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to get performance data: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GoogleAdsCampaignViewSet(viewsets.ModelViewSet):
    """ViewSet for Google Ads Campaign management"""
    serializer_class = GoogleAdsCampaignSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user_accounts = GoogleAdsAccount.objects.filter(user=self.request.user, is_active=True)
        return GoogleAdsCampaign.objects.filter(account__in=user_accounts)
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Pause a campaign"""
        try:
            campaign = self.get_object()
            campaign.campaign_status = 'PAUSED'
            campaign.save()
            
            # Update in Google Ads
            service = GoogleAdsService()
            service.update_campaign_status(campaign.account.customer_id, campaign.campaign_id, 'PAUSED')
            
            return Response({'success': True, 'message': 'Campaign paused successfully'})
        except Exception as e:
            logger.error(f"Failed to pause campaign: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def enable(self, request, pk=None):
        """Enable a campaign"""
        try:
            campaign = self.get_object()
            campaign.campaign_status = 'ENABLED'
            campaign.save()
            
            # Update in Google Ads
            service = GoogleAdsService()
            service.update_campaign_status(campaign.account.customer_id, campaign.campaign_id, 'ENABLED')
            
            return Response({'success': True, 'message': 'Campaign enabled successfully'})
        except Exception as e:
            logger.error(f"Failed to enable campaign: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def ad_groups(self, request, pk=None):
        """Get ad groups for a campaign"""
        try:
            campaign = self.get_object()
            ad_groups = GoogleAdsAdGroup.objects.filter(campaign=campaign)
            serializer = GoogleAdsAdGroupSerializer(ad_groups, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to get ad groups: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        """Get performance data for a campaign"""
        try:
            campaign = self.get_object()
            
            # Get date range from query params
            days = int(request.query_params.get('days', 30))
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days)
            
            performance_data = GoogleAdsPerformance.objects.filter(
                campaign=campaign,
                date__range=[start_date, end_date]
            ).order_by('-date')
            
            serializer = GoogleAdsPerformanceSerializer(performance_data, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to get campaign performance: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GoogleAdsAdGroupViewSet(viewsets.ModelViewSet):
    """ViewSet for Google Ads Ad Group management"""
    serializer_class = GoogleAdsAdGroupSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user_accounts = GoogleAdsAccount.objects.filter(user=self.request.user, is_active=True)
        return GoogleAdsAdGroup.objects.filter(campaign__account__in=user_accounts)
    
    @action(detail=True, methods=['get'])
    def keywords(self, request, pk=None):
        """Get keywords for an ad group"""
        try:
            ad_group = self.get_object()
            keywords = GoogleAdsKeyword.objects.filter(ad_group=ad_group)
            serializer = GoogleAdsKeywordSerializer(keywords, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to get keywords: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        """Get performance data for an ad group"""
        try:
            ad_group = self.get_object()
            
            # Get date range from query params
            days = int(request.query_params.get('days', 30))
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days)
            
            performance_data = GoogleAdsPerformance.objects.filter(
                ad_group=ad_group,
                date__range=[start_date, end_date]
            ).order_by('-date')
            
            serializer = GoogleAdsPerformanceSerializer(performance_data, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to get ad group performance: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GoogleAdsKeywordViewSet(viewsets.ModelViewSet):
    """ViewSet for Google Ads Keyword management"""
    serializer_class = GoogleAdsKeywordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user_accounts = GoogleAdsAccount.objects.filter(user=self.request.user, is_active=True)
        return GoogleAdsKeyword.objects.filter(ad_group__campaign__account__in=user_accounts)
    
    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        """Get performance data for a keyword"""
        try:
            keyword = self.get_object()
            
            # Get date range from query params
            days = int(request.query_params.get('days', 30))
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days)
            
            performance_data = GoogleAdsPerformance.objects.filter(
                keyword=keyword,
                date__range=[start_date, end_date]
            ).order_by('-date')
            
            serializer = GoogleAdsPerformanceSerializer(performance_data, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to get keyword performance: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GoogleAdsPerformanceViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Google Ads Performance data"""
    serializer_class = GoogleAdsPerformanceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Apply filters
        account_id = self.request.query_params.get('account')
        campaign_id = self.request.query_params.get('campaign')
        ad_group_id = self.request.query_params.get('ad_group')
        keyword_id = self.request.query_params.get('keyword')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if account_id:
            queryset = queryset.filter(account_id=account_id)
        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)
        if ad_group_id:
            queryset = queryset.filter(ad_group_id=ad_group_id)
        if keyword_id:
            queryset = queryset.filter(keyword_id=keyword_id)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset.order_by('-date')
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get performance summary"""
        try:
            queryset = self.get_queryset()
            
            summary = queryset.aggregate(
                total_impressions=Sum('impressions'),
                total_clicks=Sum('clicks'),
                total_cost=Sum('cost_micros'),
                total_conversions=Sum('conversions'),
                total_conversion_value=Sum('conversion_value'),
                avg_ctr=Avg('ctr'),
                avg_cpc=Avg('cpc'),
                avg_roas=Avg('roas')
            )
            
            # Convert cost from micros
            if summary['total_cost']:
                summary['total_cost'] = summary['total_cost'] / 1000000
            
            return Response(summary)
        except Exception as e:
            logger.error(f"Failed to get performance summary: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GoogleAdsReportViewSet(viewsets.ModelViewSet):
    """ViewSet for Google Ads Report management"""
    serializer_class = GoogleAdsReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return GoogleAdsReport.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GoogleAdsAlertViewSet(viewsets.ModelViewSet):
    """ViewSet for Google Ads Alert management"""
    serializer_class = GoogleAdsAlertSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user_accounts = GoogleAdsAccount.objects.filter(user=self.request.user, is_active=True)
        return GoogleAdsAlert.objects.filter(account__in=user_accounts)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark an alert as read"""
        try:
            alert = self.get_object()
            alert.is_read = True
            alert.save()
            return Response({'success': True})
        except Exception as e:
            logger.error(f"Failed to mark alert as read: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve an alert"""
        try:
            alert = self.get_object()
            alert.is_resolved = True
            alert.resolved_at = timezone.now()
            alert.save()
            return Response({'success': True})
        except Exception as e:
            logger.error(f"Failed to resolve alert: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DashboardView(APIView):
    """Dashboard view for Google Ads metrics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get dashboard metrics"""
        try:
            days = int(request.query_params.get('days', 30))
            
            service = GoogleAdsService()
            metrics = service.get_dashboard_metrics(request.user.id, days)
            
            if 'error' in metrics:
                return Response({
                    'error': metrics['error']
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            serializer = DashboardMetricsSerializer(metrics)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Failed to get dashboard metrics: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AccountSyncView(APIView):
    """Account synchronization view"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Sync account data from Google Ads"""
        try:
            serializer = AccountSyncSerializer(data=request.data)
            if serializer.is_valid():
                customer_id = serializer.validated_data['customer_id']
                force_sync = serializer.validated_data.get('force_sync', False)
                
                service = GoogleAdsService()
                result = service.sync_account_data(customer_id, request.user.id)
                
                if result['success']:
                    return Response({
                        'success': True,
                        'message': result['message']
                    })
                else:
                    return Response({
                        'success': False,
                        'error': result['error']
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'success': False,
                    'error': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Account sync failed: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CampaignCreateView(APIView):
    """Campaign creation view"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Create a new campaign"""
        try:
            serializer = CampaignCreateSerializer(data=request.data)
            if serializer.is_valid():
                campaign_data = serializer.validated_data
                
                # Get the account
                account = GoogleAdsAccount.objects.get(
                    id=campaign_data['account'],
                    user=request.user,
                    is_active=True
                )
                
                service = GoogleAdsService()
                campaign_id = service.create_campaign(
                    account.customer_id,
                    campaign_data
                )
                
                if campaign_id:
                    return Response({
                        'success': True,
                        'campaign_id': campaign_id,
                        'message': 'Campaign created successfully'
                    })
                else:
                    return Response({
                        'success': False,
                        'error': 'Failed to create campaign'
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'success': False,
                    'error': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Campaign creation failed: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class KeywordCreateView(APIView):
    """Keyword creation view"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Create a new keyword"""
        try:
            serializer = KeywordCreateSerializer(data=request.data)
            if serializer.is_valid():
                keyword_data = serializer.validated_data
                
                # Get the ad group and verify ownership
                ad_group = GoogleAdsAdGroup.objects.get(
                    id=keyword_data['ad_group'],
                    campaign__account__user=request.user,
                    campaign__account__is_active=True
                )
                
                # Create keyword in database
                keyword = GoogleAdsKeyword.objects.create(
                    ad_group=ad_group,
                    keyword_text=keyword_data['keyword_text'],
                    match_type=keyword_data['match_type'],
                    status='ENABLED'
                )
                
                return Response({
                    'success': True,
                    'keyword_id': keyword.id,
                    'message': 'Keyword created successfully'
                })
            else:
                return Response({
                    'success': False,
                    'error': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Keyword creation failed: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PerformanceExportView(APIView):
    """Performance data export view"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Export performance data"""
        try:
            serializer = PerformanceFilterSerializer(data=request.query_params)
            if serializer.is_valid():
                filters = serializer.validated_data
                
                # Build queryset
                user_accounts = GoogleAdsAccount.objects.filter(
                    user=request.user, is_active=True
                )
                queryset = GoogleAdsPerformance.objects.filter(account__in=user_accounts)
                
                # Apply filters
                if filters.get('start_date'):
                    queryset = queryset.filter(date__gte=filters['start_date'])
                if filters.get('end_date'):
                    queryset = queryset.filter(date__lte=filters['end_date'])
                if filters.get('account'):
                    queryset = queryset.filter(account_id=filters['account'])
                if filters.get('campaign'):
                    queryset = queryset.filter(campaign_id=filters['campaign'])
                if filters.get('ad_group'):
                    queryset = queryset.filter(ad_group_id=filters['ad_group'])
                if filters.get('keyword'):
                    queryset = queryset.filter(keyword_id=filters['keyword'])
                
                # Get data
                performance_data = queryset.order_by('-date')
                serializer = GoogleAdsPerformanceSerializer(performance_data, many=True)
                
                return Response({
                    'success': True,
                    'data': serializer.data,
                    'total_records': len(serializer.data)
                })
            else:
                return Response({
                    'success': False,
                    'error': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Performance export failed: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

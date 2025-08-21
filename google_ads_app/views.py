from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.conf import settings
import json
import logging
import os
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Avg
from datetime import datetime, timedelta, timezone

from .models import (
    GoogleAdsAccount, GoogleAdsCampaign, GoogleAdsAdGroup,
    GoogleAdsKeyword, GoogleAdsPerformance, GoogleAdsReport, GoogleAdsAlert, DataSyncLog
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
from .chat_service import GoogleAdsChatService

logger = logging.getLogger(__name__)


@login_required
def dashboard_view(request):
    """Simple dashboard view that renders the HTML template"""
    try:
        # Get user's accounts
        user_accounts = GoogleAdsAccount.objects.filter(user=request.user, is_active=True)
        
        # Get sync status for each account
        sync_status = []
        for account in user_accounts:
            latest_sync = DataSyncLog.objects.filter(
                account=account
            ).order_by('-created_at').first()
            
            sync_status.append({
                'account_id': account.id,
                'account_name': account.account_name,
                'customer_id': account.customer_id,
                'sync_status': account.sync_status,
                'last_sync_at': account.last_sync_at.isoformat() if account.last_sync_at else None,
                'latest_sync_log': {
                    'id': latest_sync.id,
                    'sync_type': latest_sync.sync_type,
                    'status': latest_sync.status,
                    'created_at': latest_sync.created_at.isoformat(),
                    'summary': latest_sync.get_summary()
                } if latest_sync else None
            })
        
        context = {
            'accounts': user_accounts,
            'sync_status': sync_status,
            'has_openai_key': bool(getattr(settings, 'OPENAI_API_KEY', None))
        }
        
        return render(request, 'google_ads_app/dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error in dashboard: {e}")
        messages.error(request, f"Error loading dashboard: {str(e)}")
        return redirect('google-ads-dashboard-view')


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
            
            try:
                service = GoogleAdsService()
                metrics = service.get_dashboard_metrics(request.user.id, days)
                
                if 'error' in metrics:
                    return Response({
                        'error': metrics['error']
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                serializer = DashboardMetricsSerializer(metrics)
                return Response(serializer.data)
                
            except Exception as ads_error:
                logger.warning(f"Google Ads service failed: {ads_error}")
                # Return fallback data when Google Ads service is unavailable
                fallback_metrics = {
                    'total_accounts': 0,
                    'total_campaigns': 0,
                    'total_spend': 0,
                    'total_impressions': 0,
                    'total_clicks': 0,
                    'total_conversions': 0,
                    'total_conversion_value': 0,
                    'overall_ctr': 0,
                    'overall_cpc': 0,
                    'overall_roas': 0,
                    'performance_trend': [],
                    'top_campaigns': [],
                    'top_keywords': [],
                    'warning': 'Google Ads service temporarily unavailable. Please check your credentials.'
                }
                
                serializer = DashboardMetricsSerializer(fallback_metrics)
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
                
                try:
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
                        
                except Exception as ads_error:
                    logger.warning(f"Google Ads service failed during account sync: {ads_error}")
                    return Response({
                        'success': False,
                        'error': 'Google Ads service temporarily unavailable. Please check your credentials and try again.'
                    }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
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
                
                try:
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
                        
                except Exception as ads_error:
                    logger.warning(f"Google Ads service failed during campaign creation: {ads_error}")
                    return Response({
                        'success': False,
                        'error': 'Google Ads service temporarily unavailable. Please check your credentials and try again.'
                    }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
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


@login_required
def chat_dashboard(request):
    """Chat dashboard view"""
    try:
        # Get user's accounts for context
        accounts = GoogleAdsAccount.objects.filter(user_id=request.user.id, is_active=True)
        
        # Initialize chat service
        chat_service = GoogleAdsChatService(
            user_id=request.user.id,
            openai_api_key=os.getenv('OPENAI_API_KEY', None)
        )
        
        # Get quick insights
        insights = chat_service.get_quick_insights()
        
        context = {
            'accounts': accounts,
            'insights': insights,
            'has_openai_key': bool(getattr(settings, 'OPENAI_API_KEY', None))
        }
        
        return render(request, 'google_ads_app/chat_dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error in chat dashboard: {e}")
        messages.error(request, f"Error loading chat dashboard: {str(e)}")
        return redirect('google-ads-dashboard-view')


@require_http_methods(["POST"])
@login_required
def chat_api(request):
    """Chat API endpoint"""
    print(f"🔍 DEBUG: ===== CHAT API VIEW BREAKPOINT =====")
    print(f"🔍 DEBUG: Chat API called by user: {request.user.id}")
    print(f"🔍 DEBUG: Request method: {request.method}")
    print(f"🔍 DEBUG: Request headers: {dict(request.headers)}")
    
    try:
        print(f"🔍 DEBUG: ===== PARSING REQUEST BODY =====")
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        print(f"🔍 DEBUG: User message: {user_message}")
        print(f"🔍 DEBUG: Full request data: {data}")
        
        if not user_message:
            print(f"❌ DEBUG: No message provided")
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Initialize chat service
        print(f"🔍 DEBUG: ===== INITIALIZING CHAT SERVICE =====")
        print(f"🔍 DEBUG: Initializing GoogleAdsChatService...")
        openai_key = getattr(settings, 'OPENAI_API_KEY', None)
        print(f"🔍 DEBUG: OpenAI API key available: {bool(openai_key)}")
        print(f"🔍 DEBUG: OpenAI API key length: {len(openai_key) if openai_key else 0}")
        
        chat_service = GoogleAdsChatService(
            user_id=request.user.id,
            openai_api_key=openai_key
        )
        print(f"🔍 DEBUG: GoogleAdsChatService initialized")
        
        # Process chat message
        print(f"🔍 DEBUG: ===== PROCESSING CHAT MESSAGE =====")
        print(f"🔍 DEBUG: Processing chat message...")
        response = chat_service.chat(user_message)
        print(f"🔍 DEBUG: Chat response generated: {type(response)}")
        print(f"🔍 DEBUG: Response content: {response}")
        
        return JsonResponse(response)
        
    except json.JSONDecodeError:
        print(f"❌ DEBUG: ===== JSON DECODE ERROR =====")
        print(f"❌ DEBUG: JSON decode error in chat API")
        print(f"❌ DEBUG: Request body: {request.body}")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"❌ DEBUG: ===== EXCEPTION IN CHAT API =====")
        print(f"❌ DEBUG: Error in chat API: {e}")
        print(f"❌ DEBUG: Error type: {type(e)}")
        print(f"❌ DEBUG: Error details: {str(e)}")
        import traceback
        print(f"❌ DEBUG: Full traceback:")
        traceback.print_exc()
        logger.error(f"Error in chat API: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_quick_insights(request):
    """Get quick insights API endpoint"""
    try:
        chat_service = GoogleAdsChatService(
            user_id=request.user.id,
            openai_api_key=getattr(settings, 'OPENAI_API_KEY', None)
        )
        
        insights = chat_service.get_quick_insights()
        return JsonResponse(insights)
        
    except Exception as e:
        logger.error(f"Error getting quick insights: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def sync_status_view(request):
    """Get sync status for dashboard"""
    try:
        user_accounts = GoogleAdsAccount.objects.filter(user=request.user, is_active=True)
        
        sync_status = []
        for account in user_accounts:
            latest_sync = DataSyncLog.objects.filter(
                account=account
            ).order_by('-created_at').first()
            
            sync_status.append({
                'account_id': account.id,
                'account_name': account.account_name,
                'customer_id': account.customer_id,
                'sync_status': account.sync_status,
                'last_sync_at': account.last_sync_at.isoformat() if account.last_sync_at else None,
                'latest_sync_log': {
                    'id': latest_sync.id,
                    'sync_type': latest_sync.sync_type,
                    'status': latest_sync.status,
                    'created_at': latest_sync.created_at.isoformat(),
                    'summary': latest_sync.get_summary()
                } if latest_sync else None
            })
        
        return JsonResponse({
            'success': True,
            'sync_status': sync_status
        })
        
    except Exception as e:
        logger.error(f"Error getting sync status: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def sync_data_view(request):
    """Trigger data sync for user's accounts"""
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            sync_type = data.get('sync_type', 'daily')
            account_id = data.get('account_id')
            
            if sync_type == 'daily':
                # Trigger daily sync using simple mock service
                from .simple_mock_sync import SimpleMockGoogleAdsSyncService
                sync_service = SimpleMockGoogleAdsSyncService()
                if account_id:
                    result = sync_service.sync_last_week_data(account_id)
                else:
                    result = sync_service.sync_last_week_data()
                
                if result['success']:
                    return JsonResponse({
                        'success': True,
                        'message': 'Daily sync completed successfully',
                        'data': result
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': result.get('error', 'Sync failed')
                    }, status=400)
                
                return JsonResponse({
                    'success': True,
                    'message': 'Daily sync initiated',
                    'task_id': task.id
                })
            
            elif sync_type == 'historical':
                weeks = data.get('weeks', 10)
                if account_id:
                    from .simple_mock_sync import SimpleMockGoogleAdsSyncService
                    sync_service = SimpleMockGoogleAdsSyncService()
                    result = sync_service.sync_historical_weeks(account_id, weeks)
                    
                    if result['success']:
                        return JsonResponse({
                            'success': True,
                            'message': f'Historical sync completed for {weeks} weeks',
                            'data': result
                        })
                    else:
                        return JsonResponse({
                            'success': False,
                            'error': result.get('error', 'Historical sync failed')
                        }, status=400)
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'Account ID required for historical sync'
                    }, status=400)
            
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid sync type'
                }, status=400)
        
        return JsonResponse({
            'success': False,
            'error': 'Method not allowed'
        }, status=405)
        
    except Exception as e:
        logger.error(f"Error in sync data view: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def get_synced_data_view(request):
    """Get synced data for dashboard with pagination"""
    try:
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        account_id = request.GET.get('account_id')
        
        # Get user's accounts
        if account_id:
            accounts = GoogleAdsAccount.objects.filter(
                id=account_id, 
                user=request.user, 
                is_active=True
            )
        else:
            accounts = GoogleAdsAccount.objects.filter(user=request.user, is_active=True)
        
        if not accounts.exists():
            return JsonResponse({
                'success': True,
                'data': [],
                'has_more': False,
                'total': 0
            })
        
        # Get performance data for the last week
        from datetime import datetime, timedelta
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        
        # Get performance data with pagination
        performance_data = GoogleAdsPerformance.objects.filter(
            account__in=accounts,
            date__range=[start_date, end_date]
        ).select_related('account', 'campaign', 'ad_group', 'keyword')
        
        total_count = performance_data.count()
        
        # Paginate the data
        start_index = (page - 1) * per_page
        end_index = start_index + per_page
        
        paginated_data = performance_data[start_index:end_index]
        
        # Serialize the data
        data = []
        for perf in paginated_data:
            data.append({
                'id': perf.id,
                'date': perf.date.isoformat(),
                'account_name': perf.account.account_name,
                'campaign_name': perf.campaign.campaign_name if perf.campaign else 'N/A',
                'ad_group_name': perf.ad_group.ad_group_name if perf.ad_group else 'N/A',
                'keyword_text': perf.keyword.keyword_text if perf.keyword else 'N/A',
                'impressions': perf.impressions,
                'clicks': perf.clicks,
                'cost': perf.cost_micros / 1000000,  # Convert from micros
                'conversions': perf.conversions,
                'conversion_value': perf.conversion_value,
                'ctr': (perf.clicks / perf.impressions * 100) if perf.impressions > 0 else 0,
                'cpc': (perf.cost_micros / 1000000 / perf.clicks) if perf.clicks > 0 else 0,
            })
        
        has_more = end_index < total_count
        
        return JsonResponse({
            'success': True,
            'data': data,
            'has_more': has_more,
            'total': total_count,
            'page': page,
            'per_page': per_page,
            'date_range': f"{start_date} to {end_date}"
        })
        
    except Exception as e:
        logger.error(f"Error getting synced data: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def test_csrf(request):
    """Test view for CSRF token verification"""
    if request.method == 'POST':
        return JsonResponse({
            'success': True,
            'message': 'CSRF token verified successfully',
            'received_data': request.POST.get('test_data', 'No data')
        })
    
    return render(request, 'google_ads_app/test_csrf.html')

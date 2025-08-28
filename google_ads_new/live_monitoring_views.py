#!/usr/bin/env python3
"""
Live Monitoring API Views
Provides REST API endpoints for live monitoring data
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, BasePermission
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
import logging

from .models import GoogleAdsAccount
from .live_monitoring_service import LiveMonitoringService

logger = logging.getLogger(__name__)

class GoogleAdsAccountAccessPermission(BasePermission):
    """
    Custom permission to ensure users can only access their own Google Ads accounts
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to access Google Ads accounts"""
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission to access specific Google Ads account"""
        # For account-specific views, obj should be the GoogleAdsAccount
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False

class LiveMonitoringView(APIView):
    """Main live monitoring endpoint for all accounts"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get live monitoring data for all user accounts"""
        try:
            user = request.user
            
            # Get all user's Google Ads accounts - ONLY accounts owned by this user
            accounts = GoogleAdsAccount.objects.filter(
                user=user,
                is_active=True
            ).select_related('user')
            
            if not accounts.exists():
                return Response({
                    "status": "error",
                    "message": "No active Google Ads accounts found for your user account",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Log access for security monitoring
            logger.info(f"User {user.username} (ID: {user.id}) accessed live monitoring for {accounts.count()} accounts")
            
            # Get monitoring data for each account
            all_accounts_data = []
            for account in accounts:
                # Double-check ownership (defense in depth)
                if account.user != user:
                    logger.warning(f"Security warning: User {user.username} attempted to access account {account.id} owned by {account.user.username}")
                    continue
                
                monitoring_service = LiveMonitoringService(account.id)
                account_data = monitoring_service.get_live_monitoring_data()
                
                all_accounts_data.append({
                    "account_id": account.id,
                    "account_name": account.account_name,
                    "customer_id": account.customer_id,
                    "monitoring_data": account_data
                })
            
            # Aggregate data across all accounts
            aggregated_data = self._aggregate_accounts_data(all_accounts_data)
            
            return Response({
                "status": "success",
                "message": f"Live monitoring data retrieved successfully for {len(all_accounts_data)} accounts",
                "data": {
                    "accounts": all_accounts_data,
                    "aggregated": aggregated_data,
                    "total_accounts": len(all_accounts_data),
                    "user_info": {
                        "username": user.username,
                        "user_id": user.id,
                        "access_level": "owner"
                    }
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in live monitoring view for user {request.user.username}: {e}")
            return Response({
                "status": "error",
                "message": f"Failed to retrieve monitoring data: {str(e)}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _aggregate_accounts_data(self, accounts_data):
        """Aggregate monitoring data across all accounts"""
        try:
            aggregated = {
                "total_active_campaigns": 0,
                "total_spend_24h": 0,
                "total_impressions_24h": 0,
                "total_clicks_24h": 0,
                "total_conversions_24h": 0,
                "avg_roas": 0,
                "total_alerts": 0,
                "total_optimization_opportunities": 0
            }
            
            total_roas = 0
            accounts_with_roas = 0
            
            for account_data in accounts_data:
                monitoring_data = account_data.get("monitoring_data", {})
                
                # Quick stats aggregation
                quick_stats = monitoring_data.get("quick_stats", {})
                aggregated["total_active_campaigns"] += quick_stats.get("active_campaigns", 0)
                
                # Convert currency strings to numbers for aggregation
                spend_str = quick_stats.get("total_spend_24h", "$0")
                spend_value = float(spend_str.replace("$", "").replace(",", "")) if spend_str != "$0" else 0
                aggregated["total_spend_24h"] += spend_value
                
                impressions_str = quick_stats.get("impressions_24h", "0")
                aggregated["total_impressions_24h"] += int(impressions_str.replace(",", "")) if impressions_str != "0" else 0
                
                clicks_str = quick_stats.get("clicks_24h", "0")
                aggregated["total_clicks_24h"] += int(clicks_str.replace(",", "")) if clicks_str != "0" else 0
                
                conversions_str = quick_stats.get("conversions", "0")
                aggregated["total_conversions_24h"] += int(conversions_str.replace(",", "")) if conversions_str != "0" else 0
                
                # ROAS aggregation
                roas_str = quick_stats.get("avg_roas", "0x")
                roas_value = float(roas_str.replace("x", "")) if roas_str != "0x" else 0
                if roas_value > 0:
                    total_roas += roas_value
                    accounts_with_roas += 1
                
                # Alerts and optimization aggregation
                alerts = monitoring_data.get("monitoring", {}).get("alerts", [])
                aggregated["total_alerts"] += len(alerts)
                
                optimization = monitoring_data.get("monitoring", {}).get("optimization", [])
                aggregated["total_optimization_opportunities"] += len(optimization)
            
            # Calculate average ROAS
            if accounts_with_roas > 0:
                aggregated["avg_roas"] = round(total_roas / accounts_with_roas, 2)
            
            # Format aggregated values
            aggregated["total_spend_24h"] = f"${aggregated['total_spend_24h']:,.0f}"
            aggregated["total_impressions_24h"] = f"{aggregated['total_impressions_24h']:,}"
            aggregated["total_clicks_24h"] = f"{aggregated['total_clicks_24h']:,}"
            aggregated["total_conversions_24h"] = f"{aggregated['total_conversions_24h']:,}"
            aggregated["avg_roas"] = f"{aggregated['avg_roas']:.1f}x"
            
            return aggregated
            
        except Exception as e:
            logger.error(f"Error aggregating accounts data: {e}")
            return {}

class AccountLiveMonitoringView(APIView):
    """Live monitoring endpoint for a specific account"""
    
    permission_classes = [IsAuthenticated, GoogleAdsAccountAccessPermission]
    
    def get(self, request, account_id):
        """Get live monitoring data for a specific account"""
        try:
            user = request.user
            
            # Get the specific account and verify ownership
            try:
                account = GoogleAdsAccount.objects.get(
                    id=account_id,
                    is_active=True
                )
            except GoogleAdsAccount.DoesNotExist:
                return Response({
                    "status": "error",
                    "message": "Google Ads account not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            
            # CRITICAL: Verify user owns this account
            if account.user != user:
                logger.warning(f"Security violation: User {user.username} (ID: {user.id}) attempted to access account {account_id} owned by {account.user.username}")
                return Response({
                    "status": "error",
                    "message": "Access denied: You can only access your own Google Ads accounts",
                    "data": None
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Log successful access
            logger.info(f"User {user.username} (ID: {user.id}) accessed live monitoring for account {account.account_name} (ID: {account_id})")
            
            # Get monitoring data for this account
            monitoring_service = LiveMonitoringService(account.id)
            monitoring_data = monitoring_service.get_live_monitoring_data()
            
            return Response({
                "status": "success",
                "message": f"Live monitoring data retrieved for {account.account_name}",
                "data": {
                    "account": {
                        "id": account.id,
                        "name": account.account_name,
                        "customer_id": account.customer_id,
                        "currency_code": account.currency_code,
                        "time_zone": account.time_zone,
                        "last_sync_at": account.last_sync_at.isoformat() if account.last_sync_at else None,
                        "ownership_verified": True,
                        "access_level": "owner"
                    },
                    "monitoring": monitoring_data,
                    "user_info": {
                        "username": user.username,
                        "user_id": user.id,
                        "access_verified": True
                    }
                }
            }, status=status.HTTP_200_OK)
            
        except GoogleAdsAccount.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Account not found or access denied",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in account live monitoring view for user {request.user.username}, account {account_id}: {e}")
            return Response({
                "status": "error",
                "message": f"Failed to retrieve monitoring data: {str(e)}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LiveMonitoringInsightsView(APIView):
    """Get specific insights from live monitoring"""
    
    permission_classes = [IsAuthenticated, GoogleAdsAccountAccessPermission]
    
    def get(self, request, account_id):
        """Get specific insights for an account"""
        try:
            user = request.user
            
            # Get the specific account and verify ownership
            try:
                account = GoogleAdsAccount.objects.get(
                    id=account_id,
                    is_active=True
                )
            except GoogleAdsAccount.DoesNotExist:
                return Response({
                    "status": "error",
                    "message": "Google Ads account not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            
            # CRITICAL: Verify user owns this account
            if account.user != user:
                logger.warning(f"Security violation: User {user.username} attempted to access insights for account {account_id}")
                return Response({
                    "status": "error",
                    "message": "Access denied: You can only access your own Google Ads accounts",
                    "data": None
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Log successful access
            logger.info(f"User {user.username} accessed insights for account {account.account_name} (ID: {account_id})")
            
            # Get monitoring service
            monitoring_service = LiveMonitoringService(account.id)
            
            # Get specific insights
            insights_type = request.query_params.get('type', 'all')
            
            if insights_type == 'performance':
                insights = monitoring_service._get_performance_insights()
            elif insights_type == 'alerts':
                insights = monitoring_service._get_alerts()
            elif insights_type == 'optimization':
                insights = monitoring_service._get_optimization_insights()
            elif insights_type == 'trends':
                insights = monitoring_service._get_trend_analysis()
            else:
                # Get all insights
                insights = {
                    "performance": monitoring_service._get_performance_insights(),
                    "alerts": monitoring_service._get_alerts(),
                    "optimization": monitoring_service._get_optimization_insights(),
                    "trends": monitoring_service._get_trend_analysis()
                }
            
            return Response({
                "status": "success",
                "message": f"Insights retrieved for {account.account_name}",
                "data": {
                    "account": {
                        "id": account.id,
                        "name": account.account_name,
                        "ownership_verified": True
                    },
                    "insights_type": insights_type,
                    "insights": insights,
                    "user_info": {
                        "username": user.username,
                        "user_id": user.id,
                        "access_verified": True
                    }
                }
            }, status=status.HTTP_200_OK)
            
        except GoogleAdsAccount.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Account not found or access denied",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in insights view for user {request.user.username}, account {account_id}: {e}")
            return Response({
                "status": "error",
                "message": f"Failed to retrieve insights: {str(e)}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LiveMonitoringQuickStatsView(APIView):
    """Get quick stats for live monitoring"""
    
    permission_classes = [IsAuthenticated, GoogleAdsAccountAccessPermission]
    
    def get(self, request, account_id):
        """Get quick stats for an account"""
        try:
            user = request.user
            
            # Get the specific account and verify ownership
            try:
                account = GoogleAdsAccount.objects.get(
                    id=account_id,
                    is_active=True
                )
            except GoogleAdsAccount.DoesNotExist:
                return Response({
                    "status": "error",
                    "message": "Google Ads account not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            
            # CRITICAL: Verify user owns this account
            if account.user != user:
                logger.warning(f"Security violation: User {user.username} attempted to access quick stats for account {account_id}")
                return Response({
                    "status": "error",
                    "message": "Access denied: You can only access your own Google Ads accounts",
                    "data": None
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Log successful access
            logger.info(f"User {user.username} accessed quick stats for account {account.account_name} (ID: {account_id})")
            
            # Get monitoring service
            monitoring_service = LiveMonitoringService(account.id)
            
            # Get quick stats
            quick_stats = monitoring_service._get_quick_stats()
            campaign_overview = monitoring_service._get_campaign_overview()
            
            return Response({
                "status": "success",
                "message": f"Quick stats retrieved for {account.account_name}",
                "data": {
                    "account": {
                        "id": account.id,
                        "name": account.account_name,
                        "ownership_verified": True
                    },
                    "quick_stats": quick_stats,
                    "campaign_overview": campaign_overview,
                    "user_info": {
                        "username": user.username,
                        "user_id": user.id,
                        "access_verified": True
                    }
                }
            }, status=status.HTTP_200_OK)
            
        except GoogleAdsAccount.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Account not found or access denied",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in quick stats view for user {request.user.username}, account {account_id}: {e}")
            return Response({
                "status": "error",
                "message": f"Failed to retrieve quick stats: {str(e)}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LiveMonitoringPerformanceView(APIView):
    """Get detailed performance metrics"""
    
    permission_classes = [IsAuthenticated, GoogleAdsAccountAccessPermission]
    
    def get(self, request, account_id):
        """Get detailed performance metrics for an account"""
        try:
            user = request.user
            
            # Get the specific account and verify ownership
            try:
                account = GoogleAdsAccount.objects.get(
                    id=account_id,
                    is_active=True
                )
            except GoogleAdsAccount.DoesNotExist:
                return Response({
                    "status": "error",
                    "message": "Google Ads account not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            
            # CRITICAL: Verify user owns this account
            if account.user != user:
                logger.warning(f"Security violation: User {user.username} attempted to access performance metrics for account {account_id}")
                return Response({
                    "status": "error",
                    "message": "Access denied: You can only access your own Google Ads accounts",
                    "data": None
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Log successful access
            logger.info(f"User {user.username} accessed performance metrics for account {account.account_name} (ID: {account_id})")
            
            # Get monitoring service
            monitoring_service = LiveMonitoringService(account.id)
            
            # Get performance metrics
            performance_metrics = monitoring_service._get_performance_metrics()
            budget_insights = monitoring_service._get_budget_insights()
            conversion_insights = monitoring_service._get_conversion_insights()
            
            return Response({
                "status": "success",
                "message": f"Performance metrics retrieved for {account.account_name}",
                "data": {
                    "account": {
                        "id": account.id,
                        "name": account.account_name,
                        "ownership_verified": True
                    },
                    "performance_metrics": performance_metrics,
                    "budget_insights": budget_insights,
                    "conversion_insights": conversion_insights,
                    "user_info": {
                        "username": user.username,
                        "user_id": user.id,
                        "access_verified": True
                    }
                }
            }, status=status.HTTP_200_OK)
            
        except GoogleAdsAccount.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Account not found or access denied",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in performance view for user {request.user.username}, account {account_id}: {e}")
            return Response({
                "status": "error",
                "message": f"Failed to retrieve performance metrics: {str(e)}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

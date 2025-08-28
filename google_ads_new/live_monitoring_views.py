#!/usr/bin/env python3
"""
Live Monitoring API Views
Provides REST API endpoints for live monitoring data
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
import logging

from .models import GoogleAdsAccount
from .live_monitoring_service import LiveMonitoringService

logger = logging.getLogger(__name__)

class LiveMonitoringView(APIView):
    """Main live monitoring endpoint for all accounts"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get live monitoring data for all user accounts"""
        try:
            user = request.user
            
            # Get all user's Google Ads accounts
            accounts = GoogleAdsAccount.objects.filter(
                user=user,
                is_active=True
            )
            
            if not accounts.exists():
                return Response({
                    "status": "error",
                    "message": "No active Google Ads accounts found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Get monitoring data for each account
            all_accounts_data = []
            for account in accounts:
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
                "message": "Live monitoring data retrieved successfully",
                "data": {
                    "accounts": all_accounts_data,
                    "aggregated": aggregated_data,
                    "total_accounts": len(all_accounts_data)
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in live monitoring view: {e}")
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
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, account_id):
        """Get live monitoring data for a specific account"""
        try:
            user = request.user
            
            # Get the specific account
            account = get_object_or_404(
                GoogleAdsAccount,
                id=account_id,
                user=user,
                is_active=True
            )
            
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
                        "last_sync_at": account.last_sync_at.isoformat() if account.last_sync_at else None
                    },
                    "monitoring": monitoring_data
                }
            }, status=status.HTTP_200_OK)
            
        except GoogleAdsAccount.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Account not found or access denied",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in account live monitoring view: {e}")
            return Response({
                "status": "error",
                "message": f"Failed to retrieve monitoring data: {str(e)}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LiveMonitoringInsightsView(APIView):
    """Get specific insights from live monitoring"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, account_id):
        """Get specific insights for an account"""
        try:
            user = request.user
            
            # Get the specific account
            account = get_object_or_404(
                GoogleAdsAccount,
                id=account_id,
                user=user,
                is_active=True
            )
            
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
                        "name": account.account_name
                    },
                    "insights_type": insights_type,
                    "insights": insights
                }
            }, status=status.HTTP_200_OK)
            
        except GoogleAdsAccount.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Account not found or access denied",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in insights view: {e}")
            return Response({
                "status": "error",
                "message": f"Failed to retrieve insights: {str(e)}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LiveMonitoringQuickStatsView(APIView):
    """Get quick stats for live monitoring"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, account_id):
        """Get quick stats for an account"""
        try:
            user = request.user
            
            # Get the specific account
            account = get_object_or_404(
                GoogleAdsAccount,
                id=account_id,
                user=user,
                is_active=True
            )
            
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
                        "name": account.account_name
                    },
                    "quick_stats": quick_stats,
                    "campaign_overview": campaign_overview
                }
            }, status=status.HTTP_200_OK)
            
        except GoogleAdsAccount.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Account not found or access denied",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in quick stats view: {e}")
            return Response({
                "status": "error",
                "message": f"Failed to retrieve quick stats: {str(e)}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LiveMonitoringPerformanceView(APIView):
    """Get detailed performance metrics"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, account_id):
        """Get detailed performance metrics for an account"""
        try:
            user = request.user
            
            # Get the specific account
            account = get_object_or_404(
                GoogleAdsAccount,
                id=account_id,
                user=user,
                is_active=True
            )
            
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
                        "name": account.account_name
                    },
                    "performance_metrics": performance_metrics,
                    "budget_insights": budget_insights,
                    "conversion_insights": conversion_insights
                }
            }, status=status.HTTP_200_OK)
            
        except GoogleAdsAccount.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Account not found or access denied",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in performance view: {e}")
            return Response({
                "status": "error",
                "message": f"Failed to retrieve performance metrics: {str(e)}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

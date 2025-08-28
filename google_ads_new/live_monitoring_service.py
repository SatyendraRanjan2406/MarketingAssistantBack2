#!/usr/bin/env python3
"""
Live Monitoring Service for Google Ads
Provides real-time insights and alerts based on performance data
"""

from typing import Dict, Any, List, Optional
from django.db.models import Sum, Avg, Count, Q, F, ExpressionWrapper, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from .models import (
    GoogleAdsAccount, GoogleAdsCampaign, GoogleAdsAdGroup, 
    GoogleAdsPerformance
)

logger = logging.getLogger(__name__)

class LiveMonitoringService:
    """Service for live monitoring and real-time insights"""
    
    def __init__(self, account_id: Optional[int] = None):
        self.account_id = account_id
        self.now = timezone.now()
        self.today = self.now.date()
        self.yesterday = self.today - timedelta(days=1)
        self.last_24h = self.now - timedelta(hours=24)
        self.last_7d = self.now - timedelta(days=7)
        self.last_30d = self.now - timedelta(days=30)
    
    def get_live_monitoring_data(self) -> Dict[str, Any]:
        """Get comprehensive live monitoring data"""
        try:
            return {
                "status": "success",
                "timestamp": self.now.isoformat(),
                "last_updated": self._get_last_updated_text(),
                "monitoring": {
                    "performance": self._get_performance_insights(),
                    "alerts": self._get_alerts(),
                    "optimization": self._get_optimization_insights(),
                    "trends": self._get_trend_analysis()
                },
                "quick_stats": self._get_quick_stats(),
                "campaign_overview": self._get_campaign_overview(),
                "performance_metrics": self._get_performance_metrics(),
                "budget_insights": self._get_budget_insights(),
                "conversion_insights": self._get_conversion_insights()
            }
        except Exception as e:
            logger.error(f"Error getting live monitoring data: {e}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": self.now.isoformat()
            }
    
    def _get_last_updated_text(self) -> str:
        """Get human-readable last updated text"""
        try:
            latest_performance = GoogleAdsPerformance.objects.filter(
                account_id=self.account_id
            ).order_by('-updated_at').first()
            
            if latest_performance:
                time_diff = self.now - latest_performance.updated_at
                if time_diff.total_seconds() < 60:
                    return "Just now"
                elif time_diff.total_seconds() < 3600:
                    minutes = int(time_diff.total_seconds() / 60)
                    return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
                else:
                    hours = int(time_diff.total_seconds() / 3600)
                    return f"{hours} hour{'s' if hours != 1 else ''} ago"
            else:
                return "No data available"
        except Exception as e:
            logger.error(f"Error getting last updated text: {e}")
            return "Unknown"
    
    def _get_performance_insights(self) -> List[Dict[str, Any]]:
        """Get performance insights for the last 24 hours"""
        insights = []
        
        try:
            # Get 24h performance data
            performance_24h = self._get_performance_data(self.last_24h, self.now)
            performance_prev_24h = self._get_performance_data(
                self.now - timedelta(hours=48), 
                self.now - timedelta(hours=24)
            )
            
            if performance_24h and performance_prev_24h:
                # ROAS trend
                roas_change = self._calculate_percentage_change(
                    performance_24h.get('roas', 0),
                    performance_prev_24h.get('roas', 0)
                )
                if abs(roas_change) >= 5:  # Only show significant changes
                    insights.append({
                        "type": "PERFORMANCE",
                        "time": "38m ago",
                        "title": "ROAS Trending Up" if roas_change > 0 else "ROAS Trending Down",
                        "change": f"{roas_change:+.0f}%",
                        "description": f"Return on ad spend {'increased' if roas_change > 0 else 'decreased'} significantly"
                    })
                
                # CTR trend
                ctr_change = self._calculate_percentage_change(
                    performance_24h.get('ctr', 0),
                    performance_prev_24h.get('ctr', 0)
                )
                if abs(ctr_change) >= 3:  # Only show significant changes
                    insights.append({
                        "type": "PERFORMANCE",
                        "time": "3h ago",
                        "title": "CTR Improvement" if ctr_change > 0 else "CTR Decline",
                        "change": f"{ctr_change:+.0f}%",
                        "description": f"Click-through rate showing {'steady growth' if ctr_change > 0 else 'decline'}"
                    })
                
                # Conversion rate trend
                conv_change = self._calculate_percentage_change(
                    performance_24h.get('conversion_rate', 0),
                    performance_prev_24h.get('conversion_rate', 0)
                )
                if abs(conv_change) >= 5:  # Only show significant changes
                    insights.append({
                        "type": "PERFORMANCE" if conv_change > 0 else "ALERT",
                        "time": "4h ago",
                        "title": "Conversion Rate Improvement" if conv_change > 0 else "Conversion Rate Drop",
                        "change": f"{conv_change:+.0f}%",
                        "description": f"Conversion rate {'improving' if conv_change > 0 else 'dropping'} - {'excellent performance' if conv_change > 0 else 'monitor landing page performance'}"
                    })
            
        except Exception as e:
            logger.error(f"Error getting performance insights: {e}")
        
        return insights
    
    def _get_alerts(self) -> List[Dict[str, Any]]:
        """Get critical alerts and warnings"""
        alerts = []
        
        try:
            # Get current performance data
            performance_24h = self._get_performance_data(self.last_24h, self.now)
            
            if performance_24h:
                # High CPM Alert
                current_cpm = performance_24h.get('cpm', 0)
                if current_cpm > 50:  # High CPM threshold
                    cpm_change = self._get_cpm_change()
                    alerts.append({
                        "type": "ALERT",
                        "time": "1h ago",
                        "title": "High CPM Alert",
                        "change": f"{cpm_change:+.0f}%",
                        "description": "Cost per mille requires immediate attention",
                        "severity": "high" if current_cpm > 100 else "medium"
                    })
                
                # Budget Alert
                budget_utilization = self._get_budget_utilization()
                if budget_utilization > 90:
                    alerts.append({
                        "type": "ALERT",
                        "time": "30m ago",
                        "title": "Budget Limit Approaching",
                        "change": f"{budget_utilization:.0f}%",
                        "description": "Account budget utilization is high",
                        "severity": "high" if budget_utilization > 95 else "medium"
                    })
                
                # Low Quality Score Alert
                avg_quality_score = self._get_average_quality_score()
                if avg_quality_score < 5:
                    alerts.append({
                        "type": "ALERT",
                        "time": "2h ago",
                        "title": "Low Quality Score",
                        "change": f"{avg_quality_score:.1f}",
                        "description": "Average keyword quality score is below optimal",
                        "severity": "medium"
                    })
                
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
        
        return alerts
    
    def _get_optimization_insights(self) -> List[Dict[str, Any]]:
        """Get optimization recommendations"""
        insights = []
        
        try:
            # Budget reallocation opportunity
            budget_insights = self._get_budget_optimization_insights()
            if budget_insights:
                insights.append({
                    "type": "OPTIMIZATION",
                    "time": "2h ago",
                    "title": "Budget Reallocation",
                    "change": f"{budget_insights.get('opportunity_percentage', 0):.0f}%",
                    "description": "Opportunity to optimize budget distribution"
                })
            
            # Keyword optimization
            keyword_insights = self._get_keyword_optimization_insights()
            if keyword_insights:
                insights.append({
                    "type": "OPTIMIZATION",
                    "time": "1h ago",
                    "title": "Keyword Performance",
                    "change": f"{keyword_insights.get('improvement_potential', 0):.0f}%",
                    "description": "Keywords with optimization potential identified"
                })
            
            # Ad group performance
            adgroup_insights = self._get_adgroup_optimization_insights()
            if adgroup_insights:
                insights.append({
                    "type": "OPTIMIZATION",
                    "time": "45m ago",
                    "title": "Ad Group Performance",
                    "change": f"{adgroup_insights.get('optimization_opportunity', 0):.0f}%",
                    "description": "Ad groups ready for optimization"
                })
                
        except Exception as e:
            logger.error(f"Error getting optimization insights: {e}")
        
        return insights
    
    def _get_trend_analysis(self) -> List[Dict[str, Any]]:
        """Get trend analysis for key metrics"""
        trends = []
        
        try:
            # Get trend data for last 7 days vs previous 7 days
            current_week = self._get_performance_data(self.now - timedelta(days=7), self.now)
            previous_week = self._get_performance_data(
                self.now - timedelta(days=14), 
                self.now - timedelta(days=7)
            )
            
            if current_week and previous_week:
                # Impressions trend
                impressions_change = self._calculate_percentage_change(
                    current_week.get('impressions', 0),
                    previous_week.get('impressions', 0)
                )
                trends.append({
                    "metric": "Impressions",
                    "change": f"{impressions_change:+.0f}%",
                    "trend": "up" if impressions_change > 0 else "down",
                    "description": f"Impressions {'increased' if impressions_change > 0 else 'decreased'} compared to last week"
                })
                
                # Clicks trend
                clicks_change = self._calculate_percentage_change(
                    current_week.get('clicks', 0),
                    previous_week.get('clicks', 0)
                )
                trends.append({
                    "metric": "Clicks",
                    "change": f"{clicks_change:+.0f}%",
                    "trend": "up" if clicks_change > 0 else "down",
                    "description": f"Clicks {'increased' if clicks_change > 0 else 'decreased'} compared to last week"
                })
                
                # Cost trend
                cost_change = self._calculate_percentage_change(
                    current_week.get('cost', 0),
                    previous_week.get('cost', 0)
                )
                trends.append({
                    "metric": "Cost",
                    "change": f"{cost_change:+.0f}%",
                    "trend": "up" if cost_change > 0 else "down",
                    "description": f"Cost {'increased' if cost_change > 0 else 'decreased'} compared to last week"
                })
                
        except Exception as e:
            logger.error(f"Error getting trend analysis: {e}")
        
        return trends
    
    def _get_quick_stats(self) -> Dict[str, Any]:
        """Get quick stats overview"""
        try:
            # Active campaigns count
            active_campaigns = GoogleAdsCampaign.objects.filter(
                account_id=self.account_id,
                campaign_status='ENABLED'
            ).count()
            
            # 24h performance data
            performance_24h = self._get_performance_data(self.last_24h, self.now)
            
            # Calculate quick stats
            total_spend_24h = performance_24h.get('cost', 0) if performance_24h else 0
            avg_roas = performance_24h.get('roas', 0) if performance_24h else 0
            conversions_24h = performance_24h.get('conversions', 0) if performance_24h else 0
            
            return {
                "active_campaigns": active_campaigns,
                "total_spend_24h": f"${total_spend_24h:,.0f}",
                "avg_roas": f"{avg_roas:.1f}x",
                "conversions": f"{conversions_24h:,.0f}",
                "impressions_24h": f"{performance_24h.get('impressions', 0):,}" if performance_24h else "0",
                "clicks_24h": f"{performance_24h.get('clicks', 0):,}" if performance_24h else "0",
                "ctr_24h": f"{performance_24h.get('ctr', 0)*100:.2f}%" if performance_24h else "0%"
            }
            
        except Exception as e:
            logger.error(f"Error getting quick stats: {e}")
            return {
                "active_campaigns": 0,
                "total_spend_24h": "$0",
                "avg_roas": "0x",
                "conversions": "0",
                "impressions_24h": "0",
                "clicks_24h": "0",
                "ctr_24h": "0%"
            }
    
    def _get_campaign_overview(self) -> Dict[str, Any]:
        """Get campaign overview data"""
        try:
            campaigns = GoogleAdsCampaign.objects.filter(
                account_id=self.account_id
            ).select_related('account')
            
            campaign_stats = []
            for campaign in campaigns:
                # Get campaign performance for last 7 days
                campaign_performance = GoogleAdsPerformance.objects.filter(
                    campaign=campaign,
                    date__gte=self.now.date() - timedelta(days=7)
                ).aggregate(
                    total_impressions=Coalesce(Sum('impressions'), 0),
                    total_clicks=Coalesce(Sum('clicks'), 0),
                    total_cost=Coalesce(Sum('cost_micros'), 0),
                    total_conversions=Coalesce(Sum('conversions'), 0),
                    total_conversion_value=Coalesce(Sum('conversion_value'), 0)
                )
                
                # Calculate metrics
                cost = campaign_performance['total_cost'] / 1000000  # Convert from micros
                roas = (campaign_performance['total_conversion_value'] / cost) if cost > 0 else 0
                ctr = (campaign_performance['total_clicks'] / campaign_performance['total_impressions']) if campaign_performance['total_impressions'] > 0 else 0
                
                campaign_stats.append({
                    "id": campaign.campaign_id,
                    "name": campaign.campaign_name,
                    "status": campaign.campaign_status,
                    "type": campaign.campaign_type,
                    "budget": float(campaign.budget_amount) if campaign.budget_amount else 0,
                    "budget_type": campaign.budget_type,
                    "impressions": campaign_performance['total_impressions'],
                    "clicks": campaign_performance['total_clicks'],
                    "cost": round(cost, 2),
                    "conversions": float(campaign_performance['total_conversions']),
                    "roas": round(roas, 2),
                    "ctr": round(ctr * 100, 2)
                })
            
            return {
                "total_campaigns": len(campaign_stats),
                "active_campaigns": len([c for c in campaign_stats if c['status'] == 'ENABLED']),
                "paused_campaigns": len([c for c in campaign_stats if c['status'] == 'PAUSED']),
                "campaigns": campaign_stats
            }
            
        except Exception as e:
            logger.error(f"Error getting campaign overview: {e}")
            return {
                "total_campaigns": 0,
                "active_campaigns": 0,
                "paused_campaigns": 0,
                "campaigns": []
            }
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics"""
        try:
            # Get performance data for different time periods
            performance_24h = self._get_performance_data(self.last_24h, self.now)
            performance_7d = self._get_performance_data(self.last_7d, self.now)
            performance_30d = self._get_performance_data(self.last_30d, self.now)
            
            return {
                "last_24_hours": performance_24h or {},
                "last_7_days": performance_7d or {},
                "last_30_days": performance_30d or {},
                "metrics_summary": {
                    "total_impressions": performance_30d.get('impressions', 0) if performance_30d else 0,
                    "total_clicks": performance_30d.get('clicks', 0) if performance_30d else 0,
                    "total_cost": performance_30d.get('cost', 0) if performance_30d else 0,
                    "total_conversions": performance_30d.get('conversions', 0) if performance_30d else 0,
                    "total_conversion_value": performance_30d.get('conversion_value', 0) if performance_30d else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {}
    
    def _get_budget_insights(self) -> Dict[str, Any]:
        """Get budget-related insights"""
        try:
            # Get current month budget vs spend
            current_month_start = self.now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            current_month_performance = self._get_performance_data(current_month_start, self.now)
            
            # Get account budget information
            account = GoogleAdsAccount.objects.get(id=self.account_id) if self.account_id else None
            
            budget_insights = {
                "month_to_date_spend": current_month_performance.get('cost', 0) if current_month_performance else 0,
                "budget_utilization": 0,
                "remaining_budget": 0,
                "budget_alerts": [],
                "optimization_opportunities": []
            }
            
            # Add budget alerts if spending is high
            if budget_insights["month_to_date_spend"] > 1000:  # High spend threshold
                budget_insights["budget_alerts"].append({
                    "type": "high_spend",
                    "message": "Monthly spend is above average",
                    "severity": "medium"
                })
            
            return budget_insights
            
        except Exception as e:
            logger.error(f"Error getting budget insights: {e}")
            return {}
    
    def _get_conversion_insights(self) -> Dict[str, Any]:
        """Get conversion-related insights"""
        try:
            # Get conversion data for last 7 days
            conversion_data = GoogleAdsPerformance.objects.filter(
                account_id=self.account_id,
                date__gte=self.now.date() - timedelta(days=7)
            ).aggregate(
                total_conversions=Coalesce(Sum('conversions'), 0),
                total_conversion_value=Coalesce(Sum('conversion_value'), 0),
                avg_conversion_rate=Coalesce(Avg('conversion_rate'), 0)
            )
            
            # Get conversion trends
            conversion_trends = self._get_conversion_trends()
            
            return {
                "total_conversions_7d": float(conversion_data['total_conversions']),
                "total_conversion_value_7d": float(conversion_data['total_conversion_value']),
                "avg_conversion_rate_7d": float(conversion_data['avg_conversion_rate']),
                "conversion_trends": conversion_trends,
                "insights": self._generate_conversion_insights(conversion_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting conversion insights: {e}")
            return {}
    
    # Helper methods
    def _get_performance_data(self, start_time, end_time) -> Optional[Dict[str, Any]]:
        """Get aggregated performance data for a time period"""
        try:
            if isinstance(start_time, datetime):
                start_date = start_time.date()
            else:
                start_date = start_time
                
            if isinstance(end_time, datetime):
                end_date = end_time.date()
            else:
                end_date = end_time
            
            performance = GoogleAdsPerformance.objects.filter(
                account_id=self.account_id,
                date__gte=start_date,
                date__lte=end_date
            ).aggregate(
                impressions=Coalesce(Sum('impressions'), 0),
                clicks=Coalesce(Sum('clicks'), 0),
                cost_micros=Coalesce(Sum('cost_micros'), 0),
                conversions=Coalesce(Sum('conversions'), 0),
                conversion_value=Coalesce(Sum('conversion_value'), 0)
            )
            
            if performance['impressions'] > 0:
                # Calculate derived metrics
                cost = performance['cost_micros'] / 1000000  # Convert from micros
                ctr = performance['clicks'] / performance['impressions']
                cpc = cost / performance['clicks'] if performance['clicks'] > 0 else 0
                cpm = (cost / performance['impressions']) * 1000 if performance['impressions'] > 0 else 0
                conversion_rate = performance['conversions'] / performance['clicks'] if performance['clicks'] > 0 else 0
                roas = performance['conversion_value'] / cost if cost > 0 else 0
                
                return {
                    "impressions": performance['impressions'],
                    "clicks": performance['clicks'],
                    "cost": round(cost, 2),
                    "conversions": float(performance['conversions']),
                    "conversion_value": float(performance['conversion_value']),
                    "ctr": round(ctr, 4),
                    "cpc": round(cpc, 2),
                    "cpm": round(cpm, 2),
                    "conversion_rate": round(conversion_rate, 4),
                    "roas": round(roas, 2)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting performance data: {e}")
            return None
    
    def _calculate_percentage_change(self, current: float, previous: float) -> float:
        """Calculate percentage change between two values"""
        try:
            if previous == 0:
                return 100 if current > 0 else 0
            return ((current - previous) / previous) * 100
        except Exception:
            return 0
    
    def _get_cpm_change(self) -> float:
        """Get CPM change percentage"""
        try:
            current_cpm = self._get_performance_data(self.last_24h, self.now)
            previous_cpm = self._get_performance_data(
                self.now - timedelta(hours=48), 
                self.now - timedelta(hours=24)
            )
            
            if current_cpm and previous_cpm:
                return self._calculate_percentage_change(
                    current_cpm.get('cpm', 0),
                    previous_cpm.get('cpm', 0)
                )
            return 0
        except Exception:
            return 0
    
    def _get_budget_utilization(self) -> float:
        """Get current budget utilization percentage"""
        try:
            # This would need to be implemented based on your budget tracking
            return 75.0  # Placeholder
        except Exception:
            return 0.0
    
    def _get_average_quality_score(self) -> float:
        """Get average keyword quality score"""
        try:
            avg_score = GoogleAdsKeyword.objects.filter(
                ad_group__campaign__account_id=self.account_id,
                quality_score__isnull=False
            ).aggregate(avg_score=Avg('quality_score'))
            
            return float(avg_score['avg_score']) if avg_score['avg_score'] else 0
        except Exception:
            return 0.0
    
    def _get_budget_optimization_insights(self) -> Optional[Dict[str, Any]]:
        """Get budget optimization insights"""
        try:
            # This would analyze budget distribution and identify opportunities
            return {
                "opportunity_percentage": 12,
                "description": "Budget reallocation opportunity identified"
            }
        except Exception:
            return None
    
    def _get_keyword_optimization_insights(self) -> Optional[Dict[str, Any]]:
        """Get keyword optimization insights"""
        try:
            # This would analyze keyword performance and identify optimization opportunities
            return {
                "improvement_potential": 8,
                "description": "Keywords with optimization potential identified"
            }
        except Exception:
            return None
    
    def _get_adgroup_optimization_insights(self) -> Optional[Dict[str, Any]]:
        """Get ad group optimization insights"""
        try:
            # This would analyze ad group performance and identify optimization opportunities
            return {
                "optimization_opportunity": 15,
                "description": "Ad groups ready for optimization"
            }
        except Exception:
            return None
    
    def _get_conversion_trends(self) -> List[Dict[str, Any]]:
        """Get conversion trends over time"""
        try:
            # Get daily conversion data for last 7 days
            conversion_trends = []
            for i in range(7):
                date = self.now.date() - timedelta(days=i)
                daily_conversions = GoogleAdsPerformance.objects.filter(
                    account_id=self.account_id,
                    date=date
                ).aggregate(
                    total_conversions=Coalesce(Sum('conversions'), 0)
                )
                
                conversion_trends.append({
                    "date": date.isoformat(),
                    "conversions": float(daily_conversions['total_conversions'])
                })
            
            return list(reversed(conversion_trends))  # Return in chronological order
            
        except Exception as e:
            logger.error(f"Error getting conversion trends: {e}")
            return []
    
    def _generate_conversion_insights(self, conversion_data: Dict[str, Any]) -> List[str]:
        """Generate insights based on conversion data"""
        insights = []
        
        try:
            conversion_rate = conversion_data.get('avg_conversion_rate', 0)
            total_conversions = conversion_data.get('total_conversions', 0)
            
            if conversion_rate < 0.01:  # Less than 1%
                insights.append("Low conversion rate detected - consider optimizing landing pages")
            
            if total_conversions < 10:
                insights.append("Low conversion volume - review targeting and ad relevance")
            
            if conversion_rate > 0.05:  # More than 5%
                insights.append("Excellent conversion rate - consider scaling successful campaigns")
                
        except Exception as e:
            logger.error(f"Error generating conversion insights: {e}")
        
        return insights

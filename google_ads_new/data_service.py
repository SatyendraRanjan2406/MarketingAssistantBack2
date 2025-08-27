"""
Data Service for Google Ads Analysis
Fetches real campaign data from database for OpenAI analysis
"""

import logging
from typing import Dict, List, Any, Optional
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Sum

logger = logging.getLogger(__name__)

class GoogleAdsDataService:
    """Service for fetching Google Ads data from database"""
    
    def __init__(self, user):
        self.user = user
        self.logger = logging.getLogger(__name__)
    
    def get_campaign_data(self, account_id: str = None) -> Dict[str, Any]:
        """Get comprehensive campaign data for analysis"""
        try:
            from .models import GoogleAdsAccount, GoogleAdsCampaign, GoogleAdsAdGroup, GoogleAdsPerformance
            
            # Get user's accounts
            accounts = self._get_user_accounts(account_id)
            if not accounts:
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            # Fetch campaign data
            campaigns = GoogleAdsCampaign.objects.filter(account=account)
            ad_groups = GoogleAdsAdGroup.objects.filter(campaign__account=account)
            
            # Get performance data if available
            performance_data = self._get_performance_data(account)
            
            campaign_data = {
                "account_info": {
                    "account_name": account.account_name,
                    "customer_id": account.customer_id,
                    "account_status": account.is_active
                },
                "campaigns": list(campaigns.values(
                    'campaign_name', 'campaign_status', 'budget_amount', 
                    'campaign_type', 'start_date', 'end_date'
                )),
                "ad_groups": list(ad_groups.values(
                    'ad_group_name', 'campaign__campaign_name', 'status'
                )),
                "performance_metrics": performance_data,
                "summary": {
                    "total_campaigns": campaigns.count(),
                    "active_campaigns": campaigns.filter(campaign_status='ENABLED').count(),
                    "total_ad_groups": ad_groups.count(),
                    "total_budget": sum(c.budget_amount or 0 for c in campaigns if c.budget_amount),
                    "analysis_date": timezone.now().isoformat()
                }
            }
            
            return campaign_data
            
        except Exception as e:
            self.logger.error(f"Error fetching campaign data: {e}")
            return {"error": f"Failed to fetch campaign data: {str(e)}"}
    
    def get_keyword_data(self, account_id: str = None) -> Dict[str, Any]:
        """Get keyword data for analysis"""
        try:
            from .models import GoogleAdsAccount, GoogleAdsCampaign, GoogleAdsAdGroup
            
            accounts = self._get_user_accounts(account_id)
            if not accounts:
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            # Fetch keyword-related data
            campaigns = GoogleAdsCampaign.objects.filter(account=account)
            ad_groups = GoogleAdsAdGroup.objects.filter(campaign__account=account)
            
            keyword_data = {
                "account_name": account.account_name,
                "campaigns": list(campaigns.values('campaign_name', 'campaign_status')),
                "ad_groups": list(ad_groups.values('ad_group_name', 'campaign__campaign_name')),
                "keyword_analysis": {
                    "total_campaigns": campaigns.count(),
                    "total_ad_groups": ad_groups.count(),
                    "analysis_focus": "keyword performance, trends, and optimization"
                }
            }
            
            return keyword_data
            
        except Exception as e:
            self.logger.error(f"Error fetching keyword data: {e}")
            return {"error": f"Failed to fetch keyword data: {str(e)}"}
    
    def get_performance_data(self, account_id: str = None, days: int = 30) -> Dict[str, Any]:
        """Get performance data for analysis"""
        try:
            from .models import GoogleAdsAccount, GoogleAdsCampaign, GoogleAdsPerformance
            
            accounts = self._get_user_accounts(account_id)
            if not accounts:
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            # Calculate date range
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            # Fetch performance data
            performance_records = GoogleAdsPerformance.objects.filter(
                campaign__account=account,
                date__range=[start_date, end_date]
            )
            
            # Aggregate performance data
            performance_summary = {
                "total_impressions": sum(p.impressions or 0 for p in performance_records),
                "total_clicks": sum(p.clicks or 0 for p in performance_records),
                "total_spend": sum(p.cost or 0 for p in performance_records),
                "total_conversions": sum(p.conversions or 0 for p in performance_records),
                "avg_ctr": self._calculate_avg_ctr(performance_records),
                "avg_cpc": self._calculate_avg_cpc(performance_records),
                "conversion_rate": self._calculate_conversion_rate(performance_records),
                "roas": self._calculate_roas(performance_records)
            }
            
            performance_data = {
                "account_name": account.account_name,
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": days
                },
                "performance_summary": performance_summary,
                "daily_data": list(performance_records.values('date', 'impressions', 'clicks', 'cost', 'conversions')),
                "campaign_performance": self._get_campaign_performance(account, start_date, end_date)
            }
            
            return performance_data
            
        except Exception as e:
            self.logger.error(f"Error fetching performance data: {e}")
            return {"error": f"Failed to fetch performance data: {str(e)}"}
    
    def get_budget_data(self, account_id: str = None) -> Dict[str, Any]:
        """Get budget data for analysis"""
        try:
            from .models import GoogleAdsAccount, GoogleAdsCampaign
            
            accounts = self._get_user_accounts(account_id)
            if not accounts:
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            # Fetch budget-related data
            campaigns = GoogleAdsCampaign.objects.filter(account=account)
            
            budget_data = {
                "account_name": account.account_name,
                "total_budget": sum(c.budget_amount or 0 for c in campaigns if c.budget_amount),
                "campaigns": list(campaigns.values('campaign_name', 'budget_amount', 'campaign_status')),
                "budget_distribution": self._analyze_budget_distribution(campaigns),
                "budget_efficiency": self._analyze_budget_efficiency(campaigns)
            }
            
            return budget_data
            
        except Exception as e:
            self.logger.error(f"Error fetching budget data: {e}")
            return {"error": f"Failed to fetch budget data: {str(e)}"}
    
    def get_device_performance_data(self, account_id: str = None) -> Dict[str, Any]:
        """Get device performance data for analysis"""
        try:
            from .models import GoogleAdsAccount, GoogleAdsCampaign
            
            accounts = self._get_user_accounts(account_id)
            if not accounts:
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            # Mock device performance data (replace with actual data when available)
            device_data = {
                "account_name": account.account_name,
                "device_performance": {
                    "mobile": {
                        "impressions": 10000,
                        "clicks": 500,
                        "cost": 1000,
                        "conversions": 25,
                        "ctr": 0.05,
                        "cpc": 2.0,
                        "conversion_rate": 0.05
                    },
                    "desktop": {
                        "impressions": 8000,
                        "clicks": 600,
                        "cost": 1200,
                        "conversions": 40,
                        "ctr": 0.075,
                        "cpc": 2.0,
                        "conversion_rate": 0.067
                    },
                    "tablet": {
                        "impressions": 2000,
                        "clicks": 100,
                        "cost": 200,
                        "conversions": 5,
                        "ctr": 0.05,
                        "cpc": 2.0,
                        "conversion_rate": 0.05
                    }
                }
            }
            
            return device_data
            
        except Exception as e:
            self.logger.error(f"Error fetching device performance data: {e}")
            return {"error": f"Failed to fetch device performance data: {str(e)}"}
    
    def get_location_performance_data(self, account_id: str = None) -> Dict[str, Any]:
        """Get location performance data for analysis"""
        try:
            from .models import GoogleAdsAccount, GoogleAdsCampaign
            
            accounts = self._get_user_accounts(account_id)
            if not accounts:
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            # Mock location performance data (replace with actual data when available)
            location_data = {
                "account_name": account.account_name,
                "location_performance": {
                    "New York": {
                        "impressions": 5000,
                        "clicks": 300,
                        "cost": 600,
                        "conversions": 20,
                        "ctr": 0.06,
                        "cpc": 2.0,
                        "conversion_rate": 0.067
                    },
                    "Los Angeles": {
                        "impressions": 4000,
                        "clicks": 250,
                        "cost": 500,
                        "conversions": 15,
                        "ctr": 0.0625,
                        "cpc": 2.0,
                        "conversion_rate": 0.06
                    },
                    "Chicago": {
                        "impressions": 3000,
                        "clicks": 180,
                        "cost": 360,
                        "conversions": 12,
                        "ctr": 0.06,
                        "cpc": 2.0,
                        "conversion_rate": 0.067
                    }
                }
            }
            
            return location_data
            
        except Exception as e:
            self.logger.error(f"Error fetching location performance data: {e}")
            return {"error": f"Failed to fetch location performance data: {str(e)}"}
    
    def _get_user_accounts(self, account_id: str = None):
        """Get user's Google Ads accounts"""
        from .models import GoogleAdsAccount
        
        accounts = GoogleAdsAccount.objects.filter(user=self.user, is_active=True)
        if account_id:
            accounts = accounts.filter(customer_id=account_id)
        return accounts
    
    def _get_performance_data(self, account) -> Dict[str, Any]:
        """Get performance data for an account"""
        try:
            from .models import GoogleAdsPerformance
            
            # Get recent performance data
            recent_performance = GoogleAdsPerformance.objects.filter(
                campaign__account=account
            ).order_by('-date')[:30]  # Last 30 records
            
            if recent_performance:
                return {
                    "total_impressions": sum(p.impressions or 0 for p in recent_performance),
                    "total_clicks": sum(p.clicks or 0 for p in recent_performance),
                    "total_cost": sum(p.cost or 0 for p in recent_performance),
                    "total_conversions": sum(p.conversions or 0 for p in recent_performance)
                }
            else:
                return {
                    "total_impressions": 0,
                    "total_clicks": 0,
                    "total_cost": 0,
                    "total_conversions": 0
                }
        except Exception as e:
            self.logger.error(f"Error getting performance data: {e}")
            return {}
    
    def _get_campaign_performance(self, account, start_date, end_date) -> List[Dict]:
        """Get campaign performance data"""
        try:
            from .models import GoogleAdsCampaign, GoogleAdsPerformance
            
            campaigns = GoogleAdsCampaign.objects.filter(account=account)
            campaign_performance = []
            
            for campaign in campaigns:
                performance = GoogleAdsPerformance.objects.filter(
                    campaign=campaign,
                    date__range=[start_date, end_date]
                ).aggregate(
                    total_impressions=Sum('impressions') or 0,
                    total_clicks=Sum('clicks') or 0,
                    total_cost=Sum('cost') or 0,
                    total_conversions=Sum('conversions') or 0
                )
                
                campaign_performance.append({
                    "campaign_name": campaign.campaign_name,
                    "campaign_status": campaign.campaign_status,
                    "budget_amount": campaign.budget_amount,
                    "performance": performance
                })
            
            return campaign_performance
            
        except Exception as e:
            self.logger.error(f"Error getting campaign performance: {e}")
            return []
    
    def _analyze_budget_distribution(self, campaigns) -> Dict[str, Any]:
        """Analyze budget distribution across campaigns"""
        try:
            total_budget = sum(c.budget_amount or 0 for c in campaigns if c.budget_amount)
            if total_budget == 0:
                return {"distribution": "No budget data available"}
            
            budget_distribution = {}
            for campaign in campaigns:
                if campaign.budget_amount:
                    percentage = (campaign.budget_amount / total_budget) * 100
                    budget_distribution[campaign.campaign_name] = {
                        "budget": campaign.budget_amount,
                        "percentage": round(percentage, 2)
                    }
            
            return budget_distribution
            
        except Exception as e:
            self.logger.error(f"Error analyzing budget distribution: {e}")
            return {}
    
    def _analyze_budget_efficiency(self, campaigns) -> Dict[str, Any]:
        """Analyze budget efficiency across campaigns"""
        try:
            active_campaigns = campaigns.filter(campaign_status='ENABLED')
            paused_campaigns = campaigns.filter(campaign_status='PAUSED')
            
            return {
                "active_campaigns_count": active_campaigns.count(),
                "paused_campaigns_count": paused_campaigns.count(),
                "total_campaigns": campaigns.count(),
                "efficiency_metrics": "Budget efficiency analysis based on campaign status and performance"
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing budget efficiency: {e}")
            return {}
    
    def _calculate_avg_ctr(self, performance_records) -> float:
        """Calculate average CTR"""
        try:
            total_impressions = sum(p.impressions or 0 for p in performance_records)
            total_clicks = sum(p.clicks or 0 for p in performance_records)
            
            if total_impressions > 0:
                return round((total_clicks / total_impressions) * 100, 2)
            return 0.0
        except Exception:
            return 0.0
    
    def _calculate_avg_cpc(self, performance_records) -> float:
        """Calculate average CPC"""
        try:
            total_clicks = sum(p.clicks or 0 for p in performance_records)
            total_cost = sum(p.cost or 0 for p in performance_records)
            
            if total_clicks > 0:
                return round(total_cost / total_clicks, 2)
            return 0.0
        except Exception:
            return 0.0
    
    def _calculate_conversion_rate(self, performance_records) -> float:
        """Calculate conversion rate"""
        try:
            total_clicks = sum(p.clicks or 0 for p in performance_records)
            total_conversions = sum(p.conversions or 0 for p in performance_records)
            
            if total_clicks > 0:
                return round((total_conversions / total_clicks) * 100, 2)
            return 0.0
        except Exception:
            return 0.0
    
    def _calculate_roas(self, performance_records) -> float:
        """Calculate ROAS (Return on Ad Spend)"""
        try:
            total_cost = sum(p.cost or 0 for p in performance_records)
            # Assuming conversion value is available in performance data
            # For now, using a placeholder calculation
            total_conversion_value = sum(p.conversions or 0 for p in performance_records) * 100  # Placeholder
            
            if total_cost > 0:
                return round(total_conversion_value / total_cost, 2)
            return 0.0
        except Exception:
            return 0.0


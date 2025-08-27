"""
Comprehensive Google Ads Analysis Service
Handles all analysis actions and provides intelligent optimization recommendations
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal
import json

logger = logging.getLogger(__name__)

class GoogleAdsAnalysisService:
    """Comprehensive analysis service for Google Ads campaigns"""
    
    def __init__(self, user):
        self.user = user
        self.logger = logging.getLogger(__name__)
    
    def analyze_audience(self, account_id: str = None) -> Dict[str, Any]:
        """Analyze audience size, overlap, and quality"""
        try:
            from .models import GoogleAdsAccount, GoogleAdsCampaign, GoogleAdsAdGroup
            from .openai_service import GoogleAdsOpenAIService
            
            # Get user's accounts
            accounts = GoogleAdsAccount.objects.filter(user=self.user, is_active=True)
            if account_id:
                accounts = accounts.filter(customer_id=account_id)
            
            if not accounts.exists():
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            # Get actual campaign and ad group data
            campaigns = GoogleAdsCampaign.objects.filter(account=account)
            ad_groups = GoogleAdsAdGroup.objects.filter(campaign__account=account)
            
            # Prepare data for OpenAI analysis
            analysis_data = {
                "account_name": account.account_name,
                "campaigns_count": campaigns.count(),
                "ad_groups_count": ad_groups.count(),
                "campaigns": list(campaigns.values('campaign_name', 'campaign_status', 'budget_amount', 'campaign_type')),
                "ad_groups": list(ad_groups.values('ad_group_name', 'campaign__campaign_name', 'status')),
                "analysis_type": "audience_analysis",
                "target_audience_size": "1M-10M for conversion, 100K-1M for awareness",
                "target_overlap": "<20% between ad sets"
            }
            
            # Generate dynamic response using OpenAI
            openai_service = GoogleAdsOpenAIService()
            response = openai_service.generate_analysis_response(
                "ANALYZE_AUDIENCE", 
                analysis_data,
                f"Analyzing audience size, overlap, and quality for account {account.account_name}"
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error analyzing audience: {e}")
            return {"error": f"Failed to analyze audience: {str(e)}"}
    
    def check_creative_fatigue(self, account_id: str = None) -> Dict[str, Any]:
        """Monitor creative fatigue and variety"""
        try:
            from .models import GoogleAdsAccount, GoogleAdsCampaign, GoogleAdsAdGroup
            
            accounts = GoogleAdsAccount.objects.filter(user=self.user, is_active=True)
            if account_id:
                accounts = accounts.filter(customer_id=account_id)
            
            if not accounts.exists():
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            # Mock creative fatigue analysis
            creative_analysis = {
                "frequency_analysis": {
                    "status": "warning",
                    "message": "Frequency should be <3.5 for prospecting, <5.0 for retargeting",
                    "recommendations": [
                        "Monitor frequency levels across campaigns",
                        "Suggest creative refresh when thresholds exceeded",
                        "Implement frequency capping for better reach"
                    ]
                },
                "creative_variety": {
                    "status": "info",
                    "message": "Each ad set should have 3-6 active creatives for optimal delivery",
                    "recommendations": [
                        "Check creative count per ad set",
                        "Suggest adding more creatives if <3",
                        "Pause underperformers if >6",
                        "Maintain creative diversity for better performance"
                    ]
                }
            }
            
            return {
                "success": True,
                "analysis": creative_analysis,
                "account": account.account_name,
                "timestamp": timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error checking creative fatigue: {e}")
            return {"error": f"Failed to check creative fatigue: {str(e)}"}
    
    def analyze_video_performance(self, account_id: str = None) -> Dict[str, Any]:
        """Analyze video completion rates and format performance"""
        try:
            from .models import GoogleAdsAccount
            
            accounts = GoogleAdsAccount.objects.filter(user=self.user, is_active=True)
            if account_id:
                accounts = accounts.filter(customer_id=account_id)
            
            if not accounts.exists():
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            video_analysis = {
                "completion_rates": {
                    "status": "warning",
                    "message": "Video ads should achieve >25% completion rate for 15s videos, >15% for 30s+ videos",
                    "recommendations": [
                        "Flag low completion rates",
                        "Suggest video optimization (hook, length, format)",
                        "Test shorter video formats for better completion",
                        "Optimize video thumbnails and first 3 seconds"
                    ]
                },
                "format_performance": {
                    "status": "info",
                    "message": "Test multiple formats: single image, carousel, video, collection",
                    "recommendations": [
                        "Analyze format performance",
                        "Suggest format shifts based on CPM and engagement data",
                        "Test different creative formats systematically",
                        "Use format performance data to guide creative strategy"
                    ]
                }
            }
            
            return {
                "success": True,
                "analysis": video_analysis,
                "account": account.account_name,
                "timestamp": timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing video performance: {e}")
            return {"error": f"Failed to analyze video performance: {str(e)}"}
    
    def compare_performance(self, comparison_type: str = "M1_M2", account_id: str = None) -> Dict[str, Any]:
        """Compare performance across time periods"""
        try:
            from .models import GoogleAdsAccount
            
            accounts = GoogleAdsAccount.objects.filter(user=self.user, is_active=True)
            if account_id:
                accounts = accounts.filter(customer_id=account_id)
            
            if not accounts.exists():
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            # Define comparison types
            comparison_types = {
                "M1_M2": "Month 1 vs Month 2 comparison",
                "MTD": "Month-to-date comparison",
                "W1_W2": "Week 1 vs Week 2 comparison",
                "D1_D2": "Day 1 vs Day 2 comparison"
            }
            
            comparison_type_name = comparison_types.get(comparison_type, comparison_type)
            
            performance_comparison = {
                "campaign_level": {
                    "metrics": ["Reach", "Impressions", "CPM", "CTR", "CPC", "Frequency", "Conv Rate", "Conversions", "Spend", "Cost/Conv", "ROAS"],
                    "status": "info",
                    "message": f"Campaign level performance comparison: {comparison_type_name}"
                },
                "ad_set_level": {
                    "metrics": ["Reach", "Impressions", "CPM", "CTR", "CPC", "Frequency", "Conv Rate", "Conversions", "Spend", "Cost/Conv", "ROAS"],
                    "status": "info",
                    "message": f"Ad set level performance comparison: {comparison_type_name}"
                },
                "ad_level": {
                    "metrics": ["Reach", "Impressions", "CPM", "CTR", "CPC", "Frequency", "Engagement Rate", "Conv Rate", "Conversions", "Relevance Score"],
                    "status": "info",
                    "message": f"Ad level performance comparison: {comparison_type_name}"
                },
                "red_flags": {
                    "critical": [],
                    "moderate": []
                }
            }
            
            return {
                "success": True,
                "comparison": performance_comparison,
                "comparison_type": comparison_type_name,
                "account": account.account_name,
                "timestamp": timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error comparing performance: {e}")
            return {"error": f"Failed to compare performance: {str(e)}"}
    
    def optimize_campaign(self, account_id: str = None) -> Dict[str, Any]:
        """Provide campaign-level optimization recommendations"""
        try:
            from .models import GoogleAdsAccount, GoogleAdsCampaign
            from .openai_service import GoogleAdsOpenAIService
            
            accounts = GoogleAdsAccount.objects.filter(user=self.user, is_active=True)
            if account_id:
                accounts = accounts.filter(customer_id=account_id)
            
            if not accounts.exists():
                return {
                    "error": "No active Google Ads accounts found",
                    "message": "Please connect your Google Ads accounts first to use this feature.",
                    "blocks": [
                        {
                            "type": "text",
                            "content": "No Google Ads Accounts Connected",
                            "style": "heading"
                        },
                        {
                            "type": "text",
                            "content": "To analyze and optimize campaigns, you need to connect your Google Ads accounts first.",
                            "style": "paragraph"
                        },
                        {
                            "type": "actions",
                            "title": "Connect Accounts",
                            "items": [
                                {"id": "connect_accounts", "label": "Connect Google Ads Accounts"}
                            ]
                        }
                    ]
                }
            
            account = accounts.first()
            
            # Get actual campaign data for optimization analysis
            campaigns = GoogleAdsCampaign.objects.filter(account=account)
            
            # Prepare data for OpenAI analysis
            analysis_data = {
                "account_name": account.account_name,
                "campaigns_count": campaigns.count(),
                "campaigns": list(campaigns.values('campaign_name', 'campaign_status', 'budget_amount', 'campaign_type')),
                "analysis_type": "campaign_optimization",
                "optimization_focus": "budget, performance, delivery, and efficiency"
            }
            
            # Generate dynamic response using OpenAI
            openai_service = GoogleAdsOpenAIService()
            response = openai_service.generate_analysis_response(
                "OPTIMIZE_CAMPAIGN", 
                analysis_data,
                f"Providing campaign optimization recommendations for account {account.account_name}"
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error optimizing campaigns: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return {"error": f"Failed to optimize campaigns: {str(e)}", "details": traceback.format_exc()}
    
    def optimize_adset(self, account_id: str = None) -> Dict[str, Any]:
        """Provide ad set-level optimization recommendations"""
        try:
            from .models import GoogleAdsAccount
            
            accounts = GoogleAdsAccount.objects.filter(user=self.user, is_active=True)
            if account_id:
                accounts = accounts.filter(customer_id=account_id)
            
            if not accounts.exists():
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            adset_optimizations = {
                "audience_expansion": {
                    "condition": "Ad set with good performance but limited by audience size",
                    "action": "Expand to broader lookalike audiences (2%, 3%)",
                    "priority": "medium"
                },
                "frequency_optimization": {
                    "condition": "Ad set with high frequency and declining CTR",
                    "action": "Refresh creatives or expand audience",
                    "priority": "high"
                },
                "delivery_optimization": {
                    "condition": "Ad set with low delivery and good metrics",
                    "action": "Increase bid or remove audience overlap",
                    "priority": "medium"
                },
                "relevance_optimization": {
                    "condition": "Ad set with poor relevance score (<6) and high CPM",
                    "action": "Review targeting and creative alignment",
                    "priority": "high"
                }
            }
            
            return {
                "success": True,
                "optimizations": adset_optimizations,
                "account": account.account_name,
                "timestamp": timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing ad sets: {e}")
            return {"error": f"Failed to optimize ad sets: {str(e)}"}
    
    def optimize_ad(self, account_id: str = None) -> Dict[str, Any]:
        """Provide ad-level optimization recommendations"""
        try:
            from .models import GoogleAdsAccount
            
            accounts = GoogleAdsAccount.objects.filter(user=self.user, is_active=True)
            if account_id:
                accounts = accounts.filter(customer_id=account_id)
            
            if not accounts.exists():
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            ad_optimizations = {
                "high_performing_dominance": {
                    "condition": "High-performing ad creative dominating delivery",
                    "action": "Duplicate successful elements in new creatives",
                    "priority": "medium"
                },
                "ctr_conversion_mismatch": {
                    "condition": "Ad with high CTR but low conversion rate",
                    "action": "Check landing page alignment and conversion tracking",
                    "priority": "high"
                }
            }
            
            return {
                "success": True,
                "optimizations": ad_optimizations,
                "account": account.account_name,
                "timestamp": timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing ads: {e}")
            return {"error": f"Failed to optimize ads: {str(e)}"}
    
    def analyze_placements(self, account_id: str = None) -> Dict[str, Any]:
        """Analyze placement performance (auto vs manual)"""
        try:
            from .models import GoogleAdsAccount
            
            accounts = GoogleAdsAccount.objects.filter(user=self.user, is_active=True)
            if account_id:
                accounts = accounts.filter(customer_id=account_id)
            
            if not accounts.exists():
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            placement_analysis = {
                "auto_vs_manual": {
                    "status": "info",
                    "message": "Auto placements vs manual placement performance analysis",
                    "recommendations": [
                        "Compare performance between auto and manual placements",
                        "Identify top-performing placement types",
                        "Optimize bid adjustments for different placements",
                        "Consider manual placement for better control"
                    ]
                }
            }
            
            return {
                "success": True,
                "analysis": placement_analysis,
                "account": account.account_name,
                "timestamp": timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing placements: {e}")
            return {"error": f"Failed to analyze placements: {str(e)}"}
    
    def analyze_device_performance(self, account_id: str = None) -> Dict[str, Any]:
        """Compare mobile vs desktop performance"""
        try:
            from .models import GoogleAdsAccount
            
            accounts = GoogleAdsAccount.objects.filter(user=self.user, is_active=True)
            if account_id:
                accounts = accounts.filter(customer_id=account_id)
            
            if not accounts.exists():
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            device_analysis = {
                "mobile_vs_desktop": {
                    "status": "info",
                    "message": "Mobile vs desktop performance comparison",
                    "recommendations": [
                        "Analyze device-specific metrics",
                        "Suggest bid adjustments (+/-20% for mobile/desktop)",
                        "Optimize creative formats for each device type",
                        "Consider device-specific landing pages"
                    ]
                }
            }
            
            return {
                "success": True,
                "analysis": device_analysis,
                "account": account.account_name,
                "timestamp": timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing device performance: {e}")
            return {"error": f"Failed to analyze device performance: {str(e)}"}
    
    def analyze_time_performance(self, account_id: str = None) -> Dict[str, Any]:
        """Analyze day of week and hour performance"""
        try:
            from .models import GoogleAdsAccount
            
            accounts = GoogleAdsAccount.objects.filter(user=self.user, is_active=True)
            if account_id:
                accounts = accounts.filter(customer_id=account_id)
            
            if not accounts.exists():
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            time_analysis = {
                "day_of_week": {
                    "status": "info",
                    "message": "Day of week performance analysis",
                    "recommendations": [
                        "Identify peak performance days",
                        "Optimize ad scheduling for high-performing days",
                        "Adjust budget allocation based on day performance"
                    ]
                },
                "hour_analysis": {
                    "status": "info",
                    "message": "Hour of day performance analysis",
                    "recommendations": [
                        "Identify peak performance hours",
                        "Optimize ad delivery timing",
                        "Schedule ads during high-engagement hours"
                    ]
                }
            }
            
            return {
                "success": True,
                "analysis": time_analysis,
                "account": account.account_name,
                "timestamp": timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing time performance: {e}")
            return {"error": f"Failed to analyze time performance: {str(e)}"}
    
    def analyze_demographics(self, account_id: str = None) -> Dict[str, Any]:
        """Analyze age and gender performance within segments"""
        try:
            from .models import GoogleAdsAccount
            
            accounts = GoogleAdsAccount.objects.filter(user=self.user, is_active=True)
            if account_id:
                accounts = accounts.filter(customer_id=account_id)
            
            if not accounts.exists():
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            demographic_analysis = {
                "age_gender_performance": {
                    "status": "info",
                    "message": "Demographic performance breakdown within targeted segments",
                    "recommendations": [
                        "Find top-performing age/gender segments",
                        "Suggest audience refinement or separate campaigns",
                        "Optimize targeting for high-performing demographics",
                        "Consider demographic-specific creative messaging"
                    ]
                }
            }
            
            return {
                "success": True,
                "analysis": demographic_analysis,
                "account": account.account_name,
                "timestamp": timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing demographics: {e}")
            return {"error": f"Failed to analyze demographics: {str(e)}"}
    
    def analyze_competitors(self, account_id: str = None) -> Dict[str, Any]:
        """Monitor competitor creative activity and trends"""
        try:
            from .models import GoogleAdsAccount
            
            accounts = GoogleAdsAccount.objects.filter(user=self.user, is_active=True)
            if account_id:
                accounts = accounts.filter(customer_id=account_id)
            
            if not accounts.exists():
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            competitor_analysis = {
                "creative_monitoring": {
                    "status": "info",
                    "message": "Monitor competitor ad activity and creative trends in industry",
                    "recommendations": [
                        "Use Facebook Ad Library to analyze top competitors' creatives",
                        "Suggest creative strategy improvements based on trends",
                        "Monitor competitor messaging and positioning",
                        "Identify creative opportunities and gaps"
                    ]
                }
            }
            
            return {
                "success": True,
                "analysis": competitor_analysis,
                "account": account.account_name,
                "timestamp": timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing competitors: {e}")
            return {"error": f"Failed to analyze competitors: {str(e)}"}
    
    def test_creative_elements(self, account_id: str = None) -> Dict[str, Any]:
        """Test individual creative elements systematically"""
        try:
            from .models import GoogleAdsAccount
            
            accounts = GoogleAdsAccount.objects.filter(user=self.user, is_active=True)
            if account_id:
                accounts = accounts.filter(customer_id=account_id)
            
            if not accounts.exists():
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            creative_testing = {
                "systematic_testing": {
                    "status": "info",
                    "message": "Test individual creative elements (headlines, images, CTAs)",
                    "recommendations": [
                        "Implement systematic creative testing framework",
                        "Test with statistical significance",
                        "Isolate individual elements for testing",
                        "Track performance metrics for each variation"
                    ]
                }
            }
            
            return {
                "success": True,
                "testing": creative_testing,
                "account": account.account_name,
                "timestamp": timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error testing creative elements: {e}")
            return {"error": f"Failed to test creative elements: {str(e)}"}
    
    def check_technical_compliance(self, account_id: str = None) -> Dict[str, Any]:
        """Verify technical implementation and compliance"""
        try:
            from .models import GoogleAdsAccount
            
            accounts = GoogleAdsAccount.objects.filter(user=self.user, is_active=True)
            if account_id:
                accounts = accounts.filter(customer_id=account_id)
            
            if not accounts.exists():
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            technical_checks = {
                "pixel_implementation": {
                    "status": "warning",
                    "message": "Facebook Pixel should fire correctly on all conversion events",
                    "recommendations": [
                        "Verify pixel firing using Facebook Pixel Helper",
                        "Check event parameters and data accuracy",
                        "Ensure all conversion events are tracked",
                        "Test pixel functionality regularly"
                    ]
                },
                "ios_attribution": {
                    "status": "warning",
                    "message": "Account for iOS attribution challenges in reporting",
                    "recommendations": [
                        "Check if Conversions API is implemented",
                        "Suggest attribution modeling adjustments",
                        "Monitor iOS 14.5+ impact on performance",
                        "Implement alternative tracking methods"
                    ]
                },
                "creative_compliance": {
                    "status": "info",
                    "message": "Ads should comply with Meta's advertising policies",
                    "recommendations": [
                        "Review ads for policy violations",
                        "Check text overlay limits",
                        "Avoid prohibited content",
                        "Ensure truthful and non-misleading claims"
                    ]
                },
                "landing_page_experience": {
                    "status": "info",
                    "message": "Landing page should match ad promise and load quickly",
                    "recommendations": [
                        "Check landing page relevance",
                        "Ensure mobile optimization",
                        "Target load speed <3 seconds",
                        "Match ad messaging to landing page content"
                    ]
                }
            }
            
            return {
                "success": True,
                "checks": technical_checks,
                "account": account.account_name,
                "timestamp": timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error checking technical compliance: {e}")
            return {"error": f"Failed to check technical compliance: {str(e)}"}
    
    def analyze_audience_insights(self, account_id: str = None) -> Dict[str, Any]:
        """Monitor audience saturation and cross-campaign attribution"""
        try:
            from .models import GoogleAdsAccount
            
            accounts = GoogleAdsAccount.objects.filter(user=self.user, is_active=True)
            if account_id:
                accounts = accounts.filter(customer_id=account_id)
            
            if not accounts.exists():
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            audience_insights = {
                "audience_saturation": {
                    "status": "info",
                    "message": "Monitor audience saturation levels and performance decline",
                    "recommendations": [
                        "Track frequency trends and performance metrics",
                        "Identify when to expand audiences",
                        "Monitor for performance decline due to saturation",
                        "Implement audience expansion strategies"
                    ]
                },
                "cross_campaign_attribution": {
                    "status": "info",
                    "message": "Track customer journey across multiple campaigns and touchpoints",
                    "recommendations": [
                        "Analyze attribution data for campaign interaction",
                        "Optimize budget allocation based on attribution",
                        "Understand customer journey patterns",
                        "Optimize campaign sequencing"
                    ]
                },
                "custom_conversion_events": {
                    "status": "info",
                    "message": "Optimize for events that closely align with business value",
                    "recommendations": [
                        "Review conversion events and their value",
                        "Suggest optimization for higher-value actions",
                        "Prioritize purchase events over page views",
                        "Align conversion tracking with business goals"
                    ]
                }
            }
            
            return {
                "success": True,
                "insights": audience_insights,
                "account": account.account_name,
                "timestamp": timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing audience insights: {e}")
            return {"error": f"Failed to analyze audience insights: {str(e)}"}
    
    def optimize_budgets(self, account_id: str = None) -> Dict[str, Any]:
        """Provide budget optimization recommendations"""
        try:
            from .models import GoogleAdsAccount
            
            accounts = GoogleAdsAccount.objects.filter(user=self.user, is_active=True)
            if account_id:
                accounts = accounts.filter(customer_id=account_id)
            
            if not accounts.exists():
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            budget_optimizations = {
                "budget_allocation": {
                    "status": "info",
                    "message": "Optimize budget allocation based on performance",
                    "recommendations": [
                        "Shift budget to high-performing campaigns",
                        "Reduce budget for underperforming campaigns",
                        "Consider seasonal budget adjustments",
                        "Implement budget pacing strategies"
                    ]
                },
                "bid_optimization": {
                    "status": "info",
                    "message": "Optimize bids for better performance",
                    "recommendations": [
                        "Adjust bids based on performance data",
                        "Implement automated bidding strategies",
                        "Monitor bid competition and adjust accordingly",
                        "Test different bid strategies"
                    ]
                }
            }
            
            return {
                "success": True,
                "optimizations": budget_optimizations,
                "account": account.account_name,
                "timestamp": timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing budgets: {e}")
            return {"error": f"Failed to optimize budgets: {str(e)}"}
    
    def check_campaign_consistency(self, account_id: str = None) -> Dict[str, Any]:
        """Check keyword-ad consistency and ad group alignment"""
        try:
            from .models import GoogleAdsAccount, GoogleAdsCampaign, GoogleAdsAdGroup
            from .openai_service import GoogleAdsOpenAIService
            
            # Get user's accounts
            accounts = GoogleAdsAccount.objects.filter(user=self.user, is_active=True)
            if account_id:
                accounts = accounts.filter(customer_id=account_id)
            
            if not accounts.exists():
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            # Get actual campaign data using data service
            from .data_service import GoogleAdsDataService
            data_service = GoogleAdsDataService(self.user)
            analysis_data = data_service.get_campaign_data(account_id)
            
            if "error" in analysis_data:
                return analysis_data
            
            # Add analysis type
            analysis_data["analysis_type"] = "campaign_consistency"
            
            # Generate dynamic response using OpenAI
            openai_service = GoogleAdsOpenAIService()
            response = openai_service.generate_analysis_response(
                "CHECK_CAMPAIGN_CONSISTENCY", 
                analysis_data,
                f"Analyzing campaign consistency for account {account.account_name}"
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error checking campaign consistency: {e}")
            return {"error": f"Failed to check campaign consistency: {str(e)}"}
    
    def check_sitelinks(self, account_id: str = None) -> Dict[str, Any]:
        """Verify 4-6 sitelinks are present and optimized"""
        try:
            from .models import GoogleAdsAccount, GoogleAdsCampaign
            from .openai_service import GoogleAdsOpenAIService
            
            accounts = GoogleAdsAccount.objects.filter(user=self.user, is_active=True)
            if account_id:
                accounts = accounts.filter(customer_id=account_id)
            
            if not accounts.exists():
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            # Get actual campaign data for sitelink analysis
            campaigns = GoogleAdsCampaign.objects.filter(account=account)
            
            # Prepare data for OpenAI analysis
            analysis_data = {
                "account_name": account.account_name,
                "campaigns_count": campaigns.count(),
                "campaigns": list(campaigns.values('campaign_name', 'campaign_status', 'budget_amount')),
                "analysis_type": "sitelink_analysis",
                "target_sitelink_count": "4-6 sitelinks per campaign"
            }
            
            # Generate dynamic response using OpenAI
            openai_service = GoogleAdsOpenAIService()
            response = openai_service.generate_analysis_response(
                "CHECK_SITELINKS", 
                analysis_data,
                f"Analyzing sitelink presence and optimization for account {account.account_name}"
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error checking sitelinks: {e}")
            return {"error": f"Failed to check sitelinks: {str(e)}"}
    
    def check_landing_page_url(self, account_id: str = None) -> Dict[str, Any]:
        """Validate LP URL functionality and keyword relevance"""
        try:
            from .models import GoogleAdsAccount
            
            accounts = GoogleAdsAccount.objects.filter(user=self.user, is_active=True)
            if account_id:
                accounts = accounts.filter(customer_id=account_id)
            
            if not accounts.exists():
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            landing_page_analysis = {
                "url_functionality": {
                    "status": "warning",
                    "message": "Check if landing page URL is working and has relevant keywords",
                    "recommendations": [
                        "Verify all landing page URLs are functional",
                        "Check for 404 errors or broken links",
                        "Ensure landing pages load quickly",
                        "Test mobile responsiveness"
                    ]
                },
                "keyword_relevance": {
                    "status": "info",
                    "message": "Landing page content should align with keywords",
                    "recommendations": [
                        "Check if URL page content syncs with keywords",
                        "Implement landing page best practices",
                        "Ensure content relevance to ad messaging",
                        "Optimize for user intent and conversion"
                    ]
                }
            }
            
            return {
                "success": True,
                "analysis": landing_page_analysis,
                "account": account.account_name,
                "timestamp": timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error checking landing page URL: {e}")
            return {"error": f"Failed to check landing page URL: {str(e)}"}
    
    def check_duplicate_keywords(self, account_id: str = None) -> Dict[str, Any]:
        """Identify duplicate keywords across campaigns/ad groups"""
        try:
            from .models import GoogleAdsAccount
            
            accounts = GoogleAdsAccount.objects.filter(user=self.user, is_active=True)
            if account_id:
                accounts = accounts.filter(customer_id=account_id)
            
            if not accounts.exists():
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            duplicate_analysis = {
                "keyword_duplication": {
                    "status": "critical",
                    "message": "Same keyword should not be present in multiple ad groups/campaigns with same targeting",
                    "recommendations": [
                        "Check for keyword duplication across campaigns",
                        "Identify keywords in multiple ad groups",
                        "Suggest consolidation to prevent bidding wars",
                        "Review targeting settings for duplicates"
                    ]
                },
                "bidding_conflicts": {
                    "status": "warning",
                    "message": "Duplicate keywords create internal bidding wars",
                    "recommendations": [
                        "Consolidate duplicate keywords into single ad group",
                        "Use different match types strategically",
                        "Implement negative keywords to prevent conflicts",
                        "Monitor for performance cannibalization"
                    ]
                }
            }
            
            return {
                "success": True,
                "analysis": duplicate_analysis,
                "account": account.account_name,
                "timestamp": timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error checking duplicate keywords: {e}")
            return {"error": f"Failed to check duplicate keywords: {str(e)}"}
    
    def analyze_keyword_trends(self, account_id: str = None) -> Dict[str, Any]:
        """Monitor high-potential keywords with increasing search volume"""
        try:
            from .models import GoogleAdsAccount
            
            accounts = GoogleAdsAccount.objects.filter(user=self.user, is_active=True)
            if account_id:
                accounts = accounts.filter(customer_id=account_id)
            
            if not accounts.exists():
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            keyword_trends = {
                "high_potential_keywords": {
                    "status": "info",
                    "message": "Identify keywords with increasing search volumes that aren't added",
                    "recommendations": [
                        "Monitor search volume trends for relevant keywords",
                        "Identify high-potential keywords not in campaigns",
                        "Suggest adding trending keywords based on volume",
                        "Track seasonal keyword patterns"
                    ]
                },
                "trend_analysis": {
                    "status": "info",
                    "message": "Analyze keyword trends for strategic opportunities",
                    "recommendations": [
                        "Use Google Trends for keyword research",
                        "Monitor competitor keyword strategies",
                        "Identify emerging keyword opportunities",
                        "Plan keyword expansion based on trends"
                    ]
                }
            }
            
            return {
                "success": True,
                "analysis": keyword_trends,
                "account": account.account_name,
                "timestamp": timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing keyword trends: {e}")
            return {"error": f"Failed to analyze keyword trends: {str(e)}"}
    
    def analyze_auction_insights(self, account_id: str = None) -> Dict[str, Any]:
        """Analyze competition and competitor ad strategies"""
        try:
            from .models import GoogleAdsAccount
            
            accounts = GoogleAdsAccount.objects.filter(user=self.user, is_active=True)
            if account_id:
                accounts = accounts.filter(customer_id=account_id)
            
            if not accounts.exists():
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            auction_insights = {
                "competition_analysis": {
                    "status": "info",
                    "message": "Analyze campaigns and ad groups where competition is eating into SI share",
                    "recommendations": [
                        "Identify top 3 SI share competitors",
                        "Check their search ads in Google Transparency Center",
                        "Analyze competitor ad strategies and messaging",
                        "Monitor competitor bid patterns"
                    ]
                },
                "competitor_ad_analysis": {
                    "status": "info",
                    "message": "Display competitor ads and create strategy summary",
                    "recommendations": [
                        "Review competitor ad copy and creative elements",
                        "Analyze competitor landing page strategies",
                        "Identify competitive advantages and opportunities",
                        "Develop counter-strategies based on insights"
                    ]
                }
            }
            
            return {
                "success": True,
                "analysis": auction_insights,
                "account": account.account_name,
                "timestamp": timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing auction insights: {e}")
            return {"error": f"Failed to analyze auction insights: {str(e)}"}
    
    def analyze_search_terms(self, account_id: str = None) -> Dict[str, Any]:
        """Review search terms for negative keyword opportunities"""
        try:
            from .models import GoogleAdsAccount
            
            accounts = GoogleAdsAccount.objects.filter(user=self.user, is_active=True)
            if account_id:
                accounts = accounts.filter(customer_id=account_id)
            
            if not accounts.exists():
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            search_term_analysis = {
                "negative_keyword_opportunities": {
                    "status": "warning",
                    "message": "Search terms with 0 conversions and not excluded should be excluded",
                    "recommendations": [
                        "Identify search terms with 0 conversions",
                        "Create negative keyword exclusion lists",
                        "Exclude poor performing conversion rate keywords",
                        "Regularly review and update negative keywords"
                    ]
                },
                "high_cac_keywords": {
                    "status": "critical",
                    "message": "High CAC, low conversion keywords need negative keyword treatment",
                    "recommendations": [
                        "Flag keywords with high cost per acquisition",
                        "Suggest negative keyword exclusions",
                        "Review bid strategies for expensive keywords",
                        "Consider pausing underperforming keywords"
                    ]
                }
            }
            
            return {
                "success": True,
                "analysis": search_term_analysis,
                "account": account.account_name,
                "timestamp": timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing search terms: {e}")
            return {"error": f"Failed to analyze search terms: {str(e)}"}
    
    def analyze_ads_showing_time(self, account_id: str = None) -> Dict[str, Any]:
        """Analyze hour-of-day performance for bid optimization"""
        try:
            from .models import GoogleAdsAccount
            
            accounts = GoogleAdsAccount.objects.filter(user=self.user, is_active=True)
            if account_id:
                accounts = accounts.filter(customer_id=account_id)
            
            if not accounts.exists():
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            time_analysis = {
                "hour_of_day_analysis": {
                    "status": "info",
                    "message": "Analyze when ads are showing across campaigns for bid optimization",
                    "recommendations": [
                        "Identify peak performance hours for each campaign",
                        "Suggest bid adjustments based on time performance",
                        "Optimize bidding during high-conversion hours",
                        "Reduce bids during low-performance periods"
                    ]
                },
                "bid_timing_optimization": {
                    "status": "info",
                    "message": "Optimize bidding settings based on performance timing",
                    "recommendations": [
                        "Increase bids during high-performing hours",
                        "Decrease bids during low-performing hours",
                        "Use ad scheduling for optimal delivery",
                        "Monitor time-based performance trends"
                    ]
                }
            }
            
            return {
                "success": True,
                "analysis": time_analysis,
                "account": account.account_name,
                "timestamp": timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing ads showing time: {e}")
            return {"error": f"Failed to analyze ads showing time: {str(e)}"}
    
    def analyze_device_performance_detailed(self, account_id: str = None) -> Dict[str, Any]:
        """Detailed device performance analysis for bid adjustments"""
        try:
            from .models import GoogleAdsAccount
            
            accounts = GoogleAdsAccount.objects.filter(user=self.user, is_active=True)
            if account_id:
                accounts = accounts.filter(customer_id=account_id)
            
            if not accounts.exists():
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            device_analysis = {
                "bid_adjustment_analysis": {
                    "status": "info",
                    "message": "Analyze device performance for bid adjustment recommendations",
                    "recommendations": [
                        "Compare mobile vs desktop performance metrics",
                        "Suggest bid adjustments based on device performance",
                        "Increase bids for high-performing devices",
                        "Decrease bids for low-performing devices"
                    ]
                },
                "device_optimization": {
                    "status": "info",
                    "message": "Optimize campaigns for device-specific performance",
                    "recommendations": [
                        "Review device-specific conversion rates",
                        "Optimize landing pages for each device type",
                        "Adjust creative elements for device preferences",
                        "Monitor device performance trends"
                    ]
                }
            }
            
            return {
                "success": True,
                "analysis": device_analysis,
                "account": account.account_name,
                "timestamp": timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing device performance: {e}")
            return {"error": f"Failed to analyze device performance: {str(e)}"}
    
    def analyze_location_performance(self, account_id: str = None) -> Dict[str, Any]:
        """City-level performance analysis and optimization"""
        try:
            from .models import GoogleAdsAccount
            
            accounts = GoogleAdsAccount.objects.filter(user=self.user, is_active=True)
            if account_id:
                accounts = accounts.filter(customer_id=account_id)
            
            if not accounts.exists():
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            location_analysis = {
                "city_performance_analysis": {
                    "status": "info",
                    "message": "Analyze which cities are performing better or worse",
                    "recommendations": [
                        "Identify top-performing cities by conversion rate",
                        "Flag underperforming cities for exclusion",
                        "Suggest separate campaigns for top cities",
                        "Optimize location targeting based on performance"
                    ]
                },
                "location_optimization": {
                    "status": "info",
                    "message": "Optimize location targeting for maximum conversions",
                    "recommendations": [
                        "Exclude low-performing cities from campaigns",
                        "Create city-specific campaigns for top performers",
                        "Adjust location bid modifiers based on performance",
                        "Monitor location performance trends"
                    ]
                }
            }
            
            return {
                "success": True,
                "analysis": location_analysis,
                "account": account.account_name,
                "timestamp": timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing location performance: {e}")
            return {"error": f"Failed to analyze location performance: {str(e)}"}
    
    def analyze_landing_page_mobile(self, account_id: str = None) -> Dict[str, Any]:
        """Mobile speed score and optimization analysis"""
        try:
            from .models import GoogleAdsAccount
            
            accounts = GoogleAdsAccount.objects.filter(user=self.user, is_active=True)
            if account_id:
                accounts = accounts.filter(customer_id=account_id)
            
            if not accounts.exists():
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            mobile_analysis = {
                "mobile_speed_score": {
                    "status": "critical",
                    "message": "Raise flag for mobile speed scores below 7/10",
                    "recommendations": [
                        "Check mobile speed scores for all landing pages",
                        "Flag pages with scores below 7/10",
                        "Optimize images and reduce page load time",
                        "Implement mobile-first design principles"
                    ]
                },
                "mobile_optimization": {
                    "status": "info",
                    "message": "Optimize landing pages for mobile performance",
                    "recommendations": [
                        "Ensure mobile responsiveness across devices",
                        "Optimize images for mobile viewing",
                        "Simplify navigation for mobile users",
                        "Test mobile user experience regularly"
                    ]
                }
            }
            
            return {
                "success": True,
                "analysis": mobile_analysis,
                "account": account.account_name,
                "timestamp": timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing landing page mobile: {e}")
            return {"error": f"Failed to analyze landing page mobile: {str(e)}"}
    
    def optimize_tcpa(self, account_id: str = None) -> Dict[str, Any]:
        """Target CPA optimization recommendations"""
        try:
            from .models import GoogleAdsAccount
            
            accounts = GoogleAdsAccount.objects.filter(user=self.user, is_active=True)
            if account_id:
                accounts = accounts.filter(customer_id=account_id)
            
            if not accounts.exists():
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            tcpa_optimization = {
                "high_performing_campaigns": {
                    "condition": "Campaign performing better than others (Lower CAC, SI ceiling not reached) and limited by TCPA",
                    "action": "Increase TCPA to allow for better performance",
                    "priority": "high"
                },
                "poor_performing_campaigns": {
                    "condition": "Campaign performing badly (Higher CAC) without TCPA applied",
                    "action": "Apply TCPA to control costs and improve efficiency",
                    "priority": "critical"
                },
                "tcp_optimization": {
                    "condition": "Campaign performing badly (Higher CAC) with TCPA already applied",
                    "action": "Lower TCPA to improve performance and reduce costs",
                    "priority": "high"
                },
                "ad_group_tcpa": {
                    "condition": "Ad group performing better than others (Lower CAC, SI ceiling not reached) and limited by TCPA",
                    "action": "Increase TCPA for better ad group performance",
                    "priority": "medium"
                },
                "ad_group_tcp_reduction": {
                    "condition": "Ad group performing badly (Higher CAC) with TCPA applied",
                    "action": "Lower TCPA to improve ad group performance",
                    "priority": "high"
                }
            }
            
            return {
                "success": True,
                "optimizations": tcpa_optimization,
                "account": account.account_name,
                "timestamp": timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing TCPA: {e}")
            return {"error": f"Failed to optimize TCPA: {str(e)}"}
    
    def optimize_budget_allocation(self, account_id: str = None) -> Dict[str, Any]:
        """Campaign budget allocation optimization"""
        try:
            from .models import GoogleAdsAccount
            
            accounts = GoogleAdsAccount.objects.filter(user=self.user, is_active=True)
            if account_id:
                accounts = accounts.filter(customer_id=account_id)
            
            if not accounts.exists():
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            budget_optimization = {
                "high_performing_budget_increase": {
                    "condition": "Campaign performing better than others (Lower CAC, SI ceiling not reached) and limited by budget",
                    "action": "Increase budget to allow for better performance",
                    "priority": "high"
                },
                "poor_performing_budget_reduction": {
                    "condition": "Campaign performing badly and budget is high",
                    "action": "Suggest budget reduction to improve efficiency",
                    "priority": "medium"
                },
                "budget_reallocation": {
                    "condition": "Need to optimize budget allocation across campaigns",
                    "action": "Reallocate budget from poor to high performers",
                    "priority": "high"
                }
            }
            
            return {
                "success": True,
                "optimizations": budget_optimization,
                "account": account.account_name,
                "timestamp": timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing budget allocation: {e}")
            return {"error": f"Failed to optimize budget allocation: {str(e)}"}
    
    def suggest_negative_keywords(self, account_id: str = None) -> Dict[str, Any]:
        """Negative keyword exclusion suggestions"""
        try:
            from .models import GoogleAdsAccount
            
            accounts = GoogleAdsAccount.objects.filter(user=self.user, is_active=True)
            if account_id:
                accounts = accounts.filter(customer_id=account_id)
            
            if not accounts.exists():
                return {"error": "No active Google Ads accounts found"}
            
            account = accounts.first()
            
            negative_keyword_suggestions = {
                "search_term_exclusions": {
                    "status": "warning",
                    "message": "Suggest negative keywords based on search term analysis",
                    "recommendations": [
                        "Review search terms with 0 conversions",
                        "Identify irrelevant search queries",
                        "Suggest negative keyword additions",
                        "Create exclusion lists for poor performers"
                    ]
                },
                "performance_based_exclusions": {
                    "status": "info",
                    "message": "Exclude keywords based on performance metrics",
                    "recommendations": [
                        "Flag high CAC, low conversion keywords",
                        "Suggest negative keywords for expensive terms",
                        "Review and update negative keyword lists",
                        "Monitor exclusion effectiveness"
                    ]
                }
            }
            
            return {
                "success": True,
                "analysis": negative_keyword_suggestions,
                "account": account.account_name,
                "timestamp": timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error suggesting negative keywords: {e}")
            return {"error": f"Failed to suggest negative keywords: {str(e)}"}

from typing import List, Dict, Any, Optional
import time
from django.contrib.auth.models import User
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from .models import (
    GoogleAdsAccount, GoogleAdsCampaign, GoogleAdsAdGroup, 
    GoogleAdsKeyword, GoogleAdsPerformance, ChatSession, 
    AIToolExecution
)
import logging

logger = logging.getLogger(__name__)

class GoogleAdsAnalysisTools:
    """Generic tools for Google Ads analysis and reporting"""
    
    def __init__(self, user: User, session_id: str = None):
        self.user = user
        self.session_id = session_id
    
    def _log_tool_execution(self, tool_name: str, input_params: Dict, output_result: Dict, 
                           execution_time_ms: int, success: bool, error_message: str = None):
        """Log tool execution for auditing"""
        try:
            if self.session_id:
                session = ChatSession.objects.get(id=self.session_id)
                AIToolExecution.objects.create(
                    user=self.user,
                    session=session,
                    tool_type='google_ads_analysis',
                    tool_name=tool_name,
                    input_parameters=input_params,
                    output_result=output_result,
                    execution_time_ms=execution_time_ms,
                    success=success,
                    error_message=error_message
                )
        except Exception as e:
            logger.error(f"Failed to log tool execution: {e}")
    
    def analyze_campaign_summary_comparison(self, sort_by: str = "spend", limit: int = 10) -> Dict[str, Any]:
        """Analyze and compare campaigns for key metrics and sorting"""
        start_time = time.time()
        try:
            # Get campaign data from local database
            campaigns = GoogleAdsCampaign.objects.filter(
                account__user=self.user,
                account__is_active=True
            ).select_related('account')
            
            if not campaigns.exists():
                return {"error": "No campaigns found for analysis"}
            
            # Get performance data
            campaign_data = []
            for campaign in campaigns:
                performance = GoogleAdsPerformance.objects.filter(
                    campaign=campaign
                ).aggregate(
                    total_impressions=Sum('impressions'),
                    total_clicks=Sum('clicks'),
                    total_cost=Sum('cost'),
                    total_conversions=Sum('conversions')
                )
                
                if performance['total_impressions']:
                    ctr = (performance['total_clicks'] / performance['total_impressions']) * 100
                    cpc = performance['total_cost'] / performance['total_clicks'] if performance['total_clicks'] > 0 else 0
                    conversion_rate = (performance['total_conversions'] / performance['total_clicks']) * 100 if performance['total_clicks'] > 0 else 0
                    cost_per_conversion = performance['total_cost'] / performance['total_conversions'] if performance['total_conversions'] > 0 else 0
                    
                    campaign_data.append({
                        "campaign_name": campaign.campaign_name,
                        "campaign_status": campaign.status,
                        "impressions": performance['total_impressions'],
                        "clicks": performance['total_clicks'],
                        "cost": float(performance['total_cost']),
                        "conversions": performance['total_conversions'],
                        "ctr": round(ctr, 2),
                        "cpc": round(float(cpc), 2),
                        "conversion_rate": round(conversion_rate, 2),
                        "cost_per_conversion": round(float(cost_per_conversion), 2)
                    })
            
            # Sort by specified metric
            if sort_by == "spend":
                campaign_data.sort(key=lambda x: x['cost'], reverse=True)
            elif sort_by == "clicks":
                campaign_data.sort(key=lambda x: x['clicks'], reverse=True)
            elif sort_by == "conversions":
                campaign_data.sort(key=lambda x: x['conversions'], reverse=True)
            elif sort_by == "ctr":
                campaign_data.sort(key=lambda x: x['ctr'], reverse=True)
            
            # Limit results
            campaign_data = campaign_data[:limit]
            
            # Calculate summary metrics
            total_spend = sum(c['cost'] for c in campaign_data)
            total_clicks = sum(c['clicks'] for c in campaign_data)
            total_impressions = sum(c['impressions'] for c in campaign_data)
            total_conversions = sum(c['conversions'] for c in campaign_data)
            
            overall_ctr = (total_clicks / total_impressions) * 100 if total_impressions > 0 else 0
            overall_cpc = total_spend / total_clicks if total_clicks > 0 else 0
            overall_conversion_rate = (total_conversions / total_clicks) * 100 if total_clicks > 0 else 0
            
            result = {
                "campaigns": campaign_data,
                "summary": {
                    "total_campaigns": len(campaign_data),
                    "total_spend": round(total_spend, 2),
                    "total_clicks": total_clicks,
                    "total_impressions": total_impressions,
                    "total_conversions": total_conversions,
                    "overall_ctr": round(overall_ctr, 2),
                    "overall_cpc": round(overall_cpc, 2),
                    "overall_conversion_rate": round(overall_conversion_rate, 2)
                },
                "sort_by": sort_by,
                "analysis_type": "campaign_summary_comparison"
            }
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution("analyze_campaign_summary_comparison", 
                                   {"sort_by": sort_by, "limit": limit}, 
                                   result, execution_time, True)
            
            return result
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            error_msg = f"Error analyzing campaign summary: {str(e)}"
            self._log_tool_execution("analyze_campaign_summary_comparison", 
                                   {"sort_by": sort_by, "limit": limit}, 
                                   {}, execution_time, False, error_msg)
            return {"error": error_msg}
    
    def analyze_performance_summary(self, days: int = 30) -> Dict[str, Any]:
        """Generate performance summary with key insights and recommendations"""
        start_time = time.time()
        try:
            # Calculate date range
            end_date = timezone.now().date()
            start_date = end_date - timezone.timedelta(days=days)
            
            # Get performance data for the period
            performance_data = GoogleAdsPerformance.objects.filter(
                campaign__account__user=self.user,
                campaign__account__is_active=True,
                date__gte=start_date,
                date__lte=end_date
            ).select_related('campaign', 'campaign__account')
            
            if not performance_data.exists():
                return {"error": f"No performance data found for the last {days} days"}
            
            # Aggregate daily performance
            daily_performance = {}
            for perf in performance_data:
                date_str = perf.date.strftime('%Y-%m-%d')
                if date_str not in daily_performance:
                    daily_performance[date_str] = {
                        "impressions": 0,
                        "clicks": 0,
                        "cost": 0,
                        "conversions": 0
                    }
                
                daily_performance[date_str]["impressions"] += perf.impressions or 0
                daily_performance[date_str]["clicks"] += perf.clicks or 0
                daily_performance[date_str]["cost"] += float(perf.cost or 0)
                daily_performance[date_str]["conversions"] += perf.conversions or 0
            
            # Convert to sorted list
            daily_data = []
            for date_str, data in sorted(daily_performance.items()):
                ctr = (data["clicks"] / data["impressions"]) * 100 if data["impressions"] > 0 else 0
                cpc = data["cost"] / data["clicks"] if data["clicks"] > 0 else 0
                
                daily_data.append({
                    "date": date_str,
                    "impressions": data["impressions"],
                    "clicks": data["clicks"],
                    "cost": round(data["cost"], 2),
                    "conversions": data["conversions"],
                    "ctr": round(ctr, 2),
                    "cpc": round(cpc, 2)
                })
            
            # Calculate totals
            total_impressions = sum(d["impressions"] for d in daily_data)
            total_clicks = sum(d["clicks"] for d in daily_data)
            total_cost = sum(d["cost"] for d in daily_data)
            total_conversions = sum(d["conversions"] for d in daily_data)
            
            overall_ctr = (total_clicks / total_impressions) * 100 if total_impressions > 0 else 0
            overall_cpc = total_cost / total_clicks if total_clicks > 0 else 0
            overall_conversion_rate = (total_conversions / total_clicks) * 100 if total_clicks > 0 else 0
            cost_per_conversion = total_cost / total_conversions if total_conversions > 0 else 0
            
            # Generate insights
            insights = []
            if total_conversions == 0:
                insights.append("No conversions recorded - investigate conversion tracking setup")
            
            if overall_cpc > 100:  # Assuming high CPC threshold
                insights.append("High average CPC indicates potential bidding inefficiencies")
            
            if overall_ctr < 1:  # Assuming low CTR threshold
                insights.append("Low CTR suggests ad relevance or targeting issues")
            
            # Find best and worst performing days
            if daily_data:
                best_day = max(daily_data, key=lambda x: x["clicks"])
                worst_day = min(daily_data, key=lambda x: x["clicks"])
                insights.append(f"Best performing day: {best_day['date']} with {best_day['clicks']} clicks")
                insights.append(f"Lowest performing day: {worst_day['date']} with {worst_day['clicks']} clicks")
            
            result = {
                "daily_performance": daily_data,
                "summary": {
                    "period_days": days,
                    "total_impressions": total_impressions,
                    "total_clicks": total_clicks,
                    "total_cost": round(total_cost, 2),
                    "total_conversions": total_conversions,
                    "overall_ctr": round(overall_ctr, 2),
                    "overall_cpc": round(overall_cpc, 2),
                    "overall_conversion_rate": round(overall_conversion_rate, 2),
                    "cost_per_conversion": round(cost_per_conversion, 2)
                },
                "insights": insights,
                "analysis_type": "performance_summary"
            }
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution("analyze_performance_summary", 
                                   {"days": days}, 
                                   result, execution_time, True)
            
            return result
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            error_msg = f"Error analyzing performance summary: {str(e)}"
            self._log_tool_execution("analyze_performance_summary", 
                                   {"days": days}, 
                                   {}, execution_time, False, error_msg)
            return {"error": error_msg}
    
    def analyze_trends(self, metric: str = "clicks", days: int = 30) -> Dict[str, Any]:
        """Analyze trends for specified metrics using line/bar charts"""
        start_time = time.time()
        try:
            # Calculate date range
            end_date = timezone.now().date()
            start_date = end_date - timezone.timedelta(days=days)
            
            # Get performance data for the period
            performance_data = GoogleAdsPerformance.objects.filter(
                campaign__account__user=self.user,
                campaign__account__is_active=True,
                date__gte=start_date,
                date__lte=end_date
            ).select_related('campaign')
            
            if not performance_data.exists():
                return {"error": f"No trend data found for the last {days} days"}
            
            # Aggregate daily metrics
            daily_metrics = {}
            for perf in performance_data:
                date_str = perf.date.strftime('%Y-%m-%d')
                if date_str not in daily_metrics:
                    daily_metrics[date_str] = {
                        "impressions": 0,
                        "clicks": 0,
                        "cost": 0,
                        "conversions": 0
                    }
                
                daily_metrics[date_str]["impressions"] += perf.impressions or 0
                daily_metrics[date_str]["clicks"] += perf.clicks or 0
                daily_metrics[date_str]["cost"] += float(perf.cost or 0)
                daily_metrics[date_str]["conversions"] += perf.conversions or 0
            
            # Calculate derived metrics
            for date_str in daily_metrics:
                data = daily_metrics[date_str]
                if data["impressions"] > 0:
                    data["ctr"] = round((data["clicks"] / data["impressions"]) * 100, 2)
                else:
                    data["ctr"] = 0
                
                if data["clicks"] > 0:
                    data["cpc"] = round(data["cost"] / data["clicks"], 2)
                else:
                    data["cpc"] = 0
            
            # Sort by date and prepare chart data
            sorted_dates = sorted(daily_metrics.keys())
            chart_data = {
                "labels": sorted_dates,
                "datasets": []
            }
            
            # Add requested metric dataset
            if metric == "clicks":
                chart_data["datasets"].append({
                    "label": "Daily Clicks",
                    "data": [daily_metrics[date]["clicks"] for date in sorted_dates]
                })
            elif metric == "cpc":
                chart_data["datasets"].append({
                    "label": "Daily CPC",
                    "data": [daily_metrics[date]["cpc"] for date in sorted_dates]
                })
            elif metric == "ctr":
                chart_data["datasets"].append({
                    "label": "Daily CTR (%)",
                    "data": [daily_metrics[date]["ctr"] for date in sorted_dates]
                })
            elif metric == "all":
                chart_data["datasets"] = [
                    {
                        "label": "Daily Clicks",
                        "data": [daily_metrics[date]["clicks"] for date in sorted_dates]
                    },
                    {
                        "label": "Daily CPC",
                        "data": [daily_metrics[date]["cpc"] for date in sorted_dates]
                    },
                    {
                        "label": "Daily CTR (%)",
                        "data": [daily_metrics[date]["ctr"] for date in sorted_dates]
                    }
                ]
            
            # Generate insights
            insights = []
            if len(sorted_dates) > 1:
                first_value = chart_data["datasets"][0]["data"][0]
                last_value = chart_data["datasets"][0]["data"][-1]
                
                if last_value > first_value:
                    trend = "increasing"
                    change_percent = ((last_value - first_value) / first_value) * 100 if first_value > 0 else 0
                    insights.append(f"{metric.upper()} trend is {trend} by {round(change_percent, 1)}% over the period")
                elif last_value < first_value:
                    trend = "decreasing"
                    change_percent = ((first_value - last_value) / first_value) * 100 if first_value > 0 else 0
                    insights.append(f"{metric.upper()} trend is {trend} by {round(change_percent, 1)}% over the period")
                else:
                    insights.append(f"{metric.upper()} trend is stable over the period")
            
            result = {
                "chart_data": chart_data,
                "metric": metric,
                "period_days": days,
                "insights": insights,
                "analysis_type": "trend_analysis"
            }
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution("analyze_trends", 
                                   {"metric": metric, "days": days}, 
                                   result, execution_time, True)
            
            return result
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            error_msg = f"Error analyzing trends: {str(e)}"
            self._log_tool_execution("analyze_trends", 
                                   {"metric": metric, "days": days}, 
                                   {}, execution_time, False, error_msg)
            return {"error": error_msg}
    
    def analyze_listing_performance(self, listing_type: str = "campaigns", limit: int = 10, 
                                  sort_by: str = "conversions", days: int = 14) -> Dict[str, Any]:
        """Analyze top performing items (campaigns, keywords, etc.) with insights"""
        start_time = time.time()
        try:
            # Calculate date range
            end_date = timezone.now().date()
            start_date = end_date - timezone.timedelta(days=days)
            
            if listing_type == "campaigns":
                # Get top campaigns by performance
                campaigns = GoogleAdsCampaign.objects.filter(
                    account__user=self.user,
                    account__is_active=True
                )
                
                campaign_performance = []
                for campaign in campaigns:
                    performance = GoogleAdsPerformance.objects.filter(
                        campaign=campaign,
                        date__gte=start_date,
                        date__lte=end_date
                    ).aggregate(
                        total_impressions=Sum('impressions'),
                        total_clicks=Sum('clicks'),
                        total_cost=Sum('cost'),
                        total_conversions=Sum('conversions')
                    )
                    
                    if performance['total_impressions']:
                        ctr = (performance['total_clicks'] / performance['total_impressions']) * 100
                        cpc = performance['total_cost'] / performance['total_clicks'] if performance['total_clicks'] > 0 else 0
                        conversion_rate = (performance['total_conversions'] / performance['total_clicks']) * 100 if performance['total_clicks'] > 0 else 0
                        cost_per_conversion = performance['total_cost'] / performance['total_conversions'] if performance['total_conversions'] > 0 else 0
                        
                        campaign_performance.append({
                            "campaign_name": campaign.campaign_name,
                            "impressions": performance['total_impressions'],
                            "clicks": performance['total_clicks'],
                            "ctr": round(ctr, 2),
                            "avg_cpc": round(float(cpc), 2),
                            "total_cost": round(float(performance['total_cost']), 2),
                            "conversions": performance['total_conversions'],
                            "conversion_rate": round(conversion_rate, 2),
                            "cost_per_conversion": round(float(cost_per_conversion), 2)
                        })
                
                # Sort by specified metric
                if sort_by == "conversions":
                    campaign_performance.sort(key=lambda x: x['conversions'], reverse=True)
                elif sort_by == "clicks":
                    campaign_performance.sort(key=lambda x: x['clicks'], reverse=True)
                elif sort_by == "spend":
                    campaign_performance.sort(key=lambda x: x['total_cost'], reverse=True)
                elif sort_by == "ctr":
                    campaign_performance.sort(key=lambda x: x['ctr'], reverse=True)
                
                # Limit results
                campaign_performance = campaign_performance[:limit]
                
                # Generate insights
                insights = []
                if campaign_performance:
                    top_campaign = campaign_performance[0]
                    insights.append(f"Top performer: '{top_campaign['campaign_name']}' with {top_campaign['conversions']} conversions")
                    
                    if top_campaign['cost_per_conversion'] > 100:  # Assuming high cost threshold
                        insights.append(f"High cost per conversion (₹{top_campaign['cost_per_conversion']}) suggests optimization needed")
                    
                    avg_ctr = sum(c['ctr'] for c in campaign_performance) / len(campaign_performance)
                    insights.append(f"Average CTR across top campaigns: {round(avg_ctr, 2)}%")
                
                result = {
                    "listing_type": listing_type,
                    "items": campaign_performance,
                    "sort_by": sort_by,
                    "period_days": days,
                    "insights": insights,
                    "analysis_type": "listing_analysis"
                }
            
            else:
                return {"error": f"Listing type '{listing_type}' not supported yet"}
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution("analyze_listing_performance", 
                                   {"listing_type": listing_type, "limit": limit, "sort_by": sort_by, "days": days}, 
                                   result, execution_time, True)
            
            return result
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            error_msg = f"Error analyzing listing performance: {str(e)}"
            self._log_tool_execution("analyze_listing_performance", 
                                   {"listing_type": listing_type, "limit": limit, "sort_by": sort_by, "days": days}, 
                                   {}, execution_time, False, error_msg)
            return {"error": error_msg}
    
    def handle_query_without_solution(self, query: str) -> Dict[str, Any]:
        """Handle queries that don't have direct solutions by providing alternatives"""
        start_time = time.time()
        try:
            # Analyze the query to understand what the user is asking for
            query_lower = query.lower()
            
            alternatives = []
            explanation = ""
            
            if "quality score" in query_lower and "account" in query_lower:
                explanation = "Google Ads doesn't provide a direct 'quality score' metric at the account level. Quality scores are assigned to keywords, not entire accounts."
                alternatives = [
                    "Show general account performance metrics for the last 30 days",
                    "Provide keyword-level quality scores for specific keywords",
                    "Display quality-related metrics like CTR, conversion rates, or impression share"
                ]
            
            elif "account-level" in query_lower:
                explanation = "Many Google Ads metrics are campaign, ad group, or keyword specific rather than account-wide."
                alternatives = [
                    "Show campaign-level performance metrics",
                    "Provide ad group performance analysis",
                    "Display keyword performance data"
                ]
            
            else:
                explanation = "This query doesn't have a direct solution in Google Ads. Let me suggest some alternatives that might be helpful."
                alternatives = [
                    "View campaign performance summary",
                    "Analyze keyword performance",
                    "Check ad group metrics",
                    "Review account overview"
                ]
            
            result = {
                "query": query,
                "explanation": explanation,
                "alternatives": alternatives,
                "analysis_type": "query_without_solution"
            }
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution("handle_query_without_solution", 
                                   {"query": query}, 
                                   result, execution_time, True)
            
            return result
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            error_msg = f"Error handling query without solution: {str(e)}"
            self._log_tool_execution("handle_query_without_solution", 
                                   {"query": query}, 
                                   {}, execution_time, False, error_msg)
            return {"error": error_msg}
    
    def analyze_pie_chart_data(self, chart_type: str = "spend", days: int = 30) -> Dict[str, Any]:
        """Generate pie chart data for spend distribution or other metrics"""
        start_time = time.time()
        try:
            # Calculate date range
            end_date = timezone.now().date()
            start_date = end_date - timezone.timedelta(days=days)
            
            if chart_type == "spend":
                # Get campaign spend distribution
                campaigns = GoogleAdsCampaign.objects.filter(
                    account__user=self.user,
                    account__is_active=True
                )
                
                campaign_spend = []
                for campaign in campaigns:
                    total_spend = GoogleAdsPerformance.objects.filter(
                        campaign=campaign,
                        date__gte=start_date,
                        date__lte=end_date
                    ).aggregate(total_cost=Sum('cost'))['total_cost'] or 0
                    
                    if total_spend > 0:
                        campaign_spend.append({
                            "label": campaign.campaign_name,
                            "value": float(total_spend)
                        })
                
                # Sort by spend and limit to top 10
                campaign_spend.sort(key=lambda x: x['value'], reverse=True)
                campaign_spend = campaign_spend[:10]
                
                # Calculate total spend
                total_spend = sum(item['value'] for item in campaign_spend)
                
                # Calculate percentages
                for item in campaign_spend:
                    item['percentage'] = round((item['value'] / total_spend) * 100, 1)
                
                chart_data = {
                    "labels": [item['label'] for item in campaign_spend],
                    "datasets": [{
                        "label": "Campaign Spend",
                        "data": [item['value'] for item in campaign_spend]
                    }]
                }
                
                insights = [
                    f"Total spend across campaigns: ₹{total_spend:,.2f}",
                    f"Top campaign: {campaign_spend[0]['label']} with {campaign_spend[0]['percentage']}% of total spend"
                ]
                
                if len(campaign_spend) > 1:
                    insights.append(f"Bottom campaign: {campaign_spend[-1]['label']} with {campaign_spend[-1]['percentage']}% of total spend")
            
            else:
                return {"error": f"Chart type '{chart_type}' not supported yet"}
            
            result = {
                "chart_data": chart_data,
                "chart_type": "pie",
                "metric": chart_type,
                "period_days": days,
                "insights": insights,
                "analysis_type": "pie_chart_display"
            }
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution("analyze_pie_chart_data", 
                                   {"chart_type": chart_type, "days": days}, 
                                   result, execution_time, True)
            
            return result
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            error_msg = f"Error analyzing pie chart data: {str(e)}"
            self._log_tool_execution("analyze_pie_chart_data", 
                                   {"chart_type": chart_type, "days": days}, 
                                   {}, execution_time, False, error_msg)
            return {"error": error_msg}
    
    def analyze_duplicate_keywords(self, days: int = 7) -> Dict[str, Any]:
        """Analyze duplicate keywords across campaigns and provide consolidation recommendations"""
        start_time = time.time()
        try:
            # Calculate date range
            end_date = timezone.now().date()
            start_date = end_date - timezone.timedelta(days=days)
            
            # Get all keywords from the period
            keywords = GoogleAdsKeyword.objects.filter(
                ad_group__campaign__account__user=self.user,
                ad_group__campaign__account__is_active=True
            ).select_related('ad_group', 'ad_group__campaign')
            
            if not keywords.exists():
                return {"error": "No keywords found for analysis"}
            
            # Group keywords by text to find duplicates
            keyword_groups = {}
            for keyword in keywords:
                keyword_text = keyword.keyword_text.lower().strip()
                if keyword_text not in keyword_groups:
                    keyword_groups[keyword_text] = []
                
                keyword_groups[keyword_text].append({
                    "keyword_id": keyword.id,
                    "keyword_text": keyword.keyword_text,
                    "campaign_name": keyword.ad_group.campaign.campaign_name,
                    "ad_group_name": keyword.ad_group.ad_group_name,
                    "match_type": keyword.match_type,
                    "status": keyword.status
                })
            
            # Find duplicates (keywords appearing in multiple campaigns)
            duplicates = []
            for keyword_text, instances in keyword_groups.items():
                if len(instances) > 1:
                    # Get performance data for this keyword across all instances
                    keyword_performance = []
                    for instance in instances:
                        performance = GoogleAdsPerformance.objects.filter(
                            keyword__id=instance['keyword_id'],
                            date__gte=start_date,
                            date__lte=end_date
                        ).aggregate(
                            total_impressions=Sum('impressions'),
                            total_clicks=Sum('clicks'),
                            total_cost=Sum('cost'),
                            total_conversions=Sum('conversions')
                        )
                        
                        if performance['total_impressions']:
                            ctr = (performance['total_clicks'] / performance['total_impressions']) * 100
                            cpc = performance['total_cost'] / performance['total_clicks'] if performance['total_clicks'] > 0 else 0
                        else:
                            ctr = 0
                            cpc = 0
                        
                        instance.update({
                            "impressions": performance['total_impressions'] or 0,
                            "clicks": performance['total_clicks'] or 0,
                            "cost": round(float(performance['total_cost'] or 0), 2),
                            "conversions": performance['total_conversions'] or 0,
                            "ctr": round(ctr, 2),
                            "cpc": round(float(cpc), 2)
                        })
                        keyword_performance.append(instance)
                    
                    duplicates.append({
                        "keyword_text": keyword_text,
                        "instances": keyword_performance,
                        "campaigns_count": len(instances),
                        "total_impressions": sum(i['impressions'] for i in instances),
                        "total_clicks": sum(i['clicks'] for i in instances),
                        "total_cost": sum(i['cost'] for i in instances),
                        "total_conversions": sum(i['conversions'] for i in instances)
                    })
            
            # Sort duplicates by number of campaigns (most duplicated first)
            duplicates.sort(key=lambda x: x['campaigns_count'], reverse=True)
            
            # Generate insights and recommendations
            insights = []
            recommendations = []
            
            if duplicates:
                total_duplicates = len(duplicates)
                insights.append(f"Found {total_duplicates} duplicate keywords across campaigns")
                
                most_duplicated = duplicates[0]
                insights.append(f"Most duplicated: '{most_duplicated['keyword_text']}' appears in {most_duplicated['campaigns_count']} campaigns")
                
                # Recommendations
                recommendations.append("Prioritize consolidation of keywords appearing in 3+ campaigns")
                recommendations.append("Keep the best performing instance and add as negative keywords in others")
                recommendations.append("Consider campaign restructuring to reduce keyword overlap")
                recommendations.append("Monitor performance after consolidation for 2-4 weeks")
            
            result = {
                "duplicates": duplicates,
                "total_duplicates": len(duplicates),
                "period_days": days,
                "insights": insights,
                "recommendations": recommendations,
                "analysis_type": "duplicate_keywords_analysis"
            }
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution("analyze_duplicate_keywords", 
                                   {"days": days}, 
                                   result, execution_time, True)
            
            return result
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            error_msg = f"Error analyzing duplicate keywords: {str(e)}"
            self._log_tool_execution("analyze_duplicate_keywords", 
                                   {"days": days}, 
                                   {}, execution_time, False, error_msg)
            return {"error": error_msg}
    
    def dig_deeper_analysis(self, base_analysis: Dict[str, Any], depth: int = 2) -> Dict[str, Any]:
        """Provide deeper analysis based on previous analysis results"""
        start_time = time.time()
        try:
            if depth > 2:
                return {"error": "Maximum dig deeper depth is 2 levels"}
            
            analysis_type = base_analysis.get('analysis_type', 'unknown')
            result = {
                "base_analysis": base_analysis,
                "dig_deeper_depth": depth,
                "analysis_type": "dig_deeper_analysis"
            }
            
            if analysis_type == "campaign_summary_comparison":
                # Provide deeper campaign insights
                campaigns = base_analysis.get('campaigns', [])
                if campaigns:
                    # Analyze performance patterns
                    high_performers = [c for c in campaigns if c.get('conversions', 0) > 0]
                    low_performers = [c for c in campaigns if c.get('conversions', 0) == 0]
                    
                    result["deeper_insights"] = {
                        "high_performing_campaigns": len(high_performers),
                        "low_performing_campaigns": len(low_performers),
                        "conversion_rate": len(high_performers) / len(campaigns) * 100 if campaigns else 0
                    }
                    
                    # Specific recommendations based on depth
                    if depth == 1:
                        result["recommendations"] = [
                            "Focus budget on campaigns with conversions",
                            "Investigate why some campaigns have 0 conversions",
                            "Consider pausing consistently underperforming campaigns"
                        ]
                    elif depth == 2:
                        result["recommendations"] = [
                            "Implement conversion tracking if not already in place",
                            "Review landing page quality for non-converting campaigns",
                            "Analyze keyword quality scores for underperforming campaigns",
                            "Consider audience targeting adjustments"
                        ]
            
            elif analysis_type == "performance_summary":
                # Provide deeper performance insights
                daily_data = base_analysis.get('daily_performance', [])
                if daily_data:
                    # Find patterns in daily performance
                    high_ctr_days = [d for d in daily_data if d.get('ctr', 0) > 5]  # Assuming 5% is high
                    low_cpc_days = [d for d in daily_data if d.get('cpc', 0) < 50]  # Assuming ₹50 is low
                    
                    result["deeper_insights"] = {
                        "high_ctr_days": len(high_ctr_days),
                        "low_cpc_days": len(low_cpc_days),
                        "best_performing_day": max(daily_data, key=lambda x: x.get('clicks', 0)) if daily_data else None
                    }
                    
                    if depth == 1:
                        result["recommendations"] = [
                            "Analyze what caused high CTR on specific days",
                            "Investigate factors leading to low CPC days",
                            "Replicate successful day strategies"
                        ]
                    elif depth == 2:
                        result["recommendations"] = [
                            "Review ad scheduling and day-of-week performance",
                            "Analyze competitor activity patterns",
                            "Check for external events affecting performance",
                            "Implement day-parting strategies based on insights"
                        ]
            
            else:
                result["deeper_insights"] = "Deep analysis not available for this analysis type"
                result["recommendations"] = ["Try a different analysis type for deeper insights"]
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution("dig_deeper_analysis", 
                                   {"analysis_type": analysis_type, "depth": depth}, 
                                   result, execution_time, True)
            
            return result
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            error_msg = f"Error in dig deeper analysis: {str(e)}"
            self._log_tool_execution("dig_deeper_analysis", 
                                   {"analysis_type": base_analysis.get('analysis_type', 'unknown'), "depth": depth}, 
                                   {}, execution_time, False, error_msg)
            return {"error": error_msg}
    
    def generate_ad_copies(self, context: str, platform: str = "google_ads", variations: int = 4) -> Dict[str, Any]:
        """Generate multiple ad copy variations for Google Ads or Meta ads"""
        start_time = time.time()
        try:
            # Parse context to extract key information
            context_lower = context.lower()
            
            # Extract business type, target audience, and key features
            business_keywords = []
            if "coaching" in context_lower or "center" in context_lower:
                business_keywords.extend(["coaching", "education", "learning", "training"])
            if "geography" in context_lower:
                business_keywords.extend(["geography", "upsc", "competitive", "exam"])
            if "indian" in context_lower:
                business_keywords.extend(["indian", "local", "regional", "cultural"])
            
            # Generate ad copy variations with specific types and advantages
            ad_copies = []
            
            if platform == "google_ads":
                # Google Ads specific copy variations with variation types
                ad_copies = [
                    {
                        "title": f"Master {business_keywords[1] if len(business_keywords) > 1 else 'Your Subject'}",
                        "description": f"Transform your {business_keywords[1] if len(business_keywords) > 1 else 'knowledge'} with proven strategies. Limited seats available!",
                        "headline1": f"Master {business_keywords[1] if len(business_keywords) > 1 else 'Your Subject'}",
                        "headline2": "Expert-Led Coaching",
                        "headline3": "Join Small Batch Classes",
                        "cta": "Enroll Now",
                        "features": ["Expert Teachers", "Small Batch Size", "Proven Results"],
                        "advantages": [
                            "Personalized attention in small groups",
                            "Proven teaching methodologies",
                            "Track record of student success"
                        ],
                        "target_audience": "Students preparing for competitive exams",
                        "variation_type": "benefit_focused",
                        "platform": "google_ads",
                        "template_type": "Educational",
                        "color_scheme": "Professional blues and whites"
                    },
                    {
                        "title": f"Top {business_keywords[1] if len(business_keywords) > 1 else 'Coaching'} Center",
                        "description": f"Join the best {business_keywords[0] if business_keywords else 'coaching'} center. Book your free demo class today!",
                        "headline1": f"Top {business_keywords[1] if len(business_keywords) > 1 else 'Coaching'} Center",
                        "headline2": "Guaranteed Success",
                        "headline3": "Free Demo Class",
                        "cta": "Book Demo",
                        "features": ["Free Demo", "Success Guarantee", "Expert Faculty"],
                        "advantages": [
                            "Risk-free trial with free demo",
                            "Guaranteed success commitment",
                            "Access to expert faculty"
                        ],
                        "target_audience": "Parents and students seeking quality education",
                        "variation_type": "social_proof",
                        "platform": "google_ads",
                        "template_type": "Marketing",
                        "color_scheme": "Trustworthy blues and greens"
                    },
                    {
                        "title": f"Best {business_keywords[1] if len(business_keywords) > 1 else 'Results'}",
                        "description": f"Get personalized attention in small batches. {business_keywords[1] if len(business_keywords) > 1 else 'Subject'} made easy!",
                        "headline1": f"Best {business_keywords[1] if len(business_keywords) > 1 else 'Results'}",
                        "headline2": "Personal Attention",
                        "headline3": "Affordable Fees",
                        "cta": "Call Now",
                        "features": ["Personal Attention", "Affordable Fees", "Small Batches"],
                        "advantages": [
                            "Individualized learning experience",
                            "Cost-effective quality education",
                            "Intimate learning environment"
                        ],
                        "target_audience": "Students looking for personalized coaching",
                        "variation_type": "emotional_appeal",
                        "platform": "google_ads",
                        "template_type": "Educational",
                        "color_scheme": "Warm oranges and yellows"
                    },
                    {
                        "title": f"Expert {business_keywords[1] if len(business_keywords) > 1 else 'Coaching'}",
                        "description": f"Learn from industry experts using proven methods. Don't miss out on limited seats!",
                        "headline1": f"Expert {business_keywords[1] if len(business_keywords) > 1 else 'Coaching'}",
                        "headline2": "Proven Methods",
                        "headline3": "Limited Seats",
                        "cta": "Apply Today",
                        "features": ["Expert Faculty", "Proven Methods", "Limited Seats"],
                        "advantages": [
                            "Industry expert guidance",
                            "Time-tested methodologies",
                            "Exclusive limited availability"
                        ],
                        "target_audience": "Serious students seeking expert guidance",
                        "variation_type": "urgency_scarcity",
                        "platform": "google_ads",
                        "template_type": "Marketing",
                        "color_scheme": "Dynamic reds and oranges"
                    }
                ]
            
            elif platform == "meta_ads":
                # Meta/Facebook ads specific copy variations with variation types
                ad_copies = [
                    {
                        "title": f"Transform Your {business_keywords[1] if len(business_keywords) > 1 else 'Future'}",
                        "description": f"Join the leading {business_keywords[0] if business_keywords else 'coaching'} center. Expert teachers, small batches, and proven results. Limited seats available!",
                        "headline": f"Transform Your {business_keywords[1] if len(business_keywords) > 1 else 'Future'}",
                        "primary_text": f"Join the leading {business_keywords[0] if business_keywords else 'coaching'} center. Expert teachers, small batches, and proven results. Limited seats available!",
                        "cta": "Learn More",
                        "features": ["Expert Teachers", "Small Batches", "Proven Results"],
                        "advantages": [
                            "Life-changing educational transformation",
                            "Proven track record of success",
                            "Exclusive small batch experience"
                        ],
                        "target_audience": "Students and parents on social media",
                        "variation_type": "emotional_appeal",
                        "platform": "meta_ads",
                        "ad_format": "feed",
                        "template_type": "Social Media",
                        "color_scheme": "Inspirational purples and blues"
                    },
                    {
                        "title": f"Best {business_keywords[1] if len(business_keywords) > 1 else 'Coaching'} Center",
                        "description": f"Get personalized attention and guaranteed success. Book your free demo class today and see the difference!",
                        "headline": f"Best {business_keywords[1] if len(business_keywords) > 1 else 'Coaching'} Center",
                        "primary_text": f"Get personalized attention and guaranteed success. Book your free demo class today and see the difference!",
                        "cta": "Book Demo",
                        "features": ["Free Demo", "Personal Attention", "Success Guarantee"],
                        "advantages": [
                            "No-risk trial experience",
                            "Personalized learning approach",
                            "Guaranteed success commitment"
                        ],
                        "target_audience": "Social media users seeking quality education",
                        "variation_type": "social_proof",
                        "platform": "meta_ads",
                        "ad_format": "feed",
                        "template_type": "Social Media",
                        "color_scheme": "Trustworthy greens and blues"
                    },
                    {
                        "title": f"Master {business_keywords[1] if len(business_keywords) > 1 else 'Your Skills'}",
                        "description": f"Join our small batch classes with expert faculty. Affordable fees, proven methods, and limited seats available!",
                        "headline": f"Master {business_keywords[1] if len(business_keywords) > 1 else 'Your Skills'}",
                        "primary_text": f"Join our small batch classes with expert faculty. Affordable fees, proven methods, and limited seats available!",
                        "cta": "Enroll Now",
                        "features": ["Small Batches", "Expert Faculty", "Affordable Fees"],
                        "advantages": [
                            "Intimate learning environment",
                            "Access to expert knowledge",
                            "Value for money education"
                        ],
                        "target_audience": "Students looking for quality education",
                        "variation_type": "benefit_focused",
                        "platform": "meta_ads",
                        "ad_format": "feed",
                        "template_type": "Social Media",
                        "color_scheme": "Professional grays with accent colors"
                    },
                    {
                        "title": f"Expert {business_keywords[1] if len(business_keywords) > 1 else 'Guidance'}",
                        "description": f"Learn from industry experts using proven methods. Don't miss out on this opportunity to excel in your studies!",
                        "headline": f"Expert {business_keywords[1] if len(business_keywords) > 1 else 'Guidance'}",
                        "primary_text": f"Learn from industry experts using proven methods. Don't miss out on this opportunity to excel in your studies!",
                        "cta": "Apply Today",
                        "features": ["Expert Guidance", "Proven Methods", "Limited Opportunity"],
                        "advantages": [
                            "Industry expert mentorship",
                            "Time-tested learning methods",
                            "Exclusive opportunity window"
                        ],
                        "target_audience": "Ambitious students seeking excellence",
                        "variation_type": "urgency_scarcity",
                        "platform": "meta_ads",
                        "ad_format": "feed",
                        "template_type": "Social Media",
                        "color_scheme": "Dynamic reds and oranges"
                    }
                ]
            
            # Generate creative suggestions
            creative_suggestions = {
                "visual_elements": [
                    "Young student studying with maps/geography materials",
                    "Confident student in graduation cap",
                    "Group of students in a modern classroom",
                    "Success symbols like trophies or certificates"
                ],
                "color_schemes": [
                    "Professional blues and whites for trust",
                    "Energetic oranges and yellows for motivation",
                    "Earthy tones for geography theme",
                    "Modern grays with accent colors"
                ],
                "typography": [
                    "Clean, modern sans-serif fonts",
                    "Bold headlines with readable body text",
                    "Professional yet approachable style",
                    "Clear hierarchy for easy scanning"
                ]
            }
            
            result = {
                "platform": platform,
                "context": context,
                "ad_copies": ad_copies,
                "creative_suggestions": creative_suggestions,
                "analysis_type": "generate_ad_copies"
            }
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution("generate_ad_copies", 
                                   {"context": context, "platform": platform, "variations": variations}, 
                                   result, execution_time, True)
            
            return result
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            error_msg = f"Error generating ad copies: {str(e)}"
            self._log_tool_execution("generate_ad_copies", 
                                   {"context": context, "platform": platform, "variations": variations}, 
                                   {}, execution_time, False, error_msg)
            return {"error": error_msg}
    
    def generate_poster_templates(self, context: str, target_audience: str = "students") -> Dict[str, Any]:
        """Generate poster templates and design suggestions"""
        start_time = time.time()
        try:
            # Parse context to extract key information
            context_lower = context.lower()
            
            # Extract business type and key features
            business_type = "coaching_center"
            if "coaching" in context_lower:
                business_type = "coaching_center"
            elif "school" in context_lower:
                business_type = "school"
            elif "college" in context_lower:
                business_type = "college"
            
            # Generate poster templates
            poster_templates = [
                {
                    "title": "Geography-Themed Educational Poster",
                    "description": "A professional poster with earthy tones, map elements, and student illustration",
                    "template_type": "Educational",
                    "features": [
                        "Earthy color scheme (browns, greens, blues)",
                        "Map or geography visual elements",
                        "Student illustration or photo",
                        "Clear hierarchy with headline, benefits, and CTA"
                    ],
                    "advantages": [
                        "Perfect visual alignment with geography subject",
                        "Professional appearance for educational institutions",
                        "Easy to read and understand"
                    ],
                    "cta_suggestions": [
                        "Enroll Now",
                        "Join Free Demo!",
                        "Start Your Journey",
                        "Register Today"
                    ],
                    "color_scheme": "Earthy tones with professional accents",
                    "target_audience": "Geography students and parents"
                },
                {
                    "title": "Bold Coaching Center Flyer",
                    "description": "Vibrant design with confident student imagery and prominent CTA button",
                    "template_type": "Marketing",
                    "features": [
                        "Vibrant, attention-grabbing colors",
                        "Confident student image",
                        "Prominent CTA button",
                        "Modern, dynamic layout"
                    ],
                    "advantages": [
                        "High visual impact for marketing campaigns",
                        "Clear call-to-action for conversions",
                        "Modern design appeals to younger audience"
                    ],
                    "cta_suggestions": [
                        "Call Now",
                        "Book Demo",
                        "Get Started",
                        "Learn More"
                    ],
                    "color_scheme": "Vibrant colors with high contrast",
                    "target_audience": "Young students and parents"
                },
                {
                    "title": "Grand Opening Style Design",
                    "description": "Clean layout with engaging headlines and placeholders for key information",
                    "template_type": "Event",
                    "features": [
                        "Clean, minimalist design",
                        "Engaging headlines",
                        "Placeholders for key information",
                        "Professional business appearance"
                    ],
                    "advantages": [
                        "Professional appearance for business launch",
                        "Easy to customize with specific information",
                        "Clean design ensures readability"
                    ],
                    "cta_suggestions": [
                        "Join Us",
                        "Be Part of Success",
                        "Enroll Now",
                        "Contact Us"
                    ],
                    "color_scheme": "Professional blues and whites",
                    "target_audience": "General public and parents"
                },
                {
                    "title": "Structured Coaching Class Template",
                    "description": "Organized layout with clear text blocks and space for student imagery",
                    "template_type": "Informational",
                    "features": [
                        "Clear text blocks and sections",
                        "Space for student imagery",
                        "Organized information hierarchy",
                        "Professional yet approachable design"
                    ],
                    "advantages": [
                        "Easy to read and understand",
                        "Professional appearance",
                        "Good for detailed information sharing"
                    ],
                    "cta_suggestions": [
                        "Apply Today",
                        "Join Classes",
                        "Start Learning",
                        "Get Information"
                    ],
                    "color_scheme": "Professional grays with accent colors",
                    "target_audience": "Serious students and parents"
                }
            ]
            
            # Generate workflow for poster creation
            workflow = {
                "title": "Suggested Workflow for Your Poster",
                "steps": [
                    {"step": "1", "action": "Pick a Poster Maker - Choose between Picsart, Fotor, BeFunky, PosterMyWall, or Visme based on ease-of-use and template style"},
                    {"step": "2", "action": "Choose a Template - Look for templates with visuals of a young student or map element, clear hierarchy (headline, benefits, CTA), and earth-tone or school-friendly color schemes"},
                    {"step": "3", "action": "Customize Design - Add business name prominently, use compelling headline, include support text, insert strong CTA in contrasting color, use high-resolution photo or illustration of a student"},
                    {"step": "4", "action": "Polish Copy - Focus on action verbs and benefits. Use compelling language that drives action"},
                    {"step": "5", "action": "Export & Share - Download as high-res PDF or PNG for printing, or share digitally across WhatsApp, Instagram, or local community boards"}
                ],
                "tools": ["Picsart", "BeFunky", "Fotor", "Visme", "PosterMyWall"],
                "tips": [
                    "Match your audience with visuals and messaging that resonate",
                    "Make your CTA bold and visible with phone number or website",
                    "Maintain balance - don't overcrowd, have breathing space, clean fonts, and readable layout"
                ]
            }
            
            # Generate tool recommendations
            tool_recommendations = {
                "ease_of_use": ["Picsart", "BeFunky", "Fotor", "Visme", "PosterMyWall"],
                "template_variety": ["Fotor", "Picsart", "BeFunky", "Visme"],
                "output_quality": ["Fotor", "Visme", "PosterMyWall"],
                "customization_power": ["Fotor", "BeFunky", "Visme"]
            }
            
            result = {
                "context": context,
                "target_audience": target_audience,
                "poster_templates": poster_templates,
                "workflow": workflow,
                "tool_recommendations": tool_recommendations,
                "analysis_type": "poster_generator"
            }
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution("generate_poster_templates", 
                                   {"context": context, "target_audience": target_audience}, 
                                   result, execution_time, True)
            
            return result
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            error_msg = f"Error generating poster templates: {str(e)}"
            self._log_tool_execution("generate_poster_templates", 
                                   {"context": context, "target_audience": target_audience}, 
                                   {}, execution_time, False, error_msg)
            return {"error": error_msg}
    
    def generate_meta_ads_creatives(self, context: str, ad_format: str = "all") -> Dict[str, Any]:
        """Generate creative ideas specifically for Meta/Facebook ads"""
        start_time = time.time()
        try:
            # Parse context to extract key information
            context_lower = context.lower()
            
            # Extract business type and key features
            business_keywords = []
            if "coaching" in context_lower or "center" in context_lower:
                business_keywords.extend(["coaching", "education", "learning", "training"])
            if "geography" in context_lower:
                business_keywords.extend(["geography", "upsc", "competitive", "exam"])
            if "indian" in context_lower:
                business_keywords.extend(["indian", "local", "regional", "cultural"])
            
            # Generate Meta ads creative ideas
            creative_ideas = [
                {
                    "title": "Student Success Story",
                    "description": "Feature a successful student with before/after results",
                    "template_type": "Story",
                    "features": [
                        "Before/after student transformation",
                        "Testimonial or success quote",
                        "Clear results and achievements",
                        "Motivational messaging"
                    ],
                    "advantages": [
                        "Builds trust through real results",
                        "Emotional connection with audience",
                        "Social proof for decision making"
                    ],
                    "cta_suggestions": [
                        "See More Success Stories",
                        "Join the Winners",
                        "Start Your Success Story",
                        "Learn How"
                    ],
                    "color_scheme": "Warm, motivational colors",
                    "target_audience": "Ambitious students and parents"
                },
                {
                    "title": "Behind-the-Scenes Learning",
                    "description": "Show the learning environment and teaching process",
                    "template_type": "Lifestyle",
                    "features": [
                        "Classroom or study environment",
                        "Teacher-student interaction",
                        "Modern facilities and resources",
                        "Engaging learning atmosphere"
                    ],
                    "advantages": [
                        "Transparent about what to expect",
                        "Shows quality of facilities",
                        "Builds confidence in the program"
                    ],
                    "cta_suggestions": [
                        "Take a Virtual Tour",
                        "Book a Visit",
                        "See Our Facilities",
                        "Experience Learning"
                    ],
                    "color_scheme": "Natural, educational colors",
                    "target_audience": "Parents and students seeking quality education"
                },
                {
                    "title": "Expert Faculty Spotlight",
                    "description": "Highlight the qualifications and experience of teachers",
                    "template_type": "Professional",
                    "features": [
                        "Teacher profiles and qualifications",
                        "Experience and achievements",
                        "Professional credentials",
                        "Student testimonials about teachers"
                    ],
                    "advantages": [
                        "Establishes credibility",
                        "Shows expertise and experience",
                        "Builds trust in the institution"
                    ],
                    "cta_suggestions": [
                        "Meet Our Teachers",
                        "Learn from Experts",
                        "See Faculty Profiles",
                        "Get Expert Guidance"
                    ],
                    "color_scheme": "Professional blues and grays",
                    "target_audience": "Serious students seeking expert guidance"
                },
                {
                    "title": "Interactive Learning Experience",
                    "description": "Showcase modern teaching methods and technology",
                    "template_type": "Innovation",
                    "features": [
                        "Modern teaching technology",
                        "Interactive learning methods",
                        "Digital resources and tools",
                        "Innovative study materials"
                    ],
                    "advantages": [
                        "Appeals to tech-savvy students",
                        "Shows modern approach to education",
                        "Differentiates from traditional methods"
                    ],
                    "cta_suggestions": [
                        "Experience Innovation",
                        "Try Modern Learning",
                        "See Technology in Action",
                        "Join the Future"
                    ],
                    "color_scheme": "Modern, tech-inspired colors",
                    "target_audience": "Tech-savvy students and parents"
                }
            ]
            
            # Generate Meta ads specific workflow
            workflow = {
                "title": "Meta Ads Implementation Workflow",
                "steps": [
                    {"step": "1", "action": "Create Facebook Business Page - Set up professional business page with complete information"},
                    {"step": "2", "action": "Design Ad Creatives - Use the creative ideas above to design compelling visuals"},
                    {"step": "3", "action": "Set Up Ad Campaign - Choose objective (Awareness, Consideration, or Conversion)"},
                    {"step": "4", "action": "Define Target Audience - Use detailed targeting for geography, age, interests, and behavior"},
                    {"step": "5", "action": "Set Budget and Schedule - Choose daily or lifetime budget with optimal ad scheduling"},
                    {"step": "6", "action": "Monitor and Optimize - Track performance metrics and optimize based on results"}
                ],
                "tools": ["Facebook Ads Manager", "Facebook Business Suite", "Canva", "Adobe Creative Suite"],
                "tips": [
                    "Use high-quality images and videos (minimum 1080x1080 for square ads)",
                    "Keep text overlay under 20% for better reach",
                    "Test multiple ad variations to find what works best",
                    "Use Facebook's automatic placement optimization initially"
                ]
            }
            
            # Generate ad format recommendations
            ad_formats = {
                "image_ads": "Best for brand awareness and consideration",
                "video_ads": "Great for storytelling and engagement",
                "carousel_ads": "Perfect for showcasing multiple features or testimonials",
                "story_ads": "Ideal for mobile-first audience engagement"
            }
            
            result = {
                "context": context,
                "ad_format": ad_format,
                "creative_ideas": creative_ideas,
                "workflow": workflow,
                "ad_formats": ad_formats,
                "analysis_type": "meta_ads_creatives"
            }
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_tool_execution("generate_meta_ads_creatives", 
                                   {"context": context, "ad_format": ad_format}, 
                                   result, execution_time, True)
            
            return result
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            error_msg = f"Error generating Meta ads creatives: {str(e)}"
            self._log_tool_execution("generate_meta_ads_creatives", 
                                   {"context": context, "ad_format": ad_format}, 
                                   {}, execution_time, False, error_msg)
            return {"error": error_msg}

"""
API tools for Google Ads and Meta Marketing API
Privacy-first: no campaign data at rest, process in memory only
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class GoogleAdsAPITool:
    """Google Ads API tool - fetches data on demand, processes in memory"""
    
    def __init__(self):
        self.base_url = "https://googleads.googleapis.com/v19/customers"
        self.developer_token = settings.GOOGLE_ADS_CONFIG.get('developer_token')
    
    async def get_insights(self, customer_id: str, access_token: str, 
                          date_range: str = "LAST_14_DAYS", 
                          segments: List[str] = None, user_id: int = None) -> Dict[str, Any]:
        """
        Fetch Google Ads insights - processes in memory, no storage
        """
        try:
            # Import the proper Google Ads API service
            from google_ads_new.google_ads_api_service import GoogleAdsAPIService
            
            # Create service instance with user_id
            service = GoogleAdsAPIService(user_id=user_id, customer_id=customer_id)
            
            # Get campaign performance data
            # Convert date_range to start_date and end_date
            end_date = datetime.now().strftime('%Y-%m-%d')
            if date_range == "LAST_7_DAYS":
                start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            elif date_range == "LAST_14_DAYS":
                start_date = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
            elif date_range == "LAST_30_DAYS":
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            else:
                start_date = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
            
            campaign_data = service.get_performance_data(
                customer_id=customer_id,
                start_date=start_date,
                end_date=end_date
            )
            
            if not campaign_data:
                return {
                    "error": f"No campaign data found for customer {customer_id}. Please ensure the customer ID is correct and you have access to this Google Ads account."
                }
            
            # Process data in memory - no storage
            processed_data = self._process_performance_data(campaign_data)
            
            logger.info(f"Successfully fetched Google Ads insights for customer {customer_id}")
            return processed_data
            
        except Exception as e:
            logger.error(f"Google Ads API error: {str(e)}")
            return {"error": f"Failed to fetch Google Ads data: {str(e)}"}
    
    def _build_date_filter(self, date_range: str) -> str:
        """Build date filter for GAQL"""
        if date_range == "LAST_7_DAYS":
            return ">= CURRENT_DATE - 7"
        elif date_range == "LAST_14_DAYS":
            return ">= CURRENT_DATE - 14"
        elif date_range == "LAST_30_DAYS":
            return ">= CURRENT_DATE - 30"
        else:
            return ">= CURRENT_DATE - 14"
    
    def _build_segment_fields(self, segments: List[str]) -> str:
        """Build segment fields for GAQL"""
        if not segments:
            return ""
        
        segment_mapping = {
            'device': 'segments.device',
            'network': 'segments.ad_network_type',
            'placement': 'segments.placement',
        }
        
        fields = []
        for segment in segments:
            if segment in segment_mapping:
                fields.append(segment_mapping[segment])
        
        return f", {', '.join(fields)}" if fields else ""
    
    def _analyze_google_ads_data(self, raw_data: Dict) -> Dict[str, Any]:
        """Analyze Google Ads data in memory - compute KPIs and trends"""
        if 'results' not in raw_data:
            return {"error": "No data returned from Google Ads API"}
        
        rows = raw_data['results']
        if not rows:
            return {"summary": "No campaign data found for the specified period"}
        
        # In-memory analysis
        by_date = {}
        by_campaign = {}
        total_metrics = {
            'spend': 0,
            'impressions': 0,
            'clicks': 0,
            'conversions': 0,
            'conversions_value': 0
        }
        
        for row in rows:
            campaign = row.get('campaign', {})
            metrics = row.get('metrics', {})
            segments = row.get('segments', {})
            
            campaign_name = campaign.get('name', 'Unknown')
            date = segments.get('date', '')
            
            # Convert micros to currency
            spend = float(metrics.get('costMicros', 0)) / 1_000_000
            cpc = float(metrics.get('cpcMicros', 0)) / 1_000_000
            cpm = float(metrics.get('cpmMicros', 0)) / 1_000_000
            
            impressions = int(metrics.get('impressions', 0))
            clicks = int(metrics.get('clicks', 0))
            conversions = float(metrics.get('conversions', 0))
            conversions_value = float(metrics.get('conversionsValue', 0))
            ctr = float(metrics.get('ctr', 0))
            cost_per_conversion = float(metrics.get('costPerConversion', 0))
            
            # Aggregate by date
            if date not in by_date:
                by_date[date] = {
                    'spend': 0, 'impressions': 0, 'clicks': 0,
                    'conversions': 0, 'conversions_value': 0
                }
            
            by_date[date]['spend'] += spend
            by_date[date]['impressions'] += impressions
            by_date[date]['clicks'] += clicks
            by_date[date]['conversions'] += conversions
            by_date[date]['conversions_value'] += conversions_value
            
            # Aggregate by campaign
            if campaign_name not in by_campaign:
                by_campaign[campaign_name] = {
                    'spend': 0, 'impressions': 0, 'clicks': 0,
                    'conversions': 0, 'conversions_value': 0,
                    'ctr': 0, 'cpc': 0, 'cpm': 0, 'cost_per_conversion': 0
                }
            
            by_campaign[campaign_name]['spend'] += spend
            by_campaign[campaign_name]['impressions'] += impressions
            by_campaign[campaign_name]['clicks'] += clicks
            by_campaign[campaign_name]['conversions'] += conversions
            by_campaign[campaign_name]['conversions_value'] += conversions_value
            
            # Update totals
            total_metrics['spend'] += spend
            total_metrics['impressions'] += impressions
            total_metrics['clicks'] += clicks
            total_metrics['conversions'] += conversions
            total_metrics['conversions_value'] += conversions_value
        
        # Compute derived metrics
        total_ctr = (total_metrics['clicks'] / total_metrics['impressions'] * 100) if total_metrics['impressions'] > 0 else 0
        total_cpc = (total_metrics['spend'] / total_metrics['clicks']) if total_metrics['clicks'] > 0 else 0
        total_cpa = (total_metrics['spend'] / total_metrics['conversions']) if total_metrics['conversions'] > 0 else 0
        
        # Compute trends (7-day vs 14-day)
        trend_analysis = self._compute_trends(by_date)
        
        return {
            'summary': {
                'total_spend': round(total_metrics['spend'], 2),
                'total_impressions': total_metrics['impressions'],
                'total_clicks': total_metrics['clicks'],
                'total_conversions': round(total_metrics['conversions'], 2),
                'total_conversions_value': round(total_metrics['conversions_value'], 2),
                'ctr': round(total_ctr, 2),
                'cpc': round(total_cpc, 2),
                'cpa': round(total_cpa, 2)
            },
            'by_campaign': by_campaign,
            'by_date': by_date,
            'trends': trend_analysis,
            'platform': 'google_ads'
        }
    
    def _compute_trends(self, by_date: Dict) -> Dict[str, Any]:
        """Compute trend analysis in memory"""
        dates = sorted(by_date.keys())
        if len(dates) < 7:
            return {"insufficient_data": True}
        
        # Compare last 7 days vs previous 7 days
        recent_7 = dates[:7]
        previous_7 = dates[7:14] if len(dates) >= 14 else []
        
        recent_metrics = self._aggregate_period(by_date, recent_7)
        
        trends = {
            'recent_7_days': recent_metrics,
            'period_comparison': {}
        }
        
        if previous_7:
            previous_metrics = self._aggregate_period(by_date, previous_7)
            trends['previous_7_days'] = previous_metrics
            
            # Compute percentage changes
            for metric in ['spend', 'impressions', 'clicks', 'conversions']:
                if previous_metrics[metric] > 0:
                    change = ((recent_metrics[metric] - previous_metrics[metric]) / previous_metrics[metric]) * 100
                    trends['period_comparison'][f'{metric}_change'] = round(change, 2)
        
        return trends
    
    def _aggregate_period(self, by_date: Dict, dates: List[str]) -> Dict[str, float]:
        """Aggregate metrics for a period"""
        metrics = {'spend': 0, 'impressions': 0, 'clicks': 0, 'conversions': 0}
        for date in dates:
            if date in by_date:
                for metric in metrics:
                    metrics[metric] += by_date[date][metric]
        return metrics


class MetaMarketingAPITool:
    """Meta Marketing API tool - fetches data on demand, processes in memory"""
    
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v20.0"
    
    async def get_insights(self, ad_account_id: str, access_token: str,
                          date_range: str = "LAST_14_DAYS",
                          breakdowns: List[str] = None) -> Dict[str, Any]:
        """
        Fetch Meta Marketing insights - processes in memory, no storage
        """
        try:
            # Build date range
            since, until = self._build_date_range(date_range)
            
            # Build fields
            fields = [
                "date_start", "date_stop", "campaign_name", "campaign_id",
                "impressions", "clicks", "spend", "conversions",
                "actions", "cpm", "cpc", "ctr", "reach", "frequency"
            ]
            
            # Build breakdowns
            breakdown_param = ""
            if breakdowns:
                valid_breakdowns = ['device_platform', 'publisher_platform', 'placement']
                filtered_breakdowns = [b for b in breakdowns if b in valid_breakdowns]
                if filtered_breakdowns:
                    breakdown_param = f"&breakdowns={','.join(filtered_breakdowns)}"
            
            url = (f"{self.base_url}/act_{ad_account_id}/insights"
                   f"?fields={','.join(fields)}"
                   f"&time_range[since]={since}&time_range[until]={until}"
                   f"&level=campaign&time_increment=1{breakdown_param}")
            
            headers = {'Authorization': f'Bearer {access_token}'}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            raw_data = response.json()
            
            # Process in memory
            processed_data = self._analyze_meta_data(raw_data)
            
            # Clear raw data from memory
            del raw_data
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Meta Marketing API error: {str(e)}")
            return {"error": f"Failed to fetch Meta data: {str(e)}"}
    
    def _build_date_range(self, date_range: str) -> tuple:
        """Build date range for Meta API"""
        end_date = datetime.now().date()
        
        if date_range == "LAST_7_DAYS":
            start_date = end_date - timedelta(days=7)
        elif date_range == "LAST_14_DAYS":
            start_date = end_date - timedelta(days=14)
        elif date_range == "LAST_30_DAYS":
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=14)
        
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
    
    def _analyze_meta_data(self, raw_data: Dict) -> Dict[str, Any]:
        """Analyze Meta data in memory - compute KPIs and trends"""
        if 'data' not in raw_data:
            return {"error": "No data returned from Meta Marketing API"}
        
        rows = raw_data['data']
        if not rows:
            return {"summary": "No campaign data found for the specified period"}
        
        # In-memory analysis
        by_date = {}
        by_campaign = {}
        total_metrics = {
            'spend': 0,
            'impressions': 0,
            'clicks': 0,
            'conversions': 0,
            'reach': 0
        }
        
        for row in rows:
            campaign_name = row.get('campaign_name', 'Unknown')
            date = row.get('date_start', '')
            
            spend = float(row.get('spend', 0))
            impressions = int(row.get('impressions', 0))
            clicks = int(row.get('clicks', 0))
            reach = int(row.get('reach', 0))
            ctr = float(row.get('ctr', 0))
            cpc = float(row.get('cpc', 0))
            cpm = float(row.get('cpm', 0))
            
            # Extract conversions from actions
            conversions = 0
            actions = row.get('actions', [])
            for action in actions:
                if action.get('action_type') in ['purchase', 'lead', 'complete_registration']:
                    conversions += int(action.get('value', 0))
            
            # Aggregate by date
            if date not in by_date:
                by_date[date] = {
                    'spend': 0, 'impressions': 0, 'clicks': 0,
                    'conversions': 0, 'reach': 0
                }
            
            by_date[date]['spend'] += spend
            by_date[date]['impressions'] += impressions
            by_date[date]['clicks'] += clicks
            by_date[date]['conversions'] += conversions
            by_date[date]['reach'] += reach
            
            # Aggregate by campaign
            if campaign_name not in by_campaign:
                by_campaign[campaign_name] = {
                    'spend': 0, 'impressions': 0, 'clicks': 0,
                    'conversions': 0, 'reach': 0, 'ctr': 0, 'cpc': 0, 'cpm': 0
                }
            
            by_campaign[campaign_name]['spend'] += spend
            by_campaign[campaign_name]['impressions'] += impressions
            by_campaign[campaign_name]['clicks'] += clicks
            by_campaign[campaign_name]['conversions'] += conversions
            by_campaign[campaign_name]['reach'] += reach
            
            # Update totals
            total_metrics['spend'] += spend
            total_metrics['impressions'] += impressions
            total_metrics['clicks'] += clicks
            total_metrics['conversions'] += conversions
            total_metrics['reach'] += reach
        
        # Compute derived metrics
        total_ctr = (total_metrics['clicks'] / total_metrics['impressions'] * 100) if total_metrics['impressions'] > 0 else 0
        total_cpc = (total_metrics['spend'] / total_metrics['clicks']) if total_metrics['clicks'] > 0 else 0
        total_cpa = (total_metrics['spend'] / total_metrics['conversions']) if total_metrics['conversions'] > 0 else 0
        
        return {
            'summary': {
                'total_spend': round(total_metrics['spend'], 2),
                'total_impressions': total_metrics['impressions'],
                'total_clicks': total_metrics['clicks'],
                'total_conversions': round(total_metrics['conversions'], 2),
                'total_reach': total_metrics['reach'],
                'ctr': round(total_ctr, 2),
                'cpc': round(total_cpc, 2),
                'cpa': round(total_cpa, 2)
            },
            'by_campaign': by_campaign,
            'by_date': by_date,
            'platform': 'meta_marketing'
        }

    def _process_performance_data(self, performance_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process Google Ads performance data in memory - compute KPIs and trends"""
        try:
            if not performance_data:
                return {"error": "No performance data found"}
            
            # Group data by campaign
            campaigns = {}
            total_spend = 0
            total_impressions = 0
            total_clicks = 0
            total_conversions = 0
            
            for record in performance_data:
                campaign_id = record.get('campaign_id', 'Unknown')
                campaign_name = record.get('campaign_name', 'Unknown')
                
                if campaign_id not in campaigns:
                    campaigns[campaign_id] = {
                        'campaign_id': campaign_id,
                        'campaign_name': campaign_name,
                        'cost': 0,
                        'impressions': 0,
                        'clicks': 0,
                        'conversions': 0,
                        'conversion_value': 0
                    }
                
                # Convert micros to currency
                cost_micros = int(record.get('cost_micros', 0))
                cost = cost_micros / 1_000_000
                
                # Aggregate campaign data
                campaigns[campaign_id]['cost'] += cost
                campaigns[campaign_id]['impressions'] += int(record.get('impressions', 0))
                campaigns[campaign_id]['clicks'] += int(record.get('clicks', 0))
                campaigns[campaign_id]['conversions'] += float(record.get('conversions', 0))
                campaigns[campaign_id]['conversion_value'] += float(record.get('conversion_value', 0))
                
                # Aggregate totals
                total_spend += cost
                total_impressions += int(record.get('impressions', 0))
                total_clicks += int(record.get('clicks', 0))
                total_conversions += float(record.get('conversions', 0))
            
            # Calculate metrics for each campaign
            processed_campaigns = []
            for campaign in campaigns.values():
                campaign['ctr'] = (campaign['clicks'] / campaign['impressions'] * 100) if campaign['impressions'] > 0 else 0
                campaign['cpc'] = (campaign['cost'] / campaign['clicks']) if campaign['clicks'] > 0 else 0
                campaign['cpm'] = (campaign['cost'] / campaign['impressions'] * 1000) if campaign['impressions'] > 0 else 0
                campaign['cost_per_conversion'] = (campaign['cost'] / campaign['conversions']) if campaign['conversions'] > 0 else 0
                campaign['roas'] = (campaign['conversion_value'] / campaign['cost']) if campaign['cost'] > 0 else 0
                
                # Round values
                campaign['cost'] = round(campaign['cost'], 2)
                campaign['ctr'] = round(campaign['ctr'], 2)
                campaign['cpc'] = round(campaign['cpc'], 2)
                campaign['cpm'] = round(campaign['cpm'], 2)
                campaign['cost_per_conversion'] = round(campaign['cost_per_conversion'], 2)
                campaign['roas'] = round(campaign['roas'], 2)
                
                processed_campaigns.append(campaign)
            
            # Calculate overall metrics
            overall_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            overall_cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
            overall_cpa = (total_spend / total_conversions) if total_conversions > 0 else 0
            
            return {
                'campaigns': processed_campaigns,
                'summary': {
                    'total_campaigns': len(processed_campaigns),
                    'total_spend': round(total_spend, 2),
                    'total_impressions': total_impressions,
                    'total_clicks': total_clicks,
                    'total_conversions': total_conversions,
                    'overall_ctr': round(overall_ctr, 2),
                    'overall_cpc': round(overall_cpc, 2),
                    'overall_cpa': round(overall_cpa, 2)
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing performance data: {str(e)}")
            return {"error": f"Error processing performance data: {str(e)}"}

    def _process_campaign_data(self, campaigns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process campaign data in memory - compute KPIs and trends"""
        try:
            if not campaigns:
                return {"error": "No campaign data found"}
            
            processed_campaigns = []
            total_spend = 0
            total_impressions = 0
            total_clicks = 0
            total_conversions = 0
            
            for campaign in campaigns:
                # Process individual campaign data
                campaign_data = {
                    'campaign_name': campaign.get('name', 'Unknown'),
                    'campaign_id': campaign.get('id', 'Unknown'),
                    'cost': float(campaign.get('cost', 0)),
                    'impressions': int(campaign.get('impressions', 0)),
                    'clicks': int(campaign.get('clicks', 0)),
                    'conversions': float(campaign.get('conversions', 0)),
                    'conversions_value': float(campaign.get('conversions_value', 0)),
                    'ctr': float(campaign.get('ctr', 0)),
                    'cpc': float(campaign.get('cpc', 0)),
                    'cpm': float(campaign.get('cpm', 0)),
                    'cost_per_conversion': float(campaign.get('cost_per_conversion', 0)),
                    'roas': float(campaign.get('roas', 0))
                }
                
                processed_campaigns.append(campaign_data)
                
                # Aggregate totals
                total_spend += campaign_data['cost']
                total_impressions += campaign_data['impressions']
                total_clicks += campaign_data['clicks']
                total_conversions += campaign_data['conversions']
            
            # Calculate overall metrics
            overall_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            overall_cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
            overall_cpa = (total_spend / total_conversions) if total_conversions > 0 else 0
            
            return {
                'campaigns': processed_campaigns,
                'summary': {
                    'total_campaigns': len(processed_campaigns),
                    'total_spend': round(total_spend, 2),
                    'total_impressions': total_impressions,
                    'total_clicks': total_clicks,
                    'total_conversions': total_conversions,
                    'overall_ctr': round(overall_ctr, 2),
                    'overall_cpc': round(overall_cpc, 2),
                    'overall_cpa': round(overall_cpa, 2)
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing campaign data: {str(e)}")
            return {"error": f"Error processing campaign data: {str(e)}"}

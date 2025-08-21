import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.utils import timezone
from django.db import models
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from .models import (
    GoogleAdsAccount, GoogleAdsCampaign, GoogleAdsAdGroup,
    GoogleAdsKeyword, GoogleAdsPerformance
)

logger = logging.getLogger(__name__)


class GoogleAdsService:
    """Service class for Google Ads API operations"""
    
    def __init__(self, customer_id: str = None):
        self.customer_id = customer_id
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google Ads client"""
        try:
            config = settings.GOOGLE_ADS_CONFIG
            self.client = GoogleAdsClient.load_from_dict({
                'developer_token': config['developer_token'],
                'client_id': config['client_id'],
                'client_secret': config['client_secret'],
                'refresh_token': config['refresh_token'],
                'login_customer_id': config['login_customer_id'],
                'use_proto_plus': True,
            })
            logger.info("Google Ads client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Ads client: {e}")
            raise
    
    def get_customer_info(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get customer information from Google Ads"""
        try:
            customer_service = self.client.get_service("CustomerService")
            customer = customer_service.get_customer(
                resource_name=f"customers/{customer_id}"
            )
            
            return {
                'customer_id': customer.id,
                'descriptive_name': customer.descriptive_name,
                'currency_code': customer.currency_code,
                'time_zone': customer.time_zone,
                'manager': customer.manager,
                'test_account': customer.test_account,
            }
        except GoogleAdsException as e:
            logger.error(f"Failed to get customer info: {e}")
            return None
    
    def list_campaigns(self, customer_id: str) -> List[Dict[str, Any]]:
        """List all campaigns for a customer"""
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            query = """
                SELECT 
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    campaign.advertising_channel_type,
                    campaign.start_date,
                    campaign.end_date,
                    campaign_budget.amount_micros,
                    campaign_budget.delivery_method
                FROM campaign
                WHERE campaign.status != 'REMOVED'
                ORDER BY campaign.name
            """
            
            campaigns = []
            for row in ga_service.search(
                customer_id=customer_id,
                query=query
            ):
                campaign = row.campaign
                budget = row.campaign_budget
                
                campaigns.append({
                    'campaign_id': campaign.id,
                    'campaign_name': campaign.name,
                    'status': campaign.status.name,
                    'type': campaign.advertising_channel_type.name,
                    'start_date': campaign.start_date,
                    'end_date': campaign.end_date,
                    'budget_amount': budget.amount_micros / 1000000 if budget.amount_micros else None,
                    'budget_type': budget.delivery_method.name,
                })
            
            return campaigns
        except GoogleAdsException as e:
            logger.error(f"Failed to list campaigns: {e}")
            return []
    
    def list_ad_groups(self, customer_id: str, campaign_id: str = None) -> List[Dict[str, Any]]:
        """List ad groups for a customer or specific campaign"""
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            if campaign_id:
                query = f"""
                    SELECT 
                        ad_group.id,
                        ad_group.name,
                        ad_group.status,
                        ad_group.type,
                        campaign.id
                    FROM ad_group
                    WHERE campaign.id = {campaign_id}
                    AND ad_group.status != 'REMOVED'
                    ORDER BY ad_group.name
                """
            else:
                query = """
                    SELECT 
                        ad_group.id,
                        ad_group.name,
                        ad_group.status,
                        ad_group.type,
                        campaign.id
                    FROM ad_group
                    WHERE ad_group.status != 'REMOVED'
                    ORDER BY ad_group.name
                """
            
            ad_groups = []
            for row in ga_service.search(
                customer_id=customer_id,
                query=query
            ):
                ad_group = row.ad_group
                campaign = row.campaign
                
                ad_groups.append({
                    'ad_group_id': ad_group.id,
                    'ad_group_name': ad_group.name,
                    'status': ad_group.status.name,
                    'type': ad_group.type.name,
                    'campaign_id': campaign.id,
                })
            
            return ad_groups
        except GoogleAdsException as e:
            logger.error(f"Failed to list ad groups: {e}")
            return []
    
    def list_keywords(self, customer_id: str, ad_group_id: str = None) -> List[Dict[str, Any]]:
        """List keywords for a customer or specific ad group"""
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            if ad_group_id:
                query = f"""
                    SELECT 
                        ad_group_criterion.criterion_id,
                        ad_group_criterion.keyword.text,
                        ad_group_criterion.keyword.match_type,
                        ad_group_criterion.status,
                        ad_group_criterion.quality_info.quality_score,
                        ad_group.id
                    FROM ad_group_criterion
                    WHERE ad_group.id = {ad_group_id}
                    AND ad_group_criterion.type = 'KEYWORD'
                    AND ad_group_criterion.status != 'REMOVED'
                    ORDER BY ad_group_criterion.keyword.text
                """
            else:
                query = """
                    SELECT 
                        ad_group_criterion.criterion_id,
                        ad_group_criterion.keyword.text,
                        ad_group_criterion.keyword.match_type,
                        ad_group_criterion.status,
                        ad_group_criterion.quality_info.quality_score,
                        ad_group.id
                    FROM ad_group_criterion
                    WHERE ad_group_criterion.type = 'KEYWORD'
                    AND ad_group_criterion.status != 'REMOVED'
                    ORDER BY ad_group_criterion.keyword.text
                """
            
            keywords = []
            for row in ga_service.search(
                customer_id=customer_id,
                query=query
            ):
                criterion = row.ad_group_criterion
                keyword = criterion.keyword
                ad_group = row.ad_group
                quality_info = criterion.quality_info
                
                keywords.append({
                    'keyword_id': criterion.criterion_id,
                    'keyword_text': keyword.text,
                    'match_type': keyword.match_type.name,
                    'status': criterion.status.name,
                    'quality_score': quality_info.quality_score if quality_info.quality_score else None,
                    'ad_group_id': ad_group.id,
                })
            
            return keywords
        except GoogleAdsException as e:
            logger.error(f"Failed to list keywords: {e}")
            return []
    
    def get_performance_data(self, customer_id: str, start_date: str, end_date: str,
                           campaign_id: str = None, ad_group_id: str = None,
                           keyword_id: str = None) -> List[Dict[str, Any]]:
        """Get performance data for specified criteria"""
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            # Build query based on filters
            select_fields = [
                'customer.id',
                'campaign.id',
                'ad_group.id',
                'ad_group_criterion.criterion_id',
                'segments.date',
                'metrics.impressions',
                'metrics.clicks',
                'metrics.cost_micros',
                'metrics.conversions',
                'metrics.conversions_value'
            ]
            
            where_clauses = [
                'segments.date >= %s' % start_date,
                'segments.date <= %s' % end_date
            ]
            
            if campaign_id:
                where_clauses.append('campaign.id = %s' % campaign_id)
            if ad_group_id:
                where_clauses.append('ad_group.id = %s' % ad_group_id)
            if keyword_id:
                where_clauses.append('ad_group_criterion.criterion_id = %s' % keyword_id)
            
            query = f"""
                SELECT {', '.join(select_fields)}
                FROM customer
                WHERE {' AND '.join(where_clauses)}
                ORDER BY segments.date DESC
            """
            
            performance_data = []
            for row in ga_service.search(
                customer_id=customer_id,
                query=query
            ):
                customer = row.customer
                campaign = row.campaign
                ad_group = row.ad_group
                criterion = row.ad_group_criterion
                segments = row.segments
                metrics = row.metrics
                
                performance_data.append({
                    'customer_id': customer.id,
                    'campaign_id': campaign.id if campaign.id else None,
                    'ad_group_id': ad_group.id if ad_group.id else None,
                    'keyword_id': criterion.criterion_id if criterion.criterion_id else None,
                    'date': segments.date,
                    'impressions': metrics.impressions,
                    'clicks': metrics.clicks,
                    'cost_micros': metrics.cost_micros,
                    'conversions': metrics.conversions,
                    'conversion_value': metrics.conversions_value,
                })
            
            return performance_data
        except GoogleAdsException as e:
            logger.error(f"Failed to get performance data: {e}")
            return []
    
    def create_campaign(self, customer_id: str, campaign_data: Dict[str, Any]) -> Optional[str]:
        """Create a new campaign"""
        try:
            campaign_service = self.client.get_service("CampaignService")
            campaign_budget_service = self.client.get_service("CampaignBudgetService")
            
            # Create campaign budget first
            budget_operation = campaign_budget_service.create_campaign_budget({
                'name': f"Budget for {campaign_data['name']}",
                'amount_micros': int(campaign_data['budget_amount'] * 1000000),
                'delivery_method': campaign_data.get('budget_type', 'STANDARD'),
            })
            
            budget_resource_name = budget_operation.result.resource_name
            
            # Create campaign
            campaign_operation = campaign_service.create_campaign({
                'name': campaign_data['name'],
                'status': campaign_data.get('status', 'ENABLED'),
                'advertising_channel_type': campaign_data['type'],
                'start_date': campaign_data['start_date'],
                'campaign_budget': budget_resource_name,
            })
            
            return campaign_operation.result.resource_name
        except GoogleAdsException as e:
            logger.error(f"Failed to create campaign: {e}")
            return None
    
    def update_campaign_status(self, customer_id: str, campaign_id: str, status: str) -> bool:
        """Update campaign status"""
        try:
            campaign_service = self.client.get_service("CampaignService")
            
            campaign_service.update_campaign({
                'resource_name': f"customers/{customer_id}/campaigns/{campaign_id}",
                'status': status,
            })
            
            return True
        except GoogleAdsException as e:
            logger.error(f"Failed to update campaign status: {e}")
            return False
    
    def sync_account_data(self, customer_id: str, user_id: int) -> Dict[str, Any]:
        """Sync all account data from Google Ads"""
        try:
            # Get customer info
            customer_info = self.get_customer_info(customer_id)
            if not customer_info:
                return {'success': False, 'error': 'Failed to get customer info'}
            
            # Create or update account
            account, created = GoogleAdsAccount.objects.get_or_create(
                customer_id=customer_id,
                defaults={
                    'user_id': user_id,
                    'account_name': customer_info['descriptive_name'],
                    'currency_code': customer_info['currency_code'],
                    'time_zone': customer_info['time_zone'],
                }
            )
            
            if not created:
                account.account_name = customer_info['descriptive_name']
                account.currency_code = customer_info['currency_code']
                account.time_zone = customer_info['time_zone']
                account.save()
            
            # Sync campaigns
            campaigns_data = self.list_campaigns(customer_id)
            campaigns_synced = 0
            
            for campaign_data in campaigns_data:
                campaign, created = GoogleAdsCampaign.objects.get_or_create(
                    account=account,
                    campaign_id=campaign_data['campaign_id'],
                    defaults={
                        'campaign_name': campaign_data['campaign_name'],
                        'campaign_status': campaign_data['status'],
                        'campaign_type': campaign_data['type'],
                        'start_date': campaign_data['start_date'],
                        'end_date': campaign_data['end_date'],
                        'budget_amount': campaign_data['budget_amount'],
                        'budget_type': campaign_data['budget_type'],
                    }
                )
                
                if not created:
                    campaign.campaign_name = campaign_data['campaign_name']
                    campaign.campaign_status = campaign_data['status']
                    campaign.campaign_type = campaign_data['type']
                    campaign.start_date = campaign_data['start_date']
                    campaign.end_date = campaign_data['end_date']
                    campaign.budget_amount = campaign_data['budget_amount']
                    campaign.budget_type = campaign_data['budget_type']
                    campaign.save()
                
                campaigns_synced += 1
                
                # Sync ad groups for this campaign
                ad_groups_data = self.list_ad_groups(customer_id, campaign_data['campaign_id'])
                for ad_group_data in ad_groups_data:
                    ad_group, created = GoogleAdsAdGroup.objects.get_or_create(
                        campaign=campaign,
                        ad_group_id=ad_group_data['ad_group_id'],
                        defaults={
                            'ad_group_name': ad_group_data['ad_group_name'],
                            'status': ad_group_data['status'],
                            'type': ad_group_data['type'],
                        }
                    )
                    
                    if not created:
                        ad_group.ad_group_name = ad_group_data['ad_group_name']
                        ad_group.status = ad_group_data['status']
                        ad_group.type = ad_group_data['type']
                        ad_group.save()
                    
                    # Sync keywords for this ad group
                    keywords_data = self.list_keywords(customer_id, ad_group_data['ad_group_id'])
                    for keyword_data in keywords_data:
                        keyword, created = GoogleAdsKeyword.objects.get_or_create(
                            ad_group=ad_group,
                            keyword_id=keyword_data['keyword_id'],
                            defaults={
                                'keyword_text': keyword_data['keyword_text'],
                                'match_type': keyword_data['match_type'],
                                'status': keyword_data['status'],
                                'quality_score': keyword_data['quality_score'],
                            }
                        )
                        
                        if not created:
                            keyword.keyword_text = keyword_data['keyword_text']
                            keyword.match_type = keyword_data['match_type']
                            keyword.status = keyword_data['status']
                            keyword.quality_score = keyword_data['quality_score']
                            keyword.save()
            
            # Sync performance data for last 30 days
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
            
            performance_data = self.get_performance_data(
                customer_id,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            
            performance_synced = 0
            for perf_data in performance_data:
                # Get related objects
                try:
                    campaign = GoogleAdsCampaign.objects.get(
                        account=account,
                        campaign_id=perf_data['campaign_id']
                    ) if perf_data['campaign_id'] else None
                    
                    ad_group = GoogleAdsAdGroup.objects.get(
                        campaign=campaign,
                        ad_group_id=perf_data['ad_group_id']
                    ) if perf_data['ad_group_id'] and campaign else None
                    
                    keyword = GoogleAdsKeyword.objects.get(
                        ad_group=ad_group,
                        keyword_id=perf_data['keyword_id']
                    ) if perf_data['keyword_id'] and ad_group else None
                    
                    # Create or update performance record
                    performance, created = GoogleAdsPerformance.objects.get_or_create(
                        account=account,
                        date=perf_data['date'],
                        campaign=campaign,
                        ad_group=ad_group,
                        keyword=keyword,
                        defaults={
                            'impressions': perf_data['impressions'],
                            'clicks': perf_data['clicks'],
                            'cost_micros': perf_data['cost_micros'],
                            'conversions': perf_data['conversions'],
                            'conversion_value': perf_data['conversion_value'],
                        }
                    )
                    
                    if not created:
                        performance.impressions = perf_data['impressions']
                        performance.clicks = perf_data['clicks']
                        performance.cost_micros = perf_data['cost_micros']
                        performance.conversions = perf_data['conversions']
                        performance.conversion_value = perf_data['conversion_value']
                        performance.save()
                    
                    performance_synced += 1
                except Exception as e:
                    logger.warning(f"Failed to sync performance data: {e}")
                    continue
            
            return {
                'success': True,
                'account_synced': True,
                'campaigns_synced': campaigns_synced,
                'performance_synced': performance_synced,
                'message': f"Successfully synced {campaigns_synced} campaigns and {performance_synced} performance records"
            }
            
        except Exception as e:
            logger.error(f"Failed to sync account data: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_dashboard_metrics(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get dashboard metrics for a user"""
        try:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days)
            
            # Get user's accounts
            accounts = GoogleAdsAccount.objects.filter(user_id=user_id, is_active=True)
            
            if not accounts.exists():
                return {
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
                    'top_keywords': []
                }
            
            # Aggregate performance data
            performance_data = GoogleAdsPerformance.objects.filter(
                account__in=accounts,
                date__range=[start_date, end_date]
            )
            
            # Calculate totals
            total_spend_micros = performance_data.aggregate(
                total=models.Sum('cost_micros')
            )['total'] or 0
            total_spend = total_spend_micros / 1000000
            
            total_impressions = performance_data.aggregate(
                total=models.Sum('impressions')
            )['total'] or 0
            
            total_clicks = performance_data.aggregate(
                total=models.Sum('clicks')
            )['total'] or 0
            
            total_conversions = performance_data.aggregate(
                total=models.Sum('conversions')
            )['total'] or 0
            
            total_conversion_value = performance_data.aggregate(
                total=models.Sum('conversion_value')
            )['total'] or 0
            
            # Calculate rates
            overall_ctr = total_clicks / total_impressions if total_impressions > 0 else 0
            overall_cpc = total_spend / total_clicks if total_clicks > 0 else 0
            overall_roas = total_conversion_value / total_spend if total_spend > 0 else 0
            
            # Get performance trend
            trend_data = performance_data.values('date').annotate(
                daily_impressions=models.Sum('impressions'),
                daily_clicks=models.Sum('clicks'),
                daily_cost=models.Sum('cost_micros'),
                daily_conversions=models.Sum('conversions')
            ).order_by('date')
            
            performance_trend = []
            for day_data in trend_data:
                performance_trend.append({
                    'date': day_data['date'].strftime('%Y-%m-%d'),
                    'impressions': day_data['daily_impressions'],
                    'clicks': day_data['daily_clicks'],
                    'cost': day_data['daily_cost'] / 1000000,
                    'conversions': day_data['daily_conversions']
                })
            
            # Get top campaigns
            top_campaigns = performance_data.values(
                'campaign__campaign_name'
            ).annotate(
                total_spend=models.Sum('cost_micros'),
                total_impressions=models.Sum('impressions'),
                total_clicks=models.Sum('clicks'),
                total_conversions=models.Sum('conversions')
            ).order_by('-total_spend')[:5]
            
            top_campaigns_list = []
            for campaign_data in top_campaigns:
                top_campaigns_list.append({
                    'name': campaign_data['campaign__campaign_name'],
                    'spend': campaign_data['total_spend'] / 1000000,
                    'impressions': campaign_data['total_impressions'],
                    'clicks': campaign_data['total_clicks'],
                    'conversions': campaign_data['total_conversions']
                })
            
            # Get top keywords
            top_keywords = performance_data.values(
                'keyword__keyword_text'
            ).annotate(
                total_spend=models.Sum('cost_micros'),
                total_impressions=models.Sum('impressions'),
                total_clicks=models.Sum('clicks'),
                total_conversions=models.Sum('conversions')
            ).order_by('-total_spend')[:5]
            
            top_keywords_list = []
            for keyword_data in top_keywords:
                top_keywords_list.append({
                    'text': keyword_data['keyword__keyword_text'],
                    'spend': keyword_data['total_spend'] / 1000000,
                    'impressions': keyword_data['total_impressions'],
                    'clicks': keyword_data['total_clicks'],
                    'conversions': keyword_data['total_conversions']
                })
            
            return {
                'total_accounts': accounts.count(),
                'total_campaigns': GoogleAdsCampaign.objects.filter(account__in=accounts).count(),
                'total_spend': total_spend,
                'total_impressions': total_impressions,
                'total_clicks': total_clicks,
                'total_conversions': total_conversions,
                'total_conversion_value': total_conversion_value,
                'overall_ctr': overall_ctr,
                'overall_cpc': overall_cpc,
                'overall_roas': overall_roas,
                'performance_trend': performance_trend,
                'top_campaigns': top_campaigns_list,
                'top_keywords': top_keywords_list
            }
            
        except Exception as e:
            logger.error(f"Failed to get dashboard metrics: {e}")
            return {'error': str(e)}

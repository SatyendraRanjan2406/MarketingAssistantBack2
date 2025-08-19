import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from django.utils import timezone
from django.db import transaction
from celery import shared_task
from .models import (
    GoogleAdsAccount, GoogleAdsCampaign, GoogleAdsAdGroup,
    GoogleAdsKeyword, GoogleAdsPerformance, DataSyncLog
)
from .google_ads_api_service import GoogleAdsAPIService
from .sync_service import GoogleAdsSyncService

logger = logging.getLogger(__name__)


@shared_task(bind=True, name='google_ads_new.daily_sync')
def daily_sync_task(self, account_id: int = None):
    """Daily sync task - sync last week's data"""
    try:
        logger.info(f"Starting daily sync task for account: {account_id}")
        
        # Use the sync service for daily sync
        sync_service = GoogleAdsSyncService()
        result = sync_service.sync_last_week_data(account_id)
        
        if result['success']:
            logger.info(f"Daily sync completed successfully: {result}")
            return result
        else:
            logger.error(f"Daily sync failed: {result}")
            return result
            
    except Exception as e:
        logger.error(f"Error in daily sync task: {e}")
        return {
            'success': False,
            'error': str(e),
            'sync_type': 'daily_sync'
        }


@shared_task(bind=True, name='google_ads_new.weekly_sync')
def weekly_sync_task(self, account_id: int, weeks_back: int = 10):
    """Weekly sync task - sync historical weeks data"""
    try:
        logger.info(f"Starting weekly sync task for account {account_id}, weeks: {weeks_back}")
        
        # Use the sync service for weekly sync
        sync_service = GoogleAdsSyncService()
        result = sync_service.sync_historical_weeks(account_id, weeks_back)
        
        if result['success']:
            logger.info(f"Weekly sync completed successfully: {result}")
            return result
        else:
            logger.error(f"Weekly sync failed: {result}")
            return result
            
    except Exception as e:
        logger.error(f"Error in weekly sync task: {e}")
        return {
            'success': False,
            'error': str(e),
            'sync_type': 'weekly_sync'
        }


@shared_task(bind=True, name='google_ads_new.force_sync')
def force_sync_task(self, account_id: int, weeks: int):
    """Force sync task - sync specified number of weeks"""
    try:
        logger.info(f"Starting force sync task for account {account_id}, weeks: {weeks}")
        
        # Use the sync service for force sync
        sync_service = GoogleAdsSyncService()
        result = sync_service.force_sync_n_weeks(account_id, weeks)
        
        if result['success']:
            logger.info(f"Force sync completed successfully: {result}")
            return result
        else:
            logger.error(f"Force sync failed: {result}")
            return result
            
    except Exception as e:
        logger.error(f"Error in force sync task: {e}")
        return {
            'success': False,
            'error': str(e),
            'sync_type': 'force_sync'
        }


@shared_task(bind=True, name='google_ads_new.sync_from_api')
def sync_from_api_task(self, account_id: int, start_date: str, end_date: str):
    """Sync data directly from Google Ads API"""
    try:
        logger.info(f"Starting API sync task for account {account_id} from {start_date} to {end_date}")
        
        # Get the account
        try:
            account = GoogleAdsAccount.objects.get(id=account_id, is_active=True)
        except GoogleAdsAccount.DoesNotExist:
            return {
                'success': False,
                'error': f'Account {account_id} not found or inactive'
            }
        
        # Initialize API service
        api_service = GoogleAdsAPIService()
        
        # Test connection first
        connection_test = api_service.test_connection(account.customer_id)
        if not connection_test['success']:
            return {
                'success': False,
                'error': f'API connection failed: {connection_test["error"]}'
            }
        
        # Get performance data from API
        performance_data = api_service.get_performance_data(
            account.customer_id, start_date, end_date
        )
        
        if not performance_data:
            return {
                'success': False,
                'error': 'No performance data retrieved from API'
            }
        
        # Process and save the data
        records_created = 0
        records_updated = 0
        
        with transaction.atomic():
            for data in performance_data:
                # Get or create campaign
                campaign = None
                if data.get('campaign_id'):
                    campaign, _ = GoogleAdsCampaign.objects.get_or_create(
                        campaign_id=data['campaign_id'],
                        account=account,
                        defaults={
                            'campaign_name': data.get('campaign_name', 'Unknown Campaign'),
                            'campaign_status': 'ENABLED',
                            'campaign_type': 'SEARCH',
                            'start_date': timezone.now().date() - timedelta(days=30),
                            'budget_amount': 25.00,
                            'budget_type': 'DAILY'
                        }
                    )
                
                # Get or create ad group
                ad_group = None
                if data.get('ad_group_id'):
                    ad_group, _ = GoogleAdsAdGroup.objects.get_or_create(
                        ad_group_id=data['ad_group_id'],
                        campaign=campaign or account.campaigns.first(),
                        defaults={
                            'ad_group_name': data.get('ad_group_name', 'Unknown Ad Group'),
                            'status': 'ENABLED',
                            'type': 'STANDARD'
                        }
                    )
                
                # Get or create keyword
                keyword = None
                if data.get('keyword_id'):
                    keyword, _ = GoogleAdsKeyword.objects.get_or_create(
                        keyword_id=data['keyword_id'],
                        ad_group=ad_group or account.campaigns.first().ad_groups.first(),
                        defaults={
                            'keyword_text': data.get('keyword_text', 'Unknown Keyword'),
                            'match_type': 'BROAD',
                            'status': 'ENABLED',
                            'quality_score': data.get('quality_score', 5)
                        }
                    )
                
                # Create or update performance record
                performance, created = GoogleAdsPerformance.objects.update_or_create(
                    account=account,
                    date=data['date'],
                    campaign=campaign,
                    ad_group=ad_group,
                    keyword=keyword,
                    defaults={
                        'impressions': data.get('impressions', 0),
                        'clicks': data.get('clicks', 0),
                        'cost_micros': data.get('cost_micros', 0),
                        'conversions': data.get('conversions', 0),
                        'conversion_value': data.get('conversion_value', 0)
                    }
                )
                
                if created:
                    records_created += 1
                else:
                    records_updated += 1
        
        # Update account sync status
        account.last_sync_at = timezone.now()
        account.sync_status = 'completed'
        account.save()
        
        # Log the sync operation
        DataSyncLog.objects.create(
            sync_type='api_sync',
            account=account,
            start_date=start_date,
            end_date=end_date,
            results={
                'total_records': len(performance_data),
                'records_created': records_created,
                'records_updated': records_updated,
                'date_range': f"{start_date} to {end_date}"
            },
            status='completed'
        )
        
        result = {
            'success': True,
            'sync_type': 'api_sync',
            'account_id': account_id,
            'date_range': f"{start_date} to {end_date}",
            'total_records': len(performance_data),
            'records_created': records_created,
            'records_updated': records_updated
        }
        
        logger.info(f"API sync completed successfully: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in API sync task: {e}")
        return {
            'success': False,
            'error': str(e),
            'sync_type': 'api_sync'
        }


@shared_task(bind=True, name='google_ads_new.sync_campaigns')
def sync_campaigns_task(self, account_id: int):
    """Sync campaigns from Google Ads API"""
    try:
        logger.info(f"Starting campaigns sync task for account {account_id}")
        
        # Get the account
        try:
            account = GoogleAdsAccount.objects.get(id=account_id, is_active=True)
        except GoogleAdsAccount.DoesNotExist:
            return {
                'success': False,
                'error': f'Account {account_id} not found or inactive'
            }
        
        # Initialize API service
        api_service = GoogleAdsAPIService()
        
        # Test connection first
        connection_test = api_service.test_connection(account.customer_id)
        if not connection_test['success']:
            return {
                'success': False,
                'error': f'API connection failed: {connection_test["error"]}'
            }
        
        # Get campaigns from API
        campaigns_data = api_service.get_campaigns(account.customer_id)
        
        if not campaigns_data:
            return {
                'success': False,
                'error': 'No campaigns retrieved from API'
            }
        
        # Process and save campaigns
        campaigns_created = 0
        campaigns_updated = 0
        
        with transaction.atomic():
            for data in campaigns_data:
                campaign, created = GoogleAdsCampaign.objects.update_or_create(
                    campaign_id=data['campaign_id'],
                    account=account,
                    defaults={
                        'campaign_name': data['campaign_name'],
                        'campaign_status': data['campaign_status'],
                        'campaign_type': data['campaign_type'],
                        'start_date': data.get('start_date', timezone.now().date() - timedelta(days=30)),
                        'end_date': data.get('end_date'),
                        'budget_amount': data.get('budget_amount'),
                        'budget_type': data.get('budget_type', 'DAILY')
                    }
                )
                
                if created:
                    campaigns_created += 1
                else:
                    campaigns_updated += 1
        
        result = {
            'success': True,
            'sync_type': 'campaigns_sync',
            'account_id': account_id,
            'total_campaigns': len(campaigns_data),
            'campaigns_created': campaigns_created,
            'campaigns_updated': campaigns_updated
        }
        
        logger.info(f"Campaigns sync completed successfully: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in campaigns sync task: {e}")
        return {
            'success': False,
            'error': str(e),
            'sync_type': 'campaigns_sync'
        }


@shared_task(bind=True, name='google_ads_new.sync_ad_groups')
def sync_ad_groups_task(self, account_id: int, campaign_id: str = None):
    """Sync ad groups from Google Ads API"""
    try:
        logger.info(f"Starting ad groups sync task for account {account_id}")
        
        # Get the account
        try:
            account = GoogleAdsAccount.objects.get(id=account_id, is_active=True)
        except GoogleAdsAccount.DoesNotExist:
            return {
                'success': False,
                'error': f'Account {account_id} not found or inactive'
            }
        
        # Initialize API service
        api_service = GoogleAdsAPIService()
        
        # Test connection first
        connection_test = api_service.test_connection(account.customer_id)
        if not connection_test['success']:
            return {
                'success': False,
                'error': f'API connection failed: {connection_test["error"]}'
            }
        
        # Get ad groups from API
        ad_groups_data = api_service.get_ad_groups(account.customer_id, campaign_id)
        
        if not ad_groups_data:
            return {
                'success': False,
                'error': 'No ad groups retrieved from API'
            }
        
        # Process and save ad groups
        ad_groups_created = 0
        ad_groups_updated = 0
        
        with transaction.atomic():
            for data in ad_groups_data:
                # Find the campaign
                try:
                    campaign = GoogleAdsCampaign.objects.get(
                        campaign_id=data['campaign_id'],
                        account=account
                    )
                except GoogleAdsCampaign.DoesNotExist:
                    logger.warning(f"Campaign {data['campaign_id']} not found, skipping ad group")
                    continue
                
                ad_group, created = GoogleAdsAdGroup.objects.update_or_create(
                    ad_group_id=data['ad_group_id'],
                    campaign=campaign,
                    defaults={
                        'ad_group_name': data['ad_group_name'],
                        'status': data['status'],
                        'type': data['type']
                    }
                )
                
                if created:
                    ad_groups_created += 1
                else:
                    ad_groups_updated += 1
        
        result = {
            'success': True,
            'sync_type': 'ad_groups_sync',
            'account_id': account_id,
            'total_ad_groups': len(ad_groups_data),
            'ad_groups_created': ad_groups_created,
            'ad_groups_updated': ad_groups_updated
        }
        
        logger.info(f"Ad groups sync completed successfully: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in ad groups sync task: {e}")
        return {
            'success': False,
            'error': str(e),
            'sync_type': 'ad_groups_sync'
        }


@shared_task(bind=True, name='google_ads_new.sync_keywords')
def sync_keywords_task(self, account_id: int, ad_group_id: str = None):
    """Sync keywords from Google Ads API"""
    try:
        logger.info(f"Starting keywords sync task for account {account_id}")
        
        # Get the account
        try:
            account = GoogleAdsAccount.objects.get(id=account_id, is_active=True)
        except GoogleAdsAccount.DoesNotExist:
            return {
                'success': False,
                'error': f'Account {account_id} not found or inactive'
            }
        
        # Initialize API service
        api_service = GoogleAdsAPIService()
        
        # Test connection first
        connection_test = api_service.test_connection(account.customer_id)
        if not connection_test['success']:
            return {
                'success': False,
                'error': f'API connection failed: {connection_test["error"]}'
            }
        
        # Get keywords from API
        keywords_data = api_service.get_keywords(account.customer_id, ad_group_id)
        
        if not keywords_data:
            return {
                'success': False,
                'error': 'No keywords retrieved from API'
            }
        
        # Process and save keywords
        keywords_created = 0
        keywords_updated = 0
        
        with transaction.atomic():
            for data in keywords_data:
                # Find the ad group
                try:
                    ad_group = GoogleAdsAdGroup.objects.get(
                        ad_group_id=data['ad_group_id']
                    )
                except GoogleAdsAdGroup.DoesNotExist:
                    logger.warning(f"Ad group {data['ad_group_id']} not found, skipping keyword")
                    continue
                
                keyword, created = GoogleAdsKeyword.objects.update_or_create(
                    keyword_id=data['keyword_id'],
                    ad_group=ad_group,
                    defaults={
                        'keyword_text': data['keyword_text'],
                        'match_type': data['match_type'],
                        'status': data['status'],
                        'quality_score': data.get('quality_score')
                    }
                )
                
                if created:
                    keywords_created += 1
                else:
                    keywords_updated += 1
        
        result = {
            'success': True,
            'sync_type': 'keywords_sync',
            'account_id': account_id,
            'total_keywords': len(keywords_data),
            'keywords_created': keywords_created,
            'keywords_updated': keywords_updated
        }
        
        logger.info(f"Keywords sync completed successfully: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in keywords sync task: {e}")
        return {
            'success': False,
            'error': str(e),
            'sync_type': 'keywords_sync'
        }

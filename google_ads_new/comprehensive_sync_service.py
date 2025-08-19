#!/usr/bin/env python3
"""
Comprehensive Google Ads Sync Service
Pulls all data from Google Ads accounts and stores in database
Supports incremental daily syncs using segments.date
"""

import logging
import sys
from typing import Dict, List, Optional, Any, Iterator
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
import os

try:
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException
    GOOGLE_ADS_AVAILABLE = True
except ImportError:
    GOOGLE_ADS_AVAILABLE = False
    logging.warning("Google Ads library not available. Install with: pip install google-ads")
    class GoogleAdsException(Exception):
        pass

from .models import (
    GoogleAdsAccount, GoogleAdsCampaign, GoogleAdsAdGroup, 
    GoogleAdsKeyword, GoogleAdsPerformance, DataSyncLog
)

logger = logging.getLogger(__name__)


class ComprehensiveGoogleAdsSyncService:
    """Comprehensive service for syncing Google Ads data into database"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), 'google-ads.yaml'
        )
        self.client = None
        self.logger = logging.getLogger(__name__)
        
        # Set up logging for Google Ads library
        if GOOGLE_ADS_AVAILABLE:
            ga_logger = logging.getLogger('google.ads.googleads.client')
            ga_logger.addHandler(logging.StreamHandler(sys.stdout))
            ga_logger.setLevel(logging.INFO)
    
    def initialize_client(self) -> bool:
        """Initialize the Google Ads client"""
        try:
            if not GOOGLE_ADS_AVAILABLE:
                self.logger.error("Google Ads library not available")
                return False
            
            if not os.path.exists(self.config_path):
                self.logger.error(f"Google Ads config file not found: {self.config_path}")
                return False
            
            # Initialize the real Google Ads client
            self.client = GoogleAdsClient.load_from_storage(self.config_path)
            self.logger.info("Google Ads client initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing Google Ads client: {e}")
            return False
    
    def get_all_client_accounts(self, manager_customer_id: str) -> List[Dict[str, Any]]:
        """Get all client accounts under the manager account"""
        try:
            if not self.client:
                if not self.initialize_client():
                    return []
            
            ga_service = self.client.get_service("GoogleAdsService")
            
            query = """
                SELECT 
                    customer_client.client_customer, 
                    customer_client.descriptive_name, 
                    customer_client.currency_code, 
                    customer_client.time_zone 
                FROM customer_client
            """
            
            accounts = []
            stream = ga_service.search_stream(customer_id=manager_customer_id, query=query)
            
            for batch in stream:
                rows = batch.results
                for row in rows:
                    # Extract customer ID from resource name (e.g., "customers/1234567890" -> "1234567890")
                    customer_id = row.customer_client.client_customer.split('/')[-1]
                    
                    # Handle enum values properly
                    currency_code = None
                    if hasattr(row.customer_client, 'currency_code') and row.customer_client.currency_code:
                        try:
                            currency_code = row.customer_client.currency_code.name
                        except AttributeError:
                            currency_code = str(row.customer_client.currency_code)
                    
                    time_zone = None
                    if hasattr(row.customer_client, 'time_zone') and row.customer_client.time_zone:
                        try:
                            time_zone = row.customer_client.time_zone
                        except AttributeError:
                            time_zone = str(row.customer_client.time_zone)
                    
                    account_data = {
                        'customer_id': customer_id,
                        'descriptive_name': row.customer_client.descriptive_name,
                        'currency_code': currency_code,
                        'time_zone': time_zone,
                    }
                    accounts.append(account_data)
            
            self.logger.info(f"Retrieved {len(accounts)} client accounts for manager {manager_customer_id}")
            return accounts
            
        except GoogleAdsException as e:
            self.logger.error(f"Google Ads API error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error retrieving client accounts: {e}")
            return []
    
    def get_campaigns(self, customer_id: str) -> List[Dict[str, Any]]:
        """Retrieve campaigns from Google Ads account"""
        try:
            if not self.client:
                if not self.initialize_client():
                    return []
            
            ga_service = self.client.get_service("GoogleAdsService")
            
            query = """
                SELECT
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    campaign.advertising_channel_type,
                    campaign.start_date,
                    campaign.end_date
                FROM campaign
                WHERE campaign.status != 'REMOVED'
                ORDER BY campaign.id
            """
            
            campaigns = []
            stream = ga_service.search_stream(customer_id=customer_id, query=query)
            
            for batch in stream:
                rows = batch.results
                for row in rows:
                    campaign_data = {
                        'campaign_id': str(row.campaign.id),
                        'campaign_name': row.campaign.name,
                        'campaign_status': row.campaign.status.name if hasattr(row.campaign.status, 'name') else str(row.campaign.status),
                        'campaign_type': row.campaign.advertising_channel_type.name if hasattr(row.campaign.advertising_channel_type, 'name') else str(row.campaign.advertising_channel_type),
                        'start_date': row.campaign.start_date,
                        'end_date': row.campaign.end_date,
                        'budget_amount': None,  # Not available in this API version
                        'budget_type': 'DAILY',  # Default value since field is required
                    }
                    campaigns.append(campaign_data)
            
            self.logger.info(f"Retrieved {len(campaigns)} campaigns for customer {customer_id}")
            return campaigns
            
        except GoogleAdsException as e:
            self.logger.error(f"Google Ads API error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error retrieving campaigns: {e}")
            return []
    
    def get_ad_groups(self, customer_id: str, campaign_id: str = None) -> List[Dict[str, Any]]:
        """Retrieve ad groups from Google Ads account"""
        try:
            if not self.client:
                if not self.initialize_client():
                    return []
            
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
                    WHERE ad_group.status != 'REMOVED' AND campaign.id = {campaign_id}
                    ORDER BY ad_group.id
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
                    ORDER BY ad_group.id
                """
            
            ad_groups = []
            stream = ga_service.search_stream(customer_id=customer_id, query=query)
            
            for batch in stream:
                rows = batch.results
                for row in rows:
                    ad_group_data = {
                        'ad_group_id': str(row.ad_group.id),
                        'ad_group_name': row.ad_group.name,
                        'status': row.ad_group.status.name if hasattr(row.ad_group.status, 'name') else str(row.ad_group.status),
                        'type': row.ad_group.type.name if hasattr(row.ad_group.type, 'name') else str(row.ad_group.type),
                        'campaign_id': str(row.campaign.id),
                    }
                    ad_groups.append(ad_group_data)
            
            self.logger.info(f"Retrieved {len(ad_groups)} ad groups for customer {customer_id}")
            return ad_groups
            
        except GoogleAdsException as e:
            self.logger.error(f"Google Ads API error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error retrieving ad groups: {e}")
            return []
    
    def get_ads(self, customer_id: str, ad_group_id: str = None) -> List[Dict[str, Any]]:
        """Retrieve ads from Google Ads account"""
        try:
            if not self.client:
                if not self.initialize_client():
                    return []
            
            ga_service = self.client.get_service("GoogleAdsService")
            
            if ad_group_id:
                query = f"""
                    SELECT
                        ad_group_ad.ad.id,
                        ad_group_ad.ad.responsive_search_ad.headlines,
                        ad_group_ad.status,
                        ad_group.id
                    FROM ad_group_ad
                    WHERE ad_group_ad.status != 'REMOVED' AND ad_group.id = {ad_group_id}
                    ORDER BY ad_group_ad.ad.id
                """
            else:
                query = """
                    SELECT
                        ad_group_ad.ad.id,
                        ad_group_ad.ad.responsive_search_ad.headlines,
                        ad_group_ad.status,
                        ad_group.id
                    FROM ad_group_ad
                    WHERE ad_group_ad.status != 'REMOVED'
                    ORDER BY ad_group_ad.ad.id
                """
            
            ads = []
            stream = ga_service.search_stream(customer_id=customer_id, query=query)
            
            for batch in stream:
                rows = batch.results
                for row in rows:
                    # Extract headlines from responsive search ad
                    headlines = []
                    if hasattr(row.ad_group_ad.ad, 'responsive_search_ad') and row.ad_group_ad.ad.responsive_search_ad:
                        for headline in row.ad_group_ad.ad.responsive_search_ad.headlines:
                            headlines.append(headline.text)
                    
                    ad_data = {
                        'ad_id': str(row.ad_group_ad.ad.id),
                        'headlines': headlines,
                        'status': row.ad_group_ad.status.name if hasattr(row.ad_group_ad.status, 'name') else str(row.ad_group_ad.status),
                        'ad_group_id': str(row.ad_group.id),
                    }
                    ads.append(ad_data)
            
            self.logger.info(f"Retrieved {len(ads)} ads for customer {customer_id}")
            return ads
            
        except GoogleAdsException as e:
            self.logger.error(f"Google Ads API error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error retrieving ads: {e}")
            return []
    
    def get_keywords(self, customer_id: str, ad_group_id: str = None) -> List[Dict[str, Any]]:
        """Retrieve keywords (criteria) from Google Ads account"""
        try:
            if not self.client:
                if not self.initialize_client():
                    return []
            
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
                    WHERE ad_group_criterion.type = 'KEYWORD' 
                        AND ad_group_criterion.status != 'REMOVED'
                        AND ad_group.id = {ad_group_id}
                    ORDER BY ad_group_criterion.criterion_id
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
                    ORDER BY ad_group_criterion.criterion_id
                """
            
            keywords = []
            stream = ga_service.search_stream(customer_id=customer_id, query=query)
            
            for batch in stream:
                rows = batch.results
                for row in rows:
                    keyword_data = {
                        'keyword_id': str(row.ad_group_criterion.criterion_id),
                        'keyword_text': row.ad_group_criterion.keyword.text,
                        'match_type': row.ad_group_criterion.keyword.match_type.name if hasattr(row.ad_group_criterion.keyword.match_type, 'name') else str(row.ad_group_criterion.keyword.match_type),
                        'status': row.ad_group_criterion.status.name if hasattr(row.ad_group_criterion.status, 'name') else str(row.ad_group_criterion.status),
                        'quality_score': row.ad_group_criterion.quality_info.quality_score if row.ad_group_criterion.quality_info.quality_score else None,
                        'ad_group_id': str(row.ad_group.id),
                    }
                    keywords.append(keyword_data)
            
            self.logger.info(f"Retrieved {len(keywords)} keywords for customer {customer_id}")
            return keywords
            
        except GoogleAdsException as e:
            self.logger.error(f"Google Ads API error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error retrieving keywords: {e}")
            return []
    
    def get_performance_data(self, customer_id: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Retrieve performance data from Google Ads account with date filtering"""
        try:
            if not self.client:
                if not self.initialize_client():
                    return []
            
            ga_service = self.client.get_service("GoogleAdsService")
            
            query = f"""
                SELECT
                    campaign.id,
                    campaign.name,
                    ad_group.id,
                    ad_group.name,
                    ad_group_criterion.criterion_id,
                    ad_group_criterion.keyword.text,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.conversions_value,
                    segments.date
                FROM keyword_view
                WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
                ORDER BY segments.date DESC
            """
            
            performance_data = []
            stream = ga_service.search_stream(customer_id=customer_id, query=query)
            
            for batch in stream:
                rows = batch.results
                for row in rows:
                    data = {
                        'campaign_id': str(row.campaign.id) if row.campaign.id else None,
                        'campaign_name': row.campaign.name if row.campaign.name else None,
                        'ad_group_id': str(row.ad_group.id) if row.ad_group.id else None,
                        'ad_group_name': row.ad_group.name if row.ad_group.name else None,
                        'keyword_id': str(row.ad_group_criterion.criterion_id) if row.ad_group_criterion.criterion_id else None,
                        'keyword_text': row.ad_group_criterion.keyword.text if row.ad_group_criterion.keyword.text else None,
                        'impressions': row.metrics.impressions,
                        'clicks': row.metrics.clicks,
                        'cost_micros': row.metrics.cost_micros,
                        'conversions': row.metrics.conversions,
                        'conversion_value': row.metrics.conversions_value,
                        'date': row.segments.date,
                    }
                    performance_data.append(data)
            
            self.logger.info(f"Retrieved {len(performance_data)} performance records for customer {customer_id}")
            return performance_data
            
        except GoogleAdsException as e:
            self.logger.error(f"Google Ads API error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error retrieving performance data: {e}")
            return []
    
    def sync_account_to_database(self, account_data: Dict[str, Any]) -> Optional[GoogleAdsAccount]:
        """Sync a single account to the database"""
        try:
            with transaction.atomic():
                # Get or create a default user for the account
                from django.contrib.auth.models import User
                default_user, created = User.objects.get_or_create(
                    username='google_ads_sync_user',
                    defaults={
                        'email': 'sync@googleads.local',
                        'first_name': 'Google',
                        'last_name': 'Ads Sync',
                        'is_active': False,  # Not a real user
                    }
                )
                
                # Create or update the account
                account, created = GoogleAdsAccount.objects.update_or_create(
                    customer_id=account_data['customer_id'],
                    defaults={
                        'user': default_user,
                        'account_name': account_data['descriptive_name'],
                        'currency_code': account_data['currency_code'],
                        'time_zone': account_data['time_zone'],
                        'last_sync_at': timezone.now(),
                        'sync_status': 'SYNCED',
                    }
                )
                
                if created:
                    self.logger.info(f"Created new account: {account_data['customer_id']}")
                else:
                    self.logger.info(f"Updated existing account: {account_data['customer_id']}")
                
                return account
                
        except Exception as e:
            self.logger.error(f"Error syncing account {account_data['customer_id']}: {e}")
            return None
    
    def sync_campaigns_to_database(self, account: GoogleAdsAccount, campaigns_data: List[Dict[str, Any]]) -> int:
        """Sync campaigns to the database"""
        try:
            with transaction.atomic():
                synced_count = 0
                
                for campaign_data in campaigns_data:
                    campaign, created = GoogleAdsCampaign.objects.update_or_create(
                        campaign_id=campaign_data['campaign_id'],
                        account=account,
                        defaults={
                            'campaign_name': campaign_data['campaign_name'],
                            'campaign_status': campaign_data['campaign_status'],
                            'campaign_type': campaign_data['campaign_type'],
                            'start_date': campaign_data['start_date'],
                            'end_date': campaign_data['end_date'],
                            'budget_amount': campaign_data['budget_amount'],
                            'budget_type': campaign_data['budget_type'],
                        }
                    )
                    
                    if created:
                        self.logger.info(f"Created campaign: {campaign_data['campaign_id']}")
                    else:
                        self.logger.info(f"Updated campaign: {campaign_data['campaign_id']}")
                    
                    synced_count += 1
                
                return synced_count
                
        except Exception as e:
            self.logger.error(f"Error syncing campaigns for account {account.customer_id}: {e}")
            return 0
    
    def sync_ad_groups_to_database(self, account: GoogleAdsAccount, ad_groups_data: List[Dict[str, Any]]) -> int:
        """Sync ad groups to the database"""
        try:
            with transaction.atomic():
                synced_count = 0
                
                for ad_group_data in ad_groups_data:
                    # Find the campaign
                    try:
                        campaign = GoogleAdsCampaign.objects.get(
                            campaign_id=ad_group_data['campaign_id'],
                            account=account
                        )
                    except GoogleAdsCampaign.DoesNotExist:
                        self.logger.warning(f"Campaign {ad_group_data['campaign_id']} not found for ad group {ad_group_data['ad_group_id']}")
                        continue
                    
                    ad_group, created = GoogleAdsAdGroup.objects.update_or_create(
                        ad_group_id=ad_group_data['ad_group_id'],
                        campaign=campaign,
                        defaults={
                            'ad_group_name': ad_group_data['ad_group_name'],
                            'status': ad_group_data['status'],
                            'type': ad_group_data['type'],
                        }
                    )
                    
                    if created:
                        self.logger.info(f"Created ad group: {ad_group_data['ad_group_id']}")
                    else:
                        self.logger.info(f"Updated ad group: {ad_group_data['ad_group_id']}")
                    
                    synced_count += 1
                
                return synced_count
                
        except Exception as e:
            self.logger.error(f"Error syncing ad groups for account {account.customer_id}: {e}")
            return 0
    
    def sync_keywords_to_database(self, account: GoogleAdsAccount, keywords_data: List[Dict[str, Any]]) -> int:
        """Sync keywords to the database"""
        try:
            with transaction.atomic():
                synced_count = 0
                
                for keyword_data in keywords_data:
                    # Find the ad group
                    try:
                        ad_group = GoogleAdsAdGroup.objects.get(
                            ad_group_id=keyword_data['ad_group_id'],
                            campaign__account=account
                        )
                    except GoogleAdsAdGroup.DoesNotExist:
                        self.logger.warning(f"Ad group {keyword_data['ad_group_id']} not found for keyword {keyword_data['keyword_id']}")
                        continue
                    
                    keyword, created = GoogleAdsKeyword.objects.update_or_create(
                        keyword_id=keyword_data['keyword_id'],
                        ad_group=ad_group,
                        defaults={
                            'keyword_text': keyword_data['keyword_text'],
                            'match_type': keyword_data['match_type'],
                            'status': keyword_data['status'],
                            'quality_score': keyword_data['quality_score'],
                        }
                    )
                    
                    if created:
                        self.logger.info(f"Created keyword: {keyword_data['keyword_id']}")
                    else:
                        self.logger.info(f"Updated keyword: {keyword_data['keyword_id']}")
                    
                    synced_count += 1
                
                return synced_count
                
        except Exception as e:
            self.logger.error(f"Error syncing keywords for account {account.customer_id}: {e}")
            return 0
    
    def sync_performance_to_database(self, account: GoogleAdsAccount, performance_data: List[Dict[str, Any]]) -> int:
        """Sync performance data to the database"""
        try:
            with transaction.atomic():
                synced_count = 0
                
                for perf_data in performance_data:
                    # Find the keyword if it exists
                    keyword = None
                    if perf_data['keyword_id']:
                        try:
                            keyword = GoogleAdsKeyword.objects.get(
                                keyword_id=perf_data['keyword_id'],
                                ad_group__campaign__account=account
                            )
                        except GoogleAdsKeyword.DoesNotExist:
                            self.logger.warning(f"Keyword {perf_data['keyword_id']} not found for performance data")
                    
                    # Find the campaign if it exists
                    campaign = None
                    if perf_data['campaign_id']:
                        try:
                            campaign = GoogleAdsCampaign.objects.get(
                                campaign_id=perf_data['campaign_id'],
                                account=account
                            )
                        except GoogleAdsCampaign.DoesNotExist:
                            self.logger.warning(f"Campaign {perf_data['campaign_id']} not found for performance data")
                    
                    # Find the ad group if it exists
                    ad_group = None
                    if perf_data['ad_group_id']:
                        try:
                            ad_group = GoogleAdsAdGroup.objects.get(
                                ad_group_id=perf_data['ad_group_id'],
                                campaign__account=account
                            )
                        except GoogleAdsAdGroup.DoesNotExist:
                            self.logger.warning(f"Ad group {perf_data['ad_group_id']} not found for performance data")
                    
                    # Create or update performance record
                    performance, created = GoogleAdsPerformance.objects.update_or_create(
                        account=account,
                        date=perf_data['date'],
                        keyword=keyword,
                        defaults={
                            'campaign': campaign,
                            'ad_group': ad_group,
                            'impressions': perf_data['impressions'],
                            'clicks': perf_data['clicks'],
                            'cost_micros': perf_data['cost_micros'],
                            'conversions': perf_data['conversions'],
                            'conversion_value': perf_data['conversion_value'],
                        }
                    )
                    
                    if created:
                        self.logger.info(f"Created performance record for date: {perf_data['date']}")
                    else:
                        self.logger.info(f"Updated performance record for date: {perf_data['date']}")
                    
                    synced_count += 1
                
                return synced_count
                
        except Exception as e:
            self.logger.error(f"Error syncing performance data for account {account.customer_id}: {e}")
            return 0
    
    def log_sync_operation(self, account: GoogleAdsAccount, operation: str, details: str, success: bool = True) -> None:
        """Log sync operations for tracking"""
        try:
            DataSyncLog.objects.create(
                sync_type='account_sync',
                account=account,
                results={'operation': operation, 'details': details, 'success': success},
                status='completed' if success else 'failed',
                error_message=None if success else details,
                completed_at=timezone.now(),
            )
        except Exception as e:
            self.logger.error(f"Error logging sync operation: {e}")
    
    def comprehensive_sync(self, manager_customer_id: str, days_back: int = 7) -> Dict[str, Any]:
        """Perform comprehensive sync of all Google Ads data"""
        try:
            if not self.client:
                if not self.initialize_client():
                    return {'success': False, 'error': 'Failed to initialize client'}
            
            # Calculate date range for performance data
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days_back)
            
            self.logger.info(f"Starting comprehensive sync for manager {manager_customer_id}")
            self.logger.info(f"Date range: {start_date} to {end_date}")
            
            # Get all client accounts
            client_accounts = self.get_all_client_accounts(manager_customer_id)
            if not client_accounts:
                return {'success': False, 'error': 'No client accounts found'}
            
            sync_summary = {
                'manager_customer_id': manager_customer_id,
                'accounts_processed': 0,
                'campaigns_synced': 0,
                'ad_groups_synced': 0,
                'keywords_synced': 0,
                'performance_records_synced': 0,
                'errors': [],
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
            }
            
            # Process each client account
            for account_data in client_accounts:
                try:
                    self.logger.info(f"Processing account: {account_data['customer_id']}")
                    
                    # Sync account to database
                    account = self.sync_account_to_database(account_data)
                    if not account:
                        sync_summary['errors'].append(f"Failed to sync account {account_data['customer_id']}")
                        continue
                    
                    sync_summary['accounts_processed'] += 1
                    
                    # Get and sync campaigns
                    campaigns_data = self.get_campaigns(account_data['customer_id'])
                    campaigns_synced = self.sync_campaigns_to_database(account, campaigns_data)
                    sync_summary['campaigns_synced'] += campaigns_synced
                    
                    # Get and sync ad groups
                    ad_groups_data = self.get_ad_groups(account_data['customer_id'])
                    ad_groups_synced = self.sync_ad_groups_to_database(account, ad_groups_data)
                    sync_summary['ad_groups_synced'] += ad_groups_synced
                    
                    # Get and sync keywords
                    keywords_data = self.get_keywords(account_data['customer_id'])
                    keywords_synced = self.sync_keywords_to_database(account, keywords_data)
                    sync_summary['keywords_synced'] += keywords_synced
                    
                    # Get and sync performance data
                    performance_data = self.get_performance_data(
                        account_data['customer_id'], 
                        start_date.isoformat(), 
                        end_date.isoformat()
                    )
                    performance_synced = self.sync_performance_to_database(account, performance_data)
                    sync_summary['performance_records_synced'] += performance_synced
                    
                    # Log successful sync
                    self.log_sync_operation(
                        account, 
                        'COMPREHENSIVE_SYNC', 
                        f"Synced {campaigns_synced} campaigns, {ad_groups_synced} ad groups, {keywords_synced} keywords, {performance_synced} performance records"
                    )
                    
                    self.logger.info(f"Successfully synced account {account_data['customer_id']}")
                    
                except Exception as e:
                    error_msg = f"Error processing account {account_data['customer_id']}: {e}"
                    self.logger.error(error_msg)
                    sync_summary['errors'].append(error_msg)
                    
                    # Log failed sync
                    if 'account' in locals():
                        self.log_sync_operation(account, 'COMPREHENSIVE_SYNC', str(e), success=False)
            
            self.logger.info(f"Comprehensive sync completed. Summary: {sync_summary}")
            return {'success': True, 'summary': sync_summary}
            
        except Exception as e:
            error_msg = f"Error in comprehensive sync: {e}"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}
    
    def incremental_daily_sync(self, manager_customer_id: str) -> Dict[str, Any]:
        """Perform incremental daily sync (last 1 day)"""
        return self.comprehensive_sync(manager_customer_id, days_back=1)

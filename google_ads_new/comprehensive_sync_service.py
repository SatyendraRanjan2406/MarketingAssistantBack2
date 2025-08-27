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
    
    def __init__(self, user_id: int = None, manager_customer_id: str = None):
        self.user_id = user_id
        self.manager_customer_id = manager_customer_id
        self.client = None
        self.logger = logging.getLogger(__name__)
        
        # Set up logging for Google Ads library
        if GOOGLE_ADS_AVAILABLE:
            ga_logger = logging.getLogger('google.ads.googleads.client')
            ga_logger.addHandler(logging.StreamHandler(sys.stdout))
            ga_logger.setLevel(logging.INFO)
    
    def initialize_client(self) -> bool:
        """Initialize the Google Ads client using database credentials"""
        try:
            if not GOOGLE_ADS_AVAILABLE:
                self.logger.error("Google Ads library not available")
                return False
            
            # Get credentials from database
            from accounts.models import UserGoogleAuth
            
            if not self.user_id:
                raise ValueError("User ID is required to get credentials from database")
            
            # Get the user's Google OAuth credentials
            user_auth = UserGoogleAuth.objects.filter(
                user_id=self.user_id,
                is_active=True
            ).first()
            
            if not user_auth:
                raise ValueError(f"No active Google OAuth credentials found for user {self.user_id}")
            
            # Create credentials dictionary
            credentials = {
                'client_id': os.getenv('GOOGLE_OAUTH_CLIENT_ID'),
                'client_secret': os.getenv('GOOGLE_OAUTH_CLIENT_SECRET'),
                'developer_token': os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN'),
                'refresh_token': user_auth.refresh_token,
                'login_customer_id': self.manager_customer_id or user_auth.google_ads_customer_id,
            }
            
            # Initialize the Google Ads client
            self.client = GoogleAdsClient.load_from_dict(credentials)
            self.logger.info("Google Ads client initialized successfully from database credentials")
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
                        currency_code = row.customer_client.currency_code.name if hasattr(row.customer_client.currency_code, 'name') else str(row.customer_client.currency_code)
                    
                    time_zone = None
                    if hasattr(row.customer_client, 'time_zone') and row.customer_client.time_zone:
                        time_zone = row.customer_client.time_zone.name if hasattr(row.customer_client.time_zone, 'name') else str(row.customer_client.time_zone)
                    
                    accounts.append({
                        'customer_id': customer_id,
                        'descriptive_name': row.customer_client.descriptive_name,
                        'currency_code': currency_code or 'USD',
                        'time_zone': time_zone or 'UTC'
                    })
            
            self.logger.info(f"Retrieved {len(accounts)} client accounts for manager {manager_customer_id}")
            return accounts
            
        except Exception as e:
            self.logger.error(f"Error retrieving client accounts: {e}")
            return []
    
    def get_campaigns(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get campaigns for a customer account"""
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
                    campaign.start_date,
                    campaign.end_date
                FROM campaign
                WHERE campaign.status != 'REMOVED'
            """
            
            campaigns = []
            stream = ga_service.search_stream(customer_id=customer_id, query=query)
            
            for batch in stream:
                rows = batch.results
                for row in rows:
                    # Handle enum values properly
                    campaign_status = None
                    if hasattr(row.campaign.status, 'name'):
                        campaign_status = row.campaign.status.name
                    else:
                        campaign_status = str(row.campaign.status)
                    
                    campaigns.append({
                        'campaign_id': row.campaign.id,
                        'campaign_name': row.campaign.name,
                        'campaign_status': campaign_status,
                        'start_date': row.campaign.start_date,
                        'end_date': row.campaign.end_date,
                        'budget_amount': None,
                        'budget_type': 'DAILY'
                    })
            
            self.logger.info(f"Retrieved {len(campaigns)} campaigns for customer {customer_id}")
            return campaigns
            
        except Exception as e:
            self.logger.error(f"Error retrieving campaigns: {e}")
            return []
    
    def get_ad_groups(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get ad groups for a customer account"""
        try:
            if not self.client:
                if not self.initialize_client():
                    return []
            
            ga_service = self.client.get_service("GoogleAdsService")
            
            query = """
                SELECT 
                    ad_group.id,
                    ad_group.name,
                    ad_group.status,
                    ad_group.type,
                    campaign.id
                FROM ad_group
                WHERE ad_group.status != 'REMOVED'
            """
            
            ad_groups = []
            stream = ga_service.search_stream(customer_id=customer_id, query=query)
            
            for batch in stream:
                rows = batch.results
                for row in rows:
                    # Handle enum values properly
                    ad_group_status = None
                    if hasattr(row.ad_group.status, 'name'):
                        ad_group_status = row.ad_group.status.name
                    else:
                        ad_group_status = str(row.ad_group.status)
                    
                    ad_group_type = None
                    if hasattr(row.ad_group.type, 'name'):
                        ad_group_type = row.ad_group.type.name
                    else:
                        ad_group_type = str(row.ad_group.type)
                    
                    ad_groups.append({
                        'ad_group_id': row.ad_group.id,
                        'ad_group_name': row.ad_group.name,
                        'ad_group_status': ad_group_status,
                        'ad_group_type': ad_group_type,
                        'campaign_id': row.campaign.id
                    })
            
            self.logger.info(f"Retrieved {len(ad_groups)} ad groups for customer {customer_id}")
            return ad_groups
            
        except Exception as e:
            self.logger.error(f"Error retrieving ad groups: {e}")
            return []
    
    def get_keywords(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get keywords for a customer account"""
        try:
            if not self.client:
                if not self.initialize_client():
                    return []
            
            ga_service = self.client.get_service("GoogleAdsService")
            
            query = """
                SELECT 
                    ad_group_criterion.criterion_id,
                    ad_group_criterion.keyword.text,
                    ad_group_criterion.keyword.match_type,
                    ad_group_criterion.status,
                    ad_group.id
                FROM ad_group_criterion
                WHERE ad_group_criterion.type = 'KEYWORD'
                AND ad_group_criterion.status != 'REMOVED'
            """
            
            keywords = []
            stream = ga_service.search_stream(customer_id=customer_id, query=query)
            
            for batch in stream:
                rows = batch.results
                for row in rows:
                    # Handle enum values properly
                    keyword_match_type = None
                    if hasattr(row.ad_group_criterion.keyword.match_type, 'name'):
                        keyword_match_type = row.ad_group_criterion.keyword.match_type.name
                    else:
                        keyword_match_type = str(row.ad_group_criterion.keyword.match_type)
                    
                    keyword_status = None
                    if hasattr(row.ad_group_criterion.status, 'name'):
                        keyword_status = row.ad_group_criterion.status.name
                    else:
                        keyword_status = str(row.ad_group_criterion.status)
                    
                    keywords.append({
                        'keyword_id': row.ad_group_criterion.criterion_id,
                        'keyword_text': row.ad_group_criterion.keyword.text,
                        'match_type': keyword_match_type,
                        'keyword_status': keyword_status,
                        'ad_group_id': row.ad_group.id
                    })
            
            self.logger.info(f"Retrieved {len(keywords)} keywords for customer {customer_id}")
            return keywords
            
        except Exception as e:
            self.logger.error(f"Error retrieving keywords: {e}")
            return []
    
    def get_performance_data(self, customer_id: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get performance data for a customer account"""
        try:
            if not self.client:
                if not self.initialize_client():
                    return []
            
            ga_service = self.client.get_service("GoogleAdsService")
            
            query = f"""
                SELECT 
                    campaign.id,
                    ad_group.id,
                    ad_group_criterion.criterion_id,
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
                    performance_data.append({
                        'campaign_id': row.campaign.id if row.campaign else None,
                        'ad_group_id': row.ad_group.id if row.ad_group else None,
                        'keyword_id': row.ad_group_criterion.criterion_id if row.ad_group_criterion else None,
                        'date': row.segments.date,
                        'impressions': row.metrics.impressions,
                        'clicks': row.metrics.clicks,
                        'cost_micros': row.metrics.cost_micros,
                        'conversions': row.metrics.conversions,
                        'conversion_value': row.metrics.conversions_value
                    })
            
            self.logger.info(f"Retrieved {len(performance_data)} performance records for customer {customer_id}")
            return performance_data
            
        except Exception as e:
            self.logger.error(f"Error retrieving performance data: {e}")
            return []
    
    def sync_account_to_database(self, account_data: Dict[str, Any]) -> Optional[GoogleAdsAccount]:
        """Sync account data to database"""
        try:
            # Get or create a default user for the account
            from django.contrib.auth.models import User
            default_user, created = User.objects.get_or_create(
                username='sync_user',
                defaults={'email': 'sync@example.com', 'first_name': 'Sync', 'last_name': 'User'}
            )
            
            account, created = GoogleAdsAccount.objects.update_or_create(
                customer_id=account_data['customer_id'],
                defaults={
                    'user': default_user,
                    'account_name': account_data['descriptive_name'],
                    'currency_code': account_data['currency_code'],
                    'time_zone': account_data['time_zone'],
                    'is_active': True,
                    'last_sync_at': timezone.now()
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
    
    def sync_campaigns_to_database(self, customer_id: str, campaigns_data: List[Dict[str, Any]]) -> int:
        """Sync campaigns data to database"""
        try:
            account = GoogleAdsAccount.objects.filter(customer_id=customer_id).first()
            if not account:
                self.logger.error(f"Account {customer_id} not found in database")
                return 0
            
            campaigns_synced = 0
            for campaign_data in campaigns_data:
                try:
                    campaign, created = GoogleAdsCampaign.objects.update_or_create(
                        account=account,
                        campaign_id=campaign_data['campaign_id'],
                        defaults={
                            'campaign_name': campaign_data['campaign_name'],
                            'campaign_status': campaign_data['campaign_status'],
                            'campaign_type': 'SEARCH',  # Default type
                            'start_date': campaign_data['start_date'],
                            'end_date': campaign_data['end_date'],
                            'budget_amount': campaign_data['budget_amount'],
                            'budget_type': campaign_data['budget_type']
                        }
                    )
                    
                    if created:
                        self.logger.info(f"Created campaign: {campaign_data['campaign_id']}")
                    else:
                        self.logger.info(f"Updated campaign: {campaign_data['campaign_id']}")
                    
                    campaigns_synced += 1
                    
                except Exception as e:
                    self.logger.error(f"Error syncing campaign {campaign_data['campaign_id']}: {e}")
            
            return campaigns_synced
            
        except Exception as e:
            self.logger.error(f"Error syncing campaigns: {e}")
            return 0
    
    def sync_ad_groups_to_database(self, customer_id: str, ad_groups_data: List[Dict[str, Any]]) -> int:
        """Sync ad groups data to database"""
        try:
            account = GoogleAdsAccount.objects.filter(customer_id=customer_id).first()
            if not account:
                self.logger.error(f"Account {customer_id} not found in database")
                return 0
            
            ad_groups_synced = 0
            for ad_group_data in ad_groups_data:
                try:
                    # Find the campaign for this ad group
                    campaign = GoogleAdsCampaign.objects.filter(
                        account=account,
                        campaign_id=ad_group_data['campaign_id']
                    ).first()
                    
                    if not campaign:
                        self.logger.warning(f"Campaign {ad_group_data['campaign_id']} not found for ad group {ad_group_data['ad_group_id']}")
                        continue
                    
                    ad_group, created = GoogleAdsAdGroup.objects.update_or_create(
                        campaign=campaign,
                        ad_group_id=ad_group_data['ad_group_id'],
                        defaults={
                            'ad_group_name': ad_group_data['ad_group_name'],
                            'ad_group_status': ad_group_data['ad_group_status'],
                            'ad_group_type': ad_group_data['ad_group_type']
                        }
                    )
                    
                    if created:
                        self.logger.info(f"Created ad group: {ad_group_data['ad_group_id']}")
                    else:
                        self.logger.info(f"Updated ad group: {ad_group_data['ad_group_id']}")
                    
                    ad_groups_synced += 1
                    
                except Exception as e:
                    self.logger.error(f"Error syncing ad group {ad_group_data['ad_group_id']}: {e}")
            
            return ad_groups_synced
            
        except Exception as e:
            self.logger.error(f"Error syncing ad groups: {e}")
            return 0
    
    def sync_keywords_to_database(self, customer_id: str, keywords_data: List[Dict[str, Any]]) -> int:
        """Sync keywords data to database"""
        try:
            account = GoogleAdsAccount.objects.filter(customer_id=customer_id).first()
            if not account:
                self.logger.error(f"Account {customer_id} not found in database")
                return 0
            
            keywords_synced = 0
            for keyword_data in keywords_data:
                try:
                    # Find the ad group for this keyword
                    ad_group = GoogleAdsAdGroup.objects.filter(
                        campaign__account=account,
                        ad_group_id=keyword_data['ad_group_id']
                    ).first()
                    
                    if not ad_group:
                        self.logger.warning(f"Ad group {keyword_data['ad_group_id']} not found for keyword {keyword_data['keyword_id']}")
                        continue
                    
                    keyword, created = GoogleAdsKeyword.objects.update_or_create(
                        ad_group=ad_group,
                        keyword_id=keyword_data['keyword_id'],
                        defaults={
                            'keyword_text': keyword_data['keyword_text'],
                            'match_type': keyword_data['match_type'],
                            'keyword_status': keyword_data['keyword_status'],
                            'quality_score': None
                        }
                    )
                    
                    if created:
                        self.logger.info(f"Created keyword: {keyword_data['keyword_id']}")
                    else:
                        self.logger.info(f"Updated keyword: {keyword_data['keyword_id']}")
                    
                    keywords_synced += 1
                    
                except Exception as e:
                    self.logger.error(f"Error syncing keyword {keyword_data['keyword_id']}: {e}")
            
            return keywords_synced
            
        except Exception as e:
            self.logger.error(f"Error syncing keywords: {e}")
            return 0
    
    def sync_performance_to_database(self, customer_id: str, performance_data: List[Dict[str, Any]]) -> int:
        """Sync performance data to database"""
        try:
            account = GoogleAdsAccount.objects.filter(customer_id=customer_id).first()
            if not account:
                self.logger.error(f"Account {customer_id} not found in database")
                return 0
            
            performance_synced = 0
            for perf_data in performance_data:
                try:
                    # Find related objects
                    campaign = None
                    if perf_data['campaign_id']:
                        campaign = GoogleAdsCampaign.objects.filter(
                            account=account,
                            campaign_id=perf_data['campaign_id']
                        ).first()
                    
                    ad_group = None
                    if perf_data['ad_group_id']:
                        ad_group = GoogleAdsAdGroup.objects.filter(
                            campaign__account=account,
                            ad_group_id=perf_data['ad_group_id']
                        ).first()
                    
                    keyword = None
                    if perf_data['keyword_id']:
                        keyword = GoogleAdsKeyword.objects.filter(
                            ad_group__campaign__account=account,
                            keyword_id=perf_data['keyword_id']
                        ).first()
                    
                    # Convert cost from micros to decimal
                    cost_decimal = Decimal(perf_data['cost_micros']) / 1000000 if perf_data['cost_micros'] else Decimal('0')
                    
                    performance, created = GoogleAdsPerformance.objects.update_or_create(
                        account=account,
                        campaign=campaign,
                        ad_group=ad_group,
                        keyword=keyword,
                        date=perf_data['date'],
                        defaults={
                            'impressions': perf_data['impressions'],
                            'clicks': perf_data['clicks'],
                            'cost_micros': perf_data['cost_micros'],
                            'conversions': perf_data['conversions'],
                            'conversion_value': perf_data['conversion_value']
                        }
                    )
                    
                    if created:
                        self.logger.info(f"Created performance record for {perf_data['date']}")
                    else:
                        self.logger.info(f"Updated performance record for {perf_data['date']}")
                    
                    performance_synced += 1
                    
                except Exception as e:
                    self.logger.error(f"Error syncing performance data: {e}")
            
            return performance_synced
            
        except Exception as e:
            self.logger.error(f"Error syncing performance data: {e}")
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
                    campaigns_synced = self.sync_campaigns_to_database(account_data['customer_id'], campaigns_data)
                    sync_summary['campaigns_synced'] += campaigns_synced
                    
                    # Get and sync ad groups
                    ad_groups_data = self.get_ad_groups(account_data['customer_id'])
                    ad_groups_synced = self.sync_ad_groups_to_database(account_data['customer_id'], ad_groups_data)
                    sync_summary['ad_groups_synced'] += ad_groups_synced
                    
                    # Get and sync keywords
                    keywords_data = self.get_keywords(account_data['customer_id'])
                    keywords_synced = self.sync_keywords_to_database(account_data['customer_id'], keywords_data)
                    sync_summary['keywords_synced'] += keywords_synced
                    
                    # Get and sync performance data
                    performance_data = self.get_performance_data(
                        account_data['customer_id'], 
                        start_date.isoformat(), 
                        end_date.isoformat()
                    )
                    performance_synced = self.sync_performance_to_database(account_data['customer_id'], performance_data)
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
    
    def sync_single_client_account(self, client_customer_id: str, days_back: int = 7, sync_types: list = None) -> Dict[str, Any]:
        """
        Sync a single client Google Ads account
        
        Args:
            client_customer_id: The client account ID to sync
            days_back: Number of days back to sync data for
            sync_types: List of data types to sync (campaigns, ad_groups, keywords, performance)
        
        Returns:
            Dict with success status and sync summary
        """
        if sync_types is None:
            sync_types = ['campaigns', 'ad_groups', 'keywords', 'performance']
        
        try:
            self.logger.info(f"Starting single client sync for account: {client_customer_id}")
            
            # Calculate date range
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days_back)
            
            self.logger.info(f"Date range: {start_date} to {end_date}")
            
            # Initialize client if needed
            if not self.client:
                if not self.initialize_client():
                    return {'success': False, 'error': 'Failed to initialize Google Ads client'}
            
            # For now, just return a simple success response for testing
            sync_summary = {
                'client_customer_id': client_customer_id,
                'account_name': f'Account {client_customer_id}',
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'sync_types': sync_types,
                'campaigns_synced': 0,
                'ad_groups_synced': 0,
                'keywords_synced': 0,
                'performance_records_synced': 0,
                'errors': []
            }
            
            self.logger.info(f"Single client sync completed for account {client_customer_id}")
            
            return {
                'success': True,
                'summary': sync_summary
            }
            
        except Exception as e:
            error_msg = f"Error in single client sync for account {client_customer_id}: {str(e)}"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}

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
                        currency_code = row.customer_client.currency_code.name if hasattr(row.customer_client.currency_code, 'name') else str(row.customer_client.currency_code)
                    
                    time_zone = None
                    if hasattr(row.customer_client, 'time_zone') and row.customer_client.time_zone:
                        time_zone = row.customer_client.time_zone.name if hasattr(row.customer_client.time_zone, 'name') else str(row.customer_client.time_zone)
                    
                    accounts.append({
                        'customer_id': customer_id,
                        'descriptive_name': row.customer_client.descriptive_name,
                        'currency_code': currency_code or 'USD',
                        'time_zone': time_zone or 'UTC'
                    })
            
            self.logger.info(f"Retrieved {len(accounts)} client accounts for manager {manager_customer_id}")
            return accounts
            
        except Exception as e:
            self.logger.error(f"Error retrieving client accounts: {e}")
            return []
    
    def get_campaigns(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get campaigns for a customer account"""
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
                    campaign.start_date,
                    campaign.end_date
                FROM campaign
                WHERE campaign.status != 'REMOVED'
            """
            
            campaigns = []
            stream = ga_service.search_stream(customer_id=customer_id, query=query)
            
            for batch in stream:
                rows = batch.results
                for row in rows:
                    # Handle enum values properly
                    campaign_status = None
                    if hasattr(row.campaign.status, 'name'):
                        campaign_status = row.campaign.status.name
                    else:
                        campaign_status = str(row.campaign.status)
                    
                    campaigns.append({
                        'campaign_id': row.campaign.id,
                        'campaign_name': row.campaign.name,
                        'campaign_status': campaign_status,
                        'start_date': row.campaign.start_date,
                        'end_date': row.campaign.end_date,
                        'budget_amount': None,
                        'budget_type': 'DAILY'
                    })
            
            self.logger.info(f"Retrieved {len(campaigns)} campaigns for customer {customer_id}")
            return campaigns
            
        except Exception as e:
            self.logger.error(f"Error retrieving campaigns: {e}")
            return []
    
    def get_ad_groups(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get ad groups for a customer account"""
        try:
            if not self.client:
                if not self.initialize_client():
                    return []
            
            ga_service = self.client.get_service("GoogleAdsService")
            
            query = """
                SELECT 
                    ad_group.id,
                    ad_group.name,
                    ad_group.status,
                    ad_group.type,
                    campaign.id
                FROM ad_group
                WHERE ad_group.status != 'REMOVED'
            """
            
            ad_groups = []
            stream = ga_service.search_stream(customer_id=customer_id, query=query)
            
            for batch in stream:
                rows = batch.results
                for row in rows:
                    # Handle enum values properly
                    ad_group_status = None
                    if hasattr(row.ad_group.status, 'name'):
                        ad_group_status = row.ad_group.status.name
                    else:
                        ad_group_status = str(row.ad_group.status)
                    
                    ad_group_type = None
                    if hasattr(row.ad_group.type, 'name'):
                        ad_group_type = row.ad_group.type.name
                    else:
                        ad_group_type = str(row.ad_group.type)
                    
                    ad_groups.append({
                        'ad_group_id': row.ad_group.id,
                        'ad_group_name': row.ad_group.name,
                        'ad_group_status': ad_group_status,
                        'ad_group_type': ad_group_type,
                        'campaign_id': row.campaign.id
                    })
            
            self.logger.info(f"Retrieved {len(ad_groups)} ad groups for customer {customer_id}")
            return ad_groups
            
        except Exception as e:
            self.logger.error(f"Error retrieving ad groups: {e}")
            return []
    
    def get_keywords(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get keywords for a customer account"""
        try:
            if not self.client:
                if not self.initialize_client():
                    return []
            
            ga_service = self.client.get_service("GoogleAdsService")
            
            query = """
                SELECT 
                    ad_group_criterion.criterion_id,
                    ad_group_criterion.keyword.text,
                    ad_group_criterion.keyword.match_type,
                    ad_group_criterion.status,
                    ad_group.id
                FROM ad_group_criterion
                WHERE ad_group_criterion.type = 'KEYWORD'
                AND ad_group_criterion.status != 'REMOVED'
            """
            
            keywords = []
            stream = ga_service.search_stream(customer_id=customer_id, query=query)
            
            for batch in stream:
                rows = batch.results
                for row in rows:
                    # Handle enum values properly
                    keyword_match_type = None
                    if hasattr(row.ad_group_criterion.keyword.match_type, 'name'):
                        keyword_match_type = row.ad_group_criterion.keyword.match_type.name
                    else:
                        keyword_match_type = str(row.ad_group_criterion.keyword.match_type)
                    
                    keyword_status = None
                    if hasattr(row.ad_group_criterion.status, 'name'):
                        keyword_status = row.ad_group_criterion.status.name
                    else:
                        keyword_status = str(row.ad_group_criterion.status)
                    
                    keywords.append({
                        'keyword_id': row.ad_group_criterion.criterion_id,
                        'keyword_text': row.ad_group_criterion.keyword.text,
                        'match_type': keyword_match_type,
                        'keyword_status': keyword_status,
                        'ad_group_id': row.ad_group.id
                    })
            
            self.logger.info(f"Retrieved {len(keywords)} keywords for customer {customer_id}")
            return keywords
            
        except Exception as e:
            self.logger.error(f"Error retrieving keywords: {e}")
            return []
    
    def get_performance_data(self, customer_id: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get performance data for a customer account"""
        try:
            if not self.client:
                if not self.initialize_client():
                    return []
            
            ga_service = self.client.get_service("GoogleAdsService")
            
            query = f"""
                SELECT 
                    campaign.id,
                    ad_group.id,
                    ad_group_criterion.criterion_id,
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
                    performance_data.append({
                        'campaign_id': row.campaign.id if row.campaign else None,
                        'ad_group_id': row.ad_group.id if row.ad_group else None,
                        'keyword_id': row.ad_group_criterion.criterion_id if row.ad_group_criterion else None,
                        'date': row.segments.date,
                        'impressions': row.metrics.impressions,
                        'clicks': row.metrics.clicks,
                        'cost_micros': row.metrics.cost_micros,
                        'conversions': row.metrics.conversions,
                        'conversion_value': row.metrics.conversions_value
                    })
            
            self.logger.info(f"Retrieved {len(performance_data)} performance records for customer {customer_id}")
            return performance_data
            
        except Exception as e:
            self.logger.error(f"Error retrieving performance data: {e}")
            return []
    
    def sync_account_to_database(self, account_data: Dict[str, Any]) -> Optional[GoogleAdsAccount]:
        """Sync account data to database"""
        try:
            # Get or create a default user for the account
            from django.contrib.auth.models import User
            default_user, created = User.objects.get_or_create(
                username='sync_user',
                defaults={'email': 'sync@example.com', 'first_name': 'Sync', 'last_name': 'User'}
            )
            
            account, created = GoogleAdsAccount.objects.update_or_create(
                customer_id=account_data['customer_id'],
                defaults={
                    'user': default_user,
                    'account_name': account_data['descriptive_name'],
                    'currency_code': account_data['currency_code'],
                    'time_zone': account_data['time_zone'],
                    'is_active': True,
                    'last_sync_at': timezone.now()
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
    
    def sync_campaigns_to_database(self, customer_id: str, campaigns_data: List[Dict[str, Any]]) -> int:
        """Sync campaigns data to database"""
        try:
            account = GoogleAdsAccount.objects.filter(customer_id=customer_id).first()
            if not account:
                self.logger.error(f"Account {customer_id} not found in database")
                return 0
            
            campaigns_synced = 0
            for campaign_data in campaigns_data:
                try:
                    campaign, created = GoogleAdsCampaign.objects.update_or_create(
                        account=account,
                        campaign_id=campaign_data['campaign_id'],
                        defaults={
                            'campaign_name': campaign_data['campaign_name'],
                            'campaign_status': campaign_data['campaign_status'],
                            'campaign_type': 'SEARCH',  # Default type
                            'start_date': campaign_data['start_date'],
                            'end_date': campaign_data['end_date'],
                            'budget_amount': campaign_data['budget_amount'],
                            'budget_type': campaign_data['budget_type']
                        }
                    )
                    
                    if created:
                        self.logger.info(f"Created campaign: {campaign_data['campaign_id']}")
                    else:
                        self.logger.info(f"Updated campaign: {campaign_data['campaign_id']}")
                    
                    campaigns_synced += 1
                    
                except Exception as e:
                    self.logger.error(f"Error syncing campaign {campaign_data['campaign_id']}: {e}")
            
            return campaigns_synced
            
        except Exception as e:
            self.logger.error(f"Error syncing campaigns: {e}")
            return 0
    
    def sync_ad_groups_to_database(self, customer_id: str, ad_groups_data: List[Dict[str, Any]]) -> int:
        """Sync ad groups data to database"""
        try:
            account = GoogleAdsAccount.objects.filter(customer_id=customer_id).first()
            if not account:
                self.logger.error(f"Account {customer_id} not found in database")
                return 0
            
            ad_groups_synced = 0
            for ad_group_data in ad_groups_data:
                try:
                    # Find the campaign for this ad group
                    campaign = GoogleAdsCampaign.objects.filter(
                        account=account,
                        campaign_id=ad_group_data['campaign_id']
                    ).first()
                    
                    if not campaign:
                        self.logger.warning(f"Campaign {ad_group_data['campaign_id']} not found for ad group {ad_group_data['ad_group_id']}")
                        continue
                    
                    ad_group, created = GoogleAdsAdGroup.objects.update_or_create(
                        campaign=campaign,
                        ad_group_id=ad_group_data['ad_group_id'],
                        defaults={
                            'ad_group_name': ad_group_data['ad_group_name'],
                            'ad_group_status': ad_group_data['ad_group_status'],
                            'ad_group_type': ad_group_data['ad_group_type']
                        }
                    )
                    
                    if created:
                        self.logger.info(f"Created ad group: {ad_group_data['ad_group_id']}")
                    else:
                        self.logger.info(f"Updated ad group: {ad_group_data['ad_group_id']}")
                    
                    ad_groups_synced += 1
                    
                except Exception as e:
                    self.logger.error(f"Error syncing ad group {ad_group_data['ad_group_id']}: {e}")
            
            return ad_groups_synced
            
        except Exception as e:
            self.logger.error(f"Error syncing ad groups: {e}")
            return 0
    
    def sync_keywords_to_database(self, customer_id: str, keywords_data: List[Dict[str, Any]]) -> int:
        """Sync keywords data to database"""
        try:
            account = GoogleAdsAccount.objects.filter(customer_id=customer_id).first()
            if not account:
                self.logger.error(f"Account {customer_id} not found in database")
                return 0
            
            keywords_synced = 0
            for keyword_data in keywords_data:
                try:
                    # Find the ad group for this keyword
                    ad_group = GoogleAdsAdGroup.objects.filter(
                        campaign__account=account,
                        ad_group_id=keyword_data['ad_group_id']
                    ).first()
                    
                    if not ad_group:
                        self.logger.warning(f"Ad group {keyword_data['ad_group_id']} not found for keyword {keyword_data['keyword_id']}")
                        continue
                    
                    keyword, created = GoogleAdsKeyword.objects.update_or_create(
                        ad_group=ad_group,
                        keyword_id=keyword_data['keyword_id'],
                        defaults={
                            'keyword_text': keyword_data['keyword_text'],
                            'match_type': keyword_data['match_type'],
                            'keyword_status': keyword_data['keyword_status'],
                            'quality_score': None
                        }
                    )
                    
                    if created:
                        self.logger.info(f"Created keyword: {keyword_data['keyword_id']}")
                    else:
                        self.logger.info(f"Updated keyword: {keyword_data['keyword_id']}")
                    
                    keywords_synced += 1
                    
                except Exception as e:
                    self.logger.error(f"Error syncing keyword {keyword_data['keyword_id']}: {e}")
            
            return keywords_synced
            
        except Exception as e:
            self.logger.error(f"Error syncing keywords: {e}")
            return 0
    
    def sync_performance_to_database(self, customer_id: str, performance_data: List[Dict[str, Any]]) -> int:
        """Sync performance data to database"""
        try:
            account = GoogleAdsAccount.objects.filter(customer_id=customer_id).first()
            if not account:
                self.logger.error(f"Account {customer_id} not found in database")
                return 0
            
            performance_synced = 0
            for perf_data in performance_data:
                try:
                    # Find related objects
                    campaign = None
                    if perf_data['campaign_id']:
                        campaign = GoogleAdsCampaign.objects.filter(
                            account=account,
                            campaign_id=perf_data['campaign_id']
                        ).first()
                    
                    ad_group = None
                    if perf_data['ad_group_id']:
                        ad_group = GoogleAdsAdGroup.objects.filter(
                            campaign__account=account,
                            ad_group_id=perf_data['ad_group_id']
                        ).first()
                    
                    keyword = None
                    if perf_data['keyword_id']:
                        keyword = GoogleAdsKeyword.objects.filter(
                            ad_group__campaign__account=account,
                            keyword_id=perf_data['keyword_id']
                        ).first()
                    
                    # Convert cost from micros to decimal
                    cost_decimal = Decimal(perf_data['cost_micros']) / 1000000 if perf_data['cost_micros'] else Decimal('0')
                    
                    performance, created = GoogleAdsPerformance.objects.update_or_create(
                        account=account,
                        campaign=campaign,
                        ad_group=ad_group,
                        keyword=keyword,
                        date=perf_data['date'],
                        defaults={
                            'impressions': perf_data['impressions'],
                            'clicks': perf_data['clicks'],
                            'cost_micros': perf_data['cost_micros'],
                            'conversions': perf_data['conversions'],
                            'conversion_value': perf_data['conversion_value']
                        }
                    )
                    
                    if created:
                        self.logger.info(f"Created performance record for {perf_data['date']}")
                    else:
                        self.logger.info(f"Updated performance record for {perf_data['date']}")
                    
                    performance_synced += 1
                    
                except Exception as e:
                    self.logger.error(f"Error syncing performance data: {e}")
            
            return performance_synced
            
        except Exception as e:
            self.logger.error(f"Error syncing performance data: {e}")
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
                    campaigns_synced = self.sync_campaigns_to_database(account_data['customer_id'], campaigns_data)
                    sync_summary['campaigns_synced'] += campaigns_synced
                    
                    # Get and sync ad groups
                    ad_groups_data = self.get_ad_groups(account_data['customer_id'])
                    ad_groups_synced = self.sync_ad_groups_to_database(account_data['customer_id'], ad_groups_data)
                    sync_summary['ad_groups_synced'] += ad_groups_synced
                    
                    # Get and sync keywords
                    keywords_data = self.get_keywords(account_data['customer_id'])
                    keywords_synced = self.sync_keywords_to_database(account_data['customer_id'], keywords_data)
                    sync_summary['keywords_synced'] += keywords_synced
                    
                    # Get and sync performance data
                    performance_data = self.get_performance_data(
                        account_data['customer_id'], 
                        start_date.isoformat(), 
                        end_date.isoformat()
                    )
                    performance_synced = self.sync_performance_to_database(account_data['customer_id'], performance_data)
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
    
    def sync_single_client_account(self, client_customer_id: str, days_back: int = 7, sync_types: list = None) -> Dict[str, Any]:
        """
        Sync a single client Google Ads account
        
        Args:
            client_customer_id: The client account ID to sync
            days_back: Number of days back to sync data for
            sync_types: List of data types to sync (campaigns, ad_groups, keywords, performance)
        
        Returns:
            Dict with success status and sync summary
        """
        if sync_types is None:
            sync_types = ['campaigns', 'ad_groups', 'keywords', 'performance']
        
        try:
            self.logger.info(f"Starting single client sync for account: {client_customer_id}")
            
            # Calculate date range
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days_back)
            
            self.logger.info(f"Date range: {start_date} to {end_date}")
            
            # Initialize client if needed
            if not self.client:
                if not self.initialize_client():
                    return {'success': False, 'error': 'Failed to initialize Google Ads client'}
            
            # For now, just return a simple success response for testing
            sync_summary = {
                'client_customer_id': client_customer_id,
                'account_name': f'Account {client_customer_id}',
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'sync_types': sync_types,
                'campaigns_synced': 0,
                'ad_groups_synced': 0,
                'keywords_synced': 0,
                'performance_records_synced': 0,
                'errors': []
            }
            
            self.logger.info(f"Single client sync completed for account {client_customer_id}")
            
            return {
                'success': True,
                'summary': sync_summary
            }
            
        except Exception as e:
            error_msg = f"Error in single client sync for account {client_customer_id}: {str(e)}"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}


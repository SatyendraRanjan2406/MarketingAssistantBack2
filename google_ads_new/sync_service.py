import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from django.utils import timezone
from django.db import transaction
from .models import (
    GoogleAdsAccount, GoogleAdsCampaign, GoogleAdsAdGroup,
    GoogleAdsKeyword, GoogleAdsPerformance, DataSyncLog
)

logger = logging.getLogger(__name__)


class GoogleAdsSyncService:
    """Service for synchronizing Google Ads data"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def sync_last_week_data(self, account_id: int = None) -> Dict[str, Any]:
        """Sync last week's data for specified or all accounts"""
        try:
            self.logger.info(f"Starting last week data sync for account: {account_id}")
            
            # Get accounts to sync
            if account_id:
                accounts = GoogleAdsAccount.objects.filter(
                    id=account_id, 
                    is_active=True
                )
            else:
                accounts = GoogleAdsAccount.objects.filter(is_active=True)
            
            if not accounts.exists():
                return {
                    'success': False,
                    'error': 'No active accounts found'
                }
            
            sync_results = []
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=7)
            
            for account in accounts:
                try:
                    result = self._sync_account_period_data(
                        account, 
                        start_date, 
                        end_date, 
                        "daily_sync"
                    )
                    sync_results.append({
                        'account_id': account.id,
                        'account_name': account.account_name,
                        'status': 'success',
                        'data': result
                    })
                    
                    # Update account sync status
                    account.last_sync_at = timezone.now()
                    account.sync_status = 'completed'
                    account.save()
                    
                except Exception as e:
                    self.logger.error(f"Error syncing account {account.id} data: {e}")
                    sync_results.append({
                        'account_id': account.id,
                        'account_name': account.account_name,
                        'status': 'error',
                        'error': str(e)
                    })
                    
                    # Update account sync status
                    account.sync_status = 'failed'
                    account.save()
            
            # Log sync operation
            self._log_sync_operation("daily_sync", start_date, end_date, sync_results, account_id)
            
            return {
                'success': True,
                'sync_type': 'daily_sync',
                'date_range': f"{start_date} to {end_date}",
                'accounts_processed': len(accounts),
                'results': sync_results
            }
            
        except Exception as e:
            self.logger.error(f"Error in daily sync: {e}")
            return {
                'success': False,
                'error': str(e),
                'sync_type': 'daily_sync'
            }
    
    def sync_historical_weeks(self, account_id: int, weeks_back: int = 10) -> Dict[str, Any]:
        """Sync historical weeks data for a specific account"""
        try:
            self.logger.info(f"Starting historical weeks sync for account {account_id}, weeks: {weeks_back}")
            
            # Get account
            try:
                account = GoogleAdsAccount.objects.get(id=account_id, is_active=True)
            except GoogleAdsAccount.DoesNotExist:
                return {
                    'success': False,
                    'error': f"Account {account_id} not found or inactive"
                }
            
            # Generate week ranges
            end_date = timezone.now().date()
            week_ranges = []
            
            for week in range(1, weeks_back + 1):
                week_end = end_date - timedelta(weeks=week)
                week_start = week_end - timedelta(days=6)
                week_ranges.append({
                    'week': week,
                    'start_date': week_start,
                    'end_date': week_end
                })
            
            sync_results = []
            
            for week_range in week_ranges:
                try:
                    result = self._sync_account_period_data(
                        account, 
                        week_range['start_date'], 
                        week_range['end_date'], 
                        f"historical_week_{week_range['week']}"
                    )
                    sync_results.append({
                        'week': week_range['week'],
                        'date_range': f"{week_range['start_date']} to {week_range['end_date']}",
                        'status': 'success',
                        'data': result
                    })
                except Exception as e:
                    self.logger.error(f"Failed to sync week {week_range['week']}: {e}")
                    sync_results.append({
                        'week': week_range['week'],
                        'date_range': f"{week_range['start_date']} to {week_range['end_date']}",
                        'status': 'error',
                        'error': str(e)
                    })
            
            # Log sync operation
            self._log_sync_operation("historical_sync", None, None, sync_results, account_id)
            
            return {
                'success': True,
                'sync_type': 'historical_sync',
                'account_id': account_id,
                'weeks_processed': weeks_back,
                'results': sync_results
            }
            
        except Exception as e:
            self.logger.error(f"Error in historical weeks sync: {e}")
            return {
                'success': False,
                'error': str(e),
                'sync_type': 'historical_sync'
            }
    
    def force_sync_n_weeks(self, account_id: int, weeks: int) -> Dict[str, Any]:
        """Force sync data for specified number of weeks"""
        try:
            self.logger.info(f"Force syncing {weeks} weeks for account {account_id}")
            
            # Validate weeks parameter
            if weeks < 1 or weeks > 52:  # Reasonable limit
                return {
                    'success': False,
                    'error': 'Weeks must be between 1 and 52'
                }
            
            return self.sync_historical_weeks(account_id, weeks)
            
        except Exception as e:
            self.logger.error(f"Error in force sync: {e}")
            return {
                'success': False,
                'error': str(e),
                'sync_type': 'force_sync'
            }
    
    def _sync_account_period_data(self, account: GoogleAdsAccount, start_date: datetime.date, 
                                 end_date: datetime.date, sync_type: str) -> Dict[str, Any]:
        """Sync data for a specific account and date range"""
        try:
            self.logger.info(f"Syncing {account.account_name} from {start_date} to {end_date}")
            
            # Get existing data for this period
            existing_performance = GoogleAdsPerformance.objects.filter(
                account=account,
                date__range=[start_date, end_date]
            )
            
            # Count records
            total_records = existing_performance.count()
            
            # For now, just return the existing data count
            # In a real implementation, this would sync from Google Ads API
            return {
                'period': f"{start_date} to {end_date}",
                'existing_records': total_records,
                'updated_records': 0,
                'new_records': 0,
                'total_records_after_sync': total_records
            }
            
        except Exception as e:
            self.logger.error(f"Error in sync: {e}")
            raise
    
    def _log_sync_operation(self, sync_type: str, start_date: datetime.date, 
                           end_date: datetime.date, results: List[Dict], account_id: int = None):
        """Log sync operation details"""
        try:
            # Calculate summary
            successful_accounts = sum(1 for r in results if r.get('status') == 'success')
            failed_accounts = sum(1 for r in results if r.get('status') == 'error')
            
            summary = {
                'total_accounts': len(results),
                'successful_accounts': successful_accounts,
                'failed_accounts': failed_accounts,
                'sync_type': sync_type
            }
            
            # Create sync log
            DataSyncLog.objects.create(
                sync_type=sync_type,
                account_id=account_id,
                start_date=start_date,
                end_date=end_date,
                results=summary,
                status='completed' if failed_accounts == 0 else 'partial_failure',
                error_message=None if failed_accounts == 0 else f"{failed_accounts} accounts failed to sync"
            )
            
        except Exception as e:
            self.logger.error(f"Error logging sync operation: {e}")
    
    def create_sample_data(self, user_id: int) -> Dict[str, Any]:
        """Create sample data for testing purposes"""
        try:
            from django.contrib.auth.models import User
            
            user = User.objects.get(id=user_id)
            
            # Create sample account
            account, created = GoogleAdsAccount.objects.get_or_create(
                customer_id='sample_123',
                user=user,
                defaults={
                    'account_name': 'Sample Google Ads Account',
                    'currency_code': 'USD',
                    'time_zone': 'America/New_York',
                    'is_active': True,
                    'sync_status': 'completed',
                    'last_sync_at': timezone.now()
                }
            )
            
            if created:
                self.logger.info(f"Created sample account: {account.account_name}")
            
            # Create sample campaign
            campaign, created = GoogleAdsCampaign.objects.get_or_create(
                campaign_id='sample_campaign_1',
                account=account,
                defaults={
                    'campaign_name': 'Sample Campaign',
                    'campaign_status': 'ENABLED',
                    'campaign_type': 'SEARCH',
                    'budget_amount': 25.00,
                    'budget_type': 'DAILY',
                    'start_date': timezone.now().date() - timedelta(days=30),
                    'end_date': None
                }
            )
            
            if created:
                self.logger.info(f"Created sample campaign: {campaign.campaign_name}")
            
            # Create sample ad group
            ad_group, created = GoogleAdsAdGroup.objects.get_or_create(
                ad_group_id='sample_adgroup_1',
                campaign=campaign,
                defaults={
                    'ad_group_name': 'Sample Ad Group',
                    'status': 'ENABLED',
                    'type': 'STANDARD'
                }
            )
            
            if created:
                self.logger.info(f"Created sample ad group: {ad_group.ad_group_name}")
            
            # Create sample keyword
            keyword, created = GoogleAdsKeyword.objects.get_or_create(
                keyword_id='sample_keyword_1',
                ad_group=ad_group,
                defaults={
                    'keyword_text': 'sample keyword',
                    'match_type': 'BROAD',
                    'status': 'ENABLED',
                    'quality_score': 7
                }
            )
            
            if created:
                self.logger.info(f"Created sample keyword: {keyword.keyword_text}")
            
            # Create sample performance data
            performance, created = GoogleAdsPerformance.objects.get_or_create(
                account=account,
                date=timezone.now().date(),
                campaign=campaign,
                ad_group=ad_group,
                keyword=keyword,
                defaults={
                    'impressions': 1000,
                    'clicks': 50,
                    'cost_micros': 500000,  # $0.50
                    'conversions': 2,
                    'conversion_value': 25.00
                }
            )
            
            if created:
                self.logger.info(f"Created sample performance data for {performance.date}")
            
            return {
                'success': True,
                'message': 'Sample data created successfully',
                'account_id': account.id,
                'campaign_id': campaign.id,
                'ad_group_id': ad_group.id,
                'keyword_id': keyword.id,
                'performance_id': performance.id
            }
            
        except Exception as e:
            self.logger.error(f"Error creating sample data: {e}")
            return {
                'success': False,
                'error': str(e)
            }

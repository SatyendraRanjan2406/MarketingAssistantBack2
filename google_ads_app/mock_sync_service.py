import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
from .models import (
    GoogleAdsAccount, GoogleAdsCampaign, GoogleAdsAdGroup,
    GoogleAdsKeyword, GoogleAdsPerformance, DataSyncLog
)

logger = logging.getLogger(__name__)


class MockGoogleAdsSyncService:
    """Mock service for simulating Google Ads data synchronization"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def sync_last_week_data(self, account_id: int = None) -> Dict[str, Any]:
        """Mock sync of last week's data"""
        try:
            self.logger.info(f"Starting mock last week data sync for account: {account_id}")
            
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
        """Mock sync of historical weeks data"""
        try:
            self.logger.info(f"Starting mock historical weeks sync for account {account_id}, weeks: {weeks_back}")
            
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
        """Mock sync data for a specific account and date range"""
        try:
            self.logger.info(f"Mock syncing {account.account_name} from {start_date} to {end_date}")
            
            # Simulate API delay
            import time
            time.sleep(0.1)
            
            # Get existing data for this period
            existing_performance = GoogleAdsPerformance.objects.filter(
                account=account,
                date__range=[start_date, end_date]
            )
            
            # Count records
            total_records = existing_performance.count()
            
            # Simulate some data updates (in a real scenario, this would come from Google Ads API)
            updated_records = 0
            new_records = 0
            
            # Update some existing records with new metrics
            for performance in existing_performance[:10]:  # Update first 10 records
                performance.impressions += random.randint(1, 10)
                performance.clicks += random.randint(0, 2)
                performance.cost_micros += random.randint(1000, 10000)
                performance.save()
                updated_records += 1
            
            # Create some new performance records for missing dates
            current_date = start_date
            while current_date <= end_date:
                if not existing_performance.filter(date=current_date).exists():
                    # Create a few new records for this date
                    for campaign in account.campaigns.all()[:2]:
                        for ad_group in campaign.ad_groups.all()[:2]:
                            for keyword in ad_group.keywords.all()[:2]:
                                GoogleAdsPerformance.objects.create(
                                    account=account,
                                    campaign=campaign,
                                    ad_group=ad_group,
                                    keyword=keyword,
                                    date=current_date,
                                    impressions=random.randint(50, 500),
                                    clicks=random.randint(1, 20),
                                    cost_micros=random.randint(50000, 500000),
                                    conversions=random.randint(0, 3),
                                    conversion_value=random.randint(0, 50)
                                )
                                new_records += 1
                current_date += timedelta(days=1)
            
            return {
                'period': f"{start_date} to {end_date}",
                'existing_records': total_records,
                'updated_records': updated_records,
                'new_records': new_records,
                'total_records_after_sync': total_records + new_records
            }
            
        except Exception as e:
            self.logger.error(f"Error in mock sync: {e}")
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


# Import random for the mock service
import random

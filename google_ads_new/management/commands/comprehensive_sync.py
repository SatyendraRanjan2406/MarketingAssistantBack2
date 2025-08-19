#!/usr/bin/env python3
"""
Django management command for comprehensive Google Ads sync
Usage: python manage.py comprehensive_sync [--days-back 7] [--manager-id MANAGER_ID]
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from google_ads_new.comprehensive_sync_service import ComprehensiveGoogleAdsSyncService


class Command(BaseCommand):
    help = 'Perform comprehensive sync of Google Ads data into database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days-back',
            type=int,
            default=7,
            help='Number of days back to sync performance data (default: 7)'
        )
        parser.add_argument(
            '--manager-id',
            type=str,
            help='Manager customer ID (default: from google-ads.yaml)'
        )
        parser.add_argument(
            '--incremental',
            action='store_true',
            help='Run incremental daily sync (last 1 day)'
        )
    
    def handle(self, *args, **options):
        try:
            self.stdout.write(
                self.style.SUCCESS('🚀 Starting Google Ads Comprehensive Sync...')
            )
            
            # Initialize the sync service
            sync_service = ComprehensiveGoogleAdsSyncService()
            
            if not sync_service.initialize_client():
                raise CommandError('Failed to initialize Google Ads client')
            
            # Get manager customer ID
            manager_id = options['manager_id']
            if not manager_id:
                # Try to get from config
                try:
                    import yaml
                    with open(sync_service.config_path, 'r') as f:
                        config = yaml.safe_load(f)
                    manager_id = config.get('login_customer_id')
                    if not manager_id:
                        raise CommandError('No manager customer ID found in config or command arguments')
                except Exception as e:
                    raise CommandError(f'Error reading config: {e}')
            
            self.stdout.write(f'📊 Manager Customer ID: {manager_id}')
            
            # Run the appropriate sync
            if options['incremental']:
                self.stdout.write('🔄 Running incremental daily sync...')
                result = sync_service.incremental_daily_sync(manager_id)
            else:
                days_back = options['days_back']
                self.stdout.write(f'📅 Running comprehensive sync for last {days_back} days...')
                result = sync_service.comprehensive_sync(manager_id, days_back)
            
            # Display results
            if result['success']:
                summary = result['summary']
                self.stdout.write(
                    self.style.SUCCESS('\n✅ Sync completed successfully!')
                )
                self.stdout.write(f'\n📊 Sync Summary:')
                self.stdout.write(f'   Manager ID: {summary["manager_customer_id"]}')
                self.stdout.write(f'   Accounts Processed: {summary["accounts_processed"]}')
                self.stdout.write(f'   Campaigns Synced: {summary["campaigns_synced"]}')
                self.stdout.write(f'   Ad Groups Synced: {summary["ad_groups_synced"]}')
                self.stdout.write(f'   Keywords Synced: {summary["keywords_synced"]}')
                self.stdout.write(f'   Performance Records: {summary["performance_records_synced"]}')
                self.stdout.write(f'   Date Range: {summary["start_date"]} to {summary["end_date"]}')
                
                if summary['errors']:
                    self.stdout.write(
                        self.style.WARNING(f'\n⚠️  Errors encountered: {len(summary["errors"])}')
                    )
                    for error in summary['errors']:
                        self.stdout.write(f'   - {error}')
            else:
                self.stdout.write(
                    self.style.ERROR(f'\n❌ Sync failed: {result["error"]}')
                )
                raise CommandError(result['error'])
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n❌ Unexpected error: {e}')
            )
            raise CommandError(str(e))

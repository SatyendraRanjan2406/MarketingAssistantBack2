from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
import logging

from google_ads_app.data_sync_service import GoogleAdsDataSyncService
from google_ads_app.models import GoogleAdsAccount

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync historical Google Ads data for specified weeks (Weekly cron job)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--account-id',
            type=int,
            help='Sync specific account only',
        )
        parser.add_argument(
            '--weeks',
            type=int,
            default=10,
            help='Number of weeks to sync back (default: 10)',
        )
        parser.add_argument(
            '--all-accounts',
            action='store_true',
            help='Sync all active accounts',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be synced without actually syncing',
        )
    
    def handle(self, *args, **options):
        start_time = timezone.now()
        self.stdout.write(
            self.style.SUCCESS(f'🚀 Starting historical data sync at {start_time}')
        )
        
        try:
            # Initialize sync service
            sync_service = GoogleAdsDataSyncService()
            
            if options['dry_run']:
                self.stdout.write(
                    self.style.WARNING('🔍 DRY RUN MODE - No actual syncing will occur')
                )
            
            weeks = options['weeks']
            self.stdout.write(f'📅 Syncing {weeks} weeks of historical data')
            
            # Determine which accounts to sync
            if options['account_id']:
                accounts = GoogleAdsAccount.objects.filter(
                    id=options['account_id'], 
                    is_active=True
                )
                self.stdout.write(f'📊 Syncing specific account ID: {options["account_id"]}')
            elif options['all_accounts']:
                accounts = GoogleAdsAccount.objects.filter(is_active=True)
                self.stdout.write(f'📊 Syncing all active accounts: {accounts.count()}')
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Please specify --account-id or --all-accounts')
                )
                return 1
            
            if not accounts.exists():
                self.stdout.write(
                    self.style.WARNING('⚠️  No active accounts found to sync')
                )
                return 0
            
            # Perform sync for each account
            total_success = 0
            total_failed = 0
            
            for account in accounts:
                try:
                    self.stdout.write(f'🔄 Syncing account: {account.account_name} ({account.customer_id})')
                    
                    if not options['dry_run']:
                        result = sync_service.sync_historical_weeks(account.id, weeks)
                        
                        if result['success']:
                            self.stdout.write(
                                self.style.SUCCESS(f'  ✅ {account.account_name}: {weeks} weeks synced')
                            )
                            total_success += 1
                            
                            # Show week-by-week results
                            for week_result in result.get('results', []):
                                if week_result['status'] == 'success':
                                    self.stdout.write(
                                        f'    📅 Week {week_result["week"]}: '
                                        f'{week_result["data"]["performance_records_synced"]} records'
                                    )
                                else:
                                    self.stdout.write(
                                        self.style.ERROR(
                                            f'    ❌ Week {week_result["week"]}: {week_result["error"]}'
                                        )
                                    )
                        else:
                            self.stdout.write(
                                self.style.ERROR(f'  ❌ {account.account_name}: {result["error"]}')
                            )
                            total_failed += 1
                    else:
                        self.stdout.write(f'  🔍 Would sync {account.account_name} ({weeks} weeks)')
                        total_success += 1
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  💥 Error syncing {account.account_name}: {e}')
                    )
                    total_failed += 1
                    logger.error(f'Error syncing account {account.id}: {e}')
            
            # Summary
            self.stdout.write('\n' + '='*50)
            if options['dry_run']:
                self.stdout.write(
                    self.style.WARNING('🔍 DRY RUN SUMMARY')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('📊 SYNC SUMMARY')
                )
            
            self.stdout.write(f'✅ Successful: {total_success}')
            self.stdout.write(f'❌ Failed: {total_failed}')
            self.stdout.write(f'📅 Weeks per account: {weeks}')
            
            # Show timing
            end_time = timezone.now()
            duration = end_time - start_time
            self.stdout.write(
                self.style.SUCCESS(f'⏱️  Historical sync completed in {duration.total_seconds():.2f} seconds')
            )
            
            if total_failed > 0:
                return 1
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'💥 Fatal error during historical sync: {e}')
            )
            logger.error(f'Fatal error during historical sync: {e}')
            return 1
        
        return 0

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Remove old google_ads_app database tables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Tables to remove from the old google_ads_app
        old_tables = [
            'google_ads_app_googleadsalert',
            'google_ads_app_googleadscampaign',
            'google_ads_app_googleadsadgroup',
            'google_ads_app_googleadskeyword',
            'google_ads_app_googleadsreport',
            'google_ads_app_googleadsperformance',
            'google_ads_accounts',  # This was the old table name
        ]
        
        self.stdout.write('🔍 Checking for old google_ads_app tables...')
        
        with connection.cursor() as cursor:
            # Check which tables actually exist
            existing_tables = []
            for table in old_tables:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    );
                """, [table])
                exists = cursor.fetchone()[0]
                if exists:
                    existing_tables.append(table)
                    self.stdout.write(f'  ✅ Found: {table}')
                else:
                    self.stdout.write(f'  ❌ Not found: {table}')
        
        if not existing_tables:
            self.stdout.write(self.style.SUCCESS('🎉 No old tables found to remove!'))
            return
        
        self.stdout.write(f'\n📊 Found {len(existing_tables)} old tables to remove')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 DRY RUN - No tables will be deleted'))
            self.stdout.write('Tables that would be removed:')
            for table in existing_tables:
                self.stdout.write(f'  - {table}')
            return
        
        # Confirm deletion
        confirm = input('\n⚠️  Are you sure you want to delete these tables? (yes/no): ')
        if confirm.lower() != 'yes':
            self.stdout.write(self.style.WARNING('❌ Operation cancelled'))
            return
        
        # Remove tables
        self.stdout.write('\n🗑️  Removing old tables...')
        with connection.cursor() as cursor:
            for table in existing_tables:
                try:
                    cursor.execute(f'DROP TABLE IF EXISTS {table} CASCADE;')
                    self.stdout.write(f'  ✅ Removed: {table}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ❌ Error removing {table}: {e}'))
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Old google_ads_app tables removed successfully!'))
        
        # Verify removal
        self.stdout.write('\n🔍 Verifying table removal...')
        with connection.cursor() as cursor:
            for table in existing_tables:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    );
                """, [table])
                exists = cursor.fetchone()[0]
                if exists:
                    self.stdout.write(self.style.ERROR(f'  ❌ Still exists: {table}'))
                else:
                    self.stdout.write(f'  ✅ Confirmed removed: {table}')

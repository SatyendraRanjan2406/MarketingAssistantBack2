from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from google_ads_new.google_ads_api_service import GoogleAdsAPIService
from google_ads_new.models import GoogleAdsAccount

class Command(BaseCommand):
    help = 'Test Google Ads API connection and functionality'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Username to test with (default: admin)'
        )
        parser.add_argument(
            '--customer-id',
            type=str,
            help='Specific customer ID to test (optional)'
        )
    
    def handle(self, *args, **options):
        username = options['username']
        customer_id = options['customer_id']
        
        try:
            # Get user
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ User {username} not found')
                )
                return 1
            
            self.stdout.write(f'👤 Testing with user: {username}')
            
            # Get accounts
            if customer_id:
                accounts = GoogleAdsAccount.objects.filter(
                    user=user,
                    customer_id=customer_id,
                    is_active=True
                )
            else:
                accounts = GoogleAdsAccount.objects.filter(user=user, is_active=True)
            
            if not accounts.exists():
                self.stdout.write(
                    self.style.WARNING(f'⚠️  No active Google Ads accounts found for user {username}')
                )
                return 1
            
            # Initialize API service
            self.stdout.write('🔧 Initializing Google Ads API service...')
            api_service = GoogleAdsAPIService()
            
            if not api_service.initialize_client():
                self.stdout.write(
                    self.style.ERROR('❌ Failed to initialize Google Ads client')
                )
                return 1
            
            self.stdout.write('✅ Google Ads client initialized successfully')
            
            # Test each account
            for account in accounts:
                self.stdout.write(f'\n📊 Testing account: {account.account_name} ({account.customer_id})')
                
                # Test connection
                self.stdout.write('  🔌 Testing API connection...')
                connection_result = api_service.test_connection(account.customer_id)
                
                if connection_result['success']:
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✅ Connection successful: {connection_result["message"]}')
                    )
                    
                    # Test campaigns retrieval
                    self.stdout.write('  📈 Testing campaigns retrieval...')
                    campaigns = api_service.get_campaigns(account.customer_id)
                    
                    if campaigns:
                        self.stdout.write(
                            self.style.SUCCESS(f'  ✅ Retrieved {len(campaigns)} campaigns')
                        )
                        
                        # Show first few campaigns
                        for i, campaign in enumerate(campaigns[:3]):
                            self.stdout.write(f'    📋 {i+1}. {campaign["campaign_name"]} ({campaign["campaign_status"]})')
                        
                        if len(campaigns) > 3:
                            self.stdout.write(f'    ... and {len(campaigns) - 3} more')
                    else:
                        self.stdout.write(
                            self.style.WARNING('  ⚠️  No campaigns found')
                        )
                    
                    # Test ad groups retrieval
                    self.stdout.write('  🎯 Testing ad groups retrieval...')
                    ad_groups = api_service.get_ad_groups(account.customer_id)
                    
                    if ad_groups:
                        self.stdout.write(
                            self.style.SUCCESS(f'  ✅ Retrieved {len(ad_groups)} ad groups')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING('  ⚠️  No ad groups found')
                        )
                    
                    # Test keywords retrieval
                    self.stdout.write('  🔑 Testing keywords retrieval...')
                    keywords = api_service.get_keywords(account.customer_id)
                    
                    if keywords:
                        self.stdout.write(
                            self.style.SUCCESS(f'  ✅ Retrieved {len(keywords)} keywords')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING('  ⚠️  No keywords found')
                        )
                    
                    # Test performance data retrieval (last 7 days)
                    self.stdout.write('  📊 Testing performance data retrieval...')
                    from datetime import datetime, timedelta
                    end_date = datetime.now().date()
                    start_date = end_date - timedelta(days=7)
                    
                    performance_data = api_service.get_performance_data(
                        account.customer_id,
                        start_date.strftime('%Y-%m-%d'),
                        end_date.strftime('%Y-%m-%d')
                    )
                    
                    if performance_data:
                        self.stdout.write(
                            self.style.SUCCESS(f'  ✅ Retrieved {len(performance_data)} performance records')
                        )
                        
                        # Show sample performance data
                        if performance_data:
                            sample = performance_data[0]
                            self.stdout.write(f'    📊 Sample: {sample["impressions"]} impressions, {sample["clicks"]} clicks, ${sample["cost_micros"]/1000000:.2f} cost')
                    else:
                        self.stdout.write(
                            self.style.WARNING('  ⚠️  No performance data found')
                        )
                    
                else:
                    self.stdout.write(
                        self.style.ERROR(f'  ❌ Connection failed: {connection_result["error"]}')
                    )
                    
                    # Provide troubleshooting tips
                    self.stdout.write('\n🔧 Troubleshooting tips:')
                    self.stdout.write('  1. Check your google-ads.yaml configuration file')
                    self.stdout.write('  2. Verify your developer token is valid')
                    self.stdout.write('  3. Ensure your service account has proper permissions')
                    self.stdout.write('  4. Check if your customer ID is correct')
                    self.stdout.write('  5. Verify your JSON key file path is accessible')
            
            self.stdout.write('\n🎉 Google Ads API testing completed!')
            
            if not customer_id:
                self.stdout.write('\n💡 To test a specific account, use:')
                self.stdout.write(f'   python manage.py test_google_ads_api --username {username} --customer-id YOUR_CUSTOMER_ID')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during API testing: {e}')
            )
            return 1
        
        return 0

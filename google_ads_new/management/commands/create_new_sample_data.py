from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import random

from google_ads_new.models import (
    GoogleAdsAccount, GoogleAdsCampaign, GoogleAdsAdGroup,
    GoogleAdsKeyword, GoogleAdsPerformance
)

class Command(BaseCommand):
    help = 'Create sample Google Ads data for the new app'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Username to create data for (default: admin)'
        )
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Clean existing sample data before creating new data'
        )
    
    def handle(self, *args, **options):
        username = options['username']
        
        try:
            # Get or create user
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'is_staff': True,
                    'is_superuser': True
                }
            )
            
            if created:
                user.set_password('admin123')
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created user: {username}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  User already exists: {username}')
                )
            
            # Clean existing data if requested
            if options['clean']:
                self.stdout.write('🧹 Cleaning existing sample data...')
                GoogleAdsPerformance.objects.filter(account__user=user).delete()
                GoogleAdsKeyword.objects.filter(ad_group__campaign__account__user=user).delete()
                GoogleAdsAdGroup.objects.filter(campaign__account__user=user).delete()
                GoogleAdsCampaign.objects.filter(account__user=user).delete()
                GoogleAdsAccount.objects.filter(user=user).delete()
                self.stdout.write('✅ Cleaned existing data')
            
            # Create sample account
            account, created = GoogleAdsAccount.objects.get_or_create(
                customer_id='new_sample_123',
                user=user,
                defaults={
                    'account_name': 'New Sample Google Ads Account',
                    'currency_code': 'USD',
                    'time_zone': 'America/New_York',
                    'is_active': True,
                    'sync_status': 'completed',
                    'last_sync_at': timezone.now()
                }
            )
            
            if created:
                self.stdout.write('✅ Created new sample Google Ads account')
            else:
                self.stdout.write('⚠️  Sample account already exists')
            
            # Create sample campaigns
            campaign_names = [
                'Brand Awareness Campaign (New)',
                'Performance Max Campaign (New)',
                'Search Network Campaign (New)',
                'Display Network Campaign (New)',
                'Shopping Campaign (New)'
            ]
            
            campaigns = []
            for i, name in enumerate(campaign_names):
                campaign, created = GoogleAdsCampaign.objects.get_or_create(
                    campaign_id=f'new_campaign_{i+1}',
                    account=account,
                    defaults={
                        'campaign_name': name,
                        'campaign_status': 'ENABLED',
                        'campaign_type': 'SEARCH',
                        'budget_amount': Decimal('30.00'),
                        'budget_type': 'DAILY',
                        'start_date': timezone.now().date() - timedelta(days=30),
                        'end_date': None
                    }
                )
                campaigns.append(campaign)
                if created:
                    self.stdout.write(f'✅ Created campaign: {name}')
            
            # Create sample ad groups
            ad_group_names = [
                'Brand Terms (New)',
                'Product Features (New)',
                'Competitor Terms (New)',
                'Generic Terms (New)',
                'Long-tail Keywords (New)'
            ]
            
            ad_groups = []
            for i, name in enumerate(ad_group_names):
                campaign = campaigns[i % len(campaigns)]
                ad_group, created = GoogleAdsAdGroup.objects.get_or_create(
                    ad_group_id=f'new_adgroup_{i+1}',
                    campaign=campaign,
                    defaults={
                        'ad_group_name': name,
                        'status': 'ENABLED',
                        'type': 'STANDARD'
                    }
                )
                ad_groups.append(ad_group)
                if created:
                    self.stdout.write(f'✅ Created ad group: {name}')
            
            # Create sample keywords
            keyword_texts = [
                'new google ads management',
                'new ppc optimization',
                'new advertising agency',
                'new digital marketing',
                'new online advertising',
                'new search ads',
                'new display ads',
                'new remarketing',
                'new conversion tracking',
                'new roi optimization'
            ]
            
            keywords = []
            for i, text in enumerate(keyword_texts):
                ad_group = ad_groups[i % len(ad_groups)]
                keyword, created = GoogleAdsKeyword.objects.get_or_create(
                    keyword_id=f'new_keyword_{i+1}',
                    ad_group=ad_group,
                    defaults={
                        'keyword_text': text,
                        'match_type': 'BROAD',
                        'status': 'ENABLED',
                        'quality_score': random.randint(1, 10)
                    }
                )
                keywords.append(keyword)
                if created:
                    self.stdout.write(f'✅ Created keyword: {text}')
            
            # Create sample performance data for the last week
            self.stdout.write('📊 Creating sample performance data...')
            
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=7)
            
            performance_records_created = 0
            
            for i in range(7):  # Last 7 days
                current_date = start_date + timedelta(days=i)
                
                for campaign in campaigns:
                    for ad_group in ad_groups[:3]:  # Limit to first 3 ad groups
                        for keyword in keywords[:5]:  # Limit to first 5 keywords
                            
                            # Generate simple performance data
                            impressions = random.randint(100, 2000)
                            clicks = random.randint(5, 50)
                            cost_micros = random.randint(100000, 2000000)  # $0.10 to $2.00
                            conversions = random.randint(0, 3)
                            conversion_value = random.randint(0, 50)
                            
                            performance, created = GoogleAdsPerformance.objects.get_or_create(
                                account=account,
                                date=current_date,
                                campaign=campaign,
                                ad_group=ad_group,
                                keyword=keyword,
                                defaults={
                                    'impressions': impressions,
                                    'clicks': clicks,
                                    'cost_micros': cost_micros,
                                    'conversions': conversions,
                                    'conversion_value': conversion_value
                                }
                            )
                            
                            if created:
                                performance_records_created += 1
                
                # Show progress
                if (i + 1) % 2 == 0:
                    self.stdout.write(f'   📅 Created data for {current_date}')
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Successfully created {performance_records_created} performance records')
            )
            
            # Update account sync status
            account.last_sync_at = timezone.now()
            account.sync_status = 'completed'
            account.save()
            
            self.stdout.write('\n🎉 New sample data creation completed!')
            self.stdout.write(f'📊 Account: {account.account_name}')
            self.stdout.write(f'📈 Campaigns: {len(campaigns)}')
            self.stdout.write(f'🎯 Ad Groups: {len(ad_groups)}')
            self.stdout.write(f'🔑 Keywords: {len(keywords)}')
            self.stdout.write(f'📊 Performance Records: {performance_records_created}')
            self.stdout.write(f'📅 Date Range: {start_date} to {end_date}')
            
            self.stdout.write('\n💡 You can now:')
            self.stdout.write('   1. Access admin at /admin/')
            self.stdout.write('   2. View the new Google Ads data')
            self.stdout.write('   3. Test the sync functionality')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating sample data: {e}')
            )
            return 1
        
        return 0

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class GoogleAdsAccount(models.Model):
    """Model to store Google Ads account information"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='google_ads_accounts')
    customer_id = models.CharField(max_length=20, unique=True)
    account_name = models.CharField(max_length=255)
    currency_code = models.CharField(max_length=3, default='USD')
    time_zone = models.CharField(max_length=50, default='America/New_York')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Google Ads Account'
        verbose_name_plural = 'Google Ads Accounts'
    
    def __str__(self):
        return f"{self.account_name} ({self.customer_id})"


class GoogleAdsCampaign(models.Model):
    """Model to store Google Ads campaign information"""
    CAMPAIGN_STATUS_CHOICES = [
        ('ENABLED', 'Enabled'),
        ('PAUSED', 'Paused'),
        ('REMOVED', 'Removed'),
    ]
    
    CAMPAIGN_TYPE_CHOICES = [
        ('SEARCH', 'Search'),
        ('DISPLAY', 'Display'),
        ('VIDEO', 'Video'),
        ('SHOPPING', 'Shopping'),
        ('PERFORMANCE_MAX', 'Performance Max'),
    ]
    
    account = models.ForeignKey(GoogleAdsAccount, on_delete=models.CASCADE, related_name='campaigns')
    campaign_id = models.CharField(max_length=20)
    campaign_name = models.CharField(max_length=255)
    campaign_status = models.CharField(max_length=20, choices=CAMPAIGN_STATUS_CHOICES, default='ENABLED')
    campaign_type = models.CharField(max_length=20, choices=CAMPAIGN_TYPE_CHOICES, default='SEARCH')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    budget_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    budget_type = models.CharField(max_length=20, default='DAILY')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('account', 'campaign_id')
        verbose_name = 'Google Ads Campaign'
        verbose_name_plural = 'Google Ads Campaigns'
    
    def __str__(self):
        return f"{self.campaign_name} ({self.campaign_id})"


class GoogleAdsAdGroup(models.Model):
    """Model to store Google Ads ad group information"""
    campaign = models.ForeignKey(GoogleAdsCampaign, on_delete=models.CASCADE, related_name='ad_groups')
    ad_group_id = models.CharField(max_length=20)
    ad_group_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, default='ENABLED')
    type = models.CharField(max_length=20, default='STANDARD')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('campaign', 'ad_group_id')
        verbose_name = 'Google Ads Ad Group'
        verbose_name_plural = 'Google Ads Ad Groups'
    
    def __str__(self):
        return f"{self.ad_group_name} ({self.ad_group_id})"


class GoogleAdsKeyword(models.Model):
    """Model to store Google Ads keyword information"""
    KEYWORD_MATCH_TYPE_CHOICES = [
        ('EXACT', 'Exact'),
        ('PHRASE', 'Phrase'),
        ('BROAD', 'Broad'),
        ('BROAD_MATCH_MODIFIER', 'Broad Match Modifier'),
    ]
    
    ad_group = models.ForeignKey(GoogleAdsAdGroup, on_delete=models.CASCADE, related_name='keywords')
    keyword_id = models.CharField(max_length=20)
    keyword_text = models.CharField(max_length=255)
    match_type = models.CharField(max_length=25, choices=KEYWORD_MATCH_TYPE_CHOICES, default='BROAD')
    status = models.CharField(max_length=20, default='ENABLED')
    quality_score = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('ad_group', 'keyword_id')
        verbose_name = 'Google Ads Keyword'
        verbose_name_plural = 'Google Ads Keywords'
    
    def __str__(self):
        return f"{self.keyword_text} ({self.match_type})"


class GoogleAdsPerformance(models.Model):
    """Model to store Google Ads performance metrics"""
    account = models.ForeignKey(GoogleAdsAccount, on_delete=models.CASCADE, related_name='performance_data')
    campaign = models.ForeignKey(GoogleAdsCampaign, on_delete=models.CASCADE, related_name='performance_data', null=True, blank=True)
    ad_group = models.ForeignKey(GoogleAdsAdGroup, on_delete=models.CASCADE, related_name='performance_data', null=True, blank=True)
    keyword = models.ForeignKey(GoogleAdsKeyword, on_delete=models.CASCADE, related_name='performance_data', null=True, blank=True)
    date = models.DateField()
    
    # Performance metrics
    impressions = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    cost_micros = models.BigIntegerField(default=0)  # Cost in micros (divide by 1,000,000)
    conversions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    conversion_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Calculated fields
    ctr = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)  # Click-through rate
    cpc = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Cost per click
    cpm = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Cost per thousand impressions
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    roas = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Return on ad spend
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('account', 'date', 'campaign', 'ad_group', 'keyword')
        verbose_name = 'Google Ads Performance'
        verbose_name_plural = 'Google Ads Performance Data'
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['account', 'date']),
            models.Index(fields=['campaign', 'date']),
        ]
    
    def __str__(self):
        return f"Performance for {self.account.account_name} on {self.date}"
    
    def save(self, *args, **kwargs):
        # Calculate derived metrics
        if self.impressions > 0:
            self.ctr = self.clicks / self.impressions
        
        if self.clicks > 0:
            self.cpc = (self.cost_micros / 1000000) / self.clicks
        
        if self.impressions > 0:
            self.cpm = ((self.cost_micros / 1000000) / self.impressions) * 1000
        
        if self.clicks > 0:
            self.conversion_rate = self.conversions / self.clicks
        
        if self.cost_micros > 0:
            self.roas = self.conversion_value / (self.cost_micros / 1000000)
        
        super().save(*args, **kwargs)


class GoogleAdsReport(models.Model):
    """Model to store Google Ads report configurations and schedules"""
    REPORT_TYPE_CHOICES = [
        ('ACCOUNT_PERFORMANCE', 'Account Performance'),
        ('CAMPAIGN_PERFORMANCE', 'Campaign Performance'),
        ('AD_GROUP_PERFORMANCE', 'Ad Group Performance'),
        ('KEYWORD_PERFORMANCE', 'Keyword Performance'),
        ('GEO_PERFORMANCE', 'Geographic Performance'),
        ('DEVICE_PERFORMANCE', 'Device Performance'),
    ]
    
    REPORT_STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('RUNNING', 'Running'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='google_ads_reports')
    name = models.CharField(max_length=255)
    report_type = models.CharField(max_length=25, choices=REPORT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=REPORT_STATUS_CHOICES, default='SCHEDULED')
    schedule = models.CharField(max_length=50, default='DAILY')  # DAILY, WEEKLY, MONTHLY
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    parameters = models.JSONField(default=dict)  # Store report parameters
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Google Ads Report'
        verbose_name_plural = 'Google Ads Reports'
    
    def __str__(self):
        return f"{self.name} ({self.report_type})"


class GoogleAdsAlert(models.Model):
    """Model to store Google Ads alerts and notifications"""
    ALERT_TYPE_CHOICES = [
        ('BUDGET', 'Budget Alert'),
        ('PERFORMANCE', 'Performance Alert'),
        ('QUALITY_SCORE', 'Quality Score Alert'),
        ('POLICY_VIOLATION', 'Policy Violation'),
        ('SYSTEM', 'System Alert'),
    ]
    
    ALERT_SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    account = models.ForeignKey(GoogleAdsAccount, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=ALERT_SEVERITY_CHOICES, default='MEDIUM')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Google Ads Alert'
        verbose_name_plural = 'Google Ads Alerts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.alert_type}"

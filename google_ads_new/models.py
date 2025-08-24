from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import uuid


class GoogleAdsAccount(models.Model):
    """Model to store Google Ads account information"""
    ACCOUNT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('pending', 'Pending'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='google_ads_accounts')
    customer_id = models.CharField(max_length=20, unique=True)
    account_name = models.CharField(max_length=255)
    currency_code = models.CharField(max_length=3, default='USD')
    time_zone = models.CharField(max_length=50, default='America/New_York')
    is_active = models.BooleanField(default=True)
    is_manager = models.BooleanField(default=False, help_text='True if this is a manager account (MCC) that can manage other sub-accounts')
    is_test_account = models.BooleanField(default=False, help_text='True if this is a test/sandbox account')
    sync_status = models.CharField(max_length=20, default='pending')
    last_sync_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Google Ads Account'
        verbose_name_plural = 'Google Ads Accounts'
        ordering = ['-created_at']
    
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
        ordering = ['campaign_name']
    
    def __str__(self):
        return f"{self.campaign_name} ({self.campaign_id})"


class GoogleAdsAdGroup(models.Model):
    """Model to store Google Ads ad group information"""
    AD_GROUP_STATUS_CHOICES = [
        ('ENABLED', 'Enabled'),
        ('PAUSED', 'Paused'),
        ('REMOVED', 'Removed'),
    ]
    
    AD_GROUP_TYPE_CHOICES = [
        ('STANDARD', 'Standard'),
        ('SEARCH_DYNAMIC_ADS', 'Search Dynamic Ads'),
        ('SHOPPING_PRODUCT_ADS', 'Shopping Product Ads'),
    ]
    
    campaign = models.ForeignKey(GoogleAdsCampaign, on_delete=models.CASCADE, related_name='ad_groups')
    ad_group_id = models.CharField(max_length=20)
    ad_group_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=AD_GROUP_STATUS_CHOICES, default='ENABLED')
    type = models.CharField(max_length=25, choices=AD_GROUP_TYPE_CHOICES, default='STANDARD')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('campaign', 'ad_group_id')
        verbose_name = 'Google Ads Ad Group'
        verbose_name_plural = 'Google Ads Ad Groups'
        ordering = ['ad_group_name']
    
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
    
    KEYWORD_STATUS_CHOICES = [
        ('ENABLED', 'Enabled'),
        ('PAUSED', 'Paused'),
        ('REMOVED', 'Removed'),
    ]
    
    ad_group = models.ForeignKey(GoogleAdsAdGroup, on_delete=models.CASCADE, related_name='keywords')
    keyword_id = models.CharField(max_length=20)
    keyword_text = models.CharField(max_length=255)
    match_type = models.CharField(max_length=25, choices=KEYWORD_MATCH_TYPE_CHOICES, default='BROAD')
    status = models.CharField(max_length=20, choices=KEYWORD_STATUS_CHOICES, default='ENABLED')
    quality_score = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('ad_group', 'keyword_id')
        verbose_name = 'Google Ads Keyword'
        verbose_name_plural = 'Google Ads Keywords'
        ordering = ['keyword_text']
    
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
    
    # Calculated fields (can be updated via signals or methods)
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
            models.Index(fields=['ad_group', 'date']),
            models.Index(fields=['keyword', 'date']),
        ]
        ordering = ['-date']
    
    def __str__(self):
        return f"Performance for {self.account.account_name} on {self.date}"
    
    def save(self, *args, **kwargs):
        # Calculate derived metrics before saving
        if self.impressions > 0:
            self.ctr = Decimal(self.clicks) / Decimal(self.impressions)
        
        if self.clicks > 0:
            self.cpc = Decimal(self.cost_micros) / Decimal(1000000) / Decimal(self.clicks)
        
        if self.impressions > 0:
            self.cpm = Decimal(self.cost_micros) / Decimal(1000000) / Decimal(self.impressions) * Decimal(1000)
        
        if self.clicks > 0:
            self.conversion_rate = Decimal(self.conversions) / Decimal(self.clicks)
        
        if self.cost_micros > 0:
            self.roas = Decimal(self.conversion_value) / (Decimal(self.cost_micros) / Decimal(1000000))
        
        super().save(*args, **kwargs)


class DataSyncLog(models.Model):
    """Model to track data synchronization operations"""
    SYNC_TYPE_CHOICES = [
        ('daily_sync', 'Daily Sync'),
        ('historical_sync', 'Historical Sync'),
        ('force_sync', 'Force Sync'),
        ('account_sync', 'Account Sync'),
    ]
    
    SYNC_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('partial_failure', 'Partial Failure'),
    ]
    
    sync_type = models.CharField(max_length=20, choices=SYNC_TYPE_CHOICES)
    account = models.ForeignKey(GoogleAdsAccount, on_delete=models.CASCADE, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    results = models.JSONField(default=dict)  # Store sync results and statistics
    status = models.CharField(max_length=20, choices=SYNC_STATUS_CHOICES, default='pending')
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Data Sync Log'
        verbose_name_plural = 'Data Sync Logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sync_type} - {self.status} at {self.created_at}"
    
    def get_summary(self):
        """Get a human-readable summary of the sync results"""
        if not self.results:
            return "No results available"
        
        summary_parts = []
        
        if 'total_accounts' in self.results:
            summary_parts.append(f"{self.results['total_accounts']} accounts")
        
        if 'accounts_processed' in self.results:
            summary_parts.append(f"{self.results['accounts_processed']} processed")
        
        if 'weeks_processed' in self.results:
            summary_parts.append(f"{self.results['weeks_processed']} weeks")
        
        if 'date_range' in self.results:
            summary_parts.append(f"Range: {self.results['date_range']}")
        
        return ", ".join(summary_parts) if summary_parts else "Sync completed"


# Chat and AI Assistant Models
class ChatSession(models.Model):
    """Chat conversation sessions for AI assistant"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_sessions'
        verbose_name = 'Chat Session'
        verbose_name_plural = 'Chat Sessions'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Chat Session {self.id} - {self.user.username}"


class ChatMessage(models.Model):
    """Individual chat messages with memory"""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
        ('tool', 'Tool'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_messages'
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session', 'created_at']),
            models.Index(fields=['role', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.role} message in {self.session.id}"


class KBDocument(models.Model):
    """Company knowledge base documents for RAG"""
    company_id = models.BigIntegerField(default=1)
    title = models.CharField(max_length=255)
    content = models.TextField()
    url = models.URLField(blank=True, null=True)
    document_type = models.CharField(max_length=50, default='general')
    embedding = models.BinaryField(blank=True, null=True)  # Store as binary for vector similarity
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'kb_documents'
        verbose_name = 'Knowledge Base Document'
        verbose_name_plural = 'Knowledge Base Documents'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['company_id']),
            models.Index(fields=['document_type']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.document_type})"


class UserIntent(models.Model):
    """User intent patterns for fine-tuning and analytics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_intents')
    user_query = models.TextField()
    detected_intent = models.CharField(max_length=100)
    intent_confidence = models.FloatField(null=True, blank=True)
    tool_calls = models.JSONField(default=dict)
    response_blocks = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_intents'
        verbose_name = 'User Intent'
        verbose_name_plural = 'User Intents'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['detected_intent']),
        ]
    
    def __str__(self):
        return f"{self.detected_intent} - {self.user.username}"


class AIToolExecution(models.Model):
    """Track AI tool executions for auditing and improvement"""
    TOOL_TYPE_CHOICES = [
        ('google_ads', 'Google Ads API'),
        ('database', 'Database Query'),
        ('knowledge_base', 'Knowledge Base Search'),
        ('analytics', 'Analytics Generation'),
        ('campaign_management', 'Campaign Management'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_tool_executions')
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='tool_executions')
    tool_type = models.CharField(max_length=30, choices=TOOL_TYPE_CHOICES)
    tool_name = models.CharField(max_length=100)
    input_parameters = models.JSONField(default=dict)
    output_result = models.JSONField(default=dict)
    execution_time_ms = models.IntegerField(null=True, blank=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_tool_executions'
        verbose_name = 'AI Tool Execution'
        verbose_name_plural = 'AI Tool Executions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['tool_type', 'success']),
            models.Index(fields=['session', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.tool_name} - {self.user.username} ({'Success' if self.success else 'Failed'})"

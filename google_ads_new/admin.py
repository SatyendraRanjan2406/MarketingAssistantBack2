from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Avg, Count
from .models import (
    GoogleAdsAccount, GoogleAdsCampaign, GoogleAdsAdGroup,
    GoogleAdsKeyword, GoogleAdsPerformance, DataSyncLog,
    ChatSession, ChatMessage, KBDocument, UserIntent, AIToolExecution
)


class GoogleAdsPerformanceInline(admin.TabularInline):
    """Inline performance data for accounts"""
    model = GoogleAdsPerformance
    extra = 0
    readonly_fields = ['ctr', 'cpc', 'cpm', 'conversion_rate', 'roas']
    fields = ['date', 'campaign', 'ad_group', 'keyword', 'impressions', 'clicks', 'cost_micros', 'conversions', 'conversion_value']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('campaign', 'ad_group', 'keyword')


class GoogleAdsCampaignInline(admin.TabularInline):
    """Inline campaigns for accounts"""
    model = GoogleAdsCampaign
    extra = 0
    fields = ['campaign_id', 'campaign_name', 'campaign_status', 'campaign_type', 'budget_amount', 'budget_type']


@admin.register(GoogleAdsAccount)
class GoogleAdsAccountAdmin(admin.ModelAdmin):
    """Admin interface for Google Ads accounts"""
    list_display = [
        'account_name', 'customer_id', 'user', 'currency_code', 
        'sync_status', 'last_sync_at', 'created_at', 'performance_summary'
    ]
    list_filter = ['sync_status', 'is_active', 'currency_code', 'created_at']
    search_fields = ['account_name', 'customer_id', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'last_sync_at']
    inlines = [GoogleAdsCampaignInline, GoogleAdsPerformanceInline]
    
    fieldsets = (
        ('Account Information', {
            'fields': ('user', 'customer_id', 'account_name', 'is_active')
        }),
        ('Settings', {
            'fields': ('currency_code', 'time_zone')
        }),
        ('Sync Status', {
            'fields': ('sync_status', 'last_sync_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def performance_summary(self, obj):
        """Display performance summary for the account"""
        performance = obj.performance_data.aggregate(
            total_impressions=Sum('impressions'),
            total_clicks=Sum('clicks'),
            total_cost=Sum('cost_micros'),
            total_conversions=Sum('conversions')
        )
        
        if performance['total_impressions']:
            ctr = (performance['total_clicks'] / performance['total_impressions']) * 100
            cost = performance['total_cost'] / 1000000  # Convert from micros
            return format_html(
                '<div style="font-size: 11px;">'
                'Impressions: {:,}<br>'
                'Clicks: {:,}<br>'
                'CTR: {:.2f}%<br>'
                'Cost: ${:.2f}'
                '</div>',
                performance['total_impressions'] or 0,
                performance['total_clicks'] or 0,
                ctr,
                cost
            )
        return "No data"
    
    performance_summary.short_description = 'Performance Summary'


class GoogleAdsAdGroupInline(admin.TabularInline):
    """Inline ad groups for campaigns"""
    model = GoogleAdsAdGroup
    extra = 0
    fields = ['ad_group_id', 'ad_group_name', 'status', 'type']


@admin.register(GoogleAdsCampaign)
class GoogleAdsCampaignAdmin(admin.ModelAdmin):
    """Admin interface for Google Ads campaigns"""
    list_display = [
        'campaign_name', 'account', 'campaign_status', 'campaign_type',
        'budget_amount', 'budget_type', 'start_date', 'end_date'
    ]
    list_filter = ['campaign_status', 'campaign_type', 'budget_type', 'start_date']
    search_fields = ['campaign_name', 'campaign_id', 'account__account_name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [GoogleAdsAdGroupInline]
    
    fieldsets = (
        ('Campaign Information', {
            'fields': ('account', 'campaign_id', 'campaign_name')
        }),
        ('Status & Type', {
            'fields': ('campaign_status', 'campaign_type')
        }),
        ('Budget & Dates', {
            'fields': ('budget_amount', 'budget_type', 'start_date', 'end_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class GoogleAdsKeywordInline(admin.TabularInline):
    """Inline keywords for ad groups"""
    model = GoogleAdsKeyword
    extra = 0
    fields = ['keyword_id', 'keyword_text', 'match_type', 'status', 'quality_score']


@admin.register(GoogleAdsAdGroup)
class GoogleAdsAdGroupAdmin(admin.ModelAdmin):
    """Admin interface for Google Ads ad groups"""
    list_display = [
        'ad_group_name', 'campaign', 'account', 'status', 'type'
    ]
    list_filter = ['status', 'type', 'created_at']
    search_fields = ['ad_group_name', 'ad_group_id', 'campaign__campaign_name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [GoogleAdsKeywordInline]
    
    def account(self, obj):
        return obj.campaign.account
    
    account.short_description = 'Account'


@admin.register(GoogleAdsKeyword)
class GoogleAdsKeywordAdmin(admin.ModelAdmin):
    """Admin interface for Google Ads keywords"""
    list_display = [
        'keyword_text', 'match_type', 'ad_group', 'campaign', 'account', 'status', 'quality_score'
    ]
    list_filter = ['match_type', 'status', 'quality_score', 'created_at']
    search_fields = ['keyword_text', 'keyword_id', 'ad_group__ad_group_name']
    readonly_fields = ['created_at', 'updated_at']
    
    def campaign(self, obj):
        return obj.ad_group.campaign
    
    def account(self, obj):
        return obj.ad_group.campaign.account
    
    campaign.short_description = 'Campaign'
    account.short_description = 'Account'


@admin.register(GoogleAdsPerformance)
class GoogleAdsPerformanceAdmin(admin.ModelAdmin):
    """Admin interface for Google Ads performance data"""
    list_display = [
        'date', 'account', 'campaign', 'ad_group', 'keyword',
        'impressions', 'clicks', 'cost_display', 'ctr_display', 'cpc_display'
    ]
    list_filter = ['date', 'account', 'campaign', 'created_at']
    search_fields = ['account__account_name', 'campaign__campaign_name', 'ad_group__ad_group_name']
    readonly_fields = ['ctr', 'cpc', 'cpm', 'conversion_rate', 'roas', 'created_at', 'updated_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Performance Data', {
            'fields': ('account', 'campaign', 'ad_group', 'keyword', 'date')
        }),
        ('Metrics', {
            'fields': ('impressions', 'clicks', 'cost_micros', 'conversions', 'conversion_value')
        }),
        ('Calculated Metrics', {
            'fields': ('ctr', 'cpc', 'cpm', 'conversion_rate', 'roas'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def cost_display(self, obj):
        """Display cost in dollars"""
        return f"${obj.cost_micros / 1000000:.2f}"
    
    def ctr_display(self, obj):
        """Display CTR as percentage"""
        if obj.ctr:
            return f"{obj.ctr * 100:.2f}%"
        return "N/A"
    
    def cpc_display(self, obj):
        """Display CPC in dollars"""
        if obj.cpc:
            return f"${obj.cpc:.2f}"
        return "N/A"
    
    cost_display.short_description = 'Cost'
    ctr_display.short_description = 'CTR'
    cpc_display.short_description = 'CPC'


@admin.register(DataSyncLog)
class DataSyncLogAdmin(admin.ModelAdmin):
    """Admin interface for data sync logs"""
    list_display = [
        'sync_type', 'account', 'status', 'start_date', 'end_date',
        'created_at', 'duration_display', 'results_summary'
    ]
    list_filter = ['sync_type', 'status', 'created_at']
    search_fields = ['sync_type', 'account__account_name']
    readonly_fields = ['created_at', 'completed_at', 'duration_seconds']
    
    fieldsets = (
        ('Sync Information', {
            'fields': ('sync_type', 'account', 'status')
        }),
        ('Date Range', {
            'fields': ('start_date', 'end_date')
        }),
        ('Results', {
            'fields': ('results', 'error_message')
        }),
        ('Timing', {
            'fields': ('created_at', 'completed_at', 'duration_seconds'),
            'classes': ('collapse',)
        }),
    )
    
    def duration_display(self, obj):
        """Display duration in human-readable format"""
        if obj.duration_seconds:
            return f"{obj.duration_seconds:.2f}s"
        return "N/A"
    
    def results_summary(self, obj):
        """Display a summary of sync results"""
        return obj.get_summary()
    
    duration_display.short_description = 'Duration'
    results_summary.short_description = 'Results Summary'


# Customize admin site
admin.site.site_header = "Google Ads Marketing Assistant Admin"
admin.site.site_title = "Google Ads Admin"
admin.site.index_title = "Welcome to Google Ads Marketing Assistant"

# Chat and AI Assistant Admin
@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    """Admin interface for chat sessions"""
    list_display = ['id', 'user', 'title', 'created_at', 'updated_at', 'message_count']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email', 'title']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Session Information', {
            'fields': ('id', 'user', 'title')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def message_count(self, obj):
        """Display count of messages in session"""
        return obj.messages.count()
    
    message_count.short_description = 'Messages'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """Admin interface for chat messages"""
    list_display = ['id', 'session', 'role', 'content_preview', 'created_at']
    list_filter = ['role', 'created_at', 'session__user']
    search_fields = ['content', 'session__user__username', 'session__title']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Message Information', {
            'fields': ('id', 'session', 'role', 'content')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        """Display preview of message content"""
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    
    content_preview.short_description = 'Content Preview'


@admin.register(KBDocument)
class KBDocumentAdmin(admin.ModelAdmin):
    """Admin interface for knowledge base documents"""
    list_display = ['id', 'title', 'company_id', 'document_type', 'created_at', 'updated_at']
    list_filter = ['document_type', 'company_id', 'created_at']
    search_fields = ['title', 'content', 'url']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Document Information', {
            'fields': ('id', 'company_id', 'title', 'content', 'url', 'document_type')
        }),
        ('Embedding', {
            'fields': ('embedding',),
            'classes': ('collapse',),
            'description': 'Vector embedding for similarity search'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserIntent)
class UserIntentAdmin(admin.ModelAdmin):
    """Admin interface for user intent patterns"""
    list_display = ['id', 'user', 'detected_intent', 'intent_confidence', 'created_at']
    list_filter = ['detected_intent', 'intent_confidence', 'created_at']
    search_fields = ['user__username', 'user_query', 'detected_intent']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Intent Information', {
            'fields': ('id', 'user', 'user_query', 'detected_intent', 'intent_confidence')
        }),
        ('Tool Calls', {
            'fields': ('tool_calls',),
            'classes': ('collapse',)
        }),
        ('Response Blocks', {
            'fields': ('response_blocks',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(AIToolExecution)
class AIToolExecutionAdmin(admin.ModelAdmin):
    """Admin interface for AI tool executions"""
    list_display = [
        'id', 'user', 'tool_type', 'tool_name', 'success', 
        'execution_time_ms', 'created_at'
    ]
    list_filter = ['tool_type', 'success', 'created_at']
    search_fields = ['user__username', 'tool_name', 'tool_type']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Execution Information', {
            'fields': ('id', 'user', 'session', 'tool_type', 'tool_name')
        }),
        ('Parameters', {
            'fields': ('input_parameters',),
            'classes': ('collapse',)
        }),
        ('Results', {
            'fields': ('output_result', 'success', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Performance', {
            'fields': ('execution_time_ms',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def execution_time_display(self, obj):
        """Display execution time in human-readable format"""
        if obj.execution_time_ms:
            return f"{obj.execution_time_ms}ms"
        return "N/A"
    
    execution_time_display.short_description = 'Execution Time'

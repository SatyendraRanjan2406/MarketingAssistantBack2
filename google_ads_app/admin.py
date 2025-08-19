from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    GoogleAdsAccount, GoogleAdsCampaign, GoogleAdsAdGroup,
    GoogleAdsKeyword, GoogleAdsPerformance, GoogleAdsReport, GoogleAdsAlert
)


@admin.register(GoogleAdsAccount)
class GoogleAdsAccountAdmin(admin.ModelAdmin):
    list_display = [
        'account_name', 'customer_id', 'user', 'currency_code', 
        'time_zone', 'is_active', 'total_campaigns', 'total_spend', 'created_at'
    ]
    list_filter = ['is_active', 'currency_code', 'time_zone', 'created_at']
    search_fields = ['account_name', 'customer_id', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def total_campaigns(self, obj):
        return obj.campaigns.count()
    total_campaigns.short_description = 'Campaigns'
    
    def total_spend(self, obj):
        total_micros = obj.performance_data.aggregate(
            total=models.Sum('cost_micros')
        )['total'] or 0
        return f"${total_micros / 1000000:.2f}"
    total_spend.short_description = 'Total Spend'


@admin.register(GoogleAdsCampaign)
class GoogleAdsCampaignAdmin(admin.ModelAdmin):
    list_display = [
        'campaign_name', 'account', 'campaign_id', 'campaign_status',
        'campaign_type', 'budget_amount', 'total_ad_groups', 'total_spend',
        'start_date', 'end_date'
    ]
    list_filter = [
        'campaign_status', 'campaign_type', 'budget_type', 
        'start_date', 'end_date', 'account__is_active'
    ]
    search_fields = ['campaign_name', 'campaign_id', 'account__account_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def total_ad_groups(self, obj):
        return obj.ad_groups.count()
    total_ad_groups.short_description = 'Ad Groups'
    
    def total_spend(self, obj):
        total_micros = obj.performance_data.aggregate(
            total=models.Sum('cost_micros')
        )['total'] or 0
        return f"${total_micros / 1000000:.2f}"
    total_spend.short_description = 'Total Spend'


@admin.register(GoogleAdsAdGroup)
class GoogleAdsAdGroupAdmin(admin.ModelAdmin):
    list_display = [
        'ad_group_name', 'campaign', 'ad_group_id', 'status', 'type',
        'total_keywords', 'total_spend'
    ]
    list_filter = ['status', 'type', 'campaign__campaign_status', 'campaign__account__is_active']
    search_fields = ['ad_group_name', 'ad_group_id', 'campaign__campaign_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def total_keywords(self, obj):
        return obj.keywords.count()
    total_keywords.short_description = 'Keywords'
    
    def total_spend(self, obj):
        total_micros = obj.performance_data.aggregate(
            total=models.Sum('cost_micros')
        )['total'] or 0
        return f"${total_micros / 1000000:.2f}"
    total_spend.short_description = 'Total Spend'


@admin.register(GoogleAdsKeyword)
class GoogleAdsKeywordAdmin(admin.ModelAdmin):
    list_display = [
        'keyword_text', 'ad_group', 'campaign', 'keyword_id', 'match_type',
        'status', 'quality_score', 'total_spend', 'total_impressions', 'total_clicks'
    ]
    list_filter = [
        'match_type', 'status', 'quality_score', 'ad_group__status',
        'ad_group__campaign__campaign_status'
    ]
    search_fields = ['keyword_text', 'keyword_id', 'ad_group__ad_group_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def campaign(self, obj):
        return obj.ad_group.campaign.campaign_name
    campaign.short_description = 'Campaign'
    
    def total_spend(self, obj):
        total_micros = obj.performance_data.aggregate(
            total=models.Sum('cost_micros')
        )['total'] or 0
        return f"${total_micros / 1000000:.2f}"
    total_spend.short_description = 'Total Spend'
    
    def total_impressions(self, obj):
        return obj.performance_data.aggregate(
            total=models.Sum('impressions')
        )['total'] or 0
    total_impressions.short_description = 'Impressions'
    
    def total_clicks(self, obj):
        return obj.performance_data.aggregate(
            total=models.Sum('clicks')
        )['total'] or 0
    total_clicks.short_description = 'Clicks'


@admin.register(GoogleAdsPerformance)
class GoogleAdsPerformanceAdmin(admin.ModelAdmin):
    list_display = [
        'date', 'account', 'campaign', 'ad_group', 'keyword',
        'impressions', 'clicks', 'cost_display', 'conversions',
        'conversion_value', 'ctr', 'cpc', 'roas'
    ]
    list_filter = [
        'date', 'account__is_active', 'campaign__campaign_status',
        'ad_group__status', 'keyword__status'
    ]
    search_fields = [
        'account__account_name', 'campaign__campaign_name',
        'ad_group__ad_group_name', 'keyword__keyword_text'
    ]
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-date']
    date_hierarchy = 'date'
    
    def cost_display(self, obj):
        return f"${obj.cost_micros / 1000000:.2f}"
    cost_display.short_description = 'Cost'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'account', 'campaign', 'ad_group', 'keyword'
        )


@admin.register(GoogleAdsReport)
class GoogleAdsReportAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'user', 'report_type', 'status', 'schedule',
        'last_run', 'next_run', 'created_at'
    ]
    list_filter = ['report_type', 'status', 'schedule', 'created_at']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(GoogleAdsAlert)
class GoogleAdsAlertAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'account', 'alert_type', 'severity', 'is_read',
        'is_resolved', 'created_at'
    ]
    list_filter = [
        'alert_type', 'severity', 'is_read', 'is_resolved', 'created_at'
    ]
    search_fields = ['title', 'message', 'account__account_name']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    actions = ['mark_as_read', 'mark_as_resolved']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} alerts marked as read.')
    mark_as_read.short_description = 'Mark selected alerts as read'
    
    def mark_as_resolved(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_resolved=True, resolved_at=timezone.now())
        self.message_user(request, f'{updated} alerts marked as resolved.')
    mark_as_resolved.short_description = 'Mark selected alerts as resolved'

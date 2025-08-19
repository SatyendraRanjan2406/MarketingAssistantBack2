from rest_framework import serializers
from .models import (
    GoogleAdsAccount, GoogleAdsCampaign, GoogleAdsAdGroup, 
    GoogleAdsKeyword, GoogleAdsPerformance, GoogleAdsReport, GoogleAdsAlert
)
from django.db import models


class GoogleAdsAccountSerializer(serializers.ModelSerializer):
    """Serializer for Google Ads Account model"""
    user = serializers.ReadOnlyField(source='user.username')
    total_campaigns = serializers.SerializerMethodField()
    total_spend = serializers.SerializerMethodField()
    
    class Meta:
        model = GoogleAdsAccount
        fields = [
            'id', 'user', 'customer_id', 'account_name', 'currency_code', 
            'time_zone', 'is_active', 'created_at', 'updated_at',
            'total_campaigns', 'total_spend'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_campaigns(self, obj):
        return obj.campaigns.count()
    
    def get_total_spend(self, obj):
        total_micros = obj.performance_data.aggregate(
            total=models.Sum('cost_micros')
        )['total'] or 0
        return total_micros / 1000000


class GoogleAdsCampaignSerializer(serializers.ModelSerializer):
    """Serializer for Google Ads Campaign model"""
    account_name = serializers.ReadOnlyField(source='account.account_name')
    total_ad_groups = serializers.SerializerMethodField()
    total_spend = serializers.SerializerMethodField()
    total_impressions = serializers.SerializerMethodField()
    total_clicks = serializers.SerializerMethodField()
    
    class Meta:
        model = GoogleAdsCampaign
        fields = [
            'id', 'account', 'account_name', 'campaign_id', 'campaign_name',
            'campaign_status', 'campaign_type', 'start_date', 'end_date',
            'budget_amount', 'budget_type', 'created_at', 'updated_at',
            'total_ad_groups', 'total_spend', 'total_impressions', 'total_clicks'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_ad_groups(self, obj):
        return obj.ad_groups.count()
    
    def get_total_spend(self, obj):
        total_micros = obj.performance_data.aggregate(
            total=models.Sum('cost_micros')
        )['total'] or 0
        return total_micros / 1000000
    
    def get_total_impressions(self, obj):
        return obj.performance_data.aggregate(
            total=models.Sum('impressions')
        )['total'] or 0
    
    def get_total_clicks(self, obj):
        return obj.performance_data.aggregate(
            total=models.Sum('clicks')
        )['total'] or 0


class GoogleAdsAdGroupSerializer(serializers.ModelSerializer):
    """Serializer for Google Ads Ad Group model"""
    campaign_name = serializers.ReadOnlyField(source='campaign.campaign_name')
    total_keywords = serializers.SerializerMethodField()
    total_spend = serializers.SerializerMethodField()
    
    class Meta:
        model = GoogleAdsAdGroup
        fields = [
            'id', 'campaign', 'campaign_name', 'ad_group_id', 'ad_group_name',
            'status', 'type', 'created_at', 'updated_at',
            'total_keywords', 'total_spend'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_keywords(self, obj):
        return obj.keywords.count()
    
    def get_total_spend(self, obj):
        total_micros = obj.performance_data.aggregate(
            total=models.Sum('cost_micros')
        )['total'] or 0
        return total_micros / 1000000


class GoogleAdsKeywordSerializer(serializers.ModelSerializer):
    """Serializer for Google Ads Keyword model"""
    ad_group_name = serializers.ReadOnlyField(source='ad_group.ad_group_name')
    campaign_name = serializers.ReadOnlyField(source='ad_group.campaign.campaign_name')
    total_spend = serializers.SerializerMethodField()
    total_impressions = serializers.SerializerMethodField()
    total_clicks = serializers.SerializerMethodField()
    
    class Meta:
        model = GoogleAdsKeyword
        fields = [
            'id', 'ad_group', 'ad_group_name', 'campaign_name', 'keyword_id',
            'keyword_text', 'match_type', 'status', 'quality_score',
            'created_at', 'updated_at', 'total_spend', 'total_impressions', 'total_clicks'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_spend(self, obj):
        total_micros = obj.performance_data.aggregate(
            total=models.Sum('cost_micros')
        )['total'] or 0
        return total_micros / 1000000
    
    def get_total_impressions(self, obj):
        return obj.performance_data.aggregate(
            total=models.Sum('impressions')
        )['total'] or 0
    
    def get_total_clicks(self, obj):
        return obj.performance_data.aggregate(
            total=models.Sum('clicks')
        )['total'] or 0


class GoogleAdsPerformanceSerializer(serializers.ModelSerializer):
    """Serializer for Google Ads Performance model"""
    account_name = serializers.ReadOnlyField(source='account.account_name')
    campaign_name = serializers.ReadOnlyField(source='campaign.campaign_name')
    ad_group_name = serializers.ReadOnlyField(source='ad_group.ad_group_name')
    keyword_text = serializers.ReadOnlyField(source='keyword.keyword_text')
    cost = serializers.SerializerMethodField()
    
    class Meta:
        model = GoogleAdsPerformance
        fields = [
            'id', 'account', 'account_name', 'campaign', 'campaign_name',
            'ad_group', 'ad_group_name', 'keyword', 'keyword_text', 'date',
            'impressions', 'clicks', 'cost', 'conversions', 'conversion_value',
            'ctr', 'cpc', 'cpm', 'conversion_rate', 'roas',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_cost(self, obj):
        return obj.cost_micros / 1000000


class GoogleAdsReportSerializer(serializers.ModelSerializer):
    """Serializer for Google Ads Report model"""
    user = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = GoogleAdsReport
        fields = [
            'id', 'user', 'name', 'report_type', 'status', 'schedule',
            'last_run', 'next_run', 'parameters', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class GoogleAdsAlertSerializer(serializers.ModelSerializer):
    """Serializer for Google Ads Alert model"""
    account_name = serializers.ReadOnlyField(source='account.account_name')
    
    class Meta:
        model = GoogleAdsAlert
        fields = [
            'id', 'account', 'account_name', 'alert_type', 'severity',
            'title', 'message', 'is_read', 'is_resolved', 'created_at', 'resolved_at'
        ]
        read_only_fields = ['id', 'created_at']


class DashboardMetricsSerializer(serializers.Serializer):
    """Serializer for dashboard metrics"""
    total_accounts = serializers.IntegerField()
    total_campaigns = serializers.IntegerField()
    total_spend = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_impressions = serializers.IntegerField()
    total_clicks = serializers.IntegerField()
    total_conversions = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_conversion_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    overall_ctr = serializers.DecimalField(max_digits=5, decimal_places=4)
    overall_cpc = serializers.DecimalField(max_digits=10, decimal_places=2)
    overall_roas = serializers.DecimalField(max_digits=10, decimal_places=2)
    performance_trend = serializers.ListField(child=serializers.DictField())
    top_campaigns = serializers.ListField(child=serializers.DictField())
    top_keywords = serializers.ListField(child=serializers.DictField())


class AccountSyncSerializer(serializers.Serializer):
    """Serializer for account synchronization"""
    customer_id = serializers.CharField(max_length=20)
    force_sync = serializers.BooleanField(default=False)


class CampaignCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating campaigns"""
    class Meta:
        model = GoogleAdsCampaign
        fields = [
            'account', 'campaign_name', 'campaign_type', 'start_date',
            'end_date', 'budget_amount', 'budget_type'
        ]


class KeywordCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating keywords"""
    class Meta:
        model = GoogleAdsKeyword
        fields = [
            'ad_group', 'keyword_text', 'match_type'
        ]


class PerformanceFilterSerializer(serializers.Serializer):
    """Serializer for performance data filtering"""
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    account = serializers.IntegerField(required=False)
    campaign = serializers.IntegerField(required=False)
    ad_group = serializers.IntegerField(required=False)
    keyword = serializers.IntegerField(required=False)
    metrics = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=['impressions', 'clicks', 'cost', 'conversions']
    )

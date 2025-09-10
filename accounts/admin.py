from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, UserGoogleAuth


class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class UserAdmin(BaseUserAdmin):
    """Custom User admin with profile inline"""
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_company_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    def get_company_name(self, obj):
        """Get company name from profile"""
        if hasattr(obj, 'profile') and obj.profile:
            return obj.profile.company_name
        return '-'
    get_company_name.short_description = 'Company Name'
    
    def get_inline_instances(self, request, obj=None):
        """Get inline instances"""
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'company_name', 'phone_number', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email', 'company_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserGoogleAuth)
class UserGoogleAuthAdmin(admin.ModelAdmin):
    list_display = ['user', 'google_email', 'google_name', 'is_active', 'last_used', 'created_at']
    list_filter = ['is_active', 'created_at', 'updated_at', 'last_used']
    search_fields = ['user__username', 'google_email', 'google_name', 'google_user_id']
    readonly_fields = ['created_at', 'updated_at', 'last_used', 'error_count', 'last_error']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'is_active')
        }),
        ('Google OAuth Tokens', {
            'fields': ('access_token', 'refresh_token', 'token_expiry', 'scopes'),
            'classes': ('collapse',)
        }),
        ('Google Account Info', {
            'fields': ('google_user_id', 'google_email', 'google_name')
        }),
        ('Google Ads', {
            'fields': ('google_ads_customer_id', 'google_ads_account_name', 'accessible_customers')
        }),
        ('Status & Metadata', {
            'fields': ('last_used', 'created_at', 'updated_at')
        }),
        ('Error Tracking', {
            'fields': ('error_count', 'last_error'),
            'classes': ('collapse',)
        }),
    )


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

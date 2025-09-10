from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    company_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'


class UserGoogleAuth(models.Model):
    """Model to store Google OAuth tokens and account information"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='google_auth_set')
    
    # Google OAuth tokens
    access_token = models.TextField(help_text="Google OAuth access token")
    refresh_token = models.TextField(help_text="Google OAuth refresh token")
    token_expiry = models.DateTimeField(help_text="When the access token expires")
    
    # Google account information
    google_user_id = models.CharField(max_length=100, help_text="Google user ID")
    google_email = models.EmailField(help_text="Google account email")
    google_name = models.CharField(max_length=255, help_text="Google account display name")
    
    # Google Ads specific
    google_ads_customer_id = models.CharField(max_length=20, blank=True, null=True, help_text="Google Ads customer ID")
    google_ads_account_name = models.CharField(max_length=255, blank=True, null=True, help_text="Google Ads account name")
    accessible_customers = models.JSONField(blank=True, null=True, help_text="List of accessible Google Ads customer IDs")
    
    # Token scopes
    scopes = models.TextField(help_text="Comma-separated list of granted OAuth scopes")
    
    # Status and metadata
    is_active = models.BooleanField(default=True, help_text="Whether this OAuth connection is active")
    last_used = models.DateTimeField(auto_now=True, help_text="Last time this OAuth connection was used")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Error tracking
    last_error = models.TextField(blank=True, null=True, help_text="Last error encountered with this OAuth connection")
    error_count = models.IntegerField(default=0, help_text="Number of consecutive errors")
    
    def __str__(self):
        return f"{self.user.username} - {self.google_email}"
    
    def is_token_expired(self):
        """Check if the access token has expired"""
        from django.utils import timezone
        return timezone.now() >= self.token_expiry
    
    def needs_refresh(self):
        """Check if token needs refresh (within 5 minutes of expiry)"""
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() >= (self.token_expiry - timedelta(minutes=5))
    
    class Meta:
        verbose_name = 'User Google Auth'
        verbose_name_plural = 'User Google Auths'
        ordering = ['-last_used']
        # Allow multiple users to connect to the same Google account
        # But prevent the same user from having multiple connections to the same Google account
        unique_together = ['user', 'google_user_id']


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

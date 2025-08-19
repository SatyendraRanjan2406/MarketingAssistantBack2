from django.apps import AppConfig


class GoogleAdsNewConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'google_ads_new'
    verbose_name = 'Google Ads (New)'
    
    def ready(self):
        """Import signals when the app is ready"""
        try:
            import google_ads_new.signals
        except ImportError:
            pass

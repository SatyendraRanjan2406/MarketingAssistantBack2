from celery.schedules import crontab
from .tasks import daily_sync_task, weekly_sync_task

# Celery Beat Schedule Configuration
CELERY_BEAT_SCHEDULE = {
    # Daily sync at 2:00 AM every day
    'daily-google-ads-sync': {
        'task': 'google_ads_new.daily_sync',
        'schedule': crontab(hour=2, minute=0),
        'args': (),
        'options': {'queue': 'google_ads_sync'}
    },
    
    # Weekly sync every Sunday at 3:00 AM
    'weekly-google-ads-sync': {
        'task': 'google_ads_new.weekly_sync',
        'schedule': crontab(day_of_week=0, hour=3, minute=0),
        'args': (),
        'options': {'queue': 'google_ads_sync'}
    },
}

# Celery Task Routes
CELERY_TASK_ROUTES = {
    'google_ads_new.daily_sync': {'queue': 'google_ads_sync'},
    'google_ads_new.weekly_sync': {'queue': 'google_ads_sync'},
    'google_ads_new.force_sync': {'queue': 'google_ads_sync'},
    'google_ads_new.sync_from_api': {'queue': 'google_ads_sync'},
    'google_ads_new.sync_campaigns': {'queue': 'google_ads_sync'},
    'google_ads_new.sync_ad_groups': {'queue': 'google_ads_sync'},
    'google_ads_new.sync_keywords': {'queue': 'google_ads_sync'},
}

# Celery Task Defaults
CELERY_TASK_DEFAULTS = {
    'google_ads_new.daily_sync': {
        'retry': True,
        'retry_policy': {
            'max_retries': 3,
            'interval_start': 0,
            'interval_step': 0.2,
            'interval_max': 0.2,
        }
    },
    'google_ads_new.weekly_sync': {
        'retry': True,
        'retry_policy': {
            'max_retries': 3,
            'interval_start': 0,
            'interval_step': 0.2,
            'interval_max': 0.2,
        }
    },
    'google_ads_new.force_sync': {
        'retry': True,
        'retry_policy': {
            'max_retries': 3,
            'interval_start': 0,
            'interval_step': 0.2,
            'interval_max': 0.2,
        }
    },
}

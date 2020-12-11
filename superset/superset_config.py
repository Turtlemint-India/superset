import os

from celery.schedules import crontab
from flask_appbuilder.const import AUTH_OAUTH
from werkzeug.contrib.cache import RedisCache

from superset.custom_sso_security_manager import CustomSsoSecurityManager

SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
REDIS_SERVER_IP = os.getenv('REDIS_SERVER_IP', '')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
SUPERSET_CACHE_REDIS_URL = "".join(['redis://:', REDIS_PASSWORD, '@', REDIS_SERVER_IP, ':6379/1'])
SUPERSET_BROKER_URL = "".join(['redis://:', REDIS_PASSWORD, '@', REDIS_SERVER_IP, ':6379/0'])
SUPERSET_CELERY_RESULT_BACKEND = "".join(['redis://:', REDIS_PASSWORD, '@', REDIS_SERVER_IP, ':6379/0'])

# SQLALCHEMY_TRACK_MODIFICATIONS = True  # What does this do?

CACHE_WARMUP_USER = "whopper"
CACHE_DEFAULT_TIMEOUT = 60 * 60 * 6
CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_DEFAULT_TIMEOUT': 60 * 60 * 6,  # 6 hr default (in secs)
    'CACHE_KEY_PREFIX': 'superset_results',
    'CACHE_REDIS_URL': SUPERSET_CACHE_REDIS_URL or 'redis://localhost:6379/0',
}

SUPERSET_WEBSERVER_TIMEOUT = 180
SQLLAB_TIMEOUT = 180
SQLLAB_VALIDATION_TIMEOUT = 180

ENABLE_PROXY_FIX = True

CUSTOM_SECURITY_MANAGER = CustomSsoSecurityManager
AUTH_TYPE = AUTH_OAUTH
AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = "Gamma"

OAUTH_PROVIDERS = [
    {'name': 'google', 'icon': 'fa-google', 'token_key': 'access_token', 'whitelist': ['@turtlemint.com'],
     'remote_app': {
         'client_id': '78989321337-5e44ugm9ev8davgp7591njjv7o81naoc.apps.googleusercontent.com',
         'client_secret': '-ul9faMKxh5ddwmXrchaUewr',
         'api_base_url': 'https://www.googleapis.com/oauth2/v2/',
         'client_kwargs': {
             'scope': 'email profile'
         },
         'request_token_url': None,
         'access_token_url': 'https://accounts.google.com/o/oauth2/token',
         'authorize_url': 'https://accounts.google.com/o/oauth2/auth'}
     }
]


class CeleryConfig:  # pylint: disable=too-few-public-methods
    BROKER_URL = SUPERSET_BROKER_URL or "redis://localhost:6379/0"
    CELERY_IMPORTS = ("superset.sql_lab", "superset.tasks")
    CELERY_RESULT_BACKEND = SUPERSET_CELERY_RESULT_BACKEND or "redis://localhost:6379/0"
    CELERYD_LOG_LEVEL = "DEBUG"
    CELERYD_PREFETCH_MULTIPLIER = 1
    CELERY_ACKS_LATE = False
    CELERY_ANNOTATIONS = {
        "sql_lab.get_sql_results": {"rate_limit": "100/s"},
        "email_reports.send": {
            "rate_limit": "1/s",
            "time_limit": 120,
            "soft_time_limit": 150,
            "ignore_result": True,
        },
    }
    CELERYBEAT_SCHEDULE = {
        'cache-warmup-hourly': {
            'task': 'cache-warmup',
            'schedule': crontab(minute=54, hour=16),  # @everyday 5AM # check for time zone
            'kwargs': {
                    'strategy_name': 'top_n_dashboards',
                    'top_n': 25,
                    'since': '7 days ago',
                },
        },
        "email_reports.schedule_hourly": {
            "task": "email_reports.schedule_hourly",
            "schedule": crontab(minute=1, hour="*"),
        }
    }


CELERY_CONFIG = CeleryConfig
RESULTS_BACKEND = RedisCache(
    host=REDIS_SERVER_IP,
    port=6379,
    key_prefix='superset_results',
    password=REDIS_PASSWORD
)

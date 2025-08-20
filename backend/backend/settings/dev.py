from .base import *

DEBUG = True
CORS_ALLOW_ALL_ORIGINS = True

INSTALLED_APPS.append('debug_toolbar')
MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
INTERNAL_IPS = ("127.0.0.1",)

def show_toolbar(_):
    return True

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": show_toolbar,
    'RESULTS_CACHE_SIZE': 100,
    'SQL_WARNING_THRESHOLD': 2000,
    'IS_RUNNING_TESTS': False
}

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000', 
    'http://localhost:8000',
]
CORS_ALLOW_CREDENTIALS = True

del REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"]

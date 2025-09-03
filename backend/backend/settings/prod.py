# from .base import *


# # DEBUG = False
# # CORS_ALLOW_ALL_ORIGINS = False
# CSRF_COOKIE_SECURE = False
# CSRF_COOKIE_HTTPONLY = True
# SESSION_COOKIE_SECURE = None
# SESSION_COOKIE_HTTPONLY = True
# CORS_ALLOW_CREDENTIALS = True
# CORS_ORIGIN_ALLOW_ALL = True

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'verbose': {
#             'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
#             'style': '{',
#         },
#     },
#     'handlers': {
#         'file': {
#             'level': 'ERROR',
#             'class': 'logging.FileHandler',
#             'filename': './logs.log',
#             'formatter': 'verbose'
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['file'],
#             'level': 'ERROR',
#             'propagate': True,
#         },
#     },
# }


from .base import *

DEBUG = True
CORS_ALLOW_ALL_ORIGINS = True


CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
]
CORS_ALLOW_CREDENTIALS = True
INSTALLED_APPS += [
    "drf_spectacular",
    "drf_spectacular_sidecar",
]

SPECTACULAR_SETTINGS = {
    "TITLE": "Master KG Job Portal API",
    "DESCRIPTION": "Master KG Job Portal API",
    "VERSION": "1.0.0",
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
    "SERVE_AUTHENTICATION": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
}
REST_FRAMEWORK["DEFAULT_SCHEMA_CLASS"] = "drf_spectacular.openapi.AutoSchema"
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
    "0.0.0.0",
]


def show_toolbar(_):
    return True


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": show_toolbar,
    "RESULTS_CACHE_SIZE": 100,
    "SQL_WARNING_THRESHOLD": 2000,
    "IS_RUNNING_TESTS": False,
}

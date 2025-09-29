from .base import *

DEBUG = True
CORS_ALLOW_ALL_ORIGINS = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True


CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
]
# Add drf_spectacular if not already present
if "drf_spectacular" not in INSTALLED_APPS:
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
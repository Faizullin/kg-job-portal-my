from .base import *

DEBUG = True
CORS_ALLOW_ALL_ORIGINS = True


CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000', 
    'http://localhost:8000',
]
CORS_ALLOW_CREDENTIALS = True

del REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"]

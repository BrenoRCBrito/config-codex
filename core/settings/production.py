"""
Production settings for config-codex project.
"""

import os

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

# Security Settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# HTTPS settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CORS Settings for production
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")

# Rate limiting
RATELIMIT_ENABLE = True

# Email settings for production
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

# Cache timeout for production
CACHES["default"]["TIMEOUT"] = "3600"  # 1 hour

# Static files for production
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Session settings
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_SAVE_EVERY_REQUEST = True

# Logging for production
# Use environment variable for log file path, fallback to console-only in containers
LOG_FILE_PATH = os.getenv("DJANGO_LOG_FILE_PATH")
if LOG_FILE_PATH:
    LOGGING["handlers"]["file"]["filename"] = LOG_FILE_PATH
else:
    # Container-friendly: remove file handler, use console only
    LOGGING["handlers"].pop("file", None)
    LOGGING["root"]["handlers"] = ["console"]
    LOGGING["loggers"]["django"]["handlers"] = ["console"]
    LOGGING["loggers"]["apps"]["handlers"] = ["console"]

LOGGING["root"]["level"] = "WARNING"
LOGGING["loggers"]["django"]["level"] = "WARNING"
LOGGING["loggers"]["apps"]["level"] = "INFO"

# Additional security headers
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

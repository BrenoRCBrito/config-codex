"""
Development settings for config-codex project.
"""

from .base import *  # noqa: F403

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# Development-specific apps
INSTALLED_APPS = INSTALLED_APPS + [
    "django_extensions",
]

# CORS Settings for development
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000",
    "http://localhost:8080",  # Alternative frontend port
    "http://127.0.0.1:8080",
]

# Allow all origins in development (less secure but convenient)
CORS_ALLOW_ALL_ORIGINS = True

# Security settings (relaxed for development)
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
X_FRAME_OPTIONS = "SAMEORIGIN"

# Disable HTTPS requirements in development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Email backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Cache timeout reduced for development
CACHES["default"]["TIMEOUT"] = "300"

# Database query logging in development
LOGGING["loggers"]["django"] = {
    "level": "DEBUG",
    "handlers": ["console"],
    "propagate": False,
}

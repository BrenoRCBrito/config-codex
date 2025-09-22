"""
Testing settings for config-codex project.
Optimized for fast, isolated test execution.
"""

import os

from .base import *  # noqa: F403

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Test-specific hosts
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

# Database configuration for testing
# Use test database prefix to avoid conflicts
DB_NAME = os.getenv("DEFAULT_DATABASE_NAME", "config_codex")
DATABASES["default"]["NAME"] = f"test_{DB_NAME}"  # noqa: F405

# Use faster password hashers for testing
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]


# Cache configuration for testing - use dummy cache
CACHES = {  # noqa: F405
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Disable external services in tests
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = ["localhost", "0.0.0.0", "127.0.0.1"]

# Security settings (relaxed for testing)
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
X_FRAME_OPTIONS = "SAMEORIGIN"

# Disable HTTPS requirements in testing
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Logging for testing - console only, reduced verbosity
LOGGING = {  # noqa: F405
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}

# JWT settings for testing - shorter tokens for faster tests
JWT_SETTINGS = {  # noqa: F405
    "ACCESS_TOKEN_LIFETIME": 300,  # 5 minutes
    "REFRESH_TOKEN_LIFETIME": 3600,  # 1 hour
    "ALGORITHM": "HS256",
    "VERIFY_SIGNATURE": True,
    "VERIFY_EXP": True,
}

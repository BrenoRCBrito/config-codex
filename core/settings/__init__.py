"""
Django settings package.

This package contains environment-specific settings modules:
- base.py: Common settings shared across all environments
- development.py: Development-specific settings
- production.py: Production-specific settings

Entry points (manage.py, wsgi.py, asgi.py) now use explicit module imports
based on the DJANGO_ENVIRONMENT variable.
"""

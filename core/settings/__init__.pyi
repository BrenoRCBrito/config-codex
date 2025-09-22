# Type stubs for custom Django settings
# This tells mypy about our custom settings attributes

# Core Django settings that are used
SECRET_KEY: str

# Custom project settings
JWT_SECRET_KEY: str

# Re-export everything from base Django settings
from django.conf import *  # noqa: E402, F403

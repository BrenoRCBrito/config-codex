"""
Identity bounded context module.

This module encapsulates all user authentication and identity management functionality.
It follows Domain-Driven Design principles with clear separation of concerns.

Structure:
- domain/: Core business logic and models
- api/: REST API endpoints and schemas
- apps.py: Django app configuration
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ninja import Router

    from .api.auth import JWTAuth, OptionalJWTAuth


def get_auth_router() -> "Router":
    from .api import auth_router

    return auth_router


def get_jwt_auth() -> "JWTAuth":
    from .api import jwt_auth

    return jwt_auth


def get_optional_jwt_auth() -> "OptionalJWTAuth":
    from .api import optional_jwt_auth

    return optional_jwt_auth


auth_router = property(lambda self: get_auth_router())
jwt_auth = property(lambda self: get_jwt_auth())
optional_jwt_auth = property(lambda self: get_optional_jwt_auth())

__all__ = [
    "get_auth_router",
    "get_jwt_auth",
    "get_optional_jwt_auth",
]

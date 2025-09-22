"""
Django-Ninja authentication backends for JWT token validation.
Provides secure authentication middleware for API endpoints.
"""

from django.http import HttpRequest
from ninja.security import HttpBearer

from ..domain.models import User
from ..domain.services import AuthenticationError, AuthService, TokenError


class JWTAuth(HttpBearer):
    """
    JWT Authentication backend for django-ninja.

    Validates JWT tokens and returns the authenticated user.
    """

    def __init__(self) -> None:
        super().__init__()
        self.auth_service = AuthService()

    def authenticate(self, request: HttpRequest, token: str) -> User | None:
        """
        Authenticate request using JWT token.

        Args:
            request: HTTP request object
            token: JWT token from Authorization header

        Returns:
            User instance if authentication succeeds, None otherwise
        """
        try:
            user = self.auth_service.get_user_from_token(token)

            request.user = user

            return user

        except (TokenError, AuthenticationError):
            # Return None to indicate authentication failure
            # django-ninja will handle the 401 response
            return None


class OptionalJWTAuth(JWTAuth):
    """
    Optional JWT Authentication backend.

    Similar to JWTAuth but allows requests without authentication.
    Useful for endpoints that work for both authenticated and anonymous users.
    """

    def authenticate(self, request: HttpRequest, token: str) -> User | None:
        """
        Authenticate request using JWT token, but allow None token.

        Args:
            request: HTTP request object
            token: JWT token from Authorization header (can be None)

        Returns:
            User instance if authentication succeeds, None for anonymous access
        """
        if not token:
            return None

        return super().authenticate(request, token)


# Global instances to use in API endpoints
jwt_auth = JWTAuth()
optional_jwt_auth = OptionalJWTAuth()


def get_client_ip(request: HttpRequest) -> str:
    """
    Get client IP address from request.

    Handles various proxy headers and fallbacks.

    Args:
        request: HTTP request object

    Returns:
        Client IP address as string
    """
    # Check for IP in various headers (common proxy configurations)
    headers_to_check = [
        "HTTP_X_FORWARDED_FOR",
        "HTTP_X_REAL_IP",
        "HTTP_X_CLIENT_IP",
        "HTTP_CF_CONNECTING_IP",  # Cloudflare
        "REMOTE_ADDR",
    ]

    for header in headers_to_check:
        ip = request.META.get(header)
        if ip:
            # X-Forwarded-For can contain multiple IPs, take the first one
            if "," in ip:
                ip = ip.split(",")[0].strip()
            if ip and ip != "unknown":
                return str(ip)

    # Fallback to REMOTE_ADDR
    return str(request.META.get("REMOTE_ADDR", "0.0.0.0"))

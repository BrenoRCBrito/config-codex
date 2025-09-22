"""
Authentication domain service implementing JWT token management.
Handles token creation, validation, and user authentication logic.
"""

import hashlib
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from ..models import User


class AuthenticationError(Exception):
    """Raised when authentication fails."""

    pass


class TokenError(Exception):
    """Raised when token operations fail."""

    pass


class AuthService:
    """
    Domain service for authentication operations.

    Handles JWT token lifecycle, user authentication, and security validations.
    """

    def __init__(self) -> None:
        if not settings.SECRET_KEY:
            raise ValueError("SECRET_KEY setting is required for JWT operations")

        self.secret_key: str = settings.JWT_SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_lifetime = timedelta(hours=1)
        self.refresh_token_lifetime = timedelta(days=7)

    def authenticate_user(
        self, email: str, password: str, ip_address: str | None = None
    ) -> User:
        """
        Authenticate user with email and password.

        Args:
            email: User's email address
            password: User's password
            ip_address: Optional IP address for logging

        Returns:
            User: Authenticated user instance

        Raises:
            AuthenticationError: If authentication fails
        """
        if not email or not password:
            raise AuthenticationError("Email and password are required")

        email = email.lower().strip()

        # Authenticate user
        user = authenticate(username=email, password=password)
        if not user:
            raise AuthenticationError("Invalid email or password")

        assert isinstance(user, User)

        if not user.is_active:
            raise AuthenticationError("User account is deactivated")

        # Update last login IP if provided
        if ip_address:
            user.update_last_login_ip(ip_address)

        return user

    def create_tokens(self, user: User) -> dict[str, Any]:
        """
        Create access and refresh tokens for user.

        Args:
            user: User instance

        Returns:
            Dict containing access_token and refresh_token
        """
        now = datetime.now(UTC)

        # Create access token payload
        access_payload = {
            "user_id": str(user.id),
            "email": user.email,
            "username": user.username,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "email_verified": user.email_verified,
            "exp": now + self.access_token_lifetime,
            "iat": now,
            "type": "access",
        }

        # Create refresh token payload
        refresh_payload = {
            "user_id": str(user.id),
            "email": user.email,
            "exp": now + self.refresh_token_lifetime,
            "iat": now,
            "type": "refresh",
            # Add token fingerprint for additional security
            "jti": self._generate_token_id(str(user.id), now),
        }

        access_token = jwt.encode(
            access_payload, self.secret_key, algorithm=self.algorithm
        )
        refresh_token = jwt.encode(
            refresh_payload, self.secret_key, algorithm=self.algorithm
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": int(self.access_token_lifetime.total_seconds()),
        }

    def validate_access_token(self, token: str) -> dict[str, Any]:
        """
        Validate and decode access token.

        Args:
            token: JWT access token

        Returns:
            Dict: Decoded token payload

        Raises:
            TokenError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            if payload.get("type") != "access":
                raise TokenError("Invalid token type")

            return dict(payload)

        except jwt.ExpiredSignatureError:
            raise TokenError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise TokenError(f"Invalid token: {str(e)}")

    def validate_refresh_token(self, token: str) -> dict[str, Any]:
        """
        Validate and decode refresh token.

        Args:
            token: JWT refresh token

        Returns:
            Dict: Decoded token payload

        Raises:
            TokenError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            if payload.get("type") != "refresh":
                raise TokenError("Invalid token type")

            return dict(payload)

        except jwt.ExpiredSignatureError:
            raise TokenError("Refresh token has expired")
        except jwt.InvalidTokenError as e:
            raise TokenError(f"Invalid refresh token: {str(e)}")

    def refresh_access_token(self, refresh_token: str) -> dict[str, Any]:
        """
        Create new access token from valid refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            Dict containing new access_token

        Raises:
            TokenError: If refresh token is invalid
            AuthenticationError: If user is not found or inactive
        """
        payload = self.validate_refresh_token(refresh_token)

        try:
            user = User.objects.get(id=payload["user_id"])
        except User.DoesNotExist:
            raise AuthenticationError("User not found")

        if not user.is_active:
            raise AuthenticationError("User account is deactivated")

        # Create new access token
        now = datetime.now(UTC)
        access_payload = {
            "user_id": str(user.id),
            "email": user.email,
            "username": user.username,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "email_verified": user.email_verified,
            "exp": now + self.access_token_lifetime,
            "iat": now,
            "type": "access",
        }

        access_token = jwt.encode(
            access_payload, self.secret_key, algorithm=self.algorithm
        )

        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": int(self.access_token_lifetime.total_seconds()),
        }

    def register_user(
        self,
        email: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
        **extra_fields: Any,  # noqa: ANN401
    ) -> User:
        """
        Register a new user with validation.

        Args:
            email: User's email address
            password: User's password
            first_name: User's first name
            last_name: User's last name
            **extra_fields: Additional user fields

        Returns:
            User: Created user instance

        Raises:
            ValidationError: If validation fails
            AuthenticationError: If user creation fails
        """
        # Validate inputs
        if not email or not password:
            raise ValidationError("Email and password are required")

        email = email.lower().strip()

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            raise ValidationError("User with this email already exists")

        # Validate password
        validate_password(password)

        try:
            user = User.objects.create_user_with_profile(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                **extra_fields,
            )
            return user
        except Exception as e:
            raise AuthenticationError(f"Failed to create user: {str(e)}")

    def get_user_from_token(self, token: str) -> User:
        """
        Get user instance from valid access token.

        Args:
            token: JWT access token

        Returns:
            User: User instance

        Raises:
            TokenError: If token is invalid
            AuthenticationError: If user is not found or inactive
        """
        payload = self.validate_access_token(token)

        try:
            user = User.objects.get(id=payload["user_id"])
        except User.DoesNotExist:
            raise AuthenticationError("User not found")

        if not user.is_active:
            raise AuthenticationError("User account is deactivated")

        return user

    def _generate_token_id(self, user_id: str, timestamp: datetime) -> str:
        """Generate unique token ID for refresh token."""
        data = f"{user_id}:{timestamp.isoformat()}:{self.secret_key}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

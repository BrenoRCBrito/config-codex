"""
Authentication API endpoints using django-ninja.
Provides REST API for user authentication, registration, and profile management.
"""

from typing import Any

from django.core.exceptions import ValidationError
from django.http import HttpRequest
from ninja import Router

from ..domain.models import User
from ..domain.services import AuthenticationError, AuthService, TokenError
from .auth import get_client_ip, jwt_auth
from .schemas import (
    AuthResponse,
    ErrorResponse,
    LoginRequest,
    MessageResponse,
    PasswordChangeRequest,
    ProfileUpdateRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

auth_router = Router(tags=["Authentication"])

auth_service = AuthService()


@auth_router.post(
    "/login", response={200: AuthResponse, 400: ErrorResponse, 401: ErrorResponse}
)
def login(request: HttpRequest, data: LoginRequest) -> tuple[int, dict[str, Any]]:
    """
    Authenticate user and return JWT tokens.

    Returns user information along with access and refresh tokens.
    """
    try:
        client_ip = get_client_ip(request)

        user = auth_service.authenticate_user(
            email=data.email, password=data.password, ip_address=client_ip
        )

        tokens = auth_service.create_tokens(user)

        return 200, {
            "user": UserResponse(**user.to_dict()),
            "tokens": TokenResponse(**tokens),
        }

    except AuthenticationError as e:
        return 401, {"error": "authentication_failed", "message": str(e)}
    except Exception as e:
        return 400, {"error": "invalid_request", "message": str(e)}


@auth_router.post("/register", response={201: AuthResponse, 400: ErrorResponse})
def register(request: HttpRequest, data: RegisterRequest) -> tuple[int, dict[str, Any]]:
    """
    Register a new user account.

    Creates a new user and returns authentication tokens.
    """
    try:
        user = auth_service.register_user(
            email=data.email,
            password=data.password,
            first_name=data.first_name,
            last_name=data.last_name,
        )

        tokens = auth_service.create_tokens(user)

        return 201, {
            "user": UserResponse(**user.to_dict()),
            "tokens": TokenResponse(**tokens),
        }

    except ValidationError as e:
        if hasattr(e, "message_dict"):
            details = e.message_dict
        elif hasattr(e, "messages"):
            details = {"general": list(e.messages)}
        else:
            details = {"general": [str(e)]}

        return 400, {
            "error": "validation_error",
            "message": "Registration validation failed",
            "details": details,
        }
    except AuthenticationError as e:
        return 400, {"error": "registration_failed", "message": str(e)}
    except Exception as e:
        return 400, {"error": "invalid_request", "message": str(e)}


@auth_router.post(
    "/refresh", response={200: TokenResponse, 400: ErrorResponse, 401: ErrorResponse}
)
def refresh_token(
    request: HttpRequest, data: RefreshTokenRequest
) -> tuple[int, TokenResponse] | tuple[int, dict[str, str]]:
    """
    Refresh access token using refresh token.

    Returns a new access token if the refresh token is valid.
    """
    try:
        tokens = auth_service.refresh_access_token(data.refresh_token)
        return 200, TokenResponse(**tokens)

    except TokenError as e:
        return 401, {"error": "invalid_token", "message": str(e)}
    except AuthenticationError as e:
        return 401, {"error": "authentication_failed", "message": str(e)}
    except Exception as e:
        return 400, {"error": "invalid_request", "message": str(e)}


@auth_router.get("/me", response={200: UserResponse, 401: ErrorResponse}, auth=jwt_auth)
def get_current_user(
    request: HttpRequest,
) -> tuple[int, UserResponse] | tuple[int, dict[str, str]]:
    """
    Get current authenticated user information.

    Requires valid JWT token in Authorization header.
    """
    try:
        user = request.user
        if not isinstance(user, User):
            return 401, {"error": "authentication_failed", "message": "Invalid user"}
        return 200, UserResponse(**user.to_dict())

    except Exception as e:
        return 401, {"error": "authentication_failed", "message": str(e)}


@auth_router.put(
    "/me",
    response={200: UserResponse, 400: ErrorResponse, 401: ErrorResponse},
    auth=jwt_auth,
)
def update_profile(
    request: HttpRequest, data: ProfileUpdateRequest
) -> tuple[int, UserResponse] | tuple[int, dict[str, str]]:
    """
    Update current user's profile information.

    Requires valid JWT token in Authorization header.
    """
    try:
        user = request.user
        if not isinstance(user, User):
            return 401, {"error": "authentication_failed", "message": "Invalid user"}

        if data.first_name is not None:
            user.first_name = data.first_name
        if data.last_name is not None:
            user.last_name = data.last_name
        if data.avatar_url is not None:
            user.avatar_url = data.avatar_url

        user.save(update_fields=["first_name", "last_name", "avatar_url", "updated_at"])

        return 200, UserResponse(**user.to_dict())

    except Exception as e:
        return 400, {"error": "update_failed", "message": str(e)}


@auth_router.post(
    "/change-password",
    response={200: MessageResponse, 400: ErrorResponse, 401: ErrorResponse},
    auth=jwt_auth,
)
def change_password(
    request: HttpRequest, data: PasswordChangeRequest
) -> tuple[int, dict[str, Any]]:
    """
    Change current user's password.

    Requires valid JWT token and current password verification.
    """
    try:
        user = request.user
        if not isinstance(user, User):
            return 401, {"error": "authentication_failed", "message": "Invalid user"}

        if not user.check_password(data.current_password):
            return 400, {
                "error": "invalid_password",
                "message": "Current password is incorrect",
            }

        from django.contrib.auth.password_validation import validate_password

        validate_password(data.new_password, user)

        user.set_password(data.new_password)
        user.save(update_fields=["password", "updated_at"])

        return 200, {"message": "Password changed successfully"}

    except ValidationError as e:
        return 400, {
            "error": "validation_error",
            "message": "Password validation failed",
            "details": {"password": list(e.messages)},
        }
    except Exception as e:
        return 400, {"error": "password_change_failed", "message": str(e)}


@auth_router.post(
    "/verify-email",
    response={200: MessageResponse, 400: ErrorResponse, 401: ErrorResponse},
    auth=jwt_auth,
)
def verify_email(request: HttpRequest) -> tuple[int, dict[str, Any]]:
    """
    Mark current user's email as verified.

    In a real application, this would be called after email verification process.
    """
    try:
        user = request.user
        if not isinstance(user, User):
            return 401, {"error": "authentication_failed", "message": "Invalid user"}

        if user.email_verified:
            return 400, {
                "error": "already_verified",
                "message": "Email is already verified",
            }

        user.verify_email()

        return 200, {"message": "Email verified successfully"}

    except Exception as e:
        return 400, {"error": "verification_failed", "message": str(e)}


@auth_router.get("/health", response={200: dict})
def health_check(request: HttpRequest) -> tuple[int, dict[str, Any]]:
    """
    Health check endpoint for authentication service.

    Returns service status and configuration info.
    """
    return 200, {
        "status": "healthy",
        "service": "identity-api",
        "version": "1.0.0",
        "features": {
            "jwt_auth": True,
            "email_verification": True,
            "profile_management": True,
        },
    }

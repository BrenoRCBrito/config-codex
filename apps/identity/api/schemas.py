"""
API schemas for the identity module using Pydantic.
Defines request/response models for authentication endpoints.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field, field_validator


class LoginRequest(BaseModel):
    """Request schema for user login."""

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=1, description="User's password")

    @field_validator("email")
    def email_must_be_lowercase(cls, v: str) -> str:
        return v.lower().strip()


class RegisterRequest(BaseModel):
    """Request schema for user registration."""

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(
        ..., min_length=8, description="User's password (min 8 characters)"
    )
    first_name: str = Field("", max_length=150, description="User's first name")
    last_name: str = Field("", max_length=150, description="User's last name")

    @field_validator("email")
    def email_must_be_lowercase(cls, v: str) -> str:
        return v.lower().strip()

    @field_validator("password")
    def password_must_be_strong(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class RefreshTokenRequest(BaseModel):
    """Request schema for token refresh."""

    refresh_token: str = Field(..., description="Valid refresh token")


class TokenResponse(BaseModel):
    """Response schema for token operations."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str | None = Field(
        None, description="JWT refresh token (only on login)"
    )
    token_type: str = Field("Bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class UserResponse(BaseModel):
    """Response schema for user information."""

    id: str = Field(..., description="User's unique identifier")
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., description="User's username")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    full_name: str = Field(..., description="User's full name")
    avatar_url: str | None = Field(None, description="User's avatar URL")
    email_verified: bool = Field(..., description="Whether email is verified")
    is_active: bool = Field(..., description="Whether user account is active")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class AuthResponse(BaseModel):
    """Response schema for authentication operations."""

    user: UserResponse = Field(..., description="User information")
    tokens: TokenResponse = Field(..., description="Authentication tokens")


class PasswordChangeRequest(BaseModel):
    """Request schema for password change."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ..., min_length=8, description="New password (min 8 characters)"
    )

    @field_validator("new_password")
    def password_must_be_strong(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class ProfileUpdateRequest(BaseModel):
    """Request schema for profile updates."""

    first_name: str | None = Field(
        None, max_length=150, description="User's first name"
    )
    last_name: str | None = Field(None, max_length=150, description="User's last name")
    avatar_url: str | None = Field(None, description="User's avatar URL")


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: dict[str, Any] | None = Field(None, description="Additional error details")


class MessageResponse(BaseModel):
    """Standard message response schema."""

    message: str = Field(..., description="Success message")
    data: dict[str, Any] | None = Field(None, description="Additional data")

"""
User domain model implementing the user aggregate root.
Following DDD principles with clear business logic separation.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

if TYPE_CHECKING:
    from django.db.models import QuerySet


class UserQuerySet(models.QuerySet["User"]):
    """Custom QuerySet for User model with domain-specific methods."""

    def active(self) -> QuerySet[User]:
        """Return only active users."""
        return self.filter(is_active=True)

    def by_email(self, email: str) -> QuerySet[User]:
        """Filter users by email address."""
        return self.filter(email__iexact=email)

    def verified(self) -> QuerySet[User]:
        """Return only email-verified users."""
        return self.filter(email_verified=True)


class UserManager(BaseUserManager["User"]):
    """Custom manager for User model."""

    def get_queryset(self) -> UserQuerySet:
        return UserQuerySet(self.model, using=self._db)

    def active(self) -> QuerySet[User]:
        return self.get_queryset().active()

    def by_email(self, email: str) -> QuerySet[User]:
        return self.get_queryset().by_email(email)

    def create_user_with_profile(
        self,
        email: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
        **extra_fields: Any,  # noqa: ANN401
    ) -> User:
        """Create user with complete profile setup."""
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.

    Acts as the User aggregate root in our domain model.
    Handles authentication, profile data, and user-related business rules.
    """

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True
    )

    # Authentication fields
    email = models.EmailField(unique=True, db_index=True)
    email_verified = models.BooleanField(default=False)
    username = models.CharField(max_length=150, unique=True, db_index=True)

    # Profile fields
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    avatar_url = models.URLField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    # Custom manager
    objects: UserManager = UserManager()  # type: ignore[misc,assignment]

    # Use email as the username field
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "identity_user"
        indexes = [
            models.Index(fields=["email", "is_active"]),
            models.Index(fields=["email_verified", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.email} ({self.get_full_name() or self.username})"

    @property
    def full_name(self) -> str:
        """Return the full name or fallback to username."""
        return self.get_full_name() or self.username

    def verify_email(self) -> None:
        """Mark user's email as verified."""
        self.email_verified = True
        self.save(update_fields=["email_verified", "updated_at"])

    def update_last_login_ip(self, ip_address: str) -> None:
        """Update the user's last login IP address."""
        self.last_login_ip = ip_address
        self.save(update_fields=["last_login_ip", "updated_at"])

    def can_access_admin(self) -> bool:
        """Check if user can access admin interface."""
        return self.is_active and self.is_staff

    def to_dict(self) -> dict[str, Any]:
        """Convert user to dictionary for serialization."""
        return {
            "id": str(self.id),
            "email": self.email,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "avatar_url": self.avatar_url,
            "email_verified": self.email_verified,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

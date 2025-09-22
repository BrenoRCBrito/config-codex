"""
Unit tests for AuthService domain service.
"""

from typing import cast

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.identity.models import User

from ..domain.services import AuthenticationError, AuthService, TokenError

UserModel: type[User] = cast("type[User]", get_user_model())


class TestAuthService(TestCase):
    """Test cases for AuthService."""

    def setUp(self) -> None:
        """Set up test data."""
        self.auth_service = AuthService()
        self.test_email = "test@example.com"
        self.test_password = "testpassword123"

        self.user = User.objects.create_user_with_profile(
            email=self.test_email,
            password=self.test_password,
            first_name="Test",
            last_name="User",
        )

    def test_authenticate_user_success(self) -> None:
        """Test successful user authentication."""
        user = self.auth_service.authenticate_user(
            email=self.test_email,
            password=self.test_password,
        )

        self.assertEqual(user.email, self.test_email)
        self.assertTrue(user.is_active)

    def test_authenticate_user_invalid_password(self) -> None:
        """Test authentication with invalid password."""
        with self.assertRaises(AuthenticationError):
            self.auth_service.authenticate_user(
                email=self.test_email,
                password="wrongpassword",
            )

    def test_authenticate_user_invalid_email(self) -> None:
        """Test authentication with invalid email."""
        with self.assertRaises(AuthenticationError):
            self.auth_service.authenticate_user(
                email="nonexistent@example.com",
                password=self.test_password,
            )

    def test_create_tokens(self) -> None:
        """Test JWT token creation."""
        tokens = self.auth_service.create_tokens(self.user)

        self.assertIn("access_token", tokens)
        self.assertIn("refresh_token", tokens)
        self.assertIn("token_type", tokens)
        self.assertIn("expires_in", tokens)
        self.assertEqual(tokens["token_type"], "Bearer")

    def test_validate_access_token(self) -> None:
        """Test access token validation."""
        tokens = self.auth_service.create_tokens(self.user)
        access_token = tokens["access_token"]

        payload = self.auth_service.validate_access_token(access_token)

        self.assertEqual(payload["user_id"], str(self.user.id))
        self.assertEqual(payload["email"], self.user.email)
        self.assertEqual(payload["type"], "access")

    def test_validate_invalid_token(self) -> None:
        """Test validation of invalid token."""
        with self.assertRaises(TokenError):
            self.auth_service.validate_access_token("invalid_token")

    def test_refresh_access_token(self) -> None:
        """Test access token refresh."""
        tokens = self.auth_service.create_tokens(self.user)
        refresh_token = tokens["refresh_token"]

        new_tokens = self.auth_service.refresh_access_token(refresh_token)

        self.assertIn("access_token", new_tokens)
        self.assertIn("token_type", new_tokens)
        self.assertIn("expires_in", new_tokens)

    def test_get_user_from_token(self) -> None:
        """Test getting user from valid token."""
        tokens = self.auth_service.create_tokens(self.user)
        access_token = tokens["access_token"]

        user = self.auth_service.get_user_from_token(access_token)

        self.assertEqual(user.id, self.user.id)
        self.assertEqual(user.email, self.user.email)

    def test_register_user_success(self) -> None:
        """Test successful user registration."""
        new_email = "newuser@example.com"
        new_password = "newpassword123"

        user = self.auth_service.register_user(
            email=new_email,
            password=new_password,
            first_name="New",
            last_name="User",
        )

        self.assertEqual(user.email, new_email)
        self.assertTrue(user.check_password(new_password))

    def test_register_user_duplicate_email(self) -> None:
        """Test registration with duplicate email."""
        with self.assertRaises(ValidationError):
            self.auth_service.register_user(
                email=self.test_email,  # Already exists
                password="anotherpassword123",
            )

    def test_register_user_weak_password(self) -> None:
        """Test registration with weak password."""
        with self.assertRaises(ValidationError):
            self.auth_service.register_user(
                email="weak@example.com",
                password="123",  # Too weak
            )

"""
Integration tests for identity API endpoints.
"""

from typing import cast

from django.contrib.auth import get_user_model
from django.test import TestCase
from ninja import NinjaAPI
from ninja.testing import TestClient

from apps.identity.models import User

UserModel: type[User] = cast("type[User]", get_user_model())

_test_api: NinjaAPI | None = None
_test_client: TestClient | None = None


def get_test_api() -> NinjaAPI:
    """Get or create dedicated test API instance."""
    global _test_api
    if _test_api is None:
        _test_api = NinjaAPI(
            title="Test API",
            version="1.0.0-test",
            urls_namespace="test_api",
        )
        from apps.identity.api.auth import jwt_auth
        from apps.identity.api.auth_endpoints import (
            change_password,
            get_current_user,
            health_check,
            login,
            refresh_token,
            register,
            update_profile,
            verify_email,
        )
        from apps.identity.api.schemas import (
            AuthResponse,
            ErrorResponse,
            MessageResponse,
            TokenResponse,
            UserResponse,
        )

        _test_api.post(
            "/auth/login",
            response={200: AuthResponse, 400: ErrorResponse, 401: ErrorResponse},
        )(login)
        _test_api.post(
            "/auth/register", response={201: AuthResponse, 400: ErrorResponse}
        )(register)
        _test_api.post(
            "/auth/refresh",
            response={200: TokenResponse, 400: ErrorResponse, 401: ErrorResponse},
        )(refresh_token)
        _test_api.get(
            "/auth/me", response={200: UserResponse, 401: ErrorResponse}, auth=jwt_auth
        )(get_current_user)
        _test_api.put(
            "/auth/me",
            response={200: UserResponse, 400: ErrorResponse, 401: ErrorResponse},
            auth=jwt_auth,
        )(update_profile)
        _test_api.post(
            "/auth/change-password",
            response={200: MessageResponse, 400: ErrorResponse, 401: ErrorResponse},
            auth=jwt_auth,
        )(change_password)
        _test_api.post(
            "/auth/verify-email",
            response={200: MessageResponse, 400: ErrorResponse, 401: ErrorResponse},
            auth=jwt_auth,
        )(verify_email)
        _test_api.get("/auth/health", response={200: dict})(health_check)
    return _test_api


def get_test_client() -> TestClient:
    """Get singleton TestClient instance for dedicated test API."""
    global _test_client
    if _test_client is None:
        _test_client = TestClient(get_test_api())
    return _test_client


class TestIdentityAPIEndpoints(TestCase):
    """Test cases for identity API endpoints."""

    def setUp(self) -> None:
        """Set up test data."""
        self.api_client = get_test_client()
        self.test_email = "test@example.com"
        self.test_password = "testpassword123"

        self.user = UserModel.objects.create_user_with_profile(
            email=self.test_email,
            password=self.test_password,
            first_name="Test",
            last_name="User",
        )

    def test_login_success(self) -> None:
        """Test successful login."""
        response = self.api_client.post(
            "/auth/login",
            json={
                "email": self.test_email,
                "password": self.test_password,
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("user", data)
        self.assertIn("tokens", data)
        self.assertEqual(data["user"]["email"], self.test_email)

    def test_login_invalid_credentials(self) -> None:
        """Test login with invalid credentials."""
        response = self.api_client.post(
            "/auth/login",
            json={
                "email": self.test_email,
                "password": "wrongpassword",
            },
        )

        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertIn("error", data)

    def test_register_success(self) -> None:
        """Test successful user registration."""
        response = self.api_client.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "newpassword123",
                "first_name": "New",
                "last_name": "User",
            },
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn("user", data)
        self.assertIn("tokens", data)

    def test_register_duplicate_email(self) -> None:
        """Test registration with duplicate email."""
        response = self.api_client.post(
            "/auth/register",
            json={
                "email": self.test_email,  # Already exists
                "password": "anotherpassword123",
            },
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)

    def test_get_current_user_authenticated(self) -> None:
        """Test getting current user with valid token."""
        login_response = self.api_client.post(
            "/auth/login",
            json={
                "email": self.test_email,
                "password": self.test_password,
            },
        )
        token = login_response.json()["tokens"]["access_token"]

        response = self.api_client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["email"], self.test_email)

    def test_get_current_user_unauthenticated(self) -> None:
        """Test getting current user without token."""
        response = self.api_client.get("/auth/me")

        self.assertEqual(response.status_code, 401)

    def test_refresh_token_success(self) -> None:
        """Test successful token refresh."""
        login_response = self.api_client.post(
            "/auth/login",
            json={
                "email": self.test_email,
                "password": self.test_password,
            },
        )
        refresh_token = login_response.json()["tokens"]["refresh_token"]

        response = self.api_client.post(
            "/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)

    def test_health_check(self) -> None:
        """Test API health check endpoint."""
        response = self.api_client.get("/auth/health")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")

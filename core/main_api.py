import os
from typing import Any

from django.http import HttpRequest
from ninja import NinjaAPI


def _get_api_kwargs() -> dict[str, Any]:
    """Get API initialization kwargs with unique namespace for testing."""
    kwargs = {
        "title": "Config Codex API",
        "version": "1.0.0",
        "description": "REST API for Game Configuration Hub Service",
        "docs_url": "/docs",
    }

    if os.getenv("DJANGO_ENVIRONMENT") == "testing":
        import uuid

        kwargs["urls_namespace"] = f"api_test_{uuid.uuid4().hex[:8]}"

    return kwargs


api = NinjaAPI(**_get_api_kwargs())


@api.get("/hello")
async def hello(request: HttpRequest) -> str:
    """Simple hello world endpoint for testing."""
    return "Hello world"


@api.get("/health")
async def health(request: HttpRequest) -> dict[str, str]:
    """API health check endpoint."""
    return {
        "status": "healthy",
        "service": "config-codex-api",
        "version": "1.0.0",
    }

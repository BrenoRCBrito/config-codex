"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

from .main_api import api

_auth_setup = False


def setup_auth() -> None:
    """Setup authentication router - called once during URL configuration."""
    global _auth_setup
    if _auth_setup:
        return

    from apps.identity.api import auth_router

    api.add_router("/auth", auth_router)
    _auth_setup = True


setup_auth()

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]

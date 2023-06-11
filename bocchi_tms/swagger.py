from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from pathlib import Path
import environ
import os

env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str)
)

schema_view = get_schema_view(
    openapi.Info(
        title="Your API",
        default_version='v1',
        description="API documentation",
        terms_of_service="",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    url=env("API_URL"),
    public=True,
    permission_classes=(permissions.AllowAny,))


urlpatterns = [
    path('', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
]

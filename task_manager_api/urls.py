from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from .swagger import urlpatterns as swagger_urls
from dj_rest_auth.views import (
    LoginView, LogoutView, PasswordChangeView,
    PasswordResetView, PasswordResetConfirmView
)

rest_auth_urlpatterns = [
    path('register', include('dj_rest_auth.registration.urls'),
         name="user-auth-registration"),
    path('login', LoginView.as_view(), name="user-login"),
    path('logout', LogoutView.as_view(), name='user-logout'),
    path('password/change/', PasswordChangeView.as_view(),
         name='rest_password_change'),
    path('password/reset', PasswordResetView.as_view(),
         name='rest_password_reset'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(),
         name='rest_password_reset_confirm'),
]

urlpatterns = [
    # ...
    # Route TemplateView to serve Swagger UI template.
    #   * Provide `extra_context` with view name of `SchemaView`.
    # path('swagger-ui/', TemplateView.as_view(
    #     template_name='swagger-ui.html',
    #     extra_context={'schema_url': 'openapi-schema'}
    # ), name='swagger-ui'),
    path("admin/", admin.site.urls),
    path('', include('tasks.urls')),
    # path('', include('dj_rest_auth.urls')).remove('user'),
    path('registration/', include('dj_rest_auth.registration.urls')),
] + rest_auth_urlpatterns + swagger_urls

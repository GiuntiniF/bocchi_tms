from django.contrib import admin
from django.urls import path, include

# urlpatterns = [
#     # path("admin/", admin.site.urls),
#     path("task/", include("task.urls")),
#     path("user/", include("user.urls")),
#     path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
#     # path("accounts/", include("django.contrib.auth.urls")),
# ]


urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('tasks.urls')),
    path('', include('dj_rest_auth.urls')),
    path('registration/', include('dj_rest_auth.registration.urls')),
]

from django.urls import include, path
from rest_framework import routers
from . import views


router = routers.DefaultRouter()
router.register(r'tasks', views.TaskViewSet, basename="task")
router.register(r'users/notifications',
                views.UserNotificationAssignmentViewSet, basename="usernotificationassignment")
router.register(r'users', views.UserViewSet, basename="user")
router.register(r'groups', views.GroupViewSet, basename="group")

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls))
]

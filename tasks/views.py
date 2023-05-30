from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.exceptions import NotAuthenticated
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.utils import timezone
from .models import Task
from .permissions import IsOwnerOrReadOnly
from .serializers import TaskSerializer, UserSerializer, GroupSerializer


def get_user(request):
    user = None
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Token '):
        token = auth_header.split(' ')[1]
        user = User.objects.get(auth_token=token)
    return user


class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint that return the task associated with the user (or all the task if the user is a superuser).
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        user = get_user(self.request)
        if user.is_superuser:
            return Task.objects.all()
        else:
            return Task.objects.filter(
                Q(owner=user.id) | Q(users=user.id))

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        request.data.updated_at = timezone.now()
        print(request.data)
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        parent_task = serializer.validated_data.get('parent_task')

        if parent_task is not None:
            if parent_task.parent_task is not None:
                return Response({"error": "Cannot assign a parent_task that already has a parent_task set."}, status=status.HTTP_400_BAD_REQUEST)
            elif parent_task is instance.id:
                return Response({"error": "Cannot assign a parent_task that is the same as the task."}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_update(serializer)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        parent_task = serializer.validated_data.get('parent_task')

        if parent_task is not None and parent_task.parent_task is not None:
            return Response({"error": "Cannot assign a parent_task that already has a parent_task set."}, status=status.HTTP_400_BAD_REQUEST)

        # if parent_task.owner is not request.user:
        #     return Response({"error": "Cannot add a subtask to a task that you do not have access to."}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

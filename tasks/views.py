from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.exceptions import NotAuthenticated
from django.contrib.auth.models import User, Group
from django.db.models import Q
from .models import Task
from .exceptions import UserNotInGroupException, TaskAssignedToHisSubtaskException
from .permissions import IsUserAssignedToTask
from .serializers import TaskSerializer, UserSerializer, GroupSerializer


def get_user(request):
    user = None
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Token '):
        token = auth_header.split(' ')[1]
        user = User.objects.get(auth_token=token)
    return user


def check_parent_task_as_subtask(instance, serializer):
    new_parent_task = serializer.validated_data.get('parent_task')
    if new_parent_task is not None:
        subtask_list = list(Task.objects.filter(parent_task=instance.id))
        while subtask_list is not None and len(subtask_list) > 0:
            subtask = subtask_list.pop()
            subtask_list = subtask_list + \
                list(Task.objects.filter(parent_task=subtask.id))
            if new_parent_task.id is subtask.id:
                raise TaskAssignedToHisSubtaskException()


def check_assigned_users_in_groups(serializer):
    # per ogni user assegnato al task controllo se fa parte di almeno un gruppo dei task, altrimenti ritorno errore
    request_groups = serializer.validated_data.get('groups')
    request_users = serializer.validated_data.get('users')
    # FIXME aggiungi controllo
    if request_groups is not None and request_users is not None:
        for user in request_users:
            is_user_assignable = False
            user_instance = User.objects.get(pk=user.id)
            user_instance_groups = user_instance.groups.all()
            for group in user_instance_groups:
                if group in request_groups:
                    is_user_assignable = True
            if is_user_assignable == False:
                raise UserNotInGroupException(context=user_instance)


def set_parent_tasks_users(serializer):
    parent_task = serializer.validated_data.get('parent_task')
    request_groups = serializer.validated_data.get('groups')
    request_users = serializer.validated_data.get('users')
    if request_groups is not None and request_users is not None:
        while parent_task is not None:
            parent_task.users.add(*request_users)
            parent_task.groups.add(*request_groups)
            parent_task.save()
            parent_task = parent_task.parent_task


def remove_user_and_group_from_subtasks(instance, serializer):
    # rimuovendo utenti e gruppi da un task padre, li rimuovo anche da tutti i task figli
    request_groups = serializer.validated_data.get('groups')
    request_users = serializer.validated_data.get('users')
    if request_groups is not None and request_users is not None:
        subtask_list = list(Task.objects.filter(parent_task=instance.id))
        while subtask_list is not None and len(subtask_list) > 0:
            subtask = subtask_list.pop()
            subtask_list = subtask_list + \
                list(Task.objects.filter(parent_task=subtask.id))
            for user in subtask.users.all():
                if user not in request_users:
                    subtask.users.remove(user)
            for group in subtask.groups.all():
                if group not in request_users:
                    subtask.groups.remove(group)
            subtask.save()


class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint that return the task associated with the user (or all the task if the user is a superuser).
    """
    serializer_class = TaskSerializer
    permission_classes = [
        permissions.IsAuthenticated, IsUserAssignedToTask]

    def get_queryset(self):
        user = get_user(self.request)
        # FIXME implement both my tasks and tasks assigned to me
        if user.is_superuser:
            return Task.objects.all().order_by('-id')
        else:
            return Task.objects.all().order_by('id')
            # return Task.objects.filter(
            #     Q(owner=user.id) | Q(users=user.id)).distinct()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        parent_task = serializer.validated_data.get('parent_task')
        if parent_task is not None and parent_task is instance.id:
            return Response({"error": "Cannot set a subtask parent task to itself."}, status=status.HTTP_400_BAD_REQUEST)

        check_parent_task_as_subtask(instance, serializer)
        check_assigned_users_in_groups(serializer)
        remove_user_and_group_from_subtasks(instance, serializer)
        self.perform_update(serializer)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        check_assigned_users_in_groups(serializer)
        set_parent_tasks_users(serializer)
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

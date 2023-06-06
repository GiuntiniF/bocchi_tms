from rest_framework import viewsets, status, permissions, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from .models import Task, UserNotificationAssignment
from .notifications import create_task_added_notification, create_group_added_removed_notification, create_user_added_removed_notification, create_task_deleted_notification, create_task_status_updated_notification, create_task_deadline_updated_notification
from .exceptions import UserNotInGroupException, TaskAssignedToHisSubtaskException
from .permissions import IsSuperuserOrReadOnly, IsOwnerOrSuperuserOrReadOnly, AssignedUserOrOwnerOsSuperuserCanView
from .serializers import TaskSerializer, UserSerializer, GroupSerializer, UserNotificationAssignmentSerializer


def check_parent_task_as_subtask(instance, serializer):
    new_parent_task = serializer.validated_data.get('parent_task')
    if new_parent_task is not None:
        subtask_list = list(instance.subtasks.all())
        while subtask_list is not None and len(subtask_list) > 0:
            subtask = subtask_list.pop()
            subtask_list = subtask_list + \
                list(subtask.subtasks.all())
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
    request_status = serializer.validated_data.get('status')
    subtask_list = list(instance.subtasks.all())
    while subtask_list is not None and len(subtask_list) > 0:
        subtask = subtask_list.pop()
        subtask_list = subtask_list + \
            list(subtask.subtasks.all())
        if request_users is not None and len(request_users) > 0:
            for user in subtask.users.all():
                if user not in request_users:
                    subtask.users.remove(user)
        if request_groups is not None and len(request_groups) > 0:
            for group in subtask.groups.all():
                if group not in request_groups:
                    subtask.groups.remove(group)
        if subtask.status != 'COMPLETED':
            subtask.status = request_status
        subtask.save()


class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint that returns the task associated with the user (or all the task if the user is a superuser).
    """
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            # superusers can see all tasks
            queryset = Task.objects.all().order_by('-id')
        elif self.action == 'list_created_tasks' or self.action == 'update' or self.action == 'partial_update' or self.action == 'destroy':
            # task that the user has created
            queryset = user.created_tasks.all().order_by('-id')
        else:
            # tasks that are assigned to the user
            queryset = user.assigned_tasks.all()

        return queryset

    def get_permission(self):
        permission_classes = [permissions.IsAuthenticated, AssignedUserOrOwnerOsSuperuserCanView,
                              IsOwnerOrSuperuserOrReadOnly]
        return permission_classes

    @action(detail=False, methods=['get'], url_path='created', url_name='created_tasks')
    def list_created_tasks(self, request):
        """
        API endpoint that returns the task created by the user.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='assigned', url_name='assigned_tasks')
    def list_assigned_tasks(self, request):
        """
        API endpoint that returns the task assigned to the user.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        if request.user.is_superuser:
            """
            API endpoint that returns all the task associated if the user is a superuser, or an API root for the task lists otherwise.
            """
            # a superuser can see all the taska that are in the system
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            # a non-superuser can only see the tasks that he created or the ones that are assigned to him
            data = {
                'message': 'Task List API root',
                'endpoints': {
                    'assigned-tasks': self.reverse_action('assigned_tasks', request=request),
                    'created-tasks': self.reverse_action('created_tasks', request=request),
                }
            }
            return Response(data)

    def retrieve(self, request, pk=None):
        queryset = Task.objects.all()
        task = get_object_or_404(queryset, pk=pk)
        self.check_object_permissions(request, obj=task)
        serializer = TaskSerializer(task, context={'request': request})
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        parent_task = serializer.validated_data.get('parent_task')
        if parent_task is not None and parent_task is instance.id:
            return Response({"error": "Cannot set a subtask parent task to itself."}, status=status.HTTP_400_BAD_REQUEST)

        if 'status' not in serializer.validated_data:
            # Field is not present, maintain the current value
            serializer.validated_data['status'] = instance.status

        check_parent_task_as_subtask(instance, serializer)
        check_assigned_users_in_groups(serializer)
        remove_user_and_group_from_subtasks(instance, serializer)
        self.perform_update(serializer, instance)
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
        updated_istance = serializer.save(owner=self.request.user)
        create_task_added_notification(updated_istance)

    def perform_update(self, serializer, instance):
        old_group_list = list(instance.groups.all())
        old_user_list = list(instance.users.all())
        old_status = instance.status
        old_deadline = instance.deadline_date
        updated_istance = serializer.save()
        create_group_added_removed_notification(
            old_group_list, old_user_list, serializer, updated_istance)
        create_user_added_removed_notification(
            old_user_list, serializer, updated_istance)
        create_task_status_updated_notification(updated_istance, old_status)
        create_task_deadline_updated_notification(
            updated_istance, old_deadline)

    def perform_destroy(self, serializer):
        instance = self.get_object()
        old_group_list = list(instance.groups.all())
        old_user_list = list(instance.users.all())
        old_task_id = instance.id
        old_task_title = instance.title
        serializer.delete()
        create_task_deleted_notification(
            old_group_list, old_user_list, old_task_id, old_task_title, serializer)


class UserNotificationAssignmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    serializer_class = UserNotificationAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            queryset = UserNotificationAssignment.objects.all()
        else:
            queryset = UserNotificationAssignment.objects.filter(user=user)
        return queryset

    # def list(self, request):
    #     queryset = self.get_queryset()
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)


class UserViewSet(mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperuserOrReadOnly]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited(only if you are logged as a superuser).
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperuserOrReadOnly]

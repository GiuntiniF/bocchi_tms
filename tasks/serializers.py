from .models import Task, TaskStatus, UserNotification, UserNotificationAssignment
from rest_framework import serializers
from django.contrib.auth.models import User, Group


class TaskReadSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(
        source='owner.id', read_only=True)
    users = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all())
    groups = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Group.objects.all())
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'url', 'title', 'description', 'owner', 'status', 'progress',
                  'created_at', 'updated_at', 'deadline_date', 'parent_task', 'subtasks', 'users', 'groups']

    def get_progress(self, obj):
        if obj.status == 'COMPLETED':
            return '100%'
        if obj.subtasks is not None and obj.subtasks.count() > 0:
            completed_subtasks = obj.subtasks.filter(status='COMPLETED')
            return str(int(completed_subtasks.count() / obj.subtasks.count() * 100)) + '%'
        else:
            return '0%'


class TaskWriteSerializer(serializers.HyperlinkedModelSerializer):
    # owner = serializers.PrimaryKeyRelatedField(
    #     source='owner.id', read_only=True)
    users = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all())
    groups = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Group.objects.all())

    class Meta:
        model = Task
        fields = ['title', 'description', 'status',
                  'deadline_date', 'parent_task', 'users', 'groups']


class UserNotificationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserNotification
        fields = ['message', 'type']


class UserNotificationAssignmentSerializer(serializers.HyperlinkedModelSerializer):
    notification = UserNotificationSerializer(read_only=True)

    class Meta:
        model = UserNotificationAssignment
        fields = ['id', 'url', 'user', 'is_read', 'notification']
        # lookup_field = 'id'


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'url', 'username', 'first_name', 'last_name', 'is_superuser',
                  'email', 'groups', 'created_tasks', 'notification_list']


class GroupWriteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['name']


class GroupReadSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'url', 'name', 'user_set']

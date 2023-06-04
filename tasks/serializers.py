from .models import Task, TaskStatus
from rest_framework import serializers
from django.contrib.auth.models import User, Group


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(
        source='owner.id', read_only=True)
    users = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all())
    groups = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Group.objects.all())
    status = serializers.PrimaryKeyRelatedField(
        queryset=TaskStatus.objects.all())
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'url', 'title', 'description', 'owner', 'status', 'progress',
                  'created_at', 'updated_at', 'deadline_date', 'parent_task', 'users', 'groups']

    def get_progress(self, obj):
        if obj.status.name == 'completed':
            return '100%'
        if obj.subtasks is not None and obj.subtasks.count() > 0:
            completed_subtasks = obj.subtasks.filter(status='completed')
            return str(int(completed_subtasks.count() / obj.subtasks.count() * 100)) + '%'
        else:
            return '0%'


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'url', 'username',
                  'email', 'groups', 'notification_list']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'url', 'name', 'user']

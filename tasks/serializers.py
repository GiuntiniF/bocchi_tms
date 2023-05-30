from .models import Task
from .permissions import IsOwnerOrReadOnly
from rest_framework import serializers
from django.contrib.auth.models import User, Group


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(
        source='owner.id', read_only=True)
    users = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all())
    groups = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Group.objects.all())

    class Meta:
        model = Task
        fields = ['id', 'url', 'title', 'description', 'owner', 'is_completed', 'test',
                  'created_at', 'updated_at', 'deadline_date', 'parent_task', 'users', 'groups']


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups', 'id']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

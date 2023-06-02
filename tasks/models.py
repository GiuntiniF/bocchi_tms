from django.db import models
from django.contrib.auth.models import User, Group


class Task(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    is_completed = models.BooleanField(default=False)
    test = models.BooleanField(default=False)
    created_at = models.DateTimeField(
        'created at', auto_now_add=True, editable=False)
    updated_at = models.DateTimeField('updated at', auto_now=True)
    deadline_date = models.DateTimeField(
        'deadline', null=True, blank=True, default=None)
    owner = models.ForeignKey(
        'auth.User', related_name='task_created', on_delete=models.CASCADE)
    groups = models.ManyToManyField(
        Group, related_name='tasks', null=True, blank=True)
    users = models.ManyToManyField(
        User, related_name='tasks', null=True, blank=True)

    parent_task = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE)


# Create your models here.

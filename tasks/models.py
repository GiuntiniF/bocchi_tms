from django.db import models
from django.contrib.auth.models import User, Group


class UserNotificationsTypes(models.Model):
    type = models.CharField(max_length=50, primary_key=True)


class TaskStatus(models.Model):
    name = models.CharField(max_length=50, primary_key=True)


class UserNotifications(models.Model):
    user = models.ForeignKey(
        User, related_name='notification_list', on_delete=models.CASCADE)
    type = models.ForeignKey(
        UserNotificationsTypes, related_name='notification_list', on_delete=models.CASCADE)
    message = models.TextField()
    is_readed = models.BooleanField(default=False)


class Task(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    status = models.ForeignKey(
        TaskStatus, default="on hold", on_delete=models.CASCADE)
    created_at = models.DateTimeField(
        'created at', auto_now_add=True, editable=False)
    updated_at = models.DateTimeField('updated at', auto_now=True)
    deadline_date = models.DateTimeField(
        'deadline', null=True, blank=True, default=None)
    owner = models.ForeignKey(
        User, related_name='created_tasks', on_delete=models.CASCADE)
    groups = models.ManyToManyField(
        Group, related_name='assigned_tasks', blank=True)
    users = models.ManyToManyField(
        User, related_name='assigned_tasks', blank=True)
    parent_task = models.ForeignKey(
        'self', related_name="subtasks", null=True, blank=True, on_delete=models.CASCADE)


# Create your models here.

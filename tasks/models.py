from django.db import models
from django.contrib.auth.models import User, Group


# class UserNotificationType(models.Model):
#     type = models.CharField(max_length=50, primary_key=True)

class NotificationType(models.TextChoices):
    DEFAULT = "DEFAULT",
    GROUP_ADDED = "GROUP_ADDED",  # ok
    GROUP_REMOVED = "GROUP_REMOVED",  # ok
    STATUS_CHANGED = "STATUS_CHANGED",  # ok
    TASK_DELETED = "TASK_DELETED",  # ok
    USER_ADDED = "USER_ADDED",  # ok
    USER_REMOVED = "USER_REMOVED",  # ok
    DEADLINE_CHANGED = "DEADLINE_CHANGED",  # ok


class UserNotification(models.Model):

    type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        default=NotificationType.DEFAULT,
    )
    message = models.TextField()


class UserNotificationAssignment(models.Model):
    notification = models.ForeignKey(
        UserNotification, related_name='receiver_list', on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, related_name='notification_list', on_delete=models.CASCADE)
    is_readed = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['notification', 'user'], name='unique_notification_user')
        ]


class TaskStatus(models.Model):
    name = models.CharField(max_length=50, primary_key=True)


class TaskStatus(models.TextChoices):
    ON_HOLD = "ON HOLD"
    IN_PROGRESS = "IN PROGRESS"
    COMPLETED = "COMPLETED"


class Task(models.Model):

    title = models.CharField(max_length=50)
    description = models.TextField()
    # status = models.ForeignKey(
    #     TaskStatus, on_delete=models.SET_NULL, default=TaskStatus.DEFAULT_PK, null=True)
    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.ON_HOLD,
    )

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

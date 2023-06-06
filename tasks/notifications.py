from .models import UserNotification, UserNotificationAssignment, NotificationType


def create_notification(user_to_notify, notification_data):
    new_notification = UserNotification.objects.create(**notification_data)
    if new_notification is not None:
        for user in user_to_notify:
            UserNotificationAssignment.objects.create(
                notification=new_notification, user=user)


def create_task_added_notification(updated_istance):
    notification_data = {
        'type': NotificationType.USER_ADDED,
        'message': 'You have been assigned to the task ' + str(updated_istance.id) + ': ' + updated_istance.title,
    }
    create_notification(updated_istance.users.all(), notification_data)


def create_group_added_removed_notification(old_group_list, old_user_list, serializer, updated_istance):
    # TODO chi notifico? tutti gli user del gruppo aggiunto e gli user già presenti nel task
    group_removed = []
    group_added = []
    if serializer.validated_data.get('groups') is not None:
        for group in old_group_list:
            if group not in serializer.validated_data.get('groups'):
                group_removed.append(group)
        for group in serializer.validated_data.get('groups'):
            if group not in old_group_list:
                group_added.append(group)
    if len(group_removed) > 0:
        user_notified_set = set()
        for group in group_removed:
            user_to_notify = group.user_set.all()
            # if a group has been removed, i notify all the user in the task
            notification_data = {
                'type': NotificationType.GROUP_REMOVED,
                'message': 'Your group ' + str(group.id) + ': ' + group.name + ' has been removed from the task ' + str(updated_istance.id) + ': ' + updated_istance.title
            }
            create_notification(user_to_notify, notification_data)
            user_notified_set = user_notified_set.union(set(user_to_notify))

        # And then i notify the remaining users the remaining users, without notifying the users already notified in the previous step
        user_to_notify = list(set(old_user_list) - user_notified_set)
        if len(user_to_notify) > 0:
            notification_message_groups = []
            notification_message = 'The following groups have been removed from the task ' + \
                str(updated_istance.id) + ': ' + updated_istance.title + '\n'
            for group in group_removed:
                notification_message_groups.append(
                    str(group.id) + '-' + group.name)
            notification_data = {
                'type': NotificationType.GROUP_REMOVED,
                'message': notification_message + '\n'.join(notification_message_groups)
            }
            create_notification(user_to_notify, notification_data)
    if len(group_added) > 0:
        user_notified_set = set()
        for group in group_added:
            user_to_notify = group.user_set.all()
            # if there are users in the group, i notify them
            notification_data = {
                'type': NotificationType.GROUP_ADDED,
                'message': 'You group ' + str(group.id) + ': ' + group.name + 'has been assigned to the task ' + str(updated_istance.id) + ': ' + updated_istance.title
            }
            create_notification(user_to_notify, notification_data)
            user_notified_set = user_notified_set.union(set(user_to_notify))

        # And then i notify the other users that there are new groups added to the task
        old_user_set = set(old_user_list)
        user_to_notify = list(old_user_set - user_notified_set)
        if len(user_to_notify) > 0:
            notification_message_users = []
            notification_message = 'The following group have been assigned to the task ' + \
                str(updated_istance.id) + ': ' + updated_istance.title + '\n'
            for group in group_added:
                notification_message_users.append(
                    str(group.id) + '-' + group.name)
            notification_data = {
                'type': NotificationType.GROUP_ADDED,
                'message': notification_message + '\n'.join(notification_message_users)
            }
            create_notification(user_to_notify, notification_data)


def create_user_added_removed_notification(old_user_list, serializer, updated_istance):
    user_removed = []
    user_added = []
    if serializer.validated_data.get('users') is not None:
        for user in old_user_list:
            if user not in serializer.validated_data.get('users'):
                user_removed.append(user)
        for user in serializer.validated_data.get('users'):
            if user not in old_user_list:
                user_added.append(user)
    if len(user_removed) > 0:
        # if there are users removed from the task, i notify them
        notification_data = {
            'type': NotificationType.USER_REMOVED,
            'message': 'You have been removed from the task ' + str(updated_istance.id) + ': ' + updated_istance.title
        }
        create_notification(user_removed, notification_data)

        # And then i notify the remaining users that the removed users are no longer part of the task
        old_user_set = set(old_user_list)
        user_removed_set = set(user_removed)
        user_to_notify = list(old_user_set - user_removed_set)
        if len(user_to_notify) > 0:
            notification_message_users = []
            notification_message = 'The following users have been removed from the task ' + \
                str(updated_istance.id) + ': ' + updated_istance.title + '\n'
            for user in user_removed:
                notification_message_users.append(
                    str(user.id) + '-' + user.username)
            notification_data = {
                'type': NotificationType.USER_REMOVED,
                'message': notification_message + '\n'.join(notification_message_users)
            }
            create_notification(user_to_notify, notification_data)
    if len(user_added) > 0:
        # if there are users added to the task, i notify them
        notification_data = {
            'type': NotificationType.USER_ADDED,
            'message': 'You have been assigned to the task ' + str(updated_istance.id) + ': ' + updated_istance.title,
        }
        create_notification(user_added, notification_data)
        # And then i notify the other users that there are new users added to the task
        old_user_set = set(old_user_list)
        user_added_set = set(user_added)
        user_to_notify = list(old_user_set - user_added_set)
        if len(user_to_notify) > 0:
            notification_message_users = []
            notification_message = 'The following users have been assigned to the task ' + \
                str(updated_istance.id) + ': ' + updated_istance.title + '\n'
            for user in user_added:
                notification_message_users.append(
                    str(user.id) + '-' + user.username)
            notification_data = {
                'type': NotificationType.USER_ADDED,
                'message': notification_message + '\n'.join(notification_message_users)
            }
            create_notification(user_to_notify, notification_data)


def create_task_deleted_notification(old_group_list, old_user_list, old_task_id, old_task_title, serializer):
    if len(old_user_list) > 0:
        # if there are users removed from the task, i notify them
        notification_data = {
            'type': NotificationType.TASK_DELETED,
            'message': 'The task ' + str(old_task_id) + ': ' + old_task_title + ' you were assigned to has been deleted'
        }
        create_notification(old_user_list, notification_data)
    user_to_notify = set()
    for group in old_group_list:
        user_to_notify = user_to_notify.union(set(group.user_set.all()))
    old_user_set = set(old_user_list)
    user_to_notify = list(user_to_notify - old_user_set)
    if len(user_to_notify) > 0:
        notification_data = {
            'type': NotificationType.TASK_DELETED,
            'message': 'The task ' + str(old_task_id) + ': ' + old_task_title + ' one of your group was assigned to has been deleted\n'
        }
        create_notification(user_to_notify, notification_data)


def create_task_status_updated_notification(updated_instance, old_status):
    if old_status is not None and old_status != updated_instance.status:
        user_list = list(updated_instance.users.all())
        if len(user_list) > 0:
            notification_data = {
                'type': NotificationType.STATUS_CHANGED,
                'message': 'The status of the task ' + str(updated_instance.id) + ': ' + updated_instance.title + ' you are assigned to has changed to ' + updated_instance.status
            }
            create_notification(user_list, notification_data)


def create_task_deadline_updated_notification(updated_instance, old_deadline):
    if old_deadline is not None and old_deadline != updated_instance.deadline_date:
        print('newdeadline')
        user_list = list(updated_instance.users.all())
        if len(user_list) > 0:
            notification_data = {
                'type': NotificationType.DEADLINE_CHANGED,
                'message': 'The deadline of the task ' + str(updated_instance.id) + ': ' + updated_instance.title + ' you are assigned to has changed to ' + str(updated_instance.deadline_date)
            }
            create_notification(user_list, notification_data)

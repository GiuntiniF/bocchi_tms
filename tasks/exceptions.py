from rest_framework.exceptions import APIException


class UserNotInGroupException(APIException):
    status_code = 400
    default_detail = 'One or more users are not part of any of the specified task groups.'
    default_code = 'user_not_in_group'

    def __init__(self, detail=None, code=None, context=None):
        detail = self.default_detail
        if context is not None and context.username is not None and context.username and type(context.username) is str:
            detail = 'User ' + context.username + \
                ' is not part of any of the specified task groups.'
        super().__init__(detail, code)


class TaskAssignedToHisSubtaskException(APIException):
    status_code = 400
    default_detail = 'Cannot set the parent task as a subtask.'
    default_code = 'parent_task_set_to_subtask'

from rest_framework import permissions


class AssignedUserOrOwnerOsSuperuserCanView(permissions.BasePermission):
    """
    Custom permissions to only allow Owners, Superusers or Assigned User to access a task
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return (request.user in list(obj.users.all())) | (obj.owner == request.user) | (request.user.is_superuser)
        return False


class IsOwnerOrSuperuserOrReadOnly(permissions.BasePermission):
    """
    Custom permissions to only allow Owners or Superusers to edit a task
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (obj.owner == request.user) | (request.user.is_superuser)


class IsSuperuserOrReadOnly(permissions.BasePermission):
    """
    Custom permissions to only allow Owners or Superusers to edit a task
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_superuser

# class isAssignedUserOrOwnerOrSuperuser(permissions.BasePermission):
#     """
#     Custom permissions to only allow Owners to edit
#     """

#     def has_object_permission(self, request, view, obj):
#         if request.method in permissions.SAFE_METHODS:
#             return obj.owner == request.user | request.user.is_superuser
#         return False

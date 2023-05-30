from rest_framework import permissions


# class IsSuperuserOrReadOnly(permissions.BasePermission):
#     """
#     Custom permissions to only allow Owners to edit
#     """

#     def has_object_permission(self, request, view, obj):
#         if request.method in permissions.SAFE_METHODS:
#             return True

#         return request.user.is_superuser


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permissions to only allow Owners to edit
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.owner == request.user

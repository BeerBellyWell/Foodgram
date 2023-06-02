from rest_framework.permissions import BasePermission, SAFE_METHODS


class AdminOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_admin


class ReadOrAdminOnly(BasePermission):
    """Доступ админу к действиям над объектом."""
    def has_permission(self, request, view):

        return (request.method in SAFE_METHODS
                or (request.user.is_authenticated
                    and request.user.is_admin))


class AuthorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or obj.author == request.user)

from rest_framework import permissions


class AuthorOrReading(permissions.BasePermission):
    def has_object_permission(self, request, view, user):
        if request.method in permissions.SAFE_METHODS or request.user == user:
            return True
        return False
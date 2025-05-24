from rest_framework import permissions


class RecipePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user and request.user.is_authenticated
        return True
    
    def has_object_permission(self, request, view, recipe):
        if request.method == "GET" or request.user == recipe.author:
            return True
        return False


class AuthorOrReading(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ["list", "create", "retrieve"]:
            return True
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, user):
        if view.action == "retrieve":
            return True
        return request.user and request.user.is_authenticated
from rest_framework import permissions


class AuthorOrReading(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'author'):
            return (request.method in permissions.SAFE_METHODS 
                    or obj.author == request.user)
        return (request.method in permissions.SAFE_METHODS
                or obj == request.user)
    
    def has_permission(self, request, view):
        if view.__class__.__name__ == "RecipeViewSet":
            return (request.method in permissions.SAFE_METHODS
                    or request.user.is_authenticated)
        return True
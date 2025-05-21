from rest_framework import permissions

class RecipePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Разрешаем все GET-запросы
        if request.method == 'GET' and view.action not in [
            "favorite", 
            "shopping_cart", 
            "download_shopping_cart"
        ]:
            return True
            
        if view.action in [
            "favorite", 
            "shopping_cart", 
            "download_shopping_cart"
        ] or request.method in ["POST", "PATCH", "DELETE"]:
            return request.user and request.user.is_authenticated
            
        return False
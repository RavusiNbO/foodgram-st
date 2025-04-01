from django.urls import path, include
from .views import RecipeViewSet, IngredientViewSet, CustomUserViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)
router.register('users', CustomUserViewSet)
# router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart', PurchaseListViewSet, basename="purchase_list")

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls'))
]

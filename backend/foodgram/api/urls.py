from django.urls import path, include
from .views import RecipeView, IngredientViewSet, CustomUserViewSet, FollowViewSet, FavoriteViewSet, PurchaseListViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('ingredients', IngredientViewSet)
router.register('users/subscriptions', FollowViewSet, basename="follows")
router.register('users', CustomUserViewSet)
router.register(r'recipes/(?P<recipe_id>\d+)/favorite', FavoriteViewSet, basename="favorite")
router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart', PurchaseListViewSet, basename="purchase_list")

urlpatterns = [
    path('recipes/', RecipeView.as_view(), name='recipe_list'),
    path('', include(router.urls)),
    path('', include('djoser.urls'))
]

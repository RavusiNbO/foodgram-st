from django.urls import path, include
from .views import RecipeViewSet, IngredientViewSet, FoodgramUserViewSet
from rest_framework.routers import DefaultRouter
from .views import redirect_recipe_by_short_link

router = DefaultRouter()
router.register("recipes", RecipeViewSet)
router.register("ingredients", IngredientViewSet)
router.register("users", FoodgramUserViewSet)
urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
    path('r/<int:pk>/', redirect_recipe_by_short_link, name='recipe_short_link'),
]
from django.urls import path, include
from .views import RecipeViewSet, IngredientViewSet
from .views import FoodgramUserViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("recipes", RecipeViewSet)
router.register("ingredients", IngredientViewSet)
router.register("users", FoodgramUserViewSet)
urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
]
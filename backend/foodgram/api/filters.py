from django_filters import rest_framework as filters
from recipes.models import Recipe, Ingredient


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="startswith")

    class Meta:
        model = Ingredient
        fields = ["name"]


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(method="filter_is_favorited")
    is_in_shopping_cart = filters.BooleanFilter(
        method="filter_is_in_shopping_cart"
    )
    author = filters.NumberFilter(field_name="author__id")

    class Meta:
        model = Recipe
        fields = ["author", "is_favorited", "is_in_shopping_cart"]

    def filter_is_favorited(self, recipes, name, value):
        if value and self.request.user.is_authenticated:
            return recipes.filter(favorites__user=self.request.user)
        return recipes

    def filter_is_in_shopping_cart(self, recipes, name, value):
        if value and self.request.user.is_authenticated:
            return recipes.filter(carts__user=self.request.user)
        return recipes

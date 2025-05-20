from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from . import models
from django.core.validators import RegexValidator


class ProductInRecipeInline(admin.StackedInline):
    model = models.ProductInRecipe
    extra = 1

@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'image',
        'text',
        'cooking_time',
        'get_ingredients',
        'author',
        'fav_count'
    )
    search_fields = ("author__username", "name")
    inlines = (ProductInRecipeInline,)

    def fav_count(self, recipe):
        return models.Favorite.objects.filter(recipe=recipe).count()
    fav_count.short_description = 'Добавления в избранное'

    def get_ingredients(self, recipe):
        return ", ".join([ingredient.name for ingredient in recipe.ingredients.all()])

    @mark_safe
    def image(self, recipe):
        return f'<img src="{recipe.image}">'
    
    # @mark_safe
    # def ingredients(self, recipe):


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'recipe_count')
    search_fields = ("name", "measurement_unit")
    list_filter = ('measurement_unit',)

    def recipe_count(self, ingredient):
        return models.ProductInRecipe.objects.filter(ingredient=ingredient).count()



@admin.register(models.FoodgramUser)
class UserAdminka(UserAdmin):
    search_fields = ("username", 'email')

admin.site.register(models.ProductInRecipe)
admin.site.register(models.Cart)
admin.site.register(models.Favorite)
admin.site.register(models.Follow)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from . import models


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
        'ingredients_list',
        'author',
        'fav_count'
    )
    search_fields = ("author__username", "name")
    inlines = (ProductInRecipeInline,)

    def fav_count(self, recipe):
        return models.Favorite.objects.filter(recipe=recipe).count()
    fav_count.short_description = 'Добавления в избранное'

    def ingredients_list(self, recipe):
        return ", ".join(
            [ingredient.name for ingredient in recipe.ingredients.all()])

    @mark_safe
    def image(self, recipe):
        return f'<img src="{recipe.image}">'


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'recipe_count')
    search_fields = ("name", "measurement_unit")
    list_filter = ('measurement_unit',)

    def recipe_count(self, ingredient):
        return models.ProductInRecipe.objects.filter(
            ingredient=ingredient).count()


@admin.register(models.FoodgramUser)
class UserAdminka(UserAdmin):
    search_fields = ("username", 'email')
    list_display = (
        "id",
        'username',
        'FIO',
        'email',
        'avatar',
        'recipes_count',
        'follow_count',
        'followers_count'
    )

    def recipes_count(self, user):
        return models.Recipe.objects.filter(author=user).count()
    recipes_count.short_description = 'Количество рецептов'

    def followers_count(self, user):
        return models.Follow.objects.filter(user=user).count()
    followers_count.short_description = 'Количество подписчиков'

    def follow_count(self, user):
        return models.Follow.objects.filter(follower=user).count()
    follow_count.short_description = 'Количество подписок'

    def FIO(self, user):
        return f'{user.last_name} {user.first_name}'

    @mark_safe
    def avatar(self, user):
        return f'<img src="{user.avatar}">'


admin.site.register(models.ProductInRecipe)
admin.site.register(models.Cart)
admin.site.register(models.Favorite)
admin.site.register(models.Follow)

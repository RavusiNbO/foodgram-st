from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from . import models
from django.contrib.admin import display


class ProductInRecipeInline(admin.StackedInline):
    model = models.ProductInRecipe
    extra = 1


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'image',
        'cooking_time',
        'author',
        'fav_count'
    )
    list_filter = ('author',)
    search_fields = ("author__username", "name")
    inlines = (ProductInRecipeInline,)

    @display(description='Избранное')
    def fav_count(self, recipe):
        return recipe.favorites.count()

    @display(description='Аватар')
    @mark_safe
    def image(self, recipe):
        return f'<img src="{recipe.image}">'


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'recipe_count')
    search_fields = ("name", "measurement_unit")
    list_filter = ('measurement_unit',)

    @display(description='Рецептов')
    def recipe_count(self, ingredient):
        return ingredient.products.count()


@admin.register(models.FoodgramUser)
class FoodgramUserAdmin(UserAdmin):
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

    @display(description='Рецептов')
    def recipes_count(self, user):
        return user.recipes.count()

    @display(description='Подписчиков')
    def followers_count(self, user):
        return user.follows_user.count()

    @display(description='Подписок')
    def follow_count(self, user):
        return user.follows_follower.count()

    @display(description='ФИО')
    def FIO(self, user):
        return f'{user.last_name} {user.first_name}'

    @mark_safe
    def avatar(self, user):
        return f'<img src="{user.avatar}">'


admin.site.register(models.ProductInRecipe)
admin.site.register(models.Cart)
admin.site.register(models.Favorite)
admin.site.register(models.Follow)

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

    @display(description='Добавления в избранное')
    def fav_count(self, recipe):
        return recipe.favorites.count()

    @mark_safe
    def image(self, recipe):
        return f'<img src="{recipe.image}">'


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'recipe_count')
    search_fields = ("name", "measurement_unit")
    list_filter = ('measurement_unit',)

    @display(description='Количество рецептов')
    def recipe_count(self, ingredient):
        return ingredient.products.count()


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

    @display(description='Количество рецептов')
    def recipes_count(self, user):
        return user.recipes.count()
    recipes_count.short_description = 'Количество рецептов'

    @display(description='Количество подписчиков')
    def followers_count(self, user):
        return user.follows_user.count()
    followers_count.short_description = 'Количество подписчиков'

    @display(description='Количество подписок')
    def follow_count(self, user):
        return user.follows_follower.count()
    follow_count.short_description = 'Количество подписок'

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

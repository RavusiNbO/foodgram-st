from . import models
from django.contrib import admin
from users.models import Favorite


class AmountInline(admin.StackedInline):
    model = models.Amount
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    search_fields = ("author__name", "name")
    inlines = (AmountInline,)

    def fav_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()




class IngredientAdmin(admin.ModelAdmin):
    search_fields = ("name",)


admin.site.register(models.Ingredient, IngredientAdmin)
admin.site.register(models.Recipe, RecipeAdmin)
admin.site.register(models.Amount)

from . import models
from django.contrib import admin


class AmountInline(admin.StackedInline):  # или admin.StackedInline
    model = models.Amount
    extra = 1  # Количество пустых форм для добавления


class RecipeAdmin(admin.ModelAdmin):
    search_fields = ("author", "name")
    inlines = (AmountInline,)


class IngredientAdmin(admin.ModelAdmin):
    search_fields = ("name",)


admin.site.register(models.Ingredient, IngredientAdmin)
admin.site.register(models.Recipe, RecipeAdmin)
admin.site.register(models.Amount)

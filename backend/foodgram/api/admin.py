from . import models
from django.contrib import admin



class RecipeAdmin(admin.ModelAdmin):
    search_fields=("author", "name")

class IngredientAdmin(admin.ModelAdmin):
    search_fields=("name",)

# class CustomUserAdmin(UserAdmin):
#     list_display="__all__"
#     list_editable="__all__"
#     search_fields=("email", "first_name")



admin.site.register(models.Ingredient, IngredientAdmin)
admin.site.register(models.Recipe, RecipeAdmin)


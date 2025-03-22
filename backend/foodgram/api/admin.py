from . import models
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

UserAdmin.fieldsets += (
    ('Extra Fields', {'fields' : ('bio', )}),
)

class RecipeAdmin(admin.ModelAdmin):
    list_display='__all__'
    list_editable="__all__"
    search_fields=("author", "name")

class IngredientAdmin(admin.ModelAdmin):
    list_display="__all__"
    list_editable="__all__"
    search_fields=("name",)

# class CustomUserAdmin(UserAdmin):
#     list_display="__all__"
#     list_editable="__all__"
#     search_fields=("email", "first_name")



admin.register(models.Ingredient, IngredientAdmin)
admin.register(models.User, UserAdmin)
admin.register(models.Recipe, RecipeAdmin)


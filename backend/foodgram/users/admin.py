from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
import models


User = get_user_model()

admin.site.register(User, UserAdmin)
admin.site.register(models.Cart)
admin.site.register(models.Favorite)
admin.site.register(models.Follow)

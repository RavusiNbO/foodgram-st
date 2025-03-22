from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomUser(AbstractUser):
    favorites = models.ForeignKey('api.Recipe', verbose_name='Избранное', on_delete=models.CASCADE, blank=True, null=True)
    follow = models.ManyToManyField('users.CustomUser', verbose_name='Подписка', blank=True)
    avatar = models.ImageField("Аватар", upload_to="avatar_images", blank=True, null=True)
    REQUIRED_FIELDS=["first_name", "last_name", "email"]
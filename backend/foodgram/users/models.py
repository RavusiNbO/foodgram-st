from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomUser(AbstractUser):
    favorites = models.ManyToManyField('api.Recipe', verbose_name='Избранное', blank=True, through='Favorite')
    following = models.ManyToManyField('users.CustomUser', verbose_name='Подписка', blank=True, through='Follow')
    avatar = models.ImageField("Аватар", upload_to="avatar_images", blank=True, null=True)
    email = models.EmailField(unique=True)
    REQUIRED_FIELDS=["first_name", "last_name", 'username']
    USERNAME_FIELD='email'

class Follow(models.Model):
    follower = models.ForeignKey('CustomUser', on_delete=models.CASCADE, verbose_name="Подписчик", related_name="follow_follower")
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, verbose_name="Автор", related_name="follow_user")

class Favorite(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, verbose_name="Юзер", related_name="favorite_user")
    recipe = models.ForeignKey('api.Recipe', on_delete=models.CASCADE, verbose_name='Рецепт', blank=True, related_name="favorite_recipe")
    

class PurchaseList(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, verbose_name="Юзер", related_name="purchase_user")
    recipe = models.ForeignKey('api.Recipe', on_delete=models.CASCADE, verbose_name='Рецепт', blank=True, related_name="purchase_recipe")
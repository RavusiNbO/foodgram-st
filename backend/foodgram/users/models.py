from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    favorites = models.ManyToManyField(
        'api.Recipe',
        verbose_name='Избранное',
        blank=True,
        through='Favorite',
    )
    following = models.ManyToManyField(
        'users.CustomUser',
        verbose_name='Подписки',
        blank=True,
        through='Follow',
    )
    avatar = models.ImageField(
        "Аватар",
        upload_to='avatar_images',
        blank=True,
        null=True
    )
    email = models.EmailField(
        unique=True,
        verbose_name="e-mail"
    )
    REQUIRED_FIELDS = ["first_name", "last_name", 'username']
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f'{self.username}'


class Follow(models.Model):
    follower = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        verbose_name="Подписчик",
        related_name="follow_follower"
    )
    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        verbose_name="Автор",
        related_name="follow_user"
    )

    class Meta:
        unique_together = ['user', 'follower']
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return f'{self.follower.username} - {self.user.username}'


class Favorite(models.Model):
    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        verbose_name="Юзер",
        related_name="favorite_user"
    )
    recipe = models.ForeignKey(
        'api.Recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        blank=True,
        related_name="favorite_recipe"
    )

    class Meta:
        unique_together = ['user', 'recipe']
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'


class Cart(models.Model):
    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        verbose_name="Юзер",
        related_name="cart_user"
    )
    recipe = models.ForeignKey(
        'api.Recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name="cart_recipe"
    )

    class Meta:
        unique_together = ['user', 'recipe']
        verbose_name = "Корзина покупок"
        verbose_name_plural = "Корзины покупок"

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'

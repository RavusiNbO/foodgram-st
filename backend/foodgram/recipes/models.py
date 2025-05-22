from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator


class FoodgramUser(AbstractUser):
    avatar = models.ImageField(
        "Аватар",
        upload_to='avatar_images',
        blank=True,
        null=True
    )
    email = models.EmailField(
        unique=True,
        verbose_name="e-mail",
        max_length=254
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=(RegexValidator(
            regex=r'^[\w.@+-]+\Z',
            message='Имя пользователя содержит недопустимые символы'
        ),
        )
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    REQUIRED_FIELDS = ["first_name", "last_name", 'username']
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['-id']

    def __str__(self):
        return self.username
    

User = FoodgramUser


class Ingredient(models.Model):
    name = models.CharField("Название", max_length=100, null=False)
    measurement_unit = models.CharField(
        "Единица измерения",
        max_length=15,
        null=False
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.measurement_unit}"


class Recipe(models.Model):
    name = models.CharField(
        "Название",
        max_length=256,
    )
    image = models.ImageField("Картинка", null=False, blank=False)
    text = models.TextField("Описание", null=False, blank=False)
    cooking_time = models.IntegerField(
        "Время приготовления",
        validators=[MinValueValidator(0),]
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name="Ингредиенты",
        blank=False,
        through="ProductInRecipe"
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="recipes",
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["-id"]

    def __str__(self):
        return f"{self.name} - {self.author.username}"


class ProductInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиент",
        related_name="products",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="products"
    )
    amount = models.IntegerField(
        "Количество",
        validators=[MinValueValidator(0),]
    )

    def __str__(self):
        return f'{self.ingredient.name} - {self.recipe.name} - {self.amount}'

    class Meta:
        verbose_name = "Продукт в рецепте"
        verbose_name_plural = "Продукты в рецепте"


class Follow(models.Model):
    follower = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        verbose_name="Подписчик",
        related_name="follows_follower"
    )
    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        verbose_name="Автор",
        related_name="follows_user"
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'follower'],
                name='unique_user_follower'
            )
        ]

    def __str__(self):
        return f'{self.follower.username} - {self.user.username}'


class FavCartBase(models.Model):
    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        verbose_name="Юзер",
        related_name="%(class)s_user"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name="%(class)s_recipe"
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe'
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'


class Favorite(FavCartBase):

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"


class Cart(FavCartBase):

    class Meta:
        verbose_name = "Корзина покупок"
        verbose_name_plural = "Корзины покупок"

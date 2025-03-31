from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

class Ingredient(models.Model):
    name = models.CharField("Название", max_length=30, null=False)
    measurement_unit = models.CharField("Единица измерения", max_length=15, null=False)

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'

class Recipe(models.Model):
    name = models.CharField("Название", max_length=30, null=False, blank=False)
    image = models.ImageField("Картинка", null=False, blank=False)
    text = models.TextField("Описание", null=False, blank=False)
    cooking_time = models.IntegerField("Время приготовления", null=False, blank=False)
    ingredients = models.ManyToManyField(Ingredient, verbose_name="Ингредиенты", blank=False, through="Amount")
    author = models.ForeignKey(User, verbose_name="Автор", null=False, on_delete=models.CASCADE, blank=False)

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return f'{self.name}, {self.author.username}'
    
class Amount(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, verbose_name="Ингредиент", related_name='amount')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name="Рецепт")
    amount = models.IntegerField('Вес', null=False, blank=False)
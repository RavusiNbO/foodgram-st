from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

ingredients = [
    ("Соль", "Соль"),
    ("Свёкла", "Свёкла"),
    ("Сельдерей", "Сельдерей"),
    ("Курятина", "Курятина"),
    ("Сливки", "Сливки"),
    ("Молоко", "Молоко"),
    ("Вода", "Вода"),
    ("Перец", "Перец"),
    ("Кетчуп", "Кетчуп"),
    ("Майонез", "Майонез"),
    ("Колбаса", "Колбаса"),
    ("Сыр", "Сыр"),
    ("Фарш", "Фарш"),
    ("Тесто", "Тесто"),
    ("Масло", "Масло"),
    
]

class Ingredient(models.Model):
    name = models.CharField("Название", max_length=30, choices=ingredients)
    measure = models.CharField("Единица измерения", max_length=15)

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return (self.name, self.measure)

class Recipe(models.Model):
    name = models.CharField("Название", max_length=30, null=False, blank=False)
    image = models.ImageField("Картинка", null=False, blank=False)
    text = models.TextField("Описание", null=False, blank=False)
    time = models.IntegerField("Время приготовления", null=False, blank=False)
    ingredients = models.ManyToManyField(Ingredient, verbose_name="Ингредиенты", blank=False)
    author = models.ForeignKey(User, verbose_name="Автор", null=False, on_delete=models.CASCADE, blank=False)

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return (self.name, self.author.username)
    
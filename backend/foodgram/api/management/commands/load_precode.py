import json
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт данных из прекода'

    def handle(self, *args, **options):
        with open("ingredients.json") as f:
            file = json.load(f)
            for i in file:
                Ingredient.objects.create(**i)
            self.stdout.write(self.style.SUCCESS('Импорт завершен'))
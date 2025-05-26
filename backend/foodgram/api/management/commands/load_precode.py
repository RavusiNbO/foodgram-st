import json
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт данных из прекода'

    def handle(self, *args, **options):
        try:
            with open("ingredients.json") as f:
                Ingredient.objects.bulk_create(
                    [Ingredient(
                        **i
                    ) for i in json.load(f)],
                    ignore_conflicts=True
                )
                self.stdout.write(self.style.SUCCESS(
                    f'Импорт завершен. Число новых \
                    записей - {Ingredient.objects.count()}'))
        except Exception as e:
            print("Произошла ошибка при загрузке данных",
                  f"из файла ingredients.json: {e}")

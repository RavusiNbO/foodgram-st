import json
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт данных из прекода'

    def handle(self, *args, **options):
        try:
            with open("ingredients.json") as f:
                data = json.load(f)
                Ingredient.objects.bulk_create(
                    Ingredient(
                        **i
                    ) for i in data
                )
                self.stdout.write(self.style.SUCCESS(
                    f'Импорт завершен. Число новых записей - {len(data)}'))
        except FileNotFoundError:
            print("Файл не найден. Пожалуйста, убедитесь,", 
                  "что ingredients.json существует.")
        except json.JSONDecodeError:
            print("Ошибка декодирования JSON. Проверьте,",
                  "что файл содержит корректные данные.")
        except Exception as e:
            print(f"Произошла ошибка: {e}")

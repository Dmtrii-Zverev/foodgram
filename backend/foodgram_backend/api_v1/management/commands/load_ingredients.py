import csv
import os

from django.core.management.base import BaseCommand, CommandError

from apps.recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загружает список ингредиентов из указанного CSV файла'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file', type=str, help='Путь к CSV файлу с ингредиентами'
        )

    def handle(self, *args, **options):
        file_path = options['csv_file']

        if not os.path.exists(file_path):
            raise CommandError(f'Файл "{file_path}" не найден')

        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            count = 0

            for row in reader:

                ingredient_name = row[0]
                unit = row[1]

                if ingredient_name and unit:
                    obj, created = Ingredient.objects.get_or_create(
                        name=ingredient_name,
                        defaults={'measurement_unit': unit}
                    )
                    if created:
                        count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Добавлен ингредиент: "{ingredient_name}"'
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Ингредиент "{ingredient_name}" уже есть.'
                            )
                        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Загрузка завершена. Добавлено новых ингредиентов: {count}'
            )
        )

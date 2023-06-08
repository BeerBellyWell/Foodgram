import csv
import os
import psycopg2


from django.core.management import BaseCommand

from recipes.models import Ingredient

class Command(BaseCommand):
    help = 'Заполнить БД данными из csv файла'

    def handle(self, *args, **kwargs):
        connect = psycopg2.connect(
            f"host={os.getenv('DB_HOST', default='db')}"
            f"port={os.getenv('DB_PORT', default='5432')}"
            f"dbname={os.getenv('DB_NAME', default='postgres')}"
            f"user={os.getenv('POSTGRES_USER', default='postgres')}"
            f"password={os.getenv('POSTGRES_PASSWORD', default='Chao14785691998')}"
        )

        cursor = connect.cursor()

        with open(
            'foodgram/data/ingredients.scv',
            'r', encoding='UTF-8') as file:
            reader = csv.reader(file)
            for row in reader:
                _, created = Ingredient.objects.create(
                    name=row[0],
                    measurement_unit=row[1],
                )

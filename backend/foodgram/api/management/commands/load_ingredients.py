import csv
import os
import psycopg2

from dotenv import load_dotenv
from django.core.management import BaseCommand


load_dotenv()


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

        with open('api/management/commands/data/ingredients.csv',
                  'r', encoding='UTF-8') as file:
            contents = csv.reader(file)
            col_names, number_questions = self.get_col_names(cursor,
                                                             'app_ingredient')
            insert_records = (f'INSERT INTO app_ingredient ({col_names})'
                              f'VALUES({number_questions})')
            cursor.executemany(insert_records, contents)

        connect.commit()
        connect.close()

    def get_col_names(self, cursor, tablename):
        cursor.execute(f"SELECT * FROM {tablename}")
        col_names = ', '.join([x[0] for x in cursor.description
                               if x[0] != 'id'])
        number_questions = ', '.join(['%s' for x in
                                      range(len(cursor.description) - 1)])
        return col_names, number_questions

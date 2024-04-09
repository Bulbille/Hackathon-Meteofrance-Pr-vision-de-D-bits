import csv
from django.core.management.base import BaseCommand
from projet.models.watercourses import Watercourse
import json
import os
from django.conf import settings

class Command(BaseCommand):
    help = "Charge les données depuis un fichier CSV"


    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Deletion of all existing data in the database"))
        Watercourse.objects.all().delete()

        csv_file_path = os.path.join(settings.BASE_DIR, 'projet' ,'data', 'watercourse_data.csv')
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            self.stdout.write(self.style.SUCCESS('Importing watercourse metadata '))

            for row in reader:
                first_point = eval(row['first_point']) if row['first_point'] else None
                last_point = eval(row['last_point']) if row['last_point'] else None
                is_affluent = True if row['is_affluent'] == '1' else False
                river_join = row['river_join'] if row['river_join'] is not None else None

                Watercourse.objects.create(
                    name=row['name'],
                    watercourse_code=row['watercourse_code'],
                    length=float(row['length']),
                    first_point=first_point,
                    last_point=last_point,
                    is_affluent=is_affluent,
                    classe=row['classe'],
                    river_join=river_join
                )
            self.stdout.write(self.style.SUCCESS('Import complete.'))
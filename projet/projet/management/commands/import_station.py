import csv
from django.core.management.base import BaseCommand
from projet.models.stations import Station
from django.utils.dateparse import parse_datetime
import json
import os
from django.conf import settings

class Command(BaseCommand):
    help = "Charge les données depuis un fichier CSV"
   

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Suppression de toutes les données existantes dans la base de données..."))
        Station.objects.all().delete()

        csv_file_path = os.path.join(settings.BASE_DIR, 'projet' ,'data', 'stations.csv')
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            self.stdout.write(self.style.SUCCESS('Importation des nouvelles stations...'))

            for row in reader:
                date_maj_station = parse_datetime(row['date_maj_station']) if row['date_maj_station'] else None
                date_ouverture_station = parse_datetime(row['date_ouverture_station']) if row['date_ouverture_station'] else None
                date_fermeture_station = parse_datetime(row['date_fermeture_station']) if row['date_fermeture_station'] else None
                coordonnee_x_station = float(row['coordonnee_x_station']) if row['coordonnee_x_station'] else None
                coordonnee_y_station = float(row['coordonnee_y_station']) if row['coordonnee_y_station'] else None
                altitude_ref_alti_station = float(row['altitude_ref_alti_station']) if row['altitude_ref_alti_station'] else None

                # if row['influence_locale_station']:
                #     influence_locale_station = float(row['influence_locale_station'])
                # else:
                #     continue 
                # if row['altitude_ref_alti_station']:
                #     altitude_ref_alti_station = float(row['altitude_ref_alti_station'])
                # else:
                #     continue 
                # influence_locale_station = float(row['influence_locale_station']) if row['influence_locale_station'] else None
                # altitude_ref_alti_station = float(row['altitude_ref_alti_station']) if row['altitude_ref_alti_station'] else None
                qualification_donnees_station = float(row['qualification_donnees_station']) if row['qualification_donnees_station'] else None
                # geometry = json.loads(row['geometry']) if row['geometry'] else None

                Station.objects.create(
                    code_site=row['code_site'],
                    libelle_site=row['libelle_site'],
                    code_station=row['code_station'],
                    libelle_station=row['libelle_station'],
                    type_station=row['type_station'],
                    coordonnee_x_station=coordonnee_x_station,
                    coordonnee_y_station=coordonnee_y_station,
                    code_projection=row['code_projection'],
                    longitude_station=float(row['longitude_station']),
                    latitude_station=float(row['latitude_station']),
                    # influence_locale_station=float(row['influence_locale_station']),
                    commentaire_station=row['commentaire_station'],
                    altitude_ref_alti_station= altitude_ref_alti_station,
                    code_systeme_alti_site=row.get('code_systeme_alti_site'),
                    code_commune_station=row['code_commune_station'],
                    libelle_commune=row['libelle_commune'],
                    code_departement=row['code_departement'],
                    code_region=row['code_region'],
                    libelle_region=row['libelle_region'],
                    code_cours_eau=row.get('code_cours_eau'),
                    libelle_cours_eau=row.get('libelle_cours_eau'),
                    uri_cours_eau=row.get('uri_cours_eau'),
                    descriptif_station=row.get('descriptif_station'),
                    date_maj_station=date_maj_station,
                    date_ouverture_station=date_ouverture_station,
                    date_fermeture_station=date_fermeture_station,
                    commentaire_influence_locale_station=row.get('commentaire_influence_locale_station'),
                    code_regime_station=row['code_regime_station'],
                    qualification_donnees_station=qualification_donnees_station,
                    code_finalite_station=row.get('code_finalite_station'),
                    type_contexte_loi_stat_station=row.get('type_contexte_loi_stat_station'),
                    type_loi_station=row.get('type_loi_station'),
                    code_sandre_reseau_station=row.get('code_sandre_reseau_station'),
                    date_debut_ref_alti_station=parse_datetime(row.get('date_debut_ref_alti_station')),
                    date_activation_ref_alti_station=parse_datetime(row.get('date_activation_ref_alti_station')),
                    date_maj_ref_alti_station=parse_datetime(row.get('date_maj_ref_alti_station')),
                    libelle_departement=row['libelle_departement'],
                    en_service=row['en_service'] == 'True',
                    # geometry=geometry
                )
            self.stdout.write(self.style.SUCCESS('Importation terminée.'))

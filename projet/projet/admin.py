from django.contrib import admin
from projet.models.stations import Station  # Assurez-vous que le chemin d'importation est correct

# Enregistrement du modèle Station pour qu'il apparaisse dans l'interface d'administration
admin.site.register(Station)

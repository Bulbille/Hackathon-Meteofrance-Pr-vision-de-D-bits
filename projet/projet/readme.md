# Station Data Explorer
Station Data Explorer est une application web Django conçue pour interagir avec des données météorologiques et hydrométriques. Elle permet aux utilisateurs de télécharger des données météo, de visualiser des informations sur les débits d'eau et d'effectuer des requêtes utilisateur simples.

### Prérequis
- Python 3.8 ou supérieur
- Django 3.1 ou supérieur
- Bibliothèque Folium pour les cartes
- Un environnement virtuel Python (recommandé)

### Installation
**Cloner le dépôt Git** :
   ```bash
   git clone https://gitlab.engine.capgemini.com/software-engineering/france/plant/hydrologie.git
   ```
   -Ajouter les extensions suivantes à  l'environnement Visual Studio Code :

      Jupyter
      SQLite Viewer

### Effectuer les migrations de la base de données 
```bash
cd projet
python manage.py makemigrations
python manage.py migrate
python manage.py import_station  ( insertion des données du fichier "Stations.csv" en base de données)
python manage.py import_watercourse ( insertion des données du fichier "watercourse_data.csv" en base de données)

```
### Installation des Dépendances
- Pour configurer correctement l'environnement de travail, suivre ces étapes :

pip install -r requirements.txt
pip install channels
pip install django_select2
pip install folium
pip install requests
pip install matplotlib
pip install plotly
pip install shapely
pip install pyproj
pip install nest_asyncio
pip install geopandas
pip install geopy
pip install aiofiles



### Remarques:
- Il faut mettre à jour le chemin dans le fichier de configuration situé à : C:\Users\sagrib\hydrologie\projet\projet\config, en remplaçant le chemin par celui de votre projet local.
- Pour la section météo, veuillez modifier le chemin dans les classes en remplaçant l'ancien chemin par celui de votre projet local. Faites de même pour le chemin dans le fichier 'config_file.ini', situé à C:\Users\sagrib\hydrologie\projet\projet\config_file.ini."


### Créer un superutilisateur pour accéder à l'interface d'administration :
```bash
python manage.py createsuperuser
```
### Lancement
```bash
```

Puis accédez à http://localhost:8000/ dans votre navigateur.

## Fonctionnalités

Téléchargement de Données Météorologiques : Permet aux utilisateurs de télécharger des données météorologiques pour une localisation et une période spécifiques en format csv ou json.
http://localhost:8000/weather 

Visualisation des Données Hydrométriques : Affiche des informations sur le débit d'eau de différentes stations.
http://localhost:8000/data_hydro

Requêtes Utilisateurs : Interface simple pour effectuer des requêtes sur les données des stations. Carte Interactive : Utilise Folium pour afficher les emplacements des stations sur une carte interactive. (En cours)
http://localhost:8000/map

## Wiki: Le processus de génération du fichier "watercourse_data.csv"
https://gitlab.engine.capgemini.com/software-engineering/france/plant/hydrologie/-/wikis/Cr%C3%A9ation-du-fichier-%22watercourse_data.csv%22
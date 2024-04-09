#### Utilisation de l'API Hub'eau ####
# Wiki: The file generation process"watercourse_data.csv"
# https://gitlab.engine.capgemini.com/software-engineering/france/plant/hydrologie/-/wikis/Cr%C3%A9ation-du-fichier-%22watercourse_data.csv%22
import sys
import os
# sys.path.append(r"C:\Users\sagrib\hydrologie\projet")
script_path = os.path.abspath(__file__)
project_dir = os.path.dirname(os.path.dirname(os.path.dirname(script_path)))
sys.path.append(project_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projet.settings")  
import django
django.setup()
from django.db import models
import asyncio
from typing import List, Tuple
import csv
import json
import folium
import branca 
import requests
import pandas as pd
import warnings
from projet.models.stations import Station as db_Station
from projet.models.watercourses import Watercourse as db_Watercourse
from asgiref.sync import sync_to_async
import nest_asyncio
from .station import StationManager
from .multipleStation import MultipleStations
from .config_ssl import NoSSLVerification, urls
import numpy as np
from pyproj import Transformer
transformer = Transformer.from_crs('epsg:4326','epsg:2154')
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)
pd.set_option('display.max_columns', None)
nest_asyncio.apply()
from django.forms.models import model_to_dict

#no ssl certificate verification
session = requests.Session()
for url in urls:
    session.mount(url, NoSSLVerification())


#  The Watercourse class is designed to gather metadata on the different watercourses in France
# from different sources, including the database's 'Station' table or Eau France APIs, such as the one available at
# 'http://id.eaufrance.fr/CEA/code_cours_d’eau'.
class Watercourse():
    def __init__(self, code: str = None, name: str = None, classe: str = None) -> None:
        if code is None and name is None:
            raise ValueError("the code or name of the watercourse is required.")
        if name is not None:
            self.name = name 
        else:    
            asyncio.run(self.get_watercourse_name())

        if code is not None:
            self.code_cours_eau = code
        else:    
            asyncio.run(self.get_watercourse_code()) 


        self.classe = classe
        self.coord = self.get_watercourse_coord()


        
    @sync_to_async
    def get_watercourse_code(self):
        try:
            db_station = db_Station.objects.filter(libelle_cours_eau=self.name).first()
            if db_station:
                self.code_cours_eau = db_station.code_cours_eau
                return self.code_cours_eau 
            else:
                # If nothing is found in the database, search the API
                try:
                    url = f"https://services.sandre.eaufrance.fr/geo/sandre?SERVICE=WFS&REQUEST=getFeature&VERSION=2.0.0&TYPENAME=CoursEau_Carthage2017&OUTPUTFORMAT=application/json%3B%20subtype%3Dgeojson&FILTER=%3CFilter%3E%3CPropertyIsEqualTo%3E%3CPropertyName%3ENomEntiteHydrographique%3C/PropertyName%3E%3CLiteral%3E{self.name}%3C/Literal%3E%3C/PropertyIsEqualTo%3E%3C/Filter%3E"
                    response = session.get(url)
                    data = response.json()
                    self.code_cours_eau = data['features'][0]['properties']['CdEntiteHydrographique']
                    return self.code_cours_eau  
                except Exception as e:
                    print(f"An error occurred when searching for the watercourse code  : {e}")
                    return None  # Returns None on error
        except db_Station.DoesNotExist:
            print("No watercourse code corresponding to this name in the database")
            return None  


    @sync_to_async
    def get_watercourse_name(self):
        try:  
            db_station = db_Station.objects.filter(code_cours_eau=self.code_cours_eau).first()
            if db_station:
                self.name = db_station.libelle_cours_eau
            else:
                try :
                    code_entite_hydrographique = self.code_cours_eau
                    url = f"https://services.sandre.eaufrance.fr/geo/sandre?SERVICE=WFS&REQUEST=getFeature&VERSION=2.0.0&TYPENAME=CoursEau_Carthage2017&OUTPUTFORMAT=application/json%3B%20subtype%3Dgeojson&FILTER=%3CFilter%3E%3CPropertyIsEqualTo%3E%3CPropertyName%3ECdEntiteHydrographique%3C/PropertyName%3E%3CLiteral%3E{code_entite_hydrographique}%3C/Literal%3E%3C/PropertyIsEqualTo%3E%3C/Filter%3E"
                    response = session.get(url)
                    data = response.json()
                    self.name = data['features'][0]['properties']['NomEntiteHydrographique']
                except:
                    raise ValueError(f"Watercourse name not found for code {self.code_cours_eau}.")
        except db_Station.DoesNotExist:
            raise ValueError("No watercourse corresponding to the code in the database")
        

    def get_watercourse_classe(self):
        code_entite_hydrographique = self.code_cours_eau

        url = f"https://api.sandre.eaufrance.fr/coursdeau/v1/amont/{code_entite_hydrographique}"
        response = session.get(url)
        
        if response.status_code != 200:
            print(f"Erreur {response.status_code}: {response.text}")
            return None

        data = response.json().get('features', [])
        for feature in data:
            properties = feature.get('properties', {})
            classe = properties.get('Classe')
        if classe  is not None:
            return self.classe 

        return None

        
    def get_watercourse_length(self):

        warnings.simplefilter(action='ignore', category=FutureWarning)

        coordinates = self.coord
        coordinates_proj = np.apply_along_axis(lambda x : transformer.transform(*x[::-1]),1,np.array(coordinates))

        total_length_km = 0

        total_length_km = np.sum(((coordinates_proj[1:][:,0]-coordinates_proj[:-1][:,0])**2 +
                        (coordinates_proj[1:][:,1]-coordinates_proj[:-1][:,1])**2)**0.5)/1000
        
        return total_length_km
    
    
    def get_all_affluents(self, code_entite_hydrographique: str = None, classe_max: int = 4):   
        if code_entite_hydrographique is None:
            code_entite_hydrographique = self.code_cours_eau

        affluents = []

        url = f"https://api.sandre.eaufrance.fr/coursdeau/v1/amont/{code_entite_hydrographique}"
        response = session.get(url)

        if response.status_code != 200:
            print(f"Erreur {response.status_code}: {response.text}")
            return []
        data = response.json().get('features', [])

        for feature in data:
            properties = feature.get('properties', {})
            classe = properties.get('Classe')
            CdEntiteHydrographique = str(properties.get('CdEntiteHydrographique'))
            NomEntiteHydrographique = str(properties.get('NomEntiteHydrographique'))

            if NomEntiteHydrographique.lower() != "none" and CdEntiteHydrographique.lower() != "none":
                if int(classe) <= classe_max:
                    if CdEntiteHydrographique not in set(self.code_cours_eau) and "canal" not in NomEntiteHydrographique.lower():
                        affluents.append((CdEntiteHydrographique, NomEntiteHydrographique, classe))

        return affluents

    
    def get_direct_affluents(self, classe_max: int = 4):
        def zoneshydro(code_entite_hydrographique, keyword):
            url = f"https://api.sandre.eaufrance.fr/coursdeau/v1/zoneshydro/{code_entite_hydrographique}"
            response = session.get(url)
            response.raise_for_status() 
            data = json.loads(response.text)
            result = any(keyword.lower() in value.lower() for value in data.values())
            return result

        all_aff = self.get_all_affluents(None, classe_max)
        direct_affluents = []
        river_coordinates_rounded = set(tuple(round(coord, 5) for coord in val) for val in self.coord)

        for aff in all_aff:
            if zoneshydro(aff[0], self.name):
                affluent = Watercourse(code=aff[0], name=aff[1], classe=aff[2])
                pt_confluence = affluent.get_last_point()
                pt_tuple = (round(pt_confluence[0], 5), round(pt_confluence[1], 5))
                if pt_tuple in river_coordinates_rounded:
                    direct_affluents.append((affluent.code_cours_eau, affluent.name))

        if direct_affluents:
            return direct_affluents
        else:
            return "The river has no direct tributaries."


    def get_watercourse_coord(self):
        
        code_entite_hydrographique = self.code_cours_eau
        url = f"https://services.sandre.eaufrance.fr/geo/sandre?SERVICE=WFS&REQUEST=getFeature&VERSION=2.0.0&TYPENAME=CoursEau_Carthage2017&OUTPUTFORMAT=application/json%3B%20subtype%3Dgeojson&FILTER=%3CFilter%3E%3CPropertyIsEqualTo%3E%3CPropertyName%3ECdEntiteHydrographique%3C/PropertyName%3E%3CLiteral%3E{code_entite_hydrographique}%3C/Literal%3E%3C/PropertyIsEqualTo%3E%3C/Filter%3E"

        response = session.get(url)
        data = response.json()
        coordinates = data['features'][0]['geometry']['coordinates']
        
        if len(coordinates) > 0 and isinstance(coordinates[0][0], (float, int)):
            self.is_canal = False
            return coordinates
        elif len(coordinates) > 0 and isinstance(coordinates[0][0][0], (float, int)):
            self.is_canal = True
            return [point for sublist in coordinates for point in sublist]
        
        return coordinates

    def get_first_point(self, long_lat : bool = True) : 
        if long_lat :
            return self.coord[0]
        return [self.coord[0][1],self.coord[0][0]]
        
    def get_last_point(self, long_lat : bool = True):
        if long_lat :
            return self.coord[-1]
        return [self.coord[-1][1],self.coord[-1][0]]
    
    def get_first_and_last_point(self, long_lat: bool = True):
        first_point = self.coord[0]
        last_point = self.coord[-1]
        if long_lat:
            first_point = [first_point[1], first_point[0]]
            last_point = [last_point[1], last_point[0]]
        return first_point, last_point
    
    # Version 1: List of river stations using the multipleStations class methods
    def stations_watercourse (self, active: bool = True) -> MultipleStations:
        stations = MultipleStations() 
        stations._get_all_french_stations(active,True)
        fleuve_stations = MultipleStations()
        for s in stations.metadata.values() :
            if (s.code_cours_eau == self.code_cours_eau):
                    fleuve_stations.add_stations([s.code_station])
        return fleuve_stations
    
    # Version 2: List of river stations from the database
    @sync_to_async
    def get_stations_watercourse(self):
        try:  
            stations = db_Station.objects.filter(libelle_cours_eau=self.name).values_list('code_station', flat=True)
            if stations:
                return stations 
        except db_Station.DoesNotExist:
            print("No stations code corresponding to the watercourse {libelle_cours_eau} in the database")
            return None  
     
    
    def get_stations_amont_aval(self, nom_affluent: str):
        # TODO à revoir également
        affluent = Watercourse(None, nom_affluent)
        last_point_affluent = affluent.get_last_point()

        stations = self.stations_watercourse()
        dict_coord_stations = stations._dict_station_coord()
        list_stations = list(dict_coord_stations.keys())

        # for i,_ in dict_coord_stations.keys() : 
        for i in range(len(list_stations) - 1):
            amont, aval = list_stations[i], list_stations[i + 1]
            coord_station_amont, coord_station_aval = dict_coord_stations[amont], dict_coord_stations[aval]
            
            try:
                result = self._get_coord_between_values(coord_station_amont, coord_station_aval)
            except ValueError:
                result = None

            if result is not None:
                rounded_result = [[round(val, 5) if isinstance(val, float) else val for val in sublist] for sublist in result]
                if [round(last_point_affluent[0], 5), round(last_point_affluent[1], 5)] in rounded_result:
                    return [amont, aval]
        return None
     
    def create_watercourse_map (self, map = None, with_affluents : bool = False, classe_max : int = 4, line_weight : int = 4, color = "red") :
        coordonnees_cours_deau = self.coord
        
        if map is None : 
            mean_latitude = np.mean([s[1] for s in coordonnees_cours_deau])
            mean_longitude = np.mean([s[0] for s in coordonnees_cours_deau])
            map = folium.Map(location=[mean_latitude, mean_longitude], zoom_start=6)

        for coord, next_station in zip(coordonnees_cours_deau, coordonnees_cours_deau[1:]):
            line_points = [(coord[1], coord[0]), (next_station[1], next_station[0])]
            folium.PolyLine(locations=line_points, color=color, weight=line_weight, opacity=0.8).add_to(map)

        if with_affluents :   
            affluents = self.get_all_affluents(self.code_cours_eau,classe_max,True)
            for affluent in affluents :
                try:
                    aff = Watercourse(affluent,None)
                    aff.create_watercourse_map(map,False,2,"blue")
                except :
                    print("error in ", affluent)                 
        return map

    def create_debit_dataframe(self, station_ref : StationManager, year : int, classe_max : int = 2) -> pd.DataFrame:
        """
            Create debit dataframe between station reference and others stations in affluents
        """
        start_date = str(year)+'-01-01'
        end_date = str(year)+'-12-31'
        
        # check if station ref has already obs
        if (station_ref.start_date != start_date or station_ref.end_date != end_date):
            if not station_ref.get_obs(start_date, end_date):
                raise ValueError("Station without data")
        station_ref.obs_elab.columns = [station_ref]

        date_station_debit_list = [station_ref.obs_elab]
        
        # get all affluent for river
        all_affluents = self.get_all_affluents(classe_max=classe_max)

        for affluent in all_affluents:
            affluent_code = affluent[0]
            
            # récupère les stations de l'affluent
            affluent_waterCourse = Watercourse(code=affluent_code)
            affluent_stations = affluent_waterCourse.stations_watercourse()

            # récupère les debits journaliers
            stations_obs = affluent_stations.get_stations_obs(start_date, end_date)

            if stations_obs is not None and not isinstance(stations_obs, str):
                date_station_debit_list.append(stations_obs)

        # concat all df
        debit_df = pd.concat(date_station_debit_list, axis=1)
        return debit_df

    def create_correlation_series(self, debit_df:pd.DataFrame, time_shift : int = 0) -> pd.core.series.Series:
        """
            Create correlation series from debit dataframe (see create_debit_dataframe)
        """
        station_ref = debit_df.columns[0]
        # time shift
        correlation_series = debit_df.corrwith(debit_df[station_ref][time_shift:])
        return correlation_series

    def create_correlation_map(self, correlation_series : pd.core.series.Series, year : int, time_shift : int) -> folium.Map:
        """
            Create correlation map (see create_correlation_series method)
        """
        min_coeff = 0.3
        max_coeff = 0.9

        mean_latitude = np.array([stationManager.latitude_station for stationManager in correlation_series.index]).mean()
        mean_longitude = np.array([stationManager.longitude_station for stationManager in correlation_series.index]).mean()
        map = folium.Map(location=[mean_latitude,mean_longitude], zoom_start=8) #Centrer la carte

        # TITLE
        title_html = '''
                    <h3 align="center" style="font-size:16px"><b>Correlation river='{}', year={}, time shift={}</b></h3>
                    '''.format(self.name, year, time_shift)
        map.get_root().html.add_child(folium.Element(title_html))

        # color legend
        colormap = branca.colormap.LinearColormap(['#FF0000', 'yellow', '#00FF00'], vmin=min_coeff, vmax=max_coeff)
        colormap.add_to(map)

        # marker for station_ref
        station_ref = correlation_series.index[0]
        station_ref_marker = folium.Marker(
                location=[station_ref.latitude_station, station_ref.longitude_station],
                popup=station_ref.libelle_station+' alt='+str(station_ref.altitude_ref_alti_station),
                icon=folium.Icon(color="blue", icon='glyphicon-asterisk')
            )
        station_ref_marker.add_to(map)

        # add marker for all stations
        for station_manager in correlation_series.index :
            correlation = correlation_series[station_manager]

            color_code = colormap.rgb_hex_str(correlation)

            marker = folium.CircleMarker(
                location=[station_manager.latitude_station, station_manager.longitude_station],
                tooltip='<h4>'+station_manager.libelle_station+'</h4>'+
                    '<font size="+1">'
                    '<b>alt</b> '+str(station_manager.altitude_ref_alti_station)+'<br>'+
                    '<b>correlation</b> '+str(int(100*correlation)/100)+'<br>'+
                    '<b>value</b> '+str(correlation)+
                    '</font>',
                color=color_code,
                fill_color=color_code,
                fill_opacity=1
            )
            marker.add_to(map)

        return map

    def get_last_station(self, active :bool = True) -> StationManager :
        stations = self.stations_watercourse(active)
        return stations.sort_stations()[-1]
        
    def get_affluents_between_stations(self, coord_station_a, coord_station_b, direct_affluents_codes : list = None)  :
        affluents_codes = direct_affluents_codes or self.get_direct_affluents(classe=7,returns_codes=True)
        
        rounded_coord = [[round(lon, 5), round(lat, 5)] for lon, lat in self._get_coord_between_values(coord_station_a,coord_station_b)]

        affluents = {}
        print(rounded_coord)
        for aff in affluents_codes :
            affluent = Watercourse(aff)
            confluence = affluent.get_last_point()
            if [round(confluence[0], 5), round(confluence[1], 5)] in rounded_coord:
                affluents[affluent.code_cours_eau] = affluent.name
        
        return affluents

    def _get_coord_between_values (self, value_1, value_2):
        def distance(point1, point2):
            return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5

        lst = self.coord
        try:
            index_value_1 = min(range(len(lst)), key=lambda i: distance(value_1, lst[i]))
            index_value_2 = min(range(len(lst)), key=lambda i: distance(value_2, lst[i]))
            return lst[min(index_value_1, index_value_2): max(index_value_1, index_value_2) + 1]
        except ValueError:
            return None
        
    @classmethod
    async def get_fleuves(cls):
        fleuves = await sync_to_async(lambda: list(db_Watercourse.objects.values('name').distinct()))()
        fleuves = [commune['name'] for commune in fleuves]
        unique_fleuve_names = list(set(fleuves ))
        return  unique_fleuve_names    
    
    
# This class aims to create a CSV file gathering all the metadata of the watercourses in France.
#We use the methods from the Watercourse class. This class is a subclass of Watercourse; it inherits the necessary methods. 
#The generated file will then be used for data insertion into the database.  
class WatercourseDataExporter(Watercourse):

    def __init__(self, name: str):
        super().__init__(name=name)

    
    async def get_watercourse_data( self, name: str, is_affluent: bool = False, code: str = None, classe: float = None, river_join: str = None) -> Tuple[str, str, float, dict, dict, int, float, str]:
        watercourse = Watercourse(name=name)
        if not is_affluent:
            code = await watercourse.get_watercourse_code()
            classe =   watercourse.get_watercourse_classe()
        else:
            if code is not None and classe is not None:
                watercourse.code_cours_eau = code
                watercourse.classe = classe
            else:
                watercourse.code_cours_eau = await watercourse.get_watercourse_code()
                watercourse.classe = watercourse.get_watercourse_classe()
                pass  

                
        length =  watercourse.get_watercourse_length()
        first_point, last_point =  watercourse.get_first_and_last_point(long_lat=False)
        if is_affluent:
            river_join = river_join  #Use the name of the principal river as river_join for tributaries
        else:
            river_join = None
        
        return  watercourse.name,  watercourse.code_cours_eau, length, first_point, last_point, int(is_affluent), classe, river_join
    
    def write_watercourse_data_to_csv(data: List[Tuple[str, str, float, dict, dict, int, float, str]]):

        script_path = os.path.abspath(__file__)

        project_dir = os.path.dirname(os.path.dirname(script_path))
        #     Path to configuration file
        config_path = os.path.join(project_dir, 'config', 'config.json')
        with open(config_path) as f:
            config = json.load(f)
        output_directory = config['output_directory']
        file_name = config['file_name']

        file_path = os.path.abspath(os.path.join(output_directory, file_name))
        header = ["name", "watercourse_code", "length", "first_point", "last_point", "is_affluent", "classe", "river_join"]

        existing_codes = set()  # Store existing watercourse codes in csv for verification

        if os.path.exists(file_path):
            with open(file_path, mode='r', newline='') as file:
                reader = csv.reader(file)
                next(reader) 
                for row in reader:
                    existing_codes.add(row[1])  # Add code to existing code set

        # Add only data that does not exist in the file
        new_data = [row for row in data if row[1] not in existing_codes]

        if new_data:  # Check for new data to add
            with open(file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
                    writer.writerow(header)  # Write header if file is empty
                writer.writerows(new_data)
            print("Data successfully added to CSV file.")
        else:
            print("No data added to the CSV file because it already exists.")



class WatercourseDatabaseReader(Watercourse):
    def __init__(self, watercourse_code: str = None, name: str = None, classe: str = None):
        
        if name is not None:
            self.name = name
            print(f"self.name: {self.name}")
        else:    
            asyncio.run(self.get_watercourse_name())
            
        if watercourse_code is not None:
            self.watercourse_code = watercourse_code
            print(f"self.watercourse_code: {self.watercourse_code}")
        else:
            print ("appel de la méthode get_watercourse_code")    
            asyncio.run(self.get_watercourse_code())


        self.classe = classe
    
    
    
    # Redefined methods for retrieving data from the "watercourse" table
    @sync_to_async
    def get_watercourse_code(self):
        try:
            
            db_watercourse = db_Watercourse.objects.filter(name=self.name).first()
            if db_Watercourse:
                self.watercourse_code= db_watercourse.watercourse_code
                return  self.watercourse_code
            else:
                # If nothing is found in the database, search the API
                try:

                    url = f"https://services.sandre.eaufrance.fr/geo/sandre?SERVICE=WFS&REQUEST=getFeature&VERSION=2.0.0&TYPENAME=CoursEau_Carthage2017&OUTPUTFORMAT=application/json%3B%20subtype%3Dgeojson&FILTER=%3CFilter%3E%3CPropertyIsEqualTo%3E%3CPropertyName%3ENomEntiteHydrographique%3C/PropertyName%3E%3CLiteral%3E{self.name}%3C/Literal%3E%3C/PropertyIsEqualTo%3E%3C/Filter%3E"
                    response = session.get(url)
                    data = response.json()
                    self.watercourse_code = data['features'][0]['properties']['CdEntiteHydrographique']
                    return  self.watercourse_code  
                except Exception as e:
                    print(f"An error occurred when searching for the watercourse code : {e}")
                    return None  # Returns None on error
        except db_Watercourse.DoesNotExist:
            print("No watercourse code corresponding to this name in the database")
            return None  
        
    @sync_to_async
    def get_watercourse_name(self):
        try:  
            db_watercourse = db_Watercourse.objects.filter(watercourse_code  =self.watercourse_code  ).first()
            if  db_watercourse:
                self.name = db_watercourse.name
            else:
                try :
                    code_entite_hydrographique =  self.watercourse_code
                    url = f"https://services.sandre.eaufrance.fr/geo/sandre?SERVICE=WFS&REQUEST=getFeature&VERSION=2.0.0&TYPENAME=CoursEau_Carthage2017&OUTPUTFORMAT=application/json%3B%20subtype%3Dgeojson&FILTER=%3CFilter%3E%3CPropertyIsEqualTo%3E%3CPropertyName%3ECdEntiteHydrographique%3C/PropertyName%3E%3CLiteral%3E{code_entite_hydrographique}%3C/Literal%3E%3C/PropertyIsEqualTo%3E%3C/Filter%3E"
                    response = session.get(url)
                    data = response.json()
                    self.name = data['features'][0]['properties']['NomEntiteHydrographique']
                except:
                    raise ValueError(f"Watercourse name not found for code {self.watercourse_code}.")
        except db_Watercourse.DoesNotExist:
            raise ValueError("No watercourse corresponding to the code in the database")
    @sync_to_async    
    def get_watercourse_data(self, watercourse_code):
        try:
            watercourse_data = db_Watercourse.objects.get(watercourse_code=watercourse_code)
            if watercourse_data:
                # Convertir l'objet en dictionnaire
                data_dict = model_to_dict(watercourse_data)
                return data_dict
            else:
                return None
        except db_Watercourse.DoesNotExist:
            return None
    @sync_to_async    
    def get_watercourse_classe(self):
        try:  

            db_watercourse = db_Watercourse.objects.filter(watercourse_code=self.watercourse_code).first()
            if  db_watercourse:
                self.classe = db_watercourse.classe
                return self.classe
            else:
                try :
                    code_entite_hydrographique = self.watercourse_code
                    url = f"https://services.sandre.eaufrance.fr/geo/sandre?SERVICE=WFS&REQUEST=getFeature&VERSION=2.0.0&TYPENAME=CoursEau_Carthage2017&OUTPUTFORMAT=application/json%3B%20subtype%3Dgeojson&FILTER=%3CFilter%3E%3CPropertyIsEqualTo%3E%3CPropertyName%3ECdEntiteHydrographique%3C/PropertyName%3E%3CLiteral%3E{code_entite_hydrographique}%3C/Literal%3E%3C/PropertyIsEqualTo%3E%3C/Filter%3E"
                    response = session.get(url)
                    data = response.json()
                    self.classe = data['features'][0]['properties']['classe']
                    return self.classe
                except:
                    raise ValueError(f"Watercourse classe not found for code {self.watercourse_code}.")
        except db_Watercourse.DoesNotExist:
            raise ValueError("No watercourse corresponding to the code in the database")
    @sync_to_async  
    def get_watercourse_length(self):
        try:  
            db_watercourse = db_Watercourse.objects.filter(watercourse_code=self.watercourse_code).first()
            
            if db_watercourse:
                self.length = db_watercourse.length
                return self.length
        except db_Watercourse.DoesNotExist:
            raise ValueError("No watercourse corresponding to the code in the database")

    
    
    @sync_to_async  
    def get_first_and_last_point(self, long_lat: bool = True):
        try:  
            db_watercourse = db_Watercourse.objects.filter(watercourse_code=self.watercourse_code).first()
            if  db_watercourse:
                self.first_point= db_watercourse.first_point
                self.last_point= db_watercourse.last_point
                return self.first_point, self.last_point
        except db_Watercourse.DoesNotExist:
            raise ValueError("No watercourse corresponding to the code in the database")
        
    @sync_to_async
    def get_affluents(self):
        try:
            affluents = db_Watercourse.objects.filter(river_join=self.name).values('name', 'watercourse_code')
            return list(affluents)
        except db_Watercourse.DoesNotExist:
            raise ValueError("No watercourse corresponding to the name in the database")





# async def main():
#     # watercourse_names = ["Le Rhin", "La Garonne", "La Seine", "Le Rhône", "La Dordogne", "la Loire"]
#     watercourse_data = []

    
#     # Cas 1 : List of principal rivers
#     for name in watercourse_names:
#         exporter = WatercourseDataExporter(name=name)  
#         data = await exporter.get_watercourse_data(name)  
#         watercourse_data.append(data)

#     #  Cas 2 : For each river, find the tributaries
#     for name in watercourse_names:
#         affluents = exporter.get_all_affluents()

#         for code, afflu_name, classe in affluents:
#             # If the affluent name consists of numbers only, it's probably a numerical name rather than a valid
#             # river name, so we ignore it.
#             if afflu_name.isdigit():
#                 continue
            
#             data = await exporter.get_watercourse_data(afflu_name, is_affluent=True, code=code, classe=classe, river_join=name)
#             watercourse_data.append(data)


#     WatercourseDataExporter.write_watercourse_data_to_csv(watercourse_data)

# asyncio.run(main())
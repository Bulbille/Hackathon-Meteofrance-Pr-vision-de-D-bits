
import pandas as pd
import folium
import requests
import warnings
import re
import numpy as np 
import geopy.distance
from projet.models.stations import Station as db_Station
import nest_asyncio
from asgiref.sync import sync_to_async
from geopy.distance import great_circle
from .station import StationManager
import asyncio
from channels.db import database_sync_to_async
from projet.models.stations import Station

warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)
pd.set_option('display.max_columns', None)
nest_asyncio.apply()
# Various links for retrieving data
#SITE      = "https://hubeau.eaufrance.fr/api/v1/hydrometrie/referentiel/sites?"
#OBS_TR    = "https://hubeau.eaufrance.fr/api/v1/hydrometrie/observations_tr?"
OBS_JOUR  = 'https://hubeau.eaufrance.fr/api/v1/hydrometrie/obs_elab?'
STATIONS  = "https://hubeau.eaufrance.fr/api/v1/hydrometrie/referentiel/stations?"


class MultipleStations() : 
    def __init__(self,stations : list = []) -> None:
        assert stations is not None, 'The station list is empty'
        self.stations       = []
        self.french_stations   = []
        self.metadata       = {}
        self.observations   = None

        for station in stations : 
            try : 
                self.metadata[station] = StationManager(station)
                self.stations.append(station)
            except :
                print('Incorrect station code :',station)


    def add_stations(self,stations : list, informations : dict = None) -> None:
        """
        Adds stations list to self.stations
        Parameters :
            stations : list of station codes (strings) and/or instances of StationManager
        """                    
        for station in stations : 
            if isinstance(station, StationManager):
                code_station = station.code_station
                station_ = station
            elif isinstance(station, str):
                code_station = station
                station_ = informations[code_station] if informations and informations[code_station] is not None else StationManager(code_station)
            else:
                print('station must be a string or StationManager but', station, 'is', type(station))
                continue

            if code_station not in set(self.stations) :
                self.metadata[code_station ] = station_
                self.stations.append(code_station )
                
    
    def remove_stations(self,stations : list) -> None:
        """
        Remove stations list to self.stations
        Parameters :
            stations : list of station codes (strings) and/or instances of StationManager
        """       
        for station in stations :
            try : 
                del self.metadata[station.code_station]
                self.stations.remove(station.code_station)
            except :
                pass
            try :
                del self.metadata[station]
                self.stations.remove(station)
            except :
                pass

    def create_map(self, marker = False) -> folium.Map :
        """
        Plots a map with all stations form self.stationss
        """             
        mean_latitude = np.array([self.metadata[s].latitude_station for s in self.stations ]).mean()
        mean_longitude = np.array([self.metadata[s].longitude_station for s in self.stations ]).mean()
        self.map = folium.Map(location=[mean_latitude,mean_longitude], zoom_start=6) #Centrer la carte
        for s in self.stations :
            station = self.metadata[s]
            if marker : 
                folium.Marker(
                    location=[station.latitude_station, station.longitude_station],
                    popup=station.libelle_station
                ).add_to(self.map)
            else : 
                folium.CircleMarker(
                    location=[station.latitude_station, station.longitude_station],
                    radius=5,
                    color='red',
                    fill=True,
                    fill_color='red',
                    popup=station.code_station+" "+station.libelle_cours_eau+" "+station.code_cours_eau
                ).add_to(self.map)
        return self.map
    
    def get_stations_obs(self,start_date : str,end_date : str) -> pd.DataFrame:
        """
        Fetches daily aggregated hydrological data flow output (L/s) for all stations
        contained in self.stations

        Returns a dataframe, stored as self.observations

        Arguments:
            start_date - str : Starting date of the request
            end_date - str : Ending date of the request
        """             
        if type(start_date) != str or type(end_date) != str : 
            raise TypeError('Dates are not strings')
        if (re.match(r'^\d{4}-\d{2}-\d{2}$',start_date) == False or  
            re.match(r'^\d{4}-\d{2}-\d{2}$',end_date) == False) :
            print('The date format must be YYYY-MM-DD')
            return False
        self.start_date = start_date
        self.end_date   = end_date

        dfs = []
        for s in self.stations :
            stationmanager = self.metadata[s]
            if stationmanager.get_obs(start_date,end_date) :
                stationmanager.obs_elab.columns = [stationmanager] 
                dfs.append(stationmanager.obs_elab)
        if len(dfs) != 0:
            self.observations = pd.concat(dfs,axis=1)
            return self.observations
        return None

    def get_nearest_station(self,code_station : str) -> str : 
        """
        Gets the nearest station from code_station, from geodesic distance
        Returns nearest code_station
        Arguments:
            code_station - str : code for the hydrological station, eg 'A021005050'
        """   
        if len(code_station.replace(' ','')) != 10 :
            raise ValueError('Invalid station code')
        if self.french_stations is None :
            self._get_all_french_stations()          
        coordsStation = [self.metadata[code_station].latitude_station,self.metadata[code_station].longitude_station]
        nearest = None
        nearestKm = np.inf
        for s in self.french_stations :
            if s == code_station :
                continue
            coords = [self.metadata[s].latitude_station,self.metadata[s].longitude_station]
            km = geopy.distance.geodesic(coordsStation,coords).km
            if km <  nearestKm :
                nearestKm = km
                nearest = s
        return nearest
    
    def get_commune(self) -> str : 
        """
        Gets the commune of all stations
        """   
        list=[]
        for s in self.stations :
            list.append(self.metadata[s].libelle_commune)
        return list

    
    def _get_all_french_stations(self,active =True, add_to_list : bool = False):

        """
        Fetches metadata from all stations in the Hub'Eau API
        Stores the metadata in self.french_stations (dict)

        Arguments:
            ,active - bool or None: if True, retrieves only active hydrological stations.
                                    If False, retrieves inactive stations.
                                    If None, retrieves all stations
            ajouter_a_liste - bool : if True, adds all stations to self.stations
        """

        try:
            if active is None:
                # Recover all stations


                self.french_stations = asyncio.run(sync_to_async(lambda: [station.code_station for station in db_Station.objects.all()])())
            else:
                # Retrieve stations by status (active or inactive)
                self.french_stations = asyncio.run(sync_to_async(lambda: [station.code_station for station in db_Station.objects.filter(en_service=active)])())

            
            for s in self.french_stations:
                self.metadata[s] = StationManager(code_station=s)
                
        except:
            en_service = ''
            if active == True : 
                en_service = 'en_service=true'
            elif active == False:
                en_service = 'en_service=false'

            r = requests.get(STATIONS \
            +en_service +'&format=json&size=10000',
                verify=False)
                        
            self.french_stations = [k['code_station'] for k in r.json()['data']]
                
            for k in r.json()['data'] :
                self.metadata[k['code_station']] = StationManager(code_station=k['code_station'],
                    informations=({key : value for key, value in k.items() if key not in ['code_station']}))
                    
        if add_to_list : 

            self.stations = self.french_stations

    def plot(self,stations : list = None) -> None :
        """
        Fetches metadata from all stations in the Hub'Eau API
        Stores the metadata in self.french_stations (dict)
        
        Arguments:
            active - bool : if True, fetches only active hydrological stations. 
                            If False, fetches also inactive stations
            stations - list : if not None, plots only data from selected stations
        """   
        if self.observations is None :
            print('No stations to display')
            return None
        
        if stations is None :
            df = self.observations
        else :
            df = self.observations[['obs_'+s for s in stations]]

        df.columns = [self.metadata[s.strip('obs_')].libelle_station + ' , ' +  s.strip('obs_') 
                    for s in df]
        df.plot(
            title='Flow observations between '+self.start_date+' et ' + self.end_date,
            xlabel='Date',
            ylabel='Débit ($L·s^{-1}$)')

    def export(self,file : str) -> None :
        """
        Exports all observations to a csv specified by file
        """
        if self.observations is None :
            raise LookupError("No data found for export")
        self.observations.to_csv(file)


    def _dict_station_coord(self) -> dict:
        """
        Returns a dictionary of sorted station codes and their coordinates.
        """
        stations_sorted = self.sort_stations()
        return {s.code_station: s.get_coordinates_station(True) for s in stations_sorted}
    
    def _get_highest_station(self):
        """
        Returns the station object with the highest altitude.
        """
        try:
            highest_station_code = max(self.stations, key=lambda s: self.metadata[s].altitude_ref_alti_station)
            highest_station = self.metadata[highest_station_code]
            return highest_station
        except ValueError:
            raise ValueError("No stations found in the list.")


    
    def sort_stations_by_altitude(self, reverse=False) -> list[StationManager]:
        """
        returns a list of stations sorted by altitude to source
        """
        stations_sorted = list(self.metadata.values())
        stations_sorted.sort(key=lambda stationManager: -stationManager.altitude_ref_alti_station, reverse=reverse)
        return stations_sorted

        #    V2:  trier les stations en fonction de leur proximité à la source en utilisant l'altitude 
    def sort_stations(self) -> list[StationManager]:
        source = self._get_highest_station()
        stations_sorted = [source]

        stations_list = [valeur for valeur in self.metadata.values() if valeur != source]

        while stations_list:
            current_station = stations_sorted[-1]
            closest_station = min(
                stations_list,
                key=lambda x: abs(x.altitude_ref_alti_station - current_station.altitude_ref_alti_station)
            )
            stations_sorted.append(closest_station)
            stations_list.remove(closest_station)

        return stations_sorted

    def get_last_station_with_obs(self, river_name: str, start_date: str, end_date: str) -> StationManager:
        """
        returns the object station with the lowest altitude
        """
        # retrieve all stations for a river
        asyncio.run(self.get_watercourse_stations(river_name))
        if len(self.stations) == 0:
            return None
        
        # retrieve station with lowest altitude and with obs
        stations_sorted = self.sort_stations_by_altitude(True)
        for station in stations_sorted:
            if station.en_service and station.get_obs(start_date, end_date):
                return station

        return None

    def sort_stations_by_altitude(self, reverse=False) -> list[StationManager]:
        """
        returns a list of stations sorted by altitude to source
        """
        stations_sorted = list(self.metadata.values())
        stations_sorted.sort(key=lambda stationManager: -stationManager.altitude_ref_alti_station, reverse=reverse)
        return stations_sorted


    # TODO : voir si on la supprime 

    @sync_to_async
    def get_watercourse_stations(self, river_name,reset=True):
        """
        Add all the stations from a watercourse from the database if connected 
        Parameters : 
            river_name  - str :  name of the river eg "Le Rhône"
            reset       - bool : True to remove all other stations from the object
        """ 
        if reset :
            self.stations = []
            self.metadata = {}

        try : 
            watercourse_stations = list(db_Station.objects.filter(libelle_cours_eau=river_name))
            for db_station in watercourse_stations:
                self.stations.append(db_station.code_station)
                # add instance stationManager in metadata
                informations = {}
                for field in db_station._meta.fields:
                    informations[field.name] = getattr(db_station, field.name)
                stationManager = StationManager(db_station.code_station, informations)
                self.metadata[db_station.code_station] = stationManager
        except :
            pass

    
    def __repr__(self) -> str:
        repr = 'List of stations considered: '
        repr += ', '.join(self.stations)
        return repr
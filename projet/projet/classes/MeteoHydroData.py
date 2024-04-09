import pandas as pd
import requests
import warnings
import re
from projet.models.stations import Station as db_Station
from projet.models.stations_meteo import Station_poste, Station_meteo
import nest_asyncio
from asgiref.sync import sync_to_async
from .station import StationManager
import asyncio
from projet.models.stations import Station
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)
pd.set_option('display.max_columns', None)
nest_asyncio.apply()
from datetime import datetime

class ObservationManager() : 

    def __init__(self):
        pass
    

    def get_multi_station_hydro_obs(self, stations_hydro, start_date, end_date):
        dfs = []
        for station in stations_hydro:
            try:
                station_manager = StationManager(station)
                
                if station_manager.get_obs(start_date, end_date):
                    dfs.append(station_manager.obs_elab)
                    
            except Exception as e:
                print(f"Error retrieving observations for station {station}: {e}")
        if len(dfs) > 0:
            observations_hydro = pd.concat(dfs, axis=1)
            observations_hydro.columns = stations_hydro
            observations_hydro.reset_index(inplace=True) 
            return observations_hydro
        else:
            return None
        
    @sync_to_async
    def get_multi_station_meteo_obs(self, id_posts, start_date, end_date):
        # Convert dates into the format expected by the database
        start_date = datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y%m%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d').strftime('%Y%m%d')
        station_dfs = []

        # Retrieve data from the Station_meteo table for each specified station
        for id_post in id_posts:

            data = Station_meteo.objects.filter(id_post=id_post, date_relv__range=(start_date, end_date)).values('haut_prec_RR', 'date_relv')

            station_df = pd.DataFrame(list(data))
            station_df.set_index('date_relv', inplace=True)  # Set date as index
            station_df.rename(columns={'haut_prec_RR':id_post}, inplace=True)  # Rename the precipitation column
            station_dfs.append(station_df)

        # Concatenate DataFrames for each station using dates as indexes
        observations_meteo = pd.concat(station_dfs, axis=1)
        observations_meteo.reset_index(inplace=True)

        observations_meteo.rename(columns={'date_relv': 'Date'}, inplace=True)

        observations_meteo.set_index('Date', inplace=True)
        observations_meteo.index = pd.to_datetime( observations_meteo .index, format='%Y%m%d').strftime('%Y-%m-%d')
        

        return observations_meteo  
        

    async def get_stations_obs(self, stations_hydro:list, id_posts:list, start_date:str, end_date:str) -> pd.DataFrame:
        # Call both methods to retrieve hydrological and meteorological data
        hydro_df = self.get_multi_station_hydro_obs(stations_hydro, start_date, end_date)
        meteo_df =  await self.get_multi_station_meteo_obs(id_posts, start_date, end_date)
        
        meteo_df.reset_index(inplace=True)
        
        hydro_df['Date'] = pd.to_datetime(hydro_df['Date'])
        meteo_df['Date'] = pd.to_datetime(meteo_df['Date'])
    

        # Concatenate the two DataFrames
        observations_df = pd.concat([hydro_df, meteo_df.drop(columns=['Date'])], axis=1)

        return observations_df


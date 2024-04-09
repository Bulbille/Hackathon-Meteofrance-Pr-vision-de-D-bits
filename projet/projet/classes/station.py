
import asyncio
import plotly.express as px
import matplotlib.pyplot as plt
import pandas as pd
import requests
import warnings
import re
from projet.models.stations import Station as db_Station
from .config_ssl import NoSSLVerification, urls
import nest_asyncio
from asgiref.sync import sync_to_async
from geopy.distance import geodesic
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)
pd.set_option('display.max_columns', None)
nest_asyncio.apply()
# Various links for retrieving data
#SITE      = "https://hubeau.eaufrance.fr/api/v1/hydrometrie/referentiel/sites?"
#OBS_TR    = "https://hubeau.eaufrance.fr/api/v1/hydrometrie/observations_tr?"
OBS_JOUR  = 'https://hubeau.eaufrance.fr/api/v1/hydrometrie/obs_elab?'
STATIONS  = "https://hubeau.eaufrance.fr/api/v1/hydrometrie/referentiel/stations?"

#no ssl certificate verification
session = requests.Session()
for url in urls:
    session.mount(url, NoSSLVerification())

class StationManager():
    """
    Class for one hydrological station from Hub'eau
    """
    def __init__(self, code_station: str, informations: dict = None) -> None:
        if len(code_station.replace(' ', '')) != 10:
            raise ValueError('Code station non valide')
        self.code_station = code_station
        self.station_name = None
        if informations is not None:
            for k, v in informations.items():
                setattr(self, k, v)
        else:
            asyncio.run(self.load_information_from_database())

    @sync_to_async
    def load_information_from_database(self):
        """
        Try to find the information in the database
        """
        try:
            db_station = db_Station.objects.get(code_station=self.code_station)
            for field in db_station._meta.fields:
                setattr(self, field.name, getattr(db_station, field.name))
                self.station_name = db_station.libelle_station 
        except db_Station.DoesNotExist:
            self.load_information_from_API()

    def load_information_from_API(self):
        """
        Try to find the information in the API
        """
        try: 
            response = session.get(STATIONS+ 'code_station=' + self.code_station)
            if response.status_code == 500 :
                raise TimeoutError('Server internal error') 
            elif response.status_code != 200 and  response.status_code != 206 : 
                raise ValueError('incorrect station code')
            for k,v in response.json()['data'][0].items() :
                setattr(self,k,v)
        except :
            raise ValueError("station code not found")


    def get_station_data(self, start_date: str, end_date: str) -> bool:
        
        if type(start_date) != str or type(end_date) != str: 
            raise TypeError('Dates are not strings')

        if not (re.match(r'^\d{4}-\d{2}-\d{2}$', start_date) and re.match(r'^\d{4}-\d{2}-\d{2}$', end_date)):
            raise ValueError('The date format must be YYYY-MM-DD')

        url = "https://hubeau.eaufrance.fr/api/v1/hydrometrie/obs_elab"
        params = {
            'code_entite': self.code_station,
            'date_debut_obs_elab': start_date,
            'date_fin_obs_elab': end_date,
            'grandeur_hydro_elab': 'QmJ',
            'size': 20000
        }

        df_obs = pd.DataFrame()

        while url:
            try:
                response = session.get(url, params=params)
                data = response.json()
                new_data = data['data']
                url = data.get('next') 
                new_df = pd.DataFrame(new_data)
                df_obs = pd.concat([df_obs, new_df], ignore_index=True)
            except Exception as e:
                print(f"Data recovery error : {e}")
                return False

        if df_obs.empty:
            self.obs_elab = None
            return False
        
        df_obs['Date'] = pd.to_datetime(df_obs['date_obs_elab'])
        df_obs.set_index('Date', inplace=True)
        df_obs.insert(0, 'Station name', self.libelle_station)
        self.obs_elab = df_obs

        return df_obs

    
    
    def get_obs(self,start_date : str,end_date : str) -> bool:
        """
        Fetches daily aggregated hydrological data flow output (L/s)
        Returns True if fetching succeeded

        Arguments:
            start_date - str : Starting date of the request YYYY-MM-DD
            end_date - str : Ending date of the request YYYY-MM-DD
        """            
        if type(start_date) != str or type(end_date) != str :
            raise TypeError('Dates are not strings')

        if( re.match(r'^\d{4}-\d{2}-\d{2}$',start_date) == False or
            re.match(r'^\d{4}-\d{2}-\d{2}$',end_date) == False) :
            print('The date format must be YYYY-MM-DD')
            return False
        self.start_date = start_date
        self.end_date   = end_date
        if self.en_service == False :
            self.obs_elab = None
            return False
    
        if hasattr(self,'obs_elab') :
            print('Previous data will be overwritten')

        r = session.get(OBS_JOUR \
                + 'code_entite=' + self.code_station
                +'&date_debut_obs_elab=' + start_date
                +'&date_fin_obs_elab=' + end_date
                +'&grandeur_hydro_elab=QmJ&size=10000')

        if r.status_code == 500 :
            raise TimeoutError('Internal server error')
        elif r.status_code != 200 and  r.status_code != 206 :
            raise ValueError('invalid station code')
            
        obs_elab = [[d['date_obs_elab'],d['resultat_obs_elab']] for d in r.json()['data']]
        if len(obs_elab) == 0 :
            self.obs_elab = None
            return False

        df = pd.DataFrame(obs_elab,columns=['Date','obs_'+self.code_station])
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date',inplace=True)

        self.start_date = start_date
        self.end_date   = end_date
        self.obs_elab   = df

        return True
    
  
    
    def graph_stations(self, df_stations, start_date=None, end_date=None):
        """
        Generates a graph from the data in the `df_stations` DataFrame to display the values
        observed results by date for several stations.
        """
        if start_date is not None and end_date is not None:
            df_stations = df_stations[(df_stations['date_obs_elab'] >= start_date) & (df_stations['date_obs_elab'] <= end_date)]
        
        df_stations['date_obs_elab'] = pd.to_datetime(df_stations['date_obs_elab'])
        pivot_df = df_stations.pivot(index='date_obs_elab', columns='libelle_station', values='resultat_obs_elab')

        plt.figure(figsize=(30, 15))
        pivot_df.plot(kind='bar', ax=plt.gca())
        # pivot_df.plot(kind='line', ax=plt.gca())

        plt.xticks(fontsize=20, rotation=90)
        plt.xlabel('Date', fontsize=30)
        plt.ylabel('Values (L/s)', fontsize=30)
        plt.yticks(fontsize=20)
        plt.title('Observed Results by Station and Date', fontsize=44)
        plt.legend(title='Stations', fontsize=20)


        
    def get_distance_to(self, code_station): 
        """
        returns the distance between 2 stations
        """
        station = StationManager(code_station)
        coordinates_B = (station.latitude_station, station.longitude_station)
        coordinates_A = (self.latitude_station, self.longitude_station)

        distance = geodesic(coordinates_A, coordinates_B).kilometers

        return distance
    
    def get_coordinates_station(self):
        """
        Returns coordinates in the format [longitude, latitude] 
        """
        return [self.longitude_station, self.latitude_station] 
    
    def create_correlation_df(self, station, year:int, time_shift_count:int=7)->pd.DataFrame:
        """
            Create correlation between 2 stations for year
        """
        start_date = str(year)+'-01-01'
        end_date = str(year)+'-12-31'

        if not self.get_obs(start_date, end_date):
            raise ValueError("Station {} without data".format(self))
        if not station.get_obs(start_date, end_date):
            raise ValueError("Station {} without data".format(station))
        
        debit_df = pd.concat([self.obs_elab, station.obs_elab], axis=1)

        # calculate correlation with time shift
        correlations = []
        index = []
        for time_shift in range(-time_shift_count , time_shift_count) :

            if time_shift > 0 :
                normal  = debit_df[debit_df.columns[0]].values
                shifted = debit_df[debit_df.columns[1]].values[time_shift:]
            else :
                normal  = debit_df[debit_df.columns[0]].values[-time_shift:]
                shifted = debit_df[debit_df.columns[1]].values

            minLength = min(len(normal),len(shifted))
            correlation_series = pd.DataFrame({'obs_xx' : normal[:minLength], 'obs_xxx' : shifted[:minLength]}).corr().iloc[0,1]

            index.append(time_shift)
            correlations.append(correlation_series)

        correlation_df = pd.DataFrame(correlations, columns=[year], index=index)
        return correlation_df

    def create_correlation_plot(self, station, correlation_df:pd.DataFrame):
        """
            Create correlation plot (see create_correlation_df method)
            Test \\sf1coeur\SHT-RD-PRODUCTION\Production\RnI_PLANT\05 - Espace contributeurs\2024\LAGARDE Cyril\20 - Stockage libre\\test_issue16.ipynb
        """
        return correlation_df.plot(xlabel="Time shift", ylabel="Correlation", title="Correlation '{}' and '{}'".format(self, station))    
    
    def __repr__(self) -> str:
        return self.libelle_station
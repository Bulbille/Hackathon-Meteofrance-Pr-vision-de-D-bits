import os
import configparser
config = configparser.ConfigParser()
script_path = os.path.abspath(__file__)
project_dir = os.path.dirname(os.path.dirname(script_path))
config_file_path = os.path.join(project_dir, 'config_file.ini')
config.read(config_file_path)
import sys
from .station import StationManager
sys.path.append(config['PATH']['app_install'])
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projet.settings")  
import django
django.setup()
import pandas as pd
import requests
import time
import io
import numpy as np


class ObservationStations:
    def __init__(self):
        pass

    def observation_meteo_from_orderId(self, url, api_key, id_order):
        
        headers_url = {
            'Accept-Language': 'en-US,en;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.201 Microsoft Edge for Business/120.0.2210.121 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'apikey': f'{api_key}',
            'Connection': 'keep-alive'
        }
        url = f"{url}{id_order}"
        response = requests.get(url, headers=headers_url, verify=False)

        if response.status_code == 201:
            data_csv_pd_read = pd.read_csv(io.StringIO(response.content.decode('utf-8')), delimiter=";")
            return data_csv_pd_read
        else:
            sleep_time = int(config['SLEEP']['sleep_api'])
            time.sleep(sleep_time)

            response = requests.get(url, headers=headers_url, verify=False)
            
            if response.status_code == 201:
                data_csv_pd_read = pd.read_csv(io.StringIO(response.content.decode('utf-8')), delimiter=";")
                return data_csv_pd_read
            else:
                return None

    def get_id_order(self, url, api_key, id_post, start_date, end_date):

        headers_url = {
            'Accept-Language': 'en-US,en;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.201 Microsoft Edge for Business/120.0.2210.121 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'apikey': f'{api_key}',
            'Connection': 'keep-alive'
        }
        url_id_cmd = "https://public-api.meteofrance.fr/public/DPClim/v1/commande-station/quotidienne?id-station="
        url = f"{url_id_cmd}{id_post}&date-deb-periode={start_date}&date-fin-periode={end_date}"
        try:
            response = requests.get(url, headers=headers_url, verify=False)
            response_json = response.json()

            if response.status_code == 202:
                data_json_df = pd.DataFrame(response_json)
                return data_json_df.iloc[0, 0]

            else:
                sleep_time = int(config['SLEEP']['sleep_api'])
                time.sleep(sleep_time)
                response = requests.get(url, headers=headers_url, verify=False)
                response_json = response.json()
                if response.status_code == 202:
                    data_json_df = pd.DataFrame(response_json)
                    df = data_json_df.iloc[0, 0]
                    return df
                else:
                    return False
        except ValueError:
            print(ValueError)


    def get_observations(self, list_stations, start_date, end_date):
        api_key ="eyJ4NXQiOiJZV0kxTTJZNE1qWTNOemsyTkRZeU5XTTRPV014TXpjek1UVmhNbU14T1RSa09ETXlOVEE0Tnc9PSIsImtpZCI6ImdhdGV3YXlfY2VydGlmaWNhdGVfYWxpYXMiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJwcm9qZXRQbGFudEBjYXJib24uc3VwZXIiLCJhcHBsaWNhdGlvbiI6eyJvd25lciI6InByb2pldFBsYW50IiwidGllclF1b3RhVHlwZSI6bnVsbCwidGllciI6IlVubGltaXRlZCIsIm5hbWUiOiJEZWZhdWx0QXBwbGljYXRpb24iLCJpZCI6Njk5NSwidXVpZCI6ImQ2OTdiNjdhLWQxZDgtNGIxNy1hZjYzLTE3MmI2NzQxYWVkOCJ9LCJpc3MiOiJodHRwczpcL1wvcG9ydGFpbC1hcGkubWV0ZW9mcmFuY2UuZnI6NDQzXC9vYXV0aDJcL3Rva2VuIiwidGllckluZm8iOnsiNTBQZXJNaW4iOnsidGllclF1b3RhVHlwZSI6InJlcXVlc3RDb3VudCIsImdyYXBoUUxNYXhDb21wbGV4aXR5IjowLCJncmFwaFFMTWF4RGVwdGgiOjAsInN0b3BPblF1b3RhUmVhY2giOnRydWUsInNwaWtlQXJyZXN0TGltaXQiOjAsInNwaWtlQXJyZXN0VW5pdCI6InNlYyJ9fSwia2V5dHlwZSI6IlBST0RVQ1RJT04iLCJzdWJzY3JpYmVkQVBJcyI6W3sic3Vic2NyaWJlclRlbmFudERvbWFpbiI6ImNhcmJvbi5zdXBlciIsIm5hbWUiOiJEb25uZWVzUHVibGlxdWVzT2JzZXJ2YXRpb24iLCJjb250ZXh0IjoiXC9wdWJsaWNcL0RQT2JzXC92MSIsInB1Ymxpc2hlciI6ImJhc3RpZW5nIiwidmVyc2lvbiI6InYxIiwic3Vic2NyaXB0aW9uVGllciI6IjUwUGVyTWluIn0seyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6IkRvbm5lZXNQdWJsaXF1ZXNDbGltYXRvbG9naWUiLCJjb250ZXh0IjoiXC9wdWJsaWNcL0RQQ2xpbVwvdjEiLCJwdWJsaXNoZXIiOiJhZG1pbl9tZiIsInZlcnNpb24iOiJ2MSIsInN1YnNjcmlwdGlvblRpZXIiOiI1MFBlck1pbiJ9LHsic3Vic2NyaWJlclRlbmFudERvbWFpbiI6ImNhcmJvbi5zdXBlciIsIm5hbWUiOiJEb25uZWVzUHVibGlxdWVzUGFxdWV0T2JzZXJ2YXRpb24iLCJjb250ZXh0IjoiXC9wdWJsaWNcL0RQUGFxdWV0T2JzXC92MSIsInB1Ymxpc2hlciI6ImJhc3RpZW5nIiwidmVyc2lvbiI6InYxIiwic3Vic2NyaXB0aW9uVGllciI6IjUwUGVyTWluIn1dLCJleHAiOjE3MTk0NjA4NjcsInRva2VuX3R5cGUiOiJhcGlLZXkiLCJpYXQiOjE3MDcyMzg2NDUsImp0aSI6Ijc3ZDE0NTFkLTE0YWItNDlmZi1iMTg5LWU0YTcwZGQyNGZkNCJ9.Z1U6EdHP3tinMJ-2Ed2wZLSHL44cOzqfh3Al2PC5Wq6nz3qKexMllNWIm9sd1xAMvCaCvBCfmpIIk4k6svWfEInGEtpYEHwAF337wRabDGjXjFp2Fmig6Trhr9V1XRSVeGcCGgpBt28x8eMCfLEGKUPedRAE0LkJFby0Jx4QT1Gtkyi8VsfXHx9-hbOfB7WuI7HxcJ9o94dKOxMv0AQbnfhdhaKc8Grmu-D8fMjloT6hfJCSEuChOHjfm8bR_s71TOVKByXrC687G-Z0tGLhYZkg5Ne2bUrowszXLGunHdHdHboSRdLO2XYU8RsomDwyve5I26MQBJx13jS11Wrblg=="
        url_id_cmd = "https://public-api.meteofrance.fr/public/DPClim/v1/commande-station/quotidienne?id-station="
        url_populate = "https://public-api.meteofrance.fr/public/DPClim/v1/commande/fichier?id-cmde="
        data_concatenated = pd.DataFrame({'DATE': []})
        stations_with_data = [] 
        
        for id_post in list_stations:
            id_commande = self.get_id_order(url_id_cmd, api_key, id_post, start_date, end_date)
            print("id de commande", id_commande)
            data_df = self.observation_meteo_from_orderId(url_populate, api_key, id_commande)
            # print( "dataframe complet:", data_df)
            if data_df is not None and not data_df.empty:
                data_subset = data_df[['POSTE', 'DATE', 'RR']]
                data_pivoted = data_subset.pivot(index='DATE', columns='POSTE', values='RR').reset_index()
                data_pivoted['DATE'] = pd.to_datetime(data_pivoted['DATE'], format='%Y%m%d')
                data_pivoted = data_pivoted.replace({None: np.nan}) 
                data_concatenated = pd.merge(data_concatenated, data_pivoted, on='DATE', how='outer')
                stations_with_data.append(id_post)  # Add station to list of stations with data
                # print(data_concatenated)
        
        # Check stations for which no data has been found and display a message
        missing_stations = set(list_stations) - set(stations_with_data)
        for station in missing_stations:
            print(f"No data found for station {station} between {start_date} and {end_date}.")
        data_concatenated.rename(columns={'DATE': 'Date'}, inplace=True)
        return data_concatenated

    def get_multi_station_hydro_obs(self, stations_hydro, start_date, end_date):
        dfs = []
        stations_without_data = []
        
        for station in stations_hydro:
            try:
                station_manager = StationManager(station)
                if station_manager.get_obs(start_date, end_date):
                    df = station_manager.obs_elab
                    df.columns = [station]  # Renommer la colonne avec le nom de la station
                    dfs.append(df)
                else:
                    stations_without_data.append(station)
            except Exception as e:
                print(f"Error retrieving observations for station {station}: {e}")

        if len(dfs) > 0:
            observations_hydro = pd.concat(dfs, axis=1)
            observations_hydro.reset_index(inplace=True) 
            if len(stations_without_data) > 0:
                print("No observations found for the following stations during the specified period:")
                for station in stations_without_data:
                    print(f"- {station}")
            return observations_hydro
        else:
            return pd.DataFrame()
    
    def concatene_dataframes(self, df_obs_hydro, df_PP_meteo):
        
        
        df_PP_meteo.iloc[:, 1:] = df_PP_meteo.iloc[:, 1:].apply(lambda x: x.str.replace(',', '.'))
        # Concatenate the two dataframes on the 'Date' column with an outer join
        df_concat = pd.merge(df_obs_hydro, df_PP_meteo, on='Date', how='outer')
        
        # Save the concatenated dataframe in CSV format
        csv_file = "liste_stations_affluents_bordeaux_meteo+hydro.csv"
        df_concat.to_csv(csv_file, index=False)
        
        return csv_file



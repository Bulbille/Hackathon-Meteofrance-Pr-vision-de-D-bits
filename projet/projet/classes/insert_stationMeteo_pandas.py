########      INSERT IN METEO_STATION from weather API with pandas library(csv file)          #########
########      Import packages                                                                 #########
########      IMPORTANT: RESPECT THE ORDER OF THE IMPORT                                      #########
########      The API works by doing 2 differents requests to get data                        #########
########      The first request give you an ID for an order                                   #########
########      The second by giving the ID will give you data requested                        #########
import os
import configparser
config = configparser.ConfigParser()
config.read(r"C:\Users\sagrib\hydrologie\projet\projet\config_file.ini")
import sys
sys.path.append(config['PATH']['app_install'])
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projet.settings")  
import django
django.setup()

from projet.models.stations_meteo import Station_meteo, Station_poste
#### module => count() function available for the models  ####

import pandas as pd
from .config_ssl import NoSSLVerification, urls
import requests
import time
import io

#no ssl certificate verification
session = requests.Session()
for url in urls:
    session.mount(url, NoSSLVerification())

####  populate the station_meteo table ####
def populate_meteo_from_orderId(url, api_key, id_order) :

    headers_url = {
        'Accept-Language': 'en-US,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.201 Microsoft Edge for Business/120.0.2210.121 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'apikey':f'{api_key}',
        'Connection': 'keep-alive'
        }
    url = f"{url}{id_order}"

    #### response body = csv file ####
    response = session.get(url, headers=headers_url)
    response_content = response.text

    print(response.status_code)
    if response.status_code == 201 :
        #### reading a csv file needs an io module   ####
        data_csv_pd_read= pd.read_csv(io.StringIO(response.content.decode('utf-8')),delimiter=";")
        #### reading dataframe from csv file      ####

        #### loop for number of rows #### 
        for idx in range(len(data_csv_pd_read.index)) :

            ###  get_or_create function(returning tuple[station_poste, bool]) allows to test whether row already exists or needs to be created ####
            ###  function choosen instead of 2 functions get() and create() ####
            station_data = Station_meteo.objects.get_or_create(id_post_id=data_csv_pd_read.iloc[idx]['POSTE'],
                                                                haut_prec_RR= str(data_csv_pd_read.iloc[idx]['RR']).replace(',','.'),
                                                                duree_prec_DRR=str(data_csv_pd_read.iloc[idx]['DRR']).replace(',','.'),
                                                                date_relv=data_csv_pd_read['DATE'].iloc[idx])

            print("end of loop = " +str(idx))
    else :
        sleep_time = int(config['SLEEP']['sleep_api'])
        time.sleep(sleep_time)

        response = session.get(url, headers=headers_url)
        response_content = response.text

        print(response.status_code)
        if response.status_code == 201 :

            data_csv_pd_read= pd.read_csv(io.StringIO(response.content.decode('utf-8')),delimiter=";")
            
            for idx in range(len(data_csv_pd_read.index)) :

                station_data = Station_meteo.objects.get_or_create(id_post_id=data_csv_pd_read.iloc[idx]['POSTE'],
                                                                haut_prec_RR= str(data_csv_pd_read.iloc[idx]['RR']).replace(',','.'),
                                                                duree_prec_DRR=str(data_csv_pd_read.iloc[idx]['DRR']).replace(',','.'),
                                                                date_relv=data_csv_pd_read['DATE'].iloc[idx])
            
            print("2nd attempt end of loop = {idx}")


#### get command id for selected dates and station id ####
def get_id_order(url, api_key, id_post, deb_date, end_date) :
    
    headers_url = {
        'Accept-Language': 'en-US,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.201 Microsoft Edge for Business/120.0.2210.121 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'apikey':f'{api_key}',
        'Connection': 'keep-alive'
        }
    
    #### format of the url ####
    ### https://public-api.meteofrance.fr/public/DPClim/v1/commande-station/quotidienne?id-station=75106001&date-deb-periode=2024-01-01T12%3A00%3A00Z&date-fin-periode=2024-01-02T12%3A00%3A00Z   #### 
    url = f"{url}{id_post}&date-deb-periode={deb_date}&date-fin-periode={end_date}"
    
    ####   Test API response => response body= json format  ####
    try :
        response = session.get(url, headers=headers_url)
        response_json = response.json()
        print("response_json " +str(response_json))

        if response.status_code == 202 :
            # TODO pas besoin d 'utiliser un dataframe
            data_json_df = pd.DataFrame(response_json)

            ####  json file => storage of id_cmd in nested field "return"  ####
            #### response body(json) = {'elaboreProduitAvecDemandeResponse': {'return': '762365728628'}}  ####
            return data_json_df.iloc[0,0]
            #print(f"ret = {ret}")

        else :
        #  Reason for pause: In the event of an overload of requests on the Météo France API, a pause is necessary before calling it back.
        # 10-second pause duration: This is an arbitrary choice that can be modified as required.
            print("pause 10 sec")
            time.sleep(config['SLEEP']['sleep_api'])
            response = session.get(url, headers=headers_url)
            response_json = response.json()
            if response.status_code == 202 :
                # TODO pas besoin d'utiliser le dataframe
                data_json_df = pd.DataFrame(response_json)
                df= data_json_df.iloc[0,0]
                return df
            else :
                return False
    except ValueError :
        print(ValueError)
    
    


if __name__ == "__main__":
    base_url_id_cmd   = "https://public-api.meteofrance.fr/public/DPClim/v1/commande-station/quotidienne?id-station="
    base_url_populate = "https://public-api.meteofrance.fr/public/DPClim/v1/commande/fichier?id-cmde="
    api_key           = "eyJ4NXQiOiJZV0kxTTJZNE1qWTNOemsyTkRZeU5XTTRPV014TXpjek1UVmhNbU14T1RSa09ETXlOVEE0Tnc9PSIsImtpZCI6ImdhdGV3YXlfY2VydGlmaWNhdGVfYWxpYXMiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJwcm9qZXRQbGFudEBjYXJib24uc3VwZXIiLCJhcHBsaWNhdGlvbiI6eyJvd25lciI6InByb2pldFBsYW50IiwidGllclF1b3RhVHlwZSI6bnVsbCwidGllciI6IlVubGltaXRlZCIsIm5hbWUiOiJEZWZhdWx0QXBwbGljYXRpb24iLCJpZCI6Njk5NSwidXVpZCI6ImQ2OTdiNjdhLWQxZDgtNGIxNy1hZjYzLTE3MmI2NzQxYWVkOCJ9LCJpc3MiOiJodHRwczpcL1wvcG9ydGFpbC1hcGkubWV0ZW9mcmFuY2UuZnI6NDQzXC9vYXV0aDJcL3Rva2VuIiwidGllckluZm8iOnsiNTBQZXJNaW4iOnsidGllclF1b3RhVHlwZSI6InJlcXVlc3RDb3VudCIsImdyYXBoUUxNYXhDb21wbGV4aXR5IjowLCJncmFwaFFMTWF4RGVwdGgiOjAsInN0b3BPblF1b3RhUmVhY2giOnRydWUsInNwaWtlQXJyZXN0TGltaXQiOjAsInNwaWtlQXJyZXN0VW5pdCI6InNlYyJ9fSwia2V5dHlwZSI6IlBST0RVQ1RJT04iLCJzdWJzY3JpYmVkQVBJcyI6W3sic3Vic2NyaWJlclRlbmFudERvbWFpbiI6ImNhcmJvbi5zdXBlciIsIm5hbWUiOiJEb25uZWVzUHVibGlxdWVzT2JzZXJ2YXRpb24iLCJjb250ZXh0IjoiXC9wdWJsaWNcL0RQT2JzXC92MSIsInB1Ymxpc2hlciI6ImJhc3RpZW5nIiwidmVyc2lvbiI6InYxIiwic3Vic2NyaXB0aW9uVGllciI6IjUwUGVyTWluIn0seyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6IkRvbm5lZXNQdWJsaXF1ZXNDbGltYXRvbG9naWUiLCJjb250ZXh0IjoiXC9wdWJsaWNcL0RQQ2xpbVwvdjEiLCJwdWJsaXNoZXIiOiJhZG1pbl9tZiIsInZlcnNpb24iOiJ2MSIsInN1YnNjcmlwdGlvblRpZXIiOiI1MFBlck1pbiJ9LHsic3Vic2NyaWJlclRlbmFudERvbWFpbiI6ImNhcmJvbi5zdXBlciIsIm5hbWUiOiJEb25uZWVzUHVibGlxdWVzUGFxdWV0T2JzZXJ2YXRpb24iLCJjb250ZXh0IjoiXC9wdWJsaWNcL0RQUGFxdWV0T2JzXC92MSIsInB1Ymxpc2hlciI6ImJhc3RpZW5nIiwidmVyc2lvbiI6InYxIiwic3Vic2NyaXB0aW9uVGllciI6IjUwUGVyTWluIn1dLCJleHAiOjE3MTk0NjA4NjcsInRva2VuX3R5cGUiOiJhcGlLZXkiLCJpYXQiOjE3MDcyMzg2NDUsImp0aSI6Ijc3ZDE0NTFkLTE0YWItNDlmZi1iMTg5LWU0YTcwZGQyNGZkNCJ9.Z1U6EdHP3tinMJ-2Ed2wZLSHL44cOzqfh3Al2PC5Wq6nz3qKexMllNWIm9sd1xAMvCaCvBCfmpIIk4k6svWfEInGEtpYEHwAF337wRabDGjXjFp2Fmig6Trhr9V1XRSVeGcCGgpBt28x8eMCfLEGKUPedRAE0LkJFby0Jx4QT1Gtkyi8VsfXHx9-hbOfB7WuI7HxcJ9o94dKOxMv0AQbnfhdhaKc8Grmu-D8fMjloT6hfJCSEuChOHjfm8bR_s71TOVKByXrC687G-Z0tGLhYZkg5Ne2bUrowszXLGunHdHdHboSRdLO2XYU8RsomDwyve5I26MQBJx13jS11Wrblg=="
    id_dept = "75"

    l_id_post = Station_poste.objects.filter(id_post__startswith=id_dept).values()
    print(f"{l_id_post}")
    pdf = pd.DataFrame(l_id_post)
    
    for idx in range(len(pdf.index)) :
        id_post = pdf.iloc[idx]['id_post']
   

###### CAREFUL SELECTION OF START AND END DATES
        deb_date = "2023-01-01T12:00:00Z"
        end_date = "2023-12-31T12:00:00Z"

        id_cmd = get_id_order(url=base_url_id_cmd, api_key=api_key, id_post=id_post, deb_date=deb_date, end_date=end_date)
        populate_meteo_from_orderId(url=base_url_populate,api_key=api_key, id_order=id_cmd)




########      INSERT IN METEO_POSTE from weather API with pandas library (json file)           #########
########      Import packages                                                                  #########
########      IMPORTANT: RESPECT THE ORDER OF THE IMPORT                                       #########
from json import JSONDecodeError
import os
import sys
import configparser

config = configparser.ConfigParser()
config.read(r"C:\Users\sagrib\hydrologie\projet\projet\config_file.ini")

app_install_path = config['PATH']['app_install']
sys.path.append(app_install_path)
print("Chemin ajouté à sys.path :", app_install_path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projet.settings")  
import django
django.setup()
import time
from turtle import goto
from django.db import models
from projet.models.stations_meteo import Station_meteo, Station_poste
from .config_ssl import NoSSLVerification, urls
from django.db.models import Count
import pandas as pd
import requests
import csv
import io

#no ssl certificate verification
session = requests.Session()
for url in urls:
    session.mount(url, NoSSLVerification())

###  populate the station_poste from weather API #### 
def populate_station_Poste(base_url, api_key, dpt_id) :
    print("----  POPULATE -----")
    url = f"{base_url}{dpt_id}"

    headers_url = {
    'Accept-Language': 'en-US,en;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.201 Microsoft Edge for Business/120.0.2210.121 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'apikey':f'{api_key}',
    'Connection': 'keep-alive'
    }

    ###  list of failed dept_id or id_post if an exception is raised ####
    dep_id_failed = []
    ###  test if API request was successful => response body = json file #### 
    try : 
        response = session.get(url, headers=headers_url)

        print("status resp ==> ",response.status_code)

        response_json = response.json()
        
        if response.status_code == 200 :
            
            for idx in range(0,len(response_json)) :    
               
                station_poste, created = Station_poste.objects.get_or_create(id_post= response_json[idx]['id'],
                                                                            post_name= response_json[idx]['nom'],
                                                                            post_open= response_json[idx]['posteOuvert'],
                                                                            post_type = response_json[idx]['typePoste'],
                                                                            post_long = str(response_json[idx]['lon']).replace(',','.'),
                                                                            post_lati = str(response_json[idx]['lat']).replace(',','.'),
                                                                            post_alti = str(response_json[idx]['alt']).replace(',','.'),
                                                                            post_publi = response_json[idx]['postePublic']
                                                                            )

        
        ###  failure in response of API ####     
        else :
            print("code response invalid, idx <> 200, wait few seconds before automatically re-call \n", idx)
    #         ###  Wait few sec before re-call API #### 
            time.sleep(int(config['SLEEP']['sleep_api']))

            while idx < range(len(response_json)) :
                response = session.get(url, headers=headers_url)
                response_json2 = response.json()
                if response.status_code == 200 :
                     for idx in range(len(response_json2)) :
                         station_poste, created = Station_poste.objects.get_or_create(id_post= response_json[idx]['id'],
                                                                            post_name= response_json[idx]['nom'],
                                                                            post_open= response_json[idx]['posteOuvert'],
                                                                            post_type = response_json[idx]['typePoste'],
                                                                            post_long = str(response_json[idx]['lon']).replace(',','.'),
                                                                            post_lati = str(response_json[idx]['lat']).replace(',','.'),
                                                                            post_alti = str(response_json[idx]['alt']).replace(',','.'),
                                                                            post_publi = response_json[idx]['postePublic']
                                                                            )
                        
                else :

                    dep_id_failed.append(response_json2[idx]['id'])
                    raise requests.exceptions.RequestException('bad status code')
        return dep_id_failed
    except requests.exceptions.RequestException as errReq:
        print("response.json failed!!")
        dep_id_failed.append(dpt_id)
        return dep_id_failed

        

if __name__ == "__main__":
    print("PATH dir = ", config['PATH']['dir'])

    base_url = "https://public-api.meteofrance.fr/public/DPClim/v1/liste-stations/quotidienne?id-departement="
    
    api_key = "eyJ4NXQiOiJZV0kxTTJZNE1qWTNOemsyTkRZeU5XTTRPV014TXpjek1UVmhNbU14T1RSa09ETXlOVEE0Tnc9PSIsImtpZCI6ImdhdGV3YXlfY2VydGlmaWNhdGVfYWxpYXMiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJwcm9qZXRQbGFudEBjYXJib24uc3VwZXIiLCJhcHBsaWNhdGlvbiI6eyJvd25lciI6InByb2pldFBsYW50IiwidGllclF1b3RhVHlwZSI6bnVsbCwidGllciI6IlVubGltaXRlZCIsIm5hbWUiOiJEZWZhdWx0QXBwbGljYXRpb24iLCJpZCI6Njk5NSwidXVpZCI6ImQ2OTdiNjdhLWQxZDgtNGIxNy1hZjYzLTE3MmI2NzQxYWVkOCJ9LCJpc3MiOiJodHRwczpcL1wvcG9ydGFpbC1hcGkubWV0ZW9mcmFuY2UuZnI6NDQzXC9vYXV0aDJcL3Rva2VuIiwidGllckluZm8iOnsiNTBQZXJNaW4iOnsidGllclF1b3RhVHlwZSI6InJlcXVlc3RDb3VudCIsImdyYXBoUUxNYXhDb21wbGV4aXR5IjowLCJncmFwaFFMTWF4RGVwdGgiOjAsInN0b3BPblF1b3RhUmVhY2giOnRydWUsInNwaWtlQXJyZXN0TGltaXQiOjAsInNwaWtlQXJyZXN0VW5pdCI6InNlYyJ9fSwia2V5dHlwZSI6IlBST0RVQ1RJT04iLCJzdWJzY3JpYmVkQVBJcyI6W3sic3Vic2NyaWJlclRlbmFudERvbWFpbiI6ImNhcmJvbi5zdXBlciIsIm5hbWUiOiJEb25uZWVzUHVibGlxdWVzT2JzZXJ2YXRpb24iLCJjb250ZXh0IjoiXC9wdWJsaWNcL0RQT2JzXC92MSIsInB1Ymxpc2hlciI6ImJhc3RpZW5nIiwidmVyc2lvbiI6InYxIiwic3Vic2NyaXB0aW9uVGllciI6IjUwUGVyTWluIn0seyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6IkRvbm5lZXNQdWJsaXF1ZXNDbGltYXRvbG9naWUiLCJjb250ZXh0IjoiXC9wdWJsaWNcL0RQQ2xpbVwvdjEiLCJwdWJsaXNoZXIiOiJhZG1pbl9tZiIsInZlcnNpb24iOiJ2MSIsInN1YnNjcmlwdGlvblRpZXIiOiI1MFBlck1pbiJ9LHsic3Vic2NyaWJlclRlbmFudERvbWFpbiI6ImNhcmJvbi5zdXBlciIsIm5hbWUiOiJEb25uZWVzUHVibGlxdWVzUGFxdWV0T2JzZXJ2YXRpb24iLCJjb250ZXh0IjoiXC9wdWJsaWNcL0RQUGFxdWV0T2JzXC92MSIsInB1Ymxpc2hlciI6ImJhc3RpZW5nIiwidmVyc2lvbiI6InYxIiwic3Vic2NyaXB0aW9uVGllciI6IjUwUGVyTWluIn1dLCJleHAiOjE3MTk0NjA4NjcsInRva2VuX3R5cGUiOiJhcGlLZXkiLCJpYXQiOjE3MDcyMzg2NDUsImp0aSI6Ijc3ZDE0NTFkLTE0YWItNDlmZi1iMTg5LWU0YTcwZGQyNGZkNCJ9.Z1U6EdHP3tinMJ-2Ed2wZLSHL44cOzqfh3Al2PC5Wq6nz3qKexMllNWIm9sd1xAMvCaCvBCfmpIIk4k6svWfEInGEtpYEHwAF337wRabDGjXjFp2Fmig6Trhr9V1XRSVeGcCGgpBt28x8eMCfLEGKUPedRAE0LkJFby0Jx4QT1Gtkyi8VsfXHx9-hbOfB7WuI7HxcJ9o94dKOxMv0AQbnfhdhaKc8Grmu-D8fMjloT6hfJCSEuChOHjfm8bR_s71TOVKByXrC687G-Z0tGLhYZkg5Ne2bUrowszXLGunHdHdHboSRdLO2XYU8RsomDwyve5I26MQBJx13jS11Wrblg=="
    ###  list of the dept in error ####
    list_deps_failed = []
    Station_poste.objects.all().delete()

    file_path = config['PATH']['dir']+r"\id_post_failed.log"
    ###  ATTENTION :  The range() function returns a sequence of numbers, starting from 0 by default, and increments by 1 (by default), and stops before a specified number. ####
    for i in range (0o1, 96) :
        print("i dans  MAIN "+str(i))
        dep_id_failed = populate_station_Poste(base_url, api_key, i) 


        ###  if API response failure, obtain failed id_post and try again to insert the same id_post ####
        if len(dep_id_failed) >= 2 :
            ###  wait for sec before try again ####
            print(type(int(config['SLEEP']['sleep_api'])))
            time.sleep(int(config['SLEEP']['sleep_api']))
        ### if second failure, retry for the last time ####
    
            list_deps_failed.append(dep_id_failed)

    


    if len(list_deps_failed) >= 2:
        try:
            with open(file_path, 'w') as file :
                for item in list_deps_failed:
                    file.write(str(item)+'\n')
        except FileExistsError as errf :
            print(f"The file '{file_path}' already exists.")


    print("end of populate table")  


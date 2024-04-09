import sys
import os
# sys.path.append(r"C:\Users\mpayen\GIT2\hydrologie\projet")
script_path = os.path.abspath(__file__)
project_dir = os.path.dirname(os.path.dirname(os.path.dirname(script_path)))
sys.path.append(project_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projet.settings")  

import django
django.setup()

from django.db import models
import pandas as pd
import numpy as np
from projet.classes.station import StationManager
from projet.classes.multipleStation import MultipleStations

import asyncio

Ville = sys.argv[1]
Fleuve = sys.argv[2]


async def getStations_from_WatercourseCity(city, watercourse) :
    """
        Get hydrologic stations and their coordinates for a city and a watercourse given
        Parameters :
            city : name of the city in which we want to study the watercourse
            watercourse : name of the watercourse in question
    """   
    stations_hydro = MultipleStations()
    await stations_hydro.get_watercourse_stations(watercourse)
    communeStation = stations_hydro.get_commune()
    size=len(communeStation)
    list=[]
    for i in range (size):
        if communeStation[i]==city:
            list.append(i)
    code_stations=[]
    coord_stations=[]
    i=0
    for j in list:
        code_stations.append(stations_hydro.stations[j])
        final_station = StationManager(code_stations[i])
        coord_stations.append(final_station.get_coordinates_station())
        i+=1
    return code_stations, coord_stations

code, coord = asyncio.run(getStations_from_WatercourseCity(Ville, Fleuve))
print(code, coord)
from django.shortcuts import render
import os
import asyncio
from django.http import JsonResponse
import json
import pandas as pd
from projet.classes.hubeau import StationManager
from  projet.classes.hubeau import Watercourse


def index(request):


    station = StationManager("O005002001")
    communes= asyncio.run(station.get_commune())

    fleuves_station = Watercourse("----0010")
    fleuves = asyncio.run(fleuves_station.get_fleuves())
    
    return render(request, 'index.html', {'communes': communes, 'fleuves': fleuves})

def submit_data(request):
    if request.method == 'POST':
        ville = request.POST.get('ville', '')
        fleuve = request.POST.get('fleuve', '')
        date = request.POST.get('trip-start', '')

        

        # Répondre avec un message de succès
        return JsonResponse({'message': 'Données soumises avec succès'})
    else:
        # Répondre avec un message d'erreur si la requête n'est pas de type POST
        return JsonResponse({'error': 'La requête doit être de type POST'})



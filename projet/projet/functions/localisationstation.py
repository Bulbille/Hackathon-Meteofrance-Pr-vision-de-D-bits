import folium
import numpy as np
from geopy.distance import great_circle
from folium.plugins import AntPath

def generate_folium_map(stations):
    m = folium.Map(location=[48.8566, 2.3522], zoom_start=5) 

    for station in stations:
        if station.latitude_station and station.longitude_station:
            folium.Marker(
                location=[station.latitude_station, station.longitude_station],
                popup=station.libelle_station
            ).add_to(m)

    return m._repr_html_()

def find_closest_station(current_station, stations):
    min_distance = float('inf')
    closest_station = None
    for station in stations:
        if station != current_station:
            distance = great_circle(
                (station.latitude_station, station.longitude_station),
                (current_station.latitude_station, current_station.longitude_station)
            ).meters
            if distance < min_distance:
                min_distance = distance
                closest_station = station
    return closest_station

def generate_watercourse_map(stations):
    stations_sorted = stations.sort_stations()

    map = stations.create_map(True)
    for index, station in enumerate(stations_sorted):
        if index < len(stations_sorted) - 1:
            next_station = stations_sorted[index + 1]
            line_points = [(station.latitude_station, station.longitude_station), 
                           (next_station.latitude_station, next_station.longitude_station)]
            AntPath(locations=line_points, color="blue", weight=5, opacity=0.8, delay=1000).add_to(map)

    return map._repr_html_()
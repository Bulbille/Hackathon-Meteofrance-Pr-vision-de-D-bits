import requests
from datetime import datetime as dt
import json
import pandas as pd
import csv

def get_weather_data(location, start_date, end_date, granularity, api_key):
    base_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"

    start_date = dt.strptime(start_date, "%Y-%m-%d")
    end_date = dt.strptime(end_date, "%Y-%m-%d")
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    url = f"{base_url}/{location}/{start_date_str}/{end_date_str}?key={api_key}&include={granularity}" 
    response = requests.get(url)
    
    if response.status_code == 200:
        weather_data = response.json()
        return weather_data
    else:
        print(response.status_code)
        return None

if __name__ == "__main__":
    location = input("Entrez la localisation : ")  
    start_date = input("Entrez la date de début (YYYY-MM-DD) : ")  
    end_date = input("Entrez la date de fin (YYYY-MM-DD) : ")  
    api_key = input("Entrez votre clé API : ")

    weather_data = get_weather_data(location, start_date, end_date, api_key)
    
    if weather_data:
        filename = f"{location}_{start_date}_{end_date}_weather_data.json"

        with open(filename, "w") as json_file:
            json.dump(weather_data, json_file)
            
        with open(filename, 'r') as json_file:
            data = json.load(json_file)
        days_data = data.get("days", [])
        df = pd.DataFrame(days_data)
        df.to_csv(f"{location}_{start_date}_{end_date}_weather_data.csv", index=False)

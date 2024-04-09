
import pandas as pd
import requests
import warnings
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

pd.set_option('display.max_columns', None)

# Différents liens pour récupérer les données  
url_sites = "https://hubeau.eaufrance.fr/api/v1/hydrometrie/referentiel/sites"
url_observations_tr = "https://hubeau.eaufrance.fr/api/v1/hydrometrie/observations_tr?size=20000"
url_stations = "https://hubeau.eaufrance.fr/api/v1/hydrometrie/referentiel/stations"
url_obs_elab = 'https://hubeau.eaufrance.fr/api/v1/hydrometrie/obs_elab'

def get_data(url, params=None):
    """
    Récupère des données paginées à partir d'une URL et retourne un DataFrame.

    Args:
        url (str): L'URL de l'API paginée.

    Returns:
        pandas.DataFrame: Un DataFrame contenant toutes les données récupérées.

    Example:
        df_sites = get_data(url_sites)
    """
    df_name = pd.DataFrame()
    while url:
        response = requests.get(url,params=params, verify=False)
        data = response.json()
        new_data = data["data"]
        url = data.get("next")  
        new_df = pd.DataFrame(new_data)
        df_name = pd.concat([df_name, new_df], ignore_index=True)
    return df_name

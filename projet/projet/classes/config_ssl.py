import requests
from requests.adapters import HTTPAdapter
import ssl

class NoSSLVerification(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        kwargs['ssl_context'] = context
        return super(NoSSLVerification, self).init_poolmanager(*args, **kwargs)

urls = [
    "https://public-api.meteofrance.fr/public/",
    "https://hubeau.eaufrance.fr/api/",
    "https://services.sandre.eaufrance.fr/geo/",
    "https://weather.visualcrossing.com/",
    "https://api.sandre.eaufrance.fr/"
]

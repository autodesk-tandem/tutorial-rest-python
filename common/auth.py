from typing import List
import requests

def create_token(client_id: str, client_secret: str, scope: List[str]) -> str:
    """ Creates 2-legged authorization token. """

    options = {
        'grant_type': 'client_credentials',
        'scope': ' '.join(scope)
    }

    response = requests.post('https://developer.api.autodesk.com/authentication/v2/token', params=options, auth=(client_id, client_secret))
    data = response.json()   
    return data.get('access_token')
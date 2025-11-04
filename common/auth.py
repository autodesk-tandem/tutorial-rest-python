from typing import List, Literal
import requests

def create_token(client_id: str, client_secret: str, scope: List[str], env: Literal['prod', 'stg'] = 'prod') -> str:
    """ Creates 2-legged authorization token. """

    base_url = {
        'prod': 'https://developer.api.autodesk.com',
        'stg': 'https://developer-stg.api.autodesk.com'
    }.get(env)
    options = {
        'grant_type': 'client_credentials',
        'scope': ' '.join(scope)
    }
    url = f'{base_url}/authentication/v2/token'
    response = requests.post(url, params=options, auth=(client_id, client_secret))
    data = response.json()
    return data.get('access_token')
"""
This example demonstrates how to list details of the facility. It prints original storage of model document in ACC/Docs.
The sample uses Data Management API to get project and item data.
    
It uses 2-legged authentication - this requires that application is added to the account as service. The application also
needs to be whitelisted in ACC/Docs.
"""
import requests
from typing import Any, Tuple

from common.auth import create_token
from common.tandemClient import TandemClient
from common.encoding import decode_urn

# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
FACILITY_URN = 'YOUR_FACILITY_URN'

def get_item(token: str, project_id: str, item_id:str) -> Any:
    """
    Get item data using Data Management API
    """

    headers = {
        'Authorization': f'Bearer {token}'
    }
    input = {
        'jsonapi': {
            'version': '1.0'
        },
        'data': {
            'type': 'commands',
            'attributes': {
                'extension': {
                    'type': 'commands:autodesk.core:ListItems',
                    'version': '1.1.0',
                    'data': {
                        'includePathInProject': True
                    }
                }
            },
            'relationships': {
                'resources': {
                    'data': [
                        {
                            'id': item_id,
                            'type': 'items'
                        }
                    ]
                }
            }
        }
    }
    url = f'https://developer.api.autodesk.com/data/v1/projects/{project_id}/commands'
    response = requests.post(url, headers=headers, json=input)
    if response.status_code != 200:
        raise Exception(f"Failed to get item details: {response.status_code} - {response.text}")
    result = response.json()
    return result.get('data').get('relationships').get('resources').get('data')[0]

def get_project(token: str, account_id: str, project_id: str) -> Any:
    """
    Get project data using Data Management API
    """

    headers = {
        'Authorization': f'Bearer {token}'
    }
    url = f'https://developer.api.autodesk.com/project/v1/hubs/{account_id}/projects/{project_id}'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to get project details: {response.status_code} - {response.text}")
    result = response.json()
    return result.get('data')

def parse_urn(urn: str) -> Tuple[str, str] | None:
    """
    Converts URN to item ID
    """

    text = decode_urn(urn)
    items = text.split(':')
    if len(items) < 4:
        return None
    bucket_key = f'{items[0]}:{items[1]}'
    lineage_id = items[3]
    index = lineage_id.find('?version=')
    if index != -1:
        lineage_id = lineage_id[:index]
    if lineage_id.startswith('vf.'):
        lineage_id = lineage_id[3:]
    result = f'{bucket_key}:dm.lineage:{lineage_id}'
    return (result, text)

def main():
    # Start
    # STEP 1 - obtain token. The sample uses 2-legged token but it would also work
    # with 3-legged token assuming that user has access to the facility
    token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read'])
    with TandemClient(lambda: token) as client:
        # STEP 2 - get facility
        facility = client.get_facility(FACILITY_URN)
        # STEP 3 - iterate through models
        for l in facility.get('links'):
            model_id = l.get('modelId')
            # STEP 4 - get model properties and convert URN to item ID
            model_props = client.get_model_props(model_id)
            urn = model_props.get('dataSource').get('forgeUrn')
            # skip internal models - i.e. default model
            if urn == 'internal':
                continue
            (item_id, version_id) = parse_urn(urn)
            # check if item_id points to ACC/Docs storage - it starts with 'urn:adsk.wip' prefix
            if item_id is None or not item_id.startswith('urn:adsk.wip'):
                continue
            # STEP 5 - get project data
            project = get_project(
                token,
                model_props.get('dataSource').get('docsAccountId'),
                model_props.get('dataSource').get('docsProjectId')
            )
            # STEP 6 - get item data
            item = get_item(
                token,
                model_props.get('dataSource').get('docsProjectId'),
                item_id
            )
            print(f'{l.get('label')}')
            print(f'  {project.get('attributes').get('name')}')
            print(f'    {item.get('meta').get('attributes').get('pathInProject')}/{item.get('meta').get('attributes').get('displayName')}')
            print(f'  needs update: {item.get('meta').get('relationships').get('tip').get('data').get('id') != version_id}')

if __name__ == '__main__':
    main()

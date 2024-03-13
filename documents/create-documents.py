"""
This example demonstrates how to create linked documents for given facility.

It uses 2-legged authentication - this requires that application is added to facility as service.
It's also using same token to access ACC/BIM360 so it's necessary to whitelist aplication in ACC/BIM360.
"""
import requests

from common.auth import create_token
from common.tandemClient import TandemClient

# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
FACILITY_URN = 'YOUR_FACILITY_URN'
ACC_ACCOUNT_ID = 'YOUR_ACC_ACCOUNT_ID'
ACC_PROJECT_ID = 'YOUR_ACC_PROJECT_ID'
ACC_FOLDER_ID = 'YOUR_ACC_FOLDER_ID'

def get_documents(token, project_id, folder_id):
    url = f'https://developer.api.autodesk.com/data/v1/projects/{project_id}/folders/{folder_id}/contents'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    items = response.json().get('data')
    for item in items:
        yield item.get('attributes').get('displayName'), item.get('id'), item.get('relationships').get('tip').get('data').get('id')


def main():
    # Start
    # STEP 1 - obtain token. The sample uses 2-legged token but it would also work
    # with 3-legged token assuming that user has access to the facility
    token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read', 'data:write'])
    with TandemClient(lambda: token) as client:
        # STEP 2 - get facility
        facility = client.get_facility(FACILITY_URN)
        # STEP 3 - get documents from ACC/BIM360
        docs = get_documents(token, ACC_PROJECT_ID, ACC_FOLDER_ID)
        doc_inputs = []

        for name, id, version in docs:
            # STEP 4 - filter out documents which are already imported into facility
            doc = next(d for d in facility.get('docs') if d.get('accAccountId') == ACC_ACCOUNT_ID
                        and d.get('accProjectId') == ACC_PROJECT_ID
                        and d.get('accLineage') == id
                        and d.get('accVersion') == version)
            if doc is not None:
                continue
            doc_inputs.append({
                'accAccountId': ACC_ACCOUNT_ID,
                'accProjectId': ACC_PROJECT_ID,
                'accLineage': id,
                'accVersion': version,
                'name': name
            })
        if len(doc_inputs) == 0:
            return
        # STEP 5 - import documents to facility & print out their name
        results = client.create_documents(FACILITY_URN, doc_inputs)
        print(results.get('status'))
        for doc in results.get('data'):
            print(f'{doc.get('name')}:{doc.get('id')}')


if __name__ == '__main__':
    main()

"""
This example demonstrates how to create generic asset (w/o geometry).
The facility is using REC Sample template and new asset is Lighting Equipment.

It uses 2-legged authentication - this requires that application is added to facility as service.
"""

from common.auth import create_token
from common.tandemClient import TandemClient
from common.constants import (
    QC_KEY,
    QC_NAME,
    QC_ONAME
)


# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
FACILITY_URN = 'YOUR_FACILITY_URN'
NAME = 'Delete me'


def main():
    # Start
    # STEP 1 - obtain token to authenticate subsequent API calls
    token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read', 'data:write'])
    with TandemClient(lambda: token) as client:
        # STEP 2 - get facility
        facility = client.get_facility(FACILITY_URN)
        deleted_element_count = 0
        # STEP 3 - iterate through facility models and process elements
        for l in facility.get('links'):
            model_id = l.get('modelId')
            # STEP 4 - get elements and find one with given name
            elements = client.get_elements(model_id)
            elements_to_delete = []

            for element in elements:
                name = element.get(QC_ONAME) or element.get(QC_NAME)
                if name == NAME:
                    elements_to_delete.append(element.get(QC_KEY))
            # STEP 5 - delete elements
            if len(elements_to_delete) > 0:
                print(f'Deleting elements: {len(elements_to_delete)}')
                client.delete_elements(model_id, elements_to_delete, 'element-delete')
                deleted_element_count += len(elements_to_delete)
        print(f'Total number of deleted elements: {deleted_element_count}')

if __name__ == '__main__':
    main()

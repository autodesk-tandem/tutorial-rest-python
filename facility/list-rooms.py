"""
This example demonstrates how to list all rooms from facility.

It uses 2-legged authentication - this requires that application is added to facility as service.
"""

from common.auth import create_token
from common.tandemClient import TandemClient
from common.constants import (
    QC_ELEVATION,
    QC_NAME
)

# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
FACILITY_URN = 'YOUR_FACILITY_URN'

def main():
    # Start
    # STEP 1 - obtain token. The sample uses 2-legged token but it would also work
    # with 3-legged token assuming that user has access to the facility
    token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read'])
    with TandemClient(lambda: token) as client:
        # STEP 2 - get facility
        facility = client.get_facility(FACILITY_URN)
        # STEP 3 - iterate through facility models and get room elements from the model
        for l in facility.get('links'):
            model_id = l.get('modelId')
            rooms = client.get_rooms(model_id)
            # STEP 4 - iterate through rooms and print their names.
            for room in rooms:
                print(f'{room.get(QC_NAME)}')


if __name__ == '__main__':
    main()

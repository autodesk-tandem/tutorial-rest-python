"""
This example demonstrates how to list all levels from facility.

It uses 2-legged authentication - this requires that application is added to facility as service.
"""

from common.auth import create_token
from common.tandemClient import TandemClient
from common.constants import (
    QC_NAME,
    QC_ONAME
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
        # STEP 3 - iterate through facility models and collect systems
        for l in facility.get('links'):
            model_id = l.get('modelId')
            systems = client.get_systems(model_id)
            # STEP 4 - iterate through systems and print their names
            for system in systems:
                name = system.get(QC_ONAME)
                if name is None:
                    name = system.get(QC_NAME)
                print(f'{name}')


if __name__ == '__main__':
    main()

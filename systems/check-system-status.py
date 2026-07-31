"""
This example demonstrates how to check state of systems in the  facility.

It uses 2-legged authentication - this requires that application is added to facility as service.
"""

from common.auth import create_token
from common.tandemClient import TandemClient
from common.constants import (
    QC_KEY,
    QC_NAME,
    QC_ONAME,
    QC_PARENT,
    QC_STATE,
    SYSTEMS_STATE_DIRTY
)
from common.utils import get_default_model

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
        # STEP 2 - get facility & template
        facility = client.get_facility(FACILITY_URN)
        # STEP 3 - iterate through systems and check their staus
        default_model = get_default_model(FACILITY_URN, facility)
        if default_model is None:
            raise Exception('Default model not found')
        systems = client.get_systems(default_model.get('modelId'))
        for system in systems:
            key = system.get(QC_KEY)
            name = system.get(QC_ONAME) or system.get(QC_NAME)
            parent = system.get(QC_PARENT)
            # skip subsystems
            if parent is not None:
                continue
            print(f'Processing system: {name} ({key})')
            # STEP 4 - check state of the system
            state = system.get(QC_STATE)
            if state == SYSTEMS_STATE_DIRTY:
                print(f'  System is in dirty state. It needs to be updated.')
        print('done')

if __name__ == '__main__':
    main()

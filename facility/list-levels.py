"""
This example demonstrates how to list all levels from facility.

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
        # STEP 3 - iterate through facility models and print level name + elevation
        for l in facility.get('links'):
            model_id = l.get('modelId')
            schema = client.get_model_schema(model_id)
            levels = client.get_levels(model_id)
            for level in levels:
                # STEP 4 - find elevation property
                prop_def = next((p for p in schema.get('attributes') if p.get('id') == QC_ELEVATION), None)
                if prop_def is None:
                    continue
                elevation = level.get(prop_def.get('id'))
                # STEP 5 - print out level name and elevation
                print(f'{level.get(QC_NAME)}:{elevation}')


if __name__ == '__main__':
    main()

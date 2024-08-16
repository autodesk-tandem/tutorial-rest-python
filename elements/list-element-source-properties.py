"""
This example demonstrates how to get read source properties (i.e. from Revit). Those properties are available as Source family.

It uses 2-legged authentication - this requires that application is added to facility as service.
"""

from common.auth import create_token
from common.tandemClient import TandemClient
from common.constants import (
    COLUMN_FAMILIES_SOURCE,
    COLUMN_FAMILIES_STANDARD,
    QC_KEY,
    QC_NAME,
    QC_ONAME
)


# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
FACILITY_URN = 'YOUR_FACILITY_URN'


def main():
    # Start
    # STEP 1 - obtain token to authenticate subsequent API calls
    token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read'])
    with TandemClient(lambda: token) as client:
        # STEP 2 - get facility
        facility = client.get_facility(FACILITY_URN)
        # STEP 3 - iterate through facility models and process elements
        for l in facility.get('links'):
            model_id = l.get('modelId')
            schema = client.get_model_schema(model_id)
            # STEP 4 - find property
            prop_def = next((p for p in schema.get('attributes') if p['fam'] == COLUMN_FAMILIES_SOURCE and p['category'] == 'Identity Data' and p['name'] == 'Type Name'), None)

            if prop_def is None:
                continue
            # STEP 5 - get elements and print out property value
            elements = client.get_elements(model_id, column_families=[ COLUMN_FAMILIES_STANDARD, COLUMN_FAMILIES_SOURCE ])

            for element in elements:
                prop = element.get(prop_def['id'])
                if prop is None:
                    continue
                name = element.get(QC_ONAME) or element.get(QC_NAME)
                print(f'{name}: {element.get(QC_KEY)}')
                print(f'  {prop}')

if __name__ == '__main__':
    main()

"""
This example demonstrates how to list properties of the facility.
    
It uses 2-legged authentication - this requires that application is added to the account as service.
"""
from common.constants import (
    COLUMN_FAMILIES_DTPROPERTIES,
    COLUMN_FAMILIES_STANDARD,
    ELEMENT_FLAGS_DOCUMENT_ROOT,
    QC_ELEMENT_FLAGS
)
from common.auth import create_token
from common.tandemClient import TandemClient
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
        # STEP 2 - get facility and default model
        facility = client.get_facility(FACILITY_URN)
        default_model = get_default_model(FACILITY_URN, facility)
        if default_model is None:
            print('Default model not found')
            return
        default_model_id = default_model.get('modelId')
        # STEP 3 - get model schema
        schema = client.get_model_schema(default_model_id)
        # STEP 4 - get elements from the model, find root element
        elements = client.get_elements(default_model_id, column_families=[COLUMN_FAMILIES_STANDARD, COLUMN_FAMILIES_DTPROPERTIES])
        root_element = next((e for e in elements if e.get(QC_ELEMENT_FLAGS) == ELEMENT_FLAGS_DOCUMENT_ROOT), None)
        if root_element is None:
            print('Root element not found')
            return
        # STEP 5 - print properties of the facility
        print('Facility properties:')
        count = 0

        for id, value in root_element.items():
            if not id.startswith(f'{COLUMN_FAMILIES_DTPROPERTIES}:'):
                continue
            prop_def = next((a for a in schema.get('attributes', []) if a.get('id') == id), None)
            if prop_def is None:
                continue
            print(f'  {prop_def.get('name')}: {value}')
            count += 1
        print(f'Total properties: {count}')

if __name__ == '__main__':
    main()

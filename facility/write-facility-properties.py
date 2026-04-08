"""
This example demonstrates how to update properties of the facility.
    
It uses 2-legged authentication - this requires that application is added to the account as service.
"""
from common.constants import (
    COLUMN_FAMILIES_DTPROPERTIES,
    COLUMN_FAMILIES_STANDARD,
    ELEMENT_FLAGS_DOCUMENT_ROOT,
    MUTATE_ACTIONS_INSERT_IF_DIFFERENT,
    QC_ELEMENT_FLAGS,
    QC_KEY
)
from common.auth import create_token
from common.tandemClient import TandemClient
from common.utils import get_default_model

# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
FACILITY_URN = 'YOUR_FACILITY_URN'

PROPERTY_NAME = 'My custom property'
PROPERTY_VALUE = 1000

def main():
    # Start
    # STEP 1 - obtain token. The sample uses 2-legged token but it would also work
    # with 3-legged token assuming that user has access to the facility
    token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read', 'data:write'])
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
        # STEP 5 - add predefined property to the root element
        prop_def = next((a for a in schema.get('attributes', []) if a.get('name', None) == PROPERTY_NAME), None)

        if prop_def is None:
            print(f'Property "{PROPERTY_NAME}" not found in schema')
            return
        muts = [
            [
                MUTATE_ACTIONS_INSERT_IF_DIFFERENT,
                prop_def.get('fam'),
                prop_def.get('col'),
                PROPERTY_VALUE
            ]
        ]
        client.mutate_elements(default_model_id, [root_element[QC_KEY]], muts, 'Update facility properties')

if __name__ == '__main__':
    main()

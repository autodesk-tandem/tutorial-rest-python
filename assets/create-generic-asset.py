"""
This example demonstrates how to create generic asset (w/o geometry).
The facility is using REC Sample template and new asset is Lighting Equipment.

It uses 2-legged authentication - this requires that application is added to facility as service.
"""

from common.auth import create_token
from common.tandemClient import TandemClient
from common.utils import get_default_model, match_classification
from common.constants import (
    COLUMN_FAMILIES_STANDARD,
    COLUMN_NAMES_CATEGORY_ID,
    COLUMN_NAMES_CLASSIFICATION,
    COLUMN_NAMES_ELEMENT_FLAGS,
    COLUMN_NAMES_NAME,
    COLUMN_NAMES_UNIFORMAT_CLASS,
    ELEMENT_FLAGS_GENERIC_ASSET,
    MUTATE_ACTIONS_INSERT
)


# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
FACILITY_URN = 'YOUR_FACILITY_URN'
CLASSIFICATION = 'Lighting Equipment'
ASSEMBLY_CODE = 'D5040.50' # Lighting Fixtures
CATEGORY = 1120 # Lighting Fixtures


def main():
    # Start
    # STEP 1 - obtain token to authenticate subsequent API calls
    token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read', 'data:write'])
    with TandemClient(lambda: token) as client:
        # STEP 2 - get facility
        facility = client.get_facility(FACILITY_URN)
        default_model = get_default_model(FACILITY_URN, facility)

        if default_model is None:
            raise Exception('Default model not found')
        # STEP 3 - get facility template
        template = client.get_facility_template(FACILITY_URN)
        # STEP 4 - get suitable parameters for classification
        classification = next((c for c in template.get('classification').get('rows') if c[1] == CLASSIFICATION), None)
        if classification is None:
            raise Exception('Classification not found')
        pset = next((p for p in template.get('psets') if p.get('name') == template.get('name')), None)
        class_parameters = list(filter(lambda item: any(match_classification(classification[0], c) for c in item.get('applicationFilters').get('userClass')), pset.get('parameters')))
        schema = client.get_model_schema(default_model.get('modelId'))
        # STEP 5 - collect inputs for new asset
        inputs = {
            'muts': [
                [
                    MUTATE_ACTIONS_INSERT,
                    COLUMN_FAMILIES_STANDARD,
                    COLUMN_NAMES_NAME,
                    'Test Asset'
                ],
                [
                    MUTATE_ACTIONS_INSERT,
                    COLUMN_FAMILIES_STANDARD,
                    COLUMN_NAMES_ELEMENT_FLAGS,
                    ELEMENT_FLAGS_GENERIC_ASSET
                ],
                [
                    MUTATE_ACTIONS_INSERT,
                    COLUMN_FAMILIES_STANDARD,
                    COLUMN_NAMES_CLASSIFICATION,
                    classification[0]
                ],
                [
                    MUTATE_ACTIONS_INSERT,
                    COLUMN_FAMILIES_STANDARD,
                    COLUMN_NAMES_CATEGORY_ID,
                    CATEGORY
                ],
                [
                    MUTATE_ACTIONS_INSERT,
                    COLUMN_FAMILIES_STANDARD,
                    COLUMN_NAMES_UNIFORMAT_CLASS,
                    ASSEMBLY_CODE
                ]
            ],
            'desc': 'Create asset'
        }
        # STEP 6 - add asset properties based on ma below (property name -> value)
        asset_properties = {
            'Asset Tag': '12345',
            'Model Number': 'ABC',
            'IP Address': '10.0.0.0',
            'Serial Number': '12345'
        }
        for item in asset_properties:
            value = asset_properties[item]
            class_parameter = next((p for p in class_parameters if p.get('name') == item), None)
            if class_parameter is None:
                continue
            param = next((p for p in schema.get('attributes') if p.get('name') == class_parameter.get('name') and p.get('category') == class_parameter.get('category')), None)
            if param is None:
                continue
            inputs['muts'].append([
                MUTATE_ACTIONS_INSERT,
                param.get('fam'),
                param.get('col'),
                value
            ])
        # STEP 7 - create new asset. Note that generic asset should be added to default model only.
        result = client.create_element(default_model.get('modelId'), inputs)

        print(f'New asset created: ${result.get('key')}')

if __name__ == '__main__':
    main()

"""
This example demonstrates how to assign classification to the element.
The scenario is quite simple - there is hardcoded mapping between element name
and classification. I can be used as reference sample in case that more
advanced logic is needed.

It uses 2-legged authentication - this requires that application is added to facility as service.
"""

from common.auth import create_token
from common.tandemClient import TandemClient
from common.constants import (
    COLUMN_FAMILIES_STANDARD,
    COLUMN_NAMES_OCLASSIFICATION,
    MUTATE_ACTIONS_INSERT,
    QC_CLASSIFICATION,
    QC_OCLASSIFICATION,
    QC_KEY,
    QC_NAME
)

# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
FACILITY_URN = 'YOUR_FACILITY_URN'

def main():
    # Start
    # STEP 1 - obtain token to authenticate subsequent API calls
    token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read', 'data:write'])
    with TandemClient(lambda: token) as client:
        # STEP 2 - get facility & facility template
        facility = client.get_facility(FACILITY_URN)
        facility_template = client.get_facility_template(FACILITY_URN)
        # this defines mapping between element name and classification
        element_class_map = {
            'Door - Interior - Double' : 'Interior Doors',
            'Door - Interior - Single' : 'Interior Doors',
            'Door - Exterior - Double' : 'Exterior Doors',
            'Door - Exterior - Single' : 'Exterior Doors'
        }
        # STEP 3 - build map between element name and classification id
        class_map = {}
        for name in element_class_map.keys():
            class_name = element_class_map[name]
            class_data = next(c for c in facility_template['classification']['rows'] if c[1] == class_name)
            if class_data is None:
                continue
            class_map[name] = class_data[0]
        # STEP 4 - iterate through facility models and apply classification based on mapping
        for l in facility.get('links'):
            keys = []
            mutations = []
            model_id = l.get('modelId')
            elements = client.get_elements(model_id)
            for element in elements:
                name = element[QC_NAME]
                class_id = class_map.get(name)
                if class_id is None:
                    continue
                # we don't want to apply same classification again
                if element.get(QC_CLASSIFICATION) == class_id or element.get(QC_OCLASSIFICATION) == class_id:
                    continue
                # store keys and mutations
                keys.append(element[QC_KEY])
                mutations.append([
                    MUTATE_ACTIONS_INSERT,
                    COLUMN_FAMILIES_STANDARD,
                    COLUMN_NAMES_OCLASSIFICATION,
                    class_id
                ])
            if len(keys) == 0:
                continue
            # STEP 5 - apply changes
            client.mutate_elements(model_id, keys, mutations, 'Update classification')
            print(f'Updated elements: {len(keys)}')


if __name__ == '__main__':
    main()

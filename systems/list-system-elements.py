"""
This example demonstrates how to get systems from facility and locate associated elements.

It uses 2-legged authentication - this requires that application is added to facility as service.
"""

from common.auth import create_token
from common.encoding import to_system_id
from common.tandemClient import TandemClient
from common.constants import (
    COLUMN_FAMILIES_STANDARD,
    COLUMN_FAMILIES_SYSTEMS,
    QC_KEY,
    QC_NAME,
    QC_ONAME
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
        # STEP 2 - get facility
        facility = client.get_facility(FACILITY_URN)
        default_model = get_default_model(FACILITY_URN, facility)
        # STEP 3 - iterate through systems and collect their data: id => (name, key)
        
        systems = client.get_systems(default_model.get('modelId'))
        system_map = {}
        for system in systems:
            name = system.get(QC_ONAME)
            if name is None:
                name = system.get(QC_NAME)
            # encode element key to system id
            key = system.get(QC_KEY)
            system_id = to_system_id(key)
            system_map[system_id] = (name, key)
        # STEP 4 - iterate through model elements and store their relationship to system
        # in dictionary: id => (model, key, name)
        system_elements_map = {}

        for l in facility.get('links'):
            model_id = l.get('modelId')
            elements = client.get_elements(model_id, column_families=[ COLUMN_FAMILIES_STANDARD, COLUMN_FAMILIES_SYSTEMS ])
            for element in elements:
                for item in element:
                    if item.startswith(f'{COLUMN_FAMILIES_SYSTEMS}:'):
                        system_id = item.replace(f'{COLUMN_FAMILIES_SYSTEMS}:', '')
                        element_list = system_elements_map.get(system_id)

                        if element_list is None:
                            element_list = []
                            system_elements_map[system_id] = element_list
                        element_list.append((model_id, element.get(QC_KEY), element.get(QC_NAME)))
        # STEP 5 - print out system names and associated elements
        for system_id in system_map:
            system_name, system_key = system_map[system_id]
            system_elements = system_elements_map.get(system_id)
            if system_elements_map is None:
                continue
            print(f'{system_name}: {len(system_elements)}')
            for model_id, element_key, element_name in system_elements:
                print(f'  {element_name}')


if __name__ == '__main__':
    main()

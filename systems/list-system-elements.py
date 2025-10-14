"""
This example demonstrates how to get systems from facility and locate associated elements.

It uses 2-legged authentication - this requires that application is added to facility as service.
"""

import re

from common.auth import create_token
from common.encoding import to_system_id
from common.tandemClient import TandemClient
from common.constants import (
    COLUMN_FAMILIES_STANDARD,
    COLUMN_FAMILIES_SYSTEMS,
    ELEMENT_FLAGS_DELETED,
    ELEMENT_FLAGS_SYSTEM,
    QC_ELEMENT_FLAGS,
    QC_KEY,
    QC_NAME,
    QC_ONAME,
    QC_PARENT,
    QC_SYSTEM_CLASS,
    QC_OSYSTEM_CLASS
)
from common.encoding import (
    to_full_key
)
from common.utils import (
    get_default_model,
    system_class_to_list
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
        default_model = get_default_model(FACILITY_URN, facility)
        if default_model is None:
            raise Exception('Default model not found')
        # STEP 3 - iterate through systems and collect their data: id => (name, key)
        
        systems = client.get_systems(default_model.get('modelId'))
        system_map = {}

        for system in systems:
            key = to_full_key(system.get(QC_KEY), True)
            name = system.get(QC_ONAME) or system.get(QC_NAME)
            parent = system.get(QC_PARENT)
            if parent is not None:
                continue
            # encode element key to system id
            system_id = to_system_id(key)
            filter = system.get(QC_OSYSTEM_CLASS) or system.get(QC_SYSTEM_CLASS)
            system_map[system_id] = (name, key, filter)
            
        # STEP 4 - iterate through model elements and store their relationship to system
        system_elements_map = {}
        system_class_map = {}

        for l in facility.get('links'):
            model_id = l.get('modelId')
            elements = client.get_elements(model_id, column_families=[ COLUMN_FAMILIES_STANDARD, COLUMN_FAMILIES_SYSTEMS ])
            for element in elements:
                element_flags = element.get(QC_ELEMENT_FLAGS)
                if element_flags == ELEMENT_FLAGS_DELETED or element_flags == ELEMENT_FLAGS_SYSTEM:
                    continue
                name = element.get(QC_ONAME) or element.get(QC_NAME)
                key = element.get(QC_KEY)
                # check if element has system class assigned
                element_class = element.get(QC_OSYSTEM_CLASS)
                if element_class is None:
                    element_class = element.get(QC_SYSTEM_CLASS)
                if element_class is None:
                    continue
                element_class_names = system_class_to_list(element_class)

                for item in element:
                    # need to handle both fam:col and fam:!col formats
                    match = re.match(r'^([^:]+):!?(.+)$', item)
                    if match is None:
                        continue
                    family, system_id = match.groups()
                    if family == COLUMN_FAMILIES_SYSTEMS:
                        system = system_map.get(system_id)
                        if system is None:
                            continue
                        filter = system[2]
                        class_names = system_class_map.get(filter, None)

                        if class_names is None:
                            class_names = system_class_to_list(filter)
                            system_class_map[filter] = class_names
                        # if system has filter, then check that element matches it
                        matches = any(name in class_names for name in element_class_names)
                        if matches:
                            # use set to handle possible duplicates
                            element_list = system_elements_map.get(system_id, set())
                            element_list.add(key)
                            system_elements_map[system_id] = element_list
        # STEP 5 - print out system names and number of associated elements
        for system_id, system in system_map.items():
            system_elements = system_elements_map.get(system_id, None)
            if system_elements is None:
                continue
            print(f'{system[0]} ({system_id})')
            print(f'  Element count: {len(system_elements)}')


if __name__ == '__main__':
    main()

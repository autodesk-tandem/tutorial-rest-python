"""
This example demonstrates how to list all systems from the facility.

It uses 2-legged authentication - this requires that application is added to facility as service.
"""

from typing import Any
import re

from common.auth import create_token
from common.tandemClient import TandemClient
from common.constants import (
    QC_KEY,
    QC_NAME,
    QC_ONAME,
    QC_PARENT,
    QC_SETTINGS
)
from common.encoding import (
    decode_text_to_object,
    to_full_key,
    to_system_id
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
        facility_template = client.get_facility_template(FACILITY_URN)
        # STEP 3 - get default model
        default_model = get_default_model(FACILITY_URN, facility)
        if default_model is None:
            raise Exception('Default model not found')
        # STEP 4 - get systems and build hierarchy of systems and subsystems
        systems = []
        subsystems = []

        items = client.get_systems(default_model.get('modelId'))
        for item in items:
            key = item.get(QC_KEY)
            name = item.get(QC_ONAME) or item.get(QC_NAME)
            parent = item.get(QC_PARENT)
            # STEP 5 - if item has parent then it is subsystem - decode its parameters
            # using facility template to get parameter names
            if parent is None:
                full_key = to_full_key(key, True)
                systems.append({
                    'name': name,
                    'key': key,
                    'systemId': to_system_id(full_key)
                })
            else:
                parameters = get_subsystem_parameters(item.get(QC_SETTINGS), facility_template)
                subsystems.append({
                    'name': name,
                    'key': key,
                    'parent': parent,
                    'parameters': parameters
                })
        # STEP 6 - print systems and their subsystems
        systems.sort(key=lambda x: x.get('name'))
        for system in systems:
            print(f'System: {system.get("name")} ({system.get("systemId")})')
            items = [s for s in subsystems if s.get('parent') == system.get('key')]
            for item in items:
                print(f'  Subsystem: {item.get("name")}')
                for parameter in item.get('parameters', []):
                    print(f'    {parameter.get("name")}: {parameter.get("value")}')
        print('done')

def get_subsystem_parameters(encoded_settings: str, facility_template: Any) -> list[dict[str, Any]]:
    """
    Utility function to decode subsystem parameters using facility template.
    """
    
    parameters = []

    try:
        config = decode_text_to_object(encoded_settings)

        for key, value in config.items():
            match = re.match(r'^\[(.+?)\]\[(.+?)\]$', key)

            if not match:
                continue
            uuid = match.group(1)
            param = next(
                (
                    p
                    for pset in facility_template.get('psets', [])
                    for p in pset.get('parameters', [])
                    if p.get('uuid') == uuid
                ),
                None
            )
            if param is not None:
                parameters.append({
                    'name': param.get('name'),
                    'uuid': uuid,
                    'value': value
                })

    except Exception as err:
        print('Error decoding parameters', err)
    return parameters

if __name__ == '__main__':
    main()

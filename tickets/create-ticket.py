"""
This example demonstrates how to create ticket using REST API. The ticket
is assigned to specified asset.

It uses 2-legged authentication - this requires that application is added
to facility as service.
"""
from datetime import datetime, timezone

from common.auth import create_token
from common.tandemClient import TandemClient
from common.constants import (
    COLUMN_FAMILIES_REFS,
    COLUMN_FAMILIES_STANDARD,
    COLUMN_FAMILIES_XREFS,
    COLUMN_NAMES_ELEMENT_FLAGS,
    COLUMN_NAMES_LEVEL,
    COLUMN_NAMES_NAME,
    COLUMN_NAMES_OPEN_DATE,
    COLUMN_NAMES_PARENT,
    COLUMN_NAMES_PRIORITY,
    COLUMN_NAMES_ROOMS,
    ELEMENT_FLAGS_TICKET,
    MUTATE_ACTIONS_INSERT,
    QC_ELEMENT_FLAGS,
    QC_KEY,
    QC_LEVEL,
    QC_OLEVEL,
    QC_NAME,
    QC_ONAME,
    QC_XROOMS,
    QC_OXROOMS
)
from common.encoding import decode_xref_key, to_full_key, to_xref_key
from common.utils import get_default_model, is_logical_element

# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
FACILITY_URN = 'YOUR_FACILITY_URN'

# Specify ticket name according to your conventions
TICKET_NAME = 'YOUR_TICKET_NAME'
# Name of the asset to search for
ASSET_NAME = 'YOUR_ASSET_NAME'

def main():
    # Start
    # STEP 1 - obtain token. The sample uses 2-legged token but it would also work
    # with 3-legged token assuming that user has access to the facility
    token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read', 'data:write'])
    with TandemClient(lambda: token) as client:
        # STEP 2 - get facility and default model.
        facility = client.get_facility(FACILITY_URN)
        default_model = get_default_model(FACILITY_URN, facility)
        if default_model is None:
            raise Exception('Unable to find default model')
        # STEP 3 - find asset by name. In case when there is multiple assets with same name the first one is selected.
        xref = None

        for link in facility.get('links', []):
            model_id = link.get('modelId')
            elements = client.get_elements(model_id)

            for element in elements:
                name = element.get(QC_ONAME) or element.get(QC_NAME)

                if name == ASSET_NAME:
                    element_flags = element.get(QC_ELEMENT_FLAGS)
                    key = element.get(QC_KEY)
                    # create xref key of an asset
                    xref = to_xref_key(model_id, to_full_key(key, is_logical_element(element_flags)))
                    break
            # element found - exit loop
            if xref is not None:
                break
        if xref is None:
            raise Exception(f'Unable to find asset with name: {ASSET_NAME}')
        # STEP 4 - get rooms and levels from parent asset
        model_id, element_key = decode_xref_key(xref)
        rooms_ids = None
        level_id = None

        if (model_id is not None) and (element_key is not None):
            parent_element = client.get_element(model_id, element_key,
                                                column_families=[COLUMN_FAMILIES_STANDARD, COLUMN_FAMILIES_REFS, COLUMN_FAMILIES_XREFS])
            rooms_ids = parent_element.get(QC_OXROOMS, None)
            if rooms_ids is None:
                rooms_ids =  parent_element.get(QC_XROOMS, None)
            # STEP 5 - find level by name in default model
            parent_level_id = parent_element.get(QC_OLEVEL, None)
            if parent_level_id is None:
                parent_level_id = parent_element.get(QC_LEVEL, None)

            if parent_level_id is not None:
                parent_level = client.get_element(model_id, parent_level_id, column_families=[COLUMN_FAMILIES_STANDARD])
                level_name = parent_level.get(QC_ONAME, None)
                if level_name is None:
                    level_name = parent_level.get(QC_NAME, None)
                levels = client.get_levels(default_model.get('modelId', None))
                level = next((l for l in levels if l.get(QC_ONAME) == level_name or l.get(QC_NAME) == level_name), None)
                if level is not None:
                    level_id = level.get(QC_KEY, None)
        # STEP 6 - payload for ticket connected to asset
        flags = ELEMENT_FLAGS_TICKET
        mutations = [
            [
                MUTATE_ACTIONS_INSERT,
                COLUMN_FAMILIES_STANDARD,
                COLUMN_NAMES_NAME,
                TICKET_NAME
            ],
            [
                MUTATE_ACTIONS_INSERT,
                COLUMN_FAMILIES_STANDARD,
                COLUMN_NAMES_ELEMENT_FLAGS,
                flags
            ],
            [
                MUTATE_ACTIONS_INSERT,
                COLUMN_FAMILIES_XREFS,
                COLUMN_NAMES_PARENT,
                xref
            ],
            [
                MUTATE_ACTIONS_INSERT,
                COLUMN_FAMILIES_STANDARD,
                COLUMN_NAMES_PRIORITY,
                'Low'
            ],
            [
                MUTATE_ACTIONS_INSERT,
                COLUMN_FAMILIES_STANDARD,
                COLUMN_NAMES_OPEN_DATE,
                datetime.now(timezone.utc).date().isoformat()
            ]
        ]
        if rooms_ids is not None:
            mutations.append([
                MUTATE_ACTIONS_INSERT,
                COLUMN_FAMILIES_XREFS,
                COLUMN_NAMES_ROOMS,
                rooms_ids
            ])
        if level_id is not None:
            mutations.append([
                MUTATE_ACTIONS_INSERT,
                COLUMN_FAMILIES_REFS,
                COLUMN_NAMES_LEVEL,
                level_id
            ])
        inputs = {
            'muts': mutations,
            'desc': 'Create ticket'
        }
        ticket_result = client.create_element(default_model.get('modelId'), inputs)
        print(f'Created new ticket: {TICKET_NAME} ({ticket_result.get('key', None)})')

if __name__ == '__main__':
    main()

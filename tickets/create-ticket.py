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
    COLUMN_FAMILIES_STANDARD,
    COLUMN_FAMILIES_XREFS,
    COLUMN_NAMES_ELEMENT_FLAGS,
    COLUMN_NAMES_NAME,
    COLUMN_NAMES_OPEN_DATE,
    COLUMN_NAMES_PARENT,
    COLUMN_NAMES_PRIORITY,
    ELEMENT_FLAGS_ALL_LOGICAL_MASK,
    ELEMENT_FLAGS_TICKET,
    MUTATE_ACTIONS_INSERT,
    QC_ELEMENT_FLAGS,
    QC_KEY,
    QC_NAME,
    QC_ONAME
)
from common.encoding import new_element_key, to_full_key, to_xref_key
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
            print('Unable to find default model')
            return
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
            if xref is not None:
                break
        if xref is None:
            raise Exception(f'Unable to find asset with name: {ASSET_NAME}')
        # STEP 4 - create ticket connected to asset
        flags = ELEMENT_FLAGS_TICKET
        new_key = new_element_key(flags & ELEMENT_FLAGS_ALL_LOGICAL_MASK)
        mutations = []
        mutations.append([
            MUTATE_ACTIONS_INSERT,
            COLUMN_FAMILIES_STANDARD,
            COLUMN_NAMES_NAME,
            TICKET_NAME
        ])
        mutations.append([
            MUTATE_ACTIONS_INSERT,
            COLUMN_FAMILIES_STANDARD,
            COLUMN_NAMES_ELEMENT_FLAGS,
            flags
        ])
        mutations.append([
            MUTATE_ACTIONS_INSERT,
            COLUMN_FAMILIES_XREFS,
            COLUMN_NAMES_PARENT,
            xref
        ])
        mutations.append([
            MUTATE_ACTIONS_INSERT,
            COLUMN_FAMILIES_STANDARD,
            COLUMN_NAMES_PRIORITY,
            'Low'
        ])
        mutations.append([
            MUTATE_ACTIONS_INSERT,
            COLUMN_FAMILIES_STANDARD,
            COLUMN_NAMES_OPEN_DATE,
            datetime.now(timezone.utc).date().isoformat()
        ])
        keys = [new_key] * len(mutations)
        inputs = {
            'keys': keys,
            'muts': mutations,
        }
        client.create_element(default_model.get('modelId'), inputs)
        print(f'Ticket {TICKET_NAME} created and assigned to asset {ASSET_NAME}')

if __name__ == '__main__':
    main()

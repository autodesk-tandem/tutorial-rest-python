"""
This example demonstrates how to change a ticket using REST API.

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
    COLUMN_NAMES_TANDEM_CATEGORY,
    ELEMENT_FLAGS_TICKET,
    MUTATE_ACTIONS_INSERT,
    QC_ELEMENT_FLAGS,
    QC_KEY,
    QC_LEVEL,
    QC_OLEVEL,
    QC_NAME,
    QC_ONAME,
    QC_XROOMS,
    QC_OXROOMS,
    TC_TICKET
)
from common.encoding import decode_xref_key, to_full_key, to_xref_key
from common.utils import get_default_model, is_logical_element

# update values below according to your environment
APS_CLIENT_ID = 'NpSUGahm5tM6qcxACmeCGvcGa6wFQ8L3'
APS_CLIENT_SECRET = 'GvmZPm0LMPacmxui'
FACILITY_URN = 'urn:adsk.dtt:utDRTilBRAiwnPQ_HVR55Q'

# Specify ticket name according to your conventions
TICKET_NAME = 'T2.001'
# Name of the asset to search for
NEW_PRIORITY = 'High'

def main():
    # Start
    # STEP 1 - obtain token. The sample uses 2-legged token but it would also work
    # with 3-legged token assuming that user has access to the facility
    token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read', 'data:write'], env='stg')
    with TandemClient(lambda: token, env='stg') as client:
        # STEP 2 - get facility and default model.
        facility = client.get_facility(FACILITY_URN)
        default_model = get_default_model(FACILITY_URN, facility)
        if default_model is None:
            raise Exception('Unable to find default model')
        # STEP 3 - get ticket elements and find the one by name.
        tickets = client.get_tickets(default_model.get('modelId'))
        ticket = next((t for t in tickets if (t.get(QC_ONAME) or t.get(QC_NAME)) == TICKET_NAME), None)

        if ticket is None:
            raise Exception(f'Unable to find ticket: {TICKET_NAME}')
        # STEP 4 - prepare mutation to set Priority property to new value.
        mutations = []
        keys = []

        keys.append(ticket.get(QC_KEY))
        mutations.append([
            MUTATE_ACTIONS_INSERT,
            COLUMN_FAMILIES_STANDARD,
            COLUMN_NAMES_PRIORITY,
            NEW_PRIORITY
        ])
            # STEP 5 - update elements
        client.mutate_elements(default_model.get('modelId'),
            keys,
            mutations,
            'Change priority')

        print('done')

if __name__ == '__main__':
    main()

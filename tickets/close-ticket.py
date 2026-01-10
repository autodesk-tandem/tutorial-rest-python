"""
This example demonstrates how to close a ticket using REST API.

It uses 2-legged authentication - this requires that application is added
to facility as service.
"""
from datetime import datetime, timezone

from common.auth import create_token
from common.tandemClient import TandemClient
from common.constants import (
    COLUMN_FAMILIES_STANDARD,
    COLUMN_NAMES_CLOSE_DATE,
    MUTATE_ACTIONS_INSERT_IF_DIFFERENT,
    QC_KEY,
    QC_NAME,
    QC_ONAME
)
from common.utils import get_default_model

# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
FACILITY_URN = 'YOUR_FACILITY_URN'

# Specify ticket name according to your conventions
TICKET_NAME = 'Ticket 01'


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
        # STEP 3 - get ticket elements and find the one by name.
        tickets = client.get_tickets(default_model.get('modelId'))
        ticket = next((t for t in tickets if (t.get(QC_ONAME) or t.get(QC_NAME)) == TICKET_NAME), None)

        if ticket is None:
            raise Exception(f'Unable to find ticket: {TICKET_NAME}')
        # STEP 4 - prepare mutation to set Priority property to new value.
        mutations = []
        keys = []
        close_date = datetime.now(timezone.utc).date().isoformat()

        keys.append(ticket.get(QC_KEY))
        mutations.append([
            MUTATE_ACTIONS_INSERT_IF_DIFFERENT,
            COLUMN_FAMILIES_STANDARD,
            COLUMN_NAMES_CLOSE_DATE,
            close_date
        ])
            # STEP 5 - update elements
        client.mutate_elements(default_model.get('modelId'),
            keys,
            mutations,
            'Close ticket')
        print('done')

if __name__ == '__main__':
    main()

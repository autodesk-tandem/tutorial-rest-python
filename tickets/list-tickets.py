"""
This example demonstrates how to create ticket using REST API. The ticket
is assigned to specified asset.

It uses 2-legged authentication - this requires that application is added
to facility as service.
"""
from common.auth import create_token
from common.tandemClient import TandemClient
from common.constants import (
    QC_NAME,
    QC_ONAME,
    QC_PRIORITY,
    QC_XPARENT
)
from common.encoding import decode_xref_key
from common.utils import get_default_model

# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
FACILITY_URN = 'YOUR_FACILITY_URN'


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
        # STEP 3 - get ticket elements.
        tickets = client.get_tickets(default_model.get('modelId'))
        # STEP 4 - iterate through tickets and print their properties.
        for ticket in tickets:
            ticket_name = ticket.get(QC_ONAME, None) or ticket.get(QC_NAME, None)

            print(f'{ticket_name}')
            # priority is optional
            priority = ticket.get(QC_PRIORITY, None)

            if priority is not None:
                print(f'  Priority: {priority}')
            # STEP 5 - decode reference to linked asset and print its name.
            xref = ticket.get(QC_XPARENT, None)

            if xref is not None:
                [ model_id, element_id ] = decode_xref_key(xref)

                element = client.get_element(model_id, element_id)
                if element is not None:
                    element_name = element.get(QC_ONAME, None) or element.get(QC_NAME, None)
                    print(f'  Element: {element_name}');
        

if __name__ == '__main__':
    main()

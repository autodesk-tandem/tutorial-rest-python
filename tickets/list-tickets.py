"""
This example demonstrates how to list tickets from facility using REST API.

It uses 2-legged authentication - this requires that application is added
to facility as service.
"""
from collections import defaultdict
from common.auth import create_token
from common.tandemClient import TandemClient
from common.constants import (
    QC_NAME,
    QC_ONAME,
    QC_PRIORITY,
    QC_XPARENT
)
from common.encoding import decode_xref_key_array
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
                # there can be more than one linked asset - collect them by model
                model_to_elements: dict[str, set[str]] = defaultdict(set)
                
                model_ids, element_ids = decode_xref_key_array(xref)
                for model_id, element_id in zip(model_ids, element_ids):
                    model_to_elements[model_id].add(element_id)
                for model_id, element_ids in model_to_elements.items():
                    elements = client.get_elements(model_id, [*element_ids])
                    for element in elements:
                        element_name = element.get(QC_ONAME, None) or element.get(QC_NAME, None)
                        print(f'  Linked Asset: {element_name}')
        

if __name__ == '__main__':
    main()

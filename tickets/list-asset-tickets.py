"""
This example demonstrates how to list tickets related to assets using REST API.

It uses 2-legged authentication - this requires that application is added
to facility as service.
"""
from collections import defaultdict
from common.auth import create_token
from common.tandemClient import TandemClient
from common.constants import (
    QC_ELEMENT_FLAGS,
    QC_KEY,
    QC_NAME,
    QC_ONAME,
    QC_PRIORITY,
    QC_XPARENT
)
from common.encoding import decode_xref_key_array, to_full_key
from common.utils import get_default_model, is_logical_element

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
        # STEP 2 - get facility and default model.
        facility = client.get_facility(FACILITY_URN)
        default_model = get_default_model(FACILITY_URN, facility)
        if default_model is None:
            raise Exception('Unable to find default model')
        # STEP 3 - get ticket elements.
        tickets = client.get_tickets(default_model.get('modelId'))
        # STEP 4 - iterate through tickets and build map between assets and tickets
        asset_tickets_map = defaultdict(list)
        model_asset_map = defaultdict(set)

        for ticket in tickets:
            xparent = ticket.get(QC_XPARENT, None)
            if xparent is None:
                continue
            model_ids, element_ids = decode_xref_key_array(xparent)

            for model_id, element_id in zip(model_ids, element_ids):
                model_asset_map[model_id].add(element_id)
                asset_tickets_map[element_id].append(ticket)
        # STEP 5 - retrieve asset details and print tickets per asset
        for model_id, element_ids in model_asset_map.items():
            assets = client.get_elements(model_id, element_ids=list(element_ids))
            for asset in assets:
                key = asset.get(QC_KEY, None)
                if key is None:
                    continue
                element_key = to_full_key(key, is_logical_element(asset.get(QC_ELEMENT_FLAGS, None)))
                asset_name = asset.get(QC_ONAME) or asset.get(QC_NAME)
                asset_tickets = asset_tickets_map.get(element_key, [])
                print(f'Asset: {asset_name} ({element_key}) Tickets: {len(tickets)}')
                for ticket in asset_tickets:
                    ticket_name = ticket.get(QC_ONAME) or ticket.get(QC_NAME)
                    ticket_priority = ticket.get(QC_PRIORITY)
                    print(f'  {ticket_name} (Priority: {ticket_priority})')


if __name__ == '__main__':
    main()

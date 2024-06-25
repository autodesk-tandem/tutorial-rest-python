"""
This example demonstrates how to find parent element (= host) of stream.

It uses 2-legged authentication - this requires that application is added to facility as service.
"""

from common.auth import create_token
from common.tandemClient import TandemClient
from common.constants import (
    COLUMN_FAMILIES_STANDARD,
    COLUMN_FAMILIES_XREFS,
    QC_KEY,
    QC_NAME,
    QC_XPARENT
)
from common.encoding import decode_xref_key, to_full_key
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
        # STEP 2 - get facility and default model. The default model has same id as facility
        facility = client.get_facility(FACILITY_URN)
        default_model = get_default_model(FACILITY_URN, facility)
        default_model_id = default_model.get('modelId')

        # STEP 3 - get streams
        streams = client.get_streams(default_model_id, [ COLUMN_FAMILIES_STANDARD, COLUMN_FAMILIES_XREFS ])
        # STEP 4 - get parent data
        stream_data = []
        stream_lookup = {}

        for stream in streams:
            if stream.get(QC_XPARENT, None) is None:
                print(f'Stream {stream.get(QC_NAME)} has no parent')
                continue
            # STEP 5 - decode and store model id and key of parent element
            parent_model_id, parent_key = decode_xref_key(stream.get(QC_XPARENT))
            stream_info = {
                'id': stream.get(QC_KEY),
                'name': stream.get(QC_NAME),
                'parent': {
                    'model_id': parent_model_id,
                    'key': parent_key
                }
            }
            stream_data.append(stream_info)
            stream_lookup[(parent_model_id, parent_key)] = stream_info
        # STEP 6 - build map of model to element key
        model_keys = {}

        for item in stream_data:
            model_id = item['parent']['model_id']
            if model_id not in model_keys:
                model_keys[model_id] = []
            model_keys[model_id].append(item['parent']['key'])
        # STEP 6 - get element details
        for model_id, element_keys in model_keys.items():
            elements = client.get_elements(model_id, element_keys)
            for element in elements:
                full_key = to_full_key(element.get(QC_KEY), False)
                item_key = (model_id, full_key)
                if item_key in stream_lookup:
                    stream_lookup[item_key]['parent']['name'] = element.get(QC_NAME)
        # STEP 7 - print results (stream name - parent name)
        for item in stream_data:
            print(f'{item['name']}: {item['parent']['name']}')


if __name__ == '__main__':
    main()

"""
This example demonstrates how to get streams from given facility and get stream details (name, parent).

It uses 2-legged authentication - this requires athat application is added to facility as service.
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
from common.encoding import decode_xref_key, to_short_key
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
        if default_model is None:
            raise Exception('Default model not found')
        default_model_id = default_model.get('modelId')
        # STEP 3 - get streams and their parents
        streams = client.get_streams(default_model_id)
        model_stream_map = {}
        for i in range(len(streams)):
            stream = streams[i]
            # host is stored as parent
            parent_xref = stream.get(QC_XPARENT)
            if parent_xref is None:
                continue
            # decode xref key of the host
            model_id, key = decode_xref_key(parent_xref)
            items = model_stream_map.get(model_id)
            if items is None:
                items = []
                model_stream_map[model_id] = items
            items.append({
                'key': to_short_key(key),
                'stream_index': i
            })
        # STEP 4 - print name of stream + name of parent
        # note we use batch query to get properties of multiple elements
        # in one call rather than query server for each element
        for model_id in model_stream_map:
            items = model_stream_map[model_id]
            keys = [item.get('key') for item in items]
            element_data = client.get_elements(f'urn:adsk.dtm:{model_id}', keys)
            for item in items:
                stream = streams[item.get('stream_index')]
                parent_data = next((e for e in element_data if e.get(QC_KEY) == item.get('key')), None)
                if parent_data is None:
                    continue
                print(f'{stream[QC_NAME]}: {parent_data[QC_NAME]}')


if __name__ == '__main__':
    main()

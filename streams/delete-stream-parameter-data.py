"""
This example demonstrates how to delete data for given parameter from specific stream.

It uses 2-legged authentication - this requires that application is added to facility as service.
"""

from common.auth import create_token
from common.encoding import to_full_key
from common.tandemClient import TandemClient
from common.constants import (
    COLUMN_FAMILIES_DTPROPERTIES,
    QC_KEY,
    QC_NAME
)
from common.utils import get_default_model

# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
FACILITY_URN = 'YOUR_FACILITY_URN'
STREAM_NAME = 'Sensor 01'
PARAMETER_NAME = 'Temperature'


def main():
    # Start
    # STEP 1 - obtain token. The sample uses 2-legged token but it would also work
    # with 3-legged token assuming that user has access to the facility
    token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read', 'data:write'])
    with TandemClient(lambda: token) as client:
        # STEP 2 - get facility and default model. The default model has same id as facility
        facility = client.get_facility(FACILITY_URN)
        default_model = get_default_model(FACILITY_URN, facility)
        default_model_id = default_model.get('modelId')
        # STEP 3 - get model schema. It is needed to find parameter id.
        schema = client.get_model_schema(default_model_id)
        # STEP 4 - get streams and find stream by name
        streams = client.get_streams(default_model_id)
        stream = next((stream for stream in streams if stream.get(QC_NAME) == STREAM_NAME), None)
        if stream is None:
            raise Exception(f'Stream {STREAM_NAME} not found')
        # STEP 5 - get stream data - we use full key because getStreamData expects full key
        stream_key = to_full_key(stream.get(QC_KEY), True)
        stream_data = client.get_stream_data(default_model_id, stream_key)
        # STEP 6 - find substream by parameter name
        for item in stream_data:
            pd = next((prop for prop in schema.get('attributes') if prop['fam'] == COLUMN_FAMILIES_DTPROPERTIES and prop['id'] == item), None)
            if pd.get('name') == PARAMETER_NAME:
                prop_def = pd
                break
        if prop_def is None:
            raise Exception(f'Parameter {PARAMETER_NAME} not found')
        client.delete_stream_data(default_model_id, [ stream_key ], [ prop_def.get('id') ])


if __name__ == '__main__':
    main()

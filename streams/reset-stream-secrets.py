"""
This example demonstrates how to get streams from given facility and reset their secrets. This is usually not needed
    but can be used in case you want to reset secrets of all streams in facility.

It uses 2-legged authentication - this requires athat application is added to facility as service.
"""

from common.auth import create_token
from common.tandemClient import TandemClient
from common.constants import (
    QC_KEY,
    QC_NAME,
    QC_ONAME
)
from common.encoding import to_full_key, to_short_key
from common.utils import get_default_model

# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
FACILITY_URN = 'YOUR_FACILITY_URN'

def main():
    # Start
    # STEP 1 - obtain token. The sample uses 2-legged token but it would also work
    # with 3-legged token assuming that user has access to the facility. Note that
    # we need to use data:write scope.
    token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read', 'data:write'])
    with TandemClient(lambda: token) as client:
        # STEP 2 - get facility and default model. The default model has same id as facility
        facility = client.get_facility(FACILITY_URN)
        default_model = get_default_model(FACILITY_URN, facility)
        if default_model is None:
            raise Exception('Default model not found')
        default_model_id = default_model.get('modelId')
        # STEP 3 - get streams & their keys
        streams = client.get_streams(default_model_id)
        keys = [stream.get(QC_KEY) for stream in streams]
        # STEP 4 - reset streams secrets
        data = client.reset_stream_secrets(default_model_id, keys, True)
        # STEP 5 - print out stream name + new secret
        for key in data:
            # stream data are stored using short key
            stream_key = to_short_key(key)
            stream_secret = data.get(key)
            stream = next((s for s in streams if s.get(QC_KEY) == stream_key), None)
            if stream is None:
                continue
            name = stream.get(QC_ONAME) or stream.get(QC_NAME)
            print(f'{name}: {stream_secret}')


if __name__ == '__main__':
    main()

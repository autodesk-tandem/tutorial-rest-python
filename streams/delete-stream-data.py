"""
This example demonstrates how to delete data from all streams. Note it deletes all data for all 
streams - use with caution.

It uses 2-legged authentication - this requires that application is added to facility as service.
"""

from common.auth import create_token
from common.tandemClient import TandemClient
from common.constants import (
    QC_KEY
)
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
        # STEP 2 - get facility and default model. The default model has same id as facility
        facility = client.get_facility(FACILITY_URN)
        default_model = get_default_model(FACILITY_URN, facility)
        default_model_id = default_model.get('modelId')

        # STEP 3 - get streams
        streams = client.get_streams(default_model_id)
        # STEP 4 - get stream keys
        keys = [stream.get(QC_KEY) for stream in streams]
        # STEP 5 - delete stream data
        client.delete_stream_data(default_model_id, keys)


if __name__ == '__main__':
    main()

"""
This example demonstrates how to read stream settings (thresholds).

It uses 2-legged authentication - this requires that application is added to facility as service.
"""

from typing import Any

from common.auth import create_token
from common.tandemClient import TandemClient
from common.constants import (
    QC_NAME,
    QC_SETTINGS
)
from common.encoding import decode_stream_settings
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
        streams = client.get_streams(default_model_id)
        for stream in streams:
            # STEP 4 - get stream settings
            stream_settings = stream.get(QC_SETTINGS)
            if stream_settings is None:
                continue
            # STEP 5 - decode settings and print thresholds
            settings = decode_stream_settings(stream_settings)
            print(f'Stream: {stream.get(QC_NAME)}')
            print(f'  Thresholds:')
            for key in settings.get('thresholds'):
                threshold = settings.get('thresholds').get(key)
                print(f'    {threshold.get('name')}')
                if (threshold.get('lower') is not None):
                    print(f'{6 * ' '}lower:')
                    print_threshold(threshold.get('lower'), 8)
                if (threshold.get('upper') is not None):
                    print(f'{6 * ' '}upper:')
                    print_threshold(threshold.get('upper'), 8)

def print_threshold(threshold: Any, indent: int = 0):
    for key in threshold:
        print(f'{indent * ' '}{key}: {threshold.get(key)}')

if __name__ == '__main__':
    main()

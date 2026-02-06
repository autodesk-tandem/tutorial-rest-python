"""
This example demonstrates how to apply override to stream configuration.

It uses 2-legged authentication - this requires athat application is added to facility as service.
"""

from common.auth import create_token
from common.constants import (
    QC_KEY,
    QC_NAME,
    QC_ONAME
)
from common.tandemClient import TandemClient
from common.utils import get_default_model

# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
FACILITY_URN = 'YOUR_FACILITY_URN'

STREAM_NAME = 'Test Stream'  # name of the stream to apply override
PARAMETER_NAME = 'Temperature'  # parameter to map in all streams
INPUT_PATH = 'temp'  # mapping path in the source data

def main():
    # Start
    # STEP 1 - obtain token. The sample uses 2-legged token but it would also work
    # with 3-legged token assuming that user has access to the facility
    token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read', 'data:write'])
    with TandemClient(lambda: token) as client:
        # STEP 2 - get facility and default model. The default model has same id as facility
        facility = client.get_facility(FACILITY_URN)
        default_model = get_default_model(FACILITY_URN, facility)
        if default_model is None:
            raise Exception('Default model not found')
        default_model_id = default_model.get('modelId')
        # STEP 3 - get streams
        streams = client.get_streams(default_model_id)
        # STEP 4 - find stream by name. Check both name and name override
        stream = next((s for s in streams if (s.get(QC_ONAME, '').lower() == STREAM_NAME.lower() or s.get(QC_NAME, '').lower() == STREAM_NAME.lower())), None)
        if not stream:
            raise Exception(f'Stream not found: {STREAM_NAME}')
        stream_key = stream.get(QC_KEY)
        # STEP 5 - get model schema to find property id by its name
        schema = client.get_model_schema(default_model_id)
        prop_def = next((a for a in schema.get('attributes', []) if a.get('name') == PARAMETER_NAME), None)

        if not prop_def:
            raise Exception(f'Property not found in schema: {PARAMETER_NAME}')
        prop_id = prop_def.get('id')
        # STEP 6 - read existing stream configuration
        config = client.get_stream_config(default_model_id, stream_key)
        # STEP 7 - update stream configuration to add override for given parameter
        settings = config.get('streamSettings', {})
        mapping = settings.get('sourceMapping') or {}

        settings['sourceMapping'] = mapping
        mapping[prop_id] = {
            'path': INPUT_PATH # mapping path in the source data
        }
        client.save_stream_config(default_model_id, stream_key, {
            'description': 'Apply configuration override',
            'streamConfig': {
                'streamSettings': settings
            }
        })
        print('Done')


if __name__ == '__main__':
    main()

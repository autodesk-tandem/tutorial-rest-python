"""
This example demonstrates how to update stream thresholds.

It uses 2-legged authentication - this requires athat application is added to facility as service.
"""

from common.auth import create_token
from common.tandemClient import TandemClient
from common.utils import get_default_model

# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
FACILITY_URN = 'YOUR_FACILITY_URN'

PARAMETER_NAME = 'Temperature'  # parameter to map in all streams

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
        # STEP 3 - get model schema to find property id by its name
        schema = client.get_model_schema(default_model_id)
        prop_def = next((a for a in schema.get('attributes', []) if a.get('name') == PARAMETER_NAME), None)

        if not prop_def:
            raise Exception(f'Property not found in schema: {PARAMETER_NAME}')
        prop_id = prop_def.get('id')
        # STEP 4 - update configurations for all streams. Add threshold to temperature parameter.
        configs = client.get_stream_configs(default_model_id)
        new_configs = []

        for config in configs:
            settings = config.get('streamSettings', {})
            source_mapping = settings.get('sourceMapping', {})
            if prop_id not in source_mapping:
                continue
            thresholds = settings.get('thresholds') or {}
            settings['thresholds'] = thresholds
            thresholds[prop_id] = {
                'name': PARAMETER_NAME,
                'lower': {
                    'warn': 18,
                    'alert': 15
                },
                'upper': {
                    'warn': 23,
                    'alert': 25
                }
            }
            new_configs.append(config)
        if len(new_configs) == 0:
            print(f'No stream configuration to update')
            return
        # STEP 5 - update stream configurations in batch
        client.update_stream_configs(default_model_id, {
            'description': 'Update configuration',
            'streamConfigs': new_configs
        })
        print('Done')


if __name__ == '__main__':
    main()

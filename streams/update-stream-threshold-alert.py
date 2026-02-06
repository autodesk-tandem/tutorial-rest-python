"""
This example demonstrates how to apply threshold alert.

It uses 2-legged authentication - this requires athat application is added to facility as service.
"""

from common.auth import create_token
from common.tandemClient import TandemClient
from common.utils import get_default_model

# update values below according to your environment
APS_CLIENT_ID = 'pErXeluFbvApeQYUoA7dnUoA6AoUsEv8'
APS_CLIENT_SECRET = 'KeTDSuToRPrnsXgw'
FACILITY_URN = 'urn:adsk.dtt:JTPLuERzTBaLxCXm52PP5Q'

PARAMETER_NAME = 'Temperature'  # parameter to map in all streams
ALERT_INTERVAL = 300  # alert evaluation period in seconds

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
        # STEP 4 - read existing stream configuration
        configs = client.get_stream_configs(default_model_id)
        # STEP 5 - iterate through stream configurations and update threshold alert for given parameter.
        # Note that we need to update whole configuration, partial update is not supported.
        # We will only update configuration which has threshold for given parameter.
        new_configs = []

        for config in configs:
            settings = config.get('streamSettings', {})

            if not settings:
                continue
            threshold = settings.get('thresholds', {}).get(prop_id)

            if not threshold:
                continue
            # STEP 6 - update alert settings for given  parameter
            alert_definition = threshold.get('alertDefinition') or {}
            threshold['alertDefinition'] = alert_definition
            alert_definition['evaluationPeriodSec'] = ALERT_INTERVAL  # set alert evaluation period to 300 seconds
            new_configs.append(config)
        if len(new_configs) == 0:
            print('No stream configuration to update')
            return
        # STEP 6 - save changes
        client.update_stream_configs(default_model_id, {
            'description': 'Update stream configuration',
            'streamConfigs': new_configs
        })
        print('Done')


if __name__ == '__main__':
    main()

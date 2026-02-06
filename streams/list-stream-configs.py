"""
This example demonstrates how to read stream configuration (including thresholds).

It uses 2-legged authentication - this requires athat application is added to facility as service.
"""

from typing import Any
from common.auth import create_token
from common.tandemClient import TandemClient
from common.constants import (
    QC_KEY,
    QC_NAME,
    QC_ONAME
)
from common.encoding import to_full_key
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
        # STEP 4 - get stream configurations
        stream_configs = client.get_stream_configs(default_model_id)
        # STEP 5 - get model schema
        schema = client.get_model_schema(default_model_id)
    
        for stream in streams:
            # STEP 6 - find settings for stream by its key. Note that configuration uses full key
            key = to_full_key(stream.get(QC_KEY), True)
            config = next((s for s in stream_configs if s.get('elementId') == key), None)
            settings = config.get('streamSettings') if config else None
            
            if not settings:
                continue
            name = stream.get(QC_ONAME) or stream.get(QC_NAME)

            print(f'Stream: {name}')
            # STEP 7 - iterate through stream parameters
            thresholds = settings.get('thresholds', None)

            for (prop_id, mapping) in settings.get('sourceMapping', {}).items():
                prop_def = next((a for a in schema.get('attributes', []) if a.get('id') == prop_id), None)

                if not prop_def:
                    print(f'  Property: {prop_id} (definition not found)')
                    continue
                path = mapping.get('path', None)
                print(f'  Property: {prop_def.get("name")} ({prop_id}) -> {path}')
                # STEP 8 - print threshold details if defined
                threshold = thresholds.get(prop_id) if thresholds else None
                
                if not threshold:
                    continue
                print(f'  Threshold: {threshold.get("name")}')
                if (lower :=threshold.get('lower', None)) is not None:
                    print(f'    lower:')
                    print_threshold(lower, 6)
                if (upper :=threshold.get('upper', None)) is not None:
                    print(f'    upper:')
                    print_threshold(upper, 6)
                # STEP 9 - print alert interval if defined
                alert_definition = threshold.get('alertDefinition', None)

                if alert_definition:
                    print(f'    alert interval (s): {alert_definition.get('evaluationPeriodSec')}')
        print('Done')
        
def print_threshold(threshold: Any, indent: int = 0):
    for key in threshold:
        print(f'{indent * ' '}{key}: {threshold.get(key)}')

if __name__ == '__main__':
    main()

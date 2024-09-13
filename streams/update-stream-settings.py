"""
This example demonstrates how to update stream settings (thresholds). Te example adds threashold to
streams that have parameter with name 'Temperature'.

It uses 2-legged authentication - this requires that application is added to facility as service.
"""

from common.auth import create_token
from common.tandemClient import TandemClient
from common.constants import (
    COLUMN_FAMILIES_STANDARD,
    COLUMN_NAMES_SETTINGS,
    MUTATE_ACTIONS_INSERT,
    QC_CLASSIFICATION,
    QC_KEY,
    QC_NAME,
    QC_OCLASSIFICATION
)
from common.encoding import encode_stream_settings
from common.utils import get_default_model, match_classification

# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
FACILITY_URN = 'YOUR_FACILITY_URN'
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

        if default_model is None:
            print('No default model found')
            return
        default_model_id = default_model.get('modelId')
        # STEP 3 - get template for facility and related parameter set
        template = client.get_facility_template(FACILITY_URN)
        pset = next((p for p in template.get('psets') if p.get('name') == template.get('name')), None)
        # STEP 4 - get schema
        schema = client.get_model_schema(default_model_id)
        keys = []
        mutations = []

        # STEP 5 - iterate through streams and apply threshold to streams that have parameter with name 'Temperature'
        streams = client.get_streams(default_model_id)
        for stream in streams:
            classification_id = stream.get(QC_OCLASSIFICATION, None)
            if classification_id is None:
                classification_id = stream.get(QC_CLASSIFICATION, None)
            if classification_id is None:
                continue
            class_parameters = list(filter(lambda item: any(match_classification(classification_id, c) for c in item.get('applicationFilters').get('userClass')), pset.get('parameters')))
            parameter = next((p for p in class_parameters if p.get('name') == PARAMETER_NAME), None)
            if parameter is None:
                continue
            parameter_def = next((p for p in schema.get('attributes') if p.get('name') == parameter.get('name')), None)
            # STEP 6 - create stream settings for specific parameter. Note this will overwrite existing settings.
            stream_settings = {
                'thresholds': {
                    parameter_def.get('id'): {
                        'schema': 'v1',
                        'name': parameter.get('name'),
                        'lower': {
                            'alert': 14,
                            'warn': 16,
                        },
                        'upper': {
                            'alert': 23,
                            'warn': 21
                        }
                    }
                }
            }
            # STEP 7 - encode stream settings and store it in list of mutations
            settings_enc = encode_stream_settings(stream_settings)
            print(f'Applying threshold to stream: {stream.get(QC_NAME)}')
            keys.append(stream.get(QC_KEY))
            mutations.append([
                MUTATE_ACTIONS_INSERT,
                COLUMN_FAMILIES_STANDARD,
                COLUMN_NAMES_SETTINGS,
                settings_enc
            ])
    # STEP 8 - apply changes
    if len(mutations) > 0:
        client.mutate_elements(default_model_id, keys, mutations, 'Update streams thresholds')

if __name__ == '__main__':
    main()

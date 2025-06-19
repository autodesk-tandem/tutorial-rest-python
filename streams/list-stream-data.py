"""
This example demonstrates how to get streams from given facility and read their data.

It uses 2-legged authentication - this requires that application is added to facility as service.
"""

from time import localtime, strftime, time

from common.auth import create_token
from common.tandemClient import TandemClient
from common.constants import (
    DATA_TYPE_STRING,
    QC_KEY,
    QC_NAME,
    QC_ONAME
)
from common.utils import get_default_model

# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
FACILITY_URN = 'YOUR_FACILITY_URN'
OFFSET_DAYS = 5

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
        # STEP 3 - get schema
        schema = client.get_model_schema(default_model_id)
        # STEP 4 - calculate dates (from, to)
        from_date = round(time() * 1000) - OFFSET_DAYS * 24 * 60 * 60 * 1000
        to_date = round(time() * 1000)
        streams = client.get_streams(default_model_id)
        for stream in streams:
            # STEP 4 - get stream data for last NN days and print their values
            key = stream.get(QC_KEY)
            name = stream.get(QC_ONAME) or stream.get(QC_NAME)

            print(f'{name}')
            stream_data = client.get_stream_data(default_model_id, key, from_date, to_date)
            for i in stream_data:
                prop_def = next((p for p in schema.get('attributes') if p.get('id') == i), None)
                if prop_def is None:
                    continue
                print(f'  {prop_def.get('name')} ({i})')
                value_map = {}

                if (prop_def.get('dataType') == DATA_TYPE_STRING):
                    for key, value in prop_def.get('allowedValues').get('map').items():
                        value_map[value] = key
                values = stream_data.get(i)
                for v in values:
                    value = values[v]
                    if prop_def.get('dataType') == DATA_TYPE_STRING:
                        name = value_map.get(value)
                        print(f'    [{strftime('%Y-%m-%d %H:%M:%S', localtime(int(v) * 0.001))}] {name}')
                    else:
                        print(f'    [{strftime('%Y-%m-%d %H:%M:%S', localtime(int(v) * 0.001))}] {value}')


if __name__ == '__main__':
    main()

"""
This example demonstrates how to get last stream reading. This is similar to list-stream-data.py
but uses different API call which is more efficient for getting last stream values.

It uses 2-legged authentication - this requires that application is added to facility as service.
"""

from time import localtime, strftime

from common.auth import create_token
from common.tandemClient import TandemClient
from common.constants import (
    DATA_TYPE_STRING,
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
        # STEP 3 - get schema
        schema = client.get_model_schema(default_model_id)
        # STEP 4 - get streams
        streams = client.get_streams(default_model_id)
        # STEP 5 - get last readings for each stream
        keys = [stream.get(QC_KEY) for stream in streams]
        data = client.get_stream_last_reading(default_model_id, keys)
        for key in data:
            # STEP 6 - read stream name
            stream = next((s for s in streams if to_full_key(s.get(QC_KEY), True) == key), None)
            if stream is None:
                continue
            name = stream.get(QC_ONAME, None) or stream.get(QC_NAME, None)
            print(f'{name}')
            # STEP 7 - print stream values
            item = data.get(key)

            for prop_id in item:
                prop_def = next((p for p in schema.get('attributes') if p.get('id') == prop_id), None)
                if prop_def is None:
                    continue
                print(f'  {prop_def.get('name')} ({prop_id})')
                # STEP 8 - create map in case of discrete values. In this case the map of allowed strings
                # is stored in the property definition. The map is string to number. The stream data contains integer
                # values which needs to be mapped to strings. We create map for this purpose.
                value_map = {}

                if (prop_def.get('dataType') == DATA_TYPE_STRING):
                    for key, value in prop_def.get('allowedValues').get('map').items():
                        value_map[value] = key
                values = item.get(prop_id)
                for ts in values:
                    date = localtime(int(ts) * 0.001)
                    value = values.get(ts)

                    if prop_def.get('dataType') == DATA_TYPE_STRING:
                        # check string value from map created above.
                        name = value_map.get(value)
                        print(f'    [{strftime('%Y-%m-%d %H:%M:%S', date)}] {name}')
                    else:
                        print(f'    [{strftime('%Y-%m-%d %H:%M:%S', date)}] {value}')


if __name__ == '__main__':
    main()

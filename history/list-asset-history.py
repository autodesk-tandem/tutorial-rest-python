"""
This example demonstrates how to get asset history.

It uses 2-legged authentication - this requires that application is added to facility as service.

NOTE: This example uses API which is NOT SUPPORTED at the moment:
    POST https://developer.api.autodesk.com/tandem/v1/modeldata/:modelId/history
"""
from time import localtime, strftime

from common.auth import create_token
from common.constants import (
    COLUMN_FAMILIES_DTPROPERTIES,
    COLUMN_FAMILIES_STANDARD,
    QC_KEY,
    QC_NAME
)
from common.tandemClient import TandemClient

# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
FACILITY_URN = 'YOUR_FACILITY_URN'

def get_timestamps(assets):
    """
    Extracts list of timestamp values from assets.
    """

    result = set()
    
    for asset in assets:
        for prop in asset:
            props = asset.get(prop)
            if not isinstance(props, list):
                continue
            for i in range(len(props))[::2]:
                ts = props[i + 1]
                if isinstance(ts, int):
                    result.add(ts)
    return sorted(result)

def main():
    # Start
    # STEP 1 - obtain token. The sample uses 2-legged token but it would also work
    # with 3-legged token assuming that user has access to the facility
    token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read'])
    with TandemClient(lambda: token) as client:
        # STEP 2 - get facility
        facility = client.get_facility(FACILITY_URN)
        # STEP 3 - iterate through facility models and collect tagged assets
        for l in facility.get('links'):
            model_id = l.get('modelId')
            schema = client.get_model_schema(model_id)
            assets = client.get_tagged_assets(model_id, [ COLUMN_FAMILIES_STANDARD, COLUMN_FAMILIES_DTPROPERTIES ], True)
            # STEP 4 - collect timestamps and get list of model changes
            timestamps = get_timestamps(assets)
            history = client.get_model_history(model_id, timestamps)
            # STEP 5 - iterate through assets and print their properties including timestamp and author of change
            for asset in assets:
                key = asset.get(QC_KEY)
                name = asset.get(QC_NAME)[0]
                print(f'{name}:{key}')
                for prop in asset:
                    props = asset.get(prop)
                    if not isinstance(props, list):
                        continue
                    prop_def = next(p for p in schema.get('attributes') if p.get('id') == prop)
                    if prop_def is None:
                        continue
                    print(f'  {prop_def.get('category')}:{prop_def.get('name')}')
                    for i in range(len(props))[::2]:
                        value = props[i]
                        ts = props[i + 1]

                        # find change details using timestamp
                        history_item = next(i for i in history if i.get('t') == ts)
                        if history_item is None:
                            continue
                        print(f'    {strftime('%Y-%m-%d %H:%M:%S', localtime(ts * 0.001))}:{value} {history_item.get('n', 'NA')}')


if __name__ == '__main__':
    main()

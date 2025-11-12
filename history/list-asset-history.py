"""
This example demonstrates how to list history of asset changes.

It uses 2-legged authentication - this requires that application is added to facility as service.
"""
from datetime import datetime, timezone
import time

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


def main():
    # Start
    # STEP 1 - obtain token. The sample uses 2-legged token but it would also work
    # with 3-legged token assuming that user has access to the facility
    token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read'])
    with TandemClient(lambda: token) as client:
        # STEP 2 - get facility
        facility = client.get_facility(FACILITY_URN)
        # STEP 3 - iterate through models
        for l in facility.get('links', []):
            model_id = l.get('modelId')
            model_label = l.get('label', None)
            if model_label is None or len(model_label) == 0:
                model_label = 'Default'
            print(f'Model: {model_label}')
            # STEP 4 - get schema, assets and history
            schema = client.get_model_schema(model_id)
            assets = client.get_tagged_assets(model_id,
                                              column_families=[COLUMN_FAMILIES_STANDARD, COLUMN_FAMILIES_DTPROPERTIES],
                                              include_history=True)
            assets_key_map = {asset.get(QC_KEY): asset for asset in assets}
            model_history = client.get_model_history(model_id,
                                                     min=1,
                                                     max=int(time.time() * 1000),
                                                     include_changes=True)
            # STEP 5 - iterate through history and print out details of changed assets
            for history_item in model_history:
                if (ts := history_item.get('t', None)) is None:
                    continue
                keys = history_item.get('k', [])
                updated_assets = [assets_key_map[key] for key in keys if key in assets_key_map]
                if len(updated_assets) == 0:
                    continue
                print(f'{datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} - {history_item.get('d', 'NA')} ({history_item.get('n', None)})')
                for asset in updated_assets:
                    name = asset.get(QC_NAME, None)
                    print(f'  {name[0]}')
                    # STEP 6 - iterate through properties of asset and find those that changed at this timestamp
                    # when history is requested, each property contains list of values and timestamps
                    for prop_id in asset:
                        prop_def = next((p for p in schema.get('attributes', []) if p.get('id', None) == prop_id), None)
                        if prop_def is None:
                            continue
                        prop = asset.get(prop_id, None)
                        if not isinstance(prop, list):
                            continue
                        for i in range(0, len(prop), 2):
                            change_ts = prop[i + 1]
                            # skip if this property change is at different timestamp
                            if change_ts != ts:
                                continue
                            value = prop[i]
                            # STEP 7 - print out name and value of changed property
                            print(f'    {prop_def.get('name')}: {value}')


if __name__ == '__main__':
    main()

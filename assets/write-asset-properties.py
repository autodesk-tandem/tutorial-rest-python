"""
This example demonstrates how to update properties of an asset.

It uses 2-legged authentication - this requires that application is added to facility as service.
"""

import itertools

from common.auth import create_token
from common.tandemClient import TandemClient
from common.constants import (
    COLUMN_FAMILIES_DTPROPERTIES,
    MUTATE_ACTIONS_INSERT,
    QC_KEY,
    QC_NAME
)

# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
FACILITY_URN = 'YOUR_FACILITY_URN'
ASSET_ID_PROPERTY = 'Device ID'

ASSET_VALUES = {
    'P001': {
        'Controller Type': 'Centrifugal',
        'Flow Rate': 2300,
        'Frequency': 60,
        'Temperature': 105,
        'Working Pressure': 175
    }
}

def main():
    # Start
    # STEP 1 - obtain token to authenticate subsequent API calls
    token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read', 'data:write'])
    with TandemClient(lambda: token) as client:
        # STEP 2 - get facility
        facility = client.get_facility(FACILITY_URN)
        # STEP 3 - collect property names
        property_names = set()
        for asset_id in ASSET_VALUES:
            props = ASSET_VALUES[asset_id]
            for prop_name in props:
                property_names.add(prop_name)
        # STEP 4 - iterate through facility models
        for l in facility.get('links'):
            model_id = l.get('modelId')
            schema = client.get_model_schema(model_id)
            # STEP 5 - create map between name and property definition
            property_map = {}
            for prop in [p for p in schema.get('attributes') if p['fam'] == COLUMN_FAMILIES_DTPROPERTIES]:
                property_map[prop['name']] = prop
            id_prop = property_map[ASSET_ID_PROPERTY]
            # STEP 6 - iterate through assets and collect changes
            assets = client.get_tagged_assets(model_id)
            for asset in assets:
                asset_id = asset.get(id_prop['id'])
                if asset_id is None:
                    continue
                print(f'{asset[QC_NAME]}:{asset_id}')
                property_data = ASSET_VALUES.get(asset_id)
                if property_data is None:
                    continue
                mutations = []
                for prop in property_data:
                    prop_def = property_map[prop]
                    new_value = property_data[prop]
                    current_value = asset.get(prop_def['id'])
                    # we apply change only if there is difference
                    if current_value == new_value:
                        continue
                    print(f'  ${prop_def['name']}:{new_value}')
                    mutations.append([
                        MUTATE_ACTIONS_INSERT,
                        prop_def.get('fam'),
                        prop_def.get('col'),
                        new_value
                    ])
                if len(mutations) == 0:
                    continue
                keys = list(itertools.repeat(asset[QC_KEY], len(mutations)))
                client.mutate_elements(model_id, keys, mutations, 'Update asset properties')
                print(f'Updated properties: {len(mutations)}')


if __name__ == '__main__':
    main()

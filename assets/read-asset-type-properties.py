"""
This example demonstrates how to get assets from facility and print their type properties.

It uses 2-legged authentication - this requires that application is added to facility as service.
"""

from common.auth import create_token
from common.tandemClient import TandemClient
from common.constants import (
    QC_KEY,
    QC_FAMILY_TYPE,
    QC_NAME,
    QC_ONAME
)

# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
FACILITY_URN = 'YOUR_FACILITY_URN'

def main():
    # Start
    # STEP 1 - obtain token to authenticate subsequent API calls
    token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read'])
    with TandemClient(lambda: token) as client:
        # STEP 2 - get facility
        facility = client.get_facility(FACILITY_URN)
        # STEP 3 - iterate through facility models and collect tagged assets
        for l in facility.get('links'):
            model_id = l.get('modelId')
            schema = client.get_model_schema(model_id)
            assets = client.get_tagged_assets(model_id)
            asset_type_ids = set()
            asset_type_map = {}
            # STEP 4 - iterate through assets and collect asset types
            for asset in assets:
                asset_type_id = asset.get(QC_FAMILY_TYPE)
                if asset_type_id is None:
                    continue
                asset_type_ids.add(asset_type_id)
                asset_type_map[asset[QC_KEY]] = asset_type_id
            if len(asset_type_ids) == 0:
                continue
            # STEP 5 - get type properties
            asset_types = client.get_elements(model_id, list(asset_type_ids))
            for asset in assets:
                asset_type_id = asset_type_map.get(asset[QC_KEY])
                if asset_type_id is None:
                    continue
                # STEP 6 - print out asset name & asset type name
                asset_type = next(a for a in asset_types if a[QC_KEY] == asset_type_id)
                asset_name = asset.get(QC_ONAME) or asset.get(QC_NAME)
                print(f'{asset_name}: {asset_type.get(QC_NAME)}')


if __name__ == '__main__':
    main()

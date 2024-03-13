"""
This example demonstrates how to get assets from facility and print their properties.

It uses 2-legged authentication - this requires that application is added to facility as service.
"""

from common.auth import create_token
from common.tandemClient import TandemClient
from common.constants import (
    QC_KEY,
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
            for asset in assets:
                # STEP 4 - map properties to schema and print out property name & value
                name = asset.get(QC_ONAME) or asset.get(QC_NAME)
                key = asset.get(QC_KEY)
                print(f'{name}: {key}')
                for prop_id in asset.keys():
                    prop = next(p for p in schema.get('attributes') if p['id'] == prop_id)
                    if prop is None:
                        continue
                    print(f'  {prop['category']}.{prop['name']}:{asset.get(prop_id)}')


if __name__ == '__main__':
    main()

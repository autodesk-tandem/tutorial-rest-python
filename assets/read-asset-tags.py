"""
This example demonstrates how to get tag properties for assets and print their values. Tag properties allow adding
multiple values to the element.

It uses 2-legged authentication - this requires that application is added to facility as service.
"""

from common.auth import create_token
from common.tandemClient import TandemClient
from common.constants import (
    DATA_TYPE_STRING_LIST,
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
            # STEP 4 - read property definitions for tag properties - they are of type StringList
            prop_defs = [p for p in schema.get('attributes') if p.get('dataType') == DATA_TYPE_STRING_LIST]

            if len(prop_defs) == 0:
                continue
            prop_ids = [p.get('id') for p in prop_defs]
            assets = client.get_tagged_assets(model_id)
            for asset in assets:
                # STEP 5 - get tag properties for each asset. Skip properties without value
                props = [p for p in prop_ids if asset.get(p) is not None]
                
                if len(props) == 0:
                    continue
                # first check for name override, if empty then use default name
                name = asset.get(QC_ONAME) or asset.get(QC_NAME)
                key = asset.get(QC_KEY)
                print(f'{name}: {key}')
                # STEP 5 - iterate through tag properties and print out property name & value
                for prop_id in props:
                    prop_def = next((p for p in schema.get('attributes') if p.get('id') == prop_id), None)
                    if prop_def is None:
                        continue
                    values = asset.get(prop_id)
                    print(f'  {prop_def.get('category')}.{prop_def.get('name')}:{','.join(values)}')


if __name__ == '__main__':
    main()

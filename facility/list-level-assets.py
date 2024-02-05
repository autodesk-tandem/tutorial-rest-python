"""
This example demonstrates how to list all levels from facility and find assets for each level.

It uses 2-legged authentication - this requires that application is added to facility as service.
"""

from common.auth import create_token
from common.tandemClient import TandemClient
from common.constants import (
    QC_KEY,
    QC_LEVEL,
    QC_NAME
)

# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
FACILITY_URN = 'YOUR_FACILITY_URN'

# Start
# STEP 1 - obtain token. The sample uses 2-legged token but it would also work
# with 3-legged token assuming that user has access to the facility
token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read'])
with TandemClient(lambda: token) as client:
    # STEP 2 - get facility
    facility = client.get_facility(FACILITY_URN)
    # STEP 3 - iterate through facility models
    for l in facility.get('links'):
        model_id = l.get('modelId')
        levels = client.get_levels(model_id)
        assets = client.get_tagged_assets(model_id)
        # STEP 4 - iterate through levels
        for level in levels:
            print(f'{level.get(QC_NAME)}')
            # STEP 5 - iterate through assets
            for asset in assets:
                asset_level = asset.get(QC_LEVEL)

                if asset_level is None:
                    continue
                # STEP 6 - compare key with level key of an asset
                # if level key is matching to current level then we print out
                # asset name.
                if level.get(QC_KEY) == asset_level:
                    print(f'  {asset.get(QC_NAME)}')

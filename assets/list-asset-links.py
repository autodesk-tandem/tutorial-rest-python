"""
This example demonstrates how to get URL for assets in the facility.

It uses 2-legged authentication - this requires that application is added to facility as service.
"""

from common.auth import create_token
from common.tandemClient import TandemClient
from common.constants import (
    KEY_FLAGS_LOGICAL,
    QC_ELEMENT_FLAGS,
    QC_KEY,
    QC_NAME,
    QC_ONAME
)
from common.encoding import (
    to_full_key,
    to_xref_key
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
        # STEP 3 - iterate through facility models and their assets
        for l in facility.get('links'):
            model_id = l.get('modelId')
            assets = client.get_tagged_assets(model_id)
            for asset in assets:
                # STEP 4 - get full key and generate URL to view asset in Tandem
                is_logical = bool(asset.get(QC_ELEMENT_FLAGS) & KEY_FLAGS_LOGICAL)
                full_key = to_full_key(asset.get(QC_KEY), is_logical)
                xref_key = to_xref_key(model_id, full_key)
                url = f'https://tandem.autodesk.com/pages/facilities/{FACILITY_URN}?selection={xref_key}'
                # STEP 5 - print out asset name and URL
                name = asset.get(QC_ONAME) or asset.get(QC_NAME)
                
                print(f'{name}: {url}')


if __name__ == '__main__':
    main()

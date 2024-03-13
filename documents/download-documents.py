"""
This example demonstrates how to download linked documents from given facility.

It uses 2-legged authentication - this requires that application is added to facility as service.
"""
import os

from common.auth import create_token
from common.tandemClient import TandemClient

# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
FACILITY_URN = 'YOUR_FACILITY_URN'
DOWNLOAD_PATH = os.environ.get('TEMP')

def main():
    # Start
    # STEP 1 - obtain token. The sample uses 2-legged token but it would also work
    # with 3-legged token assuming that user has access to the facility
    token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read'])
    with TandemClient(lambda: token) as client:
        # STEP 2 - get facility
        facility = client.get_facility(FACILITY_URN)
        docs = facility.get('docs')
        if docs is None:
            return
        # STEP 3 - iterate through documents
        for doc in docs:
            print(f'{doc.get('name')}:{doc.get('id')}')
            # STEP 4 - download document to local file
            client.save_document_content(doc.get('signedLink'), os.path.join(DOWNLOAD_PATH, doc.get('name')))


if __name__ == '__main__':
    main()

"""
This example demonstrates how to create & upload linked document for given facility.

It uses 2-legged authentication - this requires that application is added to facility as service.
"""
import os
import requests

from common.auth import create_token
from common.tandemClient import TandemClient

# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
FACILITY_URN = 'YOUR_FACILITY_URN'
FILE_PATH = 'FULL_PATH_TO_YOUR_FILE'

def main():
    # Start
    # STEP 1 - obtain token. The sample uses 2-legged token but it would also work
    # with 3-legged token assuming that user has access to the facility
    token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read', 'data:write'])
    with TandemClient(lambda: token) as client:
        # STEP 2 - get facility
        facility = client.get_facility(FACILITY_URN)
        # STEP 3 - get details about uploaded file
        file_size = os.path.getsize(FILE_PATH)
        file_name = os.path.basename(FILE_PATH)
        doc = next((d for d in facility.get('docs', []) if d.get('name', None) == file_name), None)
        if doc is not None:
            raise Exception(f'Document with name {file_name} already exists in facility.')
        # STEP 4 - start upload    
        file_input = {
            'name': file_name,
            'contentLength': file_size
        }
        file_upload = client.upload_document(FACILITY_URN, file_input)
        # STEP 5 - upload file to the provided link
        with open(FILE_PATH, 'rb') as f:
            content = f.read()
            response = requests.put(file_upload.get('uploadLink'),
                                    headers={
                                        'Content-Length': str(file_size),
                                        'Content-Type': file_upload.get('contentType')
                                    },
                                    data=content)
            if response.status_code != 200:
                raise Exception(f'File upload failed: {response.status_code} - {response.text}')
        # STEP 6 - complete upload
        upload_input = {
            'docUrn': file_upload.get('id')
        }
        upload_result = client.confirm_document_upload(FACILITY_URN, upload_input)
        print(f'Document uploaded: {upload_result.get("name")} (id: {upload_result.get("id")})')


if __name__ == '__main__':
    main()

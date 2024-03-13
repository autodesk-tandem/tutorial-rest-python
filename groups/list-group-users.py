"""
This example demonstrates how to list groups and their users.

It uses 2-legged authentication - this requires that application is added to facility as service.
"""

from common.auth import create_token
from common.tandemClient import TandemClient

# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'

def main():
    # Start
    # STEP 1 - obtain token. The sample uses 2-legged token but it would also work
    # with 3-legged token assuming that user has access to the facility
    token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read'])
    with TandemClient(lambda: token) as client:
        # STEP 2 - get groups
        groups = client.get_groups()
        #/ STEP 3 - iterate through groups and print their name and id
        for group in groups:
            print(f'{group.get('name')}:{group.get('urn')}')
            # STEP 4 - get group details and print related users
            group_details = client.get_group(group.get('urn'))
            for user in group_details.get('users'):
                print(f'  {user.get('id')}: {user.get('name')}')


if __name__ == '__main__':
    main()

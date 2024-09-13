"""
This example demonstrates how to create custom parameters using API.

It uses 2-legged authentication - this requires that application is added to the account as service.
"""

import csv
from common.auth import create_token
from common.tandemClient import TandemClient
from common.constants import (
    ATTRIBUTE_CONTEXT_ELEMENT,
    ATTRIBUTE_TYPE_STRING
)

# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
GROUP_ID = 'YOUR_GROUP_ID'
PARAMETER_CATEGORY = 'Test'

def main():
    # Start
    # STEP 1 - obtain token. The sample uses 2-legged token but it would also work
    # with 3-legged token assuming that user has access to the facility
    token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read', 'data:write'])
    with TandemClient(lambda: token) as client:
        # STEP 2 - collect existing parameters
        custom_parameters = client.get_custom_parameters(GROUP_ID)
        # STEP 3 - open CSV file with parameter data
        with open('./data/parameters.txt', 'r') as file:
            reader = csv.DictReader(file)
            for line in reader:
                # STEP 4 - check if parameter already exists
                param_name = line.get('Name')
                existing_param = next((p for p in custom_parameters if p.get('name') == param_name), None)
                if existing_param:
                    print(f'Parameter {param_name} already exists')
                    continue
                # STEP 5 - create parameter
                param_inputs = {
                    'category': PARAMETER_CATEGORY,
                    'context': ATTRIBUTE_CONTEXT_ELEMENT,
                    'dataType': ATTRIBUTE_TYPE_STRING,
                    'name': line.get('Name'),
                    'description': line.get('Description')
                }

                new_parameter = client.create_custom_parameter(GROUP_ID, param_inputs)
                print(f'Parameter imported succesfully: {new_parameter.get('name')}')

if __name__ == '__main__':
    main()

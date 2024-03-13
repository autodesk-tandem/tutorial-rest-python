"""
This example demonstrates how to send stream data using generic webhook URL.
It also provides example how to authenticate using APS Authentication service.
"""

import requests
import time

from common.auth import create_token

# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
FACILITY_URN = 'YOUR_FACILITY_URN'

def main():
    # Start
    # STEP 1 - Construct payload
    # Autodesk Tandem expects payload to be a valid JSON.
    # In the given example we will report readings from two sensors, containing
    # air temperature and air pressure values.
    # Make sure to use correct stream ids from your facility
    payload = [
        {
            'temperatureValue': 21,
            'pressureValue': 100,
            'id': 'AQAAAIh2FNrZGEnyoEzp-cMEzIcAAAAA'
        },
        {
            'temperatureValue': 19,
            'pressureValue': 95,
            'id': 'AQAAALx_Uhevv0Stghv_6xrcHo4AAAAA'
        }
    ]

    # NOTE: by default, Tandem will use server time to associate data points
    # with. You can supply your own time using fields ("time", "timestamp" or
    # "epoch") on the root level of your payload. Note on supported time
    # formats is here https://forums.autodesk.com/t5/tandem-forum/streams-highlight-supported-timestamp-formats/td-p/11989221
    define_own_timestamp = False

    if define_own_timestamp:
        payload['timestamp'] = int(round(time.time() * 1000))

    # STEP 2 - Obtain 2-legged access token using APS authentication service.
    # Note that service needs to be added to the facility or to account. It's
    # also possible to use 3-legged token if data should be send on behalf of
    # specific user. For more details regarding Authentication service check
    # documentation on APS Portal (https://aps.autodesk.com/en/docs/oauth/v2/developers_guide/overview/).
    token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read', 'data:write'])

    # STEP 3 - Post data to Tandem
    model_id = FACILITY_URN.replace('urn:adsk.dtt:', 'urn:adsk.dtm:')
    url = f'https://tandem.autodesk.com/api/v1/timeseries/models/{model_id}/webhooks/generic'
    res = requests.post(url, json=payload, headers={'Authorization': f'Bearer {token}'})
    if res.status_code == 403:
        print('Autentication failed, check ingestion URL')
        return
    print(res.status_code)


if __name__ == '__main__':
    main()

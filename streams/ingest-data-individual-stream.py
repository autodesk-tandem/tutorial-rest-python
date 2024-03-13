"""
This example demonstrates how to send sensor readings to Tandem for
individual sensor, using a dedicated per-sensor endpoint.
"""

import requests
import time

# update values below according to your environment
# to obtain your own ingestion URL use Copy link button in the UI
# next to stream name
STREAM_URL = 'https://:BUX3cp5qQ4euLYsgJu2kjQ@tandem.autodesk.com/api/v1/timeseries/models/urn:adsk.dtm:mprWPFSnT82G1ILC_4dWgA/streams/AQAAAIh2FNrZGEnyoEzp-cMEzIcAAAAA'

def main():
    # Start
    url = STREAM_URL
    # STEP 1: Construct payload
    # Autodesk Tandem expects payload to be a valid JSON
    # in the given example we will report a sensor reading, containing air
    # temperature and air pressure values.
    #
    # NOTE: Please keep in mind that Tandem supports arbitrary payloads, so,
    # an extra configuration step in UI is required to explan Tandem how to
    # parse incoming payload. See https://autodesk-tandem.github.io/API_streams.html
    # for the reference.
    payload = {
        'temperatureValue': 25,
        'pressureValue': 100
    }

    # NOTE: by default, Tandem will use server time to associate data points
    # with. You can supply your own time using fields ("time", "timestamp" or
    # "epoch") on the root level of your payload. Note on supported time
    # formats is here https://forums.autodesk.com/t5/tandem-forum/streams-highlight-supported-timestamp-formats/td-p/11989221
    define_own_timestamp = False

    if define_own_timestamp:
        payload['timestamp'] = int(round(time.time() * 1000))

    # STEP 2: Make sure auth token is provided and POST the data
    # When ingesting data to individual streams, each stream has it's own secret
    # value, that has to be provided in the HTTP call via "authorization" header
    #
    # For convinience, there is an option to copy stream ingestion URL directly
    # from the UI - this url is fully self contained. Example url looks like this:
    #
    # https://:somesecret@tandem.autodesk.com/api/v1/timeseries/models/urn:adsk.dtm:APCMKgIDSyOFpZ763lew7Q/streams/AQAAAC6lzjQuhETds3FO9vuJy5EAAAAA
    res = requests.post(url, json=payload)

    # NOTE: some HTTP clients might not respect the url shape and not set
    # authorization header correctly - in these cases, you will receive 403 from
    # the API call. To fix this, you will need to set the header manually, i.e.
    # from urllib.parse import urlparse
    #
    # parsed = urlparse(url)
    # res = requests.post(f'{parsed.scheme}://{parsed.hostname}{parsed.path}', auth=(parsed.username,parsed.password), json=payload)    

    if res.status_code == 403:
        print('Autentication failed, check ingestion URL')
        return
    print(res.status_code)


if __name__ == '__main__':
    main()

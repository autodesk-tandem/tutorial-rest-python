"""
This example demonstrates how to send sensor readings to Tandem for
multiple sensors, using a global per-facility endpoint.
"""

import requests
import time

# update values below according to your environment
# to obtain your own URL and token use Webhook Integration command under Streams
WEBHOOK_URL = 'https://tandem.autodesk.com/api/v1/timeseries/models/urn:adsk.dtm:mprWPFSnT82G1ILC_4dWgA/webhooks/generic'
AUTH = 'Basic OlFHOHAybC0xUTZlVXVLWndyd0lWYkE='

def main():
    # Start
    url = WEBHOOK_URL
    # STEP 1: Construct payload
    # Autodesk Tandem expects payload to be a valid JSON
    # in the given example we will report readings from two sensors,
    # containing air temperature and air pressure values.
    #
    # NOTE: Please keep in mind that Tandem supports arbitrary payloads,
    # so, an extra configuration step in UI is required to explan Tandem how
    # to parse incoming payload. See https://autodesk-tandem.github.io/API_streams.html
    # for the reference
    #
    # NOTE: since this payload type contains readings from multiple sensors, you need to
    # supply a routing information. Specifically, you need to indicate which Tandem stream,
    # every event belongs to. Standard way is to add "id" property on the root level of every
    # event. It should be set to the Tandem element ID, that you can obtain e.g. by exporting
    # Tandem streams to CSV using UI.
    #
    # There is also an option to customize path of the routing information, by using "idpath"
    # query parameter for the POST request. For instance, if your payload is nested (e.g. JSON API),
    # you can use dot-notation to hint Tandem API on where to search for routing information:
    # http://<POST request with sensor readings>?idpath=data.tandemID, assuming your event looks like:
    # {
    #     data: {
    #         temperatureValue: 25,
    #		  pressureValue: 100,
    #		  tandemID: 'AQAAAJVLslwb80o0jqA8wgUzxPYAAAAA',
    #	 }
    # }
    payload = [
        {
            'temperatureValue': 25,
            'pressureValue': 100,
            'id': 'AQAAAIh2FNrZGEnyoEzp-cMEzIcAAAAA'
        },
        {
            'temperatureValue': 23,
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

    # STEP 2: Make sure auth token is provided and POST the data
    # When ingesting data to individual streams, each stream has it's own secret
    # value, that has to be provided in the HTTP call via "authorization" header
    #
    # For convenience, there is an option to copy URL and authorization token
    # directly from the UI using Webhook Integration command.
    res = requests.post(url, json=payload, headers={'Authorization': AUTH})
    if res.status_code == 403:
        print('Autentication failed, check ingestion URL')
        return
    print(res.status_code)


if __name__ == '__main__':
    main()

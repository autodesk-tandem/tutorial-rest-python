"""
This example demonstrates how to get history of elements within facility.

It uses 2-legged authentication - this requires that application is added to facility as service.

NOTE: This example uses API which is NOT SUPPORTED at the moment:
    POST https://developer.api.autodesk.com/tandem/v1/modeldata/:modelId/history
"""
from time import localtime, strftime, time

from common.auth import create_token
from common.constants import (
    COLUMN_FAMILIES_DTPROPERTIES,
    COLUMN_FAMILIES_STANDARD,
    QC_KEY,
    QC_NAME
)
from common.tandemClient import TandemClient

# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
FACILITY_URN = 'YOUR_FACILITY_URN'
OFFSET_DAYS = 10

def get_history_entries(history):
    """
    Extracts simple list of keys and related timestamp (k = key, t = timestamp) from history.
    """

    result = [
        { 't': item.get('t'), 'k': key, }
        for item in history
        if item.get('k') is not None
        for key in item.get('k')
    ]

    return result

def main():
    # Start
    # STEP 1 - obtain token. The sample uses 2-legged token but it would also work
    # with 3-legged token assuming that user has access to the facility
    token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read'])
    with TandemClient(lambda: token) as client:
        # STEP 2 - get facility
        facility = client.get_facility(FACILITY_URN)
        # STEP 3 - calculate dates for history
        from_date = round(time() * 1000) - OFFSET_DAYS * 24 * 60 * 60 * 1000
        to_date = round(time() * 1000)
        # STEP 4 - iterate through facility models
        for l in facility.get('links'):
            model_id = l.get('modelId')
            schema = client.get_model_schema(model_id)
            # STEP 5 - get history between dates
            history = client.get_model_history_between_dates(model_id, from_date, to_date, True, False)
            # extract list of keys and related timestamp (k = key, t = timestamp)
            entries = get_history_entries(history)
            if len(entries) == 0:
                continue
            print(f'{l.get('label')}')
            # STEP 6 - get updated elements
            keys = list(map(lambda item: item.get('k'), entries))
            elements = client.get_elements(model_id, keys, [ COLUMN_FAMILIES_STANDARD, COLUMN_FAMILIES_DTPROPERTIES ], True)
            # STEP 7 - iterate through elements and print out changes
            for element in elements:
                key = element.get(QC_KEY)
                # get list of timestamps
                timestamps = sorted(entry['t'] for entry in entries if entry['k'] == key)
                if timestamps is None:
                    continue
                print(f'  {element.get(QC_NAME)}: {element.get(QC_KEY)}')
                # iterate through properties and identify the ones which were changed
                # using timestamp
                for prop in element:
                    props = element.get(prop)
                    if not isinstance(props, list):
                        continue
                    prop_def = next(filter(lambda item: item.get('id') == prop, schema.get('attributes')))
                    if prop_def is None:
                        continue
                    for i in range(len(props))[::2]:
                        value = props[i]
                        ts = props[i + 1]

                        if not ts in timestamps:
                            continue
                        # find change details using timestamp
                        history_item = next(i for i in history if i.get('t') == ts)
                        print(f'    {prop_def.get('category')}:{prop_def.get('name')}')
                        print(f'      {strftime('%Y-%m-%d %H:%M:%S', localtime(ts * 0.001))}:{value} {history_item.get('n', 'NA')}')


if __name__ == '__main__':
    main()

"""
This example demonstrates how find references to rooms for elements of the model.

It uses 2-legged authentication - this requires that application is added to facility as service.
"""

from common.auth import create_token
from common.encoding import from_short_key_array
from common.tandemClient import TandemClient
from common.constants import (
    COLUMN_FAMILIES_STANDARD,
    COLUMN_FAMILIES_REFS,
    ELEMENT_FLAGS_ROOM,
    QC_ELEMENT_FLAGS,
    QC_KEY,
    QC_ROOMS,
    QC_NAME
)

# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
FACILITY_URN = 'YOUR_FACILITY_URN'

def main():
    # Start
    # STEP 1 - obtain token. The sample uses 2-legged token but it would also work
    # with 3-legged token assuming that user has access to the facility
    token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read'])
    with TandemClient(lambda: token) as client:
        # STEP 2 - get facility
        facility = client.get_facility(FACILITY_URN)
        # STEP 3 - iterate through facility models and get all elements from the model
        for l in facility.get('links'):
            model_id = l.get('modelId')
            elements = client.get_elements(model_id, column_families=[ COLUMN_FAMILIES_STANDARD, COLUMN_FAMILIES_REFS])
            # STEP 4 - remember indexes of room elements
            room_index_map = {}
            for i in range(len(elements)):
                element = elements[i]
                if element.get(QC_ELEMENT_FLAGS) == ELEMENT_FLAGS_ROOM:
                    room_index_map[element.get(QC_KEY)] = i
            # STEP 5 - check if element has reference to rooms. If so then decode keys of referenced
            # rooms and print their names.
            for element in elements:
                room_refs = element.get(QC_ROOMS)
                if room_refs is None:
                    continue
                print(f'{element.get(QC_NAME)}')
                room_keys = from_short_key_array(room_refs)
                for room_key in room_keys:
                    room_index = room_index_map.get(room_key)
                    if room_index is None:
                        continue
                    room = elements[room_index]
                    print(f'  {room.get(QC_NAME)}')


if __name__ == '__main__':
    main()

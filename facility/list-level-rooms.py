"""
This example demonstrates how to list all levels from facility and related rooms.

It uses 2-legged authentication - this requires that application is added to facility as service.
"""

from common.auth import create_token
from common.tandemClient import TandemClient
from common.constants import (
    COLUMN_FAMILIES_STANDARD,
    COLUMN_FAMILIES_REFS,
    ELEMENT_FLAGS_LEVEL,
    ELEMENT_FLAGS_ROOM,
    QC_ELEMENT_FLAGS,
    QC_KEY,
    QC_LEVEL,
    QC_NAME
)

# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
FACILITY_URN = 'YOUR_FACILITY_URN'

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
        # STEP 4 - create map between rooms and their levels
        level_room_map = {}
        for i in range(len(elements)):
            element = elements[i]
            if element.get(QC_ELEMENT_FLAGS) != ELEMENT_FLAGS_ROOM:
                continue
            level_ref = element.get(QC_LEVEL)
            if level_ref is None:
                continue
            # STEP 5 - store index of room in map
            rooms = level_room_map.get(level_ref)
            if rooms is None:
                rooms = []
                level_room_map[level_ref] = rooms
            rooms.append(i)
        # STEP 6 - iterate through levels and print names of related rooms
        # we reuse elements which we already got from server and skip elements which aren't of type level
        for element in elements:
            if element.get(QC_ELEMENT_FLAGS) != ELEMENT_FLAGS_LEVEL:
                continue
            room_ids = level_room_map.get(element.get(QC_KEY))
            if room_ids is None:
                continue
            print(f'{element.get(QC_NAME)}')
            # STEP 7 - iterate through related rooms and print their names
            for room_id in room_ids:
                room = elements[room_id]
                print(f'  {room.get(QC_NAME)}')

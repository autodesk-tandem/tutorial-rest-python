"""
This example demonstrates how to list structure of the facility (level - room - asset)

It uses 2-legged authentication - this requires that application is added to facility as service.
"""
import json

from common.auth import create_token
from common.tandemClient import TandemClient
from common.encoding import from_short_key_array, from_xref_key_array, to_short_key
from common.constants import (
    COLUMN_FAMILIES_STANDARD,
    COLUMN_FAMILIES_DTPROPERTIES,
    COLUMN_FAMILIES_REFS,
    COLUMN_FAMILIES_XREFS,
    QC_KEY,
    QC_LEVEL,
    QC_NAME,
    QC_ROOMS,
    QC_XROOMS,
)

# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
FACILITY_URN = 'YOUR_FACILITY_URN'

def is_default_model(facility_id: str, model_id: str) -> bool:
    """
    Checks if model is default model for the facility.
    """

    default_model_id = facility_id.replace('urn:adsk.dtt:', 'urn:adsk.dtm:')

    return default_model_id == model_id

def get_levels(data) -> list:
    result = []
    for level_key in data['levels']:
        result.append((level_key, data['levels'][level_key]))
    return result

def get_rooms_by_level(data, level_key) -> list:
    result = []
    for room_key in data['rooms']:
        if data['room_level_map'].get(room_key) == level_key:
            room = data['rooms'][room_key]
            result.append((room_key, room))
    return result

def get_assets_by_room(data, room_key) -> list:
    asset_keys = data['room_assets_map'][room_key]
    result = []

    for asset_key in asset_keys:
        asset = data['assets'].get(asset_key)

        result.append((asset_key, asset))
    return result

# Start
# STEP 1 - obtain token. The sample uses 2-legged token but it would also work
# with 3-legged token assuming that user has access to the facility
token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read'])
with TandemClient(lambda: token) as client:
    # STEP 2 - get facility
    facility = client.get_facility(FACILITY_URN)
    # this structure is used to keep structure data. it uses element keys as keys for maps.
    data = {
        'levels': {},
        'rooms': {},
        'assets': {},
        'room_assets_map': {},
        'room_level_map': {}
    }
    model_rooms = []

    # STEP 3 - collect assets and related room references
    for l in facility.get('links'):
        model_id = l.get('modelId')
        # skip default model
        if is_default_model(FACILITY_URN, model_id):
            continue
        assets = client.get_tagged_assets(model_id, [ COLUMN_FAMILIES_STANDARD, COLUMN_FAMILIES_DTPROPERTIES, COLUMN_FAMILIES_REFS, COLUMN_FAMILIES_XREFS ])
        for asset in assets:
            # unique asset key
            asset_key = asset.get(QC_KEY)
            data['assets'][asset_key] = asset
            room_ref = asset.get(QC_ROOMS)
            asset_rooms = []
            # STEP 4 - find room references. Note that reference can be within same model or across models
            if room_ref is not None:
                room_keys = from_short_key_array(room_ref)

                for room_key in room_keys:
                    asset_rooms.append((model_id, room_key))
            else:
                room_ref = asset.get(QC_XROOMS)
                room_keys = from_xref_key_array(room_ref)
                for (model_id, room_id) in room_keys:
                    # in case of xref key we need to decode from long key to short key
                    asset_rooms.append((f'urn:adsk.dtm:{model_id}', to_short_key(room_id)))
            # STEP 5 - build map between asset and rooms - note that asset can be linked to more than one room
            for (model_id, room_key) in asset_rooms:
                asset_ids = data['room_assets_map'].get(room_key)

                if asset_ids is None:
                    asset_ids = []
                    data['room_assets_map'][room_key] = asset_ids
                asset_ids.append(asset_key)
            model_rooms.extend(asset_rooms)
    # STEP 6 - process rooms and create map between room and level
    model_ids = set(map(lambda item: item[0], model_rooms))
    for model_id in model_ids:
        room_ids = set(map(lambda item: item[1], filter(lambda item: item[0] == model_id, model_rooms)))
        rooms = client.get_elements(model_id, list(room_ids), [ COLUMN_FAMILIES_STANDARD, COLUMN_FAMILIES_REFS ])
        level_ids = set()

        for room in rooms:
            room_key = room.get(QC_KEY)

            data['rooms'][room_key] = room
            level_ref = room.get(QC_LEVEL)
            if level_ref is not None:
                level_ids.add(level_ref)
                data['room_level_map'][room_key] = level_ref
        # process levels
        if len(level_ids) > 0:
            levels = client.get_elements(model_id, list(level_ids))
            for level in levels:
                level_key = level.get(QC_KEY)
                data['levels'][level_key] = level
    # STEP 7 - iterate through structure
    print('facility data list')
    for (level_key, level) in get_levels(data):
        print(f'{level.get(QC_NAME)}')
        for (room_key, room) in get_rooms_by_level(data, level_key):
            print(f'  {room.get(QC_NAME)}')
            for (asset_key, asset) in get_assets_by_room(data, room_key):
                print(f'    {asset.get(QC_NAME)}')
    # STEP 8 - save structure to file
    with open('facility_data.json', 'w') as f:
        f.write(json.dumps(data, indent=2))

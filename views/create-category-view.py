"""
This example demonstrates how to create view using given category as filter. Note the result might be slighltly different
compared to UI based workflow. In this case it uses properties of given BASE_VIEW as template.
    
It uses 2-legged authentication - this requires that application is added to facility as service.

NOTE - the example uses API which is NOT SUPPORTED at the moment:
    POST https://developer.api.autodesk.com/tandem/v1//twins/:facilityId/views
"""
from datetime import datetime, timezone

from common.auth import create_token
from common.tandemClient import TandemClient

# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
FACILITY_URN = 'YOUR_FACILITY_URN'
BASE_VIEW_NAME = 'Home'
CATEGORY_NAME = 'Doors'
VIEW_LABEL = 'ASSETS'

# contains mapping between category name and internal category id
# category id is coming from Revit
REVIT_CATEGORIES = {
    'Doors': -2000023,
    'Lighting Fixtures': -2001120,
    'Mechanical Equipment': -2001140,
    'Plumbing Fixtures': -2001160,
    'Walls': -2000011,
    'Windows': -2000014
}

def main():
    # STEP 1 - obtain token. The sample uses 2-legged token but it would also work with 3-legged token
    # assuming that user has access to the facility
    token = create_token(APS_CLIENT_ID,
        APS_CLIENT_SECRET, ['data:read', 'data:write'])
    with TandemClient(lambda: token) as client:
        # STEP 2 - get facility & views
        facility_id = FACILITY_URN
        facility = client.get_facility(facility_id)
        views = client.get_views(facility_id)
        # STEP 3 - find base view and category id
        base_view = next((v for v in views if v.get('viewName', None) == BASE_VIEW_NAME), None)
        if not base_view:
            raise ValueError('Base view not found')
        # find category id based on name
        category_id = REVIT_CATEGORIES.get(CATEGORY_NAME, None)

        if not category_id:
            raise ValueError(f'Category id not found for category: {CATEGORY_NAME}')
        # STEP 4 - create input for new view
        new_view = {
            'author': base_view.get('author', None),
            'camera': base_view.get('camera', None),
            'charts': base_view.get('charts', None),
            'createTime': datetime.now(timezone.utc).isoformat(),
            'cutPlanes': base_view.get('cutPlanes', None),
            'facets': {
                'filters': {
                    'cats': [ category_id ],
                    'models': base_view.get('facets', {}).get('filters', {}).get('models', [])
                },
                'isFloorplanEnabled': False,
                'settings': [
                    { 'id': 'models' },
                    { 'id': 'levels' },
                    { 'id': 'spaces' },
                    { 'id': 'classifications' },
                    { 'id': 'tandemCategories' },
                    { 'id': 'cats' }
                ]
            },
            'heatmap': base_view.get('heatmap', None),
            'hiddenElements': base_view.get('hiddenElements', None),
            'hud': {},
            'inventory': base_view.get('inventory', None),
            'label': VIEW_LABEL,
            'version': 2,
            'viewName': CATEGORY_NAME
        }

        # STEP 5 - create new view
        new_view_result = client.create_view(facility_id, new_view)

        print(f"new view: {CATEGORY_NAME} ({new_view_result.get('id', None)})")


if __name__ == '__main__':
    main()

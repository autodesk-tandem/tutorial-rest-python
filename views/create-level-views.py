"""
This example demonstrates how to create views for each level in the facility.
In this case it uses properties of given BASE_VIEW as template.

It uses 2-legged authentication - this requires that application is added to facility as service.
"""
from datetime import datetime, timezone

from common.auth import create_token
from common.constants import (
    QC_NAME,
    QC_ONAME
)
from common.tandemClient import TandemClient

# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
FACILITY_URN = 'YOUR_FACILITY_URN'
# name of the view to use as template
BASE_VIEW_NAME = 'Home'
# group label for created views
VIEW_LABEL = 'LEVELS'

def main():
    # Start
    # STEP 1 - obtain token. The sample uses 2-legged token but it would also work
    # with 3-legged token assuming that user has access to the facility
    token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read', 'data:write'])
    with TandemClient(lambda: token) as client:
        # STEP 2 - get facility & views
        facility_id = FACILITY_URN
        facility = client.get_facility(facility_id)
        views = client.get_views(facility_id)
        # STEP 3 - find base view
        base_view = next((v for v in views if v.get('viewName', None) == BASE_VIEW_NAME), None)
        if not base_view:
            raise ValueError('Base view not found')
        # STEP 4 - find main model
        main_model = next((link for link in facility.get('links', []) if link.get('main', False)), None)
        if not main_model:
            raise ValueError('Main model not found')
        # STEP 5 - get levels
        levels = client.get_levels(main_model.get('modelId'))
        for level in levels:
            # STEP 6 - create input for new view
            name = level.get(QC_ONAME) or level.get(QC_NAME)
            new_view = {
                'author': base_view.get('author'),
                'camera': base_view.get('camera'),
                'charts': base_view.get('charts'),
                'createTime': datetime.now(timezone.utc).isoformat(),
                'cutPlanes': base_view.get('cutPlanes'),
                'facets': {
                    'filters': {
                        'models': base_view.get('facets', {}).get('filters', {}).get('models', []),
                        'levels': [name]
                    },
                    'settings': [
                        { 'id': 'models' },
                        { 'id': 'levels' },
                        { 'id': 'spaces' },
                        { 'id': 'classifications' },
                        { 'id': 'tandemCategories' },
                        { 'id': 'cats' }
                    ]
                },
                'heatmap': base_view.get('heatmap'),
                'hiddenElements': base_view.get('hiddenElements'),
                'hud': base_view.get('hud'),
                'inventory': base_view.get('inventory'),
                'label': VIEW_LABEL,
                'version': 2,
                'viewName': name
            }
            # STEP 7 - create new view
            new_view_result = client.create_view(facility_id, new_view)

            print(f"new view: {name} ({new_view_result.get('id', None)})")


if __name__ == '__main__':
    main()

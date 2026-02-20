"""
This example demonstrates how to assign classification to the element type.
It collects element types and assigns classification based on a hardcoded mapping.

Prerequisites:
- Your APS application must be added to the facility as a service
- The facility must elements classified with specific classification
- Install dependencies: pip install -r requirements.txt

Output:
- Updated classification for element types. The classification is determined based on the classification of elements of that type.
"""
import uuid

from common.auth import create_token
from common.tandemClient import TandemClient
from common.constants import (
    COLUMN_FAMILIES_STANDARD,
    COLUMN_NAMES_OCLASSIFICATION,
    MUTATE_ACTIONS_INSERT,
    QC_CLASSIFICATION,
    QC_OCLASSIFICATION,
    QC_FAMILY_TYPE
)

# Configuration - Replace these placeholders with your actual values
APS_CLIENT_ID = 'YOUR_APS_CLIENT_ID' # Your APS application client ID
APS_CLIENT_SECRET = 'YOUR_APS_CLIENT_SECRET' # Your APS application client secret
FACILITY_URN = 'YOUR_FACILITY_URN' # Your facility URN

# Query parameters
CLASSIFICATION_NAME = 'Hydronic Equipment' # Name of the classification

def main():
    # Start
    # STEP 1 - obtain token to authenticate subsequent API calls. The sample uses 2-legged token but it would also work
    # with 3-legged token assuming that user has access to the facility
    token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read', 'data:write'])
    with TandemClient(lambda: token) as client:
        # STEP 2 - get facility & facility template
        facility = client.get_facility(FACILITY_URN)
        # STEP 3 - get facility template and  mapping of classification id to classification name
        facility_template = client.get_facility_template(FACILITY_URN)
        rows = facility_template.get('classification', {}).get('rows', [])
        classification_map = {
            row[0]: row[1]
            for row in rows
            if isinstance(row, (list, tuple)) and len(row) >= 2
        }
        # STEP 4 - generate correlation id for the mutation. Correlation id is used for grouping mutations in the UI
        # and is required for the mutation to be visible in the facility history.
        # Using the same correlation id for all mutations allows to see them as a single operation in the UI.
        correlation_id = str(uuid.uuid4())

        # STEP 5 - iterate through the models of the facility and collect element types that should be classified based
        # on the classification of elements in the model.
        for l in facility.get('links', []):
            model_id = l.get('modelId')
            model_name = l.get('label')
            print(f'Processing model: {model_name} ({model_id})')
            # Request only needed columns
            elements = client.get_elements(model_id,
                                           columns=[
                                            QC_CLASSIFICATION,
                                            QC_OCLASSIFICATION,
                                            QC_FAMILY_TYPE])
            # Map: {type_id: classification_id} for types we want to update.
            type_class_map: dict[str,str] = {}

            for element in elements:
                # Prefer overridden classification, fallback to base classification.
                classification_id = element.get(QC_OCLASSIFICATION) or element.get(QC_CLASSIFICATION)
                if not classification_id:
                    continue
                # Convert ID -> readable name so we can match target classification.
                classification_name = classification_map.get(classification_id)
                if classification_name == CLASSIFICATION_NAME:
                    type_id = element.get(QC_FAMILY_TYPE)
                    if type_id:
                        type_class_map[type_id] = classification_id
            if len(type_class_map) == 0:
                continue
            print(f'  Types to update: {len(type_class_map)}')
            # STEP 6 - build and send mutation(s) to write classification on types.
            mutations = []

            for type_id, classification_id in type_class_map.items():
                mutations.append([
                    MUTATE_ACTIONS_INSERT,
                    COLUMN_FAMILIES_STANDARD,
                    COLUMN_NAMES_OCLASSIFICATION,
                    classification_id
                ])
            client.mutate_elements(model_id,
                                   keys=list(type_class_map.keys()),
                                   mutations=mutations,
                                   description='Update classification',
                                   correlation_id=correlation_id)


if __name__ == '__main__':
    main()

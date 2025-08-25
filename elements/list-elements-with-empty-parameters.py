"""
This example demonstrates how to locate classified elements with empty parameters.

It uses 2-legged authentication - this requires that application is added to facility as service.
"""

from common.auth import create_token
from common.tandemClient import TandemClient
from common.constants import (
    COLUMN_FAMILIES_STANDARD,
    COLUMN_FAMILIES_DTPROPERTIES,
    QC_CLASSIFICATION,
    QC_OCLASSIFICATION,
    QC_NAME,
    QC_ONAME,
    QC_TANDEMCATEGORY,
    QC_OTANDEMCATEGORY
)

from common.utils import match_classification

# update values below according to your environment
APS_CLIENT_ID = 'YOUR_CLIENT_ID'
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
FACILITY_URN = 'YOUR_FACILITY_URN'


def main():
    # Start
    # STEP 1 - obtain token to authenticate subsequent API calls
    token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read'])
    with TandemClient(lambda: token) as client:
        # STEP 2 - get facility & template
        facility = client.get_facility(FACILITY_URN)
        template = client.get_facility_template(FACILITY_URN)
        pset = next((p for p in template.get('psets') if p.get('name') == template.get('name')), None)
        if pset is None:
            print(f'No parameter set found for template: {template.get("name")}')
            return
        # STEP 3 - iterate through facility models and process elements
        element_count = 0

        for l in facility.get('links'):
            model_id = l.get('modelId')
            # STEP 3 - get schema
            schema = client.get_model_schema(model_id)
            # STEP 4 - get elements and process one by one
            elements = client.get_elements(model_id, column_families=[COLUMN_FAMILIES_STANDARD, COLUMN_FAMILIES_DTPROPERTIES])
            for element in elements:
                name = element.get(QC_ONAME) or element.get(QC_NAME)
                # STEP 5 - find parameters related to classification or Tandem category
                classification = element.get(QC_OCLASSIFICATION) or element.get(QC_CLASSIFICATION)
                category = element.get(QC_OTANDEMCATEGORY) or element.get(QC_TANDEMCATEGORY)
                class_parameters = None

                if classification is not None:
                    class_parameters = list(filter(lambda item: any(match_classification(classification, c) for c in item.get('applicationFilters', {}).get('userClass', {})), pset.get('parameters')))
                elif category is not None:
                    class_parameters = list(filter(lambda item: any(match_classification(category, c) for c in item.get('applicationFilters', {}).get('tandemCategory', {})), pset.get('parameters')))
                if class_parameters is None or len(class_parameters) == 0:
                    continue
                # STEP 6 - check parameters with empty value
                parameter_count = 0

                print(f'Processing element: {name}')
                for class_parameter in class_parameters:
                    parameter_def = next((a for a in schema.get('attributes') if a.get('category') == class_parameter.get('category') and a.get('name') == class_parameter.get('name')), None)
                    if parameter_def is None:
                        continue
                    # parameter can be either missing or be empty string - depends on type
                    parameter_value = element.get(parameter_def.get('id'))
                    if parameter_value is None or parameter_value == '':
                        print(f'  Empty value: {parameter_def.get('category')}.{parameter_def.get('name')}')
                        parameter_count += 1
                if parameter_count > 0:
                    element_count += 1
        # STEP 7 - print out total number of elements with empty parameters
        print(f'Total number of elements with empty parameters: {element_count}')

if __name__ == '__main__':
    main()

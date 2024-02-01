from typing import Any

def get_default_model(facility_id: str, facility: Any) -> Any | None:
    """
    Returns default model for given facility.
    """
    
    default_model_id = facility_id.replace('urn:adsk.dtt:', 'urn:adsk.dtm:')
    for link in facility.get('links'):
        model_id = link.get('modelId')
        if model_id == default_model_id:
            return link
    return None
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

def match_classification(a: str, b: str) -> bool:
    """
    Checks if classification b is based on classification a.
    """
    b_len = len(b)

    while (b[b_len - 1] == '0' and b[b_len - 2] == '0'):
        c = b[b_len - 3]

        if c == ' ' or c == '.':
            b_len -= 3
        else:
            break
    a_i = 0
    b_i = 0
    a_c = a[a_i]
    b_c = b[b_i]
    while (a_i < len(a) and b_i < b_len):
        if a_c != b_c:
            return False
        a_i += 1
        while a_i < len(a) and a_c.isalnum() == False:
            a_i += 1
            a_c = a[a_i]
        b_i += 1
        while b_i < b_len and b_c.isalnum() == False:
            b_i += 1
            b_c = b[b_i]
    return b_i == b_len

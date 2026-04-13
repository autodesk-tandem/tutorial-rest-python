import base64
from typing import Any

from .constants import (
    ELEMENT_FLAGS_ALL_LOGICAL_MASK,
    ELEMENT_ID_SIZE,
    SYSTEM_CLASS_NAMES
)
from .encoding import __make_web_safe

def get_default_model(facility_id: str, facility: Any) -> Any | None:
    """
    Returns default model for given facility.
    """
    
    default_model_id = get_default_model_id(facility_id)
    return next(
        (link for link in facility.get('links', []) if link.get('modelId') == default_model_id),
        None
    )

def get_default_model_id(facility_id: str) -> str:
    """
    Returns id of default model for given facility.
    """
    
    return facility_id.replace('urn:adsk.dtt:', 'urn:adsk.dtm:')

def get_root_id() -> str:
    """
    Returns id of root element.
    """

    buff = bytearray(ELEMENT_ID_SIZE)
    return __make_web_safe(base64.b64encode(buff).decode('utf-8'))

def is_logical_element(element_flags: int) -> bool:
    """
    Returns true if the element is a logical element.
    """

    return bool(element_flags & ELEMENT_FLAGS_ALL_LOGICAL_MASK)

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
        while a_i < len(a) and not a[a_i].isalnum():
            a_i += 1
        if a_i < len(a):
            a_c = a[a_i]
        b_i += 1
        while b_i < b_len and not b[b_i].isalnum():
            b_i += 1
        if b_i < len(b):
            b_c = b[b_i]
    return b_i == b_len

def system_class_to_list(flags:int) -> list[str]:
    """
    Converts endcoded system class flags to array of class names.
    """

    if flags is None or flags == 0:
        return []
    result = []

    for i in range(len(SYSTEM_CLASS_NAMES)):
        if flags & (1 << i):
            result.append(SYSTEM_CLASS_NAMES[i])
    return result

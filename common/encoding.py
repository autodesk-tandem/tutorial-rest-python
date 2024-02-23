import base64
import struct
from typing import List, Tuple

from .constants import (
    ELEMENT_FLAGS_SIZE,
    ELEMENT_ID_SIZE,
    ELEMENT_ID_WITH_FLAGS_SIZE,
    KEY_FLAGS_LOGICAL,
    KEY_FLAGS_PHYSICAL,
    MODEL_ID_SIZE,
    SYSTEM_ID_SIZE
)

def decode_xref_key(key: str) -> Tuple[str, str]:
    """ Decodes xref key to model id and element key."""

    txt = __b64_prepare(key)
    buff = base64.b64decode(txt)
    model_buff = bytearray(MODEL_ID_SIZE)
    model_buff[0:] = buff[0:MODEL_ID_SIZE]
    model_id = __make_web_safe(base64.b64encode(model_buff).decode('utf-8'))
    key_buff = bytearray(MODEL_ID_SIZE)
    key_buff[0:] = buff[MODEL_ID_SIZE:]
    element_key = __make_web_safe(base64.b64encode(key_buff).decode('utf-8'))
    return model_id, element_key

def from_short_key_array(text: str, use_full_keys: bool = False, is_logical: bool = False) -> List[str]:
    """
    Decodes text (local refs) to list of keys. If use_full_keys is set to True then full
    keys are returned. If is_logical is set to True then logical keys are
    returned.
    """

    text = __b64_prepare(text)
    bin_data = base64.b64decode(text)
    buff = bytearray(ELEMENT_ID_SIZE)
    if use_full_keys:
        buff = bytearray(ELEMENT_ID_WITH_FLAGS_SIZE)
    result = []
    offset = 0
    while offset < len(bin_data):
        size = len(bin_data) - offset
        if size < ELEMENT_ID_SIZE:
            break
        if use_full_keys:
            flags_value = KEY_FLAGS_LOGICAL if is_logical else KEY_FLAGS_PHYSICAL
            struct.pack_into('>I', buff, 0, flags_value)
            buff[ELEMENT_FLAGS_SIZE:] = bin_data[offset:offset + ELEMENT_ID_SIZE]
        else:
            buff[0:] = bin_data[offset:offset + ELEMENT_ID_SIZE]
        element_key = __make_web_safe(base64.b64encode(buff).decode('utf-8'))
        result.append(element_key)
        offset += ELEMENT_ID_SIZE
    return result

def from_xref_key_array(text: str) -> List[Tuple[str, str]]:
    """ Decodes text (xref refs) to list of model id and element key tuples."""

    if text is None:
        return []
    text = __b64_prepare(text)
    bin_data = base64.b64decode(text)
    buff = bytearray(MODEL_ID_SIZE + ELEMENT_ID_WITH_FLAGS_SIZE)
    result = []
    offset = 0
    while offset < len(bin_data):
        size = len(bin_data) - offset
        if size < MODEL_ID_SIZE + ELEMENT_ID_WITH_FLAGS_SIZE:
            break
        buff[0:] = bin_data[offset:offset + MODEL_ID_SIZE + ELEMENT_ID_WITH_FLAGS_SIZE]
        model_id = __make_web_safe(base64.b64encode(buff[0:MODEL_ID_SIZE]).decode('utf-8'))
        element_key = __make_web_safe(base64.b64encode(buff[MODEL_ID_SIZE:]).decode('utf-8'))
        result.append((model_id, element_key))
        offset += MODEL_ID_SIZE + ELEMENT_ID_WITH_FLAGS_SIZE
    return result

def to_element_GUID(key: str) -> str:
    """ Converts element key to Revit GUID. Works for both short and full key. Note: It works only for models imported from Revit."""

    txt = __b64_prepare(key)
    buff = base64.b64decode(txt)
    if len(buff) == ELEMENT_ID_WITH_FLAGS_SIZE:
        del buff[0:4]
    hex = [f'{b:02x}' for b in buff]
    hex_groups = [4, 2, 2, 2, 6, 4]
    pos = 0
    result = []

    for length in hex_groups:
        result.append(''.join(hex[pos:pos + length]))
        pos += length
    return '-'.join(result)

def to_full_key(short_key: str, is_logical: bool = False) -> str:
    """ Converts short key to full key."""

    txt = __b64_prepare(short_key)
    buff = base64.b64decode(txt)
    full_key = bytearray(ELEMENT_ID_WITH_FLAGS_SIZE)
    flags_value = KEY_FLAGS_LOGICAL if is_logical else KEY_FLAGS_PHYSICAL
    struct.pack_into('>I', full_key, 0, flags_value)

    full_key[ELEMENT_FLAGS_SIZE:] = buff
    return __make_web_safe(base64.b64encode(full_key).decode('utf-8'))

def to_short_key(full_key: str) -> str:
    """ Converts full key to short key."""

    txt = __b64_prepare(full_key)
    buff = base64.b64decode(txt)
    key = bytearray(ELEMENT_ID_SIZE)
    key[0:] = buff[ELEMENT_FLAGS_SIZE:]
    return __make_web_safe(base64.b64encode(key).decode('utf-8'))

def to_system_id(key: str) -> str:
    """
    Converts element key to system id.
    """
    
    buff = base64.b64decode(__b64_prepare(key))
    id = buff[-4] << 24
    id |= buff[-3] << 16
    id |= buff[-2] << 8
    id |= buff[-1]
    res = bytearray(SYSTEM_ID_SIZE)
    offset  = [0]

    len = __write_var_int(res, offset, id)
    tmp = bytearray(len)
    tmp[0:] = res[0:len]
    text = base64.b64encode(tmp).decode('utf-8')
    text = text.replace('=','')
    return text
    

def to_xref_key(model_id: str, key: str) -> str:
    """ Converts model id and element key to xref key."""

    model_buff = base64.b64decode(__b64_prepare(model_id))
    element_buff = base64.b64decode(__b64_prepare(key))
    result = bytearray(MODEL_ID_SIZE + ELEMENT_ID_WITH_FLAGS_SIZE)
    result[0:] = model_buff
    result[MODEL_ID_SIZE:] = element_buff
    return __make_web_safe(base64.b64encode(result).decode('utf-8'))

def __b64_prepare(text: str) -> str:
    result = text.replace('-', '+')
    result = result.replace('_', '/')
    result += '=' * (len(result) % 4)
    return result

def __make_web_safe(text: str) -> str:
    result = text.replace('+', '-')
    result = result.replace('/', '_')
    result = result.rstrip('=')
    return result

def __write_var_int(buff, offset, value):
    start_offset = offset[0]

    while True:
        byte = 0 | (value & 0x7f)

        value >>= 7
        value &= 0xffffffff
        if value != 0:
            byte |= 0x80
        buff[offset[0]] = byte
        offset[0] += 1
        if not value:
            break
    return offset[0] - start_offset
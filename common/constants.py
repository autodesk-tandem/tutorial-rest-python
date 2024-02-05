ELEMENT_FLAGS_SIZE = 4
ELEMENT_ID_SIZE = 20
ELEMENT_ID_WITH_FLAGS_SIZE = ELEMENT_FLAGS_SIZE + ELEMENT_ID_SIZE
MODEL_ID_SIZE = 16

KEY_FLAGS_PHYSICAL = 0x00000000
KEY_FLAGS_LOGICAL = 0x01000000

ELEMENT_FLAGS_LEVEL = 0x01000001
ELEMENT_FLAGS_ROOM = 0x00000005
ELEMENT_FLAGS_STREAM = 0x01000003

COLUMN_FAMILIES_DTPROPERTIES = 'z'
COLUMN_FAMILIES_LMV = '0'
COLUMN_FAMILIES_STANDARD = 'n'
COLUMN_FAMILIES_SYSTEMS = 'm'
COLUMN_FAMILIES_REFS = 'l'
COLUMN_FAMILIES_XREFS = 'x'

COLUMN_NAMES_CATEGORY_ID = 'c'
COLUMN_NAMES_CLASSIFICATION = 'v'
COLUMN_NAMES_OCLASSIFICATION = '!v'
COLUMN_NAMES_ELEMENT_FLAGS = 'a'
COLUMN_NAMES_ELEVATION = 'el'
COLUMN_NAMES_FAMILY_TYPE = 't'
COLUMN_NAMES_LEVEL = 'l'
COLUMN_NAMES_NAME = 'n'
COLUMN_NAMES_PARENT = 'p'
COLUMN_NAMES_ROOMS = 'r'
COLUMN_NAMES_UNIFORMAT_CLASS = 'u'

QC_KEY = 'k'
QC_CLASSIFICATION = f'{COLUMN_FAMILIES_STANDARD}:{COLUMN_NAMES_CLASSIFICATION}'
QC_OCLASSIFICATION = f'{COLUMN_FAMILIES_STANDARD}:{COLUMN_NAMES_OCLASSIFICATION}'
QC_ELEMENT_FLAGS = f'{COLUMN_FAMILIES_STANDARD}:{COLUMN_NAMES_ELEMENT_FLAGS}'
QC_ELEVATION = f'{COLUMN_FAMILIES_STANDARD}:{COLUMN_NAMES_ELEVATION}'
QC_FAMILY_TYPE = f'{COLUMN_FAMILIES_REFS}:{COLUMN_NAMES_FAMILY_TYPE}'
QC_LEVEL = f'{COLUMN_FAMILIES_REFS}:{COLUMN_NAMES_LEVEL}'
QC_NAME = f'{COLUMN_FAMILIES_STANDARD}:{COLUMN_NAMES_NAME}'
QC_ROOMS = f'{COLUMN_FAMILIES_REFS}:{COLUMN_NAMES_ROOMS}'
QC_XPARENT = f'{COLUMN_FAMILIES_XREFS}:{COLUMN_NAMES_PARENT}'

MUTATE_ACTIONS_INSERT = 'i'
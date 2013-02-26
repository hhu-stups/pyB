from btypes import *

def pyB_ext_length(b_string):
    return len(b_string)

EXTERNAL_FUNCTIONS_DICT = {"STRING_LENGTH": pyB_ext_length}
EXTERNAL_FUNCTIONS_TYPE = {"STRING_LENGTH": IntegerType(None)}
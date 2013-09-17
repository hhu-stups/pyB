from btypes import *

# not tested at the moment 
def pyB_ext_length(args):
    b_string = args[0]
    return len(b_string)

def pyB_ext_append(args):
    b_string0 = args[0]
    b_string1 = args[1]
    return b_string0 + b_string1

EXTERNAL_FUNCTIONS_DICT = {"STRING_LENGTH": pyB_ext_length, "STRING_APPEND": pyB_ext_append}


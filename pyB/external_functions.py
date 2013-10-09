from btypes import *
from bexceptions import ValueNotInDomainException

# not tested at the moment 
def pyB_ext_length(args):
    b_string = args[0]
    return len(b_string)

def pyB_ext_append(args):
    b_string0 = args[0]
    b_string1 = args[1]
    return b_string0 + b_string1


# split is a total function => every input musst create a result    
def pyB_ext_split(args):
    b_string0 = args[0]
    sep = args[1]
    if sep=="":
        return frozenset([])
    #    raise ValueNotInDomainException("empty seperator in ext. function split")
    if b_string0=="":
    #    raise ValueNotInDomainException("empty string in ext. function split")
        return frozenset([])
    lst = b_string0.split(sep)
    result = []
    for i in range(len(lst)):
        result.append(tuple([i+1, lst[i]]))
    return frozenset(result)


def pyB_ext_chars(args):
    b_string = args[0]
    result = []
    i = 1
    for c in b_string:
        t = tuple([i,c])
        result.append(t)
        i = i+1
    return frozenset(result)   

EXTERNAL_FUNCTIONS_DICT = {"STRING_LENGTH": pyB_ext_length, "STRING_APPEND": pyB_ext_append, "STRING_SPLIT": pyB_ext_split, "STRING_CHARS": pyB_ext_chars}


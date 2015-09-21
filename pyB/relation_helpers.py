from bexceptions import EnumerationNotPossibleException
from config import USE_RPYTHON_CODE
from helpers import *
from symbolic_sets import InfiniteSet

if USE_RPYTHON_CODE:
     from rpython_b_objmodel import frozenset

# filters out every function which is not injective
# returntype: frozenset
def filter_not_injective(functions):
    injective_funs = []
    for fun in functions:
        if is_a_inje_function(fun):
            injective_funs.append(fun)
    return frozenset(injective_funs)


# filters out every function which is not surjective
# returntype: frozenset
def filter_not_surjective(functions, T):
    surj_funs = []
    for fun in functions:
        if is_a_surj_function(fun, T):
            surj_funs.append(fun)
    return frozenset(surj_funs)

# filters out every set which is no function
# returntype: frozenset
def filter_no_function(relations):
    functions = []
    for r in relations:
        if is_a_function(r):
            functions.append(r)
    return frozenset(functions)
    

# filters out every function which is not total
# returntype: frozenset
def filter_not_total(functions, S):
    total_funs = []
    for fun in functions:
        if is_a_total_function(fun, S):
            total_funs.append(fun)
    return frozenset(total_funs)


def is_a_total_function(function, preimage_set):
    if USE_RPYTHON_CODE:
        return is_a_total_function_rpython(function, preimage_set)
    else:
        return _is_a_total_function(function, preimage_set)
 
        
def is_a_surj_function(function, image_set):
    if USE_RPYTHON_CODE:
        return is_a_surj_function_rpython(function, image_set)
    else:
        return _is_a_surj_function(function, image_set)    


def is_a_inje_function(function):
    if USE_RPYTHON_CODE:
        return is_a_inje_function_rpython(function)
    else:
        return _is_a_inje_function(function)


def is_a_function(relation):
    if USE_RPYTHON_CODE:
        return is_a_function_rpython(relation)
    else:
        return _is_a_function(relation)


# checks if the function it total 
# returntype: frozenset
def _is_a_total_function(function, preimage_set):
    if isinstance(preimage_set, InfiniteSet):
        raise EnumerationNotPossibleException("InfiniteSet")
    preimage = [x[0] for x in function]
    preimage_set2 =  frozenset(preimage)
    return preimage_set == preimage_set2


# checks if the function it surjective
# returntype: boolean
def _is_a_surj_function(function, image_set):
    if isinstance(image_set, InfiniteSet):
        raise EnumerationNotPossibleException("InfiniteSet")
    image = [x[1] for x in function]
    image_set2 = frozenset(image) # remove duplicate items
    return image_set == image_set2


# checks if the function it injective
# returntype: booelan
def _is_a_inje_function(function):
    image = [x[1] for x in function]
    return not double_element_check(image)


# checks if a relation is a function
# returntype: boolean
def _is_a_function(relation):
    preimage_set = [x[0] for x in relation]
    if double_element_check(preimage_set):
        return False
    else:
        return True
        

# checks if the function it total 
# returntype: frozenset
def is_a_total_function_rpython(function, preimage_set):
    if isinstance(preimage_set, InfiniteSet):
        raise EnumerationNotPossibleException("InfiniteSet")
    preimage = []
    for t in function:
         preimage.append(t.tvalue[0])
    preimage_set2  = frozenset(preimage)
    return preimage_set.__eq__(preimage_set2)


# checks if the function it surjective
# returntype: boolean
def is_a_surj_function_rpython(function, image_set):
    if isinstance(image_set, InfiniteSet):
        raise EnumerationNotPossibleException("InfiniteSet")
    image = []
    for t in function:
         image.append(t.tvalue[1])
    image_set2 = frozenset(image) # remove duplicate items
    return image_set.__eq__(image_set2)


# checks if the function it injective
# returntype: booelan
def is_a_inje_function_rpython(function):
    image = []
    for t in function:
         image.append(t.tvalue[1])
    return not double_element_check(image)


# checks if a relation is a function
# returntype: boolean
def is_a_function_rpython(relation):
    preimage_set = []
    for t in relation:
         preimage_set.append(t.tvalue[0])
    if double_element_check(preimage_set):
        return False
    else:
        return True
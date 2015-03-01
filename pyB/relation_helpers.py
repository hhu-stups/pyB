from helpers import *
from symbolic_sets import InfiniteSet
from bexceptions import EnumerationNotPossibleException
from config import USE_COSTUM_FROZENSET
if USE_COSTUM_FROZENSET:
     from rpython_b_objmodel import frozenset

# filters out every function which is not injective
def filter_not_injective(functions):
    injective_funs = []
    for fun in functions:
        if is_a_inje_function(fun):
            injective_funs.append(fun)
    return frozenset(injective_funs)


# filters out every function which is not surjective
def filter_not_surjective(functions, T):
    surj_funs = []
    for fun in functions:
        if is_a_surj_function(fun, T):
            surj_funs.append(fun)
    return frozenset(surj_funs)

# filters out every set which is no function
def filter_no_function(relations):
    functions = []
    for r in relations:
        if is_a_function(r):
            functions.append(r)
    return frozenset(functions)
    

# filters out every function which is not total
def filter_not_total(functions, S):
    total_funs = []
    for fun in functions:
        if is_a_total_function(fun, S):
            total_funs.append(fun)
    return frozenset(total_funs)


# checks if the function it total 
def is_a_total_function(function, preimage_set):
    if isinstance(preimage_set, InfiniteSet):
        raise EnumerationNotPossibleException()
    preimage = [x[0] for x in function]
    preimage_set2 =  frozenset(preimage)
    return preimage_set == preimage_set2


# checks if the function it surjective
def is_a_surj_function(function, image_set):
    if isinstance(image_set, InfiniteSet):
        raise EnumerationNotPossibleException()
    image = [x[1] for x in function]
    image_set2= frozenset(image) # remove duplicate items
    return image_set == image_set2

# checks if the function it injective
def is_a_inje_function(function):
    image = [x[1] for x in function]
    return not double_element_check(image)

# checks if a relation is a function
def is_a_function(relation):
    preimage_set = [x[0] for x in relation]
    if double_element_check(preimage_set):
        return False
    else:
        return True
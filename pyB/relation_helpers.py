from helpers import *

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
    preimage = [x[0] for x in function]
    preimage_set2 =  frozenset(preimage)
    return preimage_set == preimage_set2


# checks if the function it surjective
def is_a_surj_function(function, image_set):
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
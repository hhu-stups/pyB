from helpers import enumerate_cross_product
from bexceptions import InfiniteSetLengthException
# helper functions for symbolic set operations

# True:  these predicates are syntacticly equal
# True examples:
# {x|x:NAT}=={y|y:NAT}
# False: these predicates are unequal
# no false cases yet implemented
# Exception: I dont know if they are equal (likely case)
# DontKnow examples: 
# {x|x>3 & x<5}=={y|y=4}
# {x|x:NAT & x<200}=={y|y<200 & y:NAT}
# {x|x:INTEGER & x>=0 }=={y|y:NATURAL}
def check_syntacticly_equal(predicate0, predicate1):
    if predicate0.__class__ == predicate1.__class__:
        try:
            length = range(len(predicate0.children))
        except AttributeError:
            return True #clase check was successful and no more children to check
        for index in length:
            child0 = predicate0.children[index]
            child1 = predicate0.children[index]
            if not check_syntacticly_equal(child0, child1):
                return False
        return True
    else:
        message = "ERROR: failed to check if predicates are equal: '%s' and '%s'" %(pretty_print(predicate0),pretty_print(predicate1))
        print message
        raise DontKnowIfEqualException(message)


# This generator returns one relation(-list) between S and T S<-->T.
# S and T can both be symbolic or explicit. If S or T is not finit enumerable, 
# this function throws an exception. It returns no frozensets because some check
# operations (e.g. function property) are more easy on lists.
# TODO: returning a symbolic set here is possible, but needs more tests an
# interpreter modification
def make_explicit_set_of_realtion_lists(S,T):   
    # size = |S|*|T|
    try:
        size = len(S)*len(T)
    except InfiniteSetLengthException:
        size = float("inf")
    # empty relation
    yield frozenset([])
    # calc all permutations
    i=0
    while True:
        for lst in _generate_relation(S,T, i+1, skip=0):
            assert len(lst)==i+1
            yield frozenset(lst)
        i = i+1
        if i==size:
            break


# It is a helper only used by make_explicit_set_of_realtion_lists to generate 
# all combinations/sub-lists of length n.
def _generate_relation(S, T, n, skip):
    # yield one element of all combinations (x,y)
    if n==1:
        for element in enumerate_cross_product(S,T):
            if skip==0:
                yield [element]
            else:
               skip = skip -1
    # yield n elements of all combinations (x,y)
    else:
        assert n>1
        skip2 = 0
        for element in enumerate_cross_product(S,T):
            skip2 = skip2 +1
            if not skip==0:
                skip = skip -1
                continue
            for L in _generate_relation(S, T, n-1, skip2):
                if element in L:
                    continue
                res = L+[element]
                if len(res)==n:
                    yield res
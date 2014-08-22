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
    # convert to explicit  
    if isinstance(S, frozenset):
        left = S
    else:
        left = S.enumerate_all()
    if isinstance(T, frozenset):
        right = T
    else:
        right = T.enumerate_all()
    # TODO: it is also possible to lazy-generate this set,
    #       but the _take generator becomes more complicated if 
    #       its input is a generator instead of a set
    all_combinations = [(x,y) for x in left for y in right]
    # size = |S|*|T|
    size = len(all_combinations)
    # empty relation
    yield []
    # calc all permutations
    for i in range(size):
        for lst in _take(all_combinations, i+1):
            assert len(lst)==i+1
            yield lst


# This function takes n elements of a list and returns them.
# It is a helper only used by make_explicit_set_of_realtion_lists to generate 
# all combinations/sub-lists of length n.
def _take(lst, n):
    # Basecase, take all in a row
    if n==1:
        for k in range(len(lst)):
            yield [lst[k]]
    # take one, remove it, take n-1, concatenate 
    else:
        assert n>1
        for k in range(len(lst)):
            e = lst[k]
            lst2 = list(lst)
            lst2.pop(k)
            for L in _take(lst2, n-1):
                yield L+[e]
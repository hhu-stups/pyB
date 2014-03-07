# -*- coding: utf-8 -*-
from config import *
from ast_nodes import *
from btypes import *
from helpers import flatten, double_element_check, all_ids_known, print_ast
from bexceptions import *

# WARNING: most of the functions in this module should only be used
# if the full set is needed in an expression: The functions are very slow 

# ** THE ENUMERATOR **
# returns a list with "all" possible values of a type
# only works if the typechecking/typing of typeit was successful
def all_values(node, env):
    assert isinstance(node, AIdentifierExpression)
    if node.enum_hint:
        print "USUNG Enum hint", node.enum_hint
        return env.get_value(node.enum_hint)
    atype = env.get_type_by_node(node)
    return all_values_by_type(atype, env)


# generate all values of a type (basetype or composed)
def all_values_by_type(atype, env):
    if isinstance(atype, IntegerType):
        #print env._min_int, env._max_int
        return range(env._min_int, env._max_int+1)
    elif isinstance(atype, BoolType):
        return [True, False]
    elif isinstance(atype, StringType): # FIXME:(#ISSUE 21) only some strings are returned here
        return frozenset(env.all_strings)
    elif isinstance(atype, SetType):
        type_name =  atype.data
        #print type_name
        #env.state_space.get_state().print_bstate()
        value = env.get_value(type_name)
        assert isinstance(value, frozenset)
        return value
    elif isinstance(atype, PowerSetType):
        val_list = all_values_by_type(atype.data, env)
        res = powerset(val_list)
        powerlist = list(res)
        lst = [frozenset(e) for e in powerlist]
        return lst
    elif isinstance(atype, CartType):
        val_pi = all_values_by_type(atype.data[0].data, env)
        val_i = all_values_by_type(atype.data[1].data, env)
        # TODO: test for realtions, seams incomplete
        lst = frozenset([(x,y) for x in val_pi for y in val_i])
        return lst
    string = "Unknown Type / Not Implemented: %s" % atype
    #print string
    raise Exception(string)


# generate all values that statify a predicate 'root'
def try_all_values(root, env, idNodes):
    from interp import interpret
    node = idNodes[0]
    if node.enum_hint:
        print "all values by USUNG Enum hint", node.enum_hint
        all_values = env.get_value(node.enum_hint)
    else:
    	atype = env.get_type_by_node(node)
    	all_values = all_values_by_type(atype, env)
    if len(idNodes)<=1:
        for val in all_values:
            try:
                env.set_value(node.idName, val)
                if interpret(root, env):
                    yield True
            except ValueNotInDomainException:
                continue
    else:
        for val in all_values:
            env.set_value(node.idName, val)
            gen = try_all_values(root, env, idNodes[1:])
            if gen.next():
                yield True
    yield False


# FIXME:(#ISSUE 22) dummy-init of deffered sets
def init_deffered_set(def_set, env):
    # TODO:(#ISSUE 22) retry if no animation possible
    assert isinstance(def_set, ADeferredSet)
    name = def_set.idName
    env.add_ids_to_frame([name])
    lst = []
    for i in range(DEFERRED_SET_ELEMENTS_NUM):
        lst.append(str(i)+"_"+name)
    #print name, lst
    env.set_value(name, frozenset(lst))


def get_image(function, preimage):
    for atuple in function:
        if atuple[0] == preimage:
            return atuple[1]
    raise ValueNotInDomainException(preimage)


# filters out every function which is not injective
def filter_not_injective(functions):
    injective_funs = []
    for fun in functions:
        image = [x[1] for x in fun]
        if not double_element_check(image):
            injective_funs.append(fun)
    return frozenset(injective_funs)


# filters out every function which is not surjective
def filter_not_surjective(functions, T):
    surj_funs = []
    for fun in functions:
        if is_a_surj_function(fun, T):
            surj_funs.append(fun)
    return frozenset(surj_funs)


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


# filters out every set which is no function
def filter_no_function(relations):
    functions = []
    for r in relations:
        if is_a_function(r):
            functions.append(r)
    return frozenset(functions)


# checks if a relation is a function
def is_a_function(relation):
    preimage_set = [x[0] for x in relation]
    if double_element_check(preimage_set):
        return False
    else:
        return True


# returns S<-->T
# WARNING: this could take some time...
def make_set_of_realtions(S,T):
    cartSet = frozenset(((x,y) for x in S for y in T))
    res = powerset(cartSet)
    powerlist = list(res)
    lst = [frozenset(e) for e in powerlist]
    return frozenset(lst)


# from http://docs.python.org/library/itertools.html
# WARNING: this could take some time...
def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    from itertools import chain, combinations
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))




# WARNING: this could take some time...
def all_records(value_dict, result, acc, index):
    if len(value_dict)==index:
        import copy
        result.append(copy.deepcopy(acc)) # FIXME:(#ISSUE 23) Performance-Problems
    else:
        name = list(value_dict.keys())[index]
        values = list(value_dict.values())[index]
        for v in values:
            acc[name] = v
            all_records(value_dict, result, acc, index+1)


# WARNING: this could take some time...
def create_all_seq_w_fixlen(images, length):
    result = []
    basis = len(images)
    noc = basis**length # number of combinations
    for i in range(noc):
        lst = create_sequence(images, i, length)
        result.append(frozenset(lst))
    return result


# WARNING: this could take some time...
def create_sequence(images, number, length):
    result = []
    basis = len(images)
    for i in range(length):
        symbol = tuple([i+1,images[number % basis]])
        result.append(symbol)
        number /= basis
    result.reverse()
    return result

    
# the right side (or both) contain a infinit set
# True  = no normal enumeration possible
# False = Maybe
def contains_infinit_enum(node, env):
    if isinstance(node, ABelongPredicate):
        if isinstance(node.children[1], APartialSurjectionExpression):
            T = node.children[1].children[1]
            isInf = contains_infinit_enum(T, env)
            return isInf
    elif isinstance(node, AIntegerSetExpression) or isinstance(node , ANaturalSetExpression) or isinstance(node, ANatural1SetExpression):
        return True
    elif isinstance(node, AIntSetExpression):
        if (-1*env._min_int+ env._max_int)>TO_MANY_ITEMS:
            return True
    elif isinstance(node, ANat1SetExpression) or isinstance(node, ANatSetExpression):
        if  env._max_int>TO_MANY_ITEMS:
            return True
    return False


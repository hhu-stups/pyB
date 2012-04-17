# -*- coding: utf-8 -*-
from config import *
from ast_nodes import *
from btypes import *
from helpers import flatten, is_flat, double_element_check


# ** THE ENUMERATOR **
# returns a list with "all" possible values of a type
# only works if the typechecking/typing of typeit was successful
def all_values(node, env):
    assert isinstance(node, AIdentifierExpression)
    atype = env.get_type_by_node(node)
    return all_values_by_type(atype, env)


def all_values_by_type(atype, env):
    if isinstance(atype, IntegerType):
        return range(min_int, max_int+1)
    elif isinstance(atype, BoolType):
        return [True, False]
    elif isinstance(atype, SetType):
        type_name =  atype.data
        assert isinstance(env.get_value(type_name), frozenset)
        return env.get_value(type_name)
    elif isinstance(atype, PowerSetType):
        val_list = all_values_by_type(atype.data, env)
        res = powerset(val_list)
        powerlist = list(res)
        lst = [frozenset(e) for e in powerlist]
        return lst
    elif isinstance(atype, CartType):
        val_pi = all_values_by_type(atype.data[0], env)
        val_i = all_values_by_type(atype.data[1], env)
        lst = frozenset(((x,y) for x in val_pi for y in val_i))
        return lst
    string = "Unknown Type / Not Implemented: %s", atype
    raise Exception(string)


def try_all_values(root, env, idNames):
    from interp import interpret
    name = idNames[0]
    atype = env.get_type(name)
    all_values = all_values_by_type(atype, env)
    if len(idNames)<=1:
        for val in all_values:
            env.set_value(name, val)
            if interpret(root, env):
                yield True
    else:
        for val in all_values:
            env.set_value(name, val)
            gen = try_all_values(root, env, idNames[1:])
            if gen.next():
                yield True
    yield False


# FIXME: dummy-init of mch-parameters
def init_mch_param(root, env, mch):
    env.add_ids_to_frame(mch.scalar_params + mch.set_params)
    # TODO: retry if no animation possible
    for name in mch.set_params:
        atype = env.get_type(name)
        assert isinstance(atype, PowerSetType)
        assert isinstance(atype.data, SetType) 
        env.set_value(name, frozenset(["0_"+name,"1_"+name,"2_"+name]))
    for name in mch.scalar_params:
        # page 126
        atype = env.get_type(name)
        assert isinstance(atype, IntegerType) or isinstance(atype, BoolType)
    if not mch.scalar_params==[]:
        assert not mch.aConstraintsMachineClause==None
        pred = mch.aConstraintsMachineClause
        gen = try_all_values(pred, env, mch.scalar_params)
        assert gen.next()


# FIXME: dummy-init of deffered sets
def init_deffered_set(def_set, env):
    # TODO: retry if no animation possible
    assert isinstance(def_set, ADeferredSet)
    name = def_set.idName
    env.add_ids_to_frame([name])
    env.set_value(name, frozenset(["0_"+name,"1_"+name,"2_"+name]))


def get_image(function, preimage):
    for atuple in function:
        if atuple[0] == preimage:
            return atuple[1]
    return None #no image found


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


# FIXME: rename quantified variables!
def set_comprehension_recursive_helper(depth, max_depth, node, env):
    from interp import interpret
    result = []
    pred = node.children[len(node.children) -1]
    idName = node.children[depth].idName
    if depth == max_depth: #basecase
        for i in all_values(node.children[depth], env):
            env.set_value(idName, i)
            if interpret(pred, env):
                result.append(i)
        return result
    else: # recursive call
        for i in all_values(node.children[depth], env):
            env.set_value(idName, i)
            partial_result = set_comprehension_recursive_helper(depth+1, max_depth, node, env)
            for j in partial_result:
                temp = []
                temp.append(i)
                temp.append(j)
                result.append(temp)
        return result


def exist_recursive_helper(depth, max_depth, node, env):
    from interp import interpret
    pred = node.children[len(node.children) -1]
    idName = node.children[depth].idName
    if depth == max_depth: #basecase
        for i in all_values(node.children[depth], env):
            env.set_value(idName, i)
            if interpret(pred, env):
                return True
        return False
    else: # recursive call
        for i in all_values(node.children[depth], env):
            env.set_value(idName, i)
            if exist_recursive_helper(depth+1, max_depth, node, env):
                return True
        return False



def forall_recursive_helper(depth, max_depth, node, env):
    from interp import interpret
    pred = node.children[len(node.children) -1]
    idName = node.children[depth].idName
    if depth == max_depth: #basecase
        for i in all_values(node.children[depth], env):
            env.set_value(idName, i)
            if not interpret(pred, env):
                return False
        return True
    else: # recursive call
        for i in all_values(node.children[depth], env):
            env.set_value(idName, i)
            if not forall_recursive_helper(depth+1, max_depth, node, env):
                return False
        return True



# WARNING: this could take some time...
def all_records(value_dict, result, acc, index):
    if len(value_dict)==index:
        import copy
        result.append(copy.deepcopy(acc))
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


def create_sequence(images, number, length):
    result = []
    basis = len(images)
    for i in range(length):
        symbol = tuple([i+1,images[number % basis]])
        result.append(symbol)
        number /= basis
    result.reverse()
    return result


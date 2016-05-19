# -*- coding: utf-8 -*-

from ast_nodes import *
from bexceptions import EnumerationNotPossibleException
from bexceptions import *
from btypes import *
from config import *
from helpers import flatten, double_element_check, all_ids_known, print_ast, remove_tuples, build_arg_by_type
from pretty_printer import pretty_print
from symbolic_sets import *
from symbolic_functions import *
from symbolic_functions_with_predicate import *


if USE_RPYTHON_CODE:
     from rpython_b_objmodel import W_Integer, W_Object, W_Boolean, W_None, W_Set_Element, W_String, W_Tuple, frozenset

# WARNING: most of the functions in this module should only be used
# if the full set is needed in an expression: The functions are very slow 

# ** THE ENUMERATOR **
# returns a list with "all" possible values of a type
# only works if the typechecking/typing of typeit was successful
def all_values(node, env):
    assert isinstance(node, AIdentifierExpression)
    atype = env.get_type_by_node(node)
    return all_values_by_type(atype, env)


# generate list of all values of a type (basetype or composed)
# the node parameter is used for debugging 
def all_values_by_type(atype, env, node):
    if PRINT_WARNINGS:
        print "\033[1m\033[91mWARNING\033[00m:",pretty_print(node), "caused brute force enumeration. MIN_INT:%s MAX_INT:%s" % (env._min_int, env._max_int)
    if isinstance(atype, IntegerType):
        #print env._min_int, env._max_int
        return range(env._min_int, env._max_int+1)
    elif isinstance(atype, BoolType):
        return [True, False]
    elif isinstance(atype, StringType): # FIXME:(#ISSUE 21) only some strings are returned here
        return frozenset(env.all_strings)
    elif isinstance(atype, SetType):
        type_name =  atype.name
        #print type_name
        #env.state_space.get_state().print_bstate()
        value = env.get_value(type_name)
        assert isinstance(value, frozenset)
        return value
    elif isinstance(atype, PowerSetType):
        val_list = all_values_by_type(atype.data, env, node)
        res = powerset(val_list, node.idName)
        powerlist = list(res)
        lst = [frozenset(e) for e in powerlist]
        #print lst
        return lst
    elif isinstance(atype, CartType):
        val_pi = all_values_by_type(atype.left.data, env, node)
        val_i = all_values_by_type(atype.right.data, env, node)
        # TODO: test for realtions, seams incomplete
        lst = frozenset([(x,y) for x in val_pi for y in val_i])
        return lst
    elif isinstance(atype, StructType):
        value_dict = {}
        for name in atype.dictionary:
            rec_type = atype.dictionary[name]
            values = all_values_by_type(rec_type, env, node)
            value_dict[name]=values
        res = all_records(value_dict)
        lst = []
        for dic in res:
            rec = []
            for entry in dic:
                rec.append(tuple([entry,dic[entry]]))
            lst.append(frozenset(rec))
        return frozenset(lst)
    string = "Unknown Type / Not Implemented: %s" % atype
    #print string
    raise Exception(string)

# Returns list of W_Objects
def all_values_by_type_RPYTHON(atype, env, node):
    if PRINT_WARNINGS:
        print "\033[1m\033[91mWARNING\033[00m:",pretty_print(node), "caused brute force enumeration. MIN_INT:%s MAX_INT:%s" % (env._min_int, env._max_int)
    if isinstance(atype, IntegerType):
        L = []
        for i in range(env._min_int, env._max_int+1):
            L.append(W_Integer(i))
        return L
    elif isinstance(atype, BoolType):
        return [W_Boolean(True), W_Boolean(False)]
    elif isinstance(atype, StringType): # FIXME:(#ISSUE 21) only some strings are returned here
        L = []
        for s in env.all_strings:
           L.append(W_String(s))
        return L
    elif isinstance(atype, SetType):
        type_name =  atype.name
        #print type_name
        #env.state_space.get_state().print_bstate()
        value = env.get_value(type_name)
        assert isinstance(value, frozenset)
        return value.to_list()
    elif isinstance(atype, PowerSetType):
        from enumeration_lazy import generate_powerset
        if PRINT_WARNINGS:
            print "\033[1m\033[91mWARNING\033[00m: (bruteforce) computing powerset of %s %s" % (iterable,name)
        
        val_list = all_values_by_type_RPYTHON(atype.data, env, node)
        card = len(val_list)
        powerlist = [frozenset([])] 
        i = 0     
        while i!=card:
            for lst in generate_powerset(val_list, card=i+1, skip=0):
                assert len(lst)==i+1
                powerlist.append(frozenset(lst))
            i = i+1
        #print powerlist
        return powerlist
    elif isinstance(atype, CartType):
        val_domain = all_values_by_type_RPYTHON(atype.left.data, env, node)
        val_image  = all_values_by_type_RPYTHON(atype.right.data, env, node)
        lst = []
        for x in val_domain:
            for y in val_image:
                lst.append(W_Tuple((x,y)))
        return lst
    string = "Unknown Type / Not Implemented: %s" % atype
    #print string
    raise Exception(string)


def enum_all_values_by_type(env, node):
    atype = env.get_type_by_node(node)
    if USE_RPYTHON_CODE:
        all_values = all_values_by_type_RPYTHON(atype, env, node)
        return all_values
    else:
        all_values = all_values_by_type(atype, env, node)
        return all_values
        

# generate all values that statify a predicate 'root'
def try_all_values(root, env, idNodes):
    for i in _try_all_values(root, env, idNodes, idNodes):
         yield i


def _try_all_values(root, env, idNodes, allNodes):
    if USE_RPYTHON_CODE:
        from rpython_interp import interpret
    else:
        from interp import interpret
    node = idNodes[0]
    all_values = enum_all_values_by_type(env, node)
    
    #print "trying", node.idName, all_values, pretty_print(root)
    if len(idNodes)<=1:
        for val in all_values:
            try:
                env.set_value(node.idName, val)
                #print "trying:"
                #for name in [n.idName for n in allNodes]:
                #     print name, "=", env.get_value(name)
                if USE_RPYTHON_CODE:
                    w_bool = interpret(root, env)
                    if w_bool.bvalue:
                        yield True
                else:
                    if interpret(root, env):
                        yield True
            except ValueNotInDomainException:
                continue
    else:
        for val in all_values:
            env.set_value(node.idName, val)
            gen = _try_all_values(root, env, idNodes[1:], allNodes)
            if gen.next():
                yield True
    yield False

# FIXME:(#ISSUE 22) dummy-init of deffered sets
def init_deffered_set(def_set, env):
    # TODO:(#ISSUE 22) retry if no animation possible
    assert isinstance(def_set, ADeferredSetSet)
    name = def_set.idName
    env.add_ids_to_frame([name])
    lst = []
    for i in range(DEFERRED_SET_ELEMENTS_NUM):
        e_name = str(i)+"_"+name
        if USE_RPYTHON_CODE:
            w_element = W_Set_Element(e_name)
            lst.append(w_element)
        else:
            lst.append(e_name)
    #print name, lst
    env.set_value(name, frozenset(lst))


def gen_all_values(env, varList):
    for dic in _gen_all_values(env, varList, {}):
        yield dic


# yields a dict {String-->W_Object} or {String-->value}
def _gen_all_values(env, varList, dic):
    idNode = varList[0]
    assert isinstance(idNode, AIdentifierExpression)
    atype = env.get_type_by_node(idNode)
    if USE_RPYTHON_CODE:
        domain = all_values_by_type_RPYTHON(atype, env, idNode)
    else:
        domain = all_values_by_type(atype, env, idNode)
    var_name = idNode.idName
    for value in domain:
        dic[var_name] = value
        if len(varList)==1:
            yield dic.copy()
        else:
            for d in _gen_all_values(env, varList[1:], dic):
                yield d
                
    
def get_image_RPython(function, preimage):
    for atuple in function:
        if atuple.tvalue[0].__eq__(preimage):
            return atuple.tvalue[1]
    raise ValueNotInDomainException(preimage)

def get_image(function, preimage):
    for atuple in function:
        if atuple[0] == preimage:
            return atuple[1]
    raise ValueNotInDomainException(preimage)


# returns S<-->T
# WARNING: this could take some time...
def make_set_of_realtions(S,T):
    if PRINT_WARNINGS:
        print "\033[1m\033[91mWARNING\033[00m: (bruteforce) computing set of relations of %s %s " % (S,T)
    cartSet = frozenset(((x,y) for x in S for y in T))
    res = powerset(cartSet)
    powerlist = list(res)
    lst = [frozenset(e) for e in powerlist]
    return frozenset(lst)


# from http://docs.python.org/library/itertools.html
# WARNING: this could take some time...
def powerset(iterable, name=""):
    if PRINT_WARNINGS:
        print "\033[1m\033[91mWARNING\033[00m: (bruteforce) computing powerset of %s %s" % (iterable,name)
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    from itertools import chain, combinations
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

# value dict is a python dict corresponding to the B struct dict
# e.g. struct(Mark:NAT, Good_enough:BOOL)
# becomes value_dict={"Mark":SymbolicNatSet, "Good_enough":frozenset([True,False])}
def all_records(value_dict):
    result = []
    _all_records(value_dict, result, {}, 0) # side-effect: fills result
    return result
    
# WARNING: this could take some time...
def _all_records(value_dict, result, acc, index):
    if len(value_dict)==index:
        clone = {}
        for key in acc:
            value = acc[key]
            if isinstance(value, W_Object):
                clone[key] = value.clone()
            else:
                clone[key] = value
        result.append(clone) # TODO:(#ISSUE 23) was solved
    else:
        name = list(value_dict.keys())[index]
        values = list(value_dict.values())[index]
        #if isinstance(values, SymbolicSet):
        #    values = values.enumerate_all()
        for v in values:
            acc[name] = v
            _all_records(value_dict, result, acc, index+1)


# WARNING: this could take some time...
def create_all_seq_w_fixlen(images, length):
    result = []
    basis = len(images)
    assert length >=0
    noc = 1 # number of combinations
    for i in range(length):
        noc = noc * basis
    #noc = basis**length  # NOT RPython
    for i in range(noc):
        lst = _create_sequence(images, i, length)
        result.append(frozenset(lst))
    return result


# WARNING: this could take some time...
def _create_sequence(images, number, length):
    assert isinstance(images, list)
    if PRINT_WARNINGS:
        print "\033[1m\033[91mWARNING\033[00m: (bruteforce) computing all sequences of %s" % images
    result = []
    basis = len(images)
    for i in range(length):
        index = number % basis
        image = images[index]
        if USE_RPYTHON_CODE:
            symbol = W_Tuple((W_Integer(i+1), image))
        else:
            symbol = tuple([i+1, image])
        result.append(symbol)
        number /= basis
    result.reverse()
    return result

    
# the right side (or both) contain a infinit set
# True  = no normal enumeration possible
# False = Maybe
#def contains_infinit_enum(node, env):
#    #print "inf?:",node.children[1]
#    if isinstance(node, AMemberPredicate):
#        if isinstance(node.children[1], APartialSurjectionExpression):
#            T = node.children[1].children[1]
#            isInf = contains_infinit_enum(T, env)
#            return isInf
#        #elif isinstance(node.children[1], AMultOrCartExpression):
#        #    infR = contains_infinit_enum(node.children[1].children[0], env)
#        #    infL = contains_infinit_enum(node.children[1].children[1], env)
#        #    return infR or infL
#    elif isinstance(node, AIntegerSetExpression) or isinstance(node , ANaturalSetExpression) or isinstance(node, ANatural1SetExpression):
#        return True
#    elif isinstance(node, AIntSetExpression):
#        if (-1*env._min_int+ env._max_int)>TOO_MANY_ITEMS:
#            return True
#    elif isinstance(node, ANat1SetExpression) or isinstance(node, ANatSetExpression):
#        if  env._max_int>TOO_MANY_ITEMS:
#            return True
#    return False

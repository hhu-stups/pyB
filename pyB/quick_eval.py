# -*- coding: utf-8 -*-
from ast_nodes import *
from abstract_interpretation import var_constraint_by_predicate
from btypes import *
from config import USE_RPYTHON_CODE
from pretty_printer import pretty_print
from symbolic_sets import LargeSet, SymbolicSet
from symbolic_functions import *
from symbolic_functions_with_predicate import *

if USE_RPYTHON_CODE:
     from rpython_b_objmodel import frozenset

# This function is used in an Belong(member)-Node. x : S
# It recursively checks if the right side(S) can 'generate' the element(x) of the left side.
# This function is quicker than fully generating the (potentially large) set (S) on the right side.
# If some sets of the right side are 'generated' by this function then only 
# if this shouldnt take much time and the full set is needed anyway
# returntype: boolean
def quick_member_eval(ast, env, element):
    if USE_RPYTHON_CODE:
        from rpython_interp import interpret
    else:
        from interp import interpret
    # Base case of recursion
    if isinstance(element, int) or isinstance(element, str):
        if isinstance(ast, ANaturalSetExpression):
            assert isinstance(element, int) # if False: typechecking Bug
            return element >=0
        if isinstance(ast, ANatural1SetExpression):
            assert isinstance(element, int) # if False: typechecking Bug
            return element >0
        elif isinstance(ast, AIntegerSetExpression):
            assert isinstance(element, int)
            return True
        elif isinstance(ast, ANatSetExpression):
            assert isinstance(element, int)
            return element >=0 and element <= env._max_int
        elif isinstance(ast, ANat1SetExpression):
            assert isinstance(element, int)
            return element >0 and element <= env._max_int
        elif isinstance(ast, AIntSetExpression):
            assert isinstance(element, int)
            return element >= env._min_int and element <= env._max_int
        elif isinstance(ast, AStringSetExpression):
            assert isinstance(element, str)
            return True
        # fallback: enumerate_all right side. This 'should' never happen...
        S = interpret(ast, env)
        #print "quck eval of:", element, val
        #S = list(val)
        #print element,S # DEBUG
        return element in S
    elif isinstance(element, SymbolicLambda):
        # only one special case
        #TODO: replace with general case
        #TODO: support lambdas with more than one arg
        # XXX: this line could case a infinit computation!
        aSet = interpret(ast, env)
        if (not isinstance(aSet, SymbolicRelationSet)) or isinstance(aSet, SymbolicPartialInjectionSet) or isinstance(aSet, SymbolicTotalInjectionSet) or isinstance(aSet, SymbolicPartialSurjectionSet) or isinstance(aSet, SymbolicTotalSurjectionSet) or isinstance(aSet, SymbolicTotalBijectionSet) or isinstance(aSet, SymbolicPartialBijectionSet):
            # XXX: Dont know how to check this for every lambda 
            print "Error: Unhandeled case: lambda eval - brute force lambda set enum"
            element = element.enumerate_all()
            result = element in aSet  
            return result
        else:
            types = []
            for var in element.variable_list:
                atype = env.get_type_by_node(var) 
                if types==[]:
                    types = atype
                else:
                    types = tuple([types,atype])
            image_type = env.get_lambda_type_by_node(element.node)
            domain_element = False
            image_element  = False
            domain_element = types in aSet.left_set
            image_element  = image_type in aSet.right_set
            #print types, " in ", aSet.left_set, domain_element
            #print "image:",image_type, " in ", aSet.right_set, image_element
            if domain_element and image_element:
                # checking if a function is total is done via an approximation:
                # if no constraint of the domain is found, the answer is yes, 
                # otherwise the answer is "dont know"
                if isinstance(aSet, ATotalFunctionExpression):
                    # TODO: call check
                    if len(element.variable_list)==1:
                        # False or Dont know
                        vcbp = var_constraint_by_predicate(element.variable_list, element.predicate)
                else:
                    return True            
        # else use other checks 
    #TODO:(#ISSUE 18) no quick eval, can crash
    if isinstance(element, Node):
        element = interpret(element, env)
    aSet = interpret(ast, env)
    #print "element, set:", element, aSet
    return element in aSet                                             



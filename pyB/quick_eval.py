# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from pretty_printer import pretty_print
from symbolic_sets import *
from abstract_interpretation import var_constraint_by_predicate

# This function is used in an Belong(member)-Node. x : S
# It recursively checks if the right side(S) can 'generate' the element(x) of the left side.
# This function is quicker than fully generating the (potentially large) set (S) on the right side.
# If some sets of the right side are 'generated' by this function then only 
# if this shouldnt take much time and the full set is needed anyway
def quick_member_eval(ast, env, element):
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
        # fallback: enumerate right side. This 'should' never happen...
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
        if (not isinstance(aSet, SymbolicRelationSet)) or isinstance(aSet, (SymbolicPartialInjectionSet, SymbolicTotalInjectionSet, SymbolicPartialSurjectionSet, SymbolicTotalSurjectionSet, SymbolicTotalBijectionSet, SymbolicPartialBijectionSet)):
           # XXX: Dont know how to check this for every lambda 
           pass
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

    if isinstance(ast, ARelationsExpression):
        #S = interpret(ast.children[0], env)
        #T = interpret(ast.children[1], env)
        for tup in element: # a relation is a set of 2-tuples
            if (not quick_member_eval(ast.children[0], env, tup[0])) or (not quick_member_eval(ast.children[1], env, tup[1])):
                return False
        return True 
    elif isinstance(ast, APartialFunctionExpression):
        #S = interpret(ast.children[0], env)
        #T = interpret(ast.children[1], env)
        preimage = []
        image = []
        for tup in element:
            preimage.append(tup[0])
            image.append(tup[1])
            if (not quick_member_eval(ast.children[0], env, tup[0])) or (not quick_member_eval(ast.children[1], env, tup[1])):
                return False
        if not (len(set(preimage))==len(preimage)): # test function attribute
            return False
        return True
    elif isinstance(ast, APartialInjectionExpression):
        #S = interpret(ast.children[0], env)
        #T = interpret(ast.children[1], env)
        preimage = []
        image = []
        for tup in element:
            preimage.append(tup[0])
            image.append(tup[1])
            if (not quick_member_eval(ast.children[0], env, tup[0])) or (not quick_member_eval(ast.children[1], env, tup[1])):
                return False
        if not (len(set(preimage))==len(preimage)): # test function attribute
            return False
        if not (len(set(image))==len(image)): # test injection
            return False
        return True
    elif isinstance(ast, APartialSurjectionExpression):
        #S = interpret(ast.children[0], env)
        T = interpret(ast.children[1], env)
        preimage = []
        image = []
        for tup in element:
            preimage.append(tup[0])
            image.append(tup[1])
            if (not quick_member_eval(ast.children[0], env, tup[0])) or (not quick_member_eval(ast.children[1], env, tup[1])):
                return False
        if not (len(set(preimage))==len(preimage)): # test function attribute
            return False
        if not set(list(T))==set(image): 
            return False # test surjection
        return True
    elif isinstance(ast, APartialBijectionExpression):
        #S = interpret(ast.children[0], env)
        T = interpret(ast.children[1], env)
        preimage = []
        image = []
        for tup in element:
            preimage.append(tup[0])
            image.append(tup[1])
            if (not quick_member_eval(ast.children[0], env, tup[0])) or (not quick_member_eval(ast.children[1], env, tup[1])):
                return False
        if not (len(set(preimage))==len(preimage)): # test function attribute
            return False
        if not set(list(T))==set(image): # test surjection
            return False                    
        if not (len(set(image))==len(image)): # test injection
            return False
        return True
    elif isinstance(ast, ATotalFunctionExpression):
        S = interpret(ast.children[0], env)
        #T = interpret(ast.children[1], env)
        preimage = []
        #image = []
        #print element
        for tup in element:
            preimage.append(tup[0])
            #image.append(tup[1])
            if (not quick_member_eval(ast.children[0], env, tup[0])) or (not quick_member_eval(ast.children[1], env, tup[1])):
                return False
        if not (len(set(preimage))==len(preimage)): # test function attribute
            return False
        if not set(list(S))==set(preimage): # test total 
            return False
        return True  
    elif isinstance(ast, ATotalInjectionExpression):
        S = interpret(ast.children[0], env)
        #T = interpret(ast.children[1], env)
        preimage = []
        image = []
        for tup in element:
            preimage.append(tup[0])
            image.append(tup[1])
            if (not quick_member_eval(ast.children[0], env, tup[0])) or (not quick_member_eval(ast.children[1], env, tup[1])):
                return False
        if not (len(set(preimage))==len(preimage)): # test function attribute
            return False
        if not (len(set(image))==len(image)): # test injection
            return False            
        if not set(list(S))==set(preimage): # test total 
            return False 
        return True   
    elif isinstance(ast, ATotalSurjectionExpression):
        S = interpret(ast.children[0], env)
        T = interpret(ast.children[1], env)
        preimage = []
        image = []
        for tup in element:
            preimage.append(tup[0])
            image.append(tup[1])
            if (not quick_member_eval(ast.children[0], env, tup[0])) or (not quick_member_eval(ast.children[1], env, tup[1])):
                return False
        if not (len(set(preimage))==len(preimage)): # test function attribute
            return False         
        if not set(list(S))==set(preimage): # test total 
            return False 
        if not set(list(T))==set(image): # test surjection
            return False            
        return True
    elif isinstance(ast, ATotalBijectionExpression):
        S = interpret(ast.children[0], env)
        T = interpret(ast.children[1], env)
        preimage = []
        image = []
        for tup in element:
            preimage.append(tup[0])
            image.append(tup[1])
            if (not quick_member_eval(ast.children[0], env, tup[0])) or (not quick_member_eval(ast.children[1], env, tup[1])):
                return False
        if not (len(set(preimage))==len(preimage)): # test function attribute
            return False         
        if not set(list(S))==set(preimage): # test total
            return False 
        if not set(list(T))==set(image): # test surjection
            return False 
        if not (len(set(image))==len(image)): # test injection
            return False
        return True
    elif isinstance(ast, ASeqExpression) or isinstance(ast, ASeq1Expression):
        preimage = []
        image = []
        if isinstance(ast, ASeq1Expression) and element==frozenset([]):
            return False
        for tup in element:
            assert isinstance(tup[0], int)
            preimage.append(tup[0])
            if not quick_member_eval(ast.children[0], env, tup[1]):
                return False
        if not (len(set(preimage))==len(preimage)): # test function attribute
            return False        
        if not set(range(1,len(preimage)+1))==set(preimage): # test sequence
            return False 
        return True
    elif isinstance(ast, AIseqExpression) or isinstance(ast, AIseq1Expression):
        preimage = []
        image = []
        if isinstance(ast, AIseq1Expression) and element==frozenset([]):
            return False
        for tup in element:
            assert isinstance(tup[0], int)
            preimage.append(tup[0])
            image.append(tup[1])
            if not quick_member_eval(ast.children[0], env, tup[1]):
                return False
        if not (len(set(preimage))==len(preimage)): # test function attribute
            return False        
        if not set(range(1,len(preimage)+1))==set(preimage): # test sequence
            return False
        if not (len(set(image))==len(image)): # test injective
            return False 
        return True
    elif isinstance(ast, APermExpression):
        preimage = []
        image = []
        for tup in element:
            assert isinstance(tup[0], int)
            preimage.append(tup[0])
            image.append(tup[1])
            if not quick_member_eval(ast.children[0], env, tup[1]):
                return False
        if not (len(set(preimage))==len(preimage)): # test function attribute
            return False        
        if not set(range(1,len(preimage)+1))==set(preimage): # test sequence
            return False
        if not (set(image)==interpret(ast.children[0], env)): # test bijection/perm
            return False 
        return True            
    elif isinstance(ast, APowSubsetExpression):
        for e in element: # element is a Set ;-)
            # TODO: empty set test 
            if not quick_member_eval(ast.children[0], env, e):
                return False
        return True
    elif isinstance(ast, APow1SubsetExpression):
        if element==frozenset(frozenset([])):
            return False
        for e in element: # element is a Set ;-)
            if not quick_member_eval(ast.children[0], env, e):
                return False
        return True
    elif isinstance(ast, AMultOrCartExpression):
        if (not quick_member_eval(ast.children[0], env, element[0])) or (not quick_member_eval(ast.children[1], env, element[1])):
            return False
        return True
    else:
        #TODO:(#ISSUE 18) no quick eval, can crash
        aSet = interpret(ast, env)
        #print "element, set:", element, aSet
        return element in aSet                                             


# checks if the element (maybe a predicate) can generated of the infinite set on the right side
def infinity_belong_check(node, env):
    assert isinstance(node, ABelongPredicate)
    if isinstance(node.children[1], APartialSurjectionExpression):
        if isinstance(node.children[0], AEmptySetExpression):
            return False
        elif isinstance(node.children[0], AIdentifierExpression):
            value = env.get_value(node.children[0].idName) # TODO: Later this could return "somthing infinite"
            return False #TODO: eval infinite value (not implemented now)
    string = pretty_print(node)
    print "WARNING: CHECK OF INFINITE SET NOT IMPLEMENTED! CAN NOT EVAL:", string
    print "default return: FALSE"
    return False # TODO:(#ISSUE 13) add more cases
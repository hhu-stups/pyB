# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *

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
        S = list(interpret(ast, env))
        #print element,S # DEBUG
        return element in S

    if isinstance(ast, ARelationsExpression):
        #S = list(interpret(ast.children[0], env))
        #T = list(interpret(ast.children[1], env))
        for tup in element: # a relation is a set of 2-tuples
            if (not quick_member_eval(ast.children[0], env, tup[0])) or (not quick_member_eval(ast.children[1], env, tup[1])):
                return False
        return True 
    elif isinstance(ast, APartialFunctionExpression):
        #S = list(interpret(ast.children[0], env))
        #T = list(interpret(ast.children[1], env))
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
        #S = list(interpret(ast.children[0], env))
        #T = list(interpret(ast.children[1], env))
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
        #S = list(interpret(ast.children[0], env))
        T = list(interpret(ast.children[1], env))
        preimage = []
        image = []
        for tup in element:
            preimage.append(tup[0])
            image.append(tup[1])
            if (not quick_member_eval(ast.children[0], env, tup[0])) or (not quick_member_eval(ast.children[1], env, tup[1])):
                return False
        if not (len(set(preimage))==len(preimage)): # test function attribute
            return False
        if not set(T)==set(image): 
            return False # test surjection
        return True
    elif isinstance(ast, APartialBijectionExpression):
        #S = list(interpret(ast.children[0], env))
        T = list(interpret(ast.children[1], env))
        preimage = []
        image = []
        for tup in element:
            preimage.append(tup[0])
            image.append(tup[1])
            if (not quick_member_eval(ast.children[0], env, tup[0])) or (not quick_member_eval(ast.children[1], env, tup[1])):
                return False
        if not (len(set(preimage))==len(preimage)): # test function attribute
            return False
        if not set(T)==set(image): # test surjection
            return False 					
        if not (len(set(image))==len(image)): # test injection
            return False
        return True
    elif isinstance(ast, ATotalFunctionExpression):
        S = list(interpret(ast.children[0], env))
        #T = list(interpret(ast.children[1], env))
        preimage = []
        image = []
        for tup in element:
            preimage.append(tup[0])
            image.append(tup[1])
            if (not quick_member_eval(ast.children[0], env, tup[0])) or (not quick_member_eval(ast.children[1], env, tup[1])):
                return False
        if not (len(set(preimage))==len(preimage)): # test function attribute
            return False
        if not set(S)==set(preimage): # test total 
            return False
        return True  
    elif isinstance(ast, ATotalInjectionExpression):
        S = list(interpret(ast.children[0], env))
        #T = list(interpret(ast.children[1], env))
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
        if not set(S)==set(preimage): # test total 
            return False 
        return True   
    elif isinstance(ast, ATotalSurjectionExpression):
        S = list(interpret(ast.children[0], env))
        T = list(interpret(ast.children[1], env))
        preimage = []
        image = []
        for tup in element:
            preimage.append(tup[0])
            image.append(tup[1])
            if (not quick_member_eval(ast.children[0], env, tup[0])) or (not quick_member_eval(ast.children[1], env, tup[1])):
                return False
        if not (len(set(preimage))==len(preimage)): # test function attribute
            return False         
        if not set(S)==set(preimage): # test total 
            return False 
        if not set(T)==set(image): # test surjection
            return False 			
        return True
    elif isinstance(ast, ATotalBijectionExpression):
        S = list(interpret(ast.children[0], env))
        T = list(interpret(ast.children[1], env))
        preimage = []
        image = []
        for tup in element:
            preimage.append(tup[0])
            image.append(tup[1])
            if (not quick_member_eval(ast.children[0], env, tup[0])) or (not quick_member_eval(ast.children[1], env, tup[1])):
                return False
        if not (len(set(preimage))==len(preimage)): # test function attribute
            return False         
        if not set(S)==set(preimage): # test total
            return False 
        if not set(T)==set(image): # test surjection
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
        #XXX no quick eval, can crash
        aSet = interpret(ast, env)
        if isinstance(element,str) and aSet=="":
            return True # FIXME: hack
        return element in aSet                                             


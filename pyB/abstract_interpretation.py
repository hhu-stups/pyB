from ast_nodes import *
from config import TO_MANY_ITEMS
import math


# TODO: support more than one variable (which is constraint by the predicate to be analysed
# this approximation is still not good. Eg. x/:NAT   
# TODO: enable caching if the predicate is "state-indipendent" i.e if the computation time
# is constant. 

# This function returns a number or inf. These value only make sense if the predicate
# is constraining a variable, which is element of a set i.e predicate defines a set
# This method is used to select sub-predicates to generate constraint-"small" value 
# domains of variables to avoid a set explosion during enumeration. It only checks the 
# effort need for computation. If a predicate constrains a variable is checked by an other
# function  
def estimate_computation_time(predicate, env):
    assert isinstance(predicate, Predicate)
    time = _abs_int(predicate, env)
    return time


# helper for estimate_computation_time
# nodes which can not occur inside predicates, are omitted.
# the implementation covers some special cases and one default case
# TODO: AComprehensionSetExpression AExistentialQuantificationPredicate, 
#       AUniversalQuantificationPredicate, ALambdaExpression
# TODO: ARecEntry, AStructExpression, ARecordFieldExpression, ARecExpression
# TODO: AFirstProjectionExpression, ASecondProjectionExpression, 
#       AParallelProductExpression, AQuantifiedIntersectionExpression, 
#       AQuantifiedUnionExpression
def _abs_int(node, env):
    #print node
    if isinstance(node, ADisjunctPredicate):
        time0 =  _abs_int(node.children[0], env)
        time1 =  _abs_int(node.children[1], env)
        # a "test-set" generator will choose the "quicker" path
        if time0<time1:
            return time1+1
        else: 
            return time0+1
    elif isinstance(node, ABoolSetExpression):
        return 2
    elif isinstance(node, (APowSubsetExpression, APow1SubsetExpression)):
        time = _abs_int(node.children[0], env)
        if time>=math.log(TO_MANY_ITEMS,2):
            return float("inf")
        else:
            return 2**(exp0)
    elif isinstance(node, (AIntegerSetExpression, ANaturalSetExpression, ANatural1SetExpression, AStringSetExpression)):
        return float("inf")
    elif isinstance(node, (ANatSetExpression, ANat1SetExpression)):
        return env._max_int
    elif isinstance(node, AIntSetExpression):
        return env._min_int*-1 + env._max_int
    ### Relations, functions, sequences
    elif isinstance(node, (APartialFunctionExpression, ARelationsExpression, APartialFunctionExpression, ATotalFunctionExpression, APartialInjectionExpression, ATotalInjectionExpression, APartialSurjectionExpression, ATotalSurjectionExpression, ATotalBijectionExpression, APartialBijectionExpression, ASeqExpression, ASeq1Expression, AIseqExpression, AIseq1Expression, APermExpression)):
        time0 = _abs_int(node.children[0], env)
        time1 = _abs_int(node.children[1], env)
        exp0  = time0*time1 
        if exp0>=math.log(TO_MANY_ITEMS,2):
            return float("inf")
        else:
            return 2**(exp0)
    ### Leafs
    elif isinstance(node, (AIdentifierExpression, APrimedIdentifierExpression, AIntegerExpression, AStringExpression, AEmptySetExpression, AEmptySequenceExpression, ATrueExpression, AFalseExpression, AMinIntExpression, AMaxIntExpression)):
        return 1
    ### Default:
    else:
        time = 1
        for child in node.children:
           time += _abs_int(child, env)
        return time

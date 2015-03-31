from ast_nodes import *
from config import TOO_MANY_ITEMS
from pretty_printer import pretty_print
import math


# TODO: support more than one variable (which is constraint by the predicate to be analysed
# this approximation is still not good. Eg. x/:NAT   
# TODO: enable caching if the predicate is "state-indipendent" i.e if the computation time
# is constant. 

# This function returns a number or inf. These value only make sense if the predicate
# is constraining a variable, which is element of a set i.e predicate defines a set
# This method is used to select sub-predicates to generate constraint-"small" value 
# domains of variables to avoid a set explosion during enumeration. It only checks the 
# effort need for computation. If a predicate constrains a variable, is checked by another
# function  
def estimate_computation_time(predicate, env, interpreter_callable):
    assert isinstance(predicate, Predicate)
    time = _abs_int(predicate, env, interpreter_callable)
    return time


# helper for estimate_computation_time
# nodes which can not occur inside predicates, are omitted.
# the implementation covers some special cases and one default case.
# the result is used by a test_set_generator (see constraint solving)
#
# TODO: AComprehensionSetExpression AExistsPredicate, 
#       AUniversalQuantificationPredicate, ALambdaExpression
# TODO: ARecEntry, AStructExpression, ARecordFieldExpression, ARecExpression
# TODO: AFirstProjectionExpression, ASecondProjectionExpression, 
#       AParallelProductExpression, AQuantifiedIntersectionExpression, 
#       AQuantifiedUnionExpression
# FIXME: C578.EML.014/360_002 cause'str' minus 'int' in leaf case
# FIXME: AMinusOrSetSubtractExpression instead of AIntegerExpression
def _abs_int(node, env, ic):
    #print node
    if isinstance(node, ABoolSetExpression):
        return 2
    elif isinstance(node, (APowSubsetExpression, APow1SubsetExpression)):
        time = _abs_int(node.children[0], env, ic)
        if time>=math.log(TOO_MANY_ITEMS,2):
            return float("inf")
        else:
            return 2**(time)
    elif isinstance(node, (AIntegerSetExpression, ANaturalSetExpression, ANatural1SetExpression, AStringSetExpression)):
        return float("inf")
    elif isinstance(node, (ANatSetExpression, ANat1SetExpression)):
        return env._max_int
    elif isinstance(node, AIntSetExpression):
        return env._min_int*-1 + env._max_int
    elif isinstance(node, AMultOrCartExpression):
        time0 = _abs_int(node.children[0], env, ic)
        time1 = _abs_int(node.children[1], env, ic)    
        prod = time0*time1
        if prod>TOO_MANY_ITEMS:
            return float("inf")
        else:
            return prod

    ### Relations, functions, sequences
    elif isinstance(node, (APartialFunctionExpression, ARelationsExpression, APartialFunctionExpression, ATotalFunctionExpression, APartialInjectionExpression, ATotalInjectionExpression, APartialSurjectionExpression, ATotalSurjectionExpression, ATotalBijectionExpression, APartialBijectionExpression, ASeqExpression, ASeq1Expression, AIseqExpression, AIseq1Expression, APermExpression)):
        time0 = _abs_int(node.children[0], env, ic)
        time1 = _abs_int(node.children[1], env, ic)
        exp0  = time0*time1 
        if exp0>=math.log(TOO_MANY_ITEMS,2):
            return float("inf")
        else:
            return 2**(exp0)
    ### Leafs
    elif isinstance(node, (AIdentifierExpression, APrimedIdentifierExpression, AIntegerExpression, AStringExpression, AEmptySetExpression, AEmptySequenceExpression, ABooleanTrueExpression, ABooleanFalseExpression, AMinIntExpression, AMaxIntExpression)):
        return 1
    elif isinstance(node, AIntervalExpression):
        left_node  = node.children[0]
        right_node = node.children[1]
        time0 = _abs_int(left_node, env, ic)
        time1 = _abs_int(right_node, env, ic)
        #print time0, time1
        if time0<TOO_MANY_ITEMS and time1<TOO_MANY_ITEMS:
            # BUG: if this interpreter call cause the lookup of an unset variable,
            # this will crash.
            val0 = ic(left_node, env)
            val1 = ic(right_node, env)
        else:
            # over approximation to avoid long interpretation
            val0 = env._min_int
            val1 = env._max_int 
        return val1-val0
    ### "meet"
    # Werden hier abstrakte Interpretation und Datenflussanalyse durcheinander geworfen? Denk noch mal drueber nach....
    elif isinstance(node, AConjunctPredicate):
        # this information is used to generate test_sets for {x|P0(x) & P1(x)}
        # the predicate is a candidate, if P0 OR P1 is finite 
        time0 = _abs_int(node.children[0], env, ic)
        time1 = _abs_int(node.children[1], env, ic)
        if time0<time1:
            return time0
        return time1
    ### Default:
    else:
        time = 1
        for child in node.children:
           time += _abs_int(child, env, ic)
        return time


# checks if a variabel is constraint by a predicate.
# returns False (nothing found) or Dont know       
def var_constraint_by_predicate(var_node, predicate):
    #print predicate, var_node
    return "Dont know"

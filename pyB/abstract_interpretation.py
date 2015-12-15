from ast_nodes import *
from bexceptions import BTypeException
from config import TOO_MANY_ITEMS, USE_RPYTHON_CODE
from pretty_printer import pretty_print
import math

if USE_RPYTHON_CODE:
    from rpython_b_objmodel import frozenset
    
class InfiniteConstraintException(BTypeException):
    def __init__(self, value):
        self.value = str(value)
    
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
def estimate_computation_time(predicate, env):
    assert isinstance(predicate, Predicate)
    time = _abstr_eval(predicate, env)
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
def _abstr_eval(node, env):
    #print node
    if isinstance(node, ABoolSetExpression):
        return 2
    elif isinstance(node, APowSubsetExpression) or isinstance(node, APow1SubsetExpression):
        time = _abstr_eval(node.children[0], env)
        #if time>=math.log(TOO_MANY_ITEMS,2):
        if time>=22: # FIXME: math.log is not rpython
            return TOO_MANY_ITEMS
        else:
            # RPython does not support 2**(time)
            assert time >=0
            result = 1
            for i in range(time):
                result = result *2
            return result
    # NATURAL, NATURAL1, INTEGER, STRING
    elif isinstance(node, AIntegerSetExpression) or isinstance(node, ANaturalSetExpression) or isinstance(node, ANatural1SetExpression) or isinstance(node, AStringSetExpression):
        raise InfiniteConstraintException("")
        # TODO: infinite exception
        #return TOO_MANY_ITEMS
    elif isinstance(node, ANatSetExpression) or isinstance(node, ANat1SetExpression):
        return env._max_int
    elif isinstance(node, AIntSetExpression):
        return env._min_int*-1 + env._max_int
    elif isinstance(node, AMultOrCartExpression):
        time0 = _abstr_eval(node.children[0], env)
        time1 = _abstr_eval(node.children[1], env)    
        prod = time0*time1
        if prod>TOO_MANY_ITEMS:
            return TOO_MANY_ITEMS
        else:
            return prod

    ### Relations, functions, sequences
    elif isinstance(node, APartialFunctionExpression) or isinstance(node, ARelationsExpression) or isinstance(node, APartialFunctionExpression) or isinstance(node, ATotalFunctionExpression) or isinstance(node, APartialInjectionExpression) or isinstance(node, ATotalInjectionExpression) or isinstance(node, APartialSurjectionExpression) or isinstance(node, ATotalSurjectionExpression) or isinstance(node, ATotalBijectionExpression) or isinstance(node, APartialBijectionExpression) or isinstance(node, ASeqExpression) or isinstance(node, ASeq1Expression) or isinstance(node, AIseqExpression) or isinstance(node, AIseq1Expression) or isinstance(node, APermExpression):
        time0 = _abstr_eval(node.children[0], env)
        time1 = _abstr_eval(node.children[1], env)
        exp0  = time0*time1
        #if exp0>=math.log(TOO_MANY_ITEMS,2):
        if exp0>=22: # math.log is not rpython
            return TOO_MANY_ITEMS
        else:
            #return 2**(exp0)
            assert exp0 >=0
            result = 1
            for i in range(exp0):
                result = result *2
            return result
    ### Leafs
    elif isinstance(node, AIdentifierExpression) or isinstance(node, APrimedIdentifierExpression) or isinstance(node, AIntegerExpression) or isinstance(node, AStringExpression) or isinstance(node, AEmptySetExpression) or isinstance(node, AEmptySequenceExpression) or isinstance(node, ABooleanTrueExpression) or isinstance(node, ABooleanFalseExpression) or isinstance(node, AMinIntExpression) or isinstance(node, AMaxIntExpression):
        return 1
    elif isinstance(node, AIntervalExpression):
        left_node  = node.children[0]
        right_node = node.children[1]
        time0 = _abstr_eval(left_node, env)
        time1 = _abstr_eval(right_node, env)
        #print time0, time1
        if time0<TOO_MANY_ITEMS and time1<TOO_MANY_ITEMS:
            # TODO: This block is not O(n)  - n ast nodes
            if USE_RPYTHON_CODE:
                from rpython_interp import interpret
                v0 = interpret(left_node, env)
                v1 = interpret(right_node, env)
                val0 = v0.ivalue
                val1 = v1.ivalue
            else:
                from interp import interpret
                val0 = interpret(left_node, env)
                val1 = interpret(right_node, env)
        else:
            # over approximation to avoid long interpretation
            val0 = env._min_int
            val1 = env._max_int
        # BUGFIX: if this interpreter call cause the lookup of an unset variable,
        # this will crash. This is a quick fix.
        if not isinstance(val0, int) or not isinstance(val1, int):
            return TOO_MANY_ITEMS
        return val1-val0
    ### "meet"
    # Werden hier abstrakte Interpretation und Datenflussanalyse durcheinander geworfen? Denk noch mal drueber nach....
    elif isinstance(node, AConjunctPredicate):
        # this information is used to generate test_sets for {x|P0(x) & P1(x)}
        # the predicate is a candidate, if P0 OR P1 is finite
        inf0 = False
        inf1 = False
        try: 
            time0 = _abstr_eval(node.children[0], env)
        except InfiniteConstraintException:
            inf0  = True
            time0 = TOO_MANY_ITEMS
        try:
            time1 = _abstr_eval(node.children[1], env)
        except InfiniteConstraintException:
            inf1  = True
            time1 = TOO_MANY_ITEMS
            
        if inf0 and inf1:
            raise InfiniteConstraintException("")
        if time0<time1:
            return time0
        return time1
    ### Default:
    else:
        time = 1
        for child in node.children:
           time += _abstr_eval(child, env)
        return time


# checks if a variabel is constraint by a predicate.
# returns False (nothing found) or Dont know       
def var_constraint_by_predicate(var_node, predicate):
    #print predicate, var_node
    return "Dont know"

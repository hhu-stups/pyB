from ast_nodes import *
#from bexceptions import ValueNotInDomainException
#from constrainsolver import calc_possible_solutions
#from enumeration import get_image
from helpers import flatten, double_element_check, find_assignd_vars, print_ast, all_ids_known, find_var_nodes, conj_tree_to_conj_list
#from symbolic_sets import *
from typing import type_check_predicate, type_check_expression


# That the result of node evaluation is an integer,  must be ensured BY THE CALLER!
# 
# For example in "x + y * z" the '*' is a multiplication, if this expression has passed the 
# type checker. A Bug inside the type checker will cause a bug here!
# The function always returns an integer, to enable RPython-translation to C
def eval_int_expression(node, env):
    if isinstance(node, AIntegerExpression):
        # TODO: add flag in config.py to enable switch to long integer here
        return node.intValue
    #elif isinstance(node, AMinExpression):
    #    aSet = interpret(node.children[0], env)
    #    return min(list(aSet))
    #elif isinstance(node, AMaxExpression):
    #    aSet = interpret(node.children[0], env)
    #    return max(list(aSet))
    elif isinstance(node, AAddExpression):
        expr1 = eval_int_expression(node.get(0), env)
        expr2 = eval_int_expression(node.get(1), env)
        return expr1 + expr2
    elif isinstance(node, AMinusOrSetSubtractExpression):
        expr1 = eval_int_expression(node.get(0), env)
        expr2 = eval_int_expression(node.get(1), env)
        return expr1 - expr2
    elif isinstance(node, AMultOrCartExpression):
        expr1 = eval_int_expression(node.get(0), env)
        expr2 = eval_int_expression(node.get(1), env)
        return expr1 * expr2
    elif isinstance(node, ADivExpression):
        expr1 = eval_int_expression(node.get(0), env)
        expr2 = eval_int_expression(node.get(1), env)
        return expr1 // expr2
    elif isinstance(node, AModuloExpression):
        expr1 = eval_int_expression(node.get(0), env)
        expr2 = eval_int_expression(node.get(1), env)
        assert expr2 > 0
        return expr1 % expr2
    elif isinstance(node, APowerOfExpression):
        basis = eval_int_expression(node.get(0), env)
        exp = eval_int_expression(node.get(1), env)
        # not RPython: result = basis ** exp
        assert exp >=0
        result = 1
        for i in range(exp):
            result *= basis
        return result
        """
    elif isinstance(node, AGeneralSumExpression):
        sum_ = 0
        # new scope
        varList = node.children[:-2]
        env.push_new_frame(varList)
        pred = node.children[-2]
        expr = node.children[-1]
        domain_generator = calc_possible_solutions(pred, env, varList, interpret)
        for entry in domain_generator:
            for name in [x.idName for x in varList]:
                value = entry[name]
                env.set_value(name, value)
            try:
                if interpret(pred, env):  # test          
                    sum_ += eval_int_expression(expr, env)
            except ValueNotInDomainException:
                continue
        env.pop_frame() # exit scope
        return sum_
    elif isinstance(node, AGeneralProductExpression):
        prod_ = 1
        # new scope
        varList = node.children[:-2]
        env.push_new_frame(varList)
        pred = node.children[-2]
        expr = node.children[-1]
        domain_generator = calc_possible_solutions(pred, env, varList, interpret)
        for entry in domain_generator:
            for name in [x.idName for x in varList]:
                value = entry[name]
                env.set_value(name, value)
            try:
                if interpret(pred, env):  # test           
                    prod_ *= eval_int_expression(expr, env)
            except ValueNotInDomainException:
                continue
        env.pop_frame() # exit scope
        return prod_
    elif isinstance(node,AUnaryExpression):
        result = eval_int_expression(node.children[0], env)
        return result.__neg__()
    elif isinstance(node, AMinIntExpression):
        return env._min_int
    elif isinstance(node, AMaxIntExpression):
        return env._max_int
    elif isinstance(node, ACardExpression):
        aSet = interpret(node.children[0], env)
        return len(aSet)
    elif isinstance(node, ASizeExpression):
        sequence = interpret(node.children[0], env)
        return len(sequence)
    elif isinstance(node, AFunctionExpression):
        #print "interpret AFunctionExpression: ", pretty_print(node)
        if isinstance(node.children[0], APredecessorExpression):
            value = interpret(node.children[1], env)
            return value-1
        if isinstance(node.children[0], ASuccessorExpression):
            value = interpret(node.children[1], env)
            return value+1
        function = interpret(node.children[0], env)
        #print "FunctionName:", node.children[0].idName
        args = None
        i = 0 
        for child in node.children[1:]:
            arg = interpret(child, env)
            if i==0:
                args = arg
            else:
                args = tuple([args, arg])
            i = i+1
        if isinstance(function, SymbolicSet):
            return function[args]
        return get_image(function, args)
    elif isinstance(node, AIdentifierExpression):
        #print node.idName
        return env.get_value(node.idName)
        """
    else:
        raise Exception("\nError: Unknown/unimplemented node inside interpreter: %s",node)
        return -1 # RPython: Avoid return of python None

# That the result of node evaluation is an boolean,  must be ensured BY THE CALLER!
def eval_bool_expression(node, env):
    if isinstance(node, AConjunctPredicate):
        bexpr1 = eval_bool_expression(node.get(0), env)
        bexpr2 = eval_bool_expression(node.get(1), env)
        return bexpr1 and bexpr2
    elif isinstance(node, ADisjunctPredicate):
        bexpr1 = eval_bool_expression(node.get(0), env)
        bexpr2 = eval_bool_expression(node.get(1), env)
        return bexpr1 or bexpr2
    elif isinstance(node, AImplicationPredicate):
        bexpr1 = eval_bool_expression(node.get(0), env)
        bexpr2 = eval_bool_expression(node.get(1), env)
        if bexpr1 and not bexpr2:
            return False # True=>False is False
        else:
            return True
    elif isinstance(node, AEquivalencePredicate):
        bexpr1 = eval_bool_expression(node.get(0), env)
        bexpr2 = eval_bool_expression(node.get(1), env)
        assert isinstance(bexpr1, bool) and isinstance(bexpr2, bool)
        return bexpr1 == bexpr2 
    elif isinstance(node, ANegationPredicate):
        bexpr = eval_bool_expression(node.get(0), env)
        return not bexpr
        """
    elif isinstance(node, AUniversalQuantificationPredicate):
        # notice: the all and any keywords are not used, because they need the generation of the whole set
        # new scope
        varList = node.children[:-1]
        env.push_new_frame(varList)
        pred = node.children[-1]
        domain_generator = calc_possible_solutions(pred.children[0], env, varList, interpret) # use left side of implication
        for entry in domain_generator:
            for name in [x.idName for x in varList]:
                value = entry[name]
                env.set_value(name, value)
            try:
                if interpret(pred.children[0], env) and not interpret(pred.children[1], env):  # test
                    env.pop_frame()           
                    return False
            except ValueNotInDomainException:
                continue
        env.pop_frame() # leave scope
        return True        
    elif isinstance(node, AExistentialQuantificationPredicate):
        # new scope
        varList = node.children[:-1]
        env.push_new_frame(varList)
        pred = node.children[-1]
        domain_generator = calc_possible_solutions(pred, env, varList, interpret)
        for entry in domain_generator:
            for name in [x.idName for x in varList]:
                value = entry[name]
                env.set_value(name, value)
            try:
                if interpret(pred, env):  # test
                    env.pop_frame()           
                    return True
            except ValueNotInDomainException:
                continue
        env.pop_frame() # leave scope
        return False        
    elif isinstance(node, AEqualPredicate):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        if isinstance(expr2, SymbolicSet) and isinstance(expr1, frozenset):
            expr2 = expr2.enumerate_all()
            return expr1 == expr2
        else:
            # else normal check, also symbolic (implemented by symbol classes)
            return expr1 == expr2
    elif isinstance(node, AUnequalPredicate):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        # TODO: handle symbolic sets
        return expr1 != expr2
    elif isinstance(node, ABelongPredicate):
        #print pretty_print(node)
        if contains_infinit_enum(node, env):
            result = infinity_belong_check(node, env)
            #print result
            return result
        if all_ids_known(node, env): #TODO: check over-approximation. All ids need to be bound?
            elm = interpret(node.children[0], env)
            result = quick_member_eval(node.children[1], env, elm)
            #print elm, result, node.children[1]
            return result
        elm = interpret(node.children[0], env)
        aSet = interpret(node.children[1], env)
        return elm in aSet
    elif isinstance(node, ANotBelongPredicate):
        if all_ids_known(node, env): #TODO: check over-approximation. All ids need to be bound?
            elm = interpret(node.children[0], env)
            return not quick_member_eval(node.children[1], env, elm)
        elm = interpret(node.children[0], env)
        aSet = interpret(node.children[1], env)
        return not elm in aSet
    elif isinstance(node, AIncludePredicate):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
        if isinstance(aSet2, SymbolicSet):
            return aSet2.issuperset(aSet1)
        return aSet1.issubset(aSet2)
    elif isinstance(node, ANotIncludePredicate):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
        return not aSet1.issubset(aSet2)
    elif isinstance(node, AIncludeStrictlyPredicate):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
        return aSet1.issubset(aSet2) and aSet1 != aSet2
    elif isinstance(node, ANotIncludeStrictlyPredicate):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
        return not (aSet1.issubset(aSet2) and aSet1 != aSet2)
        """
    elif isinstance(node, AGreaterPredicate):
        expr1 = eval_int_expression(node.get(0), env)
        expr2 = eval_int_expression(node.get(1), env)
        return expr1 > expr2
    elif isinstance(node, ALessPredicate):
        expr1 = eval_int_expression(node.get(0), env)
        expr2 = eval_int_expression(node.get(1), env)
        return expr1 < expr2
    elif isinstance(node, AGreaterEqualPredicate):
        expr1 = eval_int_expression(node.get(0), env)
        expr2 = eval_int_expression(node.get(1), env)
        return expr1 >= expr2
    elif isinstance(node, ALessEqualPredicate):
        expr1 = eval_int_expression(node.get(0), env)
        expr2 = eval_int_expression(node.get(1), env)
        return expr1 <= expr2
    else:
        raise Exception("\nError: Unknown/unimplemented node inside interpreter: %s",node)
        return False # RPython: Avoid return of python None
        
        
def interpret(node, env):
    if isinstance(node, APredicateParseUnit): #TODO: move print to animation_clui
        #type_check_predicate(node, env)
        #idNodes = find_var_nodes(node) 
        #idNames = [n.idName for n in idNodes]
        #if idNames ==[]: # variable free predicate
        result = eval_bool_expression(node.children[0], env)
        return result
        """   
        else:            # there are variables 
            env.add_ids_to_frame(idNames)
            learnd_vars = learn_assigned_values(node, env)
            if learnd_vars and VERBOSE:
                print "learnd(no enumeration): ", learnd_vars
            not_set = []
            for n in idNodes:
                if env.get_value(n.idName)==None:
                    not_set.append(n)
            # enumerate only unknown vars
            # Dont enums quantified vars like !x.(P=>Q). This is done later
            if not_set:
                if VERBOSE:
                    print "enum. vars:", [n.idName for n in not_set]
                gen = try_all_values(node.children[0], env, not_set)
                if gen.next():
                    for i in idNames:
                        if VERBOSE:
                            print i,"=", print_values_b_style(env.get_value(i))
                else:
                    print "No Solution found! MIN_INT=%s MAX_INT=%s (see config.py)" % (env._min_int, env._max_int)
                    return False
            else:
                for i in idNames:
                    print i,"=", print_values_b_style(env.get_value(i))
                result = interpret(node.children[0], env)
                return result
        return True
        """
    else:
        raise Exception("\nError: Unknown/unimplemented node inside interpreter: %s",node)
        return False # RPython: Avoid return of python None
     
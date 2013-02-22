# -*- coding: utf-8 -*-
from config import *
from ast_nodes import *
from typing import typeit, IntegerType, PowerSetType, SetType, BType, CartType, BoolType, Substitution, Predicate, type_check_bmch, type_check_predicate, type_check_expression
from helpers import find_var_nodes, find_var_names, flatten, is_flat, double_element_check, find_assignd_vars, print_ast
from bmachine import BMachine
from environment import Environment
from enumeration import *
from quick_eval import quick_member_eval
from constrainsolver import calc_possible_solutions
from pretty_printer import pretty_print
from animation_clui import print_values_b_style

# used in tests and child mchs(included, seen...)
# The data from the solution-files has already been read at the mch creation time
# If a solution file has been given to pyB , this method 'should' never been called 
def _init_machine(root, env, mch):
	mch.init_include_mchs()
	mch.init_seen_mchs()
	mch.init_used_mchs()
	mch.init_extended_mchs()
	init_mch_param(root, env, mch)
	set_up_sets(root, env, mch)
	set_up_constants(root, env, mch)
	check_properties(root, env, mch)
	mch.eval_Variables(env)
	mch.eval_Assertions(env)
	mch.eval_Init(env)


# FIXME: dummy-init of mch-parameters
def init_mch_param(root, env, mch):
    env.add_ids_to_frame([n.idName for n in mch.scalar_params + mch.set_params])
    # TODO: retry if no animation possible
    for n in mch.set_params:
        atype = env.get_type_by_node(n)
        assert isinstance(atype, PowerSetType)
        assert isinstance(atype.data, SetType)
        name = n.idName 
        env.set_value(name, frozenset(["0_"+name,"1_"+name,"2_"+name]))
    for n in mch.scalar_params:
        # page 126
        atype = env.get_type_by_node(n)
        assert isinstance(atype, IntegerType) or isinstance(atype, BoolType)
    if not mch.scalar_params==[]:
        assert not mch.aConstraintsMachineClause==None
        pred = mch.aConstraintsMachineClause
        gen = try_all_values(pred, env, mch.scalar_params)
        assert gen.next()

def set_up_sets(node, env, mch):
    if mch.aSetsMachineClause: # St
        interpret(mch.aSetsMachineClause, env)  

# TODO: enable possibilities for animation and user choice 
def set_up_constants(node, env, mch):
	if mch.aConstantsMachineClause: # k
		interpret(mch.aConstantsMachineClause, env)

def check_properties(node, env, mch):
	if mch.aPropertiesMachineClause: # B
		# set up constants
		# Some Constants/Sets are set via Prop. Preds
		# TODO: give Blacklist of Variable Names
		# find all constants like x=42 oder y={1,2,3}
		learnd_vars = learn_assigned_values(mch.aPropertiesMachineClause, env)
		if learnd_vars:
			print "leard constants (no enumeration): ", learnd_vars
		# if there are constants
		#TODO: Sets
		if mch.aConstantsMachineClause:
			const_nodes = []
			# find all constants/sets which are still not set
			for idNode in mch.aConstantsMachineClause.children:
				assert isinstance(idNode, AIdentifierExpression)
				name = idNode.idName
				if env.get_value(name)==None:
				    try:
				        value = env.solutions[name]
				        env.set_value(name, value)
				    except KeyError:
					    const_nodes.append(idNode)
			if const_nodes==[]:
				prop_result = interpret(mch.aPropertiesMachineClause, env)
			else:
				# if there are unset constants/sets enumerate them
				print "enum. constants:", [n.idName for n in const_nodes]
				gen = try_all_values(mch.aPropertiesMachineClause, env, const_nodes)
				prop_result = gen.next()
			if not prop_result:
				print "Properties FALSE!"
				print_predicate_fail(env, mch.aPropertiesMachineClause.children[0])
			assert prop_result


def print_predicate_fail(env, node):
    pred_lst = []
    while isinstance(node, AConjunctPredicate):
        pred_lst.append(node.children[1])
        node = node.children[0]
    for p in pred_lst:
        result = interpret(p, env)
        if not result:
            print "FALSE="+pretty_print(p)
            #print p.children[0].idName, env.get_value(p.children[0].idName)    


# assumes that every Variable/Constant/Set appears once 
# TODO: Add typeinfo too
def write_solutions_to_env(root, env):
    for node in root.children:
        if isinstance(node, AConjunctPredicate):
            write_solutions_to_env(node, env)
        elif isinstance(node, AEqualPredicate):
            try:
                #TODO: utlb_srv_mrtk__var_e32 --> utlb_srv_mrtk.var_e32 (underscore bug)
                if isinstance(node.children[0], AIdentifierExpression):
                    if isinstance(node.children[1], AIdentifierExpression):
                        # This is a special case, generate by ProB at this time
                        # it will be removed when defferd sets and enumerated sets 
                        # are part of a solution file.
                        # a reference to a enumerated set item can not be reolved at
                        # this time. Solution files are read ahead of time before any mch startup.
                        # TODO: remove when sets are part of the solution
                        env.solutions[node.children[0].idName] = node.children[1].idName
                    else:
                        expr = interpret(node.children[1], env)
                        env.solutions[node.children[0].idName] = expr
                    continue
                elif isinstance(node.children[1], AIdentifierExpression):
                    if isinstance(node.children[0], AIdentifierExpression):
                        env.solutions[node.children[1].idName] = node.children[0].idName
                    else:
                        expr = interpret(node.children[0], env)
                        env.solutions[node.children[1].idName] = expr
                    continue
                else:
                    continue
            except Exception:
                continue 
           

def learn_assigned_values(root, env):
    lst = []
    _learn_assigned_values(root, env, lst)
    return lst
    

# node is an "side-effect-free" AST (no assignments := )
def _learn_assigned_values(root, env, lst):
    for node in root.children:
        if isinstance(node, AEqualPredicate):
            # special case: learn values if None (optimization)
            if isinstance(node.children[0], AIdentifierExpression) and env.get_value(node.children[0].idName)==None:
                if isinstance(node.children[1], AIntegerExpression) or isinstance(node.children[1], ASetExtensionExpression) or isinstance(node.children[1], ABoolSetExpression) or isinstance(node.children[1], ATrueExpression) or isinstance(node.children[1], AFalseExpression):
                    try:
                        expr = interpret(node.children[1], env)
                        env.set_value(node.children[0].idName, expr)
                        lst.append(node.children[0].idName)
                        continue
                    except Exception:
                        continue 
            elif isinstance(node.children[1], AIdentifierExpression) and env.get_value(node.children[1].idName)==None:
                if isinstance(node.children[0], AIntegerExpression) or isinstance(node.children[0], ASetExtensionExpression) or isinstance(node.children[0], ABoolSetExpression) or isinstance(node.children[0], ATrueExpression) or isinstance(node.children[0], AFalseExpression):
                    try:
                        expr = interpret(node.children[0], env)
                        env.set_value(node.children[1].idName, expr)
                        lst.append(node.children[1].idName)
                        continue
                    except Exception:
                        continue 
            else:
                continue
        elif isinstance(node, AConjunctPredicate):
            _learn_assigned_values(node, env, lst)


# sideeffect:
# evals pred and sets var to values
# main interpreter-switch (sorted/grouped like b-toolkit list)
def interpret(node, env):

# ******************************
#
#        0. Interpretation-mode
#
# ******************************
    #print node
    if isinstance(node,APredicateParseUnit): #TODO: move print to animation_clui
        idNodes = find_var_nodes(node.children[0]) 
        idNames = [n.idName for n in idNodes]
        type_check_predicate(node, env, idNames)
        if idNames ==[]: # variable free predicate
            result = interpret(node.children[0], env)
            print result
            return
        else:            # there are variables 
            env.add_ids_to_frame(idNames)
            learnd_vars = learn_assigned_values(node, env)
            if learnd_vars:
                print "learnd(no enumeration): ", learnd_vars
            not_set = []
            for n in idNodes:
                if env.get_value(n.idName)==None:
                    not_set.append(n)
            # enumerate only unknown vars
            # Dont enums quantified vars like !x.(P=>Q)
            if not_set:
                print "enum. vars:", [n.idName for n in not_set]
                gen = try_all_values(node.children[0], env, not_set)
                if gen.next():
                    for i in idNames:
                        print i,"=", env.get_value(i)
                else:
                    print "No Solution found! MIN_INT=%s MAX_INT=%s (see config.py)" % (env._min_int, env._max_int)
                    print False
                    return
            else:
                for i in idNames:
                    print i,"=", print_values_b_style(env.get_value(i))
                result = interpret(node.children[0], env)
                print result
                return
        print True
        return None
    elif isinstance(node, AExpressionParseUnit): #TODO more
        #TODO: move print to animation_clui
        idNodes = find_var_nodes(node.children[0]) 
        idNames = [n.idName for n in idNodes]
        type_check_expression(node, env, idNames)
        if idNames ==[]: # variable free expression
            result = interpret(node.children[0], env)
            print print_values_b_style(result)
        else:
            print "Warning: Expressions with variables are not implemented now"
        return
    elif isinstance(node, AAbstractMachineParseUnit):
        # TODO: remove when prob solution eval for child mch is done
        mch = env.current_mch
    	_init_machine(node, env, mch)
    	return mch
    elif isinstance(node, AConstantsMachineClause):
        const_names = []
        for idNode in node.children:
            assert isinstance(idNode, AIdentifierExpression)
            const_names.append(idNode.idName)
            #atype = env.get_type_by_node(idNode)
        env.add_ids_to_frame(const_names)
    elif isinstance(node, AVariablesMachineClause):
        var_names = []
        for idNode in node.children:
            assert isinstance(idNode, AIdentifierExpression)
            var_names.append(idNode.idName)
            #atype = env.get_type_by_node(idNode)
        env.add_ids_to_frame(var_names)
    elif isinstance(node, ASetsMachineClause):
        for child in node.children:
            if isinstance(child, AEnumeratedSet):
                elm_lst = []
                for elm in child.children:
                    assert isinstance(elm, AIdentifierExpression)
                    elm_lst.append(elm.idName)
                    env.add_ids_to_frame([elm.idName])
                    # The values of elements of enumerated sets are their names
                    env.set_value(elm.idName, elm.idName)
                env.add_ids_to_frame([child.idName])
                env.set_value(child.idName, frozenset(elm_lst))
            else:
                init_deffered_set(child, env)
    elif isinstance(node, AConstraintsMachineClause):
        for child in node.children:
            if not interpret(child, env):
                return False
        return True
    elif isinstance(node, APropertiesMachineClause):
        assert len(node.children)==1
        return interpret(node.children[0], env)
    elif isinstance(node, AInitialisationMachineClause):
        for child in node.children:
            interpret(child, env)
    elif isinstance(node, AInvariantMachineClause):
        result = interpret(node.children[0], env)
        if not result:
            print_predicate_fail(env, node)
        return result
    elif isinstance(node, AAssertionsMachineClause):
        if ENABLE_ASSERTIONS:
            print "checking assertions"
            for child in node.children:
                print "\t", interpret(child, env)
            print "checking done."


# *********************
#
#        1. Predicates
#
# *********************
    elif isinstance(node, AConjunctPredicate):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        return expr1 and expr2
    elif isinstance(node, ADisjunctPredicate):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        return expr1 or expr2
    elif isinstance(node, AImplicationPredicate):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        if expr1 and not expr2:
            return False # True=>False is False
        else:
            return True
    elif isinstance(node, AEquivalencePredicate):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        return expr1 == expr2 # FIXME: maybe this is wrong...
    elif isinstance(node, ANegationPredicate):
        expr = interpret(node.children[0], env)
        return not expr
    elif isinstance(node, AUniversalQuantificationPredicate):
        # new scope
        varList = node.children[:-1]
        env.push_new_frame(varList)
        pred = node.children[-1]
        domain_generator = calc_possible_solutions(env, varList, pred.children[0])
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
        env.pop_frame()
        return True        
    elif isinstance(node, AExistentialQuantificationPredicate):
        # new scope
        varList = node.children[:-1]
        env.push_new_frame(varList)
        pred = node.children[-1]
        domain_generator = calc_possible_solutions(env, varList, pred.children[0])
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
        env.pop_frame()
        return False        
    elif isinstance(node, AEqualPredicate):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        # special case: learn values if None (optimization)
        if isinstance(node.children[0], AIdentifierExpression) and env.get_value(node.children[0].idName)==None:
            env.set_value(node.children[0].idName, expr2)
            return True
        elif isinstance(node.children[1], AIdentifierExpression) and env.get_value(node.children[1].idName)==None:
            env.set_value(node.children[1].idName, expr1)
            return True
        else:
            # else normal check
            return expr1 == expr2
    elif isinstance(node, AUnequalPredicate):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        return expr1 != expr2


# **************
#
#       2. Sets
#
# **************
    elif isinstance(node, ASetExtensionExpression):
        lst = []
        for child in node.children:
            elm = interpret(child, env)
            lst.append(elm)
        return frozenset(lst)
    elif isinstance(node, AEmptySetExpression):
        return frozenset()
    elif isinstance(node, AComprehensionSetExpression):
        result = []
        # new scope
        varList = node.children[:-1]
        env.push_new_frame(varList)
        pred = node.children[-1]
        domain_generator = calc_possible_solutions(env, varList, pred)
        for entry in domain_generator:
            for name in [x.idName for x in varList]:
                value = entry[name]
                env.set_value(name, value)
            try:
                if interpret(pred, env):  # test
                    i = 0
                    for name in [x.idName for x in varList]:
                        value = env.get_value(name)
                        i = i + 1
                        if i==1:
                            tup = value
                        else:
                            tup = tuple([tup,value])
                    result.append(tup)  
            except ValueNotInDomainException:
                continue
        env.pop_frame()
        return frozenset(result)       
    elif isinstance(node, AUnionExpression):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
        return aSet1.union(aSet2)
    elif isinstance(node, AIntersectionExpression):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
        return aSet1.intersection(aSet2)
    elif isinstance(node, ACoupleExpression):
        result = None
        i = 0
        for child in node.children:
            elm = interpret(child, env)
            if i==0:
                result = elm
            else:
                result = tuple([result, elm]) 
            i = i + 1
        return result
    elif isinstance(node, APowSubsetExpression):
        aSet = interpret(node.children[0], env)
        res = powerset(aSet)
        powerlist = list(res)
        lst = [frozenset(e) for e in powerlist]
        return frozenset(lst)
    elif isinstance(node, APow1SubsetExpression):
        aSet = interpret(node.children[0], env)
        res = powerset(aSet)
        powerlist = list(res)
        lst = [frozenset(e) for e in powerlist]
        lst.remove(frozenset([]))
        return frozenset(lst)
    elif isinstance(node, ACardExpression):
        aSet = interpret(node.children[0], env)
        return len(aSet)
    elif isinstance(node, AGeneralUnionExpression):
        set_of_sets = interpret(node.children[0], env)
        elem_lst = list(set_of_sets)
        acc = elem_lst[0]
        for aset in elem_lst[1:]:
            acc = acc.union(aset)
        return acc
    elif isinstance(node, AGeneralIntersectionExpression):
        set_of_sets = interpret(node.children[0], env)
        elem_lst = list(set_of_sets)
        acc = elem_lst[0]
        for aset in elem_lst[1:]:
            acc = acc.intersection(aset)
        return acc
    elif isinstance(node, AQuantifiedUnionExpression):
        result = frozenset([])
        # new scope
        varList = node.children[:-2]
        env.push_new_frame(varList)
        pred = node.children[-2]
        expr = node.children[-1]
        domain_generator = calc_possible_solutions(env, varList, pred)
        for entry in domain_generator:
            for name in [x.idName for x in varList]:
                value = entry[name]
                env.set_value(name, value)
            try:
                if interpret(pred, env):  # test   
                    result |= interpret(expr, env) 
            except ValueNotInDomainException:
                continue
        env.pop_frame()
        return result
    elif isinstance(node, AQuantifiedIntersectionExpression):  
        result = frozenset([])
        # new scope
        varList = node.children[:-2]
        env.push_new_frame(varList)
        pred = node.children[-2]
        expr = node.children[-1]
        domain_generator = calc_possible_solutions(env, varList, pred)
        for entry in domain_generator:
            for name in [x.idName for x in varList]:
                value = entry[name]
                env.set_value(name, value)
            try:
                if interpret(pred, env):  # test
                    if result==frozenset([]):
                         result = interpret(expr, env)  
                    else:      
                         result &= interpret(expr, env) 
            except ValueNotInDomainException:
                continue
        env.pop_frame()
        return result


# *************************
#
#       2.1 Set predicates
#
# *************************
    elif isinstance(node, ABelongPredicate):
        if quick_enum_possible(node, env):
            elm = interpret(node.children[0], env)
            result = quick_member_eval(node.children[1], env, elm)
            return result
        elm = interpret(node.children[0], env)
        aSet = interpret(node.children[1], env)
        #print elm, aSet, node.children[0], node.children[1]
        if isinstance(elm,str) and aSet=="":
            return True # FIXME: hack
        return elm in aSet
    elif isinstance(node, ANotBelongPredicate):
        if quick_enum_possible(node, env):
            elm = interpret(node.children[0], env)
            return not quick_member_eval(node.children[1], env, elm)
        elm = interpret(node.children[0], env)
        aSet = interpret(node.children[1], env)
        return not elm in aSet
    elif isinstance(node, AIncludePredicate):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
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


# *****************
#
#       3. Numbers
#
# *****************
    elif isinstance(node, ANaturalSetExpression):
        print "WARNING: NATURAL = 0.."+str(env._max_int)
        return frozenset(range(0,env._max_int+1)) #XXX
    elif isinstance(node, ANatural1SetExpression):
        print "WARNING: NATURAL1 = 1.."+str(env._max_int)
        return frozenset(range(1,env._max_int+1)) #XXX
    elif isinstance(node, ANatSetExpression):
        return frozenset(range(0,env._max_int+1))
    elif isinstance(node, ANat1SetExpression):
        return frozenset(range(1,env._max_int+1))
    elif isinstance(node, AIntSetExpression):
        return frozenset(range(env._min_int, env._max_int+1)) 
    elif isinstance(node, AIntegerSetExpression):
        print "WARNING: INTEGER = "+str(env._min_int)+".."+str(env._max_int)
        return frozenset(range(env._min_int,env._max_int+1)) #XXX
    elif isinstance(node, AMinExpression):
        aSet = interpret(node.children[0], env)
        return min(list(aSet))
    elif isinstance(node, AMaxExpression):
        aSet = interpret(node.children[0], env)
        return max(list(aSet))
    elif isinstance(node, AAddExpression):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        return expr1 + expr2
    elif isinstance(node, AMinusOrSetSubtractExpression) or isinstance(node, ASetSubtractionExpression):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        return expr1 - expr2
    elif isinstance(node, AMultOrCartExpression):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        if isinstance(expr1, frozenset) and isinstance(expr2, frozenset):
            return frozenset(((x,y) for x in expr1 for y in expr2))
        else:
            return expr1 * expr2
    elif isinstance(node, ADivExpression):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        return expr1 / expr2
    elif isinstance(node, AModuloExpression):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        assert expr2 > 0
        return expr1 % expr2
    elif isinstance(node, APowerOfExpression):
        basis = interpret(node.children[0], env)
        exp = interpret(node.children[1], env)
        return basis ** exp
    elif isinstance(node, AIntervalExpression):
        left = interpret(node.children[0], env)
        right = interpret(node.children[1], env)
        return frozenset(range(left, right+1))
    elif isinstance(node, AGeneralSumExpression):
        sum_ = 0
        # new scope
        varList = node.children[:-2]
        env.push_new_frame(varList)
        pred = node.children[-2]
        expr = node.children[-1]
        domain_generator = calc_possible_solutions(env, varList, pred)
        for entry in domain_generator:
            for name in [x.idName for x in varList]:
                value = entry[name]
                env.set_value(name, value)
            try:
                if interpret(pred, env):  # test          
                    sum_ += interpret(expr, env)
            except ValueNotInDomainException:
                continue
        env.pop_frame()
        return sum_
    elif isinstance(node, AGeneralProductExpression):
        prod_ = 1
        # new scope
        varList = node.children[:-2]
        env.push_new_frame(varList)
        pred = node.children[-2]
        expr = node.children[-1]
        domain_generator = calc_possible_solutions(env, varList, pred)
        for entry in domain_generator:
            for name in [x.idName for x in varList]:
                value = entry[name]
                env.set_value(name, value)
            try:
                if interpret(pred, env):  # test           
                    prod_ *= interpret(expr, env)
            except ValueNotInDomainException:
                continue
        env.pop_frame()
        return prod_



# ***************************
#
#       3.1 Number predicates
#
# ***************************
    elif isinstance(node, AGreaterPredicate):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        return expr1 > expr2
    elif isinstance(node, ALessPredicate):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        return expr1 < expr2
    elif isinstance(node, AGreaterEqualPredicate):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        return expr1 >= expr2
    elif isinstance(node, ALessEqualPredicate):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        return expr1 <= expr2


# ******************
#
#       4. Relations
#
# ******************
    elif isinstance(node, ARelationsExpression):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
        aSet = make_set_of_realtions(aSet1, aSet2)
        return aSet
    elif isinstance(node, ADomainExpression):
        # FIXME: crashs if this is not a set of 2-tuple
        aSet = interpret(node.children[0], env)
        dom = [e[0] for e in list(aSet)]
        return frozenset(dom)
    elif isinstance(node, ARangeExpression):
        # FIXME: crashs if this is not a set of 2-tuple
        aSet = interpret(node.children[0], env)
        ran = [e[1] for e in list(aSet)]
        return frozenset(ran)
    elif isinstance(node, ACompositionExpression):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
        new_rel = [(p[0],q[1]) for p in aSet1 for q in aSet2 if p[1]==q[0]]
        return frozenset(new_rel)
    elif isinstance(node, AIdentityExpression):
        aSet = interpret(node.children[0], env)
        id_r = [(x,x) for x in aSet]
        return frozenset(id_r)
    elif isinstance(node, ADomainRestrictionExpression):
        aSet = interpret(node.children[0], env)
        rel = interpret(node.children[1], env)
        new_rel = [x for x in rel if x[0] in aSet]
        return frozenset(new_rel)
    elif isinstance(node, ADomainSubtractionExpression):
        aSet = interpret(node.children[0], env)
        rel = interpret(node.children[1], env)
        new_rel = [x for x in rel if not x[0] in aSet]
        return frozenset(new_rel)
    elif isinstance(node, ARangeRestrictionExpression):
        aSet = interpret(node.children[1], env)
        rel = interpret(node.children[0], env)
        new_rel = [x for x in rel if x[1] in aSet]
        return frozenset(new_rel)
    elif isinstance(node, ARangeSubtractionExpression):
        aSet = interpret(node.children[1], env)
        rel = interpret(node.children[0], env)
        new_rel = [x for x in rel if not x[1] in aSet]
        return frozenset(new_rel)
    elif isinstance(node, AReverseExpression):
        rel = interpret(node.children[0], env)
        new_rel = [(x[1],x[0]) for x in rel]
        return frozenset(new_rel)
    elif isinstance(node, AImageExpression):
        rel = interpret(node.children[0], env)
        aSet = interpret(node.children[1], env)
        #if rel==None or aSet==None:
        #    return None
        image = [x[1] for x in rel if x[0] in aSet ]
        return frozenset(image)
    elif isinstance(node, AOverwriteExpression):
        r1 = interpret(node.children[0], env)
        r2 = interpret(node.children[1], env)
        dom_r2 = [x[0] for x in r2]
        new_r  = [x for x in r1 if x[0] not in dom_r2]
        r2_list= [x for x in r2]
        return frozenset(r2_list + new_r)
    elif isinstance(node, ADirectProductExpression):
        p = interpret(node.children[0], env)
        q = interpret(node.children[1], env)
        d_prod = [(x[0],(x[1],y[1])) for x in p for y in q if x[0]==y[0]]
        return frozenset(d_prod)
    elif isinstance(node, AParallelProductExpression):
        p = interpret(node.children[0], env)
        q = interpret(node.children[1], env)
        p_prod = [((x[0],y[0]),(x[1],y[1])) for x in p for y in q]
        return frozenset(p_prod)
    elif isinstance(node, AIterationExpression):
        arel = interpret(node.children[0], env)
        n = interpret(node.children[1], env)
        assert n>=0
        rel = list(arel)
        rel = [(x[0],x[0]) for x in rel]
        for i in range(n):
            rel = [(y[0],x[1]) for y in rel for x in arel if y[1]==x[0]]
        return frozenset(rel)
    elif isinstance(node, AReflexiveClosureExpression):
        arel = interpret(node.children[0], env)
        rel = list(arel)
        temp = [(x[1],x[1]) for x in rel] # also image
        rel = [(x[0],x[0]) for x in rel]
        rel += temp
        rel = list(frozenset(rel)) # throw away doubles
        while True: # fixpoint-search (do-while-loop)
            new_rel = [(y[0],x[1]) for y in rel for x in arel if y[1]==x[0]]
            if frozenset(new_rel).union(frozenset(rel))==frozenset(rel):
                return frozenset(rel)
            rel =list(frozenset(new_rel).union(frozenset(rel)))
    elif isinstance(node, AClosureExpression):
        arel = interpret(node.children[0], env)
        rel = list(arel)
        while True: # fixpoint-search (do-while-loop)
            new_rel = [(y[0],x[1]) for y in rel for x in arel if y[1]==x[0]]
            if frozenset(new_rel).union(frozenset(rel))==frozenset(rel):
                return frozenset(rel)
            rel =list(frozenset(new_rel).union(frozenset(rel)))
    elif isinstance(node, AFirstProjectionExpression):
        S = interpret(node.children[0], env)
        T = interpret(node.children[1], env)
        cart = frozenset(((x,y) for x in S for y in T))
        proj = [(x,x[0]) for x in cart]
        return frozenset(proj)
    elif isinstance(node, ASecondProjectionExpression):
        S = interpret(node.children[0], env)
        T = interpret(node.children[1], env)
        cart = frozenset(((x,y) for x in S for y in T))
        proj = [(x,x[1]) for x in cart]
        return frozenset(proj)



# *******************
#
#       4.1 Functions
#
# *******************
    elif isinstance(node, APartialFunctionExpression):
        S = interpret(node.children[0], env)
        T = interpret(node.children[1], env)
        relation_set = make_set_of_realtions(S,T) # S<-->T
        fun = filter_no_function(relation_set) # S+->T
        return fun
    elif isinstance(node, ATotalFunctionExpression):
        S = interpret(node.children[0], env)
        T = interpret(node.children[1], env)
        relation_set = make_set_of_realtions(S,T) # S<-->T
        fun = filter_no_function(relation_set) # S+->T
        total_fun = filter_not_total(fun, S) # S-->T
        return total_fun
    elif isinstance(node, APartialInjectionExpression):
        S = interpret(node.children[0], env)
        T = interpret(node.children[1], env)
        relation_set = make_set_of_realtions(S,T) # S<-->T
        fun = filter_no_function(relation_set) # S+->T
        inj_fun = filter_not_injective(fun) # S>+>T
        return inj_fun
    elif isinstance(node, ATotalInjectionExpression):
        S = interpret(node.children[0], env)
        T = interpret(node.children[1], env)
        relation_set = make_set_of_realtions(S,T) # S<-->T
        fun = filter_no_function(relation_set) # S+->T
        inj_fun = filter_not_injective(fun) # S>+>T
        total_inj_fun = filter_not_total(inj_fun, S) # S>->T
        return total_inj_fun
    elif isinstance(node, APartialSurjectionExpression):
        S = interpret(node.children[0], env)
        T = interpret(node.children[1], env)
        relation_set = make_set_of_realtions(S,T) # S<-->T
        fun = filter_no_function(relation_set) # S+->T
        surj_fun = filter_not_surjective(fun, T) # S+->>T
        return surj_fun
    elif isinstance(node, ATotalSurjectionExpression):
        S = interpret(node.children[0], env)
        T = interpret(node.children[1], env)
        relation_set = make_set_of_realtions(S,T) # S<-->T
        fun = filter_no_function(relation_set) # S+->T
        surj_fun = filter_not_surjective(fun, T) # S+->>T
        total_surj_fun = filter_not_total(surj_fun, S) # S-->>T
        return total_surj_fun
    elif isinstance(node, ATotalBijectionExpression):
        S = interpret(node.children[0], env)
        T = interpret(node.children[1], env)
        relation_set = make_set_of_realtions(S,T) # S<-->T
        fun = filter_no_function(relation_set) # S+->T
        inj_fun = filter_not_injective(fun) # S>+>T
        total_inj_fun = filter_not_total(inj_fun, S) # S>->T
        bij_fun = filter_not_surjective(total_inj_fun,T) # S>->>T
        return bij_fun
    elif isinstance(node, APartialBijectionExpression):
        S = interpret(node.children[0], env)
        T = interpret(node.children[1], env)
        relation_set = make_set_of_realtions(S,T) # S<-->T
        fun = filter_no_function(relation_set) # S+->T
        inj_fun = filter_not_injective(fun) # S>+>T
        bij_fun = filter_not_surjective(inj_fun,T)
        return bij_fun
    elif isinstance(node, ALambdaExpression):
        func_list = []
        # new scope
        varList = node.children[:-2]
        env.push_new_frame(varList)
        pred = node.children[-2]
        expr = node.children[-1]
        domain_generator = calc_possible_solutions(env, varList, pred)
        for entry in domain_generator:
            i = 0
            for name in [x.idName for x in varList]:
                value = entry[name]
                env.set_value(name, value)
                i = i + 1
                if i==1:
                    arg = value
                else:
                    arg = tuple([arg, value])
            try:
                if interpret(pred, env):  # test       
                    image = interpret(expr, env)
                    tup = tuple([arg, image])
                    func_list.append(tup) 
            except ValueNotInDomainException:
                continue
        env.pop_frame()
        return frozenset(func_list)
    elif isinstance(node, AFunctionExpression):
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
        return get_image(function, args)



# ********************
#
#       4.2 Sequences
#
# ********************
    elif isinstance(node,AEmptySequenceExpression):
        return frozenset([])
    elif isinstance(node,ASeqExpression):
        S = interpret(node.children[0], env)
        sequence_list = [frozenset([])]
        max_len = 1
        # find all seq. from 1..max_int
        for i in range(1, env._max_int+1):
            sequence_list += create_all_seq_w_fixlen(list(S),i)
        return frozenset(sequence_list)
    elif isinstance(node,ASeq1Expression):
        S = interpret(node.children[0], env)
        sequence_list = []
        max_len = 1
        # find all seq. from 1..max_int
        for i in range(1, env._max_int+1):
            sequence_list += create_all_seq_w_fixlen(list(S),i)
        return frozenset(sequence_list)
    elif isinstance(node,AIseqExpression):
        # TODO: this can be impl. much better
        S = interpret(node.children[0], env)
        sequence_list = [frozenset([])]
        max_len = 1
        # find all seq from 1..max_int
        for i in range(1, env._max_int+1):
            sequence_list += create_all_seq_w_fixlen(list(S),i)
        inj_sequence_list = filter_not_injective(sequence_list)
        return frozenset(inj_sequence_list)
    elif isinstance(node, AIseq1Expression):
        # TODO: this can be impl. much better
        S = interpret(node.children[0], env)
        sequence_list = [frozenset([])]
        max_len = 1
        # find all seq from 1..max_int
        for i in range(1, env._max_int+1):
            sequence_list += create_all_seq_w_fixlen(list(S),i)
        inj_sequence_list = filter_not_injective(sequence_list)
        return frozenset(inj_sequence_list)
    elif isinstance(node,APermExpression): 
        # TODO: this can be impl. much better
        S = interpret(node.children[0], env)
        sequence_list = [frozenset([])]
        max_len = 1
        # TODO: maybe call all_values() here...
        # find all seq from 1..max_int
        for i in range(1, env._max_int+1):
            sequence_list += create_all_seq_w_fixlen(list(S),i)
        inj_sequence_list = filter_not_injective(sequence_list)
        perm_sequence_list = filter_not_surjective(inj_sequence_list, S)
        return frozenset(perm_sequence_list)
    elif isinstance(node, AConcatExpression):
        s = interpret(node.children[0], env)
        t = interpret(node.children[1], env)
        new_t = []
        for tup in t: # FIXME: maybe wrong order
            new_t.append(tuple([tup[0]+len(s),tup[1]]))
        return frozenset(list(s)+new_t)
    elif isinstance(node, AInsertFrontExpression):
        E = interpret(node.children[0], env)
        s = interpret(node.children[1], env)
        new_s = [(1,E)]
        for tup in s:
            new_s.append(tuple([tup[0]+1,tup[1]]))
        return frozenset(new_s)
    elif isinstance(node, AInsertTailExpression):
        s = interpret(node.children[0], env)
        E = interpret(node.children[1], env)
        return frozenset(list(s)+[tuple([len(s)+1,E])])
    elif isinstance(node, ASequenceExtensionExpression):
        sequence = []
        i = 0
        for child in node.children:
            i = i+1
            e = interpret(child, env)
            sequence.append(tuple([i,e]))
        return frozenset(sequence)
    elif isinstance(node, ASizeExpression):
        sequence = interpret(node.children[0], env)
        return len(sequence)
    elif isinstance(node, ARevExpression):
        sequence = interpret(node.children[0], env)
        new_sequence = []
        i = len(sequence)
        for tup in sequence:
            new_sequence.append(tuple([i,tup[1]]))
            i = i-1
        return frozenset(new_sequence)
    elif isinstance(node, ARestrictFrontExpression):
        sequence = interpret(node.children[0], env)
        take = interpret(node.children[1], env)
        assert take>0
        lst = list(sequence)
        lst.sort()
        return frozenset(lst[:-take])
    elif isinstance(node, ARestrictTailExpression):
        sequence = interpret(node.children[0], env)
        drop = interpret(node.children[1], env)
        assert drop>0
        lst = list(sequence)
        lst.sort()
        new_list = []
        i = 0
        for tup in lst[drop:]:
            i = i+1
            new_list.append(tuple([i,tup[1]]))
        return frozenset(new_list)
    elif isinstance(node, AFirstExpression):
        sequence = interpret(node.children[0], env)
        lst = list(sequence)
        lst.sort()
        assert lst[0][0]==1
        return lst[0][1]
    elif isinstance(node, ALastExpression):
        sequence = interpret(node.children[0], env)
        lst = list(sequence)
        lst.sort()
        assert lst[len(sequence)-1][0]==len(sequence)
        return lst[len(sequence)-1][1]
    elif isinstance(node, ATailExpression):
        sequence = interpret(node.children[0], env)
        lst = list(sequence)
        lst.sort()
        assert lst[0][0]==1
        return frozenset(lst[1:])
    elif isinstance(node, AFrontExpression):
        sequence = interpret(node.children[0], env)
        lst = list(sequence)
        lst.sort()
        lst.pop()
        return frozenset(lst)
    elif isinstance(node, AGeneralConcatExpression):
        s = interpret(node.children[0], env)
        t = []
        index = 0
        for squ in dict(s).values():
            for val in dict(squ).values():
                index = index +1
                t.append(tuple([index, val]))
        return frozenset(t)
    elif isinstance(node, AStringExpression):
        return node.string


# ****************
#
# 5. Substitutions
#
# ****************
    elif isinstance(node, ASkipSubstitution):
        pass
    elif isinstance(node, AAssignSubstitution):
        assert int(node.lhs_size) == int(node.rhs_size)     
        used_ids = []
        values = []
        for i in range(int(node.rhs_size)):
            rhs = node.children[i+int(node.rhs_size)]
            value = interpret(rhs, env)
            values.append(value)
        for i in range(int(node.lhs_size)):
            lhs_node = node.children[i]            
            # BUG if the expression on the rhs has a sideeffect
            value = values[i]
            if isinstance(lhs_node, AIdentifierExpression):
                used_ids.append(lhs_node.idName)
                env.set_value(lhs_node.idName, value)
            else:
                assert isinstance(lhs_node, AFunctionExpression)
                assert isinstance(lhs_node.children[0], AIdentifierExpression)
                func_name = lhs_node.children[0].idName
                # get args
                args = []
                for child in lhs_node.children[1:]:
                    arg = interpret(child, env)
                    args.append(arg)
                func = dict(env.get_value(func_name))
                used_ids.append(func_name)
                # change
                if len(args)==1:
                    func[args[0]] = value
                else:
                    func[tuple(args)] = value
                # convert back
                lst = []
                for key in func:
                    lst.append(tuple([key,func[key]]))
                new_func = frozenset(lst)
                # write to env
                env.set_value(func_name, new_func)
        while not used_ids==[]:
            name = used_ids.pop()
            if name in used_ids:
                string = name + " modified twice in multiple assign-substitution!"
                raise Exception(string)
    elif isinstance(node, AConvertBoolExpression):
        return interpret(node.children[0], env)
    elif isinstance(node, ABecomesElementOfSubstitution):
        values = interpret(node.children[-1], env)
        value = list(values)[0] # XXX
        for child in node.children[:-1]:
            assert isinstance(child, AIdentifierExpression)
            env.set_value(child.idName, value)
    elif isinstance(node, ABecomesSuchSubstitution):
        # TODO: more than on ID
        nodes = []
        for child in node.children[:-1]:
            assert isinstance(child, AIdentifierExpression)
            nodes.append(child)
        # new frame to enable primed-ids
        env.push_new_frame(nodes)
        gen = try_all_values(node.children[-1], env, nodes) 
        gen.next() # sideeffect: set values
        results = []
        for n in nodes:
            i = n.idName
            results.append(env.get_value(i))
        env.pop_frame()
        # write back
        for i in range(len(nodes)):
            env.set_value(nodes[i].idName, results[i])
    elif isinstance(node, AParallelSubstitution):
        new_values = [] # values changed by this path
        # 1. exec. every parallel path and remember changed values for late lookup
        for child in node.children:
            assignd_ids = find_assignd_vars(child)
            assignd_ids = list(set(assignd_ids)) # remove double entrys
            bstate = env.get_state().clone()
            env.state_space.add_state(bstate) # TODO: write clean interface 
            # 1.1 calc path    
            interpret(child, env)
            # 1.2. remember (possible) changes
            possible_new_values = {}
            for name in assignd_ids:
                val = env.get_value(name)
                possible_new_values[name] = val
            env.state_space.undo() #set to old state and drop other state
            # 1.3 test for changes
            for name in assignd_ids:
                new = possible_new_values[name]
                old = env.get_value(name)
                if not new==old: # change! - remember it
                    new_values.append(tuple([name, new]))
        # 2. test: no variable can be modified twice (see page 108)
        # check for double entrys -> Error
        id_names = [x[0] for x in new_values]
        while not id_names==[]:
            name = id_names.pop()
            if name in id_names:
                string = name + " modified twice in parallel substitution!"
                raise Exception(string)
        # 3. write changes to state
        for pair in new_values:
            name = pair[0]
            value = pair[1]
            env.set_value(name, value)
    elif isinstance(node, ASequenceSubstitution):
        for child in node.children:
            interpret(child, env)
    elif isinstance(node, AWhileSubstitution):
    	print "WARNING: WHILE inside abstract MACHINE!!" # TODO: replace warning
    	condition = node.children[0]
        doSubst   = node.children[1]
        invariant = node.children[2]
        variant   = node.children[3]
        v_value = interpret(variant, env)
        while interpret(condition, env):
        	assert interpret(invariant, env)
        	interpret(doSubst, env)
        	temp = interpret(variant, env)
        	assert temp < v_value
        	v_value = temp
        return


# **********************
#
# 5.1. Alternative Syntax
#
# ***********************
    elif isinstance(node, ABlockSubstitution):
        for child in node.children:
            interpret(child, env)
    elif isinstance(node, APreconditionSubstitution):
        assert isinstance(node.children[0], Predicate)
        assert isinstance(node.children[1], Substitution)
        condition = interpret(node.children[0], env)
        #print condition, node.children[0]
        if condition:
            interpret(node.children[1], env)
            return
    elif isinstance(node, AAssertionSubstitution):
        assert isinstance(node.children[0], Predicate)
        assert isinstance(node.children[1], Substitution)
        assert interpret(node.children[0], env)
        interpret(node.children[1], env)
    elif isinstance(node, AIfSubstitution):
        assert isinstance(node.children[0], Predicate)
        assert isinstance(node.children[1], Substitution)
        condition = interpret(node.children[0], env)
        if condition:
            interpret(node.children[1], env)
            return
        for child in node.children[2:]:
            if isinstance(child, AIfElsifSubstitution):
                assert isinstance(child.children[0], Predicate)
                assert isinstance(child.children[1], Substitution)
                condition = interpret(child.children[0], env)
                if condition:
                    interpret(child.children[1], env)
                    return
            else:
                # ELSE (B Level)
                assert isinstance(child, Substitution)
                assert child==node.children[-1] # last child
                interpret(child, env)
                return
    elif isinstance(node, AChoiceSubstitution):
        assert isinstance(node.children[0], Substitution)
        for child in node.children[1:]:
            assert isinstance(child, AChoiceOrSubstitution)
        # TODO: random choice
        return interpret(node.children[0], env)
    elif isinstance(node, ASelectSubstitution):
        nodes = []
        assert isinstance(node.children[0], Predicate)
        assert isinstance(node.children[1], Substitution)
        if interpret(node.children[0], env):
            nodes.append(node.children[1])
        for child in node.children[2:]:
            if isinstance(child, ASelectWhenSubstitution):
                assert isinstance(child.children[0], Predicate)
                assert isinstance(child.children[1], Substitution)
                if interpret(child.children[0], env):
                    nodes.append(child.children[1])
            else:
                assert isinstance(child, Substitution)
                assert child==node.children[-1]
        if not nodes == []:
            # TODO: random choice
            interpret(nodes[0], env)
        elif node.hasElse: 
            interpret(node.children[-1], env)
    elif isinstance(node, ACaseSubstitution):
        assert isinstance(node.children[0], Expression)
        elem = interpret(node.children[0], env)
        for child in node.children[1:1+node.expNum]:
            assert isinstance(child, Expression)
            value = interpret(child, env)
            if elem == value:
                assert isinstance(node.children[node.expNum+1], Substitution)
                interpret(node.children[node.expNum+1], env)
                return
        for child in node.children[2+node.expNum:]:
            if isinstance(child, ACaseOrSubstitution):
                for expNode in child.children[:child.expNum]:
                    assert isinstance(expNode, Expression)
                    value = interpret(expNode, env)
                    if elem == value:
                        assert isinstance(child.children[-1], Substitution)
                        interpret(child.children[-1], env)
                        return
            else:
                assert isinstance(child, Substitution)
                assert child==node.children[-1]
                interpret(child, env)
                return
    elif isinstance(node, AVarSubstitution):
        nodes = []
        for idNode in node.children[:-1]:
            assert isinstance(idNode, AIdentifierExpression)
            nodes.append(idNode)
        env.push_new_frame(nodes)
        interpret(node.children[-1], env)
        env.pop_frame()
    elif isinstance(node, AAnySubstitution) or isinstance(node, ALetSubstitution):
        nodes = []
        for idNode in node.children[:node.idNum]:
            assert isinstance(idNode, AIdentifierExpression)
            nodes.append(idNode)
        pred = node.children[-2]
        assert isinstance(pred, Predicate)
        assert isinstance(node.children[-1], Substitution)
        env.push_new_frame(nodes)
        gen = try_all_values(pred, env, nodes)
        if gen.next():
            interpret(node.children[-1], env)
        env.pop_frame()


# ****************
#
# 6. Miscellaneous
#
# ****************
    elif isinstance(node,AUnaryExpression):
        result = interpret(node.children[0], env)
        return result*(-1)
    elif isinstance(node, AIntegerExpression):
        return node.intValue
    elif isinstance(node, AMinIntExpression):
        return env._min_int
    elif isinstance(node, AMaxIntExpression):
        return env._max_int
    elif isinstance(node, AIdentifierExpression):
        #print node.idName
        return env.get_value(node.idName)
    elif isinstance(node, APrimedIdentifierExpression):
        assert len(node.children)==1 # TODO x.y.z
        assert node.grade==0 #TODO: fix for while loop
        assert isinstance(node.children[0], AIdentifierExpression)
        id_Name = node.children[0].idName
        # copy paste :-)
        assert isinstance(id_Name, str)
        return env.get_value(id_Name)
        # FIXME:
        #value_map_copy =  [x for x in env.get_state().value_stack] # no ref. copy
        # pop frame to get old value (you are inside an enumeration):
        #value_map_copy.pop()
        #value_map_copy.reverse() # FIXME
        #stack_depth = len(value_map_copy)
        # lookup:
        #for i in range(stack_depth):
        #    try:
        #        return value_map_copy[i][id_Name]
        #    except KeyError:
        #        continue
        #print "LookupErr:", id_Name
        #raise KeyError
    elif isinstance(node, ABoolSetExpression):
        return frozenset([True,False])
    elif isinstance(node, ATrueExpression):
        return True
    elif isinstance(node, AFalseExpression):
        return False
    elif isinstance(node, AStructExpression):
        dictionary = {}
        for rec_entry in node.children:
            assert isinstance(rec_entry, ARecEntry)
            name = ""
            if isinstance(rec_entry.children[0], AIdentifierExpression):
                name = rec_entry.children[0].idName
            assert isinstance(rec_entry.children[-1], Expression)
            value = interpret(rec_entry.children[-1], env)
            dictionary[name] = value
        res = []
        all_records(dictionary, res, {}, 0)
        result = []
        for dic in res:
            for entry in dic:
                result.append(tuple([entry,dic[entry]]))
        return frozenset(result)
    elif isinstance(node, ARecExpression):
        result = []
        for rec_entry in node.children:
            assert isinstance(rec_entry, ARecEntry)
            name = ""
            if isinstance(rec_entry.children[0], AIdentifierExpression):
                name = rec_entry.children[0].idName
            assert isinstance(rec_entry.children[-1], Expression)
            value = interpret(rec_entry.children[-1], env)
            result.append(tuple([name,value]))
        return frozenset(result)
    elif isinstance(node, ARecordFieldExpression):
        record = interpret(node.children[0], env)
        assert isinstance(node.children[1], AIdentifierExpression)
        name = node.children[1].idName
        for entry in record:
            if entry[0]==name:
                return entry[1]
        raise Exception("wrong entry:", name)
    elif isinstance(node, AStringSetExpression):
        return "" # TODO: return set of "all" strings ;-)
    elif isinstance(node, ATransRelationExpression):
        function = interpret(node.children[0], env)
        relation = []
        for tup in function:
            preimage = tup[0]
            for image in tup[1]:
                relation.append(tuple([preimage, image]))
        return frozenset(relation)
    elif isinstance(node, ATransFunctionExpression):
        relation = interpret(node.children[0], env)
        function = []
        for tup in relation:
            image = []
            preimage = tup[0]
            for tup2 in relation:
                if tup2[0]==preimage:
                    image.append(tup2[1])
            function.append(tuple([preimage,frozenset(image)]))
        return frozenset(function)
    elif isinstance(node, AOpSubstitution):
        op_type = env.current_mch.get_includes_op_type(node.idName)
        ret_types = op_type[0]
        para_types = op_type[1]
        id_nodes = [x[0] for x in ret_types] + [x[0] for x in para_types]
        values = []
        for i in range(len(para_types)):
            value = interpret(node.children[i], env)
            values.append(value)
        op_node = op_type[3]
        env.push_new_frame(id_nodes)
        for i in range(len(para_types)):
            name = para_types[i][0].idName
            env.set_value(name, values[i])
        assert isinstance(op_node, AOperation)
        temp = env.current_mch
        env.current_mch = op_type[4]
        result = interpret(op_node.children[-1], env)
        env.current_mch = temp
        env.pop_frame()
        return result
    else:
        raise Exception("Unknown Node: %s",node)


def replace_node(ast, idNode, replaceNode):
    if isinstance(ast, AIdentifierExpression) or isinstance(ast, AStringExpression) or isinstance(ast, AIntegerExpression):
        return ast
    for i in range(len(ast.children)):
        child = ast.children[i]
        if isinstance(child, AIdentifierExpression):
            if child.idName == idNode.idName:
                ast.children[i] = replaceNode
        else:
            replace_node(child, idNode, replaceNode)
    return ast




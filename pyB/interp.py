# -*- coding: utf-8 -*-
from config import *
from ast_nodes import *
from typing import typeit, IntegerType, PowerSetType, SetType, BType, CartType, BoolType, Substitution, Predicate, type_check_bmch, type_check_predicate
from helpers import find_var_nodes, find_var_names, flatten, is_flat, double_element_check, find_assignd_vars, print_ast
from bmachine import BMachine
from environment import Environment
from enumeration import *


# assumes that every Variable/Constant/Set appears once 
# TODO: Add typeinfo too
def write_solutions_to_env(root, env):
    for node in root.children:    
        if isinstance(node, AConjunctPredicate):
            write_solutions_to_env(node, env)
        elif isinstance(node, AEqualPredicate):
            try:
                #TODO: utlb_srv_mrtk__var_e32 --> utlb_srv_mrtk.var_e32
				if isinstance(node.children[0], AIdentifierExpression):
					expr = interpret(node.children[1], env)
					env.solutions[node.children[0].idName] = expr
					continue
				elif isinstance(node.children[1], AIdentifierExpression):
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
            if isinstance(node.children[0], AIdentifierExpression) and env.bstate.get_value(node.children[0].idName)==None:
                if isinstance(node.children[1], AIntegerExpression) or isinstance(node.children[1], ASetExtensionExpression) or isinstance(node.children[1], ABoolSetExpression) or isinstance(node.children[1], ATrueExpression) or isinstance(node.children[1], AFalseExpression):
                    try:
                        expr = interpret(node.children[1], env)
                        env.bstate.set_value(node.children[0].idName, expr)
                        lst.append(node.children[0].idName)
                        continue
                    except Exception:
                        continue 
            elif isinstance(node.children[1], AIdentifierExpression) and env.bstate.get_value(node.children[1].idName)==None:
                if isinstance(node.children[0], AIntegerExpression) or isinstance(node.children[0], ASetExtensionExpression) or isinstance(node.children[0], ABoolSetExpression) or isinstance(node.children[0], ATrueExpression) or isinstance(node.children[0], AFalseExpression):
                    try:
                        expr = interpret(node.children[0], env)
                        env.bstate.set_value(node.children[1].idName, expr)
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
    if isinstance(node,APredicateParseUnit):
        idNodes = find_var_nodes(node.children[0]) 
        idNames = [n.idName for n in idNodes]
        type_check_predicate(node, env, idNames)
        if idNames ==[]: # variable free predicate
            result = interpret(node.children[0], env)
            print result
            return
        else:
            env.bstate.add_ids_to_frame(idNames)
            learnd_vars = learn_assigned_values(node, env)
            if learnd_vars:
                print "learnd(no enumeration): ", learnd_vars
            not_set = []
            for n in idNodes:
                if env.bstate.get_value(n.idName)==None:
                    not_set.append(n)
            # enumerate only unknown vars
            if not_set:
                print "enum. vars:", [n.idName for n in not_set]
                gen = try_all_values(node.children[0], env, not_set)
                if gen.next():
                    for i in idNames:
                        print i,":", env.bstate.get_value(i)
                else:
                    print "No Solution found"
                    print False
                    return
            else:
                for i in idNames:
                    print i,":", env.bstate.get_value(i)
                result = interpret(node.children[0], env)
                print result
                return
        print True
        return None
    elif isinstance(node, AAbstractMachineParseUnit):
        mch = BMachine(node, interpret, env)
        #env.bstate.set_mch(mch)
        #print mch.name
        env.bstate = mch.bstate
        env.mch = mch
        type_check_bmch(node, mch) # also checks all included
        mch.init_include_mchs()
        mch.init_seen_mchs()
        mch.init_used_mchs()
        mch.init_extended_mchs()
        env.bstate = mch.bstate
        env.mch = mch
        # TODO: Check with B spec
        # Schneider Book page 62-64:
        # The parameters p make the constraints c True
        # #p.C
        init_mch_param(node, env, mch)

        # Sets St and constants k which meet the constraints c make the properties B True
        # C => #St,k.B
        if mch.aSetsMachineClause: # St
            interpret(mch.aSetsMachineClause, env)
        if mch.aConstantsMachineClause: # k
            interpret(mch.aConstantsMachineClause, env)
        if mch.aPropertiesMachineClause: # B
            # set up constants
            # Some Constants/Sets are set via Prop. Preds
            # TODO: give Blacklist of Variable Names
            # find all constants like x=42 oder y={1,2,3}
            learnd_vars = learn_assigned_values(mch.aPropertiesMachineClause, env)
            if learnd_vars:
                print "leard constants(no enumeration): ", learnd_vars
            # if there are constants
            #TODO: Sets
            if mch.aConstantsMachineClause:
                const_nodes = []
                # find all constants/sets which are still not set
                for idNode in mch.aConstantsMachineClause.children:
                    assert isinstance(idNode, AIdentifierExpression)
                    if env.bstate.get_value(idNode.idName)==None:
                        const_nodes.append(idNode)
                if const_nodes==[]:
                    assert interpret(mch.aPropertiesMachineClause, env)
                else:
                    # if there are unset constants/sets enumerate them
                    print "enum. vars:", [n.idName for n in const_nodes]
                    gen = try_all_values(mch.aPropertiesMachineClause, env, const_nodes)
                    assert gen.next()
                    


        # If C and B is True there should be Variables v which make the Invaraiant I True
        # TODO: B & C => #v.I
        mch.eval_Variables(env)
        mch.eval_Init(env)

        res = mch.eval_Invariant(env)

        # Not in schneiders book:
        mch.eval_Assertions(env)
        return mch # return B-machine for further processing
    elif isinstance(node, AConstantsMachineClause):
        const_names = []
        for idNode in node.children:
            assert isinstance(idNode, AIdentifierExpression)
            const_names.append(idNode.idName)
            #atype = env.get_type_by_node(idNode)
        env.bstate.add_ids_to_frame(const_names)
    elif isinstance(node, AVariablesMachineClause):
        var_names = []
        for idNode in node.children:
            assert isinstance(idNode, AIdentifierExpression)
            var_names.append(idNode.idName)
            #atype = env.get_type_by_node(idNode)
        env.bstate.add_ids_to_frame(var_names)
    elif isinstance(node, ASetsMachineClause):
        for child in node.children:
            if isinstance(child, AEnumeratedSet):
                elm_lst = []
                for elm in child.children:
                    assert isinstance(elm, AIdentifierExpression)
                    elm_lst.append(elm.idName)
                    env.bstate.add_ids_to_frame([elm.idName])
                    # The values of elements of enumerated sets are their names
                    env.bstate.set_value(elm.idName, elm.idName)
                env.bstate.add_ids_to_frame([child.idName])
                env.bstate.set_value(child.idName, frozenset(elm_lst))
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
        return interpret(node.children[0], env)
    elif isinstance(node, AAssertionsMachineClause):
        if enable_assertions:
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
        env.bstate.push_new_frame(node.children[:-1])
        max_depth = len(node.children) -2 # (two preds)
        if not forall_recursive_helper(0, max_depth, node, env):
            env.bstate.pop_frame()
            return False
        else:
            env.bstate.pop_frame()
            return True
    elif isinstance(node, AExistentialQuantificationPredicate):
        # new scope
        env.bstate.push_new_frame(node.children[:-1])
        max_depth = len(node.children) -2 # (two preds)
        if exist_recursive_helper(0, max_depth, node, env):
            env.bstate.pop_frame()
            return True
        else:
            env.bstate.pop_frame()
            return False
    elif isinstance(node, AEqualPredicate):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        # special case: learn values if None (optimization)
        if isinstance(node.children[0], AIdentifierExpression) and env.bstate.get_value(node.children[0].idName)==None:
            env.bstate.set_value(node.children[0].idName, expr2)
            return True
        elif isinstance(node.children[1], AIdentifierExpression) and env.bstate.get_value(node.children[1].idName)==None:
            env.bstate.set_value(node.children[1].idName, expr1)
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
        # new scope
        env.bstate.push_new_frame(node.children[:-1])
        max_depth = len(node.children) -2
        lst = set_comprehension_recursive_helper(0, max_depth, node, env)
        # FIXME: maybe wrong:
        # [[x1,y1],[x2,y2]..] => [(x1,y2),(x2,y2)...]
        result = []
        if is_flat(lst):
            result = lst
        else:
            for i in lst:
                result.append(tuple(flatten(i,[])))
        env.bstate.pop_frame()
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
        lst = []
        for child in node.children:
            elm = interpret(child, env)
            lst.append(elm)
        return tuple(lst)
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
        nodes = []
        result = frozenset([])
        for idNode in node.children[:node.idNum]:
            assert isinstance(idNode, AIdentifierExpression)
            nodes.append(idNode)
        env.bstate.push_new_frame(nodes)
        pred = node.children[-2]
        assert isinstance(pred, Predicate)
        gen = try_all_values(pred, env, nodes)
        while gen.next():
            result |= interpret(node.children[-1], env)
        env.bstate.pop_frame()
        return result
    elif isinstance(node, AQuantifiedIntersectionExpression):
        nodes = []
        result = frozenset([])
        for idNode in node.children[:node.idNum]:
            assert isinstance(idNode, AIdentifierExpression)
            nodes.append(idNode)
        env.bstate.push_new_frame(nodes)
        pred = node.children[-2]
        assert isinstance(pred, Predicate)
        gen = try_all_values(pred, env, nodes)
        if gen.next():
            result = interpret(node.children[-1], env)
        while gen.next():
            result &= interpret(node.children[-1], env)
        env.bstate.pop_frame()
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
        #TODO: string
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
        print "WARNING: NATURAL = 0.."+str(max_int)
        return frozenset(range(0,max_int+1)) #XXX
    elif isinstance(node, ANatural1SetExpression):
        print "WARNING: NATURAL1 = 1.."+str(max_int)
        return frozenset(range(1,max_int+1)) #XXX
    elif isinstance(node, ANatSetExpression):
        return frozenset(range(0,max_int+1))
    elif isinstance(node, ANat1SetExpression):
        return frozenset(range(1,max_int+1))
    elif isinstance(node, AIntSetExpression):
        return frozenset(range(min_int,max_int+1)) 
    elif isinstance(node, AIntegerSetExpression):
        print "WARNING: INTEGER = "+str(min_int)+".."+str(max_int)
        return frozenset(range(min_int,max_int+1)) #XXX
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
        env.bstate.push_new_frame(node.children[:-2])
        preds = node.children[-2]
        expr = node.children[-1]
        # TODO: this code (maybe) dont checks all possibilities!
        # gen. all values:
        for child in node.children[:-2]:
            # enumeration
            for i in all_values(child, env):
                env.bstate.set_value(child.idName, i)
                if interpret(preds, env):
                    sum_ += interpret(expr, env)
        # done
        env.bstate.pop_frame()
        return sum_
    elif isinstance(node, AGeneralProductExpression):
        prod = 1
        # new scope
        env.bstate.push_new_frame(node.children[:-2])
        preds = node.children[-2]
        expr = node.children[-1]
        # gen. all values:
        # TODO: this code (maybe) dont checks all possibilities!
        for child in node.children[:-2]:
            # enumeration
            for i in all_values(child, env):
                env.bstate.set_value(child.idName, i)
                if interpret(preds, env):
                    prod *= interpret(expr, env)
        env.bstate.pop_frame()
        return prod


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
        env.bstate.push_new_frame(node.children[:-2])
        pred = node.children[-2]
        expr = node.children[-1]
        # TODO: this code (maybe) dont checks all possibilities!
        # gen. all values:
        for child in node.children[:-2]:
            # enumeration
            for i in all_values(child, env):
                env.bstate.set_value(child.idName, i)
                if interpret(pred, env):
                    image = interpret(expr, env)
                    tup = tuple([i, image])
                    func_list.append(tup)
        # done
        env.bstate.pop_frame()
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
        args = [] 
        for child in node.children[1:]:
            arg = interpret(child, env)
            args.append(arg)
        if len(args) > 1:
            return get_image(function, tuple(args))
        else:
            return get_image(function, args[0])


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
        for i in range(1,max_int+1):
            sequence_list += create_all_seq_w_fixlen(list(S),i)
        return frozenset(sequence_list)
    elif isinstance(node,ASeq1Expression):
        S = interpret(node.children[0], env)
        sequence_list = []
        max_len = 1
        # find all seq. from 1..max_int
        for i in range(1,max_int+1):
            sequence_list += create_all_seq_w_fixlen(list(S),i)
        return frozenset(sequence_list)
    elif isinstance(node,AIseqExpression):
        # TODO: this can be impl. much better
        S = interpret(node.children[0], env)
        sequence_list = [frozenset([])]
        max_len = 1
        # find all seq from 1..max_int
        for i in range(1,max_int+1):
            sequence_list += create_all_seq_w_fixlen(list(S),i)
        inj_sequence_list = filter_not_injective(sequence_list)
        return frozenset(inj_sequence_list)
    elif isinstance(node, AIseq1Expression):
        # TODO: this can be impl. much better
        S = interpret(node.children[0], env)
        sequence_list = [frozenset([])]
        max_len = 1
        # find all seq from 1..max_int
        for i in range(1,max_int+1):
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
        for i in range(1,max_int+1):
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
        import copy
        #env_old = copy.deepcopy(env)
        save_state = env.bstate
        old_state = copy.deepcopy(env.bstate)       
        used_ids = []
        for i in range(int(node.lhs_size)):
            lhs_node = node.children[i]
            rhs = node.children[i+int(node.rhs_size)]
            # this copy is only used in this loop/ in this execution path
            #env_copy = copy.deepcopy(env_old)
            state_copy = copy.deepcopy(old_state)
            env.bstate = state_copy
            # BUG if the expression on the rhs has a sideeffect
            value = interpret(rhs, env)
            if isinstance(lhs_node, AIdentifierExpression):
                used_ids.append(lhs_node.idName)
                save_state.set_value(lhs_node.idName, value)
            else:
                assert isinstance(lhs_node, AFunctionExpression)
                assert isinstance(lhs_node.children[0], AIdentifierExpression)
                func_name = lhs_node.children[0].idName
                # get args
                args = []
                for child in lhs_node.children[1:]:
                    arg = interpret(child, env)
                    args.append(arg)
                func = dict(state_copy.get_value(func_name))
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
                save_state.set_value(func_name, new_func)
        while not used_ids==[]:
            name = used_ids.pop()
            if name in used_ids:
                string = name + " modified twice in multiple assign-substitution!"
                raise Exception(string)
        env.bstate = save_state
    elif isinstance(node, AConvertBoolExpression):
        return interpret(node.children[0], env)
    elif isinstance(node, ABecomesElementOfSubstitution):
        values = interpret(node.children[-1], env)
        value = list(values)[0] # XXX
        for child in node.children[:-1]:
            assert isinstance(child, AIdentifierExpression)
            env.bstate.set_value(child.idName, value)
    elif isinstance(node, ABecomesSuchSubstitution):
        # TODO: more than on ID
        nodes = []
        for child in node.children[:-1]:
            assert isinstance(child, AIdentifierExpression)
            nodes.append(child)
        # new frame to enable primed-ids
        env.bstate.push_new_frame(nodes)
        gen = try_all_values(node.children[-1], env, nodes) 
        gen.next() # sideeffect: set values
        results = []
        for n in nodes:
            i = n.idName
            results.append(env.bstate.get_value(i))
        env.bstate.pop_frame()
        # write back
        for i in range(len(nodes)):
            env.bstate.set_value(nodes[i].idName, results[i])
    elif isinstance(node, AParallelSubstitution):
        import copy
        lst = []
        assignd_ids = []
        save_state = env.bstate
        for child in node.children:
            ids = find_assignd_vars(child)
            assignd_ids += ids
            bstate_copy = copy.deepcopy(save_state)
            env.bstate = bstate_copy      
            interpret(child, env)
            lst.append(bstate_copy)
        # search for changes. no var can be modified twice (see page 108)
        assignd_ids = list(set(assignd_ids)) # throw away double-entrys
        new_values = []
        for state in lst:
            for i in assignd_ids:
                new_val = state.get_value(i)
                old_val = save_state.get_value(i)
                if not new_val==old_val:
                    new_values.append(tuple([i, new_val]))
        # check for double entrys -> Error
        id_names = [x[0] for x in new_values]
        while not id_names==[]:
            name = id_names.pop()
            if name in id_names:
                string = name + " modified twice in parallel substitution!"
                raise Exception(string)
        # write changes
        for pair in new_values:
            save_state.set_value(pair[0], pair[1])
        env.bstate = save_state
    elif isinstance(node, ASequenceSubstitution):
        for child in node.children:
            interpret(child, env)


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
        print condition, node.children[0]
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
        env.bstate.push_new_frame(nodes)
        interpret(node.children[-1], env)
        env.bstate.pop_frame()
    elif isinstance(node, AAnySubstitution) or isinstance(node, ALetSubstitution):
        nodes = []
        for idNode in node.children[:node.idNum]:
            assert isinstance(idNode, AIdentifierExpression)
            nodes.append(idNode)
        pred = node.children[-2]
        assert isinstance(pred, Predicate)
        assert isinstance(node.children[-1], Substitution)
        env.bstate.push_new_frame(nodes)
        gen = try_all_values(pred, env, nodes)
        if gen.next():
            interpret(node.children[-1], env)
        env.bstate.pop_frame()


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
        return min_int
    elif isinstance(node, AMaxIntExpression):
        return max_int
    elif isinstance(node, AIdentifierExpression):
        #print node.idName
        return env.bstate.get_value(node.idName)
    elif isinstance(node, APrimedIdentifierExpression):
        assert len(node.children)==1 # TODO x.y.z
        assert node.grade==0 #TODO: fix for while loop
        assert isinstance(node.children[0], AIdentifierExpression)
        id_Name = node.children[0].idName
        # copy paste :-)
        assert isinstance(id_Name, str)
        value_map_copy =  [x for x in env.bstate.value_stack] # no ref. copy
        # pop frame to get old value (you are inside an enumeration):
        value_map_copy.pop()
        value_map_copy.reverse() # FIXME
        stack_depth = len(value_map_copy)
        # lookup:
        for i in range(stack_depth):
            try:
                return value_map_copy[i][id_Name]
            except KeyError:
                continue
        print "LookupErr:", id_Name
        raise KeyError
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
        return "" # TODO: return set of "all" strings
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
        #FIXME: set env.btype and env.mch to the correct BMachine
        op_type = env.bstate.mch.get_includes_op_type(node.idName)
        ret_types = op_type[0]
        para_types = op_type[1]
        id_nodes = [x[0] for x in ret_types] + [x[0] for x in para_types]
        # save mch+state
        #save_state = env.bstate
        #save_mch = env.mch
        #env.bstate = call_mch.bstate
        #env.mch = call_mch
        values = []
        for i in range(len(para_types)):
            value = interpret(node.children[i], env)
            values.append(value)
        op_node = op_type[3]
        env.bstate.push_new_frame(id_nodes)
        for i in range(len(para_types)):
            name = para_types[i][0].idName
            env.bstate.set_value(name, values[i])
        assert isinstance(op_node, AOperation)
        result = interpret(op_node.children[-1], env)
        env.bstate.pop_frame()
        # revert to old mch+state
        #env.bstate = save_state
        #env.mch = save_mch
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




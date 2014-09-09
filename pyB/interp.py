# -*- coding: utf-8 -*-
from config import *
from ast_nodes import *
from typing import typeit, IntegerType, PowerSetType, SetType, BType, CartType, BoolType, Substitution, Predicate, type_check_bmch, type_check_predicate, type_check_expression
from helpers import flatten, double_element_check, find_assignd_vars, print_ast, all_ids_known, find_var_nodes, conj_tree_to_conj_list
from bmachine import BMachine
from environment import Environment
from enumeration import *
from quick_eval import quick_member_eval, infinity_belong_check
from constrainsolver import calc_possible_solutions
from pretty_printer import pretty_print
from animation_clui import print_values_b_style
from symbolic_sets import *


def eval_Invariant(root, env, mch):
    if mch.aInvariantMachineClause:
        return interpret(mch.aInvariantMachineClause, env)
    else:
        return None

def eval_Properties(root, env, mch):
    if mch.aPropertiesMachineClause:
        return intperpet(mch.aPropertiesMachineClause, env)
    else:
        return None


# if ProB found a "full solution". This shouldn't do anything, except checking the solution   
def set_up_constants(root, env, mch, solution_file_read=False):
    # 0. init sets of all machines, side-effect: change current/reference-bstate
    init_sets(root, env, mch) #TODO: modify generator for partial set up 
    #env.state_space.get_state().print_bstate()
     
    # 1. Use solution file if possible
    if solution_file_read:
        use_prob_solutions(env, mch.const_names)
        pre_set_up_state = env.state_space.get_state()
        unset_lst = __find_unset_constants(mch, pre_set_up_state)
        if unset_lst and VERBOSE:
            print "WARNING: Set Up from solution file was not complete! \nunset:%s" % unset_lst
        
        env.state_space.add_state(pre_set_up_state)
        # TODO: Parameter set up
        if VERBOSE:
            print "checking properties (with proB solutions) now.."
        if not mch.aPropertiesMachineClause==None and not interpret(mch.aPropertiesMachineClause, env):
            raise SETUPNotPossibleException("\nError: Values from solution-file caused an PROPERTIES-violation (wrong predicates above).\nMIN_INT: %s MAX_INT: %s" % (env._min_int, env._max_int))            
        elif not mch.aPropertiesMachineClause==None:
            print "Properties: True"
        env.state_space.undo()
        if VERBOSE:
            print "...no vialation found"
        return [pre_set_up_state] 
               
    # 2. set up frame and B-state
    # The reference B-state: save the status before the solutions
    bstates = []
    ref_bstate = env.state_space.get_state().clone()
    bstate = ref_bstate.clone()
    env.state_space.add_state(bstate) 
    
    # 3. search for (MAX_SET_UP-)solutions  
    generator = __set_up_constants_generator(root, env, mch)
    sol_num = 0
    for solution in generator:
        if solution:
            solution_bstate = env.state_space.get_state()
            bstates.append(solution_bstate)
            env.state_space.revert(ref_bstate)
            env.init_sets_bmachnes_names = []  
            
            sol_num = sol_num + 1
            if sol_num==MAX_SET_UP: # change config.py
                break
    env.state_space.undo() # pop ref_bstate
    return bstates




# yields False if the state was not changed
# yields True  if only one machine set up was performed successfully
# Assumption: The 'set up' of one B-machine doesn't affect the 'set up' of another
def __set_up_constants_list_generator(root, env, mch_list):
    if mch_list==[]:
        yield False
    else:
        mch = mch_list[0] 
        suc_generator = __set_up_constants_generator(mch.root, env, mch)
        for bstate_change in suc_generator:
            suc_list_generator = __set_up_constants_list_generator(root, env, mch_list[1:])
            for more_bstate_change in suc_list_generator:
                yield bstate_change or more_bstate_change     

                
# yield True: B-state was successfully changed
# yield False: no change
# FIXME:(ISSUE #27) IF M1 includes/sees M2 : Constants and set which satisfy 
# M2-Properties but not M1-Properties are NOT a solution
def __set_up_constants_generator(root, env, mch):
    # 0. set up already done?
    if mch.name in env.set_up_bmachines_names:
        yield False
    else:
        env.set_up_bmachines_names.append(mch.name)
        
    # 1. set up constants of children    
    mch_list = mch.included_mch + mch.extended_mch + mch.seen_mch + mch.used_mch
    for child_bstate_change in __set_up_constants_list_generator(root, env, mch_list):      
        env.current_mch = mch
        
        # 2. init sets and set up frames     
        parameter_names = [n.idName for n in mch.scalar_params + mch.set_params]               
        env.add_ids_to_frame(parameter_names)
        ref_bstate = env.state_space.get_state().clone() # save set up of children and frames
        
        # 3. solve constraints (bmch-parameter) and properties (bmch constants)    
        param_generator = init_mch_param(root, env, mch) # init mch-param using CONSTRAINTS-clause
        for para_solution in param_generator: 
                # case (3.1) 
                # no constants to set up.
                # so para_solution is the result of this set up     
                if mch.aConstantsMachineClause==None and mch.aAbstractConstantsMachineClause==None:
                    assert mch.aPropertiesMachineClause==None
                    # if mch_list is empty, child_bstate_change is False:
                    if mch.scalar_params==[] and mch.set_params==[]:
                        yield child_bstate_change
                    elif mch_list==[]:  
                        yield para_solution
                    else:
                        yield para_solution and child_bstate_change
                # case (3.2)
                # There are constants, but there was no set up of mch-parameters 
                # because there is nothing to set up (no state-change by param_generator)
                # OR There are constants and the set up was successful
                elif para_solution or (not para_solution and mch.scalar_params==[] and mch.set_params==[]):
                    # Some Constants/Sets are set via Prop. Preds
                    # TODO: give Blacklist of Variable Names
                    # find all constants (like x=42 or y={1,2,3}) and set them
                    learnd_vars = learn_assigned_values(mch.aPropertiesMachineClause, env)
                    if learnd_vars and VERBOSE:
                        print "learnd constants (no enumeration): ", learnd_vars
                    ref_bstate2 = env.state_space.get_state().clone() # save param set up 
                    env.add_ids_to_frame(mch.const_names)
                    
                    prop_generator = check_properties(root, env, mch)
                    for solution in prop_generator:
                        yield solution 
                        env.state_space.revert(ref_bstate2) # revert parameter set up
                env.state_space.revert(ref_bstate) # revert child set up
        if  mch.aConstantsMachineClause==None and mch.aAbstractConstantsMachineClause==None and mch.scalar_params==[] and mch.set_params==[]:
            # 4. propagate set init or possible B-state-change of children
            # if mch_list is empty, child_bstate_change is False: 
            yield child_bstate_change 


# TODO: non-determinisim init of mch-set-parameters 
# inconsistency between schneider-book page 61 and the table on manrefb page 110.
# This implementation is compatible to manrefb: The Properties-clause is not used!
def init_mch_param(root, env, mch):
    __init_set_mch_parameter(root, env, mch)
    scalar_parameter_present = not mch.scalar_params==[]
    # case (1). scalar param. and maybe set param
    if scalar_parameter_present:
        if mch.aConstraintsMachineClause==None:
            names = [n.idName for n in mch.scalar_params]
            raise SETUPNotPossibleException("\nError: Missing ConstraintsMachineClause in %s! Can not set up: %s" % (mch.name, names))
        pred = mch.aConstraintsMachineClause
        gen = try_all_values(pred, env, mch.scalar_params)
        for possible in gen:
            yield possible
    # case (2). no scalar param. but set param
    elif not mch.set_params==[] and not scalar_parameter_present:
        yield True  # only set_up of set-parameters, set_up succeeds
    # case (3) nothing present and nothing done
    else:
        assert mch.scalar_params==[] and not scalar_parameter_present
        yield False # no bstate change 


# helper of init_mch_param
def __init_set_mch_parameter(root, env, mch):
    # TODO: retry with different set elem. num if no animation possible
    for n in mch.set_params:
        elem_lst = []
        name = n.idName 
        for i in range(SET_PARAMETER_NUM):
            e_name = str(i)+"_"+name
            elem_lst.append(e_name)      
        env.set_value(name, frozenset(elem_lst))

                
# only(!) inits sets of all machines
# TODO: When the ProB-Solution-file also contains set-solutions, this
#       code will need a refactoring (Uses this solutions)
def init_sets(node, env, mch):
    # (1) avoid double set-init
    if mch.name in env.init_sets_bmachnes_names:
        return 
    env.init_sets_bmachnes_names.append(mch.name)
    mch_list = mch.included_mch + mch.extended_mch + mch.seen_mch + mch.used_mch
    # (2) init-sets of child-bmch
    for m in mch_list:
        init_sets(node, env, m)
    env.current_mch = mch
    # (3) init sets if present
    if mch.aSetsMachineClause: # St
        node = mch.aSetsMachineClause
        for child in node.children:
            if isinstance(child, AEnumeratedSet):
                elm_lst = []
                for elm in child.children:
                    assert isinstance(elm, AIdentifierExpression)
                    elm_lst.append(elm.idName)
                    env.add_ids_to_frame([elm.idName])
                    # values of elements of enumerated sets are their names
                    env.set_value(elm.idName, elm.idName)
                env.add_ids_to_frame([child.idName])
                env.set_value(child.idName, frozenset(elm_lst))
            else:
                init_deffered_set(child, env) # done by enumeration.py


# yield True if successful B-state change
def check_properties(node, env, mch):
    if mch.aPropertiesMachineClause: # B
        # set up constants
        # if there are constants
        if mch.aConstantsMachineClause or mch.aAbstractConstantsMachineClause:
            const_nodes = []
            idNodes     = []
            # find all constants/sets which are still not set
            if mch.aConstantsMachineClause:
                idNodes = mch.aConstantsMachineClause.children
            if mch.aAbstractConstantsMachineClause:
                idNodes += mch.aAbstractConstantsMachineClause.children
            for idNode in idNodes:
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
                assert prop_result # if this is False: there musst be a Bug inside the interpreter
                yield prop_result 
            else:
                # if there are unset constants/sets enumerate them
                at_least_one_solution = False
                if VERBOSE:
                    print "enum. constants:", [n.idName for n in const_nodes]
                gen = try_all_values(mch.aPropertiesMachineClause.children[0], env, const_nodes)
                for prop_result in gen:
                    if prop_result:
                        at_least_one_solution = True
                        yield True
                # This generator is only called when the Constraints are True.
                # No Properties-solution means set_up fail
                if not at_least_one_solution: 
                    print "\nFALSE Predicates:"
                    print_predicate_fail(env, mch.aPropertiesMachineClause.children[0])
                    raise SETUPNotPossibleException("\nError: Properties FALSE in machine: %s!" % (mch.name))
        #TODO: Sets-Clause
    yield False # avoid stop iteration bug
            

# if ProB found a "full solution". This shouldn't do anything, except checking the solution            
# calcs up to MAX_INIT init B-states
def exec_initialisation(root, env, mch, solution_file_read=False):
    # 0. Use solution file if possible
    if solution_file_read:
        use_prob_solutions(env, mch.var_names)
        pre_init_state = env.state_space.get_state()
        unset_lst = __find_unset_variables(mch, pre_init_state)
        if unset_lst and VERBOSE:
            print "WARNING: Init from solution file was not complete! unset:%s" % unset_lst
        
        env.state_space.add_state(pre_init_state)
        if not mch.aInvariantMachineClause==None and not interpret(mch.aInvariantMachineClause, env):
            raise INITNotPossibleException("\nError: INITIALISATION unsuccessfully. Values from solution-file caused an INVARIANT-violation")
        env.state_space.undo()
        return [pre_init_state] 
               
    # 1. set up frames and state
    bstates = []
    ref_bstate = env.state_space.get_state().clone()
    env.state_space.add_state(ref_bstate)
     
    
    # 2. search for solutions  
    generator = __exec_initialisation_generator(root, env, mch)
    sol_num = 0
    for solution in generator:
        if solution:
            solution_bstate = env.state_space.get_state()
            bstates.append(solution_bstate)
            env.state_space.revert(ref_bstate) # revert to ref B-state
            env.init_bmachines_names = []
            
            sol_num = sol_num +1
            if sol_num==MAX_INIT:
                break 
    env.state_space.undo() # pop ref_state
    return bstates


# yields False if the state was not changed
# yields True  if only one machine init was performed successfully
# Assumption: The 'init' of one B-machine doesn't affect the 'init' of another
def __exec_initialisation_list_generator(root, env, mch_list):
    if mch_list==[]:
        yield False
    else:
        mch = mch_list[0] 
        init_generator = __exec_initialisation_generator(mch.root, env, mch)
        for bstate_change in init_generator:
            init_list_generator = __exec_initialisation_list_generator(root, env, mch_list[1:])
            for more_bstate_change in init_list_generator:
                yield bstate_change or more_bstate_change        

                

def __exec_initialisation_generator(root, env, mch):
    # 1. check if init already done to avoid double init
    if mch.name in env.init_bmachines_names:
        yield False
    else:
        env.init_bmachines_names.append(mch.name)
            
    # 2. init children
    children = mch.included_mch + mch.extended_mch + mch.seen_mch + mch.used_mch
    init_list_generator = __exec_initialisation_list_generator(root, env, children)

    # TODO state revert?
    for child_bstate_change in init_list_generator:         
        # 3. set up state and env. for init exec
        env.current_mch = mch 
        env.add_ids_to_frame(mch.var_names)
        ref_bstate = env.state_space.get_state().clone() # save init of children (this is a Bugfix and not the solution)
        
        # 3.1 nothing to be init.        
        if not mch.aInitialisationMachineClause:
            if not mch.aVariablesMachineClause==None and not mch.aConcreteVariablesMachineClause==None:
                raise INITNotPossibleException("\nError: Missing InitialisationMachineClause in %s!" % mch.name)
            yield child_bstate_change
        # 3.2. search for solutions  
        else:                 
            at_least_one_possible = False
            ex_sub_generator = exec_substitution(mch.aInitialisationMachineClause.children[-1], env)
            for bstate_change in ex_sub_generator:
                if bstate_change:
                    at_least_one_possible = True
                    yield True
                    env.state_space.revert(ref_bstate) # revert to current child-init-solution
            if not at_least_one_possible:
                raise INITNotPossibleException("\nWARNING: Problem while exec init. No init found/possible! in %s" % mch.name)


# TODO: use solutions of child mch (seen, used mch)
def use_prob_solutions(env, idNames):
    for name in env.solutions:
        # TODO: ordering of solutions (important!)
        #print "use_prob_solutions"
        if name in idNames:
            node = env.solutions[name]
            #print
            #print
            #print "setting ",name, " to:", pretty_print(node) 
            value = interpret(node, env)
            env.set_value(name, value)
        #print "ProB solutions set to env"
        


# search a conjunction of predicates for a false subpredicate and prints it.
# This python function is used to get better error massages for failing properties or invariants
def print_predicate_fail(env, node):
    pred_lst = []
    # if the input node is a pro
    if not (isinstance(node, AConjunctPredicate) or isinstance(node, ADisjunctPredicate)):
        pred_lst.append(node)
    while isinstance(node, AConjunctPredicate):
        pred_lst.append(node.children[1])
        node = node.children[0]
    for p in pred_lst:
        result = interpret(p, env)
        if not result:
            print "FALSE = ("+pretty_print(p)+")"
            #print p.children[0].idName, env.get_value(p.children[0].idName)    
           

def __check_unset(names, bstate, mch):
    fail_lst = []
    for id_Name in names:
        try:
            value = bstate.get_value(id_Name, mch)
            if value==None:
                fail_lst.append(id_Name)    
        except ValueNotInBStateException:
            fail_lst.append(id_Name)
    return fail_lst


# checks if there are any unset variables
def __find_unset_variables(mch, bstate):
    # TODO: Find unset in child-mchs
    var_lst = mch.var_names
    fail_lst = __check_unset(var_lst, bstate, mch)
    return fail_lst 


# checks if there are any unset constants
def __find_unset_constants(mch, bstate):
     # TODO: Find unset in child-mchs
    const_lst = mch.const_names #+ mch.eset_names + mch.dset_names
    fail_lst = __check_unset(const_lst, bstate, mch)
    return fail_lst 
    
    
def learn_assigned_values(root, env):
    lst = []
    _learn_assigned_values(root, env, lst)
    return lst
    

# node is an "side-effect-free" AST (no assignments ':=' )
def _learn_assigned_values(root, env, lst):
    for node in root.children:
        if isinstance(node, AEqualPredicate):
            expression_node = None
            idNode          = None
            # special case: learn values if None (optimization)
            if isinstance(node.children[0], AIdentifierExpression) and env.get_value(node.children[0].idName)==None:
                expression_node = node.children[1]
                idNode          = node.children[0]
            # symmetric other case. 'Expr = X' instead of 'X = Expr'
            elif isinstance(node.children[1], AIdentifierExpression) and env.get_value(node.children[1].idName)==None:
                expression_node = node.children[0]
                idNode          = node.children[1]
            else:
                continue # case not implemented: skip
            
            assert not expression_node==None
            # TODO: use idNodes-result to check if an eval. of expression node is possible
            # maybe this enum of node-classes becomes unnecessary
            
            if isinstance(expression_node, (AIntegerExpression, ASetExtensionExpression, ABoolSetExpression, ATrueExpression, AFalseExpression, AEmptySetExpression)):
                try:
                    expr = interpret(expression_node, env)
                    env.set_value(idNode.idName, expr)
                    lst.append(idNode.idName)
                    continue
                except Exception as e:
                    #TODO: this case is not covered by any test
                    continue 
            # only uses lambda which can be solved instantly 
            elif isinstance(expression_node, ALambdaExpression):# and idNodes==[]:
                try:
                    expr = interpret(expression_node, env)
                    env.set_value(idNode.idName, expr)
                    lst.append(idNode.idName)
                    continue
                except Exception as e:
                    print "Exception:",e
                    continue 

        # df-search for equations 
        elif isinstance(node, AConjunctPredicate):
            _learn_assigned_values(node, env, lst)


# side-effect:
# evals pred and sets var to values
# main interpreter-switch (sorted/grouped like b-toolkit list)
# Predicate Nodes Return True/False
# Expression Nodes Return Values (int, frozenset, boolean, string or composed)
def interpret(node, env):

# ********************************************
#
#        0. Interpretation-mode 
#
# ********************************************
    #print "DEBUG! interpret: ", pretty_print(node)  # DEBUG
    assert not isinstance(node, Substitution) # TODO: refactor
    if isinstance(node, APredicateParseUnit): #TODO: move print to animation_clui
        type_check_predicate(node, env)
        idNodes = find_var_nodes(node) 
        idNames = [n.idName for n in idNodes]
        if idNames ==[]: # variable free predicate
            result = interpret(node.children[0], env)
            return result
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
    elif isinstance(node, AExpressionParseUnit): #TODO more
        #TODO: move print to animation_clui
        type_check_expression(node, env)
        idNodes = find_var_nodes(node) 
        idNames = [n.idName for n in idNodes]
        if idNames ==[]: # variable free expression
            result = interpret(node.children[0], env)
            return result
        else:
            return "Warning: Expressions with variables are not implemented now"
            

# ********************************************
#
#        0. Clauses
#
# ********************************************
    elif isinstance(node, AConstraintsMachineClause):
        return interpret(node.children[-1], env)
    elif isinstance(node, APropertiesMachineClause): #TODO: maybe predicate fail?
        lst = conj_tree_to_conj_list(node.children[0])
        result = True
        for n in lst:
            try:
                value = interpret(n, env)
            except OverflowError:
                print "\033[1m\033[91mFAIL\033[00m: Enumeration overflow cause by: ("+pretty_print(n)+")"
                continue
            if PRINT_SUB_PROPERTIES: # config.py
                string = str(value)
                if string=="False":
                   print '\033[1m\033[91m'+'False'+'\033[00m'+": "+pretty_print(n)
                elif string=="True":
                   print '\033[1m\033[92m'+'True'+'\033[00m'+": "+pretty_print(n)
                else: #XXX
                   print '\033[1m\033[94m'+string+'\033[00m'+": "+pretty_print(n)
            result = result and value
        return result
    elif isinstance(node, AInvariantMachineClause):
        result = interpret(node.children[0], env)
        if not result:
            print "\nFALSE Predicates:"
            print_predicate_fail(env, node.children[0])
        return result
    elif isinstance(node, AAssertionsMachineClause):
        if ENABLE_ASSERTIONS:
            print "checking assertions"
            for child in node.children:
                #print_ast(child)
                result = interpret(child, env)
                print result,": \t", pretty_print(child)
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
        assert isinstance(expr1, bool) and isinstance(expr2, bool)
        return expr1 == expr2 
    elif isinstance(node, ANegationPredicate):
        expr = interpret(node.children[0], env)
        return not expr
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
        #print expr1,"=",expr2
        # special case: learn values if None (optimization)
        if isinstance(node.children[0], AIdentifierExpression) and env.get_value(node.children[0].idName)==None:
            env.set_value(node.children[0].idName, expr2)
            return True
        elif isinstance(node.children[1], AIdentifierExpression) and env.get_value(node.children[1].idName)==None:
            env.set_value(node.children[1].idName, expr1)
            return True
        #elif isinstance(expr1, SymbolicSet) and isinstance(expr2, frozenset):
        #    expr1 = enum_symbolic(expr1, node)
        #    return expr1 == expr2
        # frozensets can only be compared to frozensets
        elif isinstance(expr2, SymbolicSet) and isinstance(expr1, frozenset):
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
        varList = node.children[:-1]
        pred = node.children[-1]
        return SymbolicComprehensionSet(varList, pred, node, env, interpret, calc_possible_solutions)      
    elif isinstance(node, AUnionExpression):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
        if isinstance(aSet1, SymbolicSet) or isinstance(aSet2, SymbolicSet):
            return SymbolicUnionSet(aSet1, aSet2, env, interpret)
        return aSet1.union(aSet2)
    elif isinstance(node, AIntersectionExpression):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
        # TODO: symbolic intersection instance
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
        if isinstance(aSet, SymbolicSet):
            return SymbolicPowerSet(aSet, env, interpret)
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
        domain_generator = calc_possible_solutions(pred, env, varList, interpret)
        for entry in domain_generator:
            for name in [x.idName for x in varList]:
                value = entry[name]
                env.set_value(name, value)
            try:
                if interpret(pred, env):  # test (|= ior)
                    aSet = interpret(expr, env)
                    if isinstance(aSet, SymbolicSet):
                        aSet = aSet.enumerate_all()  
                    result |= aSet
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
        domain_generator = calc_possible_solutions(pred, env, varList, interpret)
        for entry in domain_generator:
            for name in [x.idName for x in varList]:
                value = entry[name]
                env.set_value(name, value)
            try:
                if interpret(pred, env):  # test
                    # intersection with empty set is always empty: two cases are needed
                    if result==frozenset([]): 
                        result = interpret(expr, env)
                        if isinstance(result, SymbolicSet):
                            result = result.enumerate_all()   
                    else:
                        aSet = interpret(expr, env)
                        if isinstance(aSet, SymbolicSet):
                            aSet = aSet.enumerate_all()       
                        result &= aSet
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
        #print pretty_print(node)
        if contains_infinit_enum(node, env):
            result = infinity_belong_check(node, env)
            #print result
            return result
        if all_ids_known(node, env): #TODO: check over-approximation. All ids need to be bound?
            elm = interpret(node.children[0], env)
            result = quick_member_eval(node.children[1], env, elm)
            #print result
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


# *****************
#
#       3. Numbers
#
# *****************
    elif isinstance(node, ANaturalSetExpression):
        return NaturalSet(env, interpret)
    elif isinstance(node, ANatural1SetExpression):
        return Natural1Set(env, interpret)
    elif isinstance(node, ANatSetExpression):
        return NatSet(env, interpret)
    elif isinstance(node, ANat1SetExpression):
        return Nat1Set(env, interpret)
    elif isinstance(node, AIntSetExpression):
        return IntSet(env, interpret)
    elif isinstance(node, AIntegerSetExpression):
        return IntegerSet(env, interpret)
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
        if isinstance(expr2, SymbolicSet):
            expr2 = expr2.enumerate_all()
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
        return SymbolicIntervalSet(left, right, env, interpret)
        #return frozenset(range(left, right+1))
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
                    sum_ += interpret(expr, env)
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
                    prod_ *= interpret(expr, env)
            except ValueNotInDomainException:
                continue
        env.pop_frame() # exit scope
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
        if isinstance(aSet1, SymbolicSet) or isinstance(aSet2, SymbolicSet):
            return SymbolicRelationSet(aSet1, aSet2, env, interpret, node)
        aSet = make_set_of_realtions(aSet1, aSet2)
        return aSet
    elif isinstance(node, ADomainExpression):
        # assumption: crashs if this is not a set of 2-tuple
        aSet = interpret(node.children[0], env)
        if isinstance(aSet, SymbolicSet):
            aSet = aSet.enumerate_all()
        dom = [e[0] for e in list(aSet)]
        return frozenset(dom)
    elif isinstance(node, ARangeExpression):
        # assumption: crashs if this is not a set of 2-tuple
        aSet = interpret(node.children[0], env)
        if isinstance(aSet, SymbolicSet):
            aSet = aSet.enumerate_all()
        ran = [e[1] for e in list(aSet)]
        return frozenset(ran)
    elif isinstance(node, ACompositionExpression):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
        if isinstance(aSet1, SymbolicSet) or isinstance(aSet2, SymbolicSet):
            return SymbolicCompositionSet(aSet1, aSet2, env, interpret, node)
        # p and q: tuples representing domain and image
        new_rel = [(p[0],q[1]) for p in aSet1 for q in aSet2 if p[1]==q[0]]
        return frozenset(new_rel)
    elif isinstance(node, AIdentityExpression):
        aSet = interpret(node.children[0], env)
        return SymbolicIdentitySet(aSet, aSet, env, interpret, node)
    elif isinstance(node, ADomainRestrictionExpression):
        aSet = interpret(node.children[0], env)
        rel = interpret(node.children[1], env)
        if isinstance(rel, SymbolicSet):
            #avoid infinit enum
            if isinstance(aSet, SymbolicSet):
                aSet = aSet.enumerate_all()
            new_rel = [(x,rel[x]) for x in aSet]
        else:
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
        if isinstance(rel, SymbolicSet):
            rel = rel.enumerate_all()
        new_rel = [(x[1],x[0]) for x in rel]
        return frozenset(new_rel)
        #return SymbolicInverseRelation(rel, env, interpret, node)
    elif isinstance(node, AImageExpression):
        #print "DEBUG! interpret(AImageExpression): ", pretty_print(node)
        rel = interpret(node.children[0], env)
        aSet = interpret(node.children[1], env)
        #print rel,
        #print aSet
        if isinstance(rel, SymbolicSet):
            image = []
            if isinstance(aSet, SymbolicSet):
                aSet = aSet.enumerate_all()
            for x in aSet:
                try:
                    image.append(rel[x])
                except ValueNotInDomainException:
                    continue
        else:
            image = [x[1] for x in rel if x[0] in aSet ]
        return frozenset(image)
    elif isinstance(node, AOverwriteExpression):
        #print pretty_print(node)
        r1 = interpret(node.children[0], env)
        r2 = interpret(node.children[1], env)
        if isinstance(r1, SymbolicSet):
            r1 = r1.enumerate_all()
        if isinstance(r2, SymbolicSet):
            r2 = r2.enumerate_all()
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
        #print pretty_print(node)
        arel = interpret(node.children[0], env)
        if isinstance(arel, SymbolicSet):
            arel = arel.enumerate_all()
        rel = list(arel)
        while True: # fixpoint-search (do-while-loop)
            new_rel = [(y[0],x[1]) for y in rel for x in arel if y[1]==x[0]]
            if frozenset(new_rel).union(frozenset(rel))==frozenset(rel):
                return frozenset(rel)
            rel =list(frozenset(new_rel).union(frozenset(rel)))
    elif isinstance(node, AFirstProjectionExpression):
        S = interpret(node.children[0], env)
        T = interpret(node.children[1], env)
        if isinstance(S, SymbolicSet) or isinstance(T, SymbolicSet):
            return SymbolicFirstProj(S,T, env, interpret, node)
        cart = frozenset(((x,y) for x in S for y in T))
        proj = [(t,t[0]) for t in cart]
        return frozenset(proj)
    elif isinstance(node, ASecondProjectionExpression):
        S = interpret(node.children[0], env)
        T = interpret(node.children[1], env)
        if isinstance(S, SymbolicSet) or isinstance(T, SymbolicSet):
            return SymbolicSecondProj(S,T, env, interpret, node)
        cart = frozenset(((x,y) for x in S for y in T))
        proj = [(t,t[1]) for t in cart]
        return frozenset(proj)



# *******************
#
#       4.1 Functions
#
# *******************
    elif isinstance(node, APartialFunctionExpression):
        S = interpret(node.children[0], env)
        T = interpret(node.children[1], env)
        if isinstance(S, SymbolicSet) or isinstance(T, SymbolicSet):
            return SymbolicPartialFunctionSet(S, T, env, interpret, node)
        relation_set = make_set_of_realtions(S,T) # S<->T
        fun = filter_no_function(relation_set) # S+->T
        return fun
    elif isinstance(node, ATotalFunctionExpression):
        S = interpret(node.children[0], env)
        T = interpret(node.children[1], env)
        if isinstance(S, SymbolicSet) or isinstance(T, SymbolicSet):
            return SymbolicTotalFunctionSet(S, T, env, interpret, node)
        relation_set = make_set_of_realtions(S,T) # S<->T
        fun = filter_no_function(relation_set) # S+->T
        total_fun = filter_not_total(fun, S) # S-->T
        return total_fun
    elif isinstance(node, APartialInjectionExpression):
        S = interpret(node.children[0], env)
        T = interpret(node.children[1], env)
        if isinstance(S, SymbolicSet) or isinstance(T, SymbolicSet):
            return SymbolicPartialInjectionSet(S, T, env, interpret, node)
        relation_set = make_set_of_realtions(S,T) # S<->T
        fun = filter_no_function(relation_set) # S+->T
        inj_fun = filter_not_injective(fun) # S>+>T
        return inj_fun
    elif isinstance(node, ATotalInjectionExpression):
        S = interpret(node.children[0], env)
        T = interpret(node.children[1], env)
        if isinstance(S, SymbolicSet) or isinstance(T, SymbolicSet):
            return SymbolicTotalInjectionSet(S, T, env, interpret, node)
        relation_set = make_set_of_realtions(S,T) # S<->T
        fun = filter_no_function(relation_set) # S+->T
        inj_fun = filter_not_injective(fun) # S>+>T
        total_inj_fun = filter_not_total(inj_fun, S) # S>->T
        return total_inj_fun
    elif isinstance(node, APartialSurjectionExpression):
        S = interpret(node.children[0], env)
        T = interpret(node.children[1], env)
        if isinstance(S, SymbolicSet) or isinstance(T, SymbolicSet):
            return SymbolicPartialSurjectionSet(S, T, env, interpret, node)
        relation_set = make_set_of_realtions(S,T) # S<->T
        fun = filter_no_function(relation_set) # S+->T
        surj_fun = filter_not_surjective(fun, T) # S+->>T
        return surj_fun
    elif isinstance(node, ATotalSurjectionExpression):
        S = interpret(node.children[0], env)
        T = interpret(node.children[1], env)
        if isinstance(S, SymbolicSet) or isinstance(T, SymbolicSet):
            return SymbolicTotalSurjectionSet(S, T, env, interpret, node)
        relation_set = make_set_of_realtions(S,T) # S<->T
        fun = filter_no_function(relation_set) # S+->T
        surj_fun = filter_not_surjective(fun, T) # S+->>T
        total_surj_fun = filter_not_total(surj_fun, S) # S-->>T
        return total_surj_fun
    elif isinstance(node, ATotalBijectionExpression):
        S = interpret(node.children[0], env)
        T = interpret(node.children[1], env)
        if isinstance(S, SymbolicSet) or isinstance(T, SymbolicSet):
            return SymbolicTotalBijectionSet(S, T, env, interpret, node)
        relation_set = make_set_of_realtions(S,T) # S<->T
        fun = filter_no_function(relation_set) # S+->T
        inj_fun = filter_not_injective(fun) # S>+>T
        total_inj_fun = filter_not_total(inj_fun, S) # S>->T
        bij_fun = filter_not_surjective(total_inj_fun,T) # S>->>T
        return bij_fun
    elif isinstance(node, APartialBijectionExpression):
        S = interpret(node.children[0], env)
        T = interpret(node.children[1], env)
        if isinstance(S, SymbolicSet) or isinstance(T, SymbolicSet):
            return SymbolicPartialBijectionSet(S, T, env, interpret, node)
        relation_set = make_set_of_realtions(S,T) # S<->T
        fun = filter_no_function(relation_set) # S+->T
        inj_fun = filter_not_injective(fun) # S>+>T
        bij_fun = filter_not_surjective(inj_fun,T)
        return bij_fun
    elif isinstance(node, ALambdaExpression):
        varList = node.children[:-2]
        pred = node.children[-2]
        expr = node.children[-1]
        return SymbolicLambda(varList, pred, expr, node, env, interpret, calc_possible_solutions)
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
        #print perm_sequence_list
        return frozenset(perm_sequence_list)
    elif isinstance(node, AConcatExpression):
        # u:= s^t
        s = interpret(node.children[0], env)
        t = interpret(node.children[1], env)
        u = list(s)
        for tup in t:
            index = tup[0]+len(s)
            u.append(tuple([index, tup[1]]))
        return frozenset(u)
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
        #print "sequence", sequence
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
# 6. Miscellaneous
#
# ****************
    elif isinstance(node, AConvertBoolExpression): 
        return interpret(node.children[0], env)
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
        # FIXME (ISSUE #28):
        #value_map_copy =  [x for x in env.get_state().value_stack] # no ref. copy
        # pop frame to get old value (you are inside an enumeration):
        #value_map_copy.pop()
        #value_map_copy.reverse() # FIXME (ISSUE #28)
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
        raise Exception("\nError: Problem inside RecordExpression - wrong entry: %s" % name)
    elif isinstance(node, AStringSetExpression):
        return StringSet(env, interpret)
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
    elif isinstance(node, AExternalFunctionExpression):
        args = []
        for child in node.children:
            arg = interpret(child, env)
            args.append(arg)
        result = node.pyb_impl(args)
        return result
    else:
        raise Exception("\nError: Unknown/unimplemented node inside interpreter: %s",node)


# side-effect: changes state while exec.
# returns True if substitution was possible
# Substituions return True/False if the substitution was possible
def exec_substitution(sub, env):
    
    
# ****************
#
# 5. Substitutions
#
# ****************
    assert isinstance(sub, Substitution)
    if isinstance(sub, ASkipSubstitution):
        yield True # always possible
    elif isinstance(sub, AAssignSubstitution):
        assert int(sub.lhs_size) == int(sub.rhs_size)     
        used_ids = []
        values = []
        # get values of all expressions (rhs)
        for i in range(int(sub.rhs_size)):
            rhs = sub.children[i+int(sub.rhs_size)]
            value = interpret(rhs, env)
            values.append(value)
        for i in range(int(sub.lhs_size)):
            lhs_node = sub.children[i]            
            # BUG if the expression on the rhs has a side-effect
            value = values[i]
            # case (1) lhs: no function
            if isinstance(lhs_node, AIdentifierExpression):
                used_ids.append(lhs_node.idName)
                env.set_value(lhs_node.idName, value)
            # case (2) lhs: is function 
            else:
                assert isinstance(lhs_node, AFunctionExpression)
                assert isinstance(lhs_node.children[0], AIdentifierExpression)
                func_name = lhs_node.children[0].idName
                # get args and convert to dict
                args = []
                for child in lhs_node.children[1:]:
                    arg = interpret(child, env)
                    args.append(arg)
                func = dict(env.get_value(func_name))
                used_ids.append(func_name)
                # mapping of func values
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
            # case (3) record: 3 # TODO
        while not used_ids==[]:
            name = used_ids.pop()
            if name in used_ids:
                raise Exception("\nError: %s modified twice in multiple assign-substitution!" % name)
        yield True # assign(s) was/were  successful 
    elif isinstance(sub, ABecomesElementOfSubstitution):
        values = interpret(sub.children[-1], env)
        print "DEBUG becomes:",values
        if values==frozenset([]): #empty set has no elements -> subst. imposible
            yield False
        else:
            for value in values: 
                for child in sub.children[:-1]:
                    assert isinstance(child, AIdentifierExpression)
                    env.set_value(child.idName, value)
                yield True # assign was successful 
    elif isinstance(sub, ABecomesSuchSubstitution):
        # TODO: more than on ID on lhs
        nodes = []
        for child in sub.children[:-1]:
            assert isinstance(child, AIdentifierExpression)
            nodes.append(child)
        # new frame to enable primed-ids
        env.push_new_frame(nodes)
        gen = try_all_values(sub.children[-1], env, nodes) 
        for possible in gen: # sideeffect: set values 
            if not possible:
                env.pop_frame() 
                yield False
            else:
                results = []
                for n in nodes:
                    i = n.idName
                    results.append(env.get_value(i))
                
                # write back if solution 
                if interpret(sub.children[-1], env):
                    env.pop_frame() # exit new frame
                    for i in range(len(nodes)):
                        env.set_value(nodes[i].idName, results[i])
                    yield True
                else:
                    env.pop_frame() # exit new frame
                env.push_new_frame(nodes) #enum next value in next-interation
        env.pop_frame()
    elif isinstance(sub, AParallelSubstitution):
        # 0. setup: get all substitutions 
        subst_list = []      
        for child in sub.children:
            assert isinstance(child, Substitution)
            subst_list.append(child)
        if subst_list==[]:
            yield False
        else:
            ref_state = env.get_state().clone()
            new_values = [] # values changed by this path
            # for explanation see function comments  
            ex_pa_generator = exec_parallel_substitution(subst_list, env, ref_state, new_values)
            for possible in ex_pa_generator:
                # 1. possible combination found
                if possible:
                    # 2. test: no variable can be modified twice (see page 108)
                    # check for double entrys -> Error
                    id_names = [x[0] for x in new_values]
                    while not id_names==[]:
                        name = id_names.pop()
                        if name in id_names:
                            raise Exception("\nError: modified twice in parallel substitution: " % s)
                    # 3. write changes to state
                    for pair in new_values:
                        name = pair[0]
                        value = pair[1]
                        env.set_value(name, value)
                    yield True # False if no branch was executable
                    # 4. reset for next loop
                    ref_state = env.get_state().clone()                  
    elif isinstance(sub, ASequenceSubstitution):
        subst_list = []
        for child in sub.children:
            assert isinstance(child, Substitution)
            subst_list.append(child)
        # for explanation see function comments 
        for possible in exec_sequence_substitution(subst_list, env):
            yield possible
    elif isinstance(sub, AWhileSubstitution):
        if PRINT_WARNINGS:
            print "WARNING: WHILE inside abstract MACHINE!" # TODO: replace/move warning
        condition = sub.children[0]
        doSubst   = sub.children[1]
        invariant = sub.children[2]
        variant   = sub.children[3]
        assert isinstance(condition, Predicate) 
        assert isinstance(doSubst, Substitution)
        assert isinstance(invariant, Predicate)  
        assert isinstance(variant, Expression) 
        v_value = interpret(variant, env)
        ex_while_generator = exec_while_substitution(condition, doSubst, invariant, variant, v_value, env)
        for possible in ex_while_generator:
            yield possible


# **********************
#
# 5.1. Alternative Syntax
#
# ***********************
    elif isinstance(sub, ABlockSubstitution):
        ex_generator = exec_substitution(sub.children[-1], env)
        for possible in ex_generator:
            yield possible
    elif isinstance(sub, APreconditionSubstitution):
        assert isinstance(sub.children[0], Predicate)
        assert isinstance(sub.children[1], Substitution)
        condition = interpret(sub.children[0], env)
        #print condition, node.children[0]
        if condition:
            ex_generator = exec_substitution(sub.children[1], env)
            for possible in ex_generator:
                yield possible
        else:
            yield False
    elif isinstance(sub, AAssertionSubstitution):
        assert isinstance(sub.children[0], Predicate)
        assert isinstance(sub.children[1], Substitution)
        if not interpret(sub.children[0], env):
            print "ASSERT violated:", pretty_print(sub.children[0])
            yield False  #TODO: What is correct: False or crash\Exception?
        ex_generator = exec_substitution(sub.children[1], env)
        for possible in ex_generator:
            yield possible
    elif isinstance(sub, AIfSubstitution):
        assert isinstance(sub.children[0], Predicate)
        assert isinstance(sub.children[1], Substitution)
        all_cond_false = True
        condition = interpret(sub.children[0], env)
        if condition: # take "THEN" Branch
            all_cond_false = False
            ex_generator = exec_substitution(sub.children[1], env)
            for possible in ex_generator:
                yield possible
        for child in sub.children[2:]:
            if isinstance(child, AIfElsifSubstitution):
                assert isinstance(child.children[0], Predicate)
                assert isinstance(child.children[1], Substitution)
                sub_condition = interpret(child.children[0], env)
                if sub_condition:
                    all_cond_false = False
                    ex_generator = exec_substitution(child.children[1], env)
                    for possible in ex_generator:
                        yield possible
            elif not isinstance(child, AIfElsifSubstitution) and all_cond_false: 
                # ELSE (B Level)
                assert isinstance(child, Substitution)
                assert child==sub.children[-1] # last child
                assert sub.hasElse=="True"
                ex_generator = exec_substitution(child, env)
                for possible in ex_generator:
                    yield possible
        if sub.hasElse=="False" and all_cond_false:
            yield True # no Else, default: IF P THEN S ELSE skip END
    elif isinstance(sub, AChoiceSubstitution):
        assert isinstance(sub.children[0], Substitution)
        for child in sub.children[1:]:
            assert isinstance(child, AChoiceOrSubstitution)
        ex_generator = exec_substitution(sub.children[0], env)
        for possible in ex_generator:
            yield possible
        for or_branch in sub.children[1:]:
            ex_generator = exec_substitution(or_branch.children[0], env)
            for possible in ex_generator:
                yield possible            
    elif isinstance(sub, ASelectSubstitution):
        nodes = []
        assert isinstance(sub.children[0], Predicate)
        assert isinstance(sub.children[1], Substitution)
        # (1) find enabled conditions and remember this branches 
        if interpret(sub.children[0], env):
            nodes.append(sub.children[1])
        for child in sub.children[2:]:
            if isinstance(child, ASelectWhenSubstitution):
                assert isinstance(child.children[0], Predicate)
                assert isinstance(child.children[1], Substitution)
                if interpret(child.children[0], env):
                    nodes.append(child.children[1])
            else:
                # else-branch
                assert isinstance(child, Substitution)
                assert child==sub.children[-1]
        # (2) test if possible branches are enabled
        some_branches_possible = not nodes == []
        if some_branches_possible:
            for i in range(len(nodes)):
                ex_generator = exec_substitution(nodes[i], env)
                for possible in ex_generator:
                    yield possible
        elif sub.hasElse=="True": 
            ex_generator = exec_substitution(sub.children[-1], env)
            for possible in ex_generator:
                yield possible
        else: # no branch enabled and no else branch present 
            yield False 
    elif isinstance(sub, ACaseSubstitution):
        assert isinstance(sub.children[0], Expression)
        elem = interpret(sub.children[0], env)
        all_cond_false = True
        for child in sub.children[1:1+sub.expNum]:
            assert isinstance(child, Expression)
            value = interpret(child, env)
            if elem == value:
                all_cond_false = False
                assert isinstance(sub.children[sub.expNum+1], Substitution)
                ex_generator = exec_substitution(sub.children[sub.expNum+1], env)
                for possible in ex_generator:
                    yield possible
        # EITHER E THEN S failed, check for OR-branches
        for child in sub.children[2+sub.expNum:]:
            if isinstance(child, ACaseOrSubstitution):
                for expNode in child.children[:child.expNum]:
                    assert isinstance(expNode, Expression)
                    value = interpret(expNode, env)
                    if elem == value:
                        all_cond_false = False
                        assert isinstance(child.children[-1], Substitution)
                        ex_generator = exec_substitution(child.children[-1], env)
                        for possible in ex_generator:
                            yield possible
            elif all_cond_false:
                assert isinstance(child, Substitution)
                assert child==sub.children[-1]
                assert sub.hasElse=="True"
                ex_generator = exec_substitution(child, env)
                for possible in ex_generator:
                    yield possible
        if all_cond_false and sub.hasElse=="False":
            yield True #invisible Else (page 95 manrefb)
    elif isinstance(sub, AVarSubstitution):
        nodes = []
        for idNode in sub.children[:-1]:
            assert isinstance(idNode, AIdentifierExpression)
            nodes.append(idNode)
        env.push_new_frame(nodes)
        ex_generator = exec_substitution(sub.children[-1], env)
        for possible in ex_generator: # TODO: read about python generators. It this push/pop necessary?
            env.pop_frame()
            yield possible
            env.push_new_frame(nodes)
        env.pop_frame()
    elif isinstance(sub, AAnySubstitution) or isinstance(sub, ALetSubstitution):
        nodes = []
        for idNode in sub.children[:sub.idNum]:
            assert isinstance(idNode, AIdentifierExpression)
            nodes.append(idNode)
        pred = sub.children[-2]
        assert isinstance(pred, Predicate)
        assert isinstance(sub.children[-1], Substitution)
        env.push_new_frame(nodes)
        gen = try_all_values(pred, env, nodes)
        for possible in gen:
            if possible:
                ex_generator = exec_substitution(sub.children[-1], env)
                for also_possible in ex_generator:
                    if also_possible:
                        env.pop_frame()
                        yield possible
                        env.push_new_frame(nodes)
        env.pop_frame()
        yield False
    elif isinstance(sub, AOpSubstitution):
        # TODO: parameters passed by copy (page 162), write test: side effect free?
        # set up
        boperation = env.lookup_operation(sub.idName)
        ret_types = boperation.return_types
        para_types = boperation.parameter_types
        values = []
        # get parameter values for call
        for i in range(len(para_types)):
            value = interpret(sub.children[i], env)
            values.append(value)
        op_node = boperation.ast
        # switch machine and set up parameters
        temp = env.current_mch
        env.current_mch = boperation.owner_machine
        id_nodes = [x[0] for x in para_types]       
        env.push_new_frame(id_nodes)
        for i in range(len(para_types)):
            name = para_types[i][0].idName
            env.set_value(name, values[i])
        assert isinstance(op_node, AOperation)
        ex_generator = exec_substitution(op_node.children[-1], env)
        for possible in ex_generator:
            # switch back machine
            env.pop_frame()
            env.current_mch = temp
            yield possible
            temp = env.current_mch
            env.current_mch = boperation.owner_machine
            env.push_new_frame(id_nodes)
            for i in range(len(para_types)):
                name = para_types[i][0].idName
                env.set_value(name, values[i])
        # switch back machine
        env.pop_frame()
        env.current_mch = temp
    elif isinstance(sub, AOpWithReturnSubstitution):
        # TODO: parameters passed by copy (page 162), write test: side effect free?
        # set up
        boperation = env.lookup_operation(sub.idName)
        ret_types = boperation.return_types
        para_types = boperation.parameter_types
        values = []
        # get parameter values for call
        for i in range(len(para_types)):
            parameter_node = sub.children[i+sub.return_Num]
            value = interpret(parameter_node, env)
            values.append(value)
        op_node = boperation.ast
        # switch machine and set up parameters
        temp = env.current_mch
        env.current_mch = boperation.owner_machine
        id_nodes = [x[0] for x in para_types + ret_types]
        env.push_new_frame(id_nodes)
        for i in range(len(para_types)):
            name = para_types[i][0].idName
            env.set_value(name, values[i])
        assert isinstance(op_node, AOperation)
        ex_generator = exec_substitution(op_node.children[-1], env)
        for possible in ex_generator:
            results = []
            for r in ret_types:
                name = r[0].idName
                value = env.get_value(name)
                results.append(value)
            # restore old frame after remembering return values
            # switch back machine
            env.pop_frame()
            env.current_mch = temp
            # write results to vars
            for i in range(sub.return_Num):
                ass_node = sub.children[i]
                value = results[i]
                name = ass_node.idName
                env.set_value(name, value)
            yield possible
            temp = env.current_mch
            env.current_mch = boperation.owner_machine
            env.push_new_frame(id_nodes)
            for i in range(len(para_types)):
                name = para_types[i][0].idName
                env.set_value(name, values[i])
        env.pop_frame()
        env.current_mch = temp


# a sequence substitution is only executable if every substitution it consist of is
# executable. If these substitutions are nondeterministic there maybe different "paths"
# of execution. Substituions may effect each other, so the order of execution musst be preserved
def exec_sequence_substitution(subst_list, env):
    ex_generator = exec_substitution(subst_list[0], env)
    if len(subst_list)==1:
        for possible in ex_generator:
            yield possible
    else:
        assert len(subst_list)>1
        for possible in ex_generator:
            if possible:
                bstate = env.state_space.get_state().clone() # save changes of recursion-levels above
                ex_seq_generator = exec_sequence_substitution(subst_list[1:], env)
                for others_possible in ex_seq_generator:
                    yield others_possible
                    env.state_space.undo() #revert
                    env.state_space.add_state(bstate) 
                    
                    
    
            
# same es exec_sequence_substitution (see above)
def exec_parallel_substitution(subst_list, env, ref_state, new_values):
    if len(subst_list)==0:
        yield True            
    else:
        assert len(subst_list)>0
        child = subst_list[0]
        # 1.1 setup: find changed vars (for later checks)
        # use ref_state (parallel substitutions musst not effect each other)
        assignd_ids = find_assignd_vars(child)
        assignd_ids = list(set(assignd_ids)) # remove double entries
        bstate = ref_state.clone()
        env.state_space.add_state(bstate)    # TODO: write clean interface          
        ex_generator = exec_substitution(child, env)
        for possible in ex_generator:
            # This path is executable. Maybe it changes the same vars but this is checked later
            if possible: 
                # 1.2. remember (possible) changes
                possible_new_values = {}
                for name in assignd_ids:
                    val = env.get_value(name)
                    possible_new_values[name] = val
                env.state_space.undo() #set to old state and drop other state
                # 1.3 test for changes
                pop_num = 0
                for name in assignd_ids:
                    new = possible_new_values[name]
                    old = env.get_value(name)
                    if not new==old: # change! - remember it
                        pop_num = pop_num + 1
                        new_values.append(tuple([name, new]))
                ex_pa_generator = exec_parallel_substitution(subst_list[1:], env, ref_state, new_values)
                for others_possible in ex_pa_generator:
                    yield others_possible
                # 1.4 revert. Different paths musst not effect each other
                bstate = ref_state.clone()
                env.state_space.add_state(bstate)
                for i in range(pop_num):
                    new_values.pop()
        env.state_space.undo()
                                         
                                            
# same es exec_sequence_substitution (see above)
def exec_while_substitution(condition, doSubst, invariant, variant, v_value, env):
    # always use the bstate of the last iteration 
    # without this copy the state of the last iteration can not restored 
    # after the first successful while-loop termination. 
    # This code would only be correct for non-deterministic while-loops
    bstate = env.state_space.get_state().clone()
    if not interpret(condition, env):
        yield True  #loop has already been entered. Not condition means success of "exec possible"
    else: 
        assert interpret(invariant, env)
        ex_generator = exec_substitution(doSubst, env)
        for possible in ex_generator:
            if possible:
                temp = interpret(variant, env)
                assert temp < v_value
                ex_while_generator = exec_while_substitution(condition, doSubst, invariant, variant, temp, env)
                for other_possible in ex_while_generator:
                     yield other_possible
                env.state_space.undo() # pop last bstate
                # restore the bstate of the last recursive call (python-level) 
                # i.e the last loop iteration (B-level)
                env.state_space.add_state(bstate) 
        yield False

                 
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




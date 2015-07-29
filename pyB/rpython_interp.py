from ast_nodes import *
from bexceptions import ValueNotInDomainException, INITNotPossibleException, SETUPNotPossibleException
from config import MAX_INIT, MAX_SET_UP, VERBOSE, SET_PARAMETER_NUM, USE_ANIMATION_HISTORY
#from constrainsolver import calc_possible_solutions
from enumeration import init_deffered_set, try_all_values #,get_image
from helpers import flatten, double_element_check, find_assignd_vars, print_ast, all_ids_known, find_var_nodes, conj_tree_to_conj_list
from pretty_printer import pretty_print
#from symbolic_sets import *
from symbolic_sets import SymbolicIntervalSet
from rpython_b_objmodel import W_Integer, W_Object, W_Boolean, W_None, W_Set_Element, frozenset
from typing import type_check_predicate, type_check_expression


#def parallel_caller(q, n, env):
#    q.put(interpret(n, env))

def eval_Invariant(root, env, mch):
    if mch.has_invariant_mc:
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
            print "\033[1m\033[91mWARNING\033[00m: Set Up from solution file was not complete! \nunset:%s" % unset_lst
        
        env.state_space.add_state(pre_set_up_state)
        # TODO: Parameter set up
        if VERBOSE:
            print "checking properties (with proB solutions) now.."
        if mch.has_properties_mc and not interpret(mch.aPropertiesMachineClause, env):
            raise SETUPNotPossibleException("\nError: Values from solution-file caused an PROPERTIES-violation (wrong predicates above).\nMIN_INT: %s MAX_INT: %s" % (env._min_int, env._max_int))            
        elif mch.has_properties_mc:
            print "Properties: True"
        env.state_space.undo()
        if VERBOSE:
            print "...no vialation found"
        return [pre_set_up_state] 
                   
    # 2. set up frame and B-state
    # The reference B-state: save the status before the solutions
    bstates = []
    """
    ref_bstate = env.state_space.get_state().clone()
    bstate = ref_bstate.clone()
    env.state_space.add_state(bstate) 
    
    # 3. search for (MAX_SET_UP-)solutions  
    generator = __set_up_constants_generator(root, env, mch)
    sol_num = 0
    for solution in generator:
        if solution:
            solution_bstate = env.state_space.get_state()
            if USE_ANIMATION_HISTORY:
                solution_bstate.add_prev_bstate(ref_bstate, "set up", parameter_values=None) 
            bstates.append(solution_bstate)
            env.state_space.revert(ref_bstate)
            env.init_sets_bmachnes_names = []  
            
            sol_num = sol_num + 1
            if sol_num==MAX_SET_UP: # change config.py
                break
    env.state_space.undo() # pop ref_bstate
    """
    return bstates



"""
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
    if mch.mch_name in env.set_up_bmachines_names:
        yield False
    else:
        env.set_up_bmachines_names.append(mch.mch_name)
        
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
                # Manual Page 110: If one of the CONCRETE_CONSTANTS or ABSTRACT_CONSTANTS clauses is present, then the PROPERTIES clause must be present.  
                #                  Visible Table: PROPERTIES-clause may read sets in SETS-clause
                if not mch.has_constants_mc and not mch.has_abstr_constants_mc:
                    # TODO:Properties can always be present. e.g PROPERTIES 1<2
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
        if not mch.has_constants_mc and not mch.has_abstr_constants_mc and mch.scalar_params==[] and mch.set_params==[]:
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
        if not mch.has_constraints_mc:
            names = [n.idName for n in mch.scalar_params]
            raise SETUPNotPossibleException("\nError: Missing ConstraintsMachineClause in %s! Can not set up: %s" % (mch.mch_name, names))
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
            w_element = W_Set_Element(e_name)
            elem_lst.append(w_element)      
        env.set_value(name, frozenset(elem_lst))
"""
                
# only(!) inits sets of all machines
# TODO: When the ProB-Solution-file also contains set-solutions, this
#       code will need a refactoring (Uses this solutions)
def init_sets(node, env, mch):
    # (1) avoid double set-init
    if mch.mch_name in env.init_sets_bmachnes_names:
        return 
    env.init_sets_bmachnes_names.append(mch.mch_name)
    mch_list = mch.included_mch + mch.extended_mch + mch.seen_mch + mch.used_mch
    # (2) init-sets of child-bmch
    for m in mch_list:
        init_sets(node, env, m)
    env.current_mch = mch
    # (3) init sets if present
    if mch.has_sets_mc: # St
        node = mch.aSetsMachineClause
        for child in node.children:
            if isinstance(child, AEnumeratedSetSet):
                elm_lst = []
                for elm in child.children:
                    assert isinstance(elm, AIdentifierExpression)
                    e_name = elm.idName
                    w_element = W_Set_Element(e_name)
                    #elm_lst.append(elm.idName)
                    elm_lst.append(w_element)
                    env.add_ids_to_frame([elm.idName])
                    # values of elements of enumerated sets are their names
                    env.set_value(elm.idName, W_None())
                    #env.set_value(elm.idName, elm.idName)
                env.add_ids_to_frame([child.idName])
                env.set_value(child.idName, frozenset(elm_lst))
            else:
                init_deffered_set(child, env) # done by enumeration.py


# yield True if successful B-state change
def check_properties(node, env, mch):
    if mch.has_properties_mc: # B
        # set up constants
        # if there are constants
        if mch.has_constants_mc or mch.has_abstr_constants_mc:
            const_nodes = []
            idNodes     = []
            # find all constants/sets which are still not set
            if mch.has_constants_mc:
                idNodes = mch.aConstantsMachineClause.children
            if mch.has_abstr_constants_mc:
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
                assert prop_result.value # if this is False: there musst be a Bug inside the interpreter
                yield prop_result.value 
            else:
                # if there are unset constants/sets enumerate them
                at_least_one_solution = False
                if VERBOSE:
                    print "enum. constants:", [n.idName for n in const_nodes]
                gen = try_all_values(mch.aPropertiesMachineClause.children[0], env, const_nodes)
                for prop_result in gen:
                    if prop_result.value:
                        at_least_one_solution = True
                        yield True
                # This generator is only called when the Constraints are True.
                # No Properties-solution means set_up fail
                if not at_least_one_solution:
                    print "Properties violation" 
                    print "\nFALSE Predicates:"
                    print_predicate_fail(env, mch.aPropertiesMachineClause.children[0])
                    raise SETUPNotPossibleException("\nError: Properties FALSE in machine: %s!" % (mch.mch_name))
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
            print "\033[1m\033[91mWARNING\033[00m: Init from solution file was not complete! unset:%s" % unset_lst
        
        env.state_space.add_state(pre_init_state)
        if mch.has_invariant_mc and not interpret(mch.aInvariantMachineClause, env):
            raise INITNotPossibleException("\nError: INITIALISATION unsuccessfully. Values from solution-file caused an INVARIANT-violation")
        env.state_space.undo()
        return [pre_init_state] 
               
    # 1. set up frames and state
    bstates = []
    ref_bstate = env.state_space.get_state()
    bstate = ref_bstate.clone()
    env.state_space.add_state(bstate)
     
    
    # 2. search for solutions  
    generator = __exec_initialisation_generator(root, env, mch)
    sol_num = 0
    for solution in generator:
        if solution:
            solution_bstate = env.state_space.get_state()
            if USE_ANIMATION_HISTORY:
                solution_bstate.add_prev_bstate(ref_bstate, "init", parameter_values=None) 
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
    if mch.mch_name in env.init_bmachines_names:
        yield False
    else:
        env.init_bmachines_names.append(mch.mch_name)
            
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
        if not mch.has_initialisation_mc:
            if mch.has_variables_mc and  mch.has_conc_variables_mc:
                raise INITNotPossibleException("\nError: Missing InitialisationMachineClause in %s!" % mch.mch_name)
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
                raise INITNotPossibleException("\n\033[1m\033[91mWARNING\033[00m: Problem while exec init. No init found/possible! in %s" % mch.mch_name)


# TODO: use solutions of child mch (seen, used mch)
def use_prob_solutions(env, idNames):
    #print "use_prob_solutions"
    for name in idNames:
        try:
            node = env.solutions[name]
            #print "setting",name #, " to:", pretty_print(node) 
            value = interpret(node, env)
            env.set_value(name, value)
        except KeyError:
            print "\n\033[1m\033[91mWARNING\033[00m: Reading solution file. Missing solution for %s" % name
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
    

# called before the evaluation of a predicate.
# If the pred. contains obvious equations like x=42 or S={1,2}, these equations ar
# used like assignments to avoid unnecessary enumeration
def learn_assigned_values(root, env):
    lst = []
    _learn_assigned_values(root, env, lst)
    return lst
    

# node is an "side-effect-free" AST (no assignments ':=' )
def _learn_assigned_values(root, env, lst):
    for node in root.children:
        if isinstance(node, AEqualPredicate):
            # (1) X='Expression' found
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
            var_name = idNode.idName
            # TODO: use idNodes-result to check if an eval. of expression node is possible
            # maybe this enum of node-classes becomes unnecessary
            
            # (2) only compute if 'Expression' is computable in O(1)
            # TODO: If the interpreter works in to symbolic mode, this is always the case
            # this code block musst be simplified when this is done
            if isinstance(expression_node, AIntegerExpression) or isinstance(expression_node, ASetExtensionExpression) or isinstance(expression_node, ASequenceExtensionExpression) or isinstance(expression_node, ABoolSetExpression) or isinstance(expression_node, ABooleanTrueExpression) or isinstance(expression_node, ABooleanFalseExpression) or isinstance(expression_node, AEmptySetExpression):
                try:
                    value = interpret(expression_node, env)
                    env.set_value(var_name, value)
                    lst.append(var_name)
                    continue
                except Exception as e:
                    #TODO: this case is not covered by any test
                    continue 
            # XXX: hack. remove when all nodes are symbolic
            elif isinstance(expression_node, ALambdaExpression) or isinstance(expression_node, AIntervalExpression) or isinstance(expression_node, ATransFunctionExpression) or isinstance(expression_node, ATransRelationExpression) or isinstance(expression_node, AQuantifiedUnionExpression) or isinstance(expression_node, AQuantifiedIntersectionExpression):# and idNodes==[]:
                try:
                    value = interpret(expression_node, env)
                    env.set_value(var_name, value)
                    lst.append(var_name)
                    continue
                except Exception as e:
                    print "Exception: while search of known id values:",e
                    continue 

        # df-search for equations 
        elif isinstance(node, AConjunctPredicate):
            _learn_assigned_values(node, env, lst)
      
# returns a W_Object. Wrapping is a interpreter task. Not a task of the obejcts or their methods     
def interpret(node, env):
# ********************************************
#
#        0. Interpretation-mode 
#
# ********************************************
    if isinstance(node, APredicateParseUnit): #TODO: move print to animation_clui
        #type_check_predicate(node, env)
        #idNodes = find_var_nodes(node) 
        #idNames = [n.idName for n in idNodes]
        #if idNames ==[]: # variable free predicate
        result = interpret(node.get(0), env)
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
    elif isinstance(node, AExpressionParseUnit): #TODO more
        #TODO: move print to animation_clui
        type_check_expression(node, env)
        idNodes = find_var_nodes(node) 
        idNames = [n.idName for n in idNodes]
        if idNames ==[]: # variable free expression
            result = interpret(node.children[0], env)
            return result
        else:
            return "\033[1m\033[91mWARNING\033[00m: Expressions with variables are not implemented now"
        """

# ********************************************
#
#        0. Clauses
#
# ********************************************
    elif isinstance(node, AConstraintsMachineClause):
        return interpret(node.get(-1), env)
        """
    elif isinstance(node, APropertiesMachineClause): #TODO: maybe predicate fail?
        lst = conj_tree_to_conj_list(node.children[0])
        result = True
        ok = 0
        fail = 0
        timeout = 0
        for n in lst:
            try:
                if PROPERTIES_TIMEOUT<=0:
                    value = interpret(n, env)
                else:
                    import multiprocessing   
                    que = multiprocessing.Queue()
                    p = multiprocessing.Process(target = parallel_caller, args = (que, n, env))
                    # TODO: safe and restore stack depth if corruption occurs by thread termination
                    #  length_dict = env.get_state().get_valuestack_depth_of_all_bmachines()
                    p.start()
                    p.join(PROPERTIES_TIMEOUT)
                    if not que.empty():
                        value = que.get()
                    else:
                        p.terminate()
                        print "\033[1m\033[94mTIMEOUT\033[00m: ("+pretty_print(n)+")"
                        # TODO: a timeout(cancel) can result in a missing stack pop (e.g. AGeneralProductExpression
                        timeout = timeout +1
                        continue
            except OverflowError:
                print "\033[1m\033[91mFAIL\033[00m: Enumeration overflow caused by: ("+pretty_print(n)+")"
                fail = fail +1
                continue
            if PRINT_SUB_PROPERTIES: # config.py
                string = str(value)
                if string=="False":
                   print '\033[1m\033[91m'+'False'+'\033[00m'+": "+pretty_print(n)
                   fail = fail +1
                elif string=="True":
                   print '\033[1m\033[92m'+'True'+'\033[00m'+": "+pretty_print(n)
                   ok = ok +1
                else: #XXX
                   print '\033[1m\033[94m'+string+'\033[00m'+": "+pretty_print(n)
            result = result and value
        if fail>0:
            print "\033[1m\033[91mproperties clause - total:%s ok:%s fail:%s timeout:%s\033[00m" % (len(lst), ok,fail,timeout)
        elif timeout>0:
            print "\033[1m\033[94mproperties clause - total:%s ok:%s fail:%s timeout:%s\033[00m" % (len(lst), ok,fail,timeout)
        else:
            print "\033[1m\033[92mproperties clause - total:%s ok:%s fail:%s timeout:%s\033[00m" % (len(lst),ok,fail,timeout)       
        return result
        """
    elif isinstance(node, AInvariantMachineClause):
        result = interpret(node.get(0), env)
        if not result.value:
            print "Invariant violation"
            print "\nFALSE Predicates:"
            print_predicate_fail(env, node.get(0))
            if env is not None: #Rpython typer help
                env.state_space.print_history()
        return result
        """
    elif isinstance(node, AAssertionsMachineClause):
       if ENABLE_ASSERTIONS: #config.py
            # TODO: add timeout
            ok = 0
            fail = 0
            print "checking assertions clause"
            for child in node.children:
                #print_ast(child)
                result = interpret(child, env)
                if result==True:
                    print '\033[1m\033[92m'+'True'+'\033[00m'+": "+pretty_print(child)
                    ok = ok +1
                else:
                    print '\033[1m\033[91m'+str(result)+'\033[00m'+": "+pretty_print(child)
                    fail = fail +1
            color = "92"      # green
            if fail>0:
                color = "91"  # red
            #elif timeout>0:
            #    color = "94"  # yellow
            print "\033[1m\033["+color+"massertions clause - total:%s ok:%s fail:%s \033[00m" % (len(node.children), ok,fail)
        """
        
# *********************
#
#        1. Predicates
#
# *********************
    elif isinstance(node, AConjunctPredicate):
        bexpr1 = interpret(node.get(0), env)
        bexpr2 = interpret(node.get(1), env)
        assert isinstance(bexpr1, W_Boolean) and isinstance(bexpr2, W_Boolean)
        w_bool = bexpr1.__and__(bexpr2)
        return bexpr1
        #return w_bool
    elif isinstance(node, ADisjunctPredicate):
        bexpr1 = interpret(node.get(0), env)
        bexpr2 = interpret(node.get(1), env)
        assert isinstance(bexpr1, W_Boolean) and isinstance(bexpr2, W_Boolean)
        w_bool = bexpr1.__or__(bexpr2)
        return w_bool
    elif isinstance(node, AImplicationPredicate):
        bexpr1 = interpret(node.get(0), env)
        bexpr2 = interpret(node.get(1), env)
        assert isinstance(bexpr1, W_Boolean) and isinstance(bexpr2, W_Boolean)
        if bexpr1.value and not bexpr2.value:
            w_bool = W_Boolean(False) # True=>False is False
            return w_bool
        else:
            w_bool = W_Boolean(True)
            return w_bool
    elif isinstance(node, AEquivalencePredicate):
        bexpr1 = interpret(node.get(0), env)
        bexpr2 = interpret(node.get(1), env)
        assert isinstance(bexpr1, W_Boolean) and isinstance(bexpr2, W_Boolean)
        w_bool = bexpr1.__eq__(bexpr2)
        return w_bool
    elif isinstance(node, ANegationPredicate):
        bexpr = interpret(node.get(0), env)
        assert isinstance(bexpr, W_Boolean)
        w_bool = bexpr.__not__()
        return w_bool
        """
    elif isinstance(node, AForallPredicate):
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
    elif isinstance(node, AExistsPredicate):
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
        # frozensets can only be compared to frozensets
        if isinstance(expr2, SymbolicSet) and isinstance(expr1, frozenset):
            expr2 = expr2.enumerate_all()
            return expr1 == expr2
        else:
            # else normal check, also symbolic (implemented by symbol classes)
            return expr1 == expr2
    elif isinstance(node, ANotEqualPredicate):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        # TODO: handle symbolic sets
        return expr1 != expr2
        """
 
        
# **************
#
#       2. Sets
#
# **************        
        """
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
        return SymbolicUnionSet(aSet1, aSet2, env, interpret)
    elif isinstance(node, AIntersectionExpression):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
        return SymbolicIntersectionSet(aSet1, aSet2, env, interpret)
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
        return SymbolicPowerSet(aSet, env, interpret)
        #res = powerset(aSet)
        #powerlist = list(res)
        #lst = [frozenset(e) for e in powerlist]
        #return frozenset(lst)
    elif isinstance(node, APow1SubsetExpression):
        aSet = interpret(node.children[0], env)
        return SymbolicPower1Set(aSet, env, interpret)
        #res = powerset(aSet)
        #powerlist = list(res)
        #lst = [frozenset(e) for e in powerlist]
        #lst.remove(frozenset([]))
        #return frozenset(lst)
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
        #result = frozenset([])
        # new scope
        varList = node.children[:-2]
        env.push_new_frame(varList)
        pred = node.children[-2]
        expr = node.children[-1]
        #domain_generator = calc_possible_solutions(pred, env, varList, interpret)
        #for entry in domain_generator:
        #    for name in [x.idName for x in varList]:
        #        value = entry[name]
        #        env.set_value(name, value)
        #    try:
        #        if interpret(pred, env):  # test (|= ior)
        #            aSet = interpret(expr, env)
        #            if isinstance(aSet, SymbolicSet):
        #                aSet = aSet.enumerate_all() 
        #            result |= aSet
        #    except ValueNotInDomainException:
        #        continue
        #env.pop_frame()
        #return result
        return SymbolicQuantifiedUnion(varList, pred, expr, node, env, interpret, calc_possible_solutions)
    elif isinstance(node, AQuantifiedIntersectionExpression):  
        #result = frozenset([])
        # new scope
        varList = node.children[:-2]
        env.push_new_frame(varList)
        pred = node.children[-2]
        expr = node.children[-1]
        #domain_generator = calc_possible_solutions(pred, env, varList, interpret)
        #for entry in domain_generator:
        #    for name in [x.idName for x in varList]:
        #        value = entry[name]
        #        env.set_value(name, value)
        #    try:
        #        if interpret(pred, env):  # test
        #            # intersection with empty set is always empty: two cases are needed
        #            if result==frozenset([]): 
        #                result = interpret(expr, env)
        #                if isinstance(result, SymbolicSet):
        #                    result = result.enumerate_all()   
        #            else:
        #                aSet = interpret(expr, env)
        #                if isinstance(aSet, SymbolicSet):
        #                    aSet = aSet.enumerate_all()       
        #                result &= aSet
        #    except ValueNotInDomainException:
        #        continue
        #env.pop_frame()
        #return result
        return SymbolicQuantifiedIntersection(varList, pred, expr, node, env, interpret, calc_possible_solutions)
        """
    
# *************************
#
#       2.1 Set predicates
#
# ************************* 
    
    elif isinstance(node, AMemberPredicate):
        #print pretty_print(node)
        #if all_ids_known(node, env): #TODO: check over-approximation. All ids need to be bound?
        #    elm = interpret(node.children[0], env)
        #    result = quick_member_eval(node.children[1], env, elm)
        #    return result
        elm = interpret(node.get(0), env)
        aSet = interpret(node.get(1), env)
        w_bool = W_Boolean(aSet.__contains__(elm))
        return w_bool
    elif isinstance(node, ANotMemberPredicate):
        #if all_ids_known(node, env): #TODO: check over-approximation. All ids need to be bound?
        #    elm = interpret(node.children[0], env)
        #    result = quick_member_eval(node.children[1], env, elm)
        #    return not result
        elm = interpret(node.get(0), env)
        aSet = interpret(node.get(1), env)
        w_bool = W_Boolean(aSet.__contains__(elm)).__not__()
        return w_bool
        
        """
    elif isinstance(node, ASubsetPredicate):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
        if isinstance(aSet2, SymbolicSet):
            return aSet2.issuperset(aSet1)
        return aSet1.issubset(aSet2)
    elif isinstance(node, ANotSubsetPredicate):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
        return not aSet1.issubset(aSet2)
    elif isinstance(node, ASubsetStrictPredicate):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
        return aSet1.issubset(aSet2) and aSet1 != aSet2
    elif isinstance(node, ANotSubsetStrictPredicate):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
        return not (aSet1.issubset(aSet2) and aSet1 != aSet2)
        """

# *****************
#
#       3. Numbers
#
# *****************
        """
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
        """
    elif isinstance(node, AAddExpression):
        expr1 = interpret(node.get(0), env)
        expr2 = interpret(node.get(1), env)
        integer = expr1.__add__(expr2)
        return W_Integer(integer)
    elif isinstance(node, AMinusOrSetSubtractExpression): #TODO: cart
        expr1 = interpret(node.get(0), env)
        expr2 = interpret(node.get(1), env)
        integer = expr1.__sub__(expr2)
        return W_Integer(integer)
    elif isinstance(node, AMultOrCartExpression):
        expr1 = interpret(node.get(0), env)
        expr2 = interpret(node.get(1), env)
        integer = expr1.__mul__(expr2)
        return W_Integer(integer)
    elif isinstance(node, ADivExpression):
        expr1 = interpret(node.get(0), env)
        expr2 = interpret(node.get(1), env)
        integer = expr1.__floordiv__(expr2)
        return W_Integer(integer)
    elif isinstance(node, AModuloExpression):
        expr1 = interpret(node.get(0), env)
        expr2 = interpret(node.get(1), env)
        assert expr2.value > 0
        integer = expr1.__mod__(expr2)
        return W_Integer(integer)
    elif isinstance(node, APowerOfExpression):
        basis = interpret(node.get(0), env)
        exp = interpret(node.get(1), env)
        # not RPython: result = basis ** exp
        assert exp.value >=0
        result = 1
        for i in range(exp.value):
            result = result *basis.value
        return W_Integer(result)
        
    elif isinstance(node, AIntervalExpression):
        left = interpret(node.get(0), env)
        right = interpret(node.get(1), env)
        L = []
        for i in range(right.value+1):
            value = W_Integer(i+left.value)
            L.append(value)
        return frozenset(L)
        #return SymbolicIntervalSet(left, right, env, interpret)
        
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
        """     

# ***************************
#
#       3.1 Number predicates
#
# ***************************
    elif isinstance(node, AGreaterPredicate):
        expr1 = interpret(node.get(0), env)
        expr2 = interpret(node.get(1), env)
        return W_Boolean(expr1.__gt__(expr2))
    elif isinstance(node, ALessPredicate):
        expr1 = interpret(node.get(0), env)
        expr2 = interpret(node.get(1), env)
        return W_Boolean(expr1.__lt__(expr2))
    elif isinstance(node, AGreaterEqualPredicate):
        expr1 = interpret(node.get(0), env)
        expr2 = interpret(node.get(1), env)
        return W_Boolean(expr1.__ge__(expr2))
    elif isinstance(node, ALessEqualPredicate):
        expr1 = interpret(node.get(0), env)
        expr2 = interpret(node.get(1), env)
        return W_Boolean(expr1.__le__(expr2))
    

# ******************
#
#       4. Relations
#
# ******************
#TODO
    elif isinstance(node, AIntegerExpression):
        # TODO: add flag in config.py to enable switch to long integer here
        return W_Integer(node.intValue)
    elif isinstance(node, AIdentifierExpression):
        assert env is not None
        value = env.get_value(node.idName)
        assert isinstance(value, W_Object)
        return value
    else:
        raise Exception("\nError: Unknown/unimplemented node inside interpreter: %s",node)
        return W_None() # RPython: Avoid return of python None


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
            assert isinstance(value, W_Object)
            values.append(value)
        for i in range(int(sub.lhs_size)):
            lhs_node = sub.children[i]            
            # BUG if the expression on the rhs has a side-effect
            assert i>=0 and i<len(values)
            value = values[i]
            # case (1) lhs: no function
            if isinstance(lhs_node, AIdentifierExpression):
                used_ids.append(lhs_node.idName)
                env.set_value(lhs_node.idName, value)
            # TODO: implement call method on frozensets before adding this code
            """
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
            """
        while not used_ids==[]:
            name = used_ids.pop()
            if name in used_ids:
                raise Exception("\nError: %s modified twice in multiple assign-substitution!" % name)
        yield True # assign(s) was/were  successful 
    elif isinstance(sub, ABlockSubstitution):
        ex_generator = exec_substitution(sub.children[-1], env)
        for possible in ex_generator:
            yield possible
    elif isinstance(sub, APreconditionSubstitution):
        assert isinstance(sub.children[0], Predicate)
        assert isinstance(sub.children[1], Substitution)
        condition = interpret(sub.children[0], env)
        #print condition, node.children[0]
        if condition.value:
            ex_generator = exec_substitution(sub.children[1], env)
            for possible in ex_generator:
                yield possible
        else:
            yield False
     
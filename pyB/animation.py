# -*- coding: utf-8 -*-
# module-description: 
# animation calculations
from config import MAX_OP_SOLUTIONS, MAX_SELECT_BRANCHES, PRINT_WARNINGS, USE_RPYTHON_CODE, BMACHINE_SEARCH_DIR, BFILE_EXTENSION, USE_ANIMATION_HISTORY
from enumeration import try_all_values
from ast_nodes import *
from constrainsolver import calc_possible_solutions
from bexceptions import ValueNotInDomainException

if USE_RPYTHON_CODE:
    from rpython_interp import exec_substitution, interpret 
    from rpython_b_objmodel import frozenset
else:
    from interp import exec_substitution, interpret

    


# Wrapper object. Replaces list of dif. typed items.
# only returned by calc_next_states
class Executed_Operation():
    def __init__(self, opName, parameter_names, parameter_values, return_names, return_values, bstate):
        self.opName = opName
        self.parameter_names  = parameter_names
        self.parameter_values = parameter_values
        self.return_names  = return_names
        self.return_values = return_values 
        self.bstate        = bstate
    
    
# returns list of (op_name, parameter_value_list, return_value_list, bstate) of all states
# TODO:(#ISSUE 6) implement filter MAX_NEXT_EVENTS
#
# Because the constraint-solver can only find approximations of correct parameters
# every solution generated by calc_possible_solutions musst be tested by the interpreter
# before thes new state can be added to the result list
#
# generator-methods work by side-effects which change the top-of-stack state (current state)
# of the state-space. To assure independent state calculation of 
# 1. operations
# 2. operations with different parameters (domain_generator)
# 3. and operations with different parameters and nondeterministic execution-paths (domain_generator and ex_sub_generator)
# up to three pushs and their corresponding pops are necessary: 
# in some cases only if there are "more solutions"
def calc_next_states(env, bmachine):
    result = []
    if bmachine.has_operations_mc:
        # WARNING: assumes no vars/sets with the same name in two b machines
        # TODO:(#ISSUE 9) write a method to check this assumption 
        #operations = env.all_operation_asts 
        operations = env.get_all_visible_op_asts()
        #print "empty?:", operations
        for op in operations:
            assert isinstance(op, AOperation)         
            # (1) add helper state to avoid bstate-side-effects i.e. operations-state calculations
            #     that effect each other (dropped at the end of each iteration) 
            ref_bstate = env.state_space.get_state().clone()
            env.state_space.add_state(ref_bstate)  
            
            # (2) find parameter and return_val idNodes and add them to the frame of the helper state        
            #parameter_idNodes  = op.children[op.return_Num : op.return_Num+op.parameter_Num]
            #return_val_idNodes = op.children[0 : op.return_Num]
            parameter_idNodes = []
            for i in range(op.parameter_Num):
                p_node = op.children[op.return_Num+i]
                parameter_idNodes.append(p_node)
            return_val_idNodes = []
            for i in range(op.return_Num):
                r_node = op.children[i]
                return_val_idNodes.append(r_node)
                
            # check node-lists
            # TODO:(#ISSUE 14) move this check into the parsing-phase
            for idNode in parameter_idNodes + return_val_idNodes:
                assert isinstance(idNode, AIdentifierExpression) # AST corruption  
            env.add_ids_to_frame([n.idName for n in parameter_idNodes + return_val_idNodes])
            env.push_new_frame(parameter_idNodes + return_val_idNodes)          
            #print "opname: \t", op.opName # DEBUG

            substitution = op.children[-1]
            assert isinstance(substitution, Substitution)
            op_has_no_parameters = parameter_idNodes==[]   
            # (3.1) case one: no parameters
            if op_has_no_parameters:
                ex_sub_generator = exec_substitution(substitution, env)
                bstate = ref_bstate.clone() # new state for first exec-path (nondeterminism)
                env.state_space.add_state(bstate) 
                for possible in ex_sub_generator:
                    if possible:
                        return_names, return_values        = _get_value_list(env, return_val_idNodes)
                        env.pop_frame()
                        bstate = env.state_space.get_state()  # TODO:(#ISSUE 15)  remove?
                        if USE_ANIMATION_HISTORY:
                            bstate.add_prev_bstate(ref_bstate, op.opName, parameter_values=None)   
                        exec_op = Executed_Operation(op.opName, [], [], return_names, return_values, bstate)
                        result.append(exec_op)     
                        #result.append([op.opName, [], return_value_list, bstate])
                    env.state_space.undo() # pop last bstate
                    bstate = ref_bstate.clone() # new state for next exec-path (nondeterminism)
                    env.state_space.add_state(bstate)
                env.state_space.undo()  # pop bstate (all paths found)
            # (3.2) case two: find parameter values
            else:
                # This code uses the constraint solver and the top_level predicate of this op to guess 
                # parameter values. Of course this guess can produce false values but it will 
                # never drop possible values
                # (3.2.1) find top_level predicate
                domain_generator = None
                if isinstance(substitution, APreconditionSubstitution):
                    predicate = substitution.children[0]
                    # TODO: RYPTHON AssertionError domain_generator_1
                    domain_generator = calc_possible_solutions(predicate, env, parameter_idNodes)
                # TODO:(#ISSUE 13) maybe more guesses elif...
                else: # no guess possible, try all values (third-arg None cause an enum of all values)
                    domain_generator = calc_possible_solutions(None, env, parameter_idNodes)
                #import types
                #assert isinstance(domain_generator, types.GeneratorType)
                
                # Try solutions
                for solution in domain_generator:
                    try:
                        # use values of solution (iterations musst not affect each other):
                        bstate = env.state_space.get_state().clone()
                        env.state_space.add_state(bstate)  
                        _set_parameter_values(env, parameter_idNodes, solution)
                        # try to exec
                        ex_sub_generator = exec_substitution(substitution, env)
                        bstate2 = bstate.clone()
                        env.state_space.add_state(bstate2) 
                        for possible in ex_sub_generator:
                            if possible:
                                # Solution found!                          
                                # (3.2.2) get parameter and return-value solutions
                                parameter_names, parameter_values  = _get_value_list(env, parameter_idNodes)
                                return_names, return_values        = _get_value_list(env, return_val_idNodes)
                                #print parameter_value_list
                                env.pop_frame() # pop on the cloned state
                                bstate2 = env.state_space.get_state().clone() #TODO:(#ISSUE 15) remove?
                                if USE_ANIMATION_HISTORY:
                                    bstate2.add_prev_bstate(bstate, op.opName, parameter_values) 
                                exec_op = Executed_Operation(op.opName, parameter_names, parameter_values, return_names, return_values, bstate2)
                                result.append(exec_op)
                                #result.append([op.opName, parameter_value_list, return_value_list, bstate2])
                            env.state_space.undo() # pop last bstate2
                            bstate2 = bstate.clone()
                            env.state_space.add_state(bstate2)
                        env.state_space.undo() #pop last bstate2
                        env.state_space.undo() #pop bstate (all paths for this solution/parameters found)  
                    except ValueNotInDomainException: #TODO: modify enumerator not to generate that "solutions" at all
                        env.state_space.undo() #pop bstate (all paths for this solution/parameters found) 
            env.state_space.undo() # pop ref_bstate (all states for this operation found)
    if result==[] and PRINT_WARNINGS:
        print "\033[1m\033[91mWARNING\033[00m: Deadlock found!"
    # alphabetic sort of results
    result = sort_ops(result)
    #result = sorted(result, key = lambda state: state[0])
    return result

# FIXME: runtime O(n**2) 
def sort_ops(lst):
    result = []
    while(len(lst)>0):
        e = lst.pop()
        index = 0
        for i in range(len(result)):
            if e.opName<=result[i].opName:
                 break
            index = index + 1
        result.insert(index, e)
    return result

# - private method -
# changes state. Set parameter values of this operation to the solution   
def _set_parameter_values(env, parameter_idNodes, solution):
    for name in [x.idName for x in parameter_idNodes]:
        value = solution[name]
        env.set_value(name, value)

# TODO: rpython Union error in append
# - private method -
# helper method, returns list of (name, value) pairs
def _get_value_list(env, idNode_list):
    value_list = []
    name_list  = []
    for name in [x.idName for x in idNode_list]:
        value = env.get_value(name)
        name_list.append(name)
        value_list.append(value)
    return name_list, value_list


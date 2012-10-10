# -*- coding: utf-8 -*-
from config import max_op_solutions
from enumeration import try_all_values
from ast_nodes import *
from constrainsolver import calc_possible_solutions
from bexceptions import ValueNotInDomainException

# returns (op, parameter_list, return_values, bstate)
# TODO?: returnvalues
def calc_succ_states(env, bmachine):
    result = []
    if bmachine.aOperationsMachineClause:
        # WARNING: assumes no vars/set with the same name in two mch
        save_state = env.bstate
        operations = bmachine.aOperationsMachineClause.children + bmachine.promoted_ops + bmachine.seen_ops + bmachine.used_ops + bmachine.extended_ops
        for op in operations:
            # (1) create new Environment, parameter_list and return_values
            import copy
            env.bstate = copy.deepcopy(save_state)
            parameter_list = []
            return_values = []

            # (2) find parameter names and add them to the frame
            idNodes = get_para_nodes(op)
            rids =get_return_names(op)
            env.bstate.add_ids_to_frame([n.idName for n in idNodes])
            env.bstate.add_ids_to_frame(rids)
            #print "opname: \t", op.opName

            # (3) Select Operation Type
            assert isinstance(op, AOperation)
            substitution = op.children[-1]
            assert isinstance(substitution, Substitution)
            if isinstance(substitution, APreconditionSubstitution):
                predicate = substitution.children[0]
                assert isinstance(predicate, Predicate)
                if not idNodes==[]: # (3.1a) enumerate operation-parameters
                    k = 0 # number of found solutions 
                    save_next_state = env.bstate
                    domain_generator = calc_possible_solutions(env, idNodes, predicate)
                    for entry in domain_generator:
                        if k==max_op_solutions:
                            break
                        try:
                            # gen a new state for every execution
                            env.bstate = copy.deepcopy(save_next_state)
                            # use values of solution-candidate
                            for name in [x.idName for x in idNodes]:
                                value = entry[name]
                                env.bstate.set_value(name, value)
                            if bmachine.interpreter_method(predicate, env):  # test
                                # Solution found!
                                parameter_list = []
                                # (3.2) add parameter-solutions
                                for n in idNodes:
                                    i = n.idName
                                    parameter_list.append(tuple([i, env.bstate.get_value(i)]))
                                # (3.3) calc next state and add to result list
                                bmachine.interpreter_method(substitution.children[1], env)
                                return_values = add_return_values(env, rids)
                                result.append([op, parameter_list, return_values, env.bstate])
                                k = k +1
                            env.bstate = save_next_state # generator musst use correct state
                        except ValueNotInDomainException:
                            env.bstate = save_next_state # generator musst use correct state
                    env.bstate = save_next_state
                else: # (3.1b) no operation-parameters: no enumeration 
                    if bmachine.interpreter_method(predicate, env):
                        bmachine.interpreter_method(substitution.children[-1], env)
                        return_values = add_return_values(env, rids)
                        result.append([op, parameter_list, return_values, env.bstate])
            elif isinstance(substitution, ABlockSubstitution) or isinstance(substitution, AAssignSubstitution):
                bmachine.interpreter_method(op.children[-1], env)
                return_values = add_return_values(env, rids)
                result.append([op, parameter_list, return_values, env.bstate]) # no condition
            elif isinstance(substitution, AIfSubstitution):
                # TODO if there is no else block, check condition
                bmachine.interpreter_method(substitution, env)
                return_values = add_return_values(env, rids)
                result.append([op, parameter_list, return_values, env.bstate])
            elif isinstance(substitution, ASelectSubstitution):
                assert isinstance(substitution.children[0], Predicate)
                assert isinstance(substitution.children[1], Substitution)
                k = 0
                index = 0   
                predicate = substitution.children[index]
                subs = substitution.children[index+1]    
                                  
                if not idNodes==[]: 
                    # (3.1) enumerate parameters
                    while k<max_op_solutions:
                        gen = try_all_values(predicate, env, idNodes)
                        # CHECK: (3.2.1) test if there are solutions for this pred
                        save_next_state = env.bstate
                        while gen.next() and k<max_op_solutions:
                            # Solution found:
                            # gen a new state for every execution
                            env.bstate = copy.deepcopy(save_next_state)
                            parameter_list = []
                            # (3.2.2) add parameter-solutions
                            for n in idNodes:
                                i = n.idName
                                parameter_list.append(tuple([i, env.bstate.get_value(i)]))
                            # (3.2.3) calc next state
                            bmachine.interpreter_method(subs, env)
                            return_values = add_return_values(env, rids)
                            result.append([op, parameter_list, return_values, env.bstate])
                            k = k +1
                        
                        env.bstate = save_next_state     
                        # SELECT: (3.3) select next predicate if possible
                        index = index + 1
                        if index+1<len(substitution.children) and isinstance(substitution.children[index+2], ASelectWhenSubstitution):
                            swsub = substitution.children[index]
                            assert isinstance(swsub.children[0], Predicate)
                            assert isinstance(swsub.children[1], Substitution)
                            predicate = swsub.children[0]
                            subs = swsub.children[1]
                        elif substitution.hasElse=="True":
                            bmachine.interpreter_method(substitution.children[-1], env)
                            return_values = add_return_values(env, rids)
                            result.append([op, parameter_list, return_values, env.bstate])
                            break
                        else:
                            # checked everything: no more solutions and no else block
                            break
                else:  # no operation-parameters: no enumeration 
                    save_next_state = env.bstate
                    while k<max_op_solutions:
                        env.bstate = copy.deepcopy(save_next_state)
                        # CHECK: is the pred in this state true?
                        if bmachine.interpreter_method(predicate, env):
                            bmachine.interpreter_method(subs, env)
                            return_values = add_return_values(env, rids)
                            result.append([op, parameter_list, return_values, env.bstate])
                            k = k+1
                        # SELECT: select next pred
                        index = index +1
                        child = substitution.children[index]
                        if isinstance(child, ASelectWhenSubstitution):
                            assert isinstance(child.children[0], Predicate)
                            assert isinstance(child.children[1], Substitution)
                            predicate = child.children[index]
                            subs = child.children[index+1] 
                        elif substitution.hasElse=="True":                      
                            assert isinstance(child, Substitution)
                            assert child==substitution.children[-1]
                            bmachine.interpreter_method(substitution.children[-1], env)
                            return_values = add_return_values(env, rids)
                            result.append([op, parameter_list, return_values, env.bstate])
                            break
                        else:
                            # checked everything: no more solutions and no else block
                            break
                    env.bstate = save_next_state            
            else:
                raise Exception("ERROR: Optype not implemented:", op.children[-1]) 
        env.bstate = save_state
    return result


def exec_op(env,  op_and_state_list, number):
    if len(op_and_state_list)>number:
        op = op_and_state_list[number][0]
        state = op_and_state_list[number][3]
        state.last_state = env.bstate
        return state


def get_para_nodes(op):
    nodes = []
    for i in range(op.return_Num, op.return_Num+op.parameter_Num):
        assert isinstance(op.children[i], AIdentifierExpression)
        nodes.append(op.children[i])
    return nodes


def get_return_names(op):
    names = []
    for i in range(op.return_Num):
        assert isinstance(op.children[i], AIdentifierExpression)
        names.append(op.children[i].idName)
    return names


def add_return_values(env, rids):
    return_values = []
    if not rids == []:
        for i in rids:
            return_values.append(tuple([i, env.bstate.get_value(i)]))
    return return_values
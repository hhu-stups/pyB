# -*- coding: utf-8 -*-
from config import max_op_solutions
from enumeration import try_all_values
from ast_nodes import *

# returns (op, parameter_list, return_values, next_state)
# TODO: returnvalues
def calc_succ_states(current_state, bmachine):
    result = []
    if bmachine.aOperationsMachineClause:
        # assumes no vars/set with the same name in two mch
        operations = bmachine.aOperationsMachineClause.children + bmachine.promoted_ops + bmachine.seen_ops + bmachine.used_ops + bmachine.extended_ops
        for op in operations:
            # (1) create new Environment, parameter_list and return_values
            import copy
            next_state = copy.deepcopy(current_state)
            parameter_list = []
            return_values = []

            # (2) find parameter names
            idNodes = get_para_nodes(op)
            rids =get_return_names(op)
            next_state.add_ids_to_frame([n.idName for n in idNodes])
            next_state.add_ids_to_frame(rids)
            #print "opname: \t", op.opName

            # (3) Select Operation Type
            assert isinstance(op, AOperation)
            substitution = op.children[-1]
            assert isinstance(substitution, Substitution)
            if isinstance(substitution, APreconditionSubstitution):
                # (3.1) enumerate parameters
                predicate = substitution.children[0]
                assert isinstance(predicate, Predicate)
                if not idNodes==[]:
                    gen = try_all_values(predicate, next_state, idNodes)
                    k = 0
                    while gen.next() and k<max_op_solutions:
                        # gen a new state for every execution
                        temp_state = copy.deepcopy(next_state)
                        parameter_list = []
                        # (3.2) add parameter-solutions
                        for n in idNodes:
                            i = n.idName
                            parameter_list.append(tuple([i, temp_state.get_value(i)]))
                        # (3.3) calc next state
                        bmachine.interpreter_method(substitution.children[1], temp_state)
                        return_values = add_return_values(temp_state, rids)
                        result.append([op, parameter_list, return_values, temp_state])
                        k = k +1 
                # no parameter
                else:
                    if bmachine.interpreter_method(predicate, next_state):
                        bmachine.interpreter_method(substitution.children[-1], next_state)
                        return_values = add_return_values(next_state, rids)
                        result.append([op, parameter_list, return_values, next_state])
            elif isinstance(substitution, ABlockSubstitution) or isinstance(substitution, AAssignSubstitution):
                bmachine.interpreter_method(op.children[-1], next_state)
                return_values = add_return_values(next_state, rids)
                result.append([op, parameter_list, return_values, next_state]) # no condition
            elif isinstance(substitution, AIfSubstitution):
                # TODO if there is no else block, check condition
                bmachine.interpreter_method(substitution, next_state)
                return_values = add_return_values(next_state, rids)
                result.append([op, parameter_list, return_values, next_state])
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
                        gen = try_all_values(predicate, next_state, idNodes)
                        # CHECK: (3.2.1) test if there are solutions for this pred
                        while gen.next() and k<max_op_solutions:
                            # Solution found:
                            # gen a new state for every execution
                            temp_state = copy.deepcopy(next_state)
                            parameter_list = []
                            # (3.2.2) add parameter-solutions
                            for n in idNodes:
                                i = n.idName
                                parameter_list.append(tuple([i, temp_state.get_value(i)]))
                            # (3.2.3) calc next state
                            bmachine.interpreter_method(subs, temp_state)
                            return_values = add_return_values(temp_state, rids)
                            result.append([op, parameter_list, return_values, temp_state])
                            k = k +1
                             
                        # SELECT: (3.3) select next predicate if possible
                        index = index + 1
                        if index+1<len(substitution.children) and isinstance(substitution.children[index+2], ASelectWhenSubstitution):
                            swsub = substitution.children[index]
                            assert isinstance(swsub.children[0], Predicate)
                            assert isinstance(swsub.children[1], Substitution)
                            predicate = swsub.children[0]
                            subs = swsub.children[1]
                        elif substitution.hasElse=="True":
                            bmachine.interpreter_method(substitution.children[-1], next_state)
                            return_values = add_return_values(next_state, rids)
                            result.append([op, parameter_list, return_values, next_state])
                            break
                        else:
                            # checked everything: no more solutions and no else block
                            break
                else:
                    # no parameters: no enumeration
                    while k<max_op_solutions:
                        temp_state = copy.deepcopy(next_state)
                        # CHECK: is the pred in this state true?
                        if bmachine.interpreter_method(predicate, temp_state):
                            bmachine.interpreter_method(subs, temp_state)
                            return_values = add_return_values(temp_state, rids)
                            result.append([op, parameter_list, return_values, temp_state])
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
                            bmachine.interpreter_method(substitution.children[-1], temp_state)
                            return_values = add_return_values(temp_state, rids)
                            result.append([op, parameter_list, return_values, temp_state])
                            break
                        else:
                            # checked everything: no more solutions and no else block
                            break            
            else:
                raise Exception("ERROR: Optype not implemented:", op.children[-1]) 
    return result


def exec_op(current_state,  op_and_state_list, number):
    if len(op_and_state_list)>number:
        op = op_and_state_list[number][0]
        state = op_and_state_list[number][3]
        state.last_env = current_state
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
            return_values.append(tuple([i, env.get_value(i)]))
    return return_values
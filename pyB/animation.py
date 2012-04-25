# -*- coding: utf-8 -*-
from config import max_op_solutions
from enumeration import try_all_values
from ast_nodes import *

# returns (op, parameter_list, return_values, next_state)
# TODO: returnvalues
def calc_succ_states(current_state, bmachine):
    result = []
    if bmachine.aOperationsMachineClause:
        for op in bmachine.aOperationsMachineClause.children:
            # (1) create new Environment, parameter_list and return_values
            import copy
            next_state = copy.deepcopy(current_state)
            parameter_list = []
            return_values = []

            # (2) find parameter names
            ids = get_para_names(op)
            rids =get_return_names(op)
            next_state.add_ids_to_frame(ids)
            next_state.add_ids_to_frame(rids)

            # (3) Select Operation Type
            assert isinstance(op, AOperation)
            if isinstance(op.children[-1], APreconditionSubstitution):
                predicate = op.children[-1].children[0]
                assert isinstance(predicate, Predicate)

                # (3.1) enumerate parameters
                if not ids==[]:
                    gen = try_all_values(predicate, next_state, ids)
                    k = 0
                    while gen.next() and k<max_op_solutions:
                        # gen a new state for every execution
                        temp_state = copy.deepcopy(next_state)
                        parameter_list = []
                        # (3.2) add parameter-solutions
                        for i in ids:
                            parameter_list.append(tuple([i, temp_state.get_value(i)]))
                        # (3.3) calc next state
                        bmachine.interpreter_method(op.children[-1].children[1], temp_state)
                        return_values = add_return_values(temp_state, rids)
                        result.append([op, parameter_list, return_values, temp_state])
                        k = k +1 
                # no parameter
                else:
                    bmachine.interpreter_method(op.children[-1], next_state)
                    return_values = add_return_values(next_state, rids)
                    result.append([op, parameter_list, return_values, next_state])
            elif isinstance(op.children[-1], ABlockSubstitution):
                bmachine.interpreter_method(op.children[-1], next_state)
                return_values = add_return_values(next_state, rids)
                result.append([op, parameter_list, return_values, next_state]) # no condition
            elif isinstance(op.children[-1], AIfSubstitution):
                # TODO if there is no else block, check condition
                bmachine.interpreter_method(op.children[-1], next_state)
                return_values = add_return_values(next_state, rids)
                result.append([op, parameter_list, return_values, next_state])
            else:
                raise Exception("ERROR: Optype not implemented:", op.children[-1])
    return result


def exec_op(current_state,  op_and_state_list, number):
    if len(op_and_state_list)>number:
        op = op_and_state_list[number][0]
        state = op_and_state_list[number][3]
        state.last_env = current_state
        return state


def get_para_names(op):
    names = []
    for i in range(op.return_Num, op.parameter_Num):
        assert isinstance(op.children[i], AIdentifierExpression)
        names.append(op.children[i].idName)
    return names


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
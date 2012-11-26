# -*- coding: utf-8 -*-
from config import max_op_solutions, MAX_SELECT_BRANCHES
from enumeration import try_all_values
from ast_nodes import *
from constrainsolver import calc_possible_solutions
from bexceptions import ValueNotInDomainException
from helpers import select_ast_to_list

# returns list of (op, parameter_list, substitution_body)
# Because the constraint-solver only can find approximations of correct parameters
# every solution generated by calc_possible_solutions musst be tested before the
# substitution can be added to the result list
def calc_possible_operations(env, bmachine):
    result = []
    if bmachine.aOperationsMachineClause:
        # WARNING: assumes no vars/set with the same name in two mch
        operations = bmachine.aOperationsMachineClause.children + bmachine.promoted_ops + bmachine.seen_ops + bmachine.used_ops + bmachine.extended_ops
        for op in operations:
            # (1) create empty parameter_list
            parameter_list = []

            # (2) find parameter names and add them to the frame
            parameter_idNodes = get_para_nodes(op)
            bstate = env.state_space.get_state()
            bstate.add_ids_to_frame([n.idName for n in parameter_idNodes], bmachine)
            bstate.push_new_frame(parameter_idNodes, bmachine) 
            #print "opname: \t", op.opName # DEBUG

            # (3) Select Operation Type
            assert isinstance(op, AOperation) # FAIL => maybe parsing-error
            substitution = op.children[-1]
            assert isinstance(substitution, Substitution)
            if isinstance(substitution, APreconditionSubstitution):
                predicate = substitution.children[0]
                assert isinstance(predicate, Predicate)
                if not parameter_idNodes==[]:
                    # (3.1a) enumerate operation-parameters 
                    k = 0 # number of found solutions 
                    domain_generator = calc_possible_solutions(env, parameter_idNodes, predicate)
                    for solution in domain_generator:
                        if k==max_op_solutions:
                            break
                        try:
                            # use values of solution:
                            # WARNING:
                            # This should only affect the parameters, 
                            # otherwise this code contains a BUG because 
                            # calc. states affect each other 
                            for name in [x.idName for x in parameter_idNodes]:
                                value = solution[name]
                                bstate.set_value(name, value)
                            if bmachine.interpreter_method(predicate, env): # TEST
                                # Solution found!
                                parameter_list = []
                                # (3.2) add parameter-solutions
                                for name in [x.idName for x in parameter_idNodes]:
                                    parameter_list.append(tuple([name, bstate.get_value(name)]))
                                # (3.3) add op and parameter-values to result list
                                result.append([op, parameter_list, substitution.children[-1]]) #TODO: -1
                                k = k +1
                            # TODO: if states affect each other: !param.param := None
                        except ValueNotInDomainException:
                            continue
                else: 
                    # (3.1b) no operation-parameters: no enumeration 
                    if bmachine.interpreter_method(predicate, env): # TEST
                        result.append([op, [], substitution.children[-1]])
            elif isinstance(substitution, ABlockSubstitution) or isinstance(substitution, AAssignSubstitution):
                result.append([op, parameter_list, op.children[-1]]) # no condition
            elif isinstance(substitution, AIfSubstitution):
                # TODO: if there is no else block, check condition
                result.append([op, parameter_list, substitution])
            elif isinstance(substitution, ASelectSubstitution):
                select_lst = select_ast_to_list(substitution)
                k = 0 # number of found solutions 
                index = 0   
                                  
                if not parameter_idNodes==[]: 
                    # (3.1) enumerate parameters
                    while k<max_op_solutions:
                        predicate = select_lst[index][0]
                        substitution = select_lst[index][1]
                        if predicate==None:
                            assert select_ast.hasElse=="True"
                            result.append([op, parameter_list, substitution])
                            break                          
                        domain_generator = calc_possible_solutions(env, parameter_idNodes, predicate)
                        solution = domain_generator.next()
                        try:
                            # use values of solution:
                            # WARNING:
                            # This Code-Block should only affect the parameters of this operation, 
                            # otherwise this code contains a BUG because 
                            # calculated states affect each other 
                            for name in [x.idName for x in parameter_idNodes]:
                                value = solution[name]
                                bstate.set_value(name, value)
                            # TEST solution candidate 
                            if bmachine.interpreter_method(predicate, env): 
                                # Solution found!
                                parameter_list = []
                                # (3.2) add parameter-solution-tuple
                                for name in [x.idName for x in parameter_idNodes]:
                                    parameter_list.append(tuple([name, bstate.get_value(name)]))
                                # (3.3) add op and parameter-values to result list
                                result.append([op, parameter_list, substitution]) 
                                k = k +1
                            # TODO: if states affect each other: !param.param := None
                        except ValueNotInDomainException:
                            continue
                          
                        # SELECT: select next predicate
                        index = index +1
                        if index == len(select_lst):
                            break
                else:  # no operation-parameters: no enumeration 
                    while k<max_op_solutions:
                        predicate = select_lst[index][0]
                        substitution = select_lst[index][1]
                        if predicate==None:
                            assert select_ast.hasElse=="True"
                            result.append([op, parameter_list, substitution])
                            break  
                        # CHECK: is the pred in this state true?
                        if bmachine.interpreter_method(predicate, env):
                            result.append([op, [], substitution])
                            k = k+1
                            
                        # SELECT: select next predicate
                        index = index +1
                        if index == len(select_lst):
                            break         
            else:
                raise Exception("ERROR: Optype not implemented:", op.children[-1]) 
            bstate.pop_frame(bmachine)
    return result


def exec_op(env,  op_list, number, bmachine):
    if len(op_list)>number:
        op = op_list[number][0]
        parameter_list = op_list[number][1]
        substitution = op_list[number][2]
        bstate = env.state_space.get_state().clone()
        
        # set parameters
        varList = get_para_nodes(op)
        bstate.push_new_frame(varList, bmachine)
        for p in parameter_list:
            name = p[0]
            value = p[1]
            bstate.set_value(name, value, bmachine)
        #state = op_and_state_list[number][3]
        #
        #XXX rids =get_return_names(op) todo: search ridis
        # env.bstate.add_ids_to_frame(rids)
        bmachine.interpreter_method(substitution, env)
        #return_values = add_return_values(env, rids)
        bstate.pop_frame(bmachine)
        return bstate


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
	#     if not rids == []:
	#         for i in rids:
	#             return_values.append(tuple([i, env.bstate.get_value(i)]))
	#     return return_values
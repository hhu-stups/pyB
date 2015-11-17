#from abstract_interpretation import estimate_computation_time
from ast_nodes import *
from bexceptions import ConstraintNotImplementedException
from config import TOO_MANY_ITEMS, QUICK_EVAL_CONJ_PREDICATES, PRINT_WARNINGS, USE_RPYTHON_CODE
from enumeration import all_values_by_type, all_values_by_type_RPYTHON
from helpers import remove_tuples, couple_tree_to_conj_list, find_constraining_var_nodes, set_to_list
from quick_eval import quick_member_eval


# TODO: not, include and much more
# only a list of special cases at the moment
# helper-function for compute_using_external_solver
# This pretty printer prints B python-style. 
# The pretty printer in pretty_printer.py prints B B-style
def pretty_print_python_style(env, varList, node, qme_nodes):
    #print node
    if isinstance(node, AConjunctPredicate):
        string0 = pretty_print_python_style(env, varList, node.children[0], qme_nodes)
        string1 = pretty_print_python_style(env, varList, node.children[1], qme_nodes)
        if string0 and string1:
            return "("+string0 +") and ("+ string1 +")"    
        elif string0:
            return string0
        elif string1:
            return string1
    elif isinstance(node, ADisjunctPredicate):
        string0 = pretty_print_python_style(env, varList, node.children[0], qme_nodes)
        string1 = pretty_print_python_style(env, varList, node.children[1], qme_nodes)
        if string0 and string1:
            return "("+string0 +") or ("+ string1 +")"    
        elif string0:
            return string0
        elif string1:
            return string1    
    elif isinstance(node, AMemberPredicate) and isinstance(node.children[0], AIdentifierExpression) and node.children[0].idName in [x.idName for x in varList]:
        qme_nodes.append(node.children[1])
        return " quick_member_eval( qme_nodes["+str(len(qme_nodes)-1)+"], env,"+node.children[0].idName+")"
    elif isinstance(node, AGreaterPredicate) or isinstance(node, ALessPredicate) or isinstance(node, ALessEqualPredicate) or isinstance(node, AGreaterEqualPredicate) or isinstance(node, AEqualPredicate) or isinstance(node, ANotEqualPredicate):
        left = ""
        right = ""
        name = ""
        if isinstance(node.children[0], AIdentifierExpression) and node.children[0].idName in [x.idName for x in varList]:
            name = str(node.children[0].idName)
            left = name
            right = pretty_print_python_style(env, varList, node.children[1], qme_nodes)
        elif isinstance(node.children[1], AIdentifierExpression) and node.children[1].idName in [x.idName for x in varList]:
            name = str(node.children[1].idName)
            right = name
            left = pretty_print_python_style(env, varList, node.children[0], qme_nodes)
        if left and right and name:
            bin_op = ""
            if isinstance(node, AGreaterPredicate):
                bin_op = ">"
            elif isinstance(node, ALessPredicate):
                bin_op = "<"
            elif isinstance(node, AGreaterEqualPredicate):
                bin_op = ">="
            elif isinstance(node, ALessEqualPredicate):
                bin_op = "<="
            elif isinstance(node, AEqualPredicate):
                bin_op = "=="
            elif isinstance(node, ANotEqualPredicate):
                bin_op = "!="
            string = left+bin_op+right
            return string
    elif isinstance(node, AIntegerExpression):
        number = node.intValue
        return str(number) 
    elif isinstance(node, AUnaryMinusExpression):
        number = node.children[0].intValue * -1
        return str(number)
    elif isinstance(node, AFunctionExpression) and isinstance(node.children[1],AIdentifierExpression):
        func_name =  node.children[0].idName # TODO:(#ISSUE 13) this may not be an id node in all cases
        function = env.get_value(func_name)
        arg = node.children[1].idName  # TODO:(#ISSUE 13) more args possible. 
        string = arg + " in " + str(dict(function).keys()) + " and " # only try values in domain
        string += str(dict(env.get_value(func_name)))
        string += "["+arg +"]" 
        return string
    #print node.children
    raise ConstraintNotImplementedException(node)


def function(env, func_name, key):
    f = env.get_value(func_name)
    return dict(f)[key]

# wrapper-function for external contraint solver 
# WARNING: asumes that every variable in varList has no value!
def compute_using_external_solver(predicate, env, varList):
    # TODO: import at module level
    # external software:
    # install http://labix.org/python-constraint
    # download and unzip python-constraint-1.1.tar.bz2
    # python setup.py build
    # python setup.py install
    #from pretty_printer import pretty_print
    #print "predicate:", pretty_print(predicate)
    from constraint import Problem
    assert isinstance(predicate, Predicate)
    var_and_domain_lst = []
    # get domain 
    for idNode in varList:
        assert isinstance(idNode, AIdentifierExpression)
        atype = env.get_type_by_node(idNode)
        #if USE_RPYTHON_CODE:
        #    domain = all_values_by_type_RPYTHON(atype, env, idNode)
        #else:
        #    domain = all_values_by_type(atype, env, idNode)
        domain = all_values_by_type(atype, env, idNode)
        tup = (idNode.idName, domain)
        var_and_domain_lst.append(tup)
    problem = Problem() # import from "constraint"
    for tup in var_and_domain_lst:
        name = tup[0]
        lst  = tup[1]
        if isinstance(lst, frozenset):
            lst = set_to_list(lst) 
        problem.addVariable(name, lst)
    qme_nodes = []
    constraint_string = pretty_print_python_style(env, varList, predicate, qme_nodes)
    names = [x.idName for x in varList]
    expr = "lambda "
    for n in names[0:-1]:
        expr += n+","
    expr += varList[-1].idName+":"+constraint_string
    #print expr
    my_globales = {"qme_nodes":qme_nodes, "quick_member_eval":quick_member_eval, "env":env}
    lambda_func = eval(expr, my_globales)  # TODO:(#ISSUE 16) not Rpython
    problem.addConstraint(lambda_func, names)
    return problem.getSolutionIter()
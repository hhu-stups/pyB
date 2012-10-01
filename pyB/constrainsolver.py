# install http://labix.org/python-constraint
# download and unzip python-constraint-1.1.tar.bz2
# python setup.py build
# python setup.py install
from constraint import *
from ast_nodes import *
from enumeration import all_values_by_type


def calc_constraint_domain(env, varList, predicate):
    assert isinstance(predicate, Predicate)
    var_and_domain_lst = []
    for idNode in varList:
        assert isinstance(idNode, AIdentifierExpression)
        atype = env.get_type_by_node(idNode)
        domain = all_values_by_type(atype, env)
        tup = (idNode.idName, domain)
        var_and_domain_lst.append(tup)
    problem = Problem() # form constraint
    for tup in var_and_domain_lst:
        problem.addVariable(tup[0], tup[1])
    add_constraints(env, problem, varList, predicate)
    L = problem.getSolutions()
    result = []
    # add constraint domain to result list
    for idNode in varList: 
        values = [x[idNode.idName] for x in L]
        values.sort()
        result.append(values)
    return result


def add_constraints(env, problem, varList, node):
    print node
    if isinstance(node, AConjunctPredicate):
        add_constraints(env, problem, varList, node.children[0])
        add_constraints(env, problem, varList, node.children[1])
    if isinstance(node, ABelongPredicate):
        if isinstance(node.children[0], AIdentifierExpression) and node.children[0].idName in [x.idName for x in varList]:
            if isinstance(node.children[1], AIntervalExpression):
                name = str(node.children[0].idName)
                number0 = node.children[1].children[0].intValue
                number1 = node.children[1].children[1].intValue
                expr0 = "lambda "+name+":"+name+">"+str(number0-1)
                expr1 = "lambda "+name+":"+name+"<"+str(number1+1)
                problem.addConstraint(eval(expr0))
                problem.addConstraint(eval(expr1))
    elif isinstance(node, AGreaterPredicate):
        if isinstance(node.children[0], AIdentifierExpression) and node.children[0].idName in [x.idName for x in varList] and  isinstance(node.children[1], AIntegerExpression):
            number = node.children[1].intValue
            name = str(node.children[0].idName)
            expr = "lambda "+name+":"+name+">"+str(number)
            problem.addConstraint(eval(expr))
    elif isinstance(node, ALessPredicate):
         if isinstance(node.children[0], AIdentifierExpression) and node.children[0].idName in [x.idName for x in varList] and  isinstance(node.children[1], AIntegerExpression):
            number = node.children[1].intValue
            name = str(node.children[0].idName)
            expr = "lambda "+name+":"+name+"<"+str(number)
            problem.addConstraint(eval(expr))   
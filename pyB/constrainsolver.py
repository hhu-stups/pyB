# install http://labix.org/python-constraint
# download and unzip python-constraint-1.1.tar.bz2
# python setup.py build
# python setup.py install
from constraint import *
# pyB imports
from ast_nodes import *
from enumeration import all_values_by_type


# wrapper function for contraint solver 
def calc_constraint_domain(env, varList, predicate):
    assert isinstance(predicate, Predicate)
    var_and_domain_lst = []
    # get domain 
    for idNode in varList:
        assert isinstance(idNode, AIdentifierExpression)
        atype = env.get_type_by_node(idNode)
        domain = all_values_by_type(atype, env)
        tup = (idNode.idName, domain)
        var_and_domain_lst.append(tup)
    problem = Problem() # import from "constraint"
    for tup in var_and_domain_lst:
        problem.addVariable(tup[0], tup[1])
    constraint_string = pretty_print(env, varList, predicate)
    expr = "lambda "
    for x in varList[0:-1]:
        expr += x.idName+","
    expr += varList[-1].idName+":"+constraint_string
    print expr
    problem.addConstraint(eval(expr)) # XXX not Rpython
    L = problem.getSolutions()
    result = []
    # add constraint domain to result list
    for idNode in varList: 
        values = [x[idNode.idName] for x in L]
        values.sort()
        result.append(values)
    return result


def function(env, func_name, key):
    f = env.bstate.get_value(func_name)
    return dict(f)[key]

    
# TODO: not, include
# only a list of special cases at the moment
def pretty_print(env, varList, node):
    #print node
    if isinstance(node, AConjunctPredicate):
        string0 = pretty_print(env, varList, node.children[0])
        string1 = pretty_print(env, varList, node.children[1])
        if string0 and string1:
            return string0 +" and "+ string1     
        elif string0:
            return string0
        elif string1:
            return string1
    elif isinstance(node, ABelongPredicate):
        if isinstance(node.children[0], AIdentifierExpression) and node.children[0].idName in [x.idName for x in varList] and isinstance(node.children[1], AIntervalExpression):
			name = str(node.children[0].idName)
			number0 = ""
			number1 = ""
			if isinstance(node.children[1].children[0], AUnaryExpression):
				number0 = node.children[1].children[0].children[0].intValue * -1
			elif isinstance(node.children[1].children[0], AIntegerExpression):
				number0 = node.children[1].children[0].intValue
			if isinstance(node.children[1].children[1], AUnaryExpression):
				number1 = node.children[1].children[1].children[0].intValue * -1
			elif isinstance(node.children[1].children[1], AIntegerExpression):
				number1 = node.children[1].children[1].intValue
			if number0 and number1:
				string = name+">"+str(number0-1)
				string += " and "+name+"<"+str(number1+1)
				return string
	elif isinstance(node.children[0], AIdentifierExpression) and node.children[0].idName in [x.idName for x in varList] and isinstance(node.children[1], AIdentifierExpression):
			name = str(node.children[0].idName)
			setName = str(node.children[1].idName)
			value = env.bstate.get_value(setName)
			string = name+" in "+str(value)
			return string 
    elif isinstance(node, AGreaterPredicate) or isinstance(node, ALessPredicate) or isinstance(node, ALessEqualPredicate) or isinstance(node, AGreaterEqualPredicate) or isinstance(node, AEqualPredicate) or isinstance(node, AUnequalPredicate):
        left = ""
        right = ""
        name = ""
        if isinstance(node.children[0], AIdentifierExpression) and node.children[0].idName in [x.idName for x in varList] and  isinstance(node.children[1], AIntegerExpression):
            number = node.children[1].intValue
            name = str(node.children[0].idName)
            left = name
            right = str(number)
        elif isinstance(node.children[1], AIdentifierExpression) and node.children[1].idName in [x.idName for x in varList] and  isinstance(node.children[0], AIntegerExpression):
            number = node.children[0].intValue
            name = str(node.children[1].idName)
            right = name
            left = str(number)
        if left and right and name:
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
            elif isinstance(node, AUnequalPredicate):
                bin_op = "!="
            string = left+bin_op+right
            return string 
  
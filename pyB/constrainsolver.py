# pyB imports:
from ast_nodes import *
from enumeration import all_values_by_type
from bexceptions import ConstraintNotImplementedException



def calc_possible_solutions(env, varList, predicate):
    try:
        iterator = calc_constraint_domain(env, varList, predicate)
        return iterator
    except Exception: 
        generator = gen_all_values(env, varList, {})
        return generator.__iter__()
    

def gen_all_values(env, varList, dic):
    idNode = varList[0]
    assert isinstance(idNode, AIdentifierExpression)
    atype = env.get_type_by_node(idNode)
    domain = all_values_by_type(atype, env)
    var_name = idNode.idName
    for value in domain:
        dic[var_name] = value
        if len(varList)==1:
            yield dic.copy()
        else:
            for d in gen_all_values(env, varList[1:], dic):
                yield d
            
                

# wrapper-function for contraint solver 
# WARNING: asumes that every variable in varList has no value!
def calc_constraint_domain(env, varList, predicate):
    # extern software:
    # install http://labix.org/python-constraint
    # download and unzip python-constraint-1.1.tar.bz2
    # python setup.py build
    # python setup.py install
    from constraint import *
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
        name = tup[0]
        lst  = tup[1]
        problem.addVariable(name, lst)
    constraint_string = pretty_print(env, varList, predicate)
    names = [x.idName for x in varList]
    expr = "lambda "
    for n in names[0:-1]:
        expr += n+","
    expr += varList[-1].idName+":"+constraint_string
    problem.addConstraint(eval(expr),names) # XXX not Rpython
    return problem.getSolutionIter()


def function(env, func_name, key):
    f = env.get_value(func_name)
    return dict(f)[key]

    
# TODO: not, include and much more
# only a list of special cases at the moment
# helper-function for calc_constraint_domain
# This pretty printer prints B python-style. 
# The pretty printer in pretty_printer.py prints B B-style
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
    elif isinstance(node, ADisjunctPredicate):
        string0 = pretty_print(env, varList, node.children[0])
        string1 = pretty_print(env, varList, node.children[1])
        if string0 and string1:
            return string0 +" or "+ string1     
        elif string0:
            return string0
        elif string1:
            return string1    
    elif isinstance(node, ABelongPredicate) and isinstance(node.children[0], AIdentifierExpression) and node.children[0].idName in [x.idName for x in varList]:
        if isinstance(node.children[1], AIntervalExpression):
            name = str(node.children[0].idName)
            number0 = pretty_print(env, varList, node.children[1].children[0])
            number1 = pretty_print(env, varList, node.children[1].children[1])
            if number0 and number1:
                string = name+">="+str(number0)
                string += " and "+name+"<="+str(number1)
                return string
        elif isinstance(node.children[1], AIdentifierExpression):
            name = str(node.children[0].idName)
            setName = str(node.children[1].idName)
            value = env.get_value(setName)
            string = name+" in "+str(value)
            return string 
        elif isinstance(node.children[1], ANatSetExpression):
            name = str(node.children[0].idName)
            string = name+" in "+str(range(0,env._max_int+1))
            return string   
        elif isinstance(node.children[1], ANat1SetExpression):
            name = str(node.children[0].idName)
            string = name+" in "+str(range(1,env._max_int+1))
            return string 
        elif isinstance(node.children[1], AStringSetExpression):
            name = str(node.children[0].idName)
            value = env.all_strings 
            string = name+" in "+str(value)
            return string     
    elif isinstance(node, AGreaterPredicate) or isinstance(node, ALessPredicate) or isinstance(node, ALessEqualPredicate) or isinstance(node, AGreaterEqualPredicate) or isinstance(node, AEqualPredicate) or isinstance(node, AUnequalPredicate):
        left = ""
        right = ""
        name = ""
        if isinstance(node.children[0], AIdentifierExpression) and node.children[0].idName in [x.idName for x in varList]:
            name = str(node.children[0].idName)
            left = name
            right = pretty_print(env, varList, node.children[1])
        elif isinstance(node.children[1], AIdentifierExpression) and node.children[1].idName in [x.idName for x in varList]:
            name = str(node.children[1].idName)
            right = name
            left = pretty_print(env, varList, node.children[0])
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
    elif isinstance(node, AIntegerExpression):
        number = node.intValue
        return str(number) 
    elif isinstance(node, AUnaryExpression):
        number = node.children[0].intValue * -1
        return str(number)
    elif isinstance(node, AFunctionExpression):
        func_name =  node.children[0].idName
        string = str(dict(env.get_value(func_name)))
        string += "["+node.children[1].idName +"]" # XXX more args
        return string
    #print node
    #raise ConstraintNotImplementedException(node)
         
  
def string_to_number(string):
    result =0
    return result # xx
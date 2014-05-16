# This is NOT a constraint solver. It is a wrapper to enable usage of a constraint solver
# pyB imports:
from ast_nodes import *
from enumeration import all_values_by_type
from bexceptions import ConstraintNotImplementedException, ValueNotInDomainException
from quick_eval import quick_member_eval
from config import TO_MANY_ITEMS, QUICK_EVAL_CONJ_PREDICATES


# assumption: the variables of varList are typed and constraint by the
# predicate. If predicate is None, all values of the variable type is returned.
# After this function returns a generator, every solution-candidate musst be checked! 
# This function may be generate false values, but does not omit right ones 
# i.e no values are missing 
# TODO: move checking inside function
def calc_possible_solutions(predicate, env, varList, interpreter_callable):
    # check which kind of predicate
    assert isinstance(varList, list)

    # case 1: none = no predicate constraining parameter values
    if predicate==None: 
        generator = gen_all_values(env, varList, {})
        return generator.__iter__()
    
    # case 2: a special case implemented by pyB    
    # TODO: support more than one variable
    # check if a solution-set is computable without the external contraint solver
    if QUICK_EVAL_CONJ_PREDICATES and isinstance(predicate, AConjunctPredicate) and len(varList)==1:
        pred_map = _categorize_predicates(predicate, env, varList)
        assert pred_map != []
        test_set = None
        for pred in pred_map:
            if "fast" in pred_map[pred]:
                # at least on predicate of this conjunction can easiely be used
                # to compute a testset. The exact solution musst contain all 
                # or less elements than test_set
                if test_set==None:
                    test_set = _compute_test_set(pred, env, varList, interpreter_callable)
                else:
                    test_set = _filter_false_elements(pred, env, varList, interpreter_callable, test_set)
        if test_set !=None:
            final_set = _filter_false_elements(predicate, env, varList, interpreter_callable, test_set)
            iterator = _set_to_iterator(env, varList, final_set)
            return iterator
        # Todo: generate constraint set by using all "fast computable" predicates
        # Todo: call generator to return solution
        
    
    # case 3: default, use external constraint solver and hope the best
    # If iterator.next() is called the caller musst handel a StopIteration Exception
    try:
        iterator = _calc_constraint_domain(env, varList, predicate)
        # constraint solving succeed. Use iterator in next computation step
        # This generates a list and not a frozenset. 
        return iterator 
    except (ConstraintNotImplementedException, ImportError): 
        # constraint solving failed, enumerate all values (may cause a pyB fail)
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

# XXX: only on var supported
def _set_to_iterator(env, varList, aset):
    if not aset==frozenset([]):
		idNode = varList[0]
		assert isinstance(idNode, AIdentifierExpression)  
		var_name = idNode.idName 
		dic = {} 
		for element in aset:
			dic[var_name] = element 
			yield dic.copy()            
                

# wrapper-function for contraint solver 
# WARNING: asumes that every variable in varList has no value!
def _calc_constraint_domain(env, varList, predicate):
    # TODO: import at module level
    # extern software:
    # install http://labix.org/python-constraint
    # download and unzip python-constraint-1.1.tar.bz2
    # python setup.py build
    # python setup.py install
    from constraint import Problem
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
        if type(lst)==frozenset:
            lst = _set_to_list(lst) 
        problem.addVariable(name, lst)
    qme_nodes = []
    constraint_string = pretty_print(env, varList, predicate, qme_nodes)
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


def _set_to_list(lst):
    return list(lst) # TODO: list of lists

def function(env, func_name, key):
    f = env.get_value(func_name)
    return dict(f)[key]

    
# TODO: not, include and much more
# only a list of special cases at the moment
# helper-function for calc_constraint_domain
# This pretty printer prints B python-style. 
# The pretty printer in pretty_printer.py prints B B-style
def pretty_print(env, varList, node, qme_nodes):
    #print node
    if isinstance(node, AConjunctPredicate):
        string0 = pretty_print(env, varList, node.children[0], qme_nodes)
        string1 = pretty_print(env, varList, node.children[1], qme_nodes)
        if string0 and string1:
            return "("+string0 +") and ("+ string1 +")"    
        elif string0:
            return string0
        elif string1:
            return string1
    elif isinstance(node, ADisjunctPredicate):
        string0 = pretty_print(env, varList, node.children[0], qme_nodes)
        string1 = pretty_print(env, varList, node.children[1], qme_nodes)
        if string0 and string1:
            return "("+string0 +") or ("+ string1 +")"    
        elif string0:
            return string0
        elif string1:
            return string1    
    elif isinstance(node, ABelongPredicate) and isinstance(node.children[0], AIdentifierExpression) and node.children[0].idName in [x.idName for x in varList]:
        qme_nodes.append(node.children[1])
        return " quick_member_eval( qme_nodes["+str(len(qme_nodes)-1)+"], env,"+node.children[0].idName+")"
        #         if isinstance(node.children[1], AIntervalExpression):
        #             name = str(node.children[0].idName)
        #             number0 = pretty_print(env, varList, node.children[1].children[0])
        #             number1 = pretty_print(env, varList, node.children[1].children[1])
        #             if number0 and number1:
        #                 string = name+">="+str(number0)
        #                 string += " and "+name+"<="+str(number1)
        #                 return string
        #         elif isinstance(node.children[1], AIdentifierExpression):
        #             name = str(node.children[0].idName)
        #             setName = str(node.children[1].idName)
        #             value = env.get_value(setName)
        #             string = name+" in "+str(value)
        #             return string 
        #         elif isinstance(node.children[1], ANatSetExpression):
        #             name = str(node.children[0].idName)
        #             string = name+" in "+str(range(0,env._max_int+1))
        #             return string   
        #         elif isinstance(node.children[1], ANat1SetExpression):
        #             name = str(node.children[0].idName)
        #             string = name+" in "+str(range(1,env._max_int+1))
        #             return string 
        #         elif isinstance(node.children[1], AIntegerSetExpression): # TODO:(#ISSUE 17)
        #             name = str(node.children[0].idName)
        #             string = name+" in "+str(range(env._min_int,env._max_int+1))
        #             return string           
        #         elif isinstance(node.children[1], AStringSetExpression):
        #             name = str(node.children[0].idName)
        #             value = env.all_strings 
        #             string = name+" in "+str(value)
        #             return string     
    elif isinstance(node, AGreaterPredicate) or isinstance(node, ALessPredicate) or isinstance(node, ALessEqualPredicate) or isinstance(node, AGreaterEqualPredicate) or isinstance(node, AEqualPredicate) or isinstance(node, AUnequalPredicate):
        left = ""
        right = ""
        name = ""
        if isinstance(node.children[0], AIdentifierExpression) and node.children[0].idName in [x.idName for x in varList]:
            name = str(node.children[0].idName)
            left = name
            right = pretty_print(env, varList, node.children[1], qme_nodes)
        elif isinstance(node.children[1], AIdentifierExpression) and node.children[1].idName in [x.idName for x in varList]:
            name = str(node.children[1].idName)
            right = name
            left = pretty_print(env, varList, node.children[0], qme_nodes)
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


# TODO: support more than one variable
# input: P0 & P1 & ...PN
# output(example): mapping {P0->fast, P1->long,... PN->infinite}        
def _categorize_predicates(predicate, env, varList):
    if isinstance(predicate, AConjunctPredicate):
        map0 = _categorize_predicates(predicate.children[0], env, varList)
        map1 = _categorize_predicates(predicate.children[1], env, varList)
        map0.update(map1)
        return map0
    else:
       string = _estimate_computation_time(predicate, env, varList)
       return {predicate: string}


# TODO: support more than one variable (which is constraint by the predicate to be analysed
# this approximation is still not good. Eg. x/:NAT   
# TODO: maybe replace with abstract interpretation 
# TODO: return numbers insed of fast to estimate set explosion    
def _estimate_computation_time(node, env, varList):
    if isinstance(node, (AIntegerSetExpression, ANaturalSetExpression, ANatural1SetExpression)):
        return "infinite: %s" % node
    elif isinstance(node, (ANatSetExpression, ANat1SetExpression, )):
        if env._max_int > TO_MANY_ITEMS:
            return "long: %s" % node
        else: 
            return "fast"
    elif isinstance(node, AIntSetExpression):
        if env._min_int*-1 + env._max_int > TO_MANY_ITEMS:
            return "long: %s" % node
        else:
            return "fast"    
    elif isinstance(node, AIntegerExpression):
        return "fast"
    elif isinstance(node, AUnaryExpression):
        return _estimate_computation_time(node.children[0], env, varList)
    #elif isinstance(node, APartialFunctionExpression):
    #    if "fast" in _estimate_computation_time(node.children[0], env, varList) and "fast" in _estimate_computation_time(node.children[1], env, varList):
    #        return "fast"
    elif isinstance(node, (ASetExtensionExpression, ACoupleExpression)):
        if "fast" in _estimate_computation_time(node.children[0], env, varList) and "fast" in _estimate_computation_time(node.children[1], env, varList):
            return "fast"
    elif isinstance(node, ABelongPredicate):
        # takes much time if set computation on the rhs takes much time
        # left side indicates: rhs contrains set elements
        if isinstance(node.children[0], AIdentifierExpression) and node.children[0].idName in [x.idName for x in varList]:
            return _estimate_computation_time(node.children[1], env, varList)
    elif isinstance(node, AEqualPredicate):
        # takes much time if computation on the rhs takes much time
        # left side indicates: rhs contrains set elements
        if isinstance(node.children[0], AIdentifierExpression) and node.children[0].idName in [x.idName for x in varList]:
            return _estimate_computation_time(node.children[1], env, varList)
    return "dont know"


def _compute_test_set(node, env, varList, interpreter_callable):
    if isinstance(node, AEqualPredicate):
        value = interpreter_callable(node.children[1], env)
        # if elements of the set are equal to some expression, a set has to be generated 
        # e.g {x| x:NAT & x=42}  results in {42}
        return frozenset([value])
    elif isinstance(node, ABelongPredicate):
        set = interpreter_callable(node.children[1], env)
        # e.g. {x| x:Nat & x:{1,2,3}}
        assert isinstance(set, frozenset)
        return set
    else:
    	raise NotImplementedException()


# remove all elements which do not satisfy pred
# TODO: support more than on variable 
def _filter_false_elements(pred, env, varList, interpreter_callable, test_set):
    result = []
    idNode = varList[0]
    assert isinstance(idNode, AIdentifierExpression)  
    var_name = idNode.idName 
    env.push_new_frame(varList)
    for value in test_set:
        env.set_value(var_name, value)
        try:
            if interpreter_callable(pred, env):
                result.append(value)
        except ValueNotInDomainException: # function app with wrong value
            continue # skip this false value
    env.pop_frame()
    return frozenset(result)
    

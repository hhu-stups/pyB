# This is NOT a constraint solver. It is a wrapper to enable usage of a constraint solver
# pyB imports:
from ast_nodes import *
from enumeration import all_values_by_type
from bexceptions import ConstraintNotImplementedException, ValueNotInDomainException
from quick_eval import quick_member_eval
from config import TO_MANY_ITEMS, QUICK_EVAL_CONJ_PREDICATES, PRINT_WARNINGS
from abstract_interpretation import estimate_computation_time
from pretty_printer import pretty_print


class PredicateDoesNotMatchException:
    pass # TODO: refactor me

# assumption: the variables of varList are typed may constraint by the
# predicate. If predicate is None, all values of the variable type is returned.
# After this function returns a generator, every solution-candidate musst be checked! 
# This function may be generate false values, but does not omit right ones 
# i.e no values are missing 
# TODO: move checking inside this function i.e. generate NO FALSE values
def calc_possible_solutions(predicate, env, varList, interpreter_callable):
    assert isinstance(varList, list)
    # check which kind of predicate: 3 cases

    # case 1: None = no predicate constraining parameter values, generate all values
    if predicate==None: 
        generator = gen_all_values(env, varList, {})
        return generator.__iter__()
    
    # case 2: a special case implemented by pyB    
    # check if a solution-set is computable without a external contraint solver
    # TODO: support more than one variable
    if QUICK_EVAL_CONJ_PREDICATES and isinstance(predicate, AConjunctPredicate) and len(varList)==1:
        pred_map = _categorize_predicates(predicate, env, varList)
        assert pred_map != []
        test_set = None
        for pred in pred_map:
            (time, vars) = pred_map[pred]
            
            # TODO: more than one var 
            var_node = varList[0]
            if time!=float("inf") and time<TO_MANY_ITEMS and varList[0].idName in vars:
                # at least on predicate of this conjunction can easiely be used
                # to compute a testset. The exact solution musst contain all 
                # or less elements than test_set
                if test_set==None:
                    try:
                        test_set = _compute_test_set(pred, env, var_node, interpreter_callable)
                    except PredicateDoesNotMatchException: #.eg constraining y instead of x, or using unimplemented cases
                        test_set = None 
                else:
                    test_set = _filter_false_elements(pred, env, var_node, interpreter_callable, test_set)
                #print "predicate for testset:", pretty_print(pred)
                #print "test set:", test_set
        if test_set !=None:
            final_set = _filter_false_elements(predicate, env, var_node, interpreter_callable, test_set)
            iterator = _set_to_iterator(env, varList, final_set)
            return iterator
        # Todo: generate constraint set by using all "fast computable" predicates
        # Todo: call generator to return solution
        
    
    # case 3: default, use external constraint solver and hope the best
    # If iterator.next() is called the caller musst handel a StopIteration Exception
    try:
        if PRINT_WARNINGS:
            print "WARNING! External constraint solver called. Caused by: %s" % pretty_print(predicate) 
        iterator = _calc_constraint_domain(env, varList, predicate)
        # constraint solving succeed. Use iterator in next computation step
        # This generates a list and not a frozenset. 
        return iterator 
    except (ConstraintNotImplementedException, ImportError):
        if PRINT_WARNINGS:
            print "WARNING! Brute force enumeration caused by: %s" % pretty_print(predicate) 
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
    #from pretty_printer import pretty_print
    #print "predicate:", pretty_print(predicate)
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
    elif isinstance(node, ABelongPredicate) and isinstance(node.children[0], AIdentifierExpression) and node.children[0].idName in [x.idName for x in varList]:
        qme_nodes.append(node.children[1])
        return " quick_member_eval( qme_nodes["+str(len(qme_nodes)-1)+"], env,"+node.children[0].idName+")"
    elif isinstance(node, AGreaterPredicate) or isinstance(node, ALessPredicate) or isinstance(node, ALessEqualPredicate) or isinstance(node, AGreaterEqualPredicate) or isinstance(node, AEqualPredicate) or isinstance(node, AUnequalPredicate):
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
# FIMXE: doesnt finds finite-time computable sub-predicates. 
#        e.g P0="P00(x) or P01(y)" with P01 infinite
# input: P0 & P1 & ...PN
# output(example): mapping {P0->(time0, vars0), , P1->(time1, vars1),... PN->(timeN, varsN)}        
def _categorize_predicates(predicate, env, varList):
    if isinstance(predicate, AConjunctPredicate):
        map0 = _categorize_predicates(predicate.children[0], env, varList)
        map1 = _categorize_predicates(predicate.children[1], env, varList)
        map0.update(map1)
        return map0
    else:
       time = estimate_computation_time(predicate, env)
       constraint_vars = find_constraint_vars(predicate, env, varList)
       return {predicate: (time, constraint_vars)}


# input predicate is always a sub-predicate of a conjunction predicate 
def find_constraint_vars(predicate, env, varList):
    if isinstance(predicate, ABelongPredicate):
        if isinstance(predicate.children[0], AIdentifierExpression):
            test_set_var = [predicate.children[0].idName]
            return test_set_var
    elif isinstance(predicate, AEqualPredicate):
        if isinstance(predicate.children[0], AIdentifierExpression):
            test_set_var = [predicate.children[0].idName]
            return test_set_var
        elif isinstance(predicate.children[1], AIdentifierExpression):
            test_set_var = [predicate.children[1].idName]
            return test_set_var
    # if the subpredicate consists of a conjunction or disjunction, it 
    # constraints a var x if x is constraint by one sub-predicate,
    # because this sub-predicate may be a candidate for test-set generation
    elif isinstance(predicate, (ADisjunctPredicate, AConjunctPredicate)):
        lst0 = find_constraint_vars(predicate.children[0], env, varList)
        lst1 = find_constraint_vars(predicate.children[1], env, varList)
        test_set_var = list(set(lst0 + lst1)) # remove double entries 
        return test_set_var
    # No implemented case found. Maybe there are constraints, but pyB doesnt find them
    # TODO: Implement more cases, but only that on handeld in _compute_test_set
    return []
        
# TODO: be sure this cases have no side effect
# XXX: not all cases implemented (maybe not possible)
def _compute_test_set(node, env, var_node, interpreter_callable):
    if isinstance(node, AEqualPredicate):
        # if elements of the set are equal to some expression, a set has to be generated 
        # e.g {x| x:NAT & x=42}  results in {42}
        if isinstance(node.children[0], AIdentifierExpression) and node.children[0].idName==var_node.idName:
            value = interpreter_callable(node.children[1], env)
            return frozenset([value])
        if isinstance(node.children[1], AIdentifierExpression) and node.children[1].idName==var_node.idName:
            value = interpreter_callable(node.children[0], env)
            return frozenset([value])
    elif isinstance(node, ABelongPredicate):
        if isinstance(node.children[0], AIdentifierExpression) and node.children[0].idName==var_node.idName:
            set = interpreter_callable(node.children[1], env)
            # e.g. {x| x:Nat & x:{1,2,3}}
            assert isinstance(set, frozenset)
            return set
    # this is only called because both branches (node.childern[0] and node.childern[1])
    # of the disjunction are computable in finite time. (as analysed by _categorize_predicates)
    elif isinstance(node, ADisjunctPredicate):
        set0 = _compute_test_set(node.children[0], env, var_node, interpreter_callable)
        set1 = _compute_test_set(node.children[1], env, var_node, interpreter_callable)
        return set0.union(set1)
    elif isinstance(node, AConjunctPredicate):
        try:
            set0 = _compute_test_set(node.children[0], env, var_node, interpreter_callable)
            try:
                set1 = _compute_test_set(node.children[1], env, var_node, interpreter_callable)
                return set0.union(set1)
            except PredicateDoesNotMatchException:
                return set0
        except PredicateDoesNotMatchException:
            set1 = _compute_test_set(node.children[1], env, var_node, interpreter_callable)
            return set1   
    else:
        raise PredicateDoesNotMatchException()


# remove all elements which do not satisfy pred
# TODO: support more than on variable 
def _filter_false_elements(pred, env, var_node, interpreter_callable, test_set):
    result = []
    assert isinstance(var_node, AIdentifierExpression)  
    var_name = var_node.idName 
    env.push_new_frame([var_node])
    for value in test_set:
        #print "filter_false:", var_name, value
        env.set_value(var_name, value)
        try:
            if interpreter_callable(pred, env):
                result.append(value)
        except ValueNotInDomainException: # function app with wrong value
            continue # skip this false value
    env.pop_frame()
    return frozenset(result)
    

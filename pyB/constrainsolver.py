# This is NOT a constraint solver. It is a wrapper to enable usage of a constraint solver
# pyB imports:
from ast_nodes import *
from enumeration import all_values_by_type
from bexceptions import ConstraintNotImplementedException, ValueNotInDomainException
from quick_eval import quick_member_eval
from config import TO_MANY_ITEMS, QUICK_EVAL_CONJ_PREDICATES, PRINT_WARNINGS
from abstract_interpretation import estimate_computation_time
from pretty_printer import pretty_print
from helpers import remove_tuples, couple_tree_to_conj_list
from symbolic_sets import LargeSet


class PredicateDoesNotMatchException:
    pass # TODO: refactor me

# assumption: the variables of varList are typed may constraint by the
# predicate. If predicate is None(no constraint), all values of the variable type is returned.
# After this function returns a generator, every solution-candidate musst be checked! 
# This function may be generate false values, but does not omit right ones 
# i.e no values are missing 
# varList: variables need to be constraint
# returns a list of dicts [{x1:value00, ... ,xN:valueN0}, ... ,{x1:value0N, ... ,xN:value1NN}]
# TODO: move checking inside this function i.e. generate NO FALSE values
def calc_possible_solutions(predicate, env, varList, interpreter_callable):
    #print "calc_possible_solutions: ", pretty_print(predicate)
    assert isinstance(varList, list)
    # check which kind of predicate: 3 cases

    # case 1: None = no predicate constraining parameter values, generate all values
    if predicate==None: 
        generator = gen_all_values(env, varList, {})
        return generator.__iter__()
    
    # case 2: a special case implemented by pyB    
    # check if a solution-set is computable without a external contraint solver
    if QUICK_EVAL_CONJ_PREDICATES:
        pred_map = _categorize_predicates(predicate, env, varList)
        assert pred_map != []
        test_dict = {}
        #print "DEBUG: varlist", [x.idName for x in varList]
        for var_node in varList:
            #print "DEBUG: searching for", var_node.idName,"constraint"
            test_set = None 
            for pred in pred_map:
                (time, vars) = pred_map[pred]
                #print "DEBUG:  vars:",vars, "contraint by", pretty_print(pred)
                # Avoid interference between bound variables: check find_constraint_vars
                # This is less powerful, but correct
                if time!=float("inf") and time<TO_MANY_ITEMS and var_node.idName in vars:
                    # at least on predicate of this conjunction can easiely be used
                    # to compute a testset. The exact solution musst contain all 
                    # or less elements than test_set
                    if test_set==None:
                        try:
                            assert isinstance(pred, Predicate)
                            test_set = _compute_test_set(pred, env, var_node, interpreter_callable)
                            break
                        except PredicateDoesNotMatchException: 
                            #.eg constraining y instead of x, or using unimplemented cases
                            test_set = None
                #else:
                #    print "DEBUG:  can not constrain:", var_node.idName 
            # assigning constraint set or none
            test_dict[var_node] = test_set
                        
        # check if a solution has been found for every bound variable
        solution_found = True
        for var_node in varList:   
            if test_dict[var_node]==None or test_dict[var_node]==frozenset([]):
                if PRINT_WARNINGS:
                    print "WARNING! Unable to constrain bound variable: %s" % var_node.idName
                solution_found = False
                
        # use this solution and return a generator        
        if solution_found:          
            iterator = _dict_to_iterator(env, varList, test_dict, predicate, interpreter_callable, {})
            return iterator
        # Todo: generate constraint set by using all "fast computable" predicates
        # Todo: call generator to return solution
        
    
    # case 3: default, use external constraint solver and hope the best
    # If iterator.next() is called the caller musst handel a StopIteration Exception
    # TODO: Handle OverflowError, print Error message and go on
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
    domain = all_values_by_type(atype, env, idNode)
    var_name = idNode.idName
    for value in domain:
        dic[var_name] = value
        if len(varList)==1:
            yield dic.copy()
        else:
            for d in gen_all_values(env, varList[1:], dic):
                yield d


def _dict_to_iterator(env, varList, test_dict, pred, interpreter_callable, partial_solution):
    idNode = varList[0]
    aSet = test_dict[idNode]
    assert not aSet==frozenset([])
    assert isinstance(idNode, AIdentifierExpression)
    var_name = idNode.idName 
    for element in aSet:
        partial_solution[var_name] = element
        if len(varList)==1:
            if _is_solution(pred, env, interpreter_callable, varList, solution=partial_solution.copy()):
                solution = partial_solution.copy()
                yield solution
        else:
            for solution in _dict_to_iterator(env, varList[1:], test_dict, pred, interpreter_callable, partial_solution):
                yield solution



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
        domain = all_values_by_type(atype, env, idNode)
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
# input: P0 & P1 & ...PN or in special cases one predicate (like x=42)
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


# Input predicate is always a sub-predicate of a conjunction predicate or a single predicate.
# This helper may only be used to find test_set(constraint domain) generation candidates.
# return: list of variable names, constraint by this predicated AND with possible test_set gen.  
def find_constraint_vars(predicate, env, varList):
    # (1) Base case. This case should only be matched by a recursive call of find_constraint_vars.
    # otherwise it could produce wrong results!
    # WARNING: before modifying this part, be sure "_compute_test_set" can handle it!     
    if isinstance(predicate, AIdentifierExpression):
        lst = [predicate.idName]
        return lst
    elif isinstance(predicate, ACoupleExpression):
        lst0 = find_constraint_vars(predicate.children[0], env, varList)
        lst1 = find_constraint_vars(predicate.children[1], env, varList)
        lst  = list(set(lst0 + lst1)) # remove double entries
        return lst
        
    # (2) implemented predicates (by _compute_test_set)
    # WARNING: never add a case if "_compute_test_set" can not handle it!
    if isinstance(predicate, ABelongPredicate):
        lst = find_constraint_vars(predicate.children[0], env, varList)
        return lst
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
        # belong-case 1: left side is just an id
        if isinstance(node.children[0], AIdentifierExpression) and node.children[0].idName==var_node.idName:
            set = interpreter_callable(node.children[1], env)
            if isinstance(set, LargeSet):
                set = set.enumerate()
            # e.g. x:{1,2,3} or x:S
            # return finite set on the left as test_set/constraint domain
            # FIXME: isinstance('x', frozenset) -> find enumeration order!
            assert isinstance(set, frozenset)
            return set
        # belong-case 2: n-tuple on left side
        elif isinstance(node.children[0], ACoupleExpression):
            # e.g. (x,y){x|->y:{(1,2),(3,4)}...} (only one id-constraint found in this pass)
            # e.g. (x,y,z){x|->(y|->z):{(1,(2,3)),(4,(5,6))..} 
            # TODO: Handle ((x|->y),(z|->a)):S
            
            # 2.1 search n-tuple for matching var (to be constraint)
            element_list = couple_tree_to_conj_list(node.children[0])
            index = 0
            match = False
            for e in element_list:
                if isinstance(e, AIdentifierExpression) and e.idName==var_node.idName:
                    match = True
                    break
                index = index +1
            
            # 2.2. compute set if match found
            if match:
                set = interpreter_callable(node.children[1], env)
                assert isinstance(set, frozenset)
                # 2.3. return correct part of the set corresponding to position of
                # searched variable inside the tuple on the left side
                return [remove_tuples(t, [])[index] for t in set]
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


# check if solution satisfies predicate 
def _is_solution(pred, env, interpreter_callable, varList, solution):
    env.push_new_frame(varList)
    for key in solution:
        value = solution[key]
        #print "set",key,"to",value
        env.set_value(key, value)
    try:
        result = interpreter_callable(pred, env)
    except ValueNotInDomainException: # function app with wrong value
        result = False
    env.pop_frame()
    return result
    

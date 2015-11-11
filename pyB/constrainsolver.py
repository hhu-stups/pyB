# This is NOT a constraint solver. It is a wrapper to enable usage of a constraint solver
# pyB imports:
from abstract_interpretation import estimate_computation_time
from ast_nodes import *
from bexceptions import ConstraintNotImplementedException, ValueNotInDomainException
from config import TOO_MANY_ITEMS, QUICK_EVAL_CONJ_PREDICATES, PRINT_WARNINGS, USE_RPYTHON_CODE
from enumeration import all_values_by_type, all_values_by_type_RPYTHON
from helpers import remove_tuples, couple_tree_to_conj_list, find_constraining_var_nodes
from pretty_printer import pretty_print
from quick_eval import quick_member_eval
from symbolic_sets import SymbolicSet

if USE_RPYTHON_CODE:
     from rpython_b_objmodel import frozenset


class PredicateDoesNotMatchException(Exception):
    pass # TODO: refactor me

class SpecialCaseEnumerationFailedException(Exception):
    pass


        
# assumption: the variables of varList are typed may constraint by the
# predicate. If predicate is None(no constraint), all values of the variable type is returned.
# After this function returns a generator, every solution-candidate musst be checked! 
# This function may be generate false values, but does not omit right ones 
# i.e no values are missing 
# varList: variables need to be constraint
# returns a list of dicts [{x1:value00, ... ,xN:valueN0}, ... ,{x1:value0N, ... ,xN:value1NN}]
# TODO: move checking inside this function i.e. generate NO FALSE values
# TODO: maybe a new argument containing a partial computation (e.g. on of many vars with 
#       with domain constraint) would be a nice refactoring to solve get_item in symb. comp. set
def calc_possible_solutions(predicate, env, varList):
    #print "calc_possible_solutions: ", pretty_print(predicate)
    assert isinstance(varList, list)
    for n in varList:
        assert isinstance(n, AIdentifierExpression)
    # check which kind of predicate: 3 cases

    # case 1: None = no predicate constraining parameter values, generate all values
    if predicate is None: 
        generator = gen_all_values(env, varList, {})
        for d in generator:
            yield d
        raise StopIteration()
        #return generator.__iter__()


    # case 2: a special case implemented by pyB    
    # check if a solution-set is computable without a external contraint solver
    # FIXME: assertion fail in rptyhon.interpret (maybe unwrepped data)
    if QUICK_EVAL_CONJ_PREDICATES:
        try:
            generator = _compute_generator_using_special_cases(predicate, env, varList)
            for d in generator:
                yield d
            raise StopIteration()
            #return generator.__iter__()
        except SpecialCaseEnumerationFailedException:
            pass

    
    # case 3: default, use external constraint solver and hope the best
    # If iterator.next() is called the caller musst handel a StopIteration Exception
    # TODO: Handle OverflowError, print Error message and go on
    try:
        if PRINT_WARNINGS:
            print "\033[1m\033[91mWARNING\033[00m: External constraint solver called. Caused by: %s" % pretty_print(predicate) 
        #TODO: enable this call in RPYTHON
        if USE_RPYTHON_CODE: # Using external constraint solver not supported yet
            raise ImportError()
        iterator = _calc_constraint_domain(env, varList, predicate)
        # constraint solving succeed. Use iterator in next computation step
        # This generates a list and not a frozenset. 
        for d in iterator:
            yield d
        raise StopIteration()
        #return iterator 
    except (ConstraintNotImplementedException, ImportError):
        if PRINT_WARNINGS:
            print "\033[1m\033[91mWARNING\033[00m: External constraint solver faild. Brute force enumeration caused by: %s! enumerating: %s" % (pretty_print(predicate), [v.idName for v in varList])
        # TODO: maybe case 2 was able to constrain the domain of some variables but not all
        # this computation is thrown away in this step. This makes no senese. Fix it!
        # constraint solving failed, enumerate all values (may cause a pyB fail)
        generator = gen_all_values(env, varList, {})
        for d in generator:
            yield d
        raise StopIteration()
        #return generator.__iter__()
    

# yields a dict {String-->W_Object} or {String-->value}
def gen_all_values(env, varList, dic):
    idNode = varList[0]
    assert isinstance(idNode, AIdentifierExpression)
    atype = env.get_type_by_node(idNode)
    if USE_RPYTHON_CODE:
        domain = all_values_by_type_RPYTHON(atype, env, idNode)
    else:
        domain = all_values_by_type(atype, env, idNode)
    var_name = idNode.idName
    for value in domain:
        dic[var_name] = value
        if len(varList)==1:
            yield dic.copy()
        else:
            for d in gen_all_values(env, varList[1:], dic):
                yield d


# wrapper-function for external contraint solver 
# WARNING: asumes that every variable in varList has no value!
def _calc_constraint_domain(env, varList, predicate):
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
        if USE_RPYTHON_CODE:
            domain = all_values_by_type_RPYTHON(atype, env, idNode)
        else:
            domain = all_values_by_type(atype, env, idNode)
        tup = (idNode.idName, domain)
        var_and_domain_lst.append(tup)
    problem = Problem() # import from "constraint"
    for tup in var_and_domain_lst:
        name = tup[0]
        lst  = tup[1]
        if isinstance(lst, frozenset):
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


def _set_to_list(aSet):
    return list(aSet) # TODO: list of lists

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


# returns a generator or None if fail (e.g. special case not implemented)   
# Todo: generate constraint set by using all "fast computable" predicates
# Todo: call generator to return solution      
def _compute_generator_using_special_cases(predicate, env, varList):
    # 1. score predicates
    pred_map = _categorize_predicates(predicate, env, varList)
    assert pred_map is not {}
    # 2. find possible variable enum order. 
    # variable(-domains) not constraint by others will be enumerated first.
    varList  = _compute_variable_enum_order(pred_map, varList)
    #print [x.idName for x in varList]
    # 3. calc variable domains
    test_dict = {}
    for var_node in varList:
        #print "DEBUG: searching for", var_node.idName,"constraint"
        test_set = None 
        for pred in pred_map:
            (time, vars, must_be_computed_first) = pred_map[pred]
            #print (time, vars, must_be_computed_first, pred)
            #print [x.idName for x in test_dict.keys()], must_be_computed_first
            #print "DEBUG:  vars:",vars, "contraint by", pretty_print(pred)
            # Avoid interference between bound variables: check _find_constraint_vars
            # This is less powerful, but correct
            if time<TOO_MANY_ITEMS and var_node.idName in vars:
                # at least on predicate of this conjunction can easiely be used
                # to compute a testset. The exact solution musst contain all 
                # or less elements than test_set
                if test_set is None:
                    try:
                        assert isinstance(pred, Predicate)
                        # This predicate needs the computation of an other variable
                        # in test_dict first. e.g x={(0,1),(2,3)}(y).
                        # If step 2 was successful, the values of the needed bound vars
                        # are already computed for some pred in pred_map
                        # This may NOT be this pred!
                        if not must_be_computed_first==[]:
                            # all already computed variables have to be considered to
                            # find a domain for 'var_node'. must_be_computed_first contains
                            # only variables with direct constraints e.g 'var_node=f(x)' but not 'x=y+1'
                            already_computed_var_List = [key for key in varList if key in test_dict]
                            # check if all informations are present to use 'pred' to compute domain of 'var_node'
                            names_string = []
                            #for x in already_computed_var_List:
                            #    assert isinstance(x, AIdentifierExpression)
                            #    name = x.idName
                            #    assert isinstance(name, str)
                            #    names_string.append(name)
                            names_string = [x.idName for x in already_computed_var_List]
                            for mbcf in must_be_computed_first:
                                if mbcf not in names_string:
                                    raise PredicateDoesNotMatchException()
                            assert not test_dict=={}
                            # generate partial solution: all domain combinations of a subset of bound vars
                            a_cross_product_iterator = _cross_product_iterator(already_computed_var_List, test_dict, {}) 
                            # use partial solution to gen testset
                            test_set = frozenset([])
                            env.push_new_frame(varList)
                            #print "XXX:", pretty_print(pred)
                            # TODO: throwing away the partial solution makes no sense,
                            # because it will be computed anyway. Refactor this code
                            # by computing the cross product after every iteration
                            for part_sol in a_cross_product_iterator:
                                for v in already_computed_var_List:
                                    name  = v.idName
                                    value = part_sol[name] 
                                    env.set_value(name, value)
                                    try:
                                        part_testset = _compute_test_set(pred, env, var_node)
                                    except ValueNotInDomainException:
                                        continue
                                    test_set = test_set.union(part_testset)
                            env.pop_frame()
                            break
                        else:
                            # no constrains by other vars. just use this sub-predicate to 
                            # compute the domain of the current variable
                            test_set = _compute_test_set(pred, env, var_node)
                            break
                    except PredicateDoesNotMatchException: 
                        #.eg constraining y instead of x, or using unimplemented cases
                        test_set = None
        if test_set is None:
            # there is no predicate to constrain this variable in finite time. FAIL!
            if PRINT_WARNINGS:
                print "\033[1m\033[91mWARNING\033[00m: Quick enumeration fails. Unable to constrain domain of %s" % var_node.idName
            raise SpecialCaseEnumerationFailedException()
        # assigning constraint set or none
        test_dict[var_node] = test_set
                    
    # check if a solution has been found for every bound variable
    solution_found = True
    for var_node in varList:
        if test_dict[var_node] is None or test_dict[var_node]==frozenset([]):
            if PRINT_WARNINGS:
                print "\033[1m\033[91mWARNING\033[00m: Unable to constrain bound variable: %s" % var_node.idName
            solution_found = False
            
    # use this solution and return a generator        
    if solution_found:          
        a_cross_product_iterator = _cross_product_iterator(varList, test_dict, {})
        iterator = _solution_generator(a_cross_product_iterator, predicate, env, varList)
        return iterator
    else:
        raise SpecialCaseEnumerationFailedException()



# this generator yield every combination of values for some variables with finite domains
# partial_cross_product is a accumulator which is reseted to the empty dict {} at every call
def _cross_product_iterator(varList, domain_dict, partial_cross_product):
    # 1. get next variable and non-empty finite domain
    idNode = varList[0]
    aSet = domain_dict[idNode]
    assert not aSet==frozenset([])
    assert isinstance(idNode, AIdentifierExpression)
    var_name = idNode.idName
    #print "DEBUG: enum: %s" % var_name
    # 2. compute partial cross product for every element/value 
    for element in aSet:
        partial_cross_product[var_name] = element
        # case 2.1: if it was the last variable, the "cross product-element" has been computed
        if len(varList)==1:
            solution = partial_cross_product.copy()
            yield solution
        # case 2.2: more variables to handel
        else:
            for solution in _cross_product_iterator(varList[1:], domain_dict, partial_cross_product):
                # give solution to highest level of recursion
                yield solution


# this generator yields all combinations of values which satisfy a given predicate
def _solution_generator(a_cross_product_iterator, predicate, env, varList):
    for maybe_solution in a_cross_product_iterator:
        if _is_solution(predicate, env, varList, solution=maybe_solution):
            solution = maybe_solution.copy()
            yield solution


# computed the order of variables
# TODO:only correct if abstract interpretation computed predicate eval-time correct
#
# e.g.
# pred_map = {<ast_nodes.AEqualPredicate instance at 0x10e245128>: (19, ['z'], ['x', 'y']), <ast_nodes.AMemberPredicate instance at 0x10e2b84d0>: (11, ['x', 'y'], [])}
# varList = [<ast_nodes.AIdentifierExpression instance at 0x10e2b8758>, <ast_nodes.AIdentifierExpression instance at 0x10e2b8d40>, <ast_nodes.AIdentifierExpression instance at 0x10e2b87a0>]
#
def _compute_variable_enum_order(pred_map, varList):
    # 0. init of data structures 
    result = []
    graph  = {}
    # 1. construct directed graph: 
    # nodes: variables
    # edges: variable has to be enumerated first
    # node-degree zero: variable can be enumerated
    for varNode in varList:
        name = varNode.idName
        # search for all variables to be enumerated before 'name'
        listOfidNames = frozenset([]) # set-type to avoid more than one edge between two nodes
        for entry in pred_map.values():
            if name in entry[1]:
               # XXX: intersection instead of union 
               # e.g "x=z+1 & x=y+1 & x=5" in this case x can be enumerated without knowing y or z!
               # But it is importend if predicates are inf. computable. 
               # e.g. "x=y & x={a lot of time needed} & y:{1,2,...43}" here y has to be computed first
               var_list = frozenset(entry[2])
               for string in var_list:
                   assert isinstance(string, str)
               listOfidNames.union(var_list) # edges
        # all variables found: add edges to this nodes:
        if USE_RPYTHON_CODE:
            graph[name] = listOfidNames.lst
        else:
            graph[name] = list(listOfidNames)

    # 2. topologic sorting
    removed = [] # list of removed nodes (implicit list of removed edges)
    while not graph=={}:
        change = False
        for varNode in varList:
            # check if node degree is zero
            name = varNode.idName
            assert isinstance(name, str)
            try:
                constraint_by = graph[name]
            except KeyError: # done/removed in prev. iteration 
                continue # skip and handle next var in varList
            edges = [x for x in constraint_by if x not in removed]
            if edges==[]:
                assert isinstance(varNode, Node)
                result.append(varNode)
                removed.append(name) #TODO:string and w_object, not rpython, maybe from pred_map
                del graph[name]
                change = True
        if not change:
            if PRINT_WARNINGS:
                print "\033[1m\033[91mError\033[00m: Unable to compute topologic order of bound vars %s" % [x.idName for x in varList]
                raise Exception()
    
    # 3. variable order found. return result
    assert len(result)==len(varList)
    #print "variable enumeration order: ", [x.idName for x in result]
    return result
            

# TODO: support more than one variable
# FIMXE: doesnt finds finite-time computable sub-predicates. 
#        e.g P0="P00(x) or P01(y)" with P01 infinite
# input: P0 & P1 & ...PN or in special cases one predicate (like x=42)
# output(example): mapping {P0->(time0, vars0, compute_first0), , P1->(time1, vars1),... PN->(timeN, varsN, compute_firstN)}        
def _categorize_predicates(predicate, env, varList):
    if isinstance(predicate, AConjunctPredicate):
        map0 = _categorize_predicates(predicate.children[0], env, varList)
        map1 = _categorize_predicates(predicate.children[1], env, varList)
        map0.update(map1)
        return map0
    else:
       time = estimate_computation_time(predicate, env)
       constraintVarsTuple = _find_constraint_vars(predicate, env, varList)   
       return {predicate: (time, constraintVarsTuple.constraint_vars, constraintVarsTuple.vars_need_to_be_set_first)}

# Wrapper for RPython to avoid multiple return values    
class ConstraintVarsTuple():
    def __init__(self, constraint_vars, vars_need_to_be_set_first):
        self.constraint_vars = constraint_vars
        self.vars_need_to_be_set_first = vars_need_to_be_set_first
        

# Input predicate is always a sub-predicate of a conjunction predicate or a single predicate.
# This helper may only be used to find test_set(constraint domain) generation candidates.
# The test sets (constraint domains of bound vars with possible false elements) are
# computed in a second step (not in this function!) because of the predicate-selection process. 
# return: list of variable names_string, constraint by this predicated AND with possible test_set gen
# using a wrapper object ConstraintVarsTuple.
# AND a list of variable names_string (second return value) which need a value before the computation
# e.g. "x:{1,2,3} & y=x+1" here x is constraint by {1,2,3} and y is constraint by x 
#
# WARNING: before modifying this part, be sure "_compute_test_set" can handle it!  
def _find_constraint_vars(predicate, env, varList):
    # (1) Base case. This case should only be matched by a recursive call of _find_constraint_vars.
    # otherwise it could produce wrong results!     
    if isinstance(predicate, AIdentifierExpression):
        lst = [predicate.idName]
        return ConstraintVarsTuple(lst, []) #predicate constrain idName and no computation constraint by other variables
    elif isinstance(predicate, ACoupleExpression):
        varTuple0 = _find_constraint_vars(predicate.children[0], env, varList)
        varTuple1 = _find_constraint_vars(predicate.children[1], env, varList)
        
        lst = varTuple0.constraint_vars # remove double entries
        for e in varTuple1.constraint_vars:
             if e not in lst:
                 assert isinstance(e, str)
                 lst.append(e)
        #lst  =  list(set(lst0 + lst1)) 
        return ConstraintVarsTuple(lst, []) #predicate constrain idName and no computation constraint by other variables
        
    # (2) implemented predicates (by _compute_test_set)
    # WARNING: never add a case if the method "_compute_test_set" can not handle it.
    # This may introduce a Bug!
    if isinstance(predicate, AMemberPredicate):
        varTuple0 = _find_constraint_vars(predicate.children[0], env, varList)
        constraint_by_vars = find_constraining_var_nodes(predicate.children[1], varList)
        #names_string = []
        #for x in constraint_by_vars:
        #        assert isinstance(x, AIdentifierExpression)
        #        assert isinstance(x.idName, str)
        #        name = x.idName
        #        assert isinstance(name, str)
        #        names_string.append(name)
        #for s in names_string:
        #    assert isinstance(s, str)
        names_string = [x.idName for x in constraint_by_vars]
        return ConstraintVarsTuple(varTuple0.constraint_vars, names_string)
    elif isinstance(predicate, AEqualPredicate):
        if isinstance(predicate.children[0], AIdentifierExpression):
            test_set_var = [predicate.children[0].idName]
            constraint_by_vars = find_constraining_var_nodes(predicate.children[1], varList)
            #names_string = []
            #for x in constraint_by_vars:
            #    assert isinstance(x, AIdentifierExpression)
            #    assert isinstance(x.idName, str)
            #    name = x.idName
            #    assert isinstance(name, str)
            #    names_string.append(name)
            #for s in names_string:
            #    assert isinstance(s, str)
            names_string = [x.idName for x in constraint_by_vars]
            return ConstraintVarsTuple(test_set_var, names_string)
        elif isinstance(predicate.children[1], AIdentifierExpression):
            test_set_var = [predicate.children[1].idName]
            constraint_by_vars = find_constraining_var_nodes(predicate.children[0], varList)
            #names_string = []
            #for x in constraint_by_vars:
            #    assert isinstance(x, AIdentifierExpression)
            #    assert isinstance(x.idName, str)
            #    name = x.idName
            #    assert isinstance(name, str)
            #    names_string.append(name)
            #for s in names_string:
            #    assert isinstance(s, str)
            names_string = [x.idName for x in constraint_by_vars]
            return ConstraintVarsTuple(test_set_var, names_string)
        elif isinstance(predicate.children[0], ACoupleExpression):
            # FIXME not symmetrical! a|->b = (1,2) found but not (1,2)=a|->b
            varTuple0 = _find_constraint_vars(predicate.children[0], env, varList)
            constraint_by_vars = find_constraining_var_nodes(predicate.children[1], varList)
            #names_string = []
            #for x in constraint_by_vars:
            #    assert isinstance(x, AIdentifierExpression)
            #    assert isinstance(x.idName, str)
            #    name = x.idName
            #    assert isinstance(name, str)
            #    names_string.append(name)
            #for s in names_string:
            #    assert isinstance(s, str)
            names_string = [x.idName for x in constraint_by_vars]
            return ConstraintVarsTuple(varTuple0.constraint_vars, names_string)
            
    # if the subpredicate consists of a conjunction or disjunction, it 
    # constraints a var x if x is constraint by one sub-predicate,
    # because this sub-predicate may be a candidate for test-set generation
    elif isinstance(predicate, ADisjunctPredicate) or isinstance(predicate, AConjunctPredicate):
        varTuple0 = _find_constraint_vars(predicate.children[0], env, varList)
        varTuple1 = _find_constraint_vars(predicate.children[1], env, varList) 
        test_set_var = varTuple0.constraint_vars
        for e in varTuple1.constraint_vars:
            if e not in test_set_var:
                test_set_var.append(e)
        c_set_var =  varTuple0.vars_need_to_be_set_first
        for e in varTuple1.vars_need_to_be_set_first:
            if e not in c_set_var:
                c_set_var.append(e)  
        # remove double entries 
        #test_set_var = list(set(lst0 + lst1)) # remove double entries 
        #c_set_var =  list(set(cvarlst0 + cvarlst1)) # remove double entries 
        return ConstraintVarsTuple(test_set_var, c_set_var)
    # No implemented case found. Maybe there are constraints, but pyB doesnt find them
    # TODO: Implement more cases, but only that on handeld in _compute_test_set
    return ConstraintVarsTuple([], [])


# TODO: be sure this cases have no side effect
# XXX: not all cases implemented (maybe not possible)
def _compute_test_set(node, env, var_node):
    if USE_RPYTHON_CODE:
        from rpython_interp import interpret
    else:
        from interp import interpret
    if isinstance(node, AEqualPredicate):
        # if elements of the set are equal to some expression, a set has to be generated 
        # e.g {x| x:NAT & x=42}  results in {42}
        if isinstance(node.children[0], AIdentifierExpression) and node.children[0].idName==var_node.idName:
            value = interpret(node.children[1], env)
            # FIXME: TypeError: unhashable instance e.g. run C578.EML.014/CF_CV_1
            # somehow a set type is returned!
            if isinstance(value, SymbolicSet):
                return frozenset([value.enumerate_all()])
            return frozenset([value])
        if isinstance(node.children[1], AIdentifierExpression) and node.children[1].idName==var_node.idName:
            value = interpret(node.children[0], env)
            if isinstance(value, SymbolicSet):
                return frozenset([value.enumerate_all()])
            return frozenset([value])
        if isinstance(node.children[0], ACoupleExpression):
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
                # FIXME: no caching! Recomputation at every call
                aset = interpret(node.children[1], env)
                #print 
                #assert isinstance(set, frozenset)
                # 2.3. return correct part of the set corresponding to position of
                # searched variable inside the tuple on the left side
                return frozenset([remove_tuples(aset)[index]])
    elif isinstance(node, AMemberPredicate):
        # belong-case 1: left side is just an id
        if isinstance(node.children[0], AIdentifierExpression) and node.children[0].idName==var_node.idName: 
            aset = interpret(node.children[1], env)
            # e.g. x:{1,2,3} or x:S
            # return finite set on the left as test_set/constraint domain
            # FIXME: isinstance('x', frozenset) -> find enumeration order!
            if not isinstance(aset, frozenset):
                return aset.enumerate_all() # explicit domain needed
            return aset
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
                aset = interpret(node.children[1], env)
                # FIXME: C578.EML.014/R_PLACE_MAINTENANCE_2 returns SymbolicUnionSet
                assert isinstance(aset, frozenset)
                # 2.3. return correct part of the set corresponding to position of
                # searched variable inside the tuple on the left side
                return frozenset([remove_tuples(t)[index] for t in aset])
    # this is only called because both branches (node.childern[0] and node.childern[1])
    # of the disjunction are computable in finite time. (as analysed by _categorize_predicates)
    elif isinstance(node, ADisjunctPredicate):
        set0 = _compute_test_set(node.children[0], env, var_node)
        set1 = _compute_test_set(node.children[1], env, var_node)
        return set0.union(set1)
    elif isinstance(node, AConjunctPredicate):
        try:
            set0 = _compute_test_set(node.children[0], env, var_node)
            try:
                set1 = _compute_test_set(node.children[1], env, var_node)
                return set0.union(set1)
            except PredicateDoesNotMatchException:
                return set0
        except PredicateDoesNotMatchException:
            set1 = _compute_test_set(node.children[1], env, var_node)
            return set1   
    else:
        raise PredicateDoesNotMatchException()


# check if solution satisfies predicate 
# returns boolean
def _is_solution(pred, env, varList, solution):
    if USE_RPYTHON_CODE:
        from rpython_interp import interpret
    else:
        from interp import interpret
    
    env.push_new_frame(varList) #avoid side effect
    for key in solution:
        value = solution[key]
        #print "set",key,"to",value
        env.set_value(key, value)
    try:
        res = interpret(pred, env)
        if USE_RPYTHON_CODE:
            result = res.bvalue
        else:
            result = res
    except ValueNotInDomainException: # function app with wrong value
        result = False
    env.pop_frame() # leave frame
    return result
    

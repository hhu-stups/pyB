# This is NOT a constraint solver. It is a wrapper to enable usage of a constraint solver
# pyB imports:
from abstract_interpretation import estimate_computation_time
from ast_nodes import *
from bexceptions import ConstraintNotImplementedException, ValueNotInDomainException
from config import TOO_MANY_ITEMS, USE_PYB_CONSTRAINT_SOLVER, PRINT_WARNINGS, USE_RPYTHON_CODE
from enumeration import gen_all_values, enum_all_values_by_type
from external_constraintsolver import compute_using_external_solver
from helpers import remove_tuples, couple_tree_to_conj_list, find_constraining_var_nodes, set_to_list
from pretty_printer import pretty_print
from symbolic_sets import SymbolicSet

if USE_RPYTHON_CODE:
     from rpython_b_objmodel import frozenset


class PredicateDoesNotMatchException(Exception):
    pass # TODO: refactor me

class SpecialCaseEnumerationFailedException(Exception):
    pass

# Wrapper for RPython translation to avoid multiple return values 
# of helper function _find_constrained_vars. 
# Example usage: see comments in _find_constrained_vars
class Constraint():
    def __init__(self, constrained_vars, vars_need_to_be_set_first):
        self.constrained_vars = constrained_vars # vars constrained by a predicate
        self.vars_need_to_be_set_first = vars_need_to_be_set_first # vars to be computed first
    
    def set_predicate(self, predicate):
        self.predicate = predicate # predicate which belongs to this constraint (only a unused backlink)
        
    def set_time(self, time):
        self.time = time # time needed to use this constraint (threshold in config.py)


        
# assumption: the variables of varList are typed and be constrained by the predicate. 
# If predicate is None (no constraint), all values of the variable type is returned.
# After this function returns a generator, every solution-candidate musst be checked! 
# This function may be generate false values, but does not omit correct ones.
# It filters values which are obviously wrong.
# i.e no values are missing.
# 
# predicate:    predicate which may (or may not) constrain all variables
# env:          environment. possible lookup of values (other scopes)
# varList:      variables x1 .. xN need to be constrained 
#
# yields a dict {x1:value0, ... ,xN:valueM}
# TODO: move checking inside this function i.e. generate NO FALSE values
# TODO: maybe a new argument containing a partial computation (e.g. on of many vars with 
#       with domain constraint) would be a nice refactoring to solve get_item in symb. comp. set
def compute_constrained_domains(predicate, env, varList):
    assert isinstance(predicate, Predicate)
    assert isinstance(varList, list)
    for idNode in varList:
        assert isinstance(idNode, AIdentifierExpression)      
    # check which kind of strategy: 3 cases

    # case 1: Using the PyB constraint solver    
    # check if a solution-set (variable domain) is computable without a external contraint solver
    if USE_PYB_CONSTRAINT_SOLVER:
        try:
            generator = _compute_using_pyB_solver(predicate, env, varList)
            for d in generator:
                yield d
            raise StopIteration()
        except SpecialCaseEnumerationFailedException:
            print "\033[1m\033[91mDEBUG\033[00m: PyB constraint solver failed. Case not implemented"
            raise StopIteration()

    
    # case 2: Using a external constraint solver
    # TODO: Handle OverflowError, print Error message and go on
    try:
        if USE_RPYTHON_CODE: # Using external constraint solver not supported by RPython yet
            raise ImportError()
        if PRINT_WARNINGS:
            print "\033[1m\033[91mWARNING\033[00m: External constraint solver called. Caused by: %s" % pretty_print(predicate) 
        iterator = compute_using_external_solver(predicate, env, varList)
        # constraint solving succeed. 
        for d in iterator:
            yield d
        raise StopIteration()
    # case 3: Using brute force enumeration 
    except (ConstraintNotImplementedException, ImportError):
        if PRINT_WARNINGS:
            print "\033[1m\033[91mWARNING\033[00m: Brute force enumeration caused by: %s! enumerating: %s" % (pretty_print(predicate), [v.idName for v in varList])
        # TODO: maybe case 2 was able to constrain the domain of some variables but not all
        # this computation is thrown away in this step. This makes no senese. Fix it!
        # constraint solving failed, enumerate all values (may cause a pyB fail or a timeout)
        generator = gen_all_values(env, varList)
        for d in generator:
            yield d
        raise StopIteration()



# returns a generator or None if fail (e.g. special case not implemented)
# the generator returns a dict which maps id names to possible values of this variables.   
# Todo: generate constraint set by using all "fast computable" predicates
# Todo: call generator to return solution      
def _compute_using_pyB_solver(predicate, env, varList):
    # 1. score predicates
    pred_map = _analyze_predicates(predicate, env, varList) # {Predicate --> Constraint}
    assert not len(pred_map)==0 
    
    # 2. find possible variable enum order. 
    # variable(-domains) not constraint by others will be enumerated first.
    varList  = _compute_variable_enum_order(pred_map, varList)
    
    # 3. calc variable domains. Goal: mapping from vars to domain sets
    test_dict = {}
    for var_node in varList:
        domain = None 
        for pred in pred_map:
            assert isinstance(pred, Predicate)
            constraint = pred_map[pred]
            time = constraint.time
            vars = constraint.constrained_vars
            must_be_computed_first = constraint.vars_need_to_be_set_first
            takes_too_much_time     = time>=TOO_MANY_ITEMS
            does_not_constrain_var = var_node.idName not in vars
            # Only consider constraints which can be computed fast 
            # and which constraint this variable. This checks all arcs from the
            # node var_node in the constraint-graph which can be evaluated with low costs
            if takes_too_much_time or does_not_constrain_var:
                continue
                
            # This constraint can easiely be used to compute a constraint domain.
            # The exact solution musst contain all or less elements than "sub_domain"
            try:
                is_unary_constraint = must_be_computed_first==[]
                if is_unary_constraint:
                    # no constrains by other vars. just use this sub-predicate to 
                    # compute the domain of the current variable
                    sub_domain = _compute_test_set(pred, env, var_node)
                # This is a binary or n-ary constraint.
                # This predicate needs the computation of an other variable
                # in test_dict first. e.g x={(0,1),(2,3)}(y).
                # If var order computation was successful, the values of the 
                # needed bound vars are already computed for some pred in pred_map
                # This may NOT be this pred (in this iteration)!
                else:
                    # all already computed variables have to be considered to
                    # find a domain for 'var_node'. must_be_computed_first contains
                    # only variables with direct constraints e.g 'var_node=f(x)' but not 'x=y+1'
                    already_computed_var_List = [key for key in varList if key in test_dict]
                    # check if all informations are present to use 'pred' to compute domain of 'var_node'
                    names_string = []
                    names_string = [x.idName for x in already_computed_var_List]
                    for mbcf in must_be_computed_first:
                        if mbcf not in names_string:
                            raise PredicateDoesNotMatchException()
                    assert not len(test_dict)==0
                    # generate partial solution: all domain combinations of a subset of bound vars
                    a_cross_product_iterator = _cross_product_iterator(already_computed_var_List, test_dict, {}) 
                    # use partial solution to gen testset
                    sub_domain = frozenset([])
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
                            sub_domain = sub_domain.union(part_testset)
                    env.pop_frame()
            except PredicateDoesNotMatchException: 
                #.eg constraining y instead of x, or using unimplemented cases
                sub_domain = None
                
            # first constraint successfully used
            if domain is None:
                domain = sub_domain
            # the domain was already constraint in an other iteration.
            # use this sub_domain to constrain it even more.
            else:
                domain = domain.intersection(sub_domain)
                                       
        if domain is None:
            # there is no predicate to constrain this variable in finite time. 
            # Use all possible elements of the variable type
            if PRINT_WARNINGS:
                print "\033[1m\033[91mWARNING\033[00m: Quick enumeration warning: Unable to constrain domain of %s" % var_node.idName
            all_values = enum_all_values_by_type(env, var_node)
            domain = frozenset(all_values)

        # assigning constraint set or none
        test_dict[var_node] = domain
                    
    # check if a solution has been found for every bound variable
    solution_found = True
    for var_node in varList:
        domain = test_dict[var_node]
        assert domain is not None
        if domain==frozenset([]):
            if PRINT_WARNINGS:
                print "\033[1m\033[91mWARNING\033[00m: Empty solution. Unable to constrain bound variable: %s" % var_node.idName
            solution_found = False
            
    # use this solution and return a generator        
    if solution_found:          
        a_cross_product_iterator = _cross_product_iterator(varList, test_dict, {})
        iterator = _solution_generator(a_cross_product_iterator, predicate, env, varList)
        return iterator
    else:
        raise SpecialCaseEnumerationFailedException()


# TODO: support more than one variable
# FIMXE: doesnt finds finite-time computable sub-predicates. 
#        e.g P0="P00(x) or P01(y)" with P01 infinite
# input: predicate = P0 & P1 & ...PN or in special cases one predicate (like x=42)
# output(example): mapping {P0->(time0, vars0, compute_first0), , P1->(time1, vars1),... PN->(timeN, varsN, compute_firstN)}        
def _analyze_predicates(predicate, env, varList):
    if isinstance(predicate, AConjunctPredicate):
        map0 = _analyze_predicates(predicate.children[0], env, varList)
        map1 = _analyze_predicates(predicate.children[1], env, varList)
        map0.update(map1)
        return map0
    else:
        # analyse
        time = estimate_computation_time(predicate, env)
        constraint = _find_constrained_vars(predicate, env, varList)
        # return result
        constraint.set_time(time)
        constraint.set_predicate(predicate)     
        return {predicate: constraint}

# this generator yield every combination of values for some variables with finite domains
# partial_cross_product is a accumulator which is reseted to the empty dict {} at every call
# This is the labeling procedure. It uses preconstrained domains (only unary constraints)
def _cross_product_iterator(varList, domain_dict, partial_cross_product):
    # 1. get next variable and non-empty finite domain
    idNode = varList[0]
    aSet = domain_dict[idNode]
    assert not aSet==frozenset([])
    assert isinstance(idNode, AIdentifierExpression)
    var_name = idNode.idName

    # 2. compute partial cross product for every element/value 
    for element in aSet:
        partial_cross_product[var_name] = element
        # case 2.1: if it was the last variable, the "cross product-element" has been computed
        if len(varList)==1:
            solution = partial_cross_product.copy()
            yield solution
        # case 2.2: more variables to handle
        else:
            for solution in _cross_product_iterator(varList[1:], domain_dict, partial_cross_product):
                # give solution to highest level of recursion
                yield solution


# this generator yields all combinations of values which satisfy a given predicate
def _solution_generator(a_cross_product_iterator, predicate, env, varList):
    for maybe_solution_dict in a_cross_product_iterator:
        if _is_solution(predicate, env, varList, solution=maybe_solution_dict):
            solution = maybe_solution_dict.copy()
            yield solution


# compute the ordering of the variables. This is a trick to handle binary constraints as uniary 
# TODO:only correct if abstract interpretation computed predicate eval-time correct
#
# example:
# pred_map = { AEqualPredicate: Constraint(19, ['z'], ['x', 'y']), AMemberPredicate: Constraint(11, ['x', 'y'], [])}
# varList = [AIdentifierExpression, AIdentifierExpression, AIdentifierExpression]
#
def _compute_variable_enum_order(pred_map, varList):
    # 0. init of data structures 
    result = []
    graph  = {}
    constraint_list = pred_map.values()
    # 1. construct directed graph: 
    # nodes: variable name of type string
    # edges: variable has to be enumerated first
    # node-degree zero: variable can be enumerated
    for varNode in varList:
        name = varNode.idName
        assert isinstance(name, str) 
        # search for all variables to be enumerated before 'name'
        listOfidNames = []
        for constraint in constraint_list:
            if name in constraint.constrained_vars:
               # XXX: intersection instead of union 
               # e.g "x=z+1 & x=y+1 & x=5" in this case x can be enumerated without knowing y or z!
               # But it is importend if predicates are inf. computable. 
               # e.g. "x=y & x={a lot of time needed} & y:{1,2,...43}" here y has to be computed first
               for other in constraint.vars_need_to_be_set_first:
                   if not other==name and not other in listOfidNames:
                        assert isinstance(other, str) 
                        # set edge from name to other
                        listOfidNames.append(other)
        # all variables found: add edges to this nodes:
        graph[name] = listOfidNames

    # 2. topologic sorting
    removed = [] # list of removed nodes (implicit list of removed edges)
    while not len(graph)==0:
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
                removed.append(name)
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
            


# Input predicate is a sub-predicate of a conjunction predicate or a single predicate.
# This helper may only be used to find domain generation candidates.
# The test sets (=constrained domains of bound vars with possible false elements) are
# computed in a second step (not in this function!) because of the predicate-selection process. 
#
# return: a Constraint with: constrained_vars and vars_need_to_be_set_first
# constrained_vars: list of var names constrained by this predicate 
# vars_need_to_be_set_first: list of var names which need a value before the evaluation of this predicate is possible.
#
#
#
# example: 
# Predicate P1: f(x)=y  and P: {(x,y)| P1 .... Pn }
# constrained_vars = [idNode(x)]
# vars_need_to_be_set_first = [idNode(y)]
# example:
# Predicate P1: a*a+b*b=c*c and P: in {(a,b,c)| P1 .... Pn }
# constrained_vars = [idNode(c)]
# vars_need_to_be_set_first = [idNode(a), idNode(b)]
#
#
# WARNING: before modifying this part, be sure "_compute_test_set" can handle it!  
def _find_constrained_vars(predicate, env, varList):
    # (1) Base case. This case should only be matched by a recursive call of _find_constrained_vars.
    # otherwise it could produce wrong results!     
    if isinstance(predicate, AIdentifierExpression):
        lst = [predicate.idName]
        return Constraint(lst, []) #predicate constrain idName and no computation constraint by other variables
    elif isinstance(predicate, ACoupleExpression):
        varTuple0 = _find_constrained_vars(predicate.children[0], env, varList)
        varTuple1 = _find_constrained_vars(predicate.children[1], env, varList)
        
        lst = varTuple0.constrained_vars # remove double entries
        for e in varTuple1.constrained_vars:
             if e not in lst:
                 assert isinstance(e, str)
                 lst.append(e)
        #lst  =  list(set(lst0 + lst1)) 
        return Constraint(lst, []) #predicate constrain idName and no computation constraint by other variables
        
    # (2) implemented predicates (by _compute_test_set)
    # WARNING: never add a case if the method "_compute_test_set" can not handle it.
    # This may introduce a Bug!
    if isinstance(predicate, AMemberPredicate):
        varTuple0 = _find_constrained_vars(predicate.children[0], env, varList)
        constraint_by_vars = find_constraining_var_nodes(predicate.children[1], varList)
        names = [x.idName for x in constraint_by_vars]
        return Constraint(varTuple0.constrained_vars, names)
    elif isinstance(predicate, AEqualPredicate):
        if isinstance(predicate.children[0], AIdentifierExpression):
            test_set_var = [predicate.children[0].idName]
            constraint_by_vars = find_constraining_var_nodes(predicate.children[1], varList)
            names = [x.idName for x in constraint_by_vars]
            return Constraint(test_set_var, names)
        elif isinstance(predicate.children[1], AIdentifierExpression):
            test_set_var = [predicate.children[1].idName]
            constraint_by_vars = find_constraining_var_nodes(predicate.children[0], varList)
            names = [x.idName for x in constraint_by_vars]
            return Constraint(test_set_var, names)
        elif isinstance(predicate.children[0], ACoupleExpression):
            # FIXME not symmetrical! a|->b = (1,2) found but not (1,2)=a|->b
            varTuple0 = _find_constrained_vars(predicate.children[0], env, varList)
            constraint_by_vars = find_constraining_var_nodes(predicate.children[1], varList)
            names = [x.idName for x in constraint_by_vars]
            return Constraint(varTuple0.constrained_vars, names)
            
    # if the subpredicate consists of a conjunction or disjunction, it 
    # constraints a var x if x is constraint by one sub-predicate,
    # because this sub-predicate may be a candidate for test-set generation
    elif isinstance(predicate, ADisjunctPredicate) or isinstance(predicate, AConjunctPredicate):
        varTuple0 = _find_constrained_vars(predicate.children[0], env, varList)
        varTuple1 = _find_constrained_vars(predicate.children[1], env, varList) 
        test_set_var = varTuple0.constrained_vars
        for e in varTuple1.constrained_vars:
            if e not in test_set_var:
                test_set_var.append(e)
        c_set_var =  varTuple0.vars_need_to_be_set_first
        for e in varTuple1.vars_need_to_be_set_first:
            if e not in c_set_var:
                c_set_var.append(e)  
        # remove double entries 
        #test_set_var = list(set(lst0 + lst1)) # remove double entries 
        #c_set_var =  list(set(cvarlst0 + cvarlst1)) # remove double entries 
        return Constraint(test_set_var, c_set_var)
    # No implemented case found. Maybe there are constraints, but pyB doesnt find them
    # TODO: Implement more cases, but only that on handeld in _compute_test_set
    return Constraint([], [])


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
    # of the disjunction are computable in finite time. (as analysed by _analyze_predicates)
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
    

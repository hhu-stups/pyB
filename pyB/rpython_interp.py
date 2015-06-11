from ast_nodes import *
from bexceptions import ValueNotInDomainException, INITNotPossibleException
from config import MAX_INIT, VERBOSE
#from constrainsolver import calc_possible_solutions
#from enumeration import get_image
from helpers import flatten, double_element_check, find_assignd_vars, print_ast, all_ids_known, find_var_nodes, conj_tree_to_conj_list
#from symbolic_sets import *
from typing import type_check_predicate, type_check_expression


# evals a expression of unkonwn type. Returns wrapped data (see rpython_b_objmodel.py)
# example x:S (called by member node). x can be of any type.  
def eval_wtype_expression(node, env):
    pass #TODO: change environment. Implement wtype support

# That the result of node evaluation is an integer,  must be ensured BY THE CALLER!
# 
# For example in "x + y * z" the '*' is a multiplication, if this expression has passed the 
# type checker. A Bug inside the type checker will cause a bug here!
# The function always returns an integer, to enable RPython-translation to C
def eval_int_expression(node, env):
    if isinstance(node, AIntegerExpression):
        # TODO: add flag in config.py to enable switch to long integer here
        return node.intValue
    #elif isinstance(node, AMinExpression):
    #    aSet = interpret(node.children[0], env)
    #    return min(list(aSet))
    #elif isinstance(node, AMaxExpression):
    #    aSet = interpret(node.children[0], env)
    #    return max(list(aSet))
    elif isinstance(node, AAddExpression):
        expr1 = eval_int_expression(node.get(0), env)
        expr2 = eval_int_expression(node.get(1), env)
        return expr1 + expr2
    elif isinstance(node, AMinusOrSetSubtractExpression):
        expr1 = eval_int_expression(node.get(0), env)
        expr2 = eval_int_expression(node.get(1), env)
        return expr1 - expr2
    elif isinstance(node, AMultOrCartExpression):
        expr1 = eval_int_expression(node.get(0), env)
        expr2 = eval_int_expression(node.get(1), env)
        return expr1 * expr2
    elif isinstance(node, ADivExpression):
        expr1 = eval_int_expression(node.get(0), env)
        expr2 = eval_int_expression(node.get(1), env)
        return expr1 // expr2
    elif isinstance(node, AModuloExpression):
        expr1 = eval_int_expression(node.get(0), env)
        expr2 = eval_int_expression(node.get(1), env)
        assert expr2 > 0
        return expr1 % expr2
    elif isinstance(node, APowerOfExpression):
        basis = eval_int_expression(node.get(0), env)
        exp = eval_int_expression(node.get(1), env)
        # not RPython: result = basis ** exp
        assert exp >=0
        result = 1
        for i in range(exp):
            result *= basis
        return result
        """
    elif isinstance(node, AGeneralSumExpression):
        sum_ = 0
        # new scope
        varList = node.children[:-2]
        env.push_new_frame(varList)
        pred = node.children[-2]
        expr = node.children[-1]
        domain_generator = calc_possible_solutions(pred, env, varList, interpret)
        for entry in domain_generator:
            for name in [x.idName for x in varList]:
                value = entry[name]
                env.set_value(name, value)
            try:
                if interpret(pred, env):  # test          
                    sum_ += eval_int_expression(expr, env)
            except ValueNotInDomainException:
                continue
        env.pop_frame() # exit scope
        return sum_
    elif isinstance(node, AGeneralProductExpression):
        prod_ = 1
        # new scope
        varList = node.children[:-2]
        env.push_new_frame(varList)
        pred = node.children[-2]
        expr = node.children[-1]
        domain_generator = calc_possible_solutions(pred, env, varList, interpret)
        for entry in domain_generator:
            for name in [x.idName for x in varList]:
                value = entry[name]
                env.set_value(name, value)
            try:
                if interpret(pred, env):  # test           
                    prod_ *= eval_int_expression(expr, env)
            except ValueNotInDomainException:
                continue
        env.pop_frame() # exit scope
        return prod_
    elif isinstance(node, AUnaryMinusExpression):
        result = eval_int_expression(node.children[0], env)
        return result.__neg__()
    elif isinstance(node, AMinIntExpression):
        return env._min_int
    elif isinstance(node, AMaxIntExpression):
        return env._max_int
    elif isinstance(node, ACardExpression):
        aSet = interpret(node.children[0], env)
        return len(aSet)
    elif isinstance(node, ASizeExpression):
        sequence = interpret(node.children[0], env)
        return len(sequence)
    elif isinstance(node, AFunctionExpression):
        #print "interpret AFunctionExpression: ", pretty_print(node)
        if isinstance(node.children[0], APredecessorExpression):
            value = interpret(node.children[1], env)
            return value-1
        if isinstance(node.children[0], ASuccessorExpression):
            value = interpret(node.children[1], env)
            return value+1
        function = interpret(node.children[0], env)
        #print "FunctionName:", node.children[0].idName
        args = None
        i = 0 
        for child in node.children[1:]:
            arg = interpret(child, env)
            if i==0:
                args = arg
            else:
                args = tuple([args, arg])
            i = i+1
        if isinstance(function, SymbolicSet):
            return function[args]
        return get_image(function, args)
    elif isinstance(node, AIdentifierExpression):
        #print node.idName
        return env.get_value(node.idName)
        """
    else:
        raise Exception("\nError: Unknown/unimplemented node inside eval_int_expression: %s",node)
        return -1 # RPython: Avoid return of python None


# That the result of node evaluation is an boolean,  must be ensured BY THE CALLER!
def eval_bool_expression(node, env):
    if isinstance(node, AConjunctPredicate):
        bexpr1 = eval_bool_expression(node.get(0), env)
        bexpr2 = eval_bool_expression(node.get(1), env)
        return bexpr1 and bexpr2
    elif isinstance(node, ADisjunctPredicate):
        bexpr1 = eval_bool_expression(node.get(0), env)
        bexpr2 = eval_bool_expression(node.get(1), env)
        return bexpr1 or bexpr2
    elif isinstance(node, AImplicationPredicate):
        bexpr1 = eval_bool_expression(node.get(0), env)
        bexpr2 = eval_bool_expression(node.get(1), env)
        if bexpr1 and not bexpr2:
            return False # True=>False is False
        else:
            return True
    elif isinstance(node, AEquivalencePredicate):
        bexpr1 = eval_bool_expression(node.get(0), env)
        bexpr2 = eval_bool_expression(node.get(1), env)
        assert isinstance(bexpr1, bool) and isinstance(bexpr2, bool)
        return bexpr1 == bexpr2 
    elif isinstance(node, ANegationPredicate):
        bexpr = eval_bool_expression(node.get(0), env)
        return not bexpr
        """
    elif isinstance(node, AForallPredicate):
        # notice: the all and any keywords are not used, because they need the generation of the whole set
        # new scope
        varList = node.children[:-1]
        env.push_new_frame(varList)
        pred = node.children[-1]
        domain_generator = calc_possible_solutions(pred.children[0], env, varList, interpret) # use left side of implication
        for entry in domain_generator:
            for name in [x.idName for x in varList]:
                value = entry[name]
                env.set_value(name, value)
            try:
                if interpret(pred.children[0], env) and not interpret(pred.children[1], env):  # test
                    env.pop_frame()           
                    return False
            except ValueNotInDomainException:
                continue
        env.pop_frame() # leave scope
        return True        
    elif isinstance(node, AExistsPredicate):
        # new scope
        varList = node.children[:-1]
        env.push_new_frame(varList)
        pred = node.children[-1]
        domain_generator = calc_possible_solutions(pred, env, varList, interpret)
        for entry in domain_generator:
            for name in [x.idName for x in varList]:
                value = entry[name]
                env.set_value(name, value)
            try:
                if interpret(pred, env):  # test
                    env.pop_frame()           
                    return True
            except ValueNotInDomainException:
                continue
        env.pop_frame() # leave scope
        return False        
    elif isinstance(node, AEqualPredicate):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        if isinstance(expr2, SymbolicSet) and isinstance(expr1, frozenset):
            expr2 = expr2.enumerate_all()
            return expr1 == expr2
        else:
            # else normal check, also symbolic (implemented by symbol classes)
            return expr1 == expr2
    elif isinstance(node, ANotEqualPredicate):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        # TODO: handle symbolic sets
        return expr1 != expr2
        """
        """
    elif isinstance(node, AMemberPredicate):
        # TODO: two lambda cases (see interp.py)
        elm = interpret(node.children[0], env)
        aSet = interpret(node.children[1], env)
        return elm in aSet
    elif isinstance(node, ANotMemberPredicate):
        # TODO: two lambda cases (see interp.py)
        elm = interpret(node.children[0], env)
        aSet = interpret(node.children[1], env)
        return not elm in aSet
        """
        """
    elif isinstance(node, ASubsetPredicate):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
        if isinstance(aSet2, SymbolicSet):
            return aSet2.issuperset(aSet1)
        return aSet1.issubset(aSet2)
    elif isinstance(node, ANotSubsetPredicate):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
        return not aSet1.issubset(aSet2)
    elif isinstance(node, ASubsetStrictPredicate):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
        return aSet1.issubset(aSet2) and aSet1 != aSet2
    elif isinstance(node, ANotSubsetStrictPredicate):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
        return not (aSet1.issubset(aSet2) and aSet1 != aSet2)
        """
    elif isinstance(node, AGreaterPredicate):
        expr1 = eval_int_expression(node.get(0), env)
        expr2 = eval_int_expression(node.get(1), env)
        return expr1 > expr2
    elif isinstance(node, ALessPredicate):
        expr1 = eval_int_expression(node.get(0), env)
        expr2 = eval_int_expression(node.get(1), env)
        return expr1 < expr2
    elif isinstance(node, AGreaterEqualPredicate):
        expr1 = eval_int_expression(node.get(0), env)
        expr2 = eval_int_expression(node.get(1), env)
        return expr1 >= expr2
    elif isinstance(node, ALessEqualPredicate):
        expr1 = eval_int_expression(node.get(0), env)
        expr2 = eval_int_expression(node.get(1), env)
        return expr1 <= expr2
    else:
        raise Exception("\nError: Unknown/unimplemented node inside eval_bool_expression: %s",node)
        return False # RPython: Avoid return of python None


def eval_clause(node, env):
    if isinstance(node, AConstraintsMachineClause):
        return eval_bool_expression(node.get(-1), env)
        """
    elif isinstance(node, APropertiesMachineClause): #TODO: maybe predicate fail?
        lst = conj_tree_to_conj_list(node.children[0])
        result = True
        ok = 0
        fail = 0
        timeout = 0
        for n in lst:
            try:
                if PROPERTIES_TIMEOUT<=0:
                    value = interpret(n, env)
                else:
                    import multiprocessing   
                    que = multiprocessing.Queue()
                    p = multiprocessing.Process(target = parallel_caller, args = (que, n, env))
                    # TODO: safe and restore stack depth if corruption occurs by thread termination
                    #  length_dict = env.get_state().get_valuestack_depth_of_all_bmachines()
                    p.start()
                    p.join(PROPERTIES_TIMEOUT)
                    if not que.empty():
                        value = que.get()
                    else:
                        p.terminate()
                        print "\033[1m\033[94mTIMEOUT\033[00m: ("+pretty_print(n)+")"
                        # TODO: a timeout(cancel) can result in a missing stack pop (e.g. AGeneralProductExpression
                        timeout = timeout +1
                        continue
            except OverflowError:
                print "\033[1m\033[91mFAIL\033[00m: Enumeration overflow caused by: ("+pretty_print(n)+")"
                fail = fail +1
                continue
            if PRINT_SUB_PROPERTIES: # config.py
                string = str(value)
                if string=="False":
                   print '\033[1m\033[91m'+'False'+'\033[00m'+": "+pretty_print(n)
                   fail = fail +1
                elif string=="True":
                   print '\033[1m\033[92m'+'True'+'\033[00m'+": "+pretty_print(n)
                   ok = ok +1
                else: #XXX
                   print '\033[1m\033[94m'+string+'\033[00m'+": "+pretty_print(n)
            result = result and value
        if fail>0:
            print "\033[1m\033[91mproperties clause - total:%s ok:%s fail:%s timeout:%s\033[00m" % (len(lst), ok,fail,timeout)
        elif timeout>0:
            print "\033[1m\033[94mproperties clause - total:%s ok:%s fail:%s timeout:%s\033[00m" % (len(lst), ok,fail,timeout)
        else:
            print "\033[1m\033[92mproperties clause - total:%s ok:%s fail:%s timeout:%s\033[00m" % (len(lst),ok,fail,timeout)       
        return result
        """
    elif isinstance(node, AInvariantMachineClause):
        result = eval_bool_expression(node.get(0), env)
        if not result:
            print "\nFALSE Predicates:"
            #print_predicate_fail(env, node.get(0))
        return result
        """
    elif isinstance(node, AAssertionsMachineClause):
        if ENABLE_ASSERTIONS: #config.py
            ok = 0
            fail = 0
            print "checking assertions"
            for child in node.children:
                #print_ast(child)
                result = interpret(child, env)
                if result==True:
                    print '\033[1m\033[92m'+'True'+'\033[00m'+": "+pretty_print(child)
                    ok = ok +1
                else:
                    print '\033[1m\033[91m'+str(result)+'\033[00m'+": "+pretty_print(child)
                    fail = fail +1
            print "checking done - ok:%s fail:%s" % (ok,fail)
        """
    else:
        raise Exception("\nError: Unknown/unimplemented node inside eval_clause: %s",node)
        return -1 # RPython: Avoid return of python None      
      
        
def interpret(node, env):
    if isinstance(node, APredicateParseUnit): #TODO: move print to animation_clui
        #type_check_predicate(node, env)
        #idNodes = find_var_nodes(node) 
        #idNames = [n.idName for n in idNodes]
        #if idNames ==[]: # variable free predicate
        result = eval_bool_expression(node.children[0], env)
        return result
        """   
        else:            # there are variables 
            env.add_ids_to_frame(idNames)
            learnd_vars = learn_assigned_values(node, env)
            if learnd_vars and VERBOSE:
                print "learnd(no enumeration): ", learnd_vars
            not_set = []
            for n in idNodes:
                if env.get_value(n.idName)==None:
                    not_set.append(n)
            # enumerate only unknown vars
            # Dont enums quantified vars like !x.(P=>Q). This is done later
            if not_set:
                if VERBOSE:
                    print "enum. vars:", [n.idName for n in not_set]
                gen = try_all_values(node.children[0], env, not_set)
                if gen.next():
                    for i in idNames:
                        if VERBOSE:
                            print i,"=", print_values_b_style(env.get_value(i))
                else:
                    print "No Solution found! MIN_INT=%s MAX_INT=%s (see config.py)" % (env._min_int, env._max_int)
                    return False
            else:
                for i in idNames:
                    print i,"=", print_values_b_style(env.get_value(i))
                result = interpret(node.children[0], env)
                return result
        return True
        """
    else:
        raise Exception("\nError: Unknown/unimplemented node inside interpreter: %s",node)
        return False # RPython: Avoid return of python None

# if ProB found a "full solution". This shouldn't do anything, except checking the solution            
# calcs up to MAX_INIT init B-states
def exec_initialisation(root, env, mch, solution_file_read=False):
    # 0. Use solution file if possible
    if solution_file_read:
        use_prob_solutions(env, mch.var_names)
        pre_init_state = env.state_space.get_state()
        unset_lst = __find_unset_variables(mch, pre_init_state)
        if unset_lst and VERBOSE:
            print "\033[1m\033[91mWARNING\033[00m: Init from solution file was not complete! unset:%s" % unset_lst
        
        env.state_space.add_state(pre_init_state)
        if mch.has_invariant_mc and not interpret(mch.aInvariantMachineClause, env):
            raise INITNotPossibleException("\nError: INITIALISATION unsuccessfully. Values from solution-file caused an INVARIANT-violation")
        env.state_space.undo()
        return [pre_init_state] 
               
    # 1. set up frames and state
    bstates = []
    ref_bstate = env.state_space.get_state().clone()
    env.state_space.add_state(ref_bstate)
     
    
    # 2. search for solutions  
    generator = __exec_initialisation_generator(root, env, mch)
    sol_num = 0
    for solution in generator:
        if solution:
            solution_bstate = env.state_space.get_state()
            bstates.append(solution_bstate)
            env.state_space.revert(ref_bstate) # revert to ref B-state
            env.init_bmachines_names = []
            
            sol_num = sol_num +1
            if sol_num==MAX_INIT:
                break 
    env.state_space.undo() # pop ref_state
    return bstates


# yields False if the state was not changed
# yields True  if only one machine init was performed successfully
# Assumption: The 'init' of one B-machine doesn't affect the 'init' of another
def __exec_initialisation_list_generator(root, env, mch_list):
    if mch_list==[]:
        yield False
    else:
        mch = mch_list[0] 
        init_generator = __exec_initialisation_generator(mch.root, env, mch)
        for bstate_change in init_generator:
            init_list_generator = __exec_initialisation_list_generator(root, env, mch_list[1:])
            for more_bstate_change in init_list_generator:
                yield bstate_change or more_bstate_change        

                

def __exec_initialisation_generator(root, env, mch):
    # 1. check if init already done to avoid double init
    if mch.mch_name in env.init_bmachines_names:
        yield False
    else:
        env.init_bmachines_names.append(mch.mch_name)
            
    # 2. init children
    children = mch.included_mch + mch.extended_mch + mch.seen_mch + mch.used_mch
    init_list_generator = __exec_initialisation_list_generator(root, env, children)

    # TODO state revert?
    for child_bstate_change in init_list_generator:         
        # 3. set up state and env. for init exec
        env.current_mch = mch 
        env.add_ids_to_frame(mch.var_names)
        ref_bstate = env.state_space.get_state().clone() # save init of children (this is a Bugfix and not the solution)
        
        # 3.1 nothing to be init.        
        if not mch.has_initialisation_mc:
            if mch.has_variables_mc and  mch.has_conc_variables_mc:
                raise INITNotPossibleException("\nError: Missing InitialisationMachineClause in %s!" % mch.mch_name)
            yield child_bstate_change
        # 3.2. search for solutions  
        else:                 
            at_least_one_possible = False
            ex_sub_generator = exec_substitution(mch.aInitialisationMachineClause.children[-1], env)
            for bstate_change in ex_sub_generator:
                if bstate_change:
                    at_least_one_possible = True
                    yield True
                    env.state_space.revert(ref_bstate) # revert to current child-init-solution
            if not at_least_one_possible:
                raise INITNotPossibleException("\n\033[1m\033[91mWARNING\033[00m: Problem while exec init. No init found/possible! in %s" % mch.mch_name)

# TODO: use solutions of child mch (seen, used mch)
def use_prob_solutions(env, idNames):
    #print "use_prob_solutions"
    for name in idNames:
        try:
            node = env.solutions[name]
            #print "setting",name #, " to:", pretty_print(node) 
            value = interpret(node, env)
            env.set_value(name, value)
        except KeyError:
            print "\n\033[1m\033[91mWARNING\033[00m: Reading solution file. Missing solution for %s" % name
    #print "ProB solutions set to env"


def __check_unset(names, bstate, mch):
    fail_lst = []
    for id_Name in names:
        try:
            value = bstate.get_value(id_Name, mch)
            if value==None:
                fail_lst.append(id_Name)    
        except ValueNotInBStateException:
            fail_lst.append(id_Name)
    return fail_lst


# checks if there are any unset variables
def __find_unset_variables(mch, bstate):
    # TODO: Find unset in child-mchs
    var_lst = mch.var_names
    fail_lst = __check_unset(var_lst, bstate, mch)
    return fail_lst 


# side-effect: changes state while exec.
# returns True if substitution was possible
# Substituions return True/False if the substitution was possible
def exec_substitution(sub, env):
    
    
# ****************
#
# 5. Substitutions
#
# ****************
    assert isinstance(sub, Substitution)
    if isinstance(sub, ASkipSubstitution):
        yield True # always possible
    elif isinstance(sub, AAssignSubstitution):
        assert int(sub.lhs_size) == int(sub.rhs_size)     
        used_ids = []
        values = []
        # get values of all expressions (rhs)
        for i in range(int(sub.rhs_size)):
            rhs = sub.children[i+int(sub.rhs_size)]
            value = interpret(rhs, env)
            values.append(value)
        for i in range(int(sub.lhs_size)):
            lhs_node = sub.children[i]            
            # BUG if the expression on the rhs has a side-effect
            value = values[i]
            # case (1) lhs: no function
            if isinstance(lhs_node, AIdentifierExpression):
                used_ids.append(lhs_node.idName)
                env.set_value(lhs_node.idName, value)
            # case (2) lhs: is function 
            else:
                assert isinstance(lhs_node, AFunctionExpression)
                assert isinstance(lhs_node.children[0], AIdentifierExpression)
                func_name = lhs_node.children[0].idName
                # get args and convert to dict
                args = []
                for child in lhs_node.children[1:]:
                    arg = interpret(child, env)
                    args.append(arg)
                func = dict(env.get_value(func_name))
                used_ids.append(func_name)
                # mapping of func values
                if len(args)==1:
                    func[args[0]] = value
                else:
                    func[tuple(args)] = value
                # convert back
                lst = []
                for key in func:
                    lst.append(tuple([key,func[key]]))
                new_func = frozenset(lst)
                # write to env
                env.set_value(func_name, new_func)
            # case (3) record: 3 # TODO
        while not used_ids==[]:
            name = used_ids.pop()
            if name in used_ids:
                raise Exception("\nError: %s modified twice in multiple assign-substitution!" % name)
        yield True # assign(s) was/were  successful 
     
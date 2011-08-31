# -*- coding: utf-8 -*-
from ast_nodes import *

min_int = -1
max_int = 5

class Environment():
    variable_values = {} #values of global and local vars

def inperpret(node, env):
    if isinstance(node, AConjunctPredicate):
        expr1 = inperpret(node.children[0], env)
        expr2 = inperpret(node.children[1], env)
        return expr1 and expr2
    elif isinstance(node, ADisjunctPredicate):
        expr1 = inperpret(node.children[0], env)
        expr2 = inperpret(node.children[1], env)
        return expr1 or expr2
    elif isinstance(node, AImplicationPredicate):
        expr1 = inperpret(node.children[0], env)
        expr2 = inperpret(node.children[1], env)
        if expr1 and not expr2:
            return False # True=>False is False
        else:
            return True
    elif isinstance(node, AEquivalencePredicate):
        expr1 = inperpret(node.children[0], env)
        expr2 = inperpret(node.children[1], env)
        return expr1 == expr2 # FIXME: maybe this is wrong...
    elif isinstance(node, AEqualPredicate):
        expr1 = inperpret(node.children[0], env)
        expr2 = inperpret(node.children[1], env)
        return expr1 == expr2
    elif isinstance(node, AUnequalPredicate):
        expr1 = inperpret(node.children[0], env)
        expr2 = inperpret(node.children[1], env)
        return expr1 != expr2
    elif isinstance(node, AGreaterPredicate):
        expr1 = inperpret(node.children[0], env)
        expr2 = inperpret(node.children[1], env)
        return expr1 > expr2
    elif isinstance(node, AGreaterEqualPredicate):
        expr1 = inperpret(node.children[0], env)
        expr2 = inperpret(node.children[1], env)
        return expr1 >= expr2
    elif isinstance(node, ALessPredicate):
        expr1 = inperpret(node.children[0], env)
        expr2 = inperpret(node.children[1], env)
        return expr1 < expr2
    elif isinstance(node, ALessEqualPredicate):
        expr1 = inperpret(node.children[0], env)
        expr2 = inperpret(node.children[1], env)
        return expr1 <= expr2
    elif isinstance(node, ANegationPredicate):
        expr = inperpret(node.children[0], env)
        return not expr
    elif isinstance(node, AIntegerExpression):
        return node.intValue
    elif isinstance(node, AAddExpression):
        expr1 = inperpret(node.children[0], env)
        expr2 = inperpret(node.children[1], env)
        return expr1 + expr2
    elif isinstance(node, AMinusOrSetSubtractExpression):
        expr1 = inperpret(node.children[0], env)
        expr2 = inperpret(node.children[1], env)
        return expr1 - expr2
    elif isinstance(node, AMultOrCartExpression):
        expr1 = inperpret(node.children[0], env)
        expr2 = inperpret(node.children[1], env)
        if isinstance(expr1, set) and isinstance(expr2, set):
            return set(((x,y) for x in expr1 for y in expr2))
        else:
            return expr1 * expr2
    elif isinstance(node, ADivExpression):
        expr1 = inperpret(node.children[0], env)
        expr2 = inperpret(node.children[1], env)
        return expr1 / expr2
    elif isinstance(node, AModuloExpression):
        expr1 = inperpret(node.children[0], env)
        expr2 = inperpret(node.children[1], env)
        return expr1 % expr2
    elif isinstance(node, AIdentifierExpression):
        return env.variable_values[node.idName]
    elif isinstance(node, ABelongPredicate):
        elm = inperpret(node.children[0], env)
        aSet = inperpret(node.children[1], env)
        return elm in aSet
    elif isinstance(node, ANotBelongPredicate):
        elm = inperpret(node.children[0], env)
        aSet = inperpret(node.children[1], env)
        return not elm in aSet
    elif isinstance(node, ASetExtensionExpression):
        lst = []
        for child in node.children:
            elm = inperpret(child, env)
            lst.append(elm)
        return set(lst)
    elif isinstance(node, ACardExpression):
        aSet = inperpret(node.children[0], env)
        return len(aSet)
    elif isinstance(node, AEmptySetExpression):
        return set()
    elif isinstance(node, AUnionExpression):
        aSet1 = inperpret(node.children[0], env)
        aSet2 = inperpret(node.children[1], env)
        return aSet1.union(aSet2)
    elif isinstance(node, AIntersectionExpression):
        aSet1 = inperpret(node.children[0], env)
        aSet2 = inperpret(node.children[1], env)
        return aSet1.intersection(aSet2)
    elif isinstance(node, AIncludePredicate):
        aSet1 = inperpret(node.children[0], env)
        aSet2 = inperpret(node.children[1], env)
        return aSet1.issubset(aSet2)
    elif isinstance(node, ANotIncludePredicate):
        aSet1 = inperpret(node.children[0], env)
        aSet2 = inperpret(node.children[1], env)
        return not aSet1.issubset(aSet2)
    elif isinstance(node, AIncludeStrictlyPredicate):
        aSet1 = inperpret(node.children[0], env)
        aSet2 = inperpret(node.children[1], env)
        return aSet1.issubset(aSet2) and aSet1 != aSet2
    elif isinstance(node, ANotIncludeStrictlyPredicate):
        aSet1 = inperpret(node.children[0], env)
        aSet2 = inperpret(node.children[1], env)
        return not (aSet1.issubset(aSet2) and aSet1 != aSet2)
    elif isinstance(node, AUniversalQuantificationPredicate):
        # FIXME: supports only integers!
        max_depth = len(node.children) -2
        if not forall_recursive_helper(0, max_depth, node, env):
            return False
        else:
            return True
    elif isinstance(node, AExistentialQuantificationPredicate):
        # FIXME: supports only integers!
        max_depth = len(node.children) -2
        if exist_recursive_helper(0, max_depth, node, env):
            return True
        else:
            return False
    elif isinstance(node, AComprehensionSetExpression):
        # FIXME: supports only integers!
        max_depth = len(node.children) -2
        lst = set_comprehension_recursive_helper(0, max_depth, node, env)
        # FIXME: maybe wrong:
        # [[x1,y1],[x2,y2]..] => [(x1,y2),(x2,y2)...]
        result = []
        for i in lst:
            result.append(tuple(flatten(i,[])))
        return set(result)
    elif isinstance(node, ACoupleExpression):
        lst = []
        for child in node.children:
            elm = inperpret(child, env)
            lst.append(elm)
        return tuple(lst)
    elif isinstance(node, APowSubsetExpression):
        aSet = inperpret(node.children[0], env)
        res = powerset(aSet)
        powerlist = list(res)
        lst = [frozenset(e) for e in powerlist]
        return set(lst)
    elif isinstance(node, APow1SubsetExpression):
        aSet = inperpret(node.children[0], env)
        res = powerset(aSet)
        powerlist = list(res)
        lst = [frozenset(e) for e in powerlist]
        lst.remove(frozenset([]))
        return set(lst)
    elif isinstance(node, ARelationsExpression):
        aSet1 = inperpret(node.children[0], env)
        aSet2 = inperpret(node.children[1], env)
        aSet = make_set_of_realtions(aSet1, aSet2)
        return aSet
    elif isinstance(node, ADomainExpression):
        # FIXME: crashs if this is not a set of 2-tuple
        aSet = inperpret(node.children[0], env)
        dom = [e[0] for e in list(aSet)]
        return set(dom)
    elif isinstance(node, ARangeExpression):
        # FIXME: crashs if this is not a set of 2-tuple
        aSet = inperpret(node.children[0], env)
        ran = [e[1] for e in list(aSet)]
        return set(ran)
    elif isinstance(node, ACompositionExpression):
        aSet1 = inperpret(node.children[0], env)
        aSet2 = inperpret(node.children[1], env)
        new_rel = [(p[0],q[1]) for p in aSet1 for q in aSet2 if p[1]==q[0]]
        return set(new_rel)
    elif isinstance(node, AIdentityExpression):
        aSet = inperpret(node.children[0], env)
        id_r = [(x,x) for x in aSet]
        return set(id_r)
    elif isinstance(node, ADomainRestrictionExpression):
        aSet = inperpret(node.children[0], env)
        rel = inperpret(node.children[1], env)
        new_rel = [x for x in rel if x[0] in aSet]
        return set(new_rel)
    elif isinstance(node, ADomainSubtractionExpression):
        aSet = inperpret(node.children[0], env)
        rel = inperpret(node.children[1], env)
        new_rel = [x for x in rel if not x[0] in aSet]
        return set(new_rel)
    elif isinstance(node, ARangeRestrictionExpression):
        aSet = inperpret(node.children[1], env)
        rel = inperpret(node.children[0], env)
        new_rel = [x for x in rel if x[1] in aSet]
        return set(new_rel)
    elif isinstance(node, ARangeSubtractionExpression):
        aSet = inperpret(node.children[1], env)
        rel = inperpret(node.children[0], env)
        new_rel = [x for x in rel if not x[1] in aSet]
        return set(new_rel)
    elif isinstance(node, AReverseExpression):
        rel = inperpret(node.children[0], env)
        new_rel = [(x[1],x[0]) for x in rel]
        return set(new_rel)
    elif isinstance(node, AImageExpression):
        rel = inperpret(node.children[0], env)
        aSet = inperpret(node.children[1], env)
        image = [x[1] for x in rel if x[0] in aSet ]
        return set(image)
    elif isinstance(node, AOverwriteExpression):
        r1 = inperpret(node.children[0], env)
        r2 = inperpret(node.children[1], env)
        dom_r2 = [x[0] for x in r2]
        new_r  = [x for x in r1 if x[0] not in dom_r2]
        r2_list= [x for x in r2]
        return set(r2_list + new_r)
    elif isinstance(node, AFirstProjectionExpression):
        S = inperpret(node.children[0], env)
        T = inperpret(node.children[1], env)
        cart = set(((x,y) for x in S for y in T))
        proj = [(x,x[0]) for x in cart]
        return set(proj)
    elif isinstance(node, ASecondProjectionExpression):
        S = inperpret(node.children[0], env)
        T = inperpret(node.children[1], env)
        cart = set(((x,y) for x in S for y in T))
        proj = [(x,x[1]) for x in cart]
        return set(proj)
    elif isinstance(node, ADirectProductExpression):
        p = inperpret(node.children[0], env)
        q = inperpret(node.children[1], env)
        d_prod = [(x[0],(x[1],y[1])) for x in p for y in q if x[0]==y[0]]
        return set(d_prod)
    elif isinstance(node, AParallelProductExpression):
        p = inperpret(node.children[0], env)
        q = inperpret(node.children[1], env)
        p_prod = [((x[0],y[0]),(x[1],y[1])) for x in p for y in q]
        return set(p_prod)
    elif isinstance(node, APartialFunctionExpression):
        S = inperpret(node.children[0], env)
        T = inperpret(node.children[1], env)
        relation_set = make_set_of_realtions(S,T) # S<-->T
        fun = filter_no_function(relation_set) # S+->T
        return fun
    elif isinstance(node, ATotalFunctionExpression):
        S = inperpret(node.children[0], env)
        T = inperpret(node.children[1], env)
        relation_set = make_set_of_realtions(S,T) # S<-->T
        fun = filter_no_function(relation_set) # S+->T
        total_fun = filter_not_total(fun, S) # S-->T
        return total_fun
    elif isinstance(node, APartialInjectionExpression):
        S = inperpret(node.children[0], env)
        T = inperpret(node.children[1], env)
        relation_set = make_set_of_realtions(S,T) # S<-->T
        fun = filter_no_function(relation_set) # S+->T
        inj_fun = filter_not_injective(fun) # S>+>T
        return inj_fun
    elif isinstance(node, ATotalInjectionExpression):
        S = inperpret(node.children[0], env)
        T = inperpret(node.children[1], env)
        relation_set = make_set_of_realtions(S,T) # S<-->T
        fun = filter_no_function(relation_set) # S+->T
        inj_fun = filter_not_injective(fun) # S>+>T
        total_inj_fun = filter_not_total(inj_fun, S) # S>->T
        return total_inj_fun
    elif isinstance(node, APartialSurjectionExpression):
        S = inperpret(node.children[0], env)
        T = inperpret(node.children[1], env)
        relation_set = make_set_of_realtions(S,T) # S<-->T
        fun = filter_no_function(relation_set) # S+->T
        surj_fun = filter_not_surjective(fun, T) # S+->>T
        return surj_fun
    elif isinstance(node, ATotalSurjectionExpression):
        S = inperpret(node.children[0], env)
        T = inperpret(node.children[1], env)
        relation_set = make_set_of_realtions(S,T) # S<-->T
        fun = filter_no_function(relation_set) # S+->T
        surj_fun = filter_not_surjective(fun, T) # S+->>T
        total_surj_fun = filter_not_total(surj_fun, S) # S-->>T
        return total_surj_fun
    elif isinstance(node, ATotalBijectionExpression):
        S = inperpret(node.children[0], env)
        T = inperpret(node.children[1], env)
        relation_set = make_set_of_realtions(S,T) # S<-->T
        fun = filter_no_function(relation_set) # S+->T
        inj_fun = filter_not_injective(fun) # S>+>T
        total_inj_fun = filter_not_total(inj_fun, S) # S>->T
        bij_fun = filter_not_surjective(total_inj_fun,T) # S>->>T
        return bij_fun
    elif isinstance(node, AFunctionExpression):
        function = inperpret(node.children[0], env)
        args = [] # TODO: enamble many args
        for child in node.children[1:]:
            arg = inperpret(child, env)
            args.append(arg)
        return get_image(function, args[0])
    elif isinstance(node,AEmptySequenceExpression):
        return set([])
    elif isinstance(node,ASeqExpression):
        S = inperpret(node.children[0], env)
        sequence_list = [frozenset([])]
        max_len = 1
        # find all seq from 1..max_int
        for i in range(1,max_int+1):
            sequence_list += create_all_seq_w_fixlen(list(S),i)
        return set(sequence_list)
    elif isinstance(node,ASeq1Expression):
        S = inperpret(node.children[0], env)
        sequence_list = []
        max_len = 1
        # find all seq from 1..max_int
        for i in range(1,max_int+1):
            sequence_list += create_all_seq_w_fixlen(list(S),i)
        return set(sequence_list)
    elif isinstance(node,AIseqExpression):
        # TODO: this can be impl. much better
        S = inperpret(node.children[0], env)
        sequence_list = [frozenset([])]
        max_len = 1
        # find all seq from 1..max_int
        for i in range(1,max_int+1):
            sequence_list += create_all_seq_w_fixlen(list(S),i)
        inj_sequence_list = filter_not_injective(sequence_list)
        return set(inj_sequence_list)
    elif isinstance(node,APermExpression): 
        # TODO: this can be impl. much better
        S = inperpret(node.children[0], env)
        sequence_list = [frozenset([])]
        max_len = 1
        # find all seq from 1..max_int
        for i in range(1,max_int+1):
            sequence_list += create_all_seq_w_fixlen(list(S),i)
        inj_sequence_list = filter_not_injective(sequence_list)
        perm_sequence_list = filter_not_surjective(inj_sequence_list, S)
        return set(perm_sequence_list)
    elif isinstance(node, AConcatExpression):
        s = inperpret(node.children[0], env)
        t = inperpret(node.children[1], env)
        new_t = []
        for tup in t:
            new_t.append(tuple([tup[0]+len(s),tup[1]]))
        return set(list(s)+new_t)
    elif isinstance(node, AInsertFrontExpression):
        E = inperpret(node.children[0], env)
        s = inperpret(node.children[1], env)
        new_s = [(1,E)]
        for tup in s:
            new_s.append(tuple([tup[0]+1,tup[1]]))
        return set(new_s)
    elif isinstance(node, AInsertTailExpression):
        s = inperpret(node.children[0], env)
        E = inperpret(node.children[1], env)
        return set(list(s)+[tuple([len(s)+1,E])])
    elif isinstance(node, ASequenceExtensionExpression):
        sequence = []
        i = 0
        for child in node.children:
            i = i+1
            e = inperpret(child, env)
            sequence.append(tuple([i,e]))
        return set(sequence)
    elif isinstance(node, ASizeExpression):
        sequence = inperpret(node.children[0], env)
        return len(sequence)
    elif isinstance(node, ARevExpression):
        sequence = inperpret(node.children[0], env)
        new_sequence = []
        i = len(sequence)
        for tup in sequence:
            new_sequence.append(tuple([i,tup[1]]))
            i = i-1
        return set(new_sequence)
    elif isinstance(node, ARestrictFrontExpression):
        sequence = inperpret(node.children[0], env)
        take = inperpret(node.children[1], env)
        assert take>0
        lst = list(sequence)
        lst.sort()
        return set(lst[:-take])
    elif isinstance(node, ARestrictTailExpression):
        sequence = inperpret(node.children[0], env)
        drop = inperpret(node.children[1], env)
        assert drop>0
        lst = list(sequence)
        lst.sort()
        new_list = []
        i = 0
        for tup in lst[drop:]:
            i = i+1
            new_list.append(tuple([i,tup[1]]))
        return set(new_list)
    else:
        raise Exception("Unknown Node: %s",node)


# XXX: Warning: this could take some time...
def create_all_seq_w_fixlen(images, length):
    result = []
    basis = len(images)
    noc = basis**length # number of combinations
    for i in range(noc):
        lst = create_sequence(images, i, length)
        result.append(frozenset(lst))
    return result

def create_sequence(images, number, length):
    result = []
    basis = len(images)
    for i in range(length):
        symbol = tuple([i+1,images[number % basis]])
        result.append(symbol)
        number /= basis
    result.reverse()
    return result


def flatten(lst, res):
    for e in lst:
        if not isinstance(e,list):
            res.append(e)
        else:
            res = flatten(e, res)
    return res


def get_image(function, preimage):
    for atuple in function:
        if atuple[0] == preimage:
            return atuple[1]
    return None #no image found

# checks if a list contains a duplicate element
def double_element_check(lst):
    for element in lst:
        if lst.count(element)>1:
            return True
    return False


# filters out every function which is not injective
def filter_not_injective(functions):
    injective_funs = []
    for fun in functions:
        image = [x[1] for x in fun]
        if not double_element_check(image):
            injective_funs.append(fun)
    return set(injective_funs)


# filters out every function which is not surjective
def filter_not_surjective(functions, T):
    surj_funs = []
    for fun in functions:
        if is_a_surj_function(fun, T):
            surj_funs.append(fun)
    return set(surj_funs)


# filters out every function which is not total
def filter_not_total(functions, S):
    total_funs = []
    for fun in functions:
        if is_a_total_function(fun, S):
            total_funs.append(fun)
    return set(total_funs)


# checks if the function it total 
def is_a_total_function(function, preimage_set):
    preimage = [x[0] for x in function]
    preimage_set2 =  set(preimage)
    return preimage_set == preimage_set2


# checks if the function it surjective
def is_a_surj_function(function, image_set):
    image = [x[1] for x in function]
    image_set2= set(image) # remove duplicate items
    return image_set == image_set2


# filters out every set which is no function
def filter_no_function(relations):
    functions = []
    for r in relations:
        if is_a_function(r):
            functions.append(r)
    return set(functions)


# checks if a relation is a function
def is_a_function(relation):
    preimage_set = [x[0] for x in relation]
    if double_element_check(preimage_set):
        return False
    else:
        return True


# returns S<-->T
def make_set_of_realtions(S,T):
    cartSet = set(((x,y) for x in S for y in T))
    res = powerset(cartSet)
    powerlist = list(res)
    lst = [frozenset(e) for e in powerlist]
    return set(lst)


# from http://docs.python.org/library/itertools.html
def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    from itertools import chain, combinations
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


# FIXME: rename quantified variables!
def set_comprehension_recursive_helper(depth, max_depth, node, env):
    result = []
    pred = node.children[len(node.children) -1]
    idName = node.children[depth].idName
    if depth == max_depth: #basecase
        for i in range(min_int, max_int):
            env.variable_values[idName] = i
            if inperpret(pred, env):
                result.append(i)
        return result
    else: # recursive call
        for i in range(min_int, max_int):
            env.variable_values[idName] = i
            partial_result = set_comprehension_recursive_helper(depth+1, max_depth, node, env)
            for j in partial_result:
                temp = []
                temp.append(i)
                temp.append(j)
                result.append(temp)
        return result


# FIXME: rename quantified variables!
def exist_recursive_helper(depth, max_depth, node, env):
    pred = node.children[len(node.children) -1]
    idName = node.children[depth].idName
    if depth == max_depth: #basecase
        for i in range(min_int, max_int):
            env.variable_values[idName] = i
            if inperpret(pred, env):
                return True
        return False
    else: # recursive call
        for i in range(min_int, max_int):
            env.variable_values[idName] = i
            if exist_recursive_helper(depth+1, max_depth, node, env):
                return True
        return False


# FIXME: rename quantified variables!
def forall_recursive_helper(depth, max_depth, node, env):
    pred = node.children[len(node.children) -1]
    idName = node.children[depth].idName
    if depth == max_depth: #basecase
        for i in range(min_int, max_int):
            env.variable_values[idName] = i
            if not inperpret(pred, env):
                return False
        return True
    else: # recursive call
        for i in range(min_int, max_int):
            env.variable_values[idName] = i
            if not forall_recursive_helper(depth+1, max_depth, node, env):
                return False
        return True
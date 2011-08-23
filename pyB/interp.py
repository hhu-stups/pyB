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
        cartSet = set(((x,y) for x in aSet1 for y in aSet2))
        res = powerset(cartSet)
        powerlist = list(res)
        lst = [frozenset(e) for e in powerlist]
        return set(lst)
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
        print rel
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
    else:
        raise Exception("Unknown Node: %s",node)


def flatten(lst, res):
    for e in lst:
        if not isinstance(e,list):
            res.append(e)
        else:
            res = flatten(e, res)
    return res


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
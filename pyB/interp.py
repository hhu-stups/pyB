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
    else:
        raise Exception("Unknown Node: %s",node)

def flatten(lst, res):
    for e in lst:
        if not isinstance(e,list):
            res.append(e)
        else:
            res = flatten(e, res)
    return res

# FIXME: rename quantified variables!
def set_comprehension_recursive_helper(depth, max_depth, node, env):
    result = []
    pred = node.children[len(node.children) -1]
    idName = node.children[depth].idName
    if depth == max_depth:
        for i in range(min_int, max_int):
            env.variable_values[idName] = i
            if inperpret(pred, env):
                result.append(i)
        return result
    else:
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
    if depth == max_depth:
        for i in range(min_int, max_int):
            env.variable_values[idName] = i
            if inperpret(pred, env):
                return True
        return False
    else:
        for i in range(min_int, max_int):
            env.variable_values[idName] = i
            if exist_recursive_helper(depth+1, max_depth, node, env):
                return True
        return False

# FIXME: rename quantified variables!
def forall_recursive_helper(depth, max_depth, node, env):
    pred = node.children[len(node.children) -1]
    idName = node.children[depth].idName
    if depth == max_depth:
        for i in range(min_int, max_int):
            env.variable_values[idName] = i
            if not inperpret(pred, env):
                return False
        return True
    else:
        for i in range(min_int, max_int):
            env.variable_values[idName] = i
            if not forall_recursive_helper(depth+1, max_depth, node, env):
                return False
        return True
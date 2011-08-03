# -*- coding: utf-8 -*-
from ast_nodes import *
import sets # FIXME: depricated

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
            return False # True=>False
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
        if isinstance(expr1, sets.Set) and isinstance(expr2, sets.Set):
            return sets.Set(((x,y) for x in expr1 for y in expr2))
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
        return sets.Set(lst)
    elif isinstance(node, ACardExpression):
        aSet = inperpret(node.children[0], env)
        return len(aSet)
    elif isinstance(node, AEmptySetExpression):
        return sets.Set()
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
    else:
        raise Exception("Unknown Node: %s",node)
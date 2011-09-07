# -*- coding: utf-8 -*-
from ast_nodes import *


class BType:
    pass


class IntegerType(BType):
    def __init__(self, data):
        self.data = data


# returns Type, None or String
# sideeffect: changes env
def typeit(node, env):
    if isinstance(node, ANatSetExpression):
        return IntegerType(None)
    elif isinstance(node, ANat1SetExpression):
        return IntegerType(None)
    elif isinstance(node, AIntervalExpression):
        return IntegerType(None)
    elif isinstance(node, AIntegerExpression):
        return IntegerType(node.intValue)
    elif isinstance(node, AIdentifierExpression):
        idtype = env.variable_type[node.idName]
        if idtype == None:
            return node.idName # special case
        else:
            return idtype
    elif isinstance(node, ABelongPredicate):
        elm_type = typeit(node.children[0], env)
        set_type = typeit(node.children[1], env)
        if isinstance(elm_type, str) and not set_type == None:
            assert isinstance(node.children[0], AIdentifierExpression)
            env.variable_type[elm_type] = set_type
            return
        else:
            raise Exception("Unimplemented case")
    elif isinstance(node, AEqualPredicate):
        expr1_type = typeit(node.children[0], env)
        expr2_type = typeit(node.children[1], env)
        if isinstance(expr1_type, str) and not expr2_type == None:
            assert isinstance(node.children[0], AIdentifierExpression)
            env.variable_type[expr1_type] = expr2_type
        elif isinstance(expr2_type, str) and not expr1_type == None:
            assert isinstance(node.children[1], AIdentifierExpression)
            env.variable_type[expr2_type] = expr1_type
        else:
            assert expr1_type.__class__ == expr2_type.__class__
        return None
    elif isinstance(node, AAddExpression) or isinstance(node, ADivExpression) or isinstance(node, AModuloExpression):
        expr1_type = typeit(node.children[0], env)
        expr2_type = typeit(node.children[1], env)
        assert isinstance(expr1_type, IntegerType)
        assert isinstance(expr2_type, IntegerType)
        return IntegerType(None)
    elif isinstance(node, ALessEqualPredicate) or isinstance(node, ALessPredicate) or isinstance(node, AGreaterEqualPredicate) or isinstance(node, AGreaterPredicate):
        expr1_type = typeit(node.children[0], env)
        expr2_type = typeit(node.children[1], env)
        if isinstance(expr1_type, str) and not expr2_type == None:
            assert isinstance(node.children[0], AIdentifierExpression)
            env.variable_type[expr1_type] = expr2_type
        elif isinstance(expr2_type, str) and not expr1_type == None:
            assert isinstance(node.children[1], AIdentifierExpression)
            env.variable_type[expr2_type] = expr1_type
        else:
            assert isinstance(expr1_type, IntegerType)
            assert isinstance(expr2_type, IntegerType)
        return None
    elif isinstance(node, AMinusOrSetSubtractExpression):
        expr1_type = typeit(node.children[0], env)
        expr2_type = typeit(node.children[1], env)
        if isinstance(expr1_type, IntegerType) and isinstance(expr2_type, IntegerType): # Minus
            return IntegerType(None)
        else:
            raise Exception("Unimplemented case: %s",node)
    elif isinstance(node, AMultOrCartExpression):
        expr1_type = typeit(node.children[0], env)
        expr2_type = typeit(node.children[1], env)
        if isinstance(expr1_type, IntegerType) and isinstance(expr2_type, IntegerType): # Mul
            return IntegerType(None)
        else:
            raise Exception("Unimplemented case: %s",node)
    elif isinstance(node, AGeneralSumExpression):
        typeit(node.children[-2], env)
        typeit(node.children[-1], env)
        return IntegerType(None)
    elif isinstance(node, AGeneralProductExpression):
        typeit(node.children[-2], env)
        typeit(node.children[-1], env)
        return IntegerType(None)
    else:
        raise Exception("Unimplemented case: %s",node)
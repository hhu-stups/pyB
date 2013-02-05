# -*- coding: utf-8 -*-
import json
from ast_nodes import *
from bmachine import BMachine
from interp import interpret

class PredicateParseUnit:
    def __init__(self, root):
        self.root = root

class ExpressionParseUnit:
    def __init__(self, root):
        self.root = root

# gets a python-code string. and gen a ast
# TODO: get a JSON string insted of python code
# TODO: parse JSON files
def str_ast_to_python_ast(string):
    exec string
    return root

# just generate python wrappers.
def parse_ast(root, env):
    if isinstance(root, APredicateParseUnit):
        return PredicateParseUnit(root)
    elif isinstance(root, AExpressionParseUnit):
        return ExpressionParseUnit(root)
    else:
        assert isinstance(root, AAbstractMachineParseUnit)
        mch = BMachine(root, interpret, env) # recursive parsing of all included, seen, etc. ...
        env.root_mch = mch
        env.current_mch = mch #current mch
        return mch


def parse_json(lst):
    node = None
    children = []
    for e in lst:
        if isinstance(e, str) or isinstance(e, unicode):
            node = str_to_node(e)
        elif isinstance(e, list):
            child = parse_json(e)
            children.append(child)
        elif isinstance(e, dict):
            add_sp_attr(node, e)
        else:
            raise Exception("Error while parsing json input! Check ASTJSON.java or parsing.py")
    node.children = children
    return node

def add_sp_attr(node, dic):
    if isinstance(node, AStringExpression):
        node.string = dic["string"]
    elif isinstance(node, AIdentifierExpression):
        node.idName = dic["idName"]
    elif isinstance(node, AIntegerExpression):
        node.intValue = dic["intValue"]
    else:
        raise Exception("Error while parsing json input! Check ASTJSON.java or parsing.py")


def str_to_node(string):
    if string==u'AStringExpression':
        return AStringExpression(None)
    elif string==u'AIdentifierExpression':
        return AIdentifierExpression(None)
    elif string==u'AIntegerExpression':
        return AIntegerExpression(None)
    else: # TODO: metaprogramming at runtime
        return eval(string+"()") 

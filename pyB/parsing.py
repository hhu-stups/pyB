# -*- coding: utf-8 -*-
import json
from ast_nodes import *
from bmachine import BMachine

class PredicateParseUnit:
    def __init__(self, root):
        self.root = root

class ExpressionParseUnit:
    def __init__(self, root):
        self.root = root

# gets a python-code string. and gen a ast
# TODO: get a JSON string insted of python code
# TODO: parse JSON files
# TODO: A Parsing via "exec <String>" is not RPython: 
# Write a JSON-parser to avoid the string-eval.
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
        mch = BMachine(root) 
        mch.recursive_self_parsing(env) # recursive parsing of all included, seen, etc. ...
        env.root_mch = mch
        env.current_mch = mch #current mch
        mch.add_all_visible_ops_to_env(env) # creating operation-objects and add them to bmchs and env
        return mch


def parse_json(lst):
    node = None
    children = []
    for e in lst:
        if isinstance(e, str) or isinstance(e, unicode):
            node = __str_to_node(e)
        elif isinstance(e, list):
            child = parse_json(e)
            children.append(child)
        elif isinstance(e, dict):
            __add_sp_attr(node, e)
        else:
            raise Exception("Error while parsing json input! Check ASTJSON.java or parsing.py")
    node.children = children
    return node


def __add_sp_attr(node, dic):
    if isinstance(node, AStringExpression):
        node.string = dic["string"]
    elif isinstance(node, AIdentifierExpression):
        node.idName = dic["idName"]
    elif isinstance(node, AIntegerExpression):
        node.intValue = dic["intValue"]
    else:
        raise Exception("Error while parsing json input! Check ASTJSON.java or parsing.py")


def __str_to_node(string):
    if string==u'AStringExpression':
        return AStringExpression(None)
    elif string==u'AIdentifierExpression':
        return AIdentifierExpression(None)
    elif string==u'AIntegerExpression':
        return AIntegerExpression(None)
    else: # TODO: metaprogramming at import-time (generate the other ~ 100 elifs)
        return eval(string+"()") 

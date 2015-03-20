# -*- coding: utf-8 -*-
import json
from ast_nodes import *
from bmachine import BMachine
from definition_handler import DefinitionHandler

# TODO: many nodes missing
# TODO: AFileDefinition, ADefinitionFileParseUnit, AIdentifierExpression, AStringExpression
# AAbstractMachineParseUnit, ARefinementMachineParseUnit, AMachineHeader, ASubstitutionDefinition
# APredicateDefinition, ADefinitionExpression, ADefinitionPredicate, ADefinitionSubstitution .... AOperationCallSubstitution
two_children = ["AAddExpression", "AMinusOrSetSubtractExpression", "AMultOrCartExpression", "ADivExpression", "AModuloExpression", "APowerOfExpression"]
two_children += ["AConjunctPredicate", "ADisjunctPredicate", "AImplicationPredicate", "AEquivalencePredicate"]
two_children += ["AEqualPredicate", "AGreaterPredicate", "ALessPredicate", "AGreaterEqualPredicate", "ALessEqualPredicate"]

one_child = ["APredicateParseUnit", "caseAExpressionParseUnit", "AInvariantMachineClause", "AConstraintsMachineClause"]
one_child += ["ANegationPredicate"]

no_child =  ["AStringSetExpression", "AEmptySetExpression", "AEmptySequenceExpression", "AIntegerSetExpression"]
no_child += ["ANatSetExpression", "ANaturalSetExpression", "AIntSetExpression", "ANatural1SetExpression"]
no_child += ["ANat1SetExpression", "ABooleanTrueExpression", "ABoolSetExpression", "ABooleanFalseExpression"]
no_child += ["ASkipSubstitution", "AMinIntExpression", "AMaxIntExpression", "ASuccessorExpression", "APredecessorExpression"]

# create function at import time (this is allowed by RPython) 
# using metaprogramming:
f =  "def my_exec(string):\n"
##f += "\tprint string\n"
f += "\tstack = []\n"
f += "\tfor line in string.split(\"\\n\"):\n"
# special case: AIntegerExpression
f += "\t\tif \"AIntegerExpression\" in line:\n"
f += "\t\t\ts=line.find('(')\n"
f += "\t\t\te=line.find(')')\n"
f += "\t\t\tnumber=int(line[s+1:e])\n"
f += "\t\t\tnode =AIntegerExpression(number)\n"
f += "\t\t\tstack.append(node)\n"
for node_string in no_child:
    f += "\t\telif \""+ node_string +"\" in line:\n"
    f += "\t\t\tnode = "+ node_string+"()\n"
    f += "\t\t\tstack.append(node)\n"    
for node_string in one_child:
    f += "\t\telif \""+ node_string +"\" in line:\n"
    f += "\t\t\tnode = "+ node_string+"()\n"
    f += "\t\t\tchild = stack.pop()\n"
    f += "\t\t\tnode.children.append(child)\n"
    f += "\t\t\tstack.append(node)\n"
for node_string in two_children:
    f += "\t\telif \""+ node_string +"\" in line:\n"
    f += "\t\t\tnode = "+ node_string+"()\n"
    f += "\t\t\tright = stack.pop()\n"
    f += "\t\t\tleft = stack.pop()\n"
    f += "\t\t\tnode.children.append(left)\n"
    f += "\t\t\tnode.children.append(right)\n"
    f += "\t\t\tstack.append(node)\n"
f += "\tassert len(stack)==1\n"
f += "\troot = stack.pop()\n"
f += "\treturn root\n"
#print f
exec(f) 


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
    #root = my_exec(string)
    return root


# remove definitions from AST and generate python wrappers.
def remove_defs_and_parse_ast(root, env):
    root = remove_definitions(root, env)
    return parse_ast(root, env)

def remove_definitions(root, env):
    dh = DefinitionHandler(env, str_ast_to_python_ast)
    dh.repl_defs(root) # side effect: change AST(root)
    return root

        
# remove definitions from AST and generate python wrappers.
def parse_ast(root, env):
    if isinstance(root, APredicateParseUnit):
        return PredicateParseUnit(root)
    elif isinstance(root, AExpressionParseUnit):
        return ExpressionParseUnit(root)
    else:
        assert isinstance(root, AAbstractMachineParseUnit)
        mch = BMachine(root, remove_definitions) 
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

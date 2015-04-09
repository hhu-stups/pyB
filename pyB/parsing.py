# -*- coding: utf-8 -*-
import json
from ast_nodes import *
from bmachine import BMachine
from definition_handler import DefinitionHandler
from helpers import print_ast

# categorization of possible AST nodes. 
# Two criteria: number of parameter and number of child-nodes
many_children_one_arg = ["AAbstractMachineParseUnit", "ASeesMachineClause","AUsesMachineClause", "AExtendsMachineClause", "APromotesMachineClause", "AIncludesMachineClause"]
many_children_one_arg += ["AConstantsMachineClause", "AVariablesMachineClause", "AConcreteVariablesMachineClause", "AAbstractConstantsMachineClause"]
many_children_one_arg += ["AAssertionsMachineClause", "ASetsMachineClause", "ADefinitionsMachineClause", "AOperationsMachineClause"]
many_children_one_arg += ["ASetExtensionExpression", "ACoupleExpression", "AFunctionExpression", "ASequenceExtensionExpression"]
many_children_one_arg += ["AGeneralSumExpression", "AGeneralProductExpression", "ALambdaExpression", "AComprehensionSetExpression"]
many_children_one_arg += ["AExistsPredicate", "AForallPredicate", "ASequenceSubstitution", "AParallelSubstitution", "AChoiceSubstitution"]
many_children_one_arg += ["AWhileSubstitution", "AStructExpression", "ARecExpression", "ADefinitionFileParseUnit"]

many_children_two_args = ["AMachineHeader", "AMachineReference", "AEnumeratedSetSet", "ADefinitionExpression"]
many_children_two_args += ["AQuantifiedIntersectionExpression", "AQuantifiedUnionExpression", "ADefinitionPredicate"]
many_children_two_args += ["ABecomesSuchSubstitution", "ADefinitionSubstitution", "ABecomesElementOfSubstitution", "AIfSubstitution"]
many_children_two_args += ["ASelectSubstitution", "ACaseOrSubstitution", "AVarSubstitution", "AAnySubstitution", "ALetSubstitution"]
many_children_two_args += ["APrimedIdentifierExpression"]

many_children_three_args = ["AExpressionDefinitionDefinition", "APredicateDefinitionDefinition", "AOpSubstitution"]
many_children_three_args += ["AAssignSubstitution","ASubstitutionDefinitionDefinition", "ACaseSubstitution"]


many_children_four_args = ["AOperation", "AOperationCallSubstitution"]

# nodes without constructor parameters
two_children = ["AAddExpression", "AMinusOrSetSubtractExpression", "AMultOrCartExpression", "ADivExpression", "AModuloExpression", "APowerOfExpression"]
two_children += ["AConjunctPredicate", "ADisjunctPredicate", "AImplicationPredicate", "AEquivalencePredicate"]
two_children += ["AEqualPredicate", "AGreaterPredicate", "ALessPredicate", "AGreaterEqualPredicate", "ALessEqualPredicate"]
two_children += ["AUnionExpression", "AIntersectionExpression", "ARelationsExpression", "ACompositionExpression", "AIterationExpression"]
two_children += ["ADomainRestrictionExpression", "ADomainSubtractionExpression", "ARangeRestrictionExpression", "ARangeSubtractionExpression"]
two_children += ["AImageExpression", "AOverwriteExpression", "ADirectProductExpression","AFirstProjectionExpression", "ASecondProjectionExpression","AParallelProductExpression"]
two_children += ["APartialFunctionExpression", "ATotalFunctionExpression", "APartialInjectionExpression", "ATotalInjectionExpression"]
two_children += ["APartialSurjectionExpression", "ATotalSurjectionExpression", "ATotalBijectionExpression", "APartialBijectionExpression"]
two_children += ["AConcatExpression", "AInsertFrontExpression", "AInsertTailExpression", "ARestrictFrontExpression", "ARestrictTailExpression"]
two_children += ["AIntervalExpression", "AMemberPredicate", "ANotMemberPredicate","ASubsetPredicate", "ANotSubsetPredicate", "ASubsetStrictPredicate", "ANotSubsetStrictPredicate"]
two_children += ["ANotEqualPredicate", "AIfElsifSubstitution", "APreconditionSubstitution", "AAssertionSubstitution", "ASelectWhenSubstitution"]
two_children += ["ARecEntry", "ARecordFieldExpression", "ASetSubtractionExpression"]

one_child = ["APredicateParseUnit", "AExpressionParseUnit", "AInvariantMachineClause", "AConstraintsMachineClause", "AInitialisationMachineClause", "APropertiesMachineClause"]
one_child += ["ANegationPredicate", "AUnaryMinusExpression", "AConvertBoolExpression", "AMinExpression", "AMaxExpression"]
one_child += ["AGeneralUnionExpression", "AGeneralIntersectionExpression", "ACardExpression", "APowSubsetExpression","APow1SubsetExpression"]
one_child += ["ADomainExpression", "ARangeExpression", "AIdentityExpression", "AReflexiveClosureExpression", "AClosureExpression"]
one_child += ["AReverseExpression", "ASeq1Expression", "AIseqExpression", "AIseq1Expression", "APermExpression"]
one_child += ["ASizeExpression", "ARevExpression", "AGeneralConcatExpression", "AFirstExpression", "ALastExpression", "ATailExpression", "AFrontExpression"]
one_child += ["ABlockSubstitution", "AChoiceOrSubstitution", "ATransRelationExpression", "ATransFunctionExpression"]


# AST leafs
no_child =  ["AStringSetExpression", "AEmptySetExpression", "AEmptySequenceExpression", "AIntegerSetExpression"]
no_child += ["ANatSetExpression", "ANaturalSetExpression", "AIntSetExpression", "ANatural1SetExpression"]
no_child += ["ANat1SetExpression", "ABooleanTrueExpression", "ABoolSetExpression", "ABooleanFalseExpression"]
no_child += ["ASkipSubstitution", "AMinIntExpression", "AMaxIntExpression", "ASuccessorExpression", "APredecessorExpression"]
no_child += ["AEmptySequenceExpression"]



# create parsing function at import time (this is allowed by RPython) 
# using metaprogramming (parses from string to node objects and returns AST-root:
f =  "def my_exec(string):\n"
##f += "\tprint string\n"
f += "\tstack = []\n"
f += "\tfor line in string.split(\"\\n\"):\n"
# special case: AIntegerExpression
f += "\t\tif \"AIntegerExpression\" in line:\n"
f += "\t\t\ts=line.find('(')\n"
f += "\t\t\te=line.find(')')\n"
f += "\t\t\tassert s>0\n"
f += "\t\t\tassert e>0\n"
f += "\t\t\tnumber=int(line[s+1:e])\n"
f += "\t\t\tnode =AIntegerExpression(number)\n"
f += "\t\t\tstack.append(node)\n"
# special case: AIdentifierExpression
f += "\t\telif \"AIdentifierExpression\" in line:\n"
f += "\t\t\ts=line.find('\"')\n"
f += "\t\t\te=line.rfind('\"')\n"
f += "\t\t\tassert s>0\n"
f += "\t\t\tassert e>0\n"
f += "\t\t\tidName=line[s+1:e]\n"
f += "\t\t\tnode =AIdentifierExpression(idName)\n"
f += "\t\t\tstack.append(node)\n"
# special case: AStringExpression
f += "\t\telif \"AStringExpression\" in line:\n"
f += "\t\t\ts=line.find('\"')\n"
f += "\t\t\te=line.rfind('\"')\n"
f += "\t\t\tassert s>0\n"
f += "\t\t\tassert e>0\n"
f += "\t\t\tstring=line[s+1:e]\n"
f += "\t\t\tnode =AStringExpression(string)\n"
f += "\t\t\tstack.append(node)\n"
# special case: AStringExpression
f += "\t\telif \"AFileDefinitionDefinition\" in line:\n"
f += "\t\t\ts=line.find('(')\n"
f += "\t\t\te=line.rfind(')')\n"
f += "\t\t\tassert s>0\n"
f += "\t\t\tassert e>0\n"
f += "\t\t\tidName=line[s+1:e]\n"
f += "\t\t\tnode =AFileDefinitionDefinition(idName)\n"
f += "\t\t\tstack.append(node)\n"
# special case: ADeferredSetSet
f += "\t\telif \"ADeferredSetSet\" in line:\n"
f += "\t\t\ts=line.find('(')\n"
f += "\t\t\te=line.rfind(')')\n"
f += "\t\t\tassert s>0\n"
f += "\t\t\tassert e>0\n"
f += "\t\t\tidName=line[s+1:e]\n"
f += "\t\t\tnode =ADeferredSetSet(idName)\n"
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
# only one parameter: childnum
for node_string in many_children_one_arg:
    f += "\t\telif \""+ node_string +"\" in line:\n"
    f += "\t\t\tassert \",\" not in line\n"
    f += "\t\t\ts1 = line.find(\"\\\"\")\n"
    f += "\t\t\te1 = line.rfind(\"\\\"\")\n"
    f += "\t\t\tassert s1>0\n"
    f += "\t\t\tassert e1>0\n"
    f += "\t\t\tchild_num = int(line[s1+1:e1])\n"
    f += "\t\t\tnode = "+ node_string+"(child_num)\n"
    f += "\t\t\t"+"for i in range(child_num):\n"
    f += "\t\t\t\tnode.children.append(stack.pop())\n"
    f += "\t\t\tnode.children.reverse()\n"
    f += "\t\t\tstack.append(node)\n"
for node_string in many_children_two_args + many_children_three_args + many_children_four_args:
    f += "\t\telif \""+ node_string +"\" in line:\n"
    f += "\t\t\tassert \",\" in line\n"
    f += "\t\t\targ_str = line.split(\",\")\n"
    f += "\t\t\targs = []\n"
    f += "\t\t\tfor string in arg_str:\n"
    f += "\t\t\t\ts1 = string.find(\"\\\"\")\n"
    f += "\t\t\t\te1 = string.rfind(\"\\\"\")\n"
    f += "\t\t\t\tassert s1>0\n"
    f += "\t\t\t\tassert e1>0\n"
    f += "\t\t\t\targs.append(string[s1+1:e1])\n"
    f += "\t\t\tassert len(args)>1\n"
    if node_string in many_children_two_args:
        f += "\t\t\tnode = "+ node_string+"(args[0],args[1])\n"
    elif node_string in many_children_three_args:
        f += "\t\t\tnode = "+ node_string+"(args[0], args[1], args[2])\n"
    elif node_string in many_children_four_args:
        f += "\t\t\tnode = "+ node_string+"(args[0], args[1], args[2], args[3])\n"
    f += "\t\t\tchild_num=int(args[0])\n"   
    f += "\t\t\t"+"for i in range(child_num):\n"
    f += "\t\t\t\tnode.children.append(stack.pop())\n" 
    f += "\t\t\tnode.children.reverse()\n" 
    f += "\t\t\tstack.append(node)\n"  
f += "\tassert len(stack)==1\n"
f += "\troot = stack.pop()\n"
f += "\treturn root\n"
#print f
exec(f) 

# AMachineHeader(childNum="0", idName="SIMPLE")
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
    #print_ast(root)
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

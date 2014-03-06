# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from environment import Environment
from util import type_with_known_types, get_type_by_name
from helpers import file_to_AST_str, string_to_file
from parsing import parse_ast, str_ast_to_python_ast
from definition_handler import DefinitionHandler

file_name = "input.txt"

class TestTypesDefinitions():
    def test_types_int_def(self):
        # Build AST
        string = '''
        MACHINE Test
        DEFINITIONS Knampf == NAT
        VARIABLES z
        INVARIANT z:Knampf
        INITIALISATION z:=4
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        dh = DefinitionHandler(env)
        dh.repl_defs(root)
        parse_ast(root,env)
        lst = []
        type_with_known_types(root, env, lst, ["z"])
        assert isinstance(get_type_by_name(env, "z"), IntegerType)


    def test_types_two_para_def(self):
        # Build AST
        string='''
        MACHINE Test
        VARIABLES z
        INVARIANT z:MyDef(NAT,{0})
        INITIALISATION z:= MyDef(5,1)
        DEFINITIONS MyDef(X,Y) == X-Y;
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        dh = DefinitionHandler(env)
        dh.repl_defs(root)
        parse_ast(root, env)
        lst = []
        type_with_known_types(root, env, lst, ["z"])
        assert isinstance(get_type_by_name(env, "z"), IntegerType)
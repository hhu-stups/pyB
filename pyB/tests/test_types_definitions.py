# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from environment import Environment
from typing import _test_typeit
from helpers import file_to_AST_str, string_to_file
from parsing import parse_ast
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
        exec ast_string

        # Type
        dh = DefinitionHandler()
        dh.repl_defs(root)
        env = Environment()
        parse_ast(root,env)
        lst = []
        _test_typeit(root, env, lst, ["z"])
        assert isinstance(env.get_type("z"), IntegerType)


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
        exec ast_string

        # Type
        dh = DefinitionHandler()
        dh.repl_defs(root)
        env = Environment()
        parse_ast(root, env)
        lst = []
        _test_typeit(root, env, lst, ["z"])
        assert isinstance(env.get_type("z"), IntegerType)
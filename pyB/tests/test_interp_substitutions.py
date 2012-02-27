# -*- coding: utf-8 -*-
# also typchecking-tests
from ast_nodes import *
from interp import Environment
from typing import _test_typeit, IntegerType, PowerSetType, SetType, CartType, EmptySetType, StringType, BoolType
from interp import interpret, Environment
from helpers import file_to_AST_str, string_to_file

file_name = "input.txt"

class TestInterpSubstitutions():
    def test_genAST_sub_simple_asgn(self):
        # Build AST
        string = '''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx:=3
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")==3
        assert isinstance(env.get_type("xx"), IntegerType)



    def test_genAST_sub_parallel_asgn(self):
        # Build AST
        string = '''
        MACHINE Test
        VARIABLES xx, yy
        INVARIANT xx:NAT & yy:NAT
        INITIALISATION xx:=1 || yy:= 2
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")==1
        assert env.get_value("yy")==2
        assert isinstance(env.get_type("xx"), IntegerType)
        assert isinstance(env.get_type("yy"), IntegerType)


    def test_genAST_sub_multiple_asgn(self):
        # Build AST
        string = '''
        MACHINE Test
        VARIABLES xx, yy
        INVARIANT xx:NAT & yy:NAT
        INITIALISATION xx,yy:=1,2
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")==1
        assert env.get_value("yy")==2
        assert isinstance(env.get_type("xx"), IntegerType)
        assert isinstance(env.get_type("yy"), IntegerType)


    def test_genAST_sub_bool(self):
        # Build AST
        string = '''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:BOOL
        INITIALISATION xx := bool(1<2)
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")==True
        assert isinstance(env.get_type("xx"), BoolType)
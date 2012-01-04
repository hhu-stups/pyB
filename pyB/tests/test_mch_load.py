# -*- coding: utf-8 -*-
from ast_nodes import *
from interp import interpret, Environment
from helpers import file_to_AST_str, string_to_file

file_name = "input.txt"

class TestMCHLaod():
    def test_examples_simple_acounter(self):
        string = '''
        MACHINE ACounter

        ABSTRACT_VARIABLES  ii,jj

        INVARIANT  ii:0..10 & jj:0..10 & ii<11 & jj>=0

        INITIALISATION ii,jj := 2,10

        END'''

        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)


    def test_examples_simple_bakery0(self):
        string ='''
        MACHINE Bakery0

        ABSTRACT_VARIABLES  aa

        INVARIANT  aa:0..2

        INITIALISATION aa:=0

        END'''

        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)


    def test_examples_simple_bakery1(self):
        string ='''
        MACHINE Bakery1

        ABSTRACT_VARIABLES  p1, p2, y1, y2

        INVARIANT  
                p1:0..2 & p2:0..2 & y1:NATURAL & y2:NATURAL &
                (p1=2 => p2<2) &
                (p2=2 => p1<2) 

        INITIALISATION  p1,p2,y1,y2 := 0,0,0,0

        END'''

        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
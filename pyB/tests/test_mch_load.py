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
        #OPERATIONS
        #        inc = SELECT jj>0 THEN ii:= ii+1  || jj:=jj-1 END ;
        #        result  <-- res = result := ii
        #END'''

        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # inti VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
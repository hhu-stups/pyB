# -*- coding: utf-8 -*-
import pytest
from interp import interpret
from environment import Environment
from util import arbitrary_init_machine
from helpers import file_to_AST_str, string_to_file
from parsing import parse_ast, str_ast_to_python_ast
from typing import type_check_bmch
from ast_nodes import *
from symbolic_sets import *

file_name = "input.txt"

class TestSymbolicSequences():
    import pytest
    @pytest.mark.xfail 
    def test_symbolic_sequences_first(self):
        # Build AST
        string_to_file("#PREDICATE first(%x.(x:NATURAL|x))=1", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        assert 1==2 # Timeout exception missing
        assert interpret(root, env)

    import pytest
    @pytest.mark.xfail         
    def test_symbolic_sequences_first2(self):
        # Build AST
        string_to_file("#PREDICATE (0,0):%x.(x:NATURAL|x) & first(%x.(x:NATURAL|x))=1", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        assert 1==2 # Timeout exception missing
        assert interpret(root, env)
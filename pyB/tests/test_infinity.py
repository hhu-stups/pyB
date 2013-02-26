# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from environment import Environment
from interp import interpret
from helpers import file_to_AST_str, string_to_file

file_name = "input.txt"

class TestInfinity():
    def test_infinity(self):
        # Build AST
        string_to_file("#PREDICATE {}:INT+->>INT", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert not interpret(root.children[0], env)
# -*- coding: utf-8 -*-
from ast_nodes import *
from environment import Environment
from interp import interpret
from helpers import file_to_AST_str, string_to_file

file_name = "input.txt"

class TestQuickEnum():
    def test_quick_relation_member(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2,3,4,5} & T={1,2,3,4,5} & {(1,2)}:S<->T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.bstate.add_ids_to_frame(["S","T"])
        assert interpret(root.children[0], env)


    def test_quick_relation_member2(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2,3,4,5} & T={1,2,3,4,5} & {(6,2)}:S<->T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.bstate.add_ids_to_frame(["S","T"])
        assert not interpret(root.children[0], env)
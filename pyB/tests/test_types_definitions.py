# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from interp import Environment
from typing import _test_typeit
from helpers import file_to_AST_str, string_to_file

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
        env = Environment()
        lst = []
        _test_typeit(root, env, lst, ["z"])
        assert isinstance(env.get_type("z"), IntegerType)
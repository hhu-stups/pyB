# -*- coding: utf-8 -*-
from ast_nodes import *
from interp import Environment
from typing import typeit, IntegerType, PowerSetType, SetType, CartType
from helpers import file_to_AST_str, string_to_file

file_name = "input.txt"

class TestTypesRelations():
    def test_types_relation(self):
        # Build AST
        string_to_file("#PREDICATE r=S<->T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["r"] = None
        env.variable_type["S"] = PowerSetType(SetType("X"))
        env.variable_type["T"] = PowerSetType(SetType("X"))
        typeit(root, env)
        assert isinstance(env.variable_type["r"], PowerSetType)
        assert isinstance(env.variable_type["r"].data, PowerSetType)
        assert isinstance(env.variable_type["r"].data.data, CartType)
        assert isinstance(env.variable_type["r"].data.data.data[0], SetType)
        assert isinstance(env.variable_type["r"].data.data.data[1], SetType)


    def test_types_domain(self):
        # Build AST
        string_to_file("#PREDICATE r:S<->T & x:dom(r)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["r"] = None
        env.variable_type["x"] = None
        env.variable_type["S"] = PowerSetType(SetType("X"))
        env.variable_type["T"] = PowerSetType(SetType("Y"))
        typeit(root, env)
        assert isinstance(env.variable_type["x"], SetType)
        assert env.variable_type["x"].data == "X"


    def test_types_range(self):
        # Build AST
        string_to_file("#PREDICATE r:S<->T & x:ran(r)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["r"] = None
        env.variable_type["x"] = None
        env.variable_type["S"] = PowerSetType(SetType("X"))
        env.variable_type["T"] = PowerSetType(SetType("Y"))
        typeit(root, env)
        assert isinstance(env.variable_type["x"], SetType)
        assert env.variable_type["x"].data == "Y"


    def test_types_fwd_comp(self):
        # Build AST
        string_to_file("#PREDICATE r0:S<->T & r1:T<->S & x:ran(r1;r0)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["r0"] = None
        env.variable_type["r1"] = None
        env.variable_type["x"] = None
        env.variable_type["S"] = PowerSetType(SetType("X"))
        env.variable_type["T"] = PowerSetType(SetType("Y"))
        typeit(root, env)
        assert isinstance(env.variable_type["x"], SetType)
        assert env.variable_type["x"].data == "X"
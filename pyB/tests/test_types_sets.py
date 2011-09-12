# -*- coding: utf-8 -*-
from ast_nodes import *
from interp import Environment
from typing import typeit, IntegerType, PowerSetType, SetType
from helpers import file_to_AST_str, string_to_file

file_name = "input.txt"

class TestTypesSets():
    def test_types_card(self):
        # Build AST
        string_to_file("#PREDICATE card(S)=3", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["S"] = None
        env.variable_values["S"] = set(["Huey", "Dewey", "Louie"])
        typeit(root, env)


    def test_types_simple_set(self):
        # Build AST
        string_to_file("#PREDICATE ID={aa,bb}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["ID"] = None
        env.variable_values["aa"] = "aa"
        env.variable_values["bb"] = "bb"
        env.variable_values["ID"] = set(["aa", "bb"])
        typeit(root, env)
        assert isinstance(env.variable_type["ID"], PowerSetType)
        assert isinstance(env.variable_type["ID"].data, SetType)
        assert isinstance(env.variable_type["ID"].data.data, set)


    def test_types_simple_set_empty(self):
        # Build AST
        string_to_file("#PREDICATE ID={}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["ID"] = None
        typeit(root, env)
        assert isinstance(env.variable_type["ID"], PowerSetType)


    def test_types_simple_set_com(self):
        # Build AST
        string_to_file("#PREDICATE ID={x|x<10}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["ID"] = None
        typeit(root, env)
        assert isinstance(env.variable_type["ID"], PowerSetType)
        assert isinstance(env.variable_type["x"], IntegerType)


    def test_types_simple_set_com2(self):
        # Build AST
        string_to_file("#PREDICATE S={a,b} & ID={x,y|x<10 & y:S}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["ID"] = None
        env.variable_type["S"] = None
        env.variable_type["a"] = "a"
        env.variable_type["b"] = "b"
        typeit(root, env)
        assert isinstance(env.variable_type["S"], PowerSetType)
        assert isinstance(env.variable_type["ID"], PowerSetType)
        assert isinstance(env.variable_type["x"], IntegerType)
        assert isinstance(env.variable_type["y"], SetType)
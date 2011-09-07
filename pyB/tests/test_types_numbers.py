# -*- coding: utf-8 -*-
from ast_nodes import *
from interp import Environment
from typing import typeit, IntegerType, PowerSetType
from helpers import file_to_AST_str, string_to_file

file_name = "input.txt"

class TestTypesNumbers():
    def test_types_simple_nat(self):
        # Build AST
        string_to_file("#PREDICATE x:NAT", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["x"] = None
        assert env.variable_type["x"] == None
        typeit(root, env)
        assert isinstance(env.variable_type["x"], IntegerType)


    def test_types_simple_nat1(self):
        # Build AST
        string_to_file("#PREDICATE x:NAT1", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["x"] = None
        assert env.variable_type["x"] == None
        typeit(root, env)
        assert isinstance(env.variable_type["x"], IntegerType)


    def test_types_simple_add(self):
        # Build AST
        string_to_file("#PREDICATE x=1+1", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["x"] = None
        assert env.variable_type["x"] == None
        typeit(root, env)
        assert isinstance(env.variable_type["x"], IntegerType)


    def test_types_simple_sub(self):
        # Build AST
        string_to_file("#PREDICATE x=1-1", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["x"] = None
        assert env.variable_type["x"] == None
        typeit(root, env)
        assert isinstance(env.variable_type["x"], IntegerType)


    def test_types_simple_mul(self):
        # Build AST
        string_to_file("#PREDICATE x=4*7", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["x"] = None
        assert env.variable_type["x"] == None
        typeit(root, env)
        assert isinstance(env.variable_type["x"], IntegerType)


    def test_types_simple_div(self):
        # Build AST
        string_to_file("#PREDICATE x=8/2", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["x"] = None
        assert env.variable_type["x"] == None
        typeit(root, env)
        assert isinstance(env.variable_type["x"], IntegerType)


    def test_types_simple_mod(self):
        # Build AST
        string_to_file("#PREDICATE x=8 mod 2", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["x"] = None
        assert env.variable_type["x"] == None
        typeit(root, env)
        assert isinstance(env.variable_type["x"], IntegerType)


    def test_types_simple_equal(self):
        # Build AST
        string_to_file("#PREDICATE x=y", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["y"] = IntegerType(None)
        env.variable_type["x"] = None
        assert env.variable_type["x"] == None
        typeit(root, env)
        assert isinstance(env.variable_type["x"], IntegerType)


    def test_types_simple_equal2(self):
        # Build AST
        string_to_file("#PREDICATE y=x", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["y"] = IntegerType(None)
        env.variable_type["x"] = None
        assert env.variable_type["x"] == None
        typeit(root, env)
        assert isinstance(env.variable_type["x"], IntegerType)


    def test_types_simple_equal3(self):
        # Build AST
        string_to_file("#PREDICATE y=1+1", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["y"] = IntegerType(None)
        typeit(root, env)


    def test_types_simple_equal4(self):
        # Build AST
        string_to_file("#PREDICATE 6*7=41+1", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        typeit(root, env)


    def test_types_sigma(self):
        # Build AST:
        string_to_file("#PREDICATE (SIGMA zz . (zz:1..5 | zz*zz))=55", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["zz"] = None
        typeit(root,env)
        assert isinstance(env.variable_type["zz"], IntegerType)


    def test_types_pi(self):
        # Build AST:
        string_to_file("#PREDICATE (PI zz . (zz:1..5 | zz))=120", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["zz"] = None
        typeit(root,env)
        assert isinstance(env.variable_type["zz"], IntegerType)


    def test_types_gt(self):
        # Build AST:
        string_to_file("#PREDICATE x>5", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["x"] = None
        typeit(root,env)
        assert isinstance(env.variable_type["x"], IntegerType)


    def test_types_ge(self):
        # Build AST:
        string_to_file("#PREDICATE x>=5", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["x"] = None
        typeit(root,env)
        assert isinstance(env.variable_type["x"], IntegerType)


    def test_types_ls(self):
        # Build AST:
        string_to_file("#PREDICATE x<5", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["x"] = None
        typeit(root,env)
        assert isinstance(env.variable_type["x"], IntegerType)


    def test_types_le(self):
        # Build AST:
        string_to_file("#PREDICATE x<=5", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["x"] = None
        typeit(root,env)
        assert isinstance(env.variable_type["x"], IntegerType)


    def test_types_interval(self):
        # Build AST:
        string_to_file("#PREDICATE x:1..5", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["x"] = None
        typeit(root,env)
        assert isinstance(env.variable_type["x"], IntegerType)


    def test_types_interval2(self):
        # Build AST:
        string_to_file("#PREDICATE x=1..5", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["x"] = None
        typeit(root,env)
        assert isinstance(env.variable_type["x"], PowerSetType)
        assert isinstance(env.variable_type["x"].data, IntegerType)
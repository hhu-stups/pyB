# -*- coding: utf-8 -*-
from ast_nodes import *
from interp import Environment
from typing import IntegerType, PowerSetType, _test_typeit
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
        _test_typeit(root, env, [], ["x"])
        assert isinstance(env.get_type("x"), IntegerType)


    def test_types_simple_nat1(self):
        # Build AST
        string_to_file("#PREDICATE x:NAT1", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["x"])
        assert isinstance(env.get_type("x"), IntegerType)


    def test_types_simple_add(self):
        # Build AST
        string_to_file("#PREDICATE x=1+1", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["x"])
        assert isinstance(env.get_type("x"), IntegerType)


    def test_types_simple_sub(self):
        # Build AST
        string_to_file("#PREDICATE x=1-1", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["x"])
        assert isinstance(env.get_type("x"), IntegerType)


    def test_types_simple_mul(self):
        # Build AST
        string_to_file("#PREDICATE x=4*7", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["x"])
        assert isinstance(env.get_type("x"), IntegerType)


    def test_types_simple_div(self):
        # Build AST
        string_to_file("#PREDICATE x=8/2", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["x"])
        assert isinstance(env.get_type("x"), IntegerType)


    def test_types_simple_mod(self):
        # Build AST
        string_to_file("#PREDICATE x=8 mod 2", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["x"])
        assert isinstance(env.get_type("x"), IntegerType)


    # TODO: survie refactoring
    def test_types_simple_equal(self):
        # Build AST
        string_to_file("#PREDICATE x=y", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("y", IntegerType(42))]
        _test_typeit(root, env, lst, ["x"])
        assert isinstance(env.get_type("x"), IntegerType)


    # TODO: survie refactoring 
    def test_types_simple_equal2(self):
        # Build AST
        string_to_file("#PREDICATE y=x", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("y", IntegerType(42))]
        _test_typeit(root, env, lst, ["x"])
        assert isinstance(env.get_type("x"), IntegerType)


    def test_types_simple_equal3(self):
        # Build AST
        string_to_file("#PREDICATE y=1+1", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("y", IntegerType(2))]
        _test_typeit(root, env, lst, ["y"])


    def test_types_simple_equal4(self):
        # Build AST
        string_to_file("#PREDICATE 6*7=41+1", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], [])


    # XXX: maybe wrong test
    def test_types_sigma(self):
        # Build AST:
        string_to_file("#PREDICATE (SIGMA zz . (zz:1..5 | zz*zz))=55", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], [])
        assert isinstance(env.get_type("zz"), IntegerType)


    def test_types_pi(self):
        # Build AST:
        string_to_file("#PREDICATE (PI zz . (zz:1..5 | zz))=120", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], [])
        assert isinstance(env.get_type("zz"), IntegerType)


    def test_types_gt(self):
        # Build AST:
        string_to_file("#PREDICATE x>5", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["x"])
        assert isinstance(env.get_type("x"), IntegerType)


    def test_types_ge(self):
        # Build AST:
        string_to_file("#PREDICATE x>=5", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["x"])
        assert isinstance(env.get_type("x"), IntegerType)


    def test_types_ls(self):
        # Build AST:
        string_to_file("#PREDICATE x<5", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["x"])
        assert isinstance(env.get_type("x"), IntegerType)


    def test_types_le(self):
        # Build AST:
        string_to_file("#PREDICATE x<=5", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["x"])
        assert isinstance(env.get_type("x"), IntegerType)


    def test_types_interval(self):
        # Build AST:
        string_to_file("#PREDICATE x:1..5", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["x"])
        assert isinstance(env.get_type("x"), IntegerType)


    def test_types_interval2(self):
        # Build AST:
        string_to_file("#PREDICATE x=1..5", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["x"])
        assert isinstance(env.get_type("x"), PowerSetType)
        assert isinstance(env.get_type("x").data, IntegerType)

    def test_genAST_expr_equ(self):
        # Build AST
        string_to_file("#PREDICATE x=y & x=1", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        _test_typeit(root, env, [], ["x","y"])
        assert isinstance(env.get_type("x"), IntegerType)
        assert isinstance(env.get_type("y"), IntegerType)


    def test_genAST_expr_equ2(self):
        # Build AST
        string_to_file("#PREDICATE z=x & x=y & x=1", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        _test_typeit(root, env, [], ["x","y","z"])
        assert isinstance(env.get_type("x"), IntegerType)
        assert isinstance(env.get_type("y"), IntegerType)
        assert isinstance(env.get_type("z"), IntegerType)


    def test_genAST_expr_equ3(self):
        # Build AST
        string_to_file("#PREDICATE z=x & x=y & y=1", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        _test_typeit(root, env, [], ["x","y","z"])
        assert isinstance(env.get_type("x"), IntegerType)
        assert isinstance(env.get_type("y"), IntegerType)
        assert isinstance(env.get_type("z"), IntegerType)


    def test_genAST_expr_equ4(self):
        # Build AST
        string_to_file("#PREDICATE z=x & z=1 & x=y", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        _test_typeit(root, env, [], ["x","y","z"])
        assert isinstance(env.get_type("x"), IntegerType)
        assert isinstance(env.get_type("y"), IntegerType)
        assert isinstance(env.get_type("z"), IntegerType)


    def test_genAST_expr_equ5(self):
        # Build AST
        string_to_file("#PREDICATE x=42 & z=x  & x=y", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        _test_typeit(root, env, [], ["x","y","z"])
        assert isinstance(env.get_type("x"), IntegerType)
        assert isinstance(env.get_type("y"), IntegerType)
        assert isinstance(env.get_type("z"), IntegerType)


    def test_genAST_expr_equ6(self):
        # Build AST
        string_to_file("#PREDICATE y=42 & z=x & y=x", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        _test_typeit(root, env, [], ["x","y","z"])
        assert isinstance(env.get_type("x"), IntegerType)
        assert isinstance(env.get_type("y"), IntegerType)
        assert isinstance(env.get_type("z"), IntegerType)

    def test_genAST_expr_leq(self):
        # Build AST
        string_to_file("#PREDICATE x<y & y=1", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        _test_typeit(root, env, [], ["x","y"])
        assert isinstance(env.get_type("x"), IntegerType)
        assert isinstance(env.get_type("y"), IntegerType)



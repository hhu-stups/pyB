# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from environment import Environment
from typing import _test_typeit, type_check_bmch
from helpers import file_to_AST_str, string_to_file
from parsing import parse_ast

file_name = "input.txt"

class TestTypesNumbers():
    def test_types_simple_integer(self):
        # Build AST
        string_to_file("#PREDICATE x:INTEGER", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["x"])
        assert isinstance(env.get_type("x"), IntegerType)
        
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


    def test_types_simple_sub_unify(self):
        # Build AST
        string_to_file("#PREDICATE x=a-b & a=42 & b=0", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["x","a","b"])
        assert isinstance(env.get_type("x"), IntegerType)
        assert isinstance(env.get_type("a"), IntegerType)
        assert isinstance(env.get_type("b"), IntegerType)


    def test_types_simple_mul(self):
        # Build AST
        string_to_file("#PREDICATE x=4*7", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["x"])
        assert isinstance(env.get_type("x"), IntegerType)


    def test_types_simple_mul_unify(self):
        # Build AST
        string_to_file("#PREDICATE x=a*b & a=4 & b=7", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["x","b","a"])
        assert isinstance(env.get_type("x"), IntegerType)
        assert isinstance(env.get_type("a"), IntegerType)
        assert isinstance(env.get_type("b"), IntegerType)


    def test_types_simple_mul_unify2(self):
        # Build AST
        string_to_file("#PREDICATE 42=a*b", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["b","a"])
        assert isinstance(env.get_type("a"), IntegerType)
        assert isinstance(env.get_type("b"), IntegerType)


    def test_types_simple_mul_unify3(self):
        # Build AST
        string_to_file("#PREDICATE 42*c=a*b", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["c","b","a"])
        assert isinstance(env.get_type("a"), IntegerType)
        assert isinstance(env.get_type("b"), IntegerType)
        assert isinstance(env.get_type("c"), IntegerType)


    def test_types_simple_mul_unify4(self):
        # Build AST
        string_to_file("#PREDICATE 42=a*b-c", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["a","b","c"])
        assert isinstance(env.get_type("a"), IntegerType)
        assert isinstance(env.get_type("b"), IntegerType)
        assert isinstance(env.get_type("c"), IntegerType)


    def test_types_simple_mul_unify5(self):
        # Build AST
        string_to_file("#PREDICATE d-a*b-c=42", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["a","b","c","d"])
        assert isinstance(env.get_type("a"), IntegerType)
        assert isinstance(env.get_type("b"), IntegerType)
        assert isinstance(env.get_type("c"), IntegerType)
        assert isinstance(env.get_type("d"), IntegerType)

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
        lst = [("y", IntegerType(2))] # number not important
        _test_typeit(root, env, lst, ["y"])


    def test_types_simple_equal4(self):
        # Build AST
        string_to_file("#PREDICATE 6*7=41+1", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], [])


    def test_types_simple_equal5(self):
        # Build AST
        string_to_file("#PREDICATE 2 ** 4 = 16", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], [])


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


    def test_types_ls2(self):
        # Build AST:
        string_to_file("#PREDICATE 1*1<1+1", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], [])


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


    def test_types_expr_equ(self):
        # Build AST
        string_to_file("#PREDICATE x=y & x=1", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["x","y"])
        assert isinstance(env.get_type("x"), IntegerType)
        assert isinstance(env.get_type("y"), IntegerType)


    def test_types_expr_equ2(self):
        # Build AST
        string_to_file("#PREDICATE z=x & x=y & x=1", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["x","y","z"])
        assert isinstance(env.get_type("x"), IntegerType)
        assert isinstance(env.get_type("y"), IntegerType)
        assert isinstance(env.get_type("z"), IntegerType)


    def test_types_expr_equ3(self):
        # Build AST
        string_to_file("#PREDICATE z=x & x=y & y=1", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["x","y","z"])
        assert isinstance(env.get_type("x"), IntegerType)
        assert isinstance(env.get_type("y"), IntegerType)
        assert isinstance(env.get_type("z"), IntegerType)


    def test_types_expr_equ4(self):
        # Build AST
        string_to_file("#PREDICATE z=x & z=1 & x=y", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["x","y","z"])
        assert isinstance(env.get_type("x"), IntegerType)
        assert isinstance(env.get_type("y"), IntegerType)
        assert isinstance(env.get_type("z"), IntegerType)


    def test_types_expr_equ5(self):
        # Build AST
        string_to_file("#PREDICATE x=42 & z=x  & x=y", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["x","y","z"])
        assert isinstance(env.get_type("x"), IntegerType)
        assert isinstance(env.get_type("y"), IntegerType)
        assert isinstance(env.get_type("z"), IntegerType)


    def test_types_expr_equ6(self):
        # Build AST
        string_to_file("#PREDICATE y=42 & z=x & y=x", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["x","y","z"])
        assert isinstance(env.get_type("x"), IntegerType)
        assert isinstance(env.get_type("y"), IntegerType)
        assert isinstance(env.get_type("z"), IntegerType)


    def test_types_expr_equ7(self):
        # Build AST
        string_to_file("#PREDICATE z=x & z=y & z=w & x=1", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["x","y","z","w"])
        assert isinstance(env.get_type("x"), IntegerType)
        assert isinstance(env.get_type("y"), IntegerType)
        assert isinstance(env.get_type("z"), IntegerType)
        assert isinstance(env.get_type("w"), IntegerType)


    def test_types_expr_leq(self):
        # Build AST
        string_to_file("#PREDICATE x<y & y=1", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["x","y"])
        assert isinstance(env.get_type("x"), IntegerType)
        assert isinstance(env.get_type("y"), IntegerType)


    def test_types_expr_maxint(self):
        # Build AST
        string_to_file("#PREDICATE x<MAXINT", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["x"])
        assert isinstance(env.get_type("x"), IntegerType)


    def test_types_expr_minint(self):
        # Build AST
        string_to_file("#PREDICATE x>MININT", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["x"])
        assert isinstance(env.get_type("x"), IntegerType)


    def test_types_exist(self):
        # Build AST
        string_to_file("#PREDICATE #(z).( z<4 & z>0)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["z"])
        assert isinstance(env.get_type("z"), IntegerType)


    def test_types_exist2(self):
        # Build AST
        string_to_file("#PREDICATE S<:NAT & #(z).(z:S)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["S"])
        assert isinstance(env.get_type("z"), IntegerType)
        

    def test_types_exist3(self):
        # Build AST
        string_to_file("#PREDICATE  #(z).(z:S) & S<:NAT", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["S"])
        assert isinstance(env.get_type("z"), IntegerType)


    def test_types_expr_succ(self):
        # Build AST
        string_to_file("#PREDICATE 2=succ(1)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], [])


    def test_types_expr_pred(self):
        # Build AST
        string_to_file("#PREDICATE 2=pred(3)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], [])
  
        
    def test_types_set_or_integer(self):
        string = '''
        MACHINE Test
        CONSTANTS X,yy,sum
        PROPERTIES X-yy=sum+1
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string   

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        assert isinstance(env.get_type("X"), IntegerType)
        assert isinstance(env.get_type("yy"), IntegerType)
        assert isinstance(env.get_type("sum"), IntegerType)


    def test_types_set_or_integer2(self):
        string = '''        
        MACHINE Test
        SETS S ={a,b,c}
        CONSTANTS X,yy,sum
        PROPERTIES X-yy=sum-{a,b,c}
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string   

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        assert isinstance(env.get_type("X").data, SetType)
        assert isinstance(env.get_type("yy").data, SetType)
        assert isinstance(env.get_type("sum").data, SetType)


    def test_types_set_or_integer3(self):
        string = '''        
        MACHINE Test
		SETS S ={a,b,c}
		CONSTANTS x,y,z,w,sum
		PROPERTIES x-y-z=sum-{a,b,c}-w
		END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string   

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        assert isinstance(env.get_type("x").data, SetType)
        assert isinstance(env.get_type("y").data, SetType)
        assert isinstance(env.get_type("z").data, SetType)
        assert isinstance(env.get_type("w").data, SetType)
        assert isinstance(env.get_type("sum").data, SetType)
                

    def test_types_set_or_integer4(self):
        string = '''
        MACHINE Test
        CONSTANTS X,yy,sum
        PROPERTIES X-yy=sum*2
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string   

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        assert isinstance(env.get_type("X"), IntegerType)
        assert isinstance(env.get_type("yy"), IntegerType)
        assert isinstance(env.get_type("sum"), IntegerType)

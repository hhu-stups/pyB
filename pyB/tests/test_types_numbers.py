# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from environment import Environment
from typing import type_check_bmch
from util import type_with_known_types, get_type_by_name
from helpers import file_to_AST_str, string_to_file
from parsing import parse_ast, str_ast_to_python_ast

file_name = "input.txt"

class TestTypesNumbers():
    def test_types_simple_integer(self):
        # Build AST
        string_to_file("#PREDICATE x:INTEGER", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["x"])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)
        
    def test_types_simple_nat(self):
        # Build AST
        string_to_file("#PREDICATE x:NAT", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["x"])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)


    def test_types_simple_nat1(self):
        # Build AST
        string_to_file("#PREDICATE x:NAT1", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["x"])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)


    def test_types_simple_add(self):
        # Build AST
        string_to_file("#PREDICATE x=1+1", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["x"])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)


    def test_types_simple_sub(self):
        # Build AST
        string_to_file("#PREDICATE x=1-1", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["x"])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)


    def test_types_simple_sub_unify(self):
        # Build AST
        string_to_file("#PREDICATE x=a-b & a=42 & b=0", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["x","a","b"])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)
        assert isinstance(get_type_by_name(env, "a"), IntegerType)
        assert isinstance(get_type_by_name(env, "b"), IntegerType)


    def test_types_simple_mul(self):
        # Build AST
        string_to_file("#PREDICATE x=4*7", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["x"])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)


    def test_types_simple_mul_unify(self):
        # Build AST
        string_to_file("#PREDICATE x=a*b & a=4 & b=7", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["x","b","a"])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)
        assert isinstance(get_type_by_name(env, "a"), IntegerType)
        assert isinstance(get_type_by_name(env, "b"), IntegerType)


    def test_types_simple_mul_unify2(self):
        # Build AST
        string_to_file("#PREDICATE 42=a*b", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["b","a"])
        assert isinstance(get_type_by_name(env, "a"), IntegerType)
        assert isinstance(get_type_by_name(env, "b"), IntegerType)


    def test_types_simple_mul_unify3(self):
        # Build AST
        string_to_file("#PREDICATE 42*c=a*b", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["c","b","a"])
        assert isinstance(get_type_by_name(env, "a"), IntegerType)
        assert isinstance(get_type_by_name(env, "b"), IntegerType)
        assert isinstance(get_type_by_name(env, "c"), IntegerType)


    def test_types_simple_mul_unify4(self):
        # Build AST
        string_to_file("#PREDICATE 42=a*b-c", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["a","b","c"])
        assert isinstance(get_type_by_name(env, "a"), IntegerType)
        assert isinstance(get_type_by_name(env, "b"), IntegerType)
        assert isinstance(get_type_by_name(env, "c"), IntegerType)


    def test_types_simple_mul_unify5(self):
        # Build AST
        string_to_file("#PREDICATE d-a*b-c=42", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["a","b","c","d"])
        assert isinstance(get_type_by_name(env, "a"), IntegerType)
        assert isinstance(get_type_by_name(env, "b"), IntegerType)
        assert isinstance(get_type_by_name(env, "c"), IntegerType)
        assert isinstance(get_type_by_name(env, "d"), IntegerType)

    def test_types_simple_div(self):
        # Build AST
        string_to_file("#PREDICATE x=8/2", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["x"])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)


    def test_types_simple_mod(self):
        # Build AST
        string_to_file("#PREDICATE x=8 mod 2", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["x"])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)


    def test_types_simple_equal(self):
        # Build AST
        string_to_file("#PREDICATE x=y", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("y", IntegerType())]
        type_with_known_types(root, env, lst, ["x"])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)


    def test_types_simple_equal2(self):
        # Build AST
        string_to_file("#PREDICATE y=x", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("y", IntegerType())]
        type_with_known_types(root, env, lst, ["x"])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)


    def test_types_simple_equal3(self):
        # Build AST
        string_to_file("#PREDICATE y=1+1", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("y", IntegerType())] # number not important
        type_with_known_types(root, env, lst, ["y"])


    def test_types_simple_equal4(self):
        # Build AST
        string_to_file("#PREDICATE 6*7=41+1", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], [])


    def test_types_simple_equal5(self):
        # Build AST
        string_to_file("#PREDICATE 2 ** 4 = 16", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], [])


    def test_types_sigma(self):
        # Build AST:
        string_to_file("#PREDICATE (SIGMA zz . (zz:1..5 | zz*zz))=55", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], [])
        assert isinstance(get_type_by_name(env, "zz"), IntegerType)


    def test_types_pi(self):
        # Build AST:
        string_to_file("#PREDICATE (PI zz . (zz:1..5 | zz))=120", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], [])
        assert isinstance(get_type_by_name(env, "zz"), IntegerType)


    def test_types_gt(self):
        # Build AST:
        string_to_file("#PREDICATE x>5", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["x"])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)


    def test_types_ge(self):
        # Build AST:
        string_to_file("#PREDICATE x>=5", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["x"])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)


    def test_types_ls(self):
        # Build AST:
        string_to_file("#PREDICATE x<5", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["x"])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)


    def test_types_ls2(self):
        # Build AST:
        string_to_file("#PREDICATE 1*1<1+1", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], [])


    def test_types_le(self):
        # Build AST:
        string_to_file("#PREDICATE x<=5", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["x"])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)


    def test_types_interval(self):
        # Build AST:
        string_to_file("#PREDICATE x:1..5", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["x"])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)


    def test_types_interval2(self):
        # Build AST:
        string_to_file("#PREDICATE x=1..5", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["x"])
        assert isinstance(get_type_by_name(env, "x"), PowerSetType)
        assert isinstance(get_type_by_name(env, "x").data, IntegerType)


    def test_types_expr_equ(self):
        # Build AST
        string_to_file("#PREDICATE x=y & x=1", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["x","y"])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)
        assert isinstance(get_type_by_name(env, "y"), IntegerType)


    def test_types_expr_equ2(self):
        # Build AST
        string_to_file("#PREDICATE z=x & x=y & x=1", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["x","y","z"])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)
        assert isinstance(get_type_by_name(env, "y"), IntegerType)
        assert isinstance(get_type_by_name(env, "z"), IntegerType)


    def test_types_expr_equ3(self):
        # Build AST
        string_to_file("#PREDICATE z=x & x=y & y=1", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["x","y","z"])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)
        assert isinstance(get_type_by_name(env, "y"), IntegerType)
        assert isinstance(get_type_by_name(env, "z"), IntegerType)


    def test_types_expr_equ4(self):
        # Build AST
        string_to_file("#PREDICATE z=x & z=1 & x=y", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["x","y","z"])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)
        assert isinstance(get_type_by_name(env, "y"), IntegerType)
        assert isinstance(get_type_by_name(env, "z"), IntegerType)


    def test_types_expr_equ5(self):
        # Build AST
        string_to_file("#PREDICATE x=42 & z=x  & x=y", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["x","y","z"])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)
        assert isinstance(get_type_by_name(env, "y"), IntegerType)
        assert isinstance(get_type_by_name(env, "z"), IntegerType)


    def test_types_expr_equ6(self):
        # Build AST
        string_to_file("#PREDICATE y=42 & z=x & y=x", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["x","y","z"])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)
        assert isinstance(get_type_by_name(env, "y"), IntegerType)
        assert isinstance(get_type_by_name(env, "z"), IntegerType)


    def test_types_expr_equ7(self):
        # Build AST
        string_to_file("#PREDICATE z=x & z=y & z=w & x=1", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["x","y","z","w"])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)
        assert isinstance(get_type_by_name(env, "y"), IntegerType)
        assert isinstance(get_type_by_name(env, "z"), IntegerType)
        assert isinstance(get_type_by_name(env, "w"), IntegerType)


    def test_types_expr_leq(self):
        # Build AST
        string_to_file("#PREDICATE x<y & y=1", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["x","y"])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)
        assert isinstance(get_type_by_name(env, "y"), IntegerType)


    def test_types_expr_maxint(self):
        # Build AST
        string_to_file("#PREDICATE x<MAXINT", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["x"])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)


    def test_types_expr_minint(self):
        # Build AST
        string_to_file("#PREDICATE x>MININT", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["x"])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)


    def test_types_exist(self):
        # Build AST
        string_to_file("#PREDICATE #(z).( z<4 & z>0)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["z"])
        assert isinstance(get_type_by_name(env, "z"), IntegerType)


    def test_types_exist2(self):
        # Build AST
        string_to_file("#PREDICATE S<:NAT & #(z).(z:S)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["S"])
        assert isinstance(get_type_by_name(env, "z"), IntegerType)
        

    def test_types_exist3(self):
        # Build AST
        string_to_file("#PREDICATE  #(z).(z:S) & S<:NAT", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["S"])
        assert isinstance(get_type_by_name(env, "z"), IntegerType)


    def test_types_expr_succ(self):
        # Build AST
        string_to_file("#PREDICATE 2=succ(1)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], [])


    def test_types_expr_pred(self):
        # Build AST
        string_to_file("#PREDICATE 2=pred(3)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], [])
  
        
    def test_types_set_or_integer(self):
        string = '''
        MACHINE Test
        CONSTANTS X,yy,sum
        PROPERTIES X-yy=sum+1
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)   

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        assert isinstance(get_type_by_name(env, "X"), IntegerType)
        assert isinstance(get_type_by_name(env, "yy"), IntegerType)
        assert isinstance(get_type_by_name(env, "sum"), IntegerType)


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
        root = str_ast_to_python_ast(ast_string)   

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        assert isinstance(get_type_by_name(env, "X").data, SetType)
        assert isinstance(get_type_by_name(env, "yy").data, SetType)
        assert isinstance(get_type_by_name(env, "sum").data, SetType)


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
        root = str_ast_to_python_ast(ast_string)   

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        assert isinstance(get_type_by_name(env, "x").data, SetType)
        assert isinstance(get_type_by_name(env, "y").data, SetType)
        assert isinstance(get_type_by_name(env, "z").data, SetType)
        assert isinstance(get_type_by_name(env, "w").data, SetType)
        assert isinstance(get_type_by_name(env, "sum").data, SetType)
                

    def test_types_set_or_integer4(self):
        string = '''
        MACHINE Test
        CONSTANTS X,yy,sum
        PROPERTIES X-yy=sum*2
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)   

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        assert isinstance(get_type_by_name(env, "X"), IntegerType)
        assert isinstance(get_type_by_name(env, "yy"), IntegerType)
        assert isinstance(get_type_by_name(env, "sum"), IntegerType)

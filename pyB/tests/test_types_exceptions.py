# -*- coding: utf-8 -*-
import py.test
from ast_nodes import *
from btypes import *
from environment import Environment
from typing import type_check_bmch, BTypeException
from util import type_with_known_types
from helpers import file_to_AST_str, string_to_file
from parsing import parse_ast, str_ast_to_python_ast
from bexceptions import ResolveFailedException, BTypeException
file_name = "input.txt"

class TestTypesTypeExceptions():
    def test_types_no_resolve(self):
        # Build AST
        string_to_file("#PREDICATE a=b", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type and fail
        env = Environment()
        py.test.raises(BTypeException, "type_with_known_types(root, env, [], [\"a\",\"b\"])")


    def test_types_siple_err(self):
        # Build AST
        string_to_file("#PREDICATE a=NAT & a=42", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type and fail
        env = Environment()
        py.test.raises(BTypeException, "type_with_known_types(root, env, [], [\"a\",\"b\"])")


    def test_types_op_err(self):
        # Build AST
        string_to_file("#PREDICATE a=NAT & b=a+42", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type and fail
        env = Environment()
        py.test.raises(BTypeException, "type_with_known_types(root, env, [], [\"a\",\"b\"])")


    def test_types_op_err2(self):
        # Build AST
        string_to_file("#PREDICATE b=a mod NAT", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type and fail
        env = Environment()
        py.test.raises(BTypeException, "type_with_known_types(root, env, [], [\"a\",\"b\"])")


    def test_types_op_err3(self):
        # Build AST
        string_to_file("#PREDICATE a < NAT", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type and fail
        env = Environment()
        py.test.raises(BTypeException, "type_with_known_types(root, env, [], [\"a\"])")


    def test_types_op_err4(self):
        # Build AST
        string_to_file("#PREDICATE 42*NAT=a", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type and fail
        env = Environment()
        py.test.raises(BTypeException, "type_with_known_types(root, env, [], [\"a\"])")


    def test_types_op_err5(self):
        # Build AST
        string_to_file("#PREDICATE 42-NAT=a", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type and fail
        env = Environment()
        py.test.raises(BTypeException, "type_with_known_types(root, env, [], [\"a\"])")


    def test_types_op_err6(self):
        # Build AST
        string_to_file("#PREDICATE a*b=c & a=42 & b=NAT", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type and fail
        env = Environment()
        #type_with_known_types(root, env, [], ["a","b","c"])
        py.test.raises(BTypeException, "type_with_known_types(root, env, [], [\"a\",\"b\",\"c\"])")


    def test_types_impossible_resolve(self):
        string = '''
        MACHINE Test
        SETS S ={a,b,c}
        CONSTANTS xx,yy,zz
        PROPERTIES xx-yy=zz*{a,b,c}
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)   

        # Test
        env = Environment()
        mch = parse_ast(root, env) 
        py.test.raises(ResolveFailedException, "type_check_bmch(root, env, mch)")
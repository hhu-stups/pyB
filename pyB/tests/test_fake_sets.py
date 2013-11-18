# -*- coding: utf-8 -*-
from environment import Environment
from interp import interpret
from helpers import file_to_AST_str, string_to_file
from parsing import parse_ast
from typing import type_check_bmch
from ast_nodes import *
from fake_sets import *

file_name = "input.txt"


class TestFakeSets():
    def test_fake_cart_prod_right(self):
        string = '''
		MACHINE Test
		VARIABLES x, y, z
		INVARIANT x=INTEGER & y={1,2,3} & z=x*y
		INITIALISATION x:=INTEGER ; y:={1,2,3} ; z:=x*y
		END'''
		# Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string
        
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        interpret(root, env)
        value = env.get_value("z")
        assert isinstance(value, FakeCartSet)
        assert isinstance(value.left_set, IntegerSet)
        assert isinstance(value.right_set, frozenset)


    def test_fake_cart_prod_left(self):
        string = '''
		MACHINE Test
		VARIABLES x, y, z
		INVARIANT y=INTEGER & x={1,2,3} & z=x*y
		INITIALISATION y:=INTEGER ; x:={1,2,3} ; z:=x*y
		END'''
		# Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string
        
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        interpret(root, env)
        value = env.get_value("z")
        assert isinstance(value, FakeCartSet)
        assert isinstance(value.left_set, frozenset)
        assert isinstance(value.right_set, IntegerSet)

    
    def test_fake_set_element_of(self):
        env = Environment()
        inf_set = IntegerSet(env)
        assert 1 in inf_set
        inf_set = NaturalSet(env)
        assert 0 in inf_set
        assert -1 not in inf_set
        inf_set = Natural1Set(env)
        assert 0  not in inf_set
        assert -1 not in inf_set
        assert 1 in inf_set
        large_set = NatSet(env)
        assert 0 in large_set
        assert env._max_int in large_set
        assert -1 not in large_set
        large_set = Nat1Set(env)
        assert 0  not in large_set
        assert env._max_int in large_set
        assert -1 not in large_set
        large_set = IntSet(env)
        assert 0 in large_set
        assert env._max_int in large_set
        assert env._min_int in large_set
        assert -1 in large_set
        assert env._max_int+1 not in large_set
# -*- coding: utf-8 -*-
from ast_nodes import *
from environment import Environment
from interp import interpret
from helpers import file_to_AST_str, string_to_file
from parsing import str_ast_to_python_ast

from config import USE_RPYTHON_CODE
if USE_RPYTHON_CODE:
     from rpython_b_objmodel import frozenset

file_name = "input.txt"

#import pytest
#@pytest.mark.skipif(True, reason="takes to much time") 
class TestQuickEnum():
    def test_quick_relation_member1(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2,3,4,5} & T={1,2,3,4,5} & {(1,2)}:S<->T", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)


    def test_quick_relation_member2(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2,3,4,5} & T={1,2,3,4,5} & {(6,2)}:S<->T", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert not interpret(root, env)


    def test_quick_relation_member3(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2,3} & T={1,2} & {(1,2),(2,1)}:S+->T", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)


    def test_quick_relation_member4(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2,3} & T={1,2} & {(1,2),(2,1)}:S>+>T", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)


    def test_quick_relation_member5(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2,3} & T={1,2} & {(1,2)}:S>+>T", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)


    def test_quick_relation_member6(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2,3} & T={1,2} & {(1,2),(3,2),(2,1)}:S+->>T", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)


    def test_quick_relation_member7(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2,3} & T={1,2} & {(1,2),(3,2),(2,1)}:S>+>>T", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert not interpret(root, env)


    def test_quick_relation_member8(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2,3} & T={1,2} & {(1,2)}:S>+>>T", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert not interpret(root, env)          
 
 
    def test_quick_relation_member9(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2,3} & T={1,2} & {(1,2),(2,1)}:S>+>>T", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)


    def test_quick_relation_member10(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2,3} & T={1,2} & {(1,2),(2,1)}:S-->T", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert not interpret(root, env)


    def test_quick_relation_member11(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2,3} & T={1,2} & {(1,2),(2,1),(3,1)}:S-->T", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)


    def test_quick_relation_member12(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2,3} & T={1,2} & {(1,2),(2,1),(3,1)}:S>->T", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert not interpret(root, env)    


    def test_quick_relation_member13(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2} & T={1,2} & {(1,2),(2,1)}:S>->T", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)


    def test_quick_relation_member14(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2} & T={1,2,3} & {(1,2),(2,1)}:S>->T", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)


    def test_quick_relation_member15(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2,3} & T={1,2} & {(1,2),(2,1),(3,2)}:S-->>T", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)


    def test_quick_relation_member16(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2} & T={1,2} & {(1,2),(2,1)}:S-->>T", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        #env.add_ids_to_frame(["S","T"])
        assert interpret(root, env)


    def test_quick_relation_member17(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2,3} & T={1,2} & {(1,1),(2,1),(3,1)}:S-->>T", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        #env.add_ids_to_frame(["S","T"])
        assert not interpret(root, env)


    def test_quick_relation_member18(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2,3} & T={1,2,3} & {(1,3),(2,1),(3,2)}:S>->>T", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)
        

    def test_quick_powerset_member(self):
        # Build AST
        string_to_file("#PREDICATE S=(1 .. 32) & {1}:POW(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        #env.add_ids_to_frame(["S"])
        assert interpret(root, env)


    def test_quick_cart_member(self):
        # Build AST
        string_to_file("#PREDICATE S=(1 .. 10000) & T=(1..10000) & (1,1):S*T & (9999,9999):S*T", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)


    def test_quick_power_cart_member(self):
        # Build AST
        string_to_file("#PREDICATE S=(1 .. 10000) & T=(1..10000) & {(1,1)}:POW(S*T) & {(9999,9999)}:POW(S*T)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env) 


    def test_quick_power_cart_member2(self):
        # Build AST
        string_to_file("#PREDICATE S=(1 .. 10000) & T=(1..10000) & {(1,0)}:POW(S*T)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert not interpret(root, env)


    def test_quick_power_cart_member3(self):
        # Build AST
        string_to_file("#PREDICATE S=(1 .. 10000) & T=(1..10000) & {(9999,10001)}:POW(S*T)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert not interpret(root, env)         
        

    def test_quick_squence_member(self):
        # Build AST
        string_to_file("#PREDICATE S=(1 .. 5) & T=(1..10000) & R=[{1},{2},{3},{42},{5}] & R:S-->POW(T)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)	
  
        
    def test_quick_squence_member2(self):
        # Build AST
        string_to_file("#PREDICATE S=(1 .. 34) & [1,1,2,2,3,4,5,6,7,7,8,9,10,10,11,11,12,13,14,12,15,16,17,17,18]:seq(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)	        


    def test_quick_squence_member3(self):
        # Build AST
        string_to_file("#PREDICATE S=(0 .. 42) & []/:seq1(S) & [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]:seq1(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)


    def test_quick_squence_member4(self):
        # Build AST
        string_to_file("#PREDICATE S=(0 .. 20) & []:iseq(S) & [0, 2, 4, 8, 10, 12, 14, 16, 18, 20,1,3,5,7,9,11,13,15,17,19]:iseq(S) & [1,1]/:iseq(S) & [42]/:iseq(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)


    def test_quick_squence_member5(self):
        # Build AST
        string_to_file("#PREDICATE S=(0 .. 20) & []/:perm(S) & [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20,1,3,5,7,9,11,13,15,17,19]:perm(S) & [1,1]/:perm(S) & [42]/:perm(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)


    def test_infinite_set_member(self):
        # Build AST
        string_to_file("#PREDICATE {(1,3),(3,2),(2,1)}:NAT>+>NAT", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)


    def test_infinite_set_member2(self):
        # Build AST
        string_to_file("#PREDICATE {(1,3),(3,2),(2,1)}:NAT1>+>NAT1", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)


    def test_infinite_set_member3(self):
        # Build AST
        string_to_file("#PREDICATE {(1,3),(3,2),(2,1)}:NATURAL1>+>NATURAL", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)


    def test_infinite_set_member4(self):
        # Build AST
        string_to_file("#PREDICATE {(1,3),(3,2),(2,1)}:INT>+>INTEGER", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)

    def test_quick_lambda(self):
        pass


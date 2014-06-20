# -*- coding: utf-8 -*-
import pytest
from interp import interpret
from environment import Environment
from util import arbitrary_init_machine
from helpers import file_to_AST_str, string_to_file
from parsing import parse_ast, str_ast_to_python_ast
from typing import type_check_bmch
from ast_nodes import *
from symbolic_sets import *

file_name = "input.txt"


class TestSymbolicSets():
    def test_symbolic_cart_prod_right(self):
        string = '''
		MACHINE Test
		VARIABLES x, y, z
		INVARIANT x=INTEGER & y={1,2,3} & z=x*y
		INITIALISATION x:=INTEGER ; y:={1,2,3} ; z:=x*y
		END'''
		# Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        arbitrary_init_machine(root, env, mch)
        value = env.get_value("z")
        assert isinstance(value, SymbolicCartSet)
        assert isinstance(value.left_set, IntegerSet)
        assert isinstance(value.right_set, frozenset)


    def test_symbolic_cart_prod_left(self):
        string = '''
		MACHINE Test
		VARIABLES x, y, z
		INVARIANT y=INTEGER & x={1,2,3} & z=x*y
		INITIALISATION y:=INTEGER ; x:={1,2,3} ; z:=x*y
		END'''
		# Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        arbitrary_init_machine(root, env, mch)
        value = env.get_value("z")
        assert isinstance(value, SymbolicCartSet)
        assert isinstance(value.left_set, frozenset)
        assert isinstance(value.right_set, IntegerSet)

    
    def test_symbolic_set_element_of(self):
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
        cart_set = large_set * inf_set
        assert (1,1) in cart_set
        assert (-1,-1) not in cart_set
   
        
    def test_symbolic_set_compare(self):
        env = Environment()
        inf_set = IntegerSet(env)
        inf_set2 = IntegerSet(env)
        assert inf_set == inf_set2
        inf_set3 = Natural1Set(env)
        assert not inf_set == inf_set3
        acartSet = inf_set * inf_set3
        acartSet2 = IntegerSet(env) * Natural1Set(env)
        acartSet3 = inf_set3 * inf_set
        assert acartSet==acartSet2
        assert not acartSet==acartSet3
    
    
    def test_symbolic_set_len(self):
        env = Environment()
        large_set = NatSet(env)
        assert len(large_set)== env._max_int +1
        large_set = Nat1Set(env)
        assert len(large_set)== env._max_int 
        large_set = IntSet(env)
        assert len(large_set)== env._max_int + (-1)*env._min_int + 1 
        # no impl. for inf_sets possible with __len__
    
    
    def test_symbolic_set_subset(self):
        env = Environment()
        env._min_int = -2**31
        env._max_int = 2**31
        nat_set = NatSet(env)
        nat1_set = Nat1Set(env)
        int_set = IntSet(env)
        
        assert not nat_set<=nat1_set
        assert nat_set<=int_set
        assert nat_set<=nat_set
        assert not nat_set<nat_set
        assert nat_set>=nat_set
        
        assert nat1_set<=nat_set
        assert nat1_set<=int_set
        assert nat1_set<=nat1_set
        assert not nat1_set<nat1_set
        assert nat1_set>=nat1_set
        
        assert not int_set<=nat_set
        assert not int_set<=nat1_set
        assert int_set<=int_set
        assert not int_set<int_set
        assert int_set>=int_set
        
        natural_set = NaturalSet(env)
        natural1_set = Natural1Set(env)
        integer_set = IntegerSet(env)
        
        assert not natural_set<=natural1_set
        assert natural_set<=integer_set
        assert natural_set<=natural_set
        assert not natural_set<natural_set
        assert natural_set>=natural_set
        
        assert natural1_set<=natural_set
        assert natural1_set<=integer_set
        assert natural1_set<=natural1_set
        assert not natural1_set<natural1_set
        assert natural1_set>=natural1_set
        
        assert not integer_set<=natural_set
        assert integer_set<=integer_set
        assert not integer_set<=natural1_set
        assert not integer_set<integer_set
        assert integer_set>=integer_set


    def test_symbolic_set_union(self):
        env = Environment()
        env._min_int = -2**31
        env._max_int = 2**31
        nat_set = NatSet(env)
        nat1_set = Nat1Set(env)
        int_set = IntSet(env)
        natural_set = NaturalSet(env)
        natural1_set = Natural1Set(env)
        integer_set = IntegerSet(env)
        
        assert (nat_set | nat_set) ==nat_set
        assert (nat_set | nat1_set)==nat1_set
        assert (nat_set | int_set) ==int_set
        assert (nat_set | natural_set) ==natural_set
        assert (nat_set | natural1_set) ==natural1_set
        assert (nat_set | integer_set) ==integer_set
        
    
    def test_symbolic_proj1(self):
        # Build AST
        string_to_file("#PREDICATE prj1(INTEGER*INTEGER,INTEGER)((1,42,1))=(1|->42)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test fapp
        env = Environment()
        assert interpret(root.children[0], env)
        
        # Build AST
        string_to_file("#PREDICATE (((1,2),42),(1,2)):prj1(INTEGER*INTEGER,INTEGER)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test membership
        env = Environment()
        assert interpret(root.children[0], env)       
        

    def test_symbolic_proj2(self):
        # Build AST
        string_to_file("#PREDICATE prj2(INTEGER*INTEGER,INTEGER)((1,1,42))=(42)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test fapp
        env = Environment()
        assert interpret(root.children[0], env)
        
        # Build AST
        string_to_file("#PREDICATE (((1,1),42),42):prj2(INTEGER*INTEGER,INTEGER)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test membership
        env = Environment()
        assert interpret(root.children[0], env)      

    
    def test_symbolic_relation_set(self):
        # Build AST
        string_to_file("#EXPRESSION INTEGER<->INTEGER", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test creation 
        env = Environment()
        print interpret(root.children[0], env)  
        
    import pytest
    @pytest.mark.xfail 
    def test_symbolic_function_set1(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2} & {(1,1),(2,-1)}:S-->NAT ", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test creation 
        env = Environment()
        assert not interpret(root.children[0], env)  
 
    #append
    import pytest
    @pytest.mark.xfail 
    def test_symbolic_function_set2(self):
        # Build AST
        string_to_file("#PREDICATE %(x,y).(x: STRING & y: STRING | x):STRING*STRING --> STRING", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test creation 
        env = Environment()
        assert interpret(root.children[0], env)         
               

    import pytest
    @pytest.mark.xfail
    def test_symbolic_lambda1(self):
        # Build AST
        string_to_file("#PREDICATE %x.(x:NAT|x*x)(25)=625", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test fapp
        env = Environment()
        assert interpret(root, env)        


    def test_symbolic_lambda2(self):
        # Build AST
        string_to_file("#PREDICATE %(x,y).(x:NAT & y:NAT|x*y)(5,5)=25", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test fapp
        env = Environment()
        assert interpret(root, env)        

 
    # TODO: typeinformation for lambdaexpr images
    # typeinformation for * and - nodes 
    #import pytest
    #@pytest.mark.xfail
    def test_symbolic_lambda3(self):
        # Build AST
        string_to_file("#PREDICATE %x.(x:INTEGER|x*x):INTEGER<->INTEGER", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)  
        
        # Test fapp
        env = Environment()
        assert interpret(root, env)      
        
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
        inf_set = IntegerSet(env, interpret)
        assert 1 in inf_set
        inf_set = NaturalSet(env, interpret)
        assert 0 in inf_set
        assert -1 not in inf_set
        inf_set = Natural1Set(env, interpret)
        assert 0  not in inf_set
        assert -1 not in inf_set
        assert 1 in inf_set
        large_set = NatSet(env, interpret)
        assert 0 in large_set
        assert env._max_int in large_set
        assert -1 not in large_set
        large_set = Nat1Set(env, interpret)
        assert 0  not in large_set
        assert env._max_int in large_set
        assert -1 not in large_set
        large_set = IntSet(env, interpret)
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
        inf_set = IntegerSet(env, interpret)
        inf_set2 = IntegerSet(env, interpret)
        assert inf_set == inf_set2
        inf_set3 = Natural1Set(env, interpret)
        assert not inf_set == inf_set3
        acartSet = inf_set * inf_set3
        acartSet2 = IntegerSet(env, interpret) * Natural1Set(env, interpret)
        acartSet3 = inf_set3 * inf_set
        assert acartSet==acartSet2
        assert not acartSet==acartSet3
    
    
    def test_symbolic_set_len(self):
        env = Environment()
        large_set = NatSet(env, interpret)
        assert len(large_set)== env._max_int +1
        large_set = Nat1Set(env, interpret)
        assert len(large_set)== env._max_int 
        large_set = IntSet(env, interpret)
        assert len(large_set)== env._max_int + (-1)*env._min_int + 1 
        # no impl. for inf_sets possible with __len__
    
    
    def test_symbolic_set_subset(self):
        env = Environment()
        env._min_int = -2**31
        env._max_int = 2**31
        nat_set = NatSet(env, interpret)
        nat1_set = Nat1Set(env, interpret)
        int_set = IntSet(env, interpret)
        
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
        
        natural_set = NaturalSet(env, interpret)
        natural1_set = Natural1Set(env, interpret)
        integer_set = IntegerSet(env, interpret)
        
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
        nat_set = NatSet(env, interpret)
        nat1_set = Nat1Set(env, interpret)
        int_set = IntSet(env, interpret)
        natural_set = NaturalSet(env, interpret)
        natural1_set = Natural1Set(env, interpret)
        integer_set = IntegerSet(env, interpret)
        
        assert (nat_set | nat_set) ==nat_set
        assert (nat_set | nat1_set)==nat1_set
        assert (nat_set | int_set) ==int_set
        assert (nat_set | natural_set) ==natural_set
        assert (nat_set | natural1_set) ==natural1_set
        assert (nat_set | integer_set) ==integer_set
        
    
    
    def test_symbolic_string_set(self):
        # Build AST
        string_to_file("#PREDICATE STRING<:STRING", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test 
        env = Environment()
        assert interpret(root.children[0], env)
 
        # Build AST
        string_to_file("#PREDICATE STRING<<:STRING", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test 
        env = Environment()
        assert not interpret(root.children[0], env)       
        
        # Build AST
        string_to_file("#PREDICATE {\"hello world\"}<:STRING", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test 
        env = Environment()
        assert interpret(root.children[0], env)
        
        # Build AST
        string_to_file("#PREDICATE STRING<:{\"hello world\"}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test 
        env = Environment()
        assert not interpret(root.children[0], env)

            
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

    #TODO: implement equality for proj1 (x=prj1(INTEGER,INTEGER) & y=prj1(INTEGER,INTEGER) & x=y)
 
    def test_symbolic_relation_set(self):
        # Build AST
        string_to_file("#EXPRESSION INTEGER<->INTEGER", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test creation 
        env = Environment()
        print interpret(root.children[0], env)  
        

    # munis one not element of NAT
    def test_symbolic_function_set1(self):
        # Build AST
        string_to_file("#PREDICATE {(1,1),(2,-1)}:{1,2}-->NAT ", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test creation 
        env = Environment()
        assert not interpret(root.children[0], env)  
 

    def test_symbolic_function_set2(self):
        # Build AST
        string_to_file("#PREDICATE %(x,y).(x: STRING & y: STRING | x):STRING*STRING --> STRING", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test creation 
        env = Environment()
        assert interpret(root, env)         
               

    # This test fails if max_int=5. (25 is not in domain)
    def test_symbolic_lambda1(self):
        # Build AST
        string_to_file("#PREDICATE %x.(x:NAT|x*x)(25)=625", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test fapp
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32 
        assert interpret(root, env)        


    def test_symbolic_lambda2(self):
        # Build AST
        string_to_file("#PREDICATE %(x,y).(x:NAT & y:NAT|x*y)(5,5)=25", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test fapp
        env = Environment()
        assert interpret(root, env)        

 
    # TODO: typeinformation for * and - nodes 
    def test_symbolic_lambda3(self):
        # Build AST
        string_to_file("#PREDICATE %x.(x:INTEGER|x*x):INTEGER<->INTEGER", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)  
        
        # Test fapp
        env = Environment()
        assert interpret(root, env)  

   
    # TODO: Handle timeout enumeration
    import pytest
    @pytest.mark.xfail    
    def test_symbolic_lambda_composition1(self):
        # Build AST
        string_to_file("#PREDICATE {(4,42),(5,42)}=(%x.(x:INTEGER|x*x);{(25,42),(16,42),(42,42)})", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)  
        
        # Test fapp
        env = Environment()
        assert interpret(root, env)  
 
  
    def test_symbolic_lambda_composition2(self):
        # Build AST
        string_to_file("#PREDICATE {(16,1764),(25,1764),(42,1764)}=({(25,42),(16,42),(42,42)};%x.(x:INTEGER|x*x))", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)  
        
        # Test fapp
        env = Environment()
        assert interpret(root, env)  



    def test_symbolic_lambda_composition3(self):
        # Build AST
        string_to_file("#PREDICATE {(2,12)}=({(2,(3,4))};(%(x,y).(x:INTEGER & y:INTEGER|y*x)))", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)  
        
        # Test fapp
        env = Environment()
        assert interpret(root, env)
        
  
    def test_symbolic_lambda_composition4(self):
        # Build AST
        string_to_file("#PREDICATE {(2,17)}=({(2,(3,4,5))};(%(x,y,z).(x:INTEGER & y:INTEGER & z:INTEGER|y*x+z)))", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)  
        
        # Test fapp
        env = Environment()
        assert interpret(root, env) 
        
        # Build AST (brackets)
        string_to_file("#PREDICATE {(2,17)}=({(2,((3,4),5))};(%(x,y,z).(x:INTEGER & y:INTEGER & z:INTEGER|y*x+z)))", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)  
        
        # Test fapp
        env = Environment()
        assert interpret(root, env) 
        

    def test_symbolic_lambda_composition5(self):
        # Build AST
        string_to_file("#PREDICATE {(2,7)}=({(2,(3,4))};(%(x).(x:INTEGER*INTEGER|%(a,b).(a:INTEGER & b:INTEGER|a+b)(x)))) ", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)  
        
        # Test fapp
        env = Environment()
        assert interpret(root, env) 

    # this checks if equality is symmetric 
    def test_symbolic_lambda_composition6(self):
        # Build AST
        string_to_file("#PREDICATE ({(25,42),(16,42),(42,42)};%x.(x:INTEGER|x*x))={(16,1764),(25,1764),(42,1764)}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)  
        
        # Test fapp
        env = Environment()
        assert interpret(root, env)         
        

    # checks lambda image app. (get_item method)
    def test_symbolic_lambda_composition7(self):
        # Build AST
        string_to_file("#PREDICATE maxi = 4 & S = 0..maxi-1 & (%(x,y).(x: S & y: NATURAL | x|->1|->y))[S<|{0|->19189,1|->9877,2|->28924,3|->877,4|->0, 5|->0}]={((0|->1)|->19189),((1|->1)|->9877), ((2|->1)|->28924), ((3|->1)|-> 877)}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)  
        
        # Test fapp
        env = Environment()
        assert interpret(root, env)   
        
 
    # checks lambda image app. (get_item method) with empty argument
    def test_symbolic_lambda_composition8(self):
        # Build AST
        string_to_file("#PREDICATE {}=(%(x,y).(x:0..4 & y:NATURAL|x|->1|->y)[{}])", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)  
        
        # Test fapp
        env = Environment()
        assert interpret(root, env)            


    import pytest
    @pytest.mark.xfail
    def test_symbolic_lambda_ran(self):
        # Build AST
        string_to_file("#PREDICATE ran((%x.(x:NAT|42)))={42}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)  
        
        # Test fapp
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32 
        assert 1==2 # prevent Timeout (timeout not implemented yet)
        assert interpret(root, env) 

    import pytest
    @pytest.mark.xfail 
    def test_symbolic_set_comp_ran(self):
        # Build AST
        string_to_file("#PREDICATE ran({x| #(y).(y:NAT & x:NAT*NAT & x=(y,42))})={42}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)  
        
        # Test fapp
        env = Environment()
        assert interpret(root, env) 
        
    import pytest
    @pytest.mark.xfail        
    def test_symbolic_set_comp_dom(self):
        # Build AST
        string_to_file("#PREDICATE dom({x| #(y).(y:NAT & x:NAT*NAT & x=(42,y))})={42}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)  
        
        # Test fapp
        env = Environment()
        assert interpret(root, env) 


    def test_symbolic_lambda_convert_explicit(self):
        # Build AST
        string_to_file("#PREDICATE %(x).(x:NATURAL & x<5|x)={(0,0),(1,1),(2,2),(3,3),(4,4)}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)  
        
        # Test enum
        env = Environment()
        assert interpret(root, env) 
        
       
    def test_symbolic_powerset(self):
        # Build AST
        string_to_file("#PREDICATE {1,2,3}:POW(NATURAL)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)  
        
        # Test 
        env = Environment()
        assert interpret(root, env)       


    def test_symbolic_powerset2(self):
        # Build AST
        string_to_file("#PREDICATE {-1,2,3}:POW(NATURAL)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)  
        
        # Test 
        env = Environment()
        assert not interpret(root, env)

 
    import pytest
    @pytest.mark.xfail 
    def test_symbolic_powerset3(self):
        # Build AST
        string_to_file("#PREDICATE POW(NATURAL)/\{{1,2,3}}={{1,2,3}} ", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)  
        
        # Test 
        env = Environment()
        assert not interpret(root, env)       
        
    def test_symbolic_power1set(self):
        # Build AST
        string_to_file("#PREDICATE {1,2,3}:POW1(NATURAL)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)  
        
        # Test 
        env = Environment()
        assert interpret(root, env)       


    def test_symbolic_power1set2(self):
        # Build AST
        string_to_file("#PREDICATE {}:POW1(NATURAL)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        assert not interpret(root, env)


    import pytest
    @pytest.mark.xfail 
    def test_symbolic_subset(self):
        # Build AST
        string_to_file("#PREDICATE {(1,1)}<:%x.(x:NATURAL|x) ", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        assert interpret(root, env)

    import pytest
    @pytest.mark.xfail 
    def test_symbolic_min(self):
        # Build AST
        string_to_file("#PREDICATE min({x|x:NATURAL})=0", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        assert interpret(root, env)

    import pytest
    @pytest.mark.xfail 
    def test_symbolic_max(self):
        # Build AST
        string_to_file("#PREDICATE max({x|x:NATURAL & x<42})=41", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        assert interpret(root, env)


    # TODO: Timeout, pi
    # BUG: min and max int cause constraint solver bug. returns 15!
    import pytest
    @pytest.mark.xfail
    def test_symbolic_sigma(self):
        # Build AST
        string_to_file("#PREDICATE SIGMA(x).(x:NATURAL & x<42|x)=861", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        assert interpret(root, env)

    import pytest
    @pytest.mark.xfail
    def test_symbolic_card(self):
        # Build AST
        string_to_file("#PREDICATE card(%x.(x:NATURAL & x<42|x))=42 ", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        assert interpret(root, env)   
    
    # TODO: domain subtraction test
    import pytest
    @pytest.mark.xfail
    def test_symbolic_domain_res(self):
        # Build AST
        string_to_file("#PREDICATE 0..4<|%x.(x:NAT|x)={(0,0),(1,1),(2,2),(3,3),(4,4)}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        assert interpret(root, env) 

    # TODO: range subtraction test
    import pytest
    @pytest.mark.xfail
    def test_symbolic_range_res(self):
        # Build AST
        string_to_file("#PREDICATE %x.(x:NAT|x)|>0..4={(0,0),(1,1),(2,2),(3,3),(4,4)}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        assert interpret(root, env) 

    import pytest
    @pytest.mark.xfail
    def test_symbolic_inverse_realtion(self):
        # Build AST
        string_to_file("#PREDICATE %x.(x:NAT & x<5 |x+1)~={(1,0),(2,1),(3,2),(4,3),(5,4)}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        assert interpret(root, env)

    import pytest
    @pytest.mark.xfail
    def test_symbolic_overwrite(self):
        # Build AST
        string_to_file("#PREDICATE %x.(x:NAT & x<5 |x)<+{(1,0)}={(0,0),(1,0),(2,2),(3,3),(4,4)}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        assert interpret(root, env)

    # TODO: union and inter tests for symbolic instances  
    # TODO: AMultOrCartExpression test         
    # TODO: direct product of composition set test e.g. (%(x).(x:NAT|x+1);%(x).(x:NAT|x*x))><%(x).(x:NAT|-1) or more complex
    # TODO: find real world problem for this testcase
    
    # TODO: more symbolic string id tests  (test_symbolic_id2)        
    def test_symbolic_id(self):
        # Build AST
        # {}=({("a",("b",3)),("c",("d",6))};{("a"|->("b"|->9)),("c"|->("d"|->6))}~)-id(STRING)
        string_to_file("#PREDICATE {}=({(\"a\",(\"b\",3)),(\"c\",(\"d\",6))};{(\"a\"|->(\"b\"|->9)),(\"c\"|->(\"d\"|->6))}~)-id(STRING)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)  
        
        # Test fapp
        env = Environment()
        env.get_all_strings(root)
        assert interpret(root, env) 


    def test_constraint_symbolic_compare(self):
        # Build AST:
        string_to_file("#PREDICATE {x|x:INTEGER}={y|y:INTEGER}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string) 
        
        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32  
        assert interpret(root.children[0], env)  


    # Its hard to compare two symbolic sets
    import pytest
    @pytest.mark.xfail
    def test_constraint_symbolic_compare2(self):
        # Build AST:
        string_to_file("#PREDICATE {x|x:INTEGER & x>0}={x|x:NATURAL}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string) 
        
        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32  
        assert not interpret(root.children[0], env)               


    import pytest
    @pytest.mark.xfail
    def test_constraint_symbolic_compare3(self):
        # Build AST:
        string_to_file("#PREDICATE {x|x:INTEGER & x>=0}={x|x:NATURAL}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string) 
        
        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32  
        assert interpret(root.children[0], env)   


    # test for symmetric implementation of unequality
    import pytest
    @pytest.mark.xfail
    def test_constraint_symbolic_compare4(self):
        # Build AST:
        string_to_file("#PREDICATE %x.(x:NAT & x:{0,1,2,3}|x)/={(0,0),(1,1),(2,2),(3,3)}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string) 
        
        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32  
        assert interpret(root.children[0], env) 

       

    def test_symbolic_intervall_set(self):
        # Build AST
        string_to_file("#PREDICATE %x.(x:0..999999|x*x)(4)=16", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test creation 
        env = Environment()
        env._min_int = -2**31
        env._max_int = 2**31
        assert interpret(root, env)  
   
    # TODO: symbolic intervall  
    import pytest
    @pytest.mark.xfail 
    def test_symbolic_intervall_set2(self):
        # Build AST
        string_to_file("#PREDICATE %x.(x:-2**3..2**32|x*x)(4)=16", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test creation 
        env = Environment()
        env._min_int = -2**31
        env._max_int = 2**31
        assert interpret(root, env)
        
 
    # check membership
    import pytest
    @pytest.mark.xfail
    def test_symbolic_intervall_set3(self):
        # Build AST
        string_to_file("#PREDICATE (4,16):%x.(x:-2**3..2**32|x*x)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test creation 
        env = Environment()
        env._min_int = -2**31
        env._max_int = 2**31
        assert interpret(root, env)       
  
               
    # check enumeration
    #import pytest
    #@pytest.mark.xfail
    def test_symbolic_intervall_set4(self):
        # Build AST
        string_to_file("#PREDICATE {(1,1)}=%x.(x:-2**0..2**0|x*x)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test creation 
        env = Environment()
        env._min_int = -2**31
        env._max_int = 2**31
        assert interpret(root, env)       
        

    import pytest
    @pytest.mark.xfail        
    def test_symbolic_intersection_set(self):
        # Build AST
        string_to_file("#PREDICATE %x.(x:NATURAL & x:{1,2,3}|x*x)/\%x.(x:NATURAL & x:{1,2,3}|x*2)={(2,4)} ", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test creation 
        env = Environment()
        env._min_int = -2**31
        env._max_int = 2**31
        assert interpret(root, env)     
 

    import pytest
    @pytest.mark.xfail 
    def test_symbolic_union_set(self):
        # Build AST
        string_to_file("#PREDICATE %x.(x:NATURAL & x:{1,2,3}|x*x)\/%x.(x:NATURAL & x:{1,2,3}|x*2)={(1,1),(1,2),(2,4),(3,6),(3,9)}  ", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test creation 
        env = Environment()
        env._min_int = -2**31
        env._max_int = 2**31
        assert interpret(root, env)        
             
        
        
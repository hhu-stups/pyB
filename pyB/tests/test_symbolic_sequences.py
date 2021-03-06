# -*- coding: utf-8 -*-
import pytest
from ast_nodes import *
from environment import Environment
from helpers import file_to_AST_str, string_to_file
from interp import interpret
from parsing import parse_ast, str_ast_to_python_ast
from typing import type_check_bmch
from symbolic_sets import *
from util import arbitrary_init_machine

from config import USE_RPYTHON_CODE
if USE_RPYTHON_CODE:
     from rpython_b_objmodel import frozenset

file_name = "input.txt"

# TODO: maybe more cases (some operations have only one testcase)
# maybe this is only importent in theory...
class TestSymbolicSequences():
    import pytest
    @pytest.mark.xfail 
    def test_symbolic_sequences_first(self):
        # Build AST
        string_to_file("#PREDICATE first(%x.(x:NATURAL|x))=1", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        assert 1==2 # Timeout exception missing
        assert interpret(root, env)


    import pytest
    @pytest.mark.xfail         
    def test_symbolic_sequences_first2(self):
        # Build AST
        string_to_file("#PREDICATE (0,0):%x.(x:NATURAL|x) & first(%x.(x:NATURAL|x))=1", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        assert 1==2 # Timeout exception missing
        assert interpret(root, env)


    import pytest
    @pytest.mark.xfail         
    def test_symbolic_sequences_first3(self):
        # Build AST
        # f(1)=1
        string_to_file("#PREDICATE first(%x.(x:INTEGER|x))=1", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        assert 1==2 # Timeout exception missing
        assert interpret(root, env)
        
        
    import pytest
    @pytest.mark.xfail 
    def test_symbolic_sequences_size(self):
        # Build AST
        string_to_file("#PREDICATE size(%x.(x:NATURAL & x<2**32|x))=2**32", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        env._min_int = -1
        env._max_int = 5
        assert interpret(root, env)    
        
        
    import pytest
    @pytest.mark.xfail 
    def test_symbolic_sequences_last(self):
        # Build AST
        string_to_file("#PREDICATE last(%x.(x:NAT|x))=MAXINT", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        env._min_int = -1
        env._max_int = 5
        assert interpret(root, env) 

                
    # TODO: undefined size. Throw exception
    import pytest
    @pytest.mark.xfail     
    def test_symbolic_sequences_size2(self):
        # Build AST
        string_to_file("#EXPRESSION size(%x.(x:NATURAL|x))", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        assert interpret(root, env)          
 
 
    # seq. is prob calc result
    import pytest
    @pytest.mark.xfail 
    def test_symbolic_sequences_rev(self):
        # Build AST
        string_to_file("#PREDICATE rev(%x.(x:NATURAL & x<5|x))={(2,4),(3,3),(4,2),(5,1),(6,0)}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        env._min_int = -1
        env._max_int = 5
        assert interpret(root, env)              
        

    #missing or wrong impl. for __getitem__
    #import pytest
    #@pytest.mark.xfail         
    def test_symbolic_sequences_conc(self):
        # Build AST
        string_to_file("#EXPRESSION (%x.(x:NAT1|x+1))^(%x.(x:NAT1|x*x))", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        env._min_int = -1
        env._max_int = 5
        assert interpret(root, env) 
 
        
    #missing  or wrong impl. for __getitem__
    #import pytest
    #@pytest.mark.xfail    
    def test_symbolic_sequences_append(self):
        # Build AST
        # {(1,2)...(127,128),(128,42)}
        string_to_file("#EXPRESSION (%x.(x:NAT1|x+1))<-42", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        env._min_int = -1
        env._max_int = 5
        assert interpret(root, env)        


    import pytest
    @pytest.mark.xfail 
    def test_symbolic_sequences_prepend(self):
        # Build AST
        # {(1,32),(2,2)...(128,128)}
        string_to_file("#PREDICATE (42->(%x.(x:NAT1|x+1)))(128)=128  ", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        env._min_int = -1
        env._max_int = 5
        assert interpret(root, env)        
 
 
    import pytest
    @pytest.mark.xfail   
    def test_symbolic_sequences_take(self):
        # Build AST
        string_to_file("#PREDICATE (%x.(x:NAT1|x+1))/|\\3=[2,3,4]", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        env._min_int = -1
        env._max_int = 5
        assert interpret(root, env)    
    
 
    def test_symbolic_sequences_drop(self):
        # Build AST
        string_to_file("#PREDICATE (%x.(x:NAT1|x+1))\\|/MAXINT-3=[MAXINT-1,MAXINT,MAXINT+1]", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        env._min_int = -1
        env._max_int = 5
        assert interpret(root, env)    
        
        

    def test_symbolic_sequences_front(self):
        # Build AST
        string_to_file("#PREDICATE front((%x.(x:NAT1|x)))<-MAXINT=(%x.(x:NAT1|x))", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        env._min_int = -1
        env._max_int = 5
        assert interpret(root, env)
        
    import pytest
    @pytest.mark.xfail 
    def test_symbolic_sequences_tail(self):
        # Build AST
        string_to_file("#PREDICATE 1->tail((%x.(x:NAT1|x)))=(%x.(x:NAT1|x))", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        env._min_int = -1
        env._max_int = 5
        assert interpret(root, env)       
        
 
    import pytest
    @pytest.mark.xfail  
    def test_symbolic_sequences_perm(self):
        # Build AST
        string_to_file("#PREDICATE s:perm(NAT) & s(1)=42", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        assert 1==2 # Timeout exception missing
        assert interpret(root, env)         

         
    def test_symbolic_sequences_perm2(self):
        # Build AST
        string_to_file("#PREDICATE %x.(x:NAT1|x):perm(NAT1)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        env._min_int = -1
        env._max_int = 5
        assert interpret(root, env)               
    

      
    def test_symbolic_sequences_seq(self):
        # Build AST
        string_to_file("#PREDICATE %x.(x:NAT1|x):seq(NAT1)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        env._min_int = -1
        env._max_int = 5
        assert interpret(root, env)  
    
    
           
    def test_symbolic_sequences_seq1(self):
        # Build AST
        string_to_file("#PREDICATE %x.(x:NAT1|x):seq1(NAT1)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        env._min_int = -1
        env._max_int = 5
        assert interpret(root, env)        
    
    
  
    def test_symbolic_sequences_iseq1(self):
        # Build AST
        string_to_file("#PREDICATE %x.(x:NAT1|x):iseq1(NAT)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        env._min_int = -1
        env._max_int = 5
        assert interpret(root, env)    


  
    def test_symbolic_sequences_seq_perm(self):
        # Build AST
        string_to_file("#PREDICATE %x.(x:{1,2,3} | %x.(x:{1,2,3}|x)):seq(perm({1,2,3}))", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        env._min_int = -1
        env._max_int = 5
        assert interpret(root, env)     
  
    
   
    def test_symbolic_sequences_conc2(self):
        # Build AST
        string_to_file("#PREDICATE conc(%x.(x:{1,2,3} | %x.(x:{1,2,3}|x)))=[1,2,3,1,2,3,1,2,3]", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test 
        env = Environment()
        env._min_int = -1
        env._max_int = 5
        assert interpret(root, env)       
    
    # C578.EML.014/019_100 DontKnowIfEqualException
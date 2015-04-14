# -*- coding: utf-8 -*-
from ast_nodes import *
from environment import Environment
from helpers import contains_lower_character, file_to_AST_str, string_to_file, all_ids_known, select_ast_to_list, find_var_nodes
from parsing import str_ast_to_python_ast

from config import USE_COSTUM_FROZENSET
if USE_COSTUM_FROZENSET:
     from rpython_b_objmodel import frozenset

file_name = "input.txt"


class TestHelpers():
    def test_varName_simple(self):
        string_to_file("#PREDICATE F=S+->T", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
    
        idNodes = find_var_nodes(root)
        var_list = [n.idName for n in idNodes]
        assert var_list==['F','S','T']


    def test_varName_simple2(self):
        string_to_file("#PREDICATE x<4 & x<42", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
    
        idNodes = find_var_nodes(root)
        var_list = [n.idName for n in idNodes]
        assert var_list==['x']


    def test_varName_complex1(self):
        string_to_file("#PREDICATE y=f(g(x,z))", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
    
        idNodes = find_var_nodes(root)
        var_list = [n.idName for n in idNodes]
        assert set(var_list)==set(['f','g','x','y','z'])
 
 
    def test_varName_complex2(self):
        string_to_file("#PREDICATE y=f(g(x)(z))", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
    
        idNodes = find_var_nodes(root)
        var_list = [n.idName for n in idNodes]
        assert set(var_list)==set(['f','g','x','y','z'])          


    def test_all_ids_known(self):
        string_to_file("#PREDICATE x=y & x=42", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        env = Environment()
        env.add_ids_to_frame(["x","y"])
        assert all_ids_known(root, env)==False


    def test_all_ids_known2(self):
        string_to_file("#PREDICATE x=y & x=42", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        env = Environment()
        env.add_ids_to_frame(["x","y"])
        env.set_value("x",42)
        env.set_value("y",42)
        assert all_ids_known(root, env)==True


    def test_all_ids_known3(self):
        string_to_file("#PREDICATE #(x).(x>0 & x<10)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        env = Environment()
        assert all_ids_known(root, env)==False


    def test_all_ids_known4(self):
        string_to_file("#PREDICATE ID={x|x>0 & x<10}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        env = Environment()
        env.add_ids_to_frame(["ID"])
        assert all_ids_known(root, env)==False        
  
  
    def test_all_ids_known5(self):
        string_to_file("#PREDICATE ID={x|x>0 & x<10}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        env = Environment()
        env.add_ids_to_frame(["ID"])
        env.set_value("ID", frozenset([1,2,3])) # would be false
        assert all_ids_known(root, env)==True
        
  
    def test_all_ids_known6(self):
        string_to_file("#PREDICATE {(1,2)}:S<->T", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        env = Environment()
        env.add_ids_to_frame(["S","T"])
        env.set_value("S", frozenset([1,2,3,4,5]))
        env.set_value("T", frozenset([1,2,3,4,5]))  
        assert all_ids_known(root, env)==True               
    
    
    def test_select_ast_to_list(self):
        # Build AST
        string = '''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT 
        INITIALISATION BEGIN xx:=1; 
            SELECT 1+1=2 THEN xx:=2 
            WHEN 1+1=3 THEN xx:=3
            ELSE xx:=4 END END
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        select_ast = root.children[3].children[0].children[0].children[1]
        assert isinstance(select_ast, ASelectSubstitution)
        lst = select_ast_to_list(select_ast)
        for tup in lst:
            assert isinstance(tup[1], Substitution)
            if tup[0]:
                assert isinstance(tup[0], Predicate)
            else:
                assert select_ast.hasElse=="True"
    
    def test_contains_lower_character(self):
        assert not contains_lower_character("BOOK")
        assert contains_lower_character("capacity")
        assert contains_lower_character("Book")
        assert contains_lower_character("az")
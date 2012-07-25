# -*- coding: utf-8 -*-
from ast_nodes import *
from environment import Environment
from helpers import file_to_AST_str, string_to_file, find_var_names, all_ids_known

file_name = "input.txt"


class TestHelpers():
    def test_varName_simple(self):
        string_to_file("#PREDICATE F=S+->T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        var_list = find_var_names(root)
        assert var_list==['F','S','T']


    def test_varName_simple2(self):
        string_to_file("#PREDICATE x<4 & x<42", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        var_list = find_var_names(root)
        assert var_list==['x']
    
    def test_all_ids_known(self):
    	string_to_file("#PREDICATE x=y & x=42", file_name)
    	ast_string = file_to_AST_str(file_name)
        exec ast_string
        
        env = Environment()
        env.bstate.add_ids_to_frame(["x","y"])
        assert all_ids_known(root, env)==False


    def test_all_ids_known2(self):
    	string_to_file("#PREDICATE x=y & x=42", file_name)
    	ast_string = file_to_AST_str(file_name)
        exec ast_string
        
        env = Environment()
        env.bstate.add_ids_to_frame(["x","y"])
        env.bstate.set_value("x",42)
        env.bstate.set_value("y",42)
        assert all_ids_known(root, env)==True


    def test_all_ids_known3(self):
    	string_to_file("#PREDICATE #(x).(x>0 & x<10)", file_name)
    	ast_string = file_to_AST_str(file_name)
        exec ast_string
        
        env = Environment()
        assert all_ids_known(root, env)==False


    def test_all_ids_known4(self):
    	string_to_file("#PREDICATE ID={x|x>0 & x<10}", file_name)
    	ast_string = file_to_AST_str(file_name)
        exec ast_string
        
        env = Environment()
        env.bstate.add_ids_to_frame(["ID"])
        assert all_ids_known(root, env)==False        
  
  
    def test_all_ids_known5(self):
    	string_to_file("#PREDICATE ID={x|x>0 & x<10}", file_name)
    	ast_string = file_to_AST_str(file_name)
        exec ast_string
        
        env = Environment()
        env.bstate.add_ids_to_frame(["ID"])
        env.bstate.set_value("ID", frozenset([1,2,3])) # would be false
        assert all_ids_known(root, env)==True
        
  
    def test_all_ids_known6(self):
    	string_to_file("#PREDICATE {(1,2)}:S<->T", file_name)
    	ast_string = file_to_AST_str(file_name)
        exec ast_string
        
        env = Environment()
        env.bstate.add_ids_to_frame(["S","T"])
        env.bstate.set_value("S", frozenset([1,2,3,4,5]))
        env.bstate.set_value("T", frozenset([1,2,3,4,5]))  
        assert all_ids_known(root, env)==True               
from animation_clui import print_values_b_style
from ast_nodes import *
from environment import Environment
from helpers import  string_to_file, file_to_AST_str_no_print
from interp import interpret
from parsing import parse_ast, str_ast_to_python_ast
from repl import parse_repl_input


from config import USE_RPYTHON_CODE
if USE_RPYTHON_CODE:
     from rpython_b_objmodel import frozenset

class TestRepl():
    def test_repl_add(self):
        env = Environment() 
        input = "1+1"
        output, err = parse_repl_input(input)
        assert err==None
        assert print_values_b_style(output)=="2"
        
         
    def test_repl_eq(self):
        env = Environment() 
        input = "1+1=2"
        output, err = parse_repl_input(input)
        assert err==None
        assert print_values_b_style(output)=="True"
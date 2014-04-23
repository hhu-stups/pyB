from ast_nodes import *
from helpers import  string_to_file, file_to_AST_str_no_print
from environment import Environment
from interp import interpret
from parsing import parse_ast, str_ast_to_python_ast
from repl import parse_repl_input

class TestRepl():
    def test_repl_add(self):
        env = Environment() 
        input = "1+1"
        parse_repl_input(input)
        #Todo: separate printing
        #assert sys.stdout.read()=="2" 

    def test_repl_eq(self):
        env = Environment() 
        input = "1+1=2"
        parse_repl_input(input)
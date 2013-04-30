from ast_nodes import *
from helpers import  string_to_file, file_to_AST_str_no_print
from environment import Environment
from interp import interpret
from parsing import parse_ast, str_ast_to_python_ast


def run_repl():
    print "PyB repl. Version: 08.01.2013"
    print "Input: e.g. '1+1' or '1+1<42'"
    print "quit to exit."
    string = None
    env = Environment() 
    while True:
        string = raw_input(">>")
        if string=="quit":
            break
        try:   
            string_to_file("#EXPRESSION "+string, "temp.b")
            ast_string,error = file_to_AST_str_no_print("temp.b")
            root = str_ast_to_python_ast(ast_string)    
        except NameError:
            string_to_file("#PREDICATE "+string, "temp.b")
            ast_string, error = file_to_AST_str_no_print("temp.b")
            if error:
                if "Error parsing input file" in error:
                    print "PARSING ERROR on Java-LEVEL:"
                    print error
                    continue
                else:
                    print error
                    exit()                
            root = str_ast_to_python_ast(ast_string)                                            
        result = interpret(root, env) #printing via sideeffect
    exit()
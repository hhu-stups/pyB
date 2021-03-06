from ast_nodes import *
from config import USE_RPYTHON_CODE
from environment import Environment
from helpers import  string_to_file, file_to_AST_str_no_print
from parsing import parse_ast, str_ast_to_python_ast

if USE_RPYTHON_CODE:
	from rpython_interp import interpret
else:
	from interp import interpret


def run_repl(argv):
    print "PyB repl. Version: 08.01.2013"
    print "Input: e.g. '1+1' or '1+1<42'"
    print "quit to exit."
    env = Environment()
    env.parse_config_parameter(argv)
    string = None
    while True:
        string = raw_input(">>")
        if string=="quit":
            break
        output, error = parse_repl_input(string)
        if error:
            if "Error parsing input file" in error:
                print "PARSING ERROR on Java-LEVEL:"
                print error
                print "check your jar files or yout input!"
                continue
            else:
                print error
                exit()
        else:
            print output  
    exit()

# returns value of expression, True/False or an Error
# returntype: BValue, String
def parse_repl_input(input):
    try:   
        string_to_file("#EXPRESSION "+input, "temp.b")
        ast_string,error = file_to_AST_str_no_print("temp.b")
        if ast_string=="\n":
            raise NameError() # FIXME: refactor this line
        root = str_ast_to_python_ast(ast_string) 
    except NameError: #no expression
        string_to_file("#PREDICATE "+input, "temp.b")
        ast_string, error = file_to_AST_str_no_print("temp.b")
        if error:
            result = None
            return result, error
        root = str_ast_to_python_ast(ast_string)                                                        
    result = interpret(root, Environment() ) #printing via side effect
    error = None
    return result, error
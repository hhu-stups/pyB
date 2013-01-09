# -*- coding: utf-8 -*-
import sys
from interp import interpret, write_solutions_to_env
from bmachine import BMachine
from environment import Environment
from helpers import file_to_AST_str_no_print, solution_file_to_AST_str
from parsing import PredicateParseUnit, ExpressionParseUnit, str_ast_to_python_ast
from animation_clui import show_ui, show_env
from animation import calc_possible_operations, exec_op, calc_bstates
from definition_handler import DefinitionHandler
from ast_nodes import *
from config import DEFAULT_INPUT_FILENAME
from parsing import parse_ast
from typing import type_check_bmch
from repl import run_repl


def read_input_string():
    file_name_str = DEFAULT_INPUT_FILENAME
    solution_file_name_str = ""
    if len(sys.argv)==2:
        file_name_str = sys.argv[1]
    elif len(sys.argv)==3:
        file_name_str = sys.argv[1]
        solution_file_name_str = sys.argv[2]
    else:
        print "Warning: No input file! default:",file_name_str
    return file_name_str, solution_file_name_str


def read_solution_file(env):
    ast_str, error = file_to_AST_str_no_print(solution_file_name_str)
    if error:
        print error
    exec ast_str # TODO: JSON
    write_solutions_to_env(root, env)
    if env.solutions:
        print "learnd from solution-file: ", [x for x in env.solutions] 


###### MAIN PROGRAM ######
if sys.argv[1]=="-repl":
    run_repl()
    exit()
env = Environment()                                         # 1. create env.
file_name_str, solution_file_name_str = read_input_string() # 2. read filenames
if solution_file_name_str:                                  # 3. parse and use solution-file and write to env.
    read_solution_file(env)
ast_string, error = file_to_AST_str_no_print(file_name_str) # 4. parse input-file to string
if error:
    print error
root = str_ast_to_python_ast(ast_string)                    # 5. parse string to python ast TODO: JSON
dh = DefinitionHandler()                                    # 6. replace defs if present 
dh.repl_defs(root)
#import cProfile
#cProfile.run('mch = interpret(root, env)','pyB_profile_out.txt')
parse_object = parse_ast(root, env)                         # 7. which kind of ast?
if isinstance(parse_object, BMachine):                      # 8. typecheck
    type_check_bmch(root, parse_object) # also checks all included, seen, used and extend
result = interpret(parse_object.root, env)                  # 9. calc init state

                                                            # 10. animate if ops are present 
if isinstance(parse_object, BMachine): #otherwise #PREDICATE or #EXPRESSION 
    mch = env.root_mch
    # DO-WHILE Loop
    while True:
        print mch.name," - Invariant:", mch.eval_Invariant(env) # TODO: move print to animation_clui
        op_list = calc_possible_operations(env, mch)            # List of lists
        op_and_bstate_list = calc_bstates(env, op_list, mch)
        if op_list==[]: # BUG: no enabled ops doesnt mean there are none (deadlock-state)
            show_env(env)
            break
        n = show_ui(env, mch, op_list)
        input_str = "Input (0-"+str(n)+"):"
        number = raw_input(input_str)
        number = int(number)
        if number == n-1:
            if not env.state_space.empty():
                env.state_space.undo()
            else:
                print "No undo possible: init state"
        elif number == n:
            break
        else:
            assert len(op_list)>number
            assert number >= 0
            bstate = op_and_bstate_list[number][4]
            env.state_space.add_state(bstate)

#TODO: PREDICATE or #EXPRESSION 
#TODO: move print to animation_clui
#else:
#    env.bstate.print_state()

# -*- coding: utf-8 -*-
import sys
from interp import interpret, write_solutions_to_env, set_up_sets, set_up_constants, check_properties,init_mch_param
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
ast_string, error = file_to_AST_str_no_print(file_name_str) # 3. parse input-file to string
if error:
    print error
root = str_ast_to_python_ast(ast_string)                    # 4. parse string to python ast TODO: JSON
dh = DefinitionHandler()                                    # 5. replace defs if present 
dh.repl_defs(root)
#import cProfile
#cProfile.run('mch = interpret(root, env)','pyB_profile_out.txt')
parse_object = parse_ast(root, env)                         # 6. which kind of ast?
if not isinstance(parse_object, BMachine):                  #PREDICATE or #EXPRESSION                   
	interpret(parse_object.root, env)                       # eval predicate or expression
else:
    assert isinstance(parse_object,	BMachine)			    # 7. typecheck
    type_check_bmch(root, parse_object) # also checks all included, seen, used and extend
    mch = parse_object
    mch.init_include_mchs()
    mch.init_seen_mchs()
    mch.init_used_mchs()
    mch.init_extended_mchs()

    # TODO: Check with B spec
    # Schneider Book page 62-64:
    # The parameters p make the constraints c True
    # #p.C
    init_mch_param(root, env, mch)

    # Sets St and constants k which meet the constraints c make the properties B True
    # C => #St,k.B
    set_up_sets(root, env, mch)
    if solution_file_name_str:                              # 8. parse and use solution-file and write to env.
        read_solution_file(env)
    else:
        set_up_constants(root, env, mch)
    check_properties(root, env, mch)
    
    # If C and B is True there should be Variables v which make the Invaraiant I True
    # TODO: B & C => #v.I
    if not solution_file_name_str:
    	mch.eval_Variables(env)
    

    # Not in schneiders book:
    mch.eval_Assertions(env)
    mch.eval_Init(env)
                                                            # 9. animate if ops are present                                                    
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

# -*- coding: utf-8 -*-
import sys
from interp import interpret, write_solutions_to_env, set_up_constants, exec_initialisation, eval_Invariant
from bmachine import BMachine
from environment import Environment
from helpers import file_to_AST_str_no_print, solution_file_to_AST_str
from parsing import PredicateParseUnit, ExpressionParseUnit, str_ast_to_python_ast
from animation_clui import show_ui, show_env, print_set_up_bstates, print_init_bstates
from animation import calc_next_states
from definition_handler import DefinitionHandler
from ast_nodes import *
from config import DEFAULT_INPUT_FILENAME, VERBOSE
from parsing import parse_ast
from typing import type_check_bmch
from repl import run_repl


def read_input_string(offset=0):
    file_name_str = DEFAULT_INPUT_FILENAME
    solution_file_name_str = ""
    if len(sys.argv)==2+offset:
        file_name_str = sys.argv[1+offset]
    elif len(sys.argv)==3+offset:
        file_name_str = sys.argv[1+offset]
        solution_file_name_str = sys.argv[2+offset]
    else:
        print "Warning: No input file! default:",file_name_str
    return file_name_str, solution_file_name_str


# assumes "#PREDICATE" header
def read_solution_file(env, solution_file_name_str):
    ast_str, error = file_to_AST_str_no_print(solution_file_name_str)
    if error:
        print error
    exec ast_str # TODO: JSON
    write_solutions_to_env(root, env)
    if env.solutions and VERBOSE:
        print "learnd from solution-file (constants and variables): ", [x for x in env.solutions] 


# can use a solution file to speed up the init (or make it possible).
# will go into animation mode if possible
def run_animation_mode():
    env = Environment()                                         # 1. create env.
    file_name_str, solution_file_name_str = read_input_string() # 2. read filenames
    ast_string, error = file_to_AST_str_no_print(file_name_str) # 3. parse input-file to string
    if error:
        print error
    root = str_ast_to_python_ast(ast_string)                    # 4. parse string to python ast TODO: JSON
    dh = DefinitionHandler()                                    # 5. replace defs if present 
    dh.repl_defs(root)
    # uncomment for profiling (e.g. performance tests)
    #import cProfile
    #cProfile.run('mch = interpret(root, env)','pyB_profile_out.txt')
    if solution_file_name_str:                                  # 6. parse solution-file and write to env.
        read_solution_file(env, solution_file_name_str)         # The concreate solution values are added at 
                                                                # the bmachine object-init time to the respective mch
    
    parse_object = parse_ast(root, env)                         # 7. which kind of ast?
    if not isinstance(parse_object, BMachine):                  # #PREDICATE or #EXPRESSION                   
        interpret(parse_object.root, env)                       # eval predicate or expression
    else:
        assert isinstance(parse_object, BMachine)               # 8. typecheck
        mch = parse_object
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
    
        # TODO: Check with B spec
        # Schneider Book page 62-64:
        # The parameters p make the constraints C True
        # #p.C    
        # Sets St and constants k which meet the constraints c make the properties B True
        # C => #St,k.B
        bstates = set_up_constants(root, env, mch, not solution_file_name_str=="")
        #print_set_up_bstates(bstates, mch)
        env.state_space.add_state(bstates[0]) #XXX
        
        
        # If C and B is True there should be Variables v which make the Invaraiant I True
        # B & C => #v.I
        print solution_file_name_str
        bstates = exec_initialisation(root, env, mch, not solution_file_name_str=="")
        #print_init_bstates(bstates, mch)
        env.state_space.add_state(bstates[0]) #XXX
        
        # Not in schneiders book:
        if mch.aAssertionsMachineClause:
            interpret(mch.aAssertionsMachineClause, env)

                                                               		 # 9. animate if ops are present                                                    
        # DO-WHILE Loop
        while True:
            print mch.name," - Invariant:", eval_Invariant(root, env, mch)  # TODO: move print to animation_clui
            next_states = calc_next_states(env,mch)
            if next_states==[]: # BUG: no enabled ops doesnt mean there are none (deadlock-state)
                show_env(env)
                break
            n = show_ui(env, mch, next_states)
            input_str = "Input (0-"+str(n)+"):"
            number = raw_input(input_str)
            number = int(number)
            if number == n-1:
                if not env.state_space.empty():
                    env.state_space.undo()
                else:
                    print "No undo possible: current state is init. state"
            elif number == n:
                # quit
                break
            elif len(next_states)>number and number >= 0:
                # switch state
                bstate = next_states[number][3]
                env.state_space.add_state(bstate)
            else:
                print "Error! Wrong input:", number


# check of init without animation
def run_checking_mode():
    env = Environment()                                          # 1. create env.
    file_name_str, solution_file_name_str = read_input_string(1) # 2. read filenames
    ast_string, error = file_to_AST_str_no_print(file_name_str)  # 3. parse input-file to string
    if error:
        print error
    root = str_ast_to_python_ast(ast_string)                    # 4. parse string to python ast TODO: JSON
    dh = DefinitionHandler()                                    # 5. replace defs if present 
    dh.repl_defs(root)
    if solution_file_name_str:                                  # 6. parse solution-file and write to env.
        read_solution_file(env, solution_file_name_str)         # The concreate solution values are added at 
                                                                # the bmachine object-init time to the respective mch

        
    parse_object = parse_ast(root, env)                         # 7. which kind of ast?
    if not isinstance(parse_object, BMachine):                  # #PREDICATE or #EXPRESSION                   
        interpret(parse_object.root, env)                       # eval predicate or expression
    else:
        assert isinstance(parse_object, BMachine)               # 8. typecheck
        type_check_bmch(root, env, parse_object) # also checks all included, seen, used and extend
        mch = parse_object
        bstates = set_up_constants(root, env, mch, not solution_file_name_str=="")
        env.state_space.add_state(bstates[0]) #XXX
        bstates = exec_initialisation(root, env, mch, not solution_file_name_str=="")
        env.state_space.add_state(bstates[0]) #XXX
        if mch.aAssertionsMachineClause:
            interpret(mch.aAssertionsMachineClause, env)
        return eval_Invariant(root, env, mch)   


###### MAIN PROGRAM ######
if sys.argv[1]=="-repl" or sys.argv[1]=="-r":
    run_repl()
elif sys.argv[1]=="-check_solution" or sys.argv[1]=="-c":
    result = run_checking_mode()
    print result
else:
    run_animation_mode()

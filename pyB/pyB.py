# -*- coding: utf-8 -*-
import sys
from interp import interpret, set_up_constants, exec_initialisation, eval_Invariant
from bmachine import BMachine
from bexceptions import *
from environment import Environment
from helpers import file_to_AST_str_no_print, solution_file_to_AST_str
from parsing import PredicateParseUnit, ExpressionParseUnit, str_ast_to_python_ast, remove_defs_and_parse_ast
from animation_clui import show_ui, print_set_up_bstates, print_init_bstates, print_values_b_style
from animation import calc_next_states
from ast_nodes import *
from config import DEFAULT_INPUT_FILENAME, VERBOSE
from typing import type_check_root_bmch, type_check_predicate
from repl import run_repl


# console input like python 'pyB.py somefile.mch some_solutionfile.txt'
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


# add "#PREDICATE" header and read solution 
def read_solution_file(env, solution_file_name_str):
    ast_str, error = solution_file_to_AST_str(solution_file_name_str)
    if error:
        print error
    root = str_ast_to_python_ast(ast_str)
    env.solution_root = root
    env.write_solution_nodes_to_env(root)
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
    env.set_search_dir(file_name_str)
    root = str_ast_to_python_ast(ast_string)                    # 4. parse string to python ast TODO: JSON
    # uncomment for profiling (e.g. performance tests)
    #import cProfile
    #cProfile.run('mch = interpret(root, env)','pyB_profile_out.txt')
    solution_file_present = not solution_file_name_str==""
    if solution_file_present:                                   # 5. parse solution-file and write to env.
        read_solution_file(env, solution_file_name_str)         # The concreate solution values are added at 
                                                                # the bmachine object-init time to the respective mch

                                                                # 6. replace defs and extern-functions inside mch and solution-file (if present)      
    parse_object = remove_defs_and_parse_ast(root, env)         # 7. which kind of ast?
    if not isinstance(parse_object, BMachine):                 
        is_ppu = isinstance(parse_object, PredicateParseUnit) 
        is_epu = isinstance(parse_object, ExpressionParseUnit) 
        assert is_ppu or is_epu              
        result = interpret(parse_object.root, env)              # eval predicate or expression
        print print_values_b_style(result)
    else:
        assert isinstance(parse_object, BMachine)               # 8. typecheck
        mch = parse_object
        type_check_root_bmch(root, env, mch) # also checks all included, seen, used and extend  
        # TODO: Check with B spec
                                                                # 9. animate if ops are present                                                    
        # DO-WHILE Loop
        while True:
            next_states = __calc_states_and_print_ui(root, env, mch, solution_file_present)
            if next_states==[]: # BUG: no enabled ops doesnt mean there are none (deadlock-state)
                pass
            undo_possible = not env.state_space.empty()
            number_of_options = len(next_states)
            if undo_possible: 
                number_of_options = number_of_options + 1 
            input_str = "Input (0-"+str(number_of_options)+"):"
            number = raw_input(input_str)
            number = int(number)
            
            # quit
            if number == number_of_options:
                print "goodbye"
                break
            elif undo_possible and number == number_of_options-1:
                x = env.state_space.get_stack_size()
                x = x-1 # BUGFIX: empty state on stack
                if 2==x and env.init_state_on_stack and env.set_up_state_on_stack:
                    env.init_state_on_stack==False
                    env.init_done = False
                elif 1==x and env.init_state_on_stack and env.set_up_state_on_stack==False:
                    env.init_state_on_stack==False
                    env.init_done = False
                elif 1==x and env.set_up_state_on_stack:
                    env.set_up_done = False
                    env.set_up_state_on_stack = False
                    env.set_up_bmachines_names   = []
                    
                env.state_space.undo()
            elif not env.set_up_done:
                env.set_up_done = True
                env.set_up_state_on_stack = True
                bstate = next_states[number]
                env.state_space.add_state(bstate) 
            elif not env.init_done:
                env.init_done = True
                env.init_state_on_stack = True
                bstate = next_states[number]
                env.state_space.add_state(bstate)
            # init and set_up done. Exec operation:
            elif len(next_states)>number and number >= 0:
                # switch state (
                bstate = next_states[number]
                env.state_space.add_state(bstate)
            else:
                print "Error! Wrong input:", number
                

# skips set_up or init if there is nothing to setup/init
def __calc_states_and_print_ui(root, env, mch, solution_file_read):
    # Schneider Book page 62-64:
    # The parameters p make the constraints C True
    # #p.C    
    # Sets St and constants k which meet the constraints c make the properties B True
    # C => #St,k.B
    if not env.set_up_done:
        next_states = set_up_constants(root, env, mch, solution_file_read)
        if len(next_states)>0:
            print_set_up_bstates(next_states, mch)
            return next_states
        else:
            # no bstates and no exception: set up to do (e.g no constants)
            env.set_up_done = True 
        
        
    # If C and B is True there should be Variables v which make the Invaraiant I True
    # B & C => #v.I
    if not env.init_done:
        next_states = exec_initialisation(root, env, mch, solution_file_read)
        if len(next_states)>0:
            undo_possible = not env.state_space.empty()
            print_init_bstates(next_states, mch, undo_possible)
            return next_states
        else:
            # no bstates and no exception: no init to do (e.g no variables)
            env.init_done = True

    print mch.mch_name," - Invariant:", eval_Invariant(root, env, mch)  # TODO: move print to animation_clui
    bstate_lst = calc_next_states(env, mch)
    show_ui(env, mch, bstate_lst)
    next_states = []
    for n in bstate_lst: # all other data inside bstate_lst has already been processed by show_ui
        next_states.append(n[3])
    return next_states


# check of init without animation
def run_checking_mode():
    env = Environment()                                          # 1. create env.
    file_name_str, solution_file_name_str = read_input_string(1) # 2. read filenames
    ast_string, error = file_to_AST_str_no_print(file_name_str)  # 3. parse input-file to string
    if error:
        print error
    env.set_search_dir(file_name_str)
    root = str_ast_to_python_ast(ast_string)                    # 4. parse string to python ast TODO: JSON
    if solution_file_name_str:                                  # 5. parse solution-file and write to env.
        read_solution_file(env, solution_file_name_str)         # The concreate solution values are added at 
                                                                # the bmachine object-init time to the respective mch

                                                                # 6. replace defs and extern-functions inside mch and solution-file (if present)  
    parse_object = remove_defs_and_parse_ast(root, env)         # 7. which kind of ast?
    if not isinstance(parse_object, BMachine):                  # #PREDICATE or #EXPRESSION                   
        result = interpret(parse_object.root, env)              # eval predicate or expression
        print result
    else:
        assert isinstance(parse_object, BMachine)               # 8. typecheck
        type_check_root_bmch(root, env, parse_object) # also checks all included, seen, used and extend
        mch = parse_object							 
        
        bstates = set_up_constants(root, env, mch, not solution_file_name_str=="")  # also evals properties
        if not bstates==[]: 
            result = None
            for bstate in bstates:
                env.state_space.add_state(bstate)
                #if mch.has_properties_mc:
                #    assert interpret(mch.aPropertiesMachineClause, env)
                init_bstates = exec_initialisation(root, env, mch, not solution_file_name_str=="")
                for init_bstate in init_bstates:
                    env.state_space.add_state(init_bstate)
                    if mch.has_invariant_mc:
                        result = interpret(mch.aInvariantMachineClause, env)
                    env.state_space.undo()                  
                if mch.has_assertions_mc:
                    interpret(mch.aAssertionsMachineClause, env)
                env.state_space.undo()  
            return result
        else: # TODO: dont repeat yourself 
            init_bstates = exec_initialisation(root, env, mch, not solution_file_name_str=="")
            for bstate in init_bstates:
                env.state_space.add_state(bstate)
                if mch.has_invariant_mc:
                    assert interpret(mch.aInvariantMachineClause, env)        
                if mch.has_assertions_mc:
                    interpret(mch.aAssertionsMachineClause, env)
                env.state_space.undo() 
            if not init_bstates==[]:  
                env.state_space.add_state(init_bstates[0]) 
        return eval_Invariant(root, env, mch)   


###### MAIN PROGRAM ######
try:
    if sys.argv[1]=="-repl" or sys.argv[1]=="-r":
        run_repl()
    elif sys.argv[1]=="-check_solution" or sys.argv[1]=="-c":
        result = run_checking_mode()
        print "Invariant:", result
    else:
        run_animation_mode()
except Exception as e:
    #print "Error in pyB:", type(e), e.args, e
    print "Usage: python pyB.py MachineFile <SolutionFile>"
    #print e.value

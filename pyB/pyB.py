# -*- coding: utf-8 -*-
import sys
from interp import interpret, write_solutions_to_env
from environment import Environment
from helpers import file_to_AST_str, solution_file_to_AST_str, print_ast
from animation_clui import show_ui
from animation import calc_succ_states, exec_op
from definition_handler import DefinitionHandler
from ast_nodes import *
from config import default_input_filename


def read_input_string():
	file_name_str = default_input_filename
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
    ast_str = solution_file_to_AST_str(solution_file_name_str)
    exec ast_str
    write_solutions_to_env(root, env)
    if env.solutions:
        print "learnd from solution-file: ", [x for x in env.solutions] 



##### MAIN PROGRAM ######

env = Environment() # 1. create environment 
file_name_str, solution_file_name_str = read_input_string() # 2. read filenames
if solution_file_name_str: # 3. parse and use solution-file
    read_solution_file(env)
ast_string = file_to_AST_str(file_name_str) # 4. parse input-file
exec ast_string # TODO: encapsulation of parsing
dh = DefinitionHandler()
dh.repl_defs(root)
#import cProfile
#cProfile.run('mch = interpret(root, env)','profile_out.txt')
mch = interpret(root, env)

if not mch==None: #otherwise #PREDICATE
    #print "calc states..."
    op_and_state_list = calc_succ_states(env, mch)
    print mch.name," - Invariant:", mch.eval_Invariant(env)
    if op_and_state_list==[]:
        env.bstate.print_state()
        exit()
    n = show_ui(env, mch, op_and_state_list)
    input_str = "Input (0-"+str(n)+"):"
    number = raw_input(input_str)
    number = int(number)
    if number == n-1:
        if not env.bstate.last_state==None:
            env.bstate = env.bstate.last_state
        else:
            print "No undo possible"
    elif number == n:
        exit()
    else:
        env.bstate = exec_op(env, op_and_state_list, number)
	# DO-WHILE python Problem
    while not number==n:
            print mch.name," - Invariant:", mch.eval_Invariant(env)
            op_and_state_list = calc_succ_states(env, mch)
            n = show_ui(env, mch, op_and_state_list)
            input_str = "Input (0-"+str(n)+"):"
            number = raw_input(input_str)
            number = int(number)
            if number == n-1:
                if not env.bstate.last_state==None:
                    env.bstate = env.bstate.last_state
                else:
                    print "No undo possible"
            elif number == n:
                exit()
            else:
                env.bstate = exec_op(env, op_and_state_list, number)
#else:
#    env.bstate.print_state()

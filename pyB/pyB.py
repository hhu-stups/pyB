# -*- coding: utf-8 -*-
import sys
from interp import interpret
from environment import Environment
from helpers import file_to_AST_str
from animation_clui import show_ui
from animation import calc_succ_states, exec_op
from definition_handler import DefinitionHandler
from ast_nodes import *


if len(sys.argv)>1:
    file_name_str = sys.argv[1]
else:
    file_name_str = "input.txt"

ast_string = file_to_AST_str(file_name_str)
exec ast_string
dh = DefinitionHandler()
dh.repl_defs(root)
env = Environment()
mch = interpret(root, env)

if not mch==None: #otherwise #PREDICATE
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
else:
    env.bstate.print_state()
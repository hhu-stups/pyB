# -*- coding: utf-8 -*-
import sys
from interp import interpret, Environment
from helpers import file_to_AST_str
from animation_clui import show_ui
from ast_nodes import *


if len(sys.argv)>1:
    file_name_str = sys.argv[1]
else:
    file_name_str = "input.txt"

ast_string = file_to_AST_str(file_name_str)
#print ast_string
exec ast_string
env = Environment()
mch = interpret(root, env)

if not mch==None: #otherwise #PREDICATE
    if mch.find_possible_ops(env)==[]:
        exit()
    n = show_ui(env, mch)
    input_str = "Input (0-"+str(n)+"):"
    number = raw_input(input_str)
    number = int(number)
    mch.exec_op(env, number)
    while not number==n:
            print "Invariant:", mch.eval_Invariant(env)
            n = show_ui(env, mch)
            input_str = "Input (0-"+str(n)+"):"
            number = raw_input(input_str)
            number = int(number)
            if number == n-1 and not env.last_env==None:
                env = env.last_env
            elif number == n:
                exit()
            else:
                mch.exec_op(env, number)


# -*- coding: utf-8 -*-
import sys
from interp import interpret, write_solutions_to_env
from bmachine import BMachine
from environment import Environment
from helpers import file_to_AST_str, solution_file_to_AST_str
from parsing import PredicateParseUnit,ExpressionParseUnit
from animation_clui import show_ui, show_env
from animation import calc_possible_operations, exec_op
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
parse_object = parse_ast(root, env)
result = interpret(parse_object.root, env)

if isinstance(parse_object, BMachine): #otherwise #PREDICATE or #EXPRESSION 
    mch = env.root_mch
    #print "calc states..."
    op_list = calc_possible_operations(env, mch)
    print mch.name," - Invariant:", mch.eval_Invariant(env)
    if op_list==[]:
        show_env(env)
        exit()
    n = show_ui(env, mch, op_list)
    input_str = "Input (0-"+str(n)+"):"
    number = raw_input(input_str)
    number = int(number)
    if number == n-1:
        if not env.state_space.empty():
            env.state_space.undo()
        else:
            print "No undo possible"
    elif number == n:
        exit()
    else:
        bstate = exec_op(env, op_list, number,mch)
        env.state_space.add_state(bstate)
    # DO-WHILE python Problem
    while not number==n:
            print mch.name," - Invariant:", mch.eval_Invariant(env)
            op_list = calc_possible_operations(env, mch)
            n = show_ui(env, mch, op_list)
            input_str = "Input (0-"+str(n)+"):"
            number = raw_input(input_str)
            number = int(number)
            if number == n-1:
                if not env.state_space.empty():
                    env.state_space.undo()
                else:
                    print "No undo possible"
            elif number == n:
                exit()
            else:
                bstate = exec_op(env, op_list, number,mch)
                env.state_space.add_state(bstate)
#TODO: PREDICATE or #EXPRESSION 
#else:
#    env.bstate.print_state()

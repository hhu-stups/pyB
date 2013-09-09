# -*- coding: utf-8 -*-

from ast_nodes import *
from btypes import *
from helpers import file_to_AST_str, string_to_file, solution_file_to_AST_str
from environment import Environment
from parsing import parse_ast, str_ast_to_python_ast
from typing import type_check_bmch
from interp import interpret, write_solutions_to_env, set_up_constants, exec_initialisation, eval_Invariant
from definition_handler import DefinitionHandler


def run_with_prob(option_str="", bfile_name="temp"):
    from subprocess import Popen, PIPE
    p =  Popen("../ProB_2/probcli %s -sptxt %s_values.txt %s.mch" % (option_str, bfile_name, bfile_name), shell=True, stderr=PIPE, stdin=PIPE, stdout=PIPE)
    e = p.stderr
    err_out = e.read()
    print err_out
    e.close()


def run_with_pyb(bfile_name):
    # Build AST
    ast_string = file_to_AST_str("%s.mch" % bfile_name)
    ast_root = str_ast_to_python_ast(ast_string)

    # Get ProB Solution
    env = Environment()
    env._min_int = -2**31
    env._max_int = 2**31
    ast_str = solution_file_to_AST_str("%s_values.txt" % (bfile_name))
    root = str_ast_to_python_ast(ast_str)
    write_solutions_to_env(root, env)

    # Init B-mch
    dh = DefinitionHandler()                                   
    dh.repl_defs(ast_root)
    mch = parse_ast(ast_root, env)    
    type_check_bmch(ast_root, env, mch) # also checks all included, seen, used and extend    
    # side-effect: check properties and invariant 
    bstates = set_up_constants(root, env, mch, solution_file_read=True)
    env.state_space.add_state(bstates[0]) 
    bstates = exec_initialisation(root, env, mch, solution_file_read=True)
    env.state_space.add_state(bstates[0]) 
    #if mch.aAssertionsMachineClause:
    #   interpret(mch.aAssertionsMachineClause, env)
    return eval_Invariant(root, env, mch)  


class TestTeam():
    def test_team_lift(self):
        string = '''
        MACHINE Lift
        ABSTRACT_VARIABLES  floor
        INVARIANT  floor : 0..99 /* NAT */
        INITIALISATION floor := 4
        OPERATIONS
                inc = PRE floor<99 THEN floor := floor + 1 END ;
                dec = BEGIN floor := floor - 1 END 
        END
        '''
        string_to_file(string, "temp.mch")
        run_with_prob("-init ", bfile_name="temp")
        res = run_with_pyb(bfile_name="temp")
        assert res


    def test_team_volvo(self):
        run_with_prob("-init ", bfile_name="examples/Cruise_finite1")
        res = run_with_pyb(bfile_name="examples/Cruise_finite1")
        assert res


#    def test_team_systerel(self):
#        bfile_name="examples/not_public/Systerel/C578.EML.014/CF_LD_1"
#        run_with_prob("-init -p CLPFD true -p use_large_jvm_for_parser true -p TIME_OUT 60000", bfile_name)
#        res = run_with_pyb(bfile_name)
#        assert res

#   ../ProB/probcli -init -p TIME_OUT 1000 -sptxt examples/not_public/Systerel/verdi/verdi1_values.txt examples/not_public/Systerel/verdi/verdi1.mch

    # every alstom-test runs about 5min.  
#     def test_team_alstom(self):
#         run_with_prob("-init ", bfile_name="examples/not_public/Alstom/Regles/Rule_DB_Route_0001ori_modified")
#         res = run_with_pyb(bfile_name="examples/not_public/Alstom/Regles/Rule_DB_Route_0001ori_modified")
#         assert res
#         for i in range(43):
#           run_with_prob("-timeout 30000 -init -animate"+str(i), bfile_name="examples/not_public/Alstom/Regles/Rule_DB_Route_0001ori_modified")
#           res = run_with_pyb(bfile_name="examples/not_public/Alstom/Regles/Rule_DB_Route_0001ori_modified")
#           assert res
#       #pass 
#       
#       
#     def test_team_alstom2(self):
#         run_with_prob("-init ", bfile_name="examples/not_public/Alstom/Regles/Rule_DB_Route_0001ori")
#         res = run_with_pyb(bfile_name="examples/not_public/Alstom/Regles/Rule_DB_Route_0001ori")
#         assert res
#         for i in range(43):
#           run_with_prob("-timeout 30000 -init -animate"+str(i), bfile_name="examples/not_public/Alstom/Regles/Rule_DB_Route_0001ori")
#           res = run_with_pyb(bfile_name="examples/not_public/Alstom/Regles/Rule_DB_Route_0001ori")
#           assert res
#       #pass   
# 
# 
#     def test_team_alstom3(self):
#         run_with_prob("-init ", bfile_name="examples/not_public/Alstom/Regles/Rule_DB_SIGAREA_0024_ori")
#         res = run_with_pyb(bfile_name="examples/not_public/Alstom/Regles/Rule_DB_SIGAREA_0024_ori")
#         assert res
#         #import cProfile
#         #cProfile.runctx('res = run_with_pyb(bfile_name=\"examples/not_public/Alstom/Regles/Rule_DB_SIGAREA_0024_ori\")', globals(),locals())
#         for i in range(32):
#           run_with_prob("-timeout 30000 -init -animate"+str(i), bfile_name="examples/not_public/Alstom/Regles/Rule_DB_SIGAREA_0024_ori")
#           res = run_with_pyb(bfile_name="examples/not_public/Alstom/Regles/Rule_DB_SIGAREA_0024_ori")
#           assert res
#       #pass             
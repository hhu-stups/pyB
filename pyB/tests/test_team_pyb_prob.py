# -*- coding: utf-8 -*-

from ast_nodes import *
from btypes import *
from helpers import file_to_AST_str, string_to_file, solution_file_to_AST_str, find_var_nodes
from environment import Environment
from parsing import parse_ast, str_ast_to_python_ast
from typing import type_check_root_bmch, type_check_predicate
from interp import interpret, set_up_constants, exec_initialisation, eval_Invariant
from definition_handler import DefinitionHandler


def run_with_prob(option_str="", bfile_name="temp", dir=""):
    from subprocess import Popen, PIPE
    cmd_string = "../ProB/probcli %s -sptxt %s%s_values.txt %s%s.mch" % (option_str, dir, bfile_name, dir, bfile_name)
    print cmd_string
    p =  Popen(cmd_string, shell=True, stderr=PIPE, stdin=PIPE, stdout=PIPE)
    e = p.stderr
    err_out = e.read()
    print err_out
    e.close()


def run_with_pyb(bfile_name, dir=""):
    # Build AST
    ast_string = file_to_AST_str("%s%s.mch" % (dir, bfile_name))
    ast_root = str_ast_to_python_ast(ast_string)

    # Get ProB Solution
    env = Environment()
    env._min_int = -2**31
    env._max_int = 2**31
    ast_str = solution_file_to_AST_str("%s%s_values.txt" % (dir, bfile_name))
    root = str_ast_to_python_ast(ast_str)
    env.solution_root = root
    env.write_solution_nodes_to_env(root)

    # Init B-mch
    dh = DefinitionHandler(env)                                   
    dh.repl_defs(ast_root)
    mch = parse_ast(ast_root, env)    
    type_check_root_bmch(ast_root, env, mch) # also checks all included, seen, used and extend 
    #if env.solution_root:
    #    idNodes = find_var_nodes(root.children[0]) 
    #    idNames = [n.idName for n in idNodes]
    #    type_check_predicate(env.solution_root, env, idNames)   
    # side-effect: check properties and invariant 
    bstates = set_up_constants(root, env, mch, solution_file_read=True)
    env.state_space.add_state(bstates[0]) 
    bstates = exec_initialisation(root, env, mch, solution_file_read=True)
    env.state_space.add_state(bstates[0]) 
    #if mch.aAssertionsMachineClause:
    #   interpret(mch.aAssertionsMachineClause, env)
    if mch.aPropertiesMachineClause:
        assert interpret(mch.aPropertiesMachineClause, env)
    if mch.aInvariantMachineClause:
        assert interpret(mch.aInvariantMachineClause, env)

    


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
        run_with_pyb(bfile_name="temp")
 


    def test_team_volvo(self):
        run_with_prob("-init ", bfile_name="Cruise_finite1", dir="examples/not_public/volvo/")
        run_with_pyb(bfile_name="Cruise_finite1", dir="examples/not_public/volvo/")


    def test_team_whokilledagatha(self):
        run_with_prob("-init ", bfile_name="JobsPuzzle", dir="examples/")
        res = run_with_pyb(bfile_name="JobsPuzzle", dir="examples/")


#     def test_team_alstom_malaga(self):
#         bfile_name="examples/not_public/malaga/ixl_ctx1"
#         run_with_prob("-init -p CLPFD true -p use_large_jvm_for_parser true -p TIME_OUT 60000", bfile_name)
#         res = run_with_pyb(bfile_name)
#         assert res
#         
#        
    def test_team_systerel(self):
        bfile_name="examples/not_public/Systerel/C578/2013_08_14/machines_14082013/410_002_simple"
        run_with_prob("-init -p CLPFD true -p use_large_jvm_for_parser true -p TIME_OUT 60000", bfile_name)
        run_with_pyb(bfile_name)

#
#   #../ProB/probcli -init -p TIME_OUT 1000 -sptxt examples/not_public/Systerel/verdi/verdi1_values.txt examples/not_public/Systerel/verdi/verdi1.mch
# 
#    # every alstom-test runs about 15min.  
#     def test_team_alstom(self):
#         run_with_prob("-init ", bfile_name="Rule_DB_Route_0001ori_modified", dir="examples/not_public/Alstom/Regles/")
#         res = run_with_pyb(bfile_name="Rule_DB_Route_0001ori_modified", dir="examples/not_public/Alstom/Regles/")
#         assert res
#         for i in range(43):
#           run_with_prob(" -p TIME_OUT 30000 -init -animate "+str(i), bfile_name="Rule_DB_Route_0001ori_modified", dir="examples/not_public/Alstom/Regles/")
#           res = run_with_pyb(bfile_name="Rule_DB_Route_0001ori_modified", dir="examples/not_public/Alstom/Regles/")
#           assert res
#       #pass 
#       
#       
#     def test_team_alstom2(self):
#         run_with_prob("-init ", bfile_name="Rule_DB_Route_0001ori", dir="examples/not_public/Alstom/Regles/")
#         res = run_with_pyb(bfile_name="Rule_DB_Route_0001ori", dir="examples/not_public/Alstom/Regles/")
#         assert res
#         for i in range(43):
#           run_with_prob(" -p TIME_OUT 30000 -init -animate "+str(i), bfile_name="Rule_DB_Route_0001ori", dir="examples/not_public/Alstom/Regles/")
#           res = run_with_pyb(bfile_name="Rule_DB_Route_0001ori", dir="examples/not_public/Alstom/Regles/")
#           assert res
#       #pass   
# 
# 
#     def test_team_alstom3(self):
#         run_with_prob("-init ", bfile_name="Rule_DB_SIGAREA_0024_ori", dir="examples/not_public/Alstom/Regles/")
#         res = run_with_pyb(bfile_name="Rule_DB_SIGAREA_0024_ori", dir="examples/not_public/Alstom/Regles/")
#         assert res
#         #import cProfile
#         #cProfile.runctx('res = run_with_pyb(bfile_name=\"examples/not_public/Alstom/Regles/Rule_DB_SIGAREA_0024_ori\")', globals(),locals())
#         for i in range(32):
#           run_with_prob(" -p TIME_OUT 30000 -init -animate "+str(i), bfile_name="Rule_DB_SIGAREA_0024_ori", dir="examples/not_public/Alstom/Regles/")
#           res = run_with_pyb(bfile_name="Rule_DB_SIGAREA_0024_ori", dir="examples/not_public/Alstom/Regles/")
#           assert res
#       #pass             
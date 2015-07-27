# -*- coding: utf-8 -*-
from ast_nodes import *
from bexceptions import BTypeException
from btypes import *
from definition_handler import DefinitionHandler
from environment import Environment
from helpers import file_to_AST_str, string_to_file, solution_file_to_AST_str, find_var_nodes
from interp import interpret, set_up_constants, exec_initialisation, eval_Invariant
import os
from parsing import parse_ast, str_ast_to_python_ast, remove_defs_and_parse_ast
from typing import type_check_root_bmch, type_check_predicate




from config import USE_RPYTHON_CODE
if USE_RPYTHON_CODE:
     from rpython_b_objmodel import frozenset

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
    # Build b-mch AST
    ast_string = file_to_AST_str("%s%s.mch" % (dir, bfile_name))
    ast_root = str_ast_to_python_ast(ast_string)

    # Get ProB Solution, write to env
    env = Environment()
    env._min_int = -2**31
    env._max_int = 2**31
    ast_str, err = solution_file_to_AST_str("%s%s_values.txt" % (dir, bfile_name))
    assert err==''
    root = str_ast_to_python_ast(ast_str)
    env.solution_root = root
    env.write_solution_nodes_to_env(root)

    # Init B-mch
    dh = DefinitionHandler(env, remove_defs_and_parse_ast)                                   
    dh.repl_defs(ast_root)
    mch = parse_ast(ast_root, env)    
    type_check_root_bmch(ast_root, env, mch) # also checks all included, seen, used and extend 
    #if env.solution_root:
    #    idNodes = find_var_nodes(root.children[0]) 
    #    idNames = [n.idName for n in idNodes]
    #    type_check_predicate(env.solution_root, env, idNames)   
    # side-effect: check properties and invariant 
    print "team-test:calc set up.."
    bstates = set_up_constants(root, env, mch, solution_file_read=True)
    env.state_space.add_state(bstates[0]) 
    print "team-test:calc set init.."
    bstates = exec_initialisation(root, env, mch, solution_file_read=True)
    env.state_space.add_state(bstates[0]) 
    if mch.has_properties_mc:
        print "team-test:eval properties..."
        assert interpret(mch.aPropertiesMachineClause, env)
    if mch.has_invariant_mc:
        print "team-test:eval invariant..."
        assert interpret(mch.aInvariantMachineClause, env)
    #if mch.aAssertionsMachineClause:
    #    interpret(mch.aAssertionsMachineClause, env)

    


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
        dir="examples/not_public/volvo/"
        bfile_name="Cruise_finite1"
        if os.name=='nt':
            dir="examples\not_public\volvo\\"
        run_with_prob("-init ", bfile_name, dir)
        run_with_pyb(bfile_name, dir)


    def test_team_whokilledagatha(self):
        dir="examples/"
        bfile_name="JobsPuzzle"
        if os.name=='nt':
            dir="examples\\"
        run_with_prob("-init ", bfile_name, dir)
        res = run_with_pyb(bfile_name, dir)


#     def test_team_alstom_malaga(self):
#         bfile_name="examples/not_public/malaga/ixl_ctx1"
#         run_with_prob("-init -p CLPFD true -p use_large_jvm_for_parser true -p TIME_OUT 60000", bfile_name)
#         res = run_with_pyb(bfile_name)
#         assert res
#         
#   
    # TODO: move command line input to config.py     
    def test_team_systerel(self):
        # Without/with Timeout
        # 21.72 seconds/25.48:  C578_Urgent_Jul13/151_001
        # 11.06 seconds/19.76:  C578_Final_Jul13/m-PROP_SCL_VTT_0304_001
        # 51.44 seconds/74.37:  C578_Final_Jul13/m-PROP_SCL_VTT_S_0316_001 (87.32 sec Timeout=5sec)
        # 3.61 seconds/3.85:    C578/2013_08_14/machines_14082013/410_002_simple
        # 15.02 seconds/19.24:  C578/2013_08_14/machines_27082013/0021_002
        # 8.04 seconds/10.20:   C578/2013_08_14/machines_27082013/R_04_001
        # 406.27 seconds: C578/2013_08_14/machines_27082013/R_02_002 - broken since 19.11.2014 mb compute timeout
        # 379.40 seconds: C578/2013_08_14/machines_14082013/02_001 -broken since 19.11.2014 lj compute timeout
        # C578_Final_Jul13/machines2/0682_002 (27 min)
        # 405.81 seconds: C578/2013_08_14/machines_27082013/R_07_001 - broken since 26.11.2014  ig 171.29 seconds
        
        
        ####C578/2013_08_14/machines_14082013/440_004 topologic-sort key error
        
        bfile_name="examples/not_public/Systerel/C578/2013_08_14/machines_14082013/410_002_simple"
        if os.name=='nt':
            bfile_name="examples\not_public\Systerel\C578\2013_08_14\machines_14082013\410_002_simple\\"
        run_with_prob("-init -p CLPFD true -p use_large_jvm_for_parser true -p TIME_OUT 600000", bfile_name)
        run_with_pyb(bfile_name)


    # proB gens items {S1, S2, S3, S4 }:S. Typing of these elements fails. 
    # FIXME: f={(S1|->0),(S2|->0),(S3|->0),(S4|->0)} type of f is known. this can be fixed
    def test_team_defferd_set_items(self):
        import py
        bfile_name="examples/Scope"
        if os.name=='nt':
            bfile_name="examples\Scope"
        run_with_prob("-init -p CLPFD true -p use_large_jvm_for_parser true -p TIME_OUT 600000", bfile_name)
        py.test.raises(BTypeException, "run_with_pyb(bfile_name)")  
        #run_with_pyb(bfile_name)
        
        
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
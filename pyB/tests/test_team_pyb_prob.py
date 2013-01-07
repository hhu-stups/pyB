# -*- coding: utf-8 -*-

from ast_nodes import *
from btypes import *
from helpers import file_to_AST_str, string_to_file, solution_file_to_AST_str
from environment import Environment
from parsing import parse_ast, str_ast_to_python_ast
from typing import type_check_bmch
from interp import interpret, write_solutions_to_env

bfile_name = "temp"


def create_file(b_str):
    from subprocess import Popen, PIPE
    p =  Popen("echo \"%s\" > %s.mch" % (b_str, bfile_name), shell=True, stderr=PIPE, stdin=PIPE, stdout=PIPE)
    e = p.stderr
    err_out = e.read()
    print err_out
    e.close()


def run_with_prob(option_str=""):
    from subprocess import Popen, PIPE
    p =  Popen("../../ProB_115/probcli %s -sptxt %s_values.txt %s.mch" % (option_str, bfile_name, bfile_name), shell=True, stderr=PIPE, stdin=PIPE, stdout=PIPE)
    e = p.stderr
    err_out = e.read()
    print err_out
    e.close()


def run_with_pyb(inv_index):
    # Build AST
    ast_string = file_to_AST_str("%s.mch" % bfile_name)
    ast_root = str_ast_to_python_ast(ast_string)

    # Get ProB Solution
    env = Environment()
    ast_str = solution_file_to_AST_str("%s_values.txt" % (bfile_name))
    exec ast_str
    write_solutions_to_env(root, env)

    # Test
    mch = parse_ast(ast_root, env)
    type_check_bmch(ast_root, mch)
    inv = ast_root.children[inv_index]
    assert isinstance(inv, AInvariantMachineClause)
    return interpret(inv, env) # eval INVARIANT


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
        string_to_file(string, "%s.mch" % bfile_name)
        run_with_prob("-init ")
        res = run_with_pyb(inv_index=2)
        assert res

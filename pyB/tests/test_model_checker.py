import os
from animation import calc_next_states
from ast_nodes import *
from btypes import *
from definition_handler import DefinitionHandler
from environment import Environment
from helpers import file_to_AST_str
from interp import interpret, set_up_constants, exec_initialisation
from parsing import parse_ast, str_ast_to_python_ast, remove_defs_and_parse_ast
from typing import type_check_bmch


from config import USE_COSTUM_FROZENSET
if USE_COSTUM_FROZENSET:
     from rpython_b_objmodel import frozenset

class TestModelChecker():
    """
    MACHINE Lift2
    CONCRETE_VARIABLES  floor
    INVARIANT  floor : 0..99 /* NAT */
    INITIALISATION floor := 4
    OPERATIONS
        inc = PRE floor<99 THEN floor := floor + 1 END ;    
        dec = PRE floor>0  THEN floor := floor - 1 END 
    END
    """
    def test_simple_model_checking(self):
        path = "examples/Lift2.mch"
        if os.name=='nt':
            bfile_name="examples\Lift2"
        ast_string = file_to_AST_str(path)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        
        solution_file_read = False
        bstates = set_up_constants(root, env, mch, solution_file_read)
        assert len(bstates)==0 # no setup possible
        bstates = exec_initialisation(root, env, mch, solution_file_read)
        assert len(bstates)==1 # only one possibility (floor:=4)
        env.state_space.add_state(bstates[0])
        invatiant = root.children[2]
        assert isinstance(invatiant, AInvariantMachineClause)
        assert interpret(invatiant, env) 
        next_states = calc_next_states(env, mch)
        assert len(next_states)==2
        
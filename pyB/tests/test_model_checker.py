import os
from animation import calc_next_states
from ast_nodes import *
from btypes import *
from bstate import BState
from definition_handler import DefinitionHandler
from environment import Environment
from helpers import file_to_AST_str
from interp import interpret, set_up_constants, exec_initialisation
from parsing import parse_ast, str_ast_to_python_ast, remove_defs_and_parse_ast
from typing import type_check_bmch


from config import USE_RPYTHON_CODE
if USE_RPYTHON_CODE:
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
        assert len(env.state_space.seen_states)==0        
        assert isinstance(bstates[0], BState)
        env.state_space.set_current_state(bstates[0])
        assert len(env.state_space.seen_states)==1
        invatiant = root.children[2]
        assert isinstance(invatiant, AInvariantMachineClause)
        assert interpret(invatiant, env)
        assert len(env.state_space.stack)==2 
        next_states = calc_next_states(env, mch)
        assert len(next_states)==2
        assert len(env.state_space.stack)==2 # init and empty setup
        assert env.get_value('floor')==4
        env.state_space.undo()
        assert len(env.state_space.stack)==1 # setup
        assert len(env.state_space.seen_states)==1
        for n_state in next_states:
            bstate = n_state.bstate
            assert isinstance(bstate, BState)
            if not env.state_space.is_seen_state(bstate):
                env.state_space.set_current_state(bstate)
        assert len(env.state_space.stack)==3 # dec, inc, setup
        assert len(env.state_space.seen_states)==3
        assert env.get_value('floor')==3 or env.get_value('floor')==5
        
        # TODO: Bstate needs refactoring. 
        # - Remove init state
        # - dont map None to values if parsing unit is no machine
        # - check empty on stack length 0
        # model checking loop
        while not env.state_space.empty():
            assert interpret(invatiant, env) 
            next_states = calc_next_states(env, mch)
            env.state_space.undo()
            for n_state in next_states:
                bstate = n_state.bstate
                if not env.state_space.is_seen_state(bstate):
                    env.state_space.set_current_state(bstate)  
        assert len(env.state_space.seen_states)==100
        
          
        
        
        
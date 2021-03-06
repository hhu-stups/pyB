# -*- coding: utf-8 -*-
from animation_clui import show_ui
from animation import calc_next_states
from ast_nodes import *
from btypes import *
from definition_handler import DefinitionHandler
from environment import Environment
from helpers import file_to_AST_str, string_to_file
from interp import interpret, set_up_constants, exec_initialisation
from parsing import parse_ast, str_ast_to_python_ast, remove_defs_and_parse_ast
from typing import type_check_bmch
from util import arbitrary_init_machine, get_type_by_name


from config import USE_RPYTHON_CODE
if USE_RPYTHON_CODE:
     from rpython_b_objmodel import frozenset

file_name = "input.txt"
        
class TestMCHAnimation():
    
    # also tests top-level Block_sub
    def test_ani_examples_simple_acounter(self):
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
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        invatiant = root.children[2]
        assert isinstance(invatiant, AInvariantMachineClause)
        assert interpret(invatiant, env)
        for i in range(4):
            next_states = calc_next_states(env, mch)
            assert next_states[0].opName=="dec"
            bstate = next_states[0].bstate
            env.state_space.add_state(bstate)
            assert interpret(invatiant, env)
            #op_and_state_list = calc_possible_operations(env, mch)
            #exec_op(env, op_and_state_list[1], mch)
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="dec"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        assert not interpret(invatiant, env) # floor=-1



    def test_ani_toplevel_skip_op(self):
        string ='''
        MACHINE Test
        VARIABLES xx
        INVARIANT
         xx:NAT
        INITIALISATION xx:=0
        OPERATIONS
          op = skip
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)

 
    def test_ani_toplevel_assert_op(self):
        string ='''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx:=0
        OPERATIONS
         op = ASSERT 1<2 THEN skip END
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        # TODO: Test Assert Exception/Error-MSG with False Assert


    def test_ani_toplevel_choice_op(self):
        string ='''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx:=0
        OPERATIONS
          op = CHOICE xx := 2 OR xx := 1 END
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 0==env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert len(next_states)==2      #FIXME
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        assert 2==env.get_value("xx") or 1==env.get_value("xx")  




    def test_ani_toplevel_if_op(self):
        string ='''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx:=0
        OPERATIONS
          op = IF xx=0 THEN xx := 1 ELSE xx := 0 END 
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 0 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        assert 1 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        assert 0 == env.get_value("xx")


    def test_ani_toplevel_if_op2(self):
        string ='''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx:=0
        OPERATIONS
          op = IF xx>4 THEN xx := 4 ELSIF xx>3 THEN xx:=3 ELSE xx := 1 END 
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 0 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert len(next_states)==1
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        assert 1 == env.get_value("xx")
  
    def test_ani_examples_nondeterministic_sequence(self):
        string = '''
        MACHINE Sequ
        VARIABLES x, i, sum
        INVARIANT x:NATURAL & i:NATURAL & sum:NATURAL & i:{0,1,7} & sum:{0,1,7}
        INITIALISATION x:=1; i:=0; sum:=0
        OPERATIONS
        op = 
         IF i=0 THEN x::{1,7}; i := i+x; sum:= sum+i END
        END
        '''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        invatiant = root.children[2]
        assert interpret(invatiant , env)
        next_states = calc_next_states(env,mch)
        assert len(next_states)==2
        assert next_states[0].opName=="op"
        for s in next_states:
            env.state_space.add_state(s.bstate)
            assert interpret(invatiant , env)
            assert env.get_value("i") in [1,7]
            assert env.get_value("sum") in [1,7]
        
    def test_ani_toplevel_select_op(self):
        string ='''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx:=0
        OPERATIONS
          op = SELECT xx=0 THEN xx := 1 ELSE xx := 0 END 
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 0 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        assert 1 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        assert 0 == env.get_value("xx")


    def test_ani_toplevel_select_op2(self):
        string ='''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx:=0
        OPERATIONS
          op = SELECT xx=0 THEN xx := 1 WHEN xx=1 THEN xx:= 2 ELSE xx := 0 END 
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 0 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        assert 1 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        assert 2 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        assert 0 == env.get_value("xx")


    def test_ani_toplevel_select_op3(self):
        string ='''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx:=0
        OPERATIONS
          op = SELECT xx=0 THEN xx := 1 WHEN xx=1 THEN xx:= 2 END 
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 0 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        assert 1 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        assert 2 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states==[] # deadlock 



    def test_ani_toplevel_case_op(self):
        string ='''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx:=4
        OPERATIONS
          op = 
            CASE xx/2 OF 
            EITHER 0 THEN xx := 0 
            OR 2,4,8 THEN xx := 1 
            OR 3,9 THEN xx := 2 
            ELSE xx := -1 END
          END
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 4 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        assert 1 == env.get_value("xx")
        
        
    def test_ani_toplevel_any_op(self):
        string ='''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx:=8
        OPERATIONS
          op = ANY yy WHERE yy:NAT & yy*2=xx THEN xx := yy END 
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env._min_int = -16
        env._max_int = 16
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 8 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        assert 4 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        assert 2 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        assert 1 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states==[] # deadlock 


    def test_ani_toplevel_let_op(self):
        string ='''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx:=8
        OPERATIONS
          op = LET yy BE yy*2=xx IN xx := yy END 
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env._min_int = -16
        env._max_int = 16
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 8 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        assert 4 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        assert 2 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        assert 1 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states==[] # deadlock 
 
 
    def test_ani_toplevel_become_el_op(self):
        string ='''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx:=0
        OPERATIONS
          op = xx::0..1
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 0 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        #assert len(next_states)==2  #FIXME
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        assert 1 == env.get_value("xx") or 0 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        assert 1 == env.get_value("xx") or 0 == env.get_value("xx")

    # kills ProB Performance :)
    def test_ani_toplevel_become_such_op(self):
        string ='''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx:=0
        OPERATIONS
          op = xx:(xx>=0 & xx<=1)
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env._min_int = -1
        env._max_int = 5
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 0 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        #assert len(next_states)==2 #FIXME
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        assert 1 == env.get_value("xx") or 0 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        assert 1 == env.get_value("xx") or 0 == env.get_value("xx")


    def test_ani_toplevel_var_op(self):
        string ='''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx:=8
        OPERATIONS
          op = VAR yy IN yy:= xx/2; xx:=yy END
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env._min_int = -16
        env._max_int = 16
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 8 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        assert 4 == env.get_value("xx") or 0 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        assert 2 == env.get_value("xx") or 0 == env.get_value("xx")
        # TODO xx=0 or deadlock?


    def test_ani_toplevel_assert_op_args(self):
        string ='''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx:=0
        OPERATIONS
          op(zz) = ASSERT -zz<zz THEN skip END
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env._min_int = -16
        env._max_int = 16
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        # FIXMEL assert violation 0<0


    def test_ani_toplevel_choice_op_args(self):
        string ='''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx:=0
        OPERATIONS
          op(zz) = CHOICE xx := zz OR xx := -zz END
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env._min_int = -16
        env._max_int = 16
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        some_wrong = False
        for op_and_state in next_states:
            bstate = op_and_state.bstate
            env.state_space.add_state(bstate) 
            if not interpret(root.children[2], env): 
                some_wrong = True
        assert some_wrong 


    def test_ani_toplevel_if_op_args(self):
        string ='''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx:=0
        OPERATIONS
          op(zz) = IF xx=0 THEN xx := -zz ELSE xx := zz END 
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env._min_int = -16
        env._max_int = 16
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        assert len(next_states)== -1*env._min_int+env._max_int+1
        false_num = 0
        for op_and_state in next_states:
            bstate = op_and_state.bstate
            env.state_space.add_state(bstate) 
            if env.get_value("xx")<0:
                assert not interpret(root.children[2], env)
                false_num = false_num +1
            else:
                assert interpret(root.children[2], env)
        assert false_num==env._max_int


    def test_ani_toplevel_select_op_args(self):
        string ='''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx:=0
        OPERATIONS
          op(zz) = SELECT xx=zz THEN xx := 1 ELSE xx := 0 END 
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env._min_int = -16
        env._max_int = 16
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 0 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)


    def test_ani_toplevel_select_op2_args(self):
        string ='''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx:=0
        OPERATIONS
          op(zz) = SELECT xx=zz THEN xx := 1 WHEN xx=-zz THEN xx:= 2 ELSE xx := 0 END 
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env._min_int = -16
        env._max_int = 16
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 0 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)


    def test_ani_toplevel_select_op3_args(self):
        string ='''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx:=0
        OPERATIONS
          op(zz) = SELECT xx=zz THEN xx := 1 WHEN xx=1 THEN xx:= 2 END 
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env._min_int = -16
        env._max_int = 16
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 0 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)



    def test_ani_parallel_nondeterminism(self):
        string ='''
        MACHINE Test
        VARIABLES xx, yy
        INVARIANT xx:NAT & yy:NAT
        INITIALISATION xx:=0; yy:=0
        OPERATIONS
          op = xx::{1,2,3} || yy::{4,5,6}
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 0 == env.get_value("xx")
        assert 0 == env.get_value("yy")
        next_states = calc_next_states(env,mch)
        assert len(next_states)==9
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        assert env.get_value("xx") in [1,2,3]
        assert env.get_value("yy") in [4,5,6]


    def test_ani_sequence_nondeterminism(self):
        string ='''
        MACHINE Test
        VARIABLES xx, yy, zz
        INVARIANT xx:NAT & yy:NAT & zz:NAT
        INITIALISATION xx:=0; yy:=0; zz:=0
        OPERATIONS
          op = BEGIN xx:=1 ; yy::{2,3,4} ; zz:= 5 END
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 0 == env.get_value("xx")
        assert 0 == env.get_value("yy")
        assert 0 == env.get_value("zz")
        next_states = calc_next_states(env,mch)
        assert len(next_states)==3
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        assert env.get_value("xx")==1
        assert env.get_value("yy") in [2,3,4]
        assert env.get_value("zz")==5


    def test_ani_sequence_nondeterminism2(self):
        string ='''
        MACHINE Test
        VARIABLES xx, yy, zz
        INVARIANT xx:NAT & yy:NAT & zz:NAT
        INITIALISATION xx:=0; yy:=0; zz:=0
        OPERATIONS
          op = BEGIN xx:=1 ; yy:(yy>xx & yy<xx) ; zz:= 5 END
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env._min_int = -16
        env._max_int = 16
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 0 == env.get_value("xx")
        assert 0 == env.get_value("yy")
        assert 0 == env.get_value("zz")
        next_states = calc_next_states(env,mch)
        assert len(next_states)==0


    def test_ani_sequence_nondeterminism3(self):
        string ='''
        MACHINE Test
        VARIABLES xx, yy, zz
        INVARIANT xx:NAT & yy:NAT & zz:NAT
        INITIALISATION xx:=0; yy:=0; zz:=0
        OPERATIONS
          op = BEGIN xx:=1 ; yy::{2,3,4} ; zz:= xx END
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string) 

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 0 == env.get_value("xx")
        assert 0 == env.get_value("yy")
        assert 0 == env.get_value("zz")
        next_states = calc_next_states(env,mch)
        assert len(next_states)==3
        assert next_states[1].opName=="op"
        bstate = next_states[1].bstate
        env.state_space.add_state(bstate)
        bstate.print_bstate()
        assert env.get_value("xx")==1
        assert env.get_value("yy") in [2,3,4]
        assert env.get_value("zz")==1 


    def test_ani_sequence_nondeterminism4(self):
        string ='''
        MACHINE WhileLoop3
        VARIABLES sum, i, n, x
        INVARIANT sum:NATURAL & i:NATURAL & n:NATURAL & x:NATURAL & sum:{0,55}
        INITIALISATION n := 10; sum := 0; i := 0; x :=1

        OPERATIONS    
           op = 
               WHILE i<n DO
                    IF i+1<n THEN
                        x ::{1,2}
                    ELSE
                        x := 1
                    END;
            
                    i := i+x;
            
                    IF x=1 THEN
                        sum := sum + i
                    ELSE
                        sum := sum + i + (i-1)
                    END
            
               INVARIANT
                   i:NATURAL & sum:NATURAL & sum = ((i+1) * i)/2
               VARIANT 
                   n - i
               END; /* ;i:=-1 */
       
            no_deadlock = skip 
        END    '''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string) 
        
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 0 == env.get_value("sum")
        assert 0 == env.get_value("i")
        assert 1 == env.get_value("x")
        next_states = calc_next_states(env,mch)
        # FIXME: State space explosion inside nondet. while
        #assert len(next_states)==2
        assert next_states[1].opName=="op"
        bstate = next_states[1].bstate
        env.state_space.add_state(bstate)
        bstate.print_bstate()
        assert env.get_value("sum") in [0,55]
        assert env.get_value("i")==10
        assert env.get_value("x") in [1,2] 
   
                
    def test_ani_select_nondeterminism(self):
        string ='''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx:=0
        OPERATIONS
          op = SELECT xx<=0 THEN xx := -1 WHEN xx>=0 THEN xx:= 1 END 
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 0 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert len(next_states)==2


    def test_ani_any_nondeterminism(self):
        string ='''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx:=0
        OPERATIONS
          op = ANY yy WHERE yy:NAT & yy=0 or yy=1 THEN xx := yy END 
        END'''           
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        env._min_int = -16
        env._max_int = 16
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 0 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert len(next_states)==2


    def test_setup_nondeterministic1(self):        
        string = '''
        MACHINE Test
		CONSTANTS x
		PROPERTIES x:0..3

		END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        bstates = set_up_constants(root, env, mch)
        assert len(bstates)==4
        

    def test_init_nondeterministic1(self):        
        string = '''
        MACHINE         Test
        INVARIANT       xx:NAT & xx <4
        VARIABLES       xx
        INITIALISATION  xx::{0,1,2,3}
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        bstates = set_up_constants(root, env, mch)
        assert len(bstates)==0
        bstates = exec_initialisation(root, env, mch)
        assert len(bstates)==4
        for bstate in bstates:
            env.state_space.add_state(bstate)
            xx = bstate.get_value("xx", mch)
            assert xx in [0,1,2,3]
            env.state_space.undo()
            

    def test_init_nondeterministic2(self):        
        string = '''
        MACHINE Test
		VARIABLES x
		INVARIANT x:0..5
		INITIALISATION x::0..5
		END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        bstates = set_up_constants(root, env, mch)
        assert len(bstates)==0
        bstates = exec_initialisation(root, env, mch)
        assert len(bstates)==6
                        
      
    # kills ProB Performance :)
    def test_ani_toplevel_any_op_args(self):
        string ='''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx:=8
        OPERATIONS
          op(zz) = ANY yy WHERE yy:NAT & yy*zz=xx THEN xx := yy END 
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env._min_int = -16
        env._max_int = 16
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        assert len(next_states)==4
        for op_and_state in next_states:
            bstate = op_and_state.bstate
            zz = op_and_state.parameter_values[0]
            env.state_space.add_state(bstate) 
            assert zz in [1,2,4,8]


    def test_ani_toplevel_let_op_args(self):
        string ='''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx:=8
        OPERATIONS
          op(zz) = LET yy BE yy*2=zz IN xx := yy END 
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env._min_int = -1
        env._max_int = 8
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 8 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        assert len(next_states)==5 #max(abs(min_int),max_int)+1 (zero)
        for op_and_state in next_states:
            bstate = op_and_state.bstate
            zz = op_and_state.parameter_values[0]
            env.state_space.add_state(bstate) 
            assert zz in [0,2,4,6,8]


    def test_ani_toplevel_become_el_op_args0(self):
        string ='''
        MACHINE del_me
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx:=0
        OPERATIONS
          op(zz) = xx::0..zz
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env._min_int = -16
        env._max_int = 16
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 0 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        n = env._max_int+1
        assert len(next_states)==(n*n+n)/2
        for op_and_state in next_states:
            bstate = op_and_state.bstate
            zz = op_and_state.parameter_values[0]
            env.state_space.add_state(bstate) 
            xx = env.get_value("xx")
            assert xx in range(0,zz+1)


    def test_ani_toplevel_become_el_op_args1(self):
        string ='''
        MACHINE Test
		VARIABLES x, y
		INVARIANT x:NAT & y:NAT1
		INITIALISATION x:=3 ; y:=3
		OPERATIONS
			op = BEGIN x::{0,1,2} ;  y::{x}-{0} END
		END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 3 == env.get_value("x")
        assert 3 == env.get_value("y")
        next_states = calc_next_states(env,mch)
        assert len(next_states)==2
        assert next_states[0].opName=="op"
        assert next_states[1].opName=="op"
        for op_and_state in next_states:
            bstate = op_and_state.bstate
            env.state_space.add_state(bstate) 
            y = env.get_value("y")
            assert y==1 or y==2



    # kills ProB Performance :)
    def test_ani_toplevel_become_such_op_args(self):
        string ='''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx:=0
        OPERATIONS
          op(zz) = xx:(xx>=0+zz & xx<=1-zz)
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env._min_int = -1
        env._max_int = 5
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 0 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        assert len(next_states)==6 # -1: {-1,0,1,2}, 0: {0,1}, zz>=1 no solution
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate) 
        xx = env.get_value("xx")
        assert xx in [-1,0,1] # -1:{-1,0,1,2}


    def test_ani_toplevel_var_op_args(self):
        string ='''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx:=4
        OPERATIONS
          op(zz) = VAR yy IN yy:= zz/2; xx:=yy END
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env._min_int = -16
        env._max_int = 16
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 4 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        assert len(next_states)==env._max_int+(-1*env._min_int+1)
        for op_and_state in next_states:
            bstate = op_and_state.bstate
            zz = op_and_state.parameter_values[0]
            env.state_space.add_state(bstate) 
            assert zz in range(env._min_int, env._max_int+1)


    def test_ani_examples_simple_test(self):
        string ='''
        MACHINE Test
        SETS ID={aa,bb}
        CONSTANTS iv
        PROPERTIES iv:ID
        VARIABLES xx
        INVARIANT xx:ID
        INITIALISATION xx:=iv
        OPERATIONS
        Set(yy) = PRE yy:ID THEN xx:= yy END
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env._min_int = -16
        env._max_int = 16
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[5], AInvariantMachineClause)
        assert interpret(root.children[5], env)
        


    def test_ani_parameters(self):
        string = '''
        MACHINE           Books(BOOK)
        VARIABLES         read
        INVARIANT         read <: BOOK 
        INITIALISATION    read := {}
        OPERATIONS
        bb <-- newbook =
        PRE read /= BOOK
        THEN ANY tt 
            WHERE tt : BOOK - read 
            THEN bb := tt || read := read \/ {tt}
            END
        END
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env._min_int = -16
        env._max_int = 16
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env,mch)
        invariant = root.children[2]
        assert isinstance(invariant, AInvariantMachineClause)
        assert interpret(invariant, env)
        atype = get_type_by_name(env, "BOOK")
        assert isinstance(atype, PowerSetType)
        assert isinstance(atype.data, SetType)
        empty = env.get_value("read")
        assert empty==frozenset([])
        #BOOKS = env.get_value("BOOK")       
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="newbook"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)       
        #op_and_state_list = calc_possible_operations(env, mch)
        #exec_op(env, op_and_state_list[0], mch)
        read = env.get_value("read")
        assert len(read)==1
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="newbook"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        #op_and_state_list = calc_possible_operations(env, mch)
        #exec_op(env, op_and_state_list[0], mch)
        read = env.get_value("read")
        assert len(read)==2
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="newbook"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        #op_and_state_list = calc_possible_operations(env, mch)
        #exec_op(env, op_and_state_list[0], mch)
        read = env.get_value("read")
        assert len(read)==3


    def test_ani_deferred_sets(self):
        string = '''
        MACHINE           Doors
        SETS              DOOR; POSITION = {open, closed}
        VARIABLES         position
        INVARIANT         position : DOOR --> POSITION
        INITIALISATION    position := DOOR * {closed}
        OPERATIONS
            opening(dd) = 
            PRE dd : DOOR THEN position(dd) := open END;

            closedoor(dd) = 
            PRE dd : DOOR THEN position(dd) := closed END
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env, mch)
        assert isinstance(root.children[3], AInvariantMachineClause)
        assert interpret(root.children[3], env)


    def test_ani_deferred_sets_2(self):
        string = '''
        MACHINE           Keys
        SETS              KEY
        VARIABLES         keys
        INVARIANT         keys <: KEY
        INITIALISATION    keys := {}
        OPERATIONS
           insertkey(kk) =
           PRE kk : KEY THEN keys := keys \/ {kk} END;
           
           removekey(kk) =
           PRE kk : KEY THEN keys := keys - {kk} END
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env, mch)
        assert isinstance(root.children[3], AInvariantMachineClause)
        assert interpret(root.children[3], env)
        empty = env.get_value("keys")
        assert empty==frozenset([])       
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="insertkey"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)
        #op_and_state_list = calc_possible_operations(env, mch)
        #exec_op(env, op_and_state_list[0], mch)
        keys = env.get_value("keys")
        assert len(keys)==1


    def test_schneider_inclusion(self):
        # side effect: loads examples/Doors.mch
        string = '''
        MACHINE           Locks
        INCLUDES          Doors
        PROMOTES          closedoor
        SETS              STATUS = {locked, unlocked}
        VARIABLES         status
        INVARIANT         status : DOOR --> STATUS & position~[{open}] <: status~[{unlocked}]
        INITIALISATION    status := DOOR * {locked}
        OPERATIONS
            opendoor(dd) =
            PRE dd : DOOR & status(dd) = unlocked
            THEN opening(dd)
            END;

            unlockdoor(dd) =
            PRE dd : DOOR
            THEN status(dd) := unlocked
            END;

            lockdoor(dd) =
            PRE dd : DOOR & position(dd) = closed
            THEN status(dd) := locked
            END
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        possible_ops = [op.op_name for op in env.visible_operations]
        assert sorted(possible_ops) == ['closedoor', 'lockdoor', 'opendoor', 'unlockdoor']
        arbitrary_init_machine(root, env, mch)
        assert isinstance(root.children[5], AInvariantMachineClause)
        assert interpret(root.children[5], env)

        next_states = calc_next_states(env,mch)
        assert next_states[6].opName =="unlockdoor"
        bstate = next_states[6].bstate
        env.state_space.add_state(bstate)
        next_states = calc_next_states(env,mch)
        assert next_states[6].opName =="opendoor"
        bstate = next_states[6].bstate
        env.state_space.add_state(bstate)                
        # Test PROMOTES:
        names = [op.opName for op in next_states]
        assert  "closedoor" in names
        # Vars in Locks: test if lookuperr.
        env.get_value("DOOR")
        env.get_value("POSITION")
        env.get_value("position")
        

    def test_schneider_inclusion2(self):
        # side effect: loades examples/Doors.mch  and Looks.mch and Keys.mch      
        string = '''
        MACHINE           Safes
        INCLUDES          Locks, Keys
        PROMOTES          opendoor, closedoor, lockdoor
        CONSTANTS         unlocks
        PROPERTIES        unlocks : KEY >->> DOOR
        INVARIANT         status~[{unlocked}] <: unlocks[keys]
        OPERATIONS
            insert(kk,dd) =
            PRE kk : KEY & dd : DOOR & unlocks(kk) = dd
            THEN insertkey(kk)
            END;
  
            extract(kk,dd) =
            PRE kk : KEY & dd : DOOR & unlocks(kk) = dd & status(dd) = locked
            THEN removekey(kk)
            END;

            unlock(dd) =
            PRE dd : DOOR & unlocks~(dd) : keys
            THEN unlockdoor(dd)
            END;

            quicklock(dd) =
            PRE dd : DOOR & position(dd) = closed
            THEN lockdoor(dd) || removekey(unlocks~(dd))
            END
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Config
        #import enumeration
        #enumeration.deferred_set_elements_num = 2
        
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        possible_ops = [op.op_name for op in env.visible_operations]
        assert sorted(possible_ops)== ['closedoor', 'extract', 'insert', 'lockdoor', 'opendoor', 'quicklock', 'unlock']
        arbitrary_init_machine(root, env, mch)
        assert isinstance(root.children[5], AInvariantMachineClause)
        assert interpret(root.children[5], env)
        #op_and_state_list = calc_possible_operations(env, mch) #opening enabled
        next_states = calc_next_states(env,mch)
        assert next_states[6].opName =="insert"
        bstate = next_states[6].bstate     
        # test PROMOTES:
        names = [op.opName for op in next_states]
        result = frozenset(names)
        assert result==frozenset(['insert', 'lockdoor', 'extract', 'closedoor', 'quicklock'])
        empty = env.get_value("keys")
        assert empty==frozenset([])
        #exec_op(env, op_and_state_list[0], mch) # insert
        env.state_space.add_state(bstate)
        one = env.get_value("keys")
        assert len(one)==1
        next_states = calc_next_states(env,mch)
        names = [op.opName for op in next_states]
        assert frozenset(names)==frozenset(['insert', 'lockdoor', 'extract', 'closedoor', 'quicklock', 'unlock'])
        

    def test_schneider_sees(self):
        # side effect: loades examples/Goods.mch        
        string = '''
        MACHINE           Price
        SEES              Goods
        VARIABLES         price
        INVARIANT         price : GOODS --> NAT1
        INITIALISATION    price :: GOODS --> NAT1
        OPERATIONS
            setprice(gg,pp) =
            PRE gg : GOODS & pp : NAT1
            THEN price(gg) := pp
            END;

            pp <-- pricequery(gg) =
            PRE gg : GOODS THEN pp := price(gg) END
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env._min_int = -1
        env._max_int = 5
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        possible_ops = [op.op_name for op in env.visible_operations]
        assert sorted(possible_ops)== ['pricequery', 'setprice']
        arbitrary_init_machine(root, env, mch)
        assert not env.get_value("GOODS")==None
        next_states = calc_next_states(env,mch)
        names = [op.opName for op in next_states]
        assert frozenset(names)==frozenset(['setprice', 'pricequery'])


    def test_schneider_sees2(self):
        # side effect: loades examples/Goods.mch and Price.mch           
        string = '''
        MACHINE           Shop
        SEES              Price, Goods
        VARIABLES         takings
        INVARIANT         takings : NAT
        INITIALISATION    takings := 0
        OPERATIONS
            sale(gg) =
            PRE gg : GOODS & takings + price(gg) <= 2147483647 THEN takings := takings + price(gg) END;

            tt <-- total = tt := takings
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        env._min_int = -1
        env._max_int = 5
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        possible_ops = [op.op_name for op in env.visible_operations]
        assert sorted(possible_ops)== ['Price.pricequery', 'Price.setprice', 'sale', 'total']
        arbitrary_init_machine(root, env, mch)
        assert not env.get_value("GOODS")==None
        assert not env.get_value("price")==None
        assert env.get_value("takings")==0
        next_states = calc_next_states(env,mch)
        names = [op.opName for op in next_states]
        assert frozenset(names)==frozenset(['setprice', 'pricequery','total','sale'])
        
       
    def test_schneider_sees3(self):
        # TODO: crashs if min_int = -2
        # side effect: loades examples/Goods.mch and Price.mch           
        string = '''
        MACHINE           Customer
        SEES              Price, Goods 
        CONSTANTS         limit
        PROPERTIES        limit : GOODS --> NAT1
        VARIABLES         purchases
        INVARIANT         purchases <: GOODS
        INITIALISATION    purchases := {}
        OPERATIONS
        pp <-- buy(gg) =
            PRE gg : GOODS & price(gg) <= limit(gg)
            THEN purchases := purchases \/ {gg} || pp <-- pricequery(gg)
            END
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env._min_int = -1
        env._max_int = 5
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        possible_ops = [op.op_name for op in env.visible_operations]
        assert sorted(possible_ops)== ['Price.pricequery', 'Price.setprice', 'buy']
        arbitrary_init_machine(root, env, mch)
        assert not env.get_value("GOODS")==None
        assert not env.get_value("price")==None
        assert isinstance(root.children[5], AInvariantMachineClause)
        assert interpret(root.children[5], env)
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="buy"
        name = next_states[0].return_names[0]
        value = next_states[0].return_values[0]
        assert name == "pp" 
        assert value in range(env._min_int, env._max_int)

     
                
    def test_schneider_uses(self):        
        string = '''
        MACHINE           Marriage
        USES              Life
        VARIABLES         marriage
        INVARIANT         marriage : male >+> female
        INITIALISATION    marriage := {}
        OPERATIONS
            wed(mm,ff) =
            PRE mm : male & mm /: dom(marriage) & ff : female & ff /: ran(marriage)
            THEN marriage(mm) := ff
            END;

            part(mm,ff) =
            PRE mm : male & ff : female & mm |->ff : marriage
            THEN marriage := marriage - {mm |-> ff}
            END;

            pp <-- partner(nn) =
             PRE nn: PERSON & nn : dom(marriage) \/ ran(marriage)
             THEN 
              IF nn : dom(marriage)
              THEN pp := marriage(nn)
              ELSE pp := marriage~(nn)
             END
            END
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        possible_ops = [op.op_name for op in env.visible_operations]
        assert sorted(possible_ops)== ['Life.born', 'Life.die', 'part', 'partner', 'wed']
        arbitrary_init_machine(root, env, mch)
        value = env.get_value("marriage") 
        assert value==frozenset([])
        value1 = env.get_value("male")
        assert value1==frozenset([])
        value2 = env.get_value("female")
        assert value2==frozenset([])

        
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="born"
        bstate = next_states[0].bstate
        env.state_space.add_state(bstate)  
        names = [op.opName for op in next_states]        
        #op_and_state_list = calc_possible_operations(env, mch) 
        #names = [op[0].opName for op in op_and_state_list]
        assert frozenset(names)==frozenset(['born'])
        #exec_op(env, op_and_state_list[0], mch) # born
        #op_and_state_list = calc_possible_operations(env, mch) 
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="born"
        bstate = next_states[0].bstate
        names = [op.opName for op in next_states]
        assert frozenset(names)==frozenset(['born', 'die'])


    def test_extends(self):
        string = '''
        MACHINE           Books2(B)
        EXTENDS           Books(B)
        OPERATIONS
            rr <-- show = rr := read
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env, mch)
        value = env.get_value("read") 
        assert value==frozenset([])
        next_states = calc_next_states(env,mch)
        assert next_states[3].opName=="show"
        bstate = next_states[3].bstate
        names = [op.opName for op in next_states]         
        #op_and_state_list = calc_possible_operations(env, mch) 
        #names = [op.opName for op in op_and_state_list]
        assert frozenset(names)==frozenset(['show','newbook'])

    # ISSUE 31
    import pytest
    @pytest.mark.xfail
    def test_extends_with_arg(self):
        string = '''
        MACHINE Test
        EXTENDS Club(2)
        END '''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env._min_int = -1
        env._max_int = 5
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        bstates = set_up_constants(root, env, mch)
        for s in bstates:
            env.state_space.add_state(s)
            assert env.get_value("capacity")==2
            assert env.get_value("total")>2
            env.state_space.undo()     


    def test_scheduler(self):        
        string = '''
        MACHINE scheduler
        SETS    PID 
        VARIABLES active, ready, waiting
        DEFINITIONS scope_PID == 1..3
        INVARIANT  active : POW(PID) & ready : POW(PID) & waiting: POW(PID) & /* the types */
                   /* and now the rest of the invariant */
                   active <: PID &
                   ready <: PID   &
                   waiting <: PID &
                   (ready /\ waiting) = {} &
                   active /\ (ready \/ waiting) = {} &
                   card(active) <= 1 &
                   ((active = {})  => (ready = {}))
                          
        INITIALISATION  active := {} || ready := {} || waiting := {}
            
        OPERATIONS
        
        rr <-- nr_ready = rr:= card(ready);
        
        new(pp) =
            SELECT
                pp : PID  &
                pp /: active &
                pp /: (ready \/ waiting) 
            THEN
                waiting := (waiting \/ { pp })
            END;
        
        del(pp) =
            SELECT
                pp : waiting 
            THEN
                waiting := waiting - { pp }
            END;
            
        ready(rr) =
                SELECT
                        rr : waiting
                THEN
                        waiting := (waiting - {rr}) ||
                        IF (active = {}) THEN
                           active := {rr}
                        ELSE
                           ready := ready \/ {rr} 
                        END
                END; 
                    
        swap =
                SELECT
                        active /= {}
                THEN
                        waiting := (waiting \/ active) ||
                        IF (ready = {}) THEN
                           active := {}
                        ELSE
                           ANY pp WHERE pp : ready
                           THEN
                               active := {pp} ||
                               ready := ready - {pp} 
                           END
                        END
                END       
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        dh = DefinitionHandler(env, remove_defs_and_parse_ast)
        dh.repl_defs(root)
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env, mch)
        next_states = calc_next_states(env,mch)
        names = [op.opName for op in next_states]  
        assert frozenset(names)==frozenset(['new','nr_ready'])


    def test_Farmer(self):
        string = '''
        MACHINE Farmer
        SETS
         Obj={farmer,fox, chicken, grain}
        DEFINITIONS
          safe(s) == (!(x,y).(x:s & y:s => x|->y /: eats));
          GOAL == (far=Obj)
        CONSTANTS eats
        PROPERTIES
         eats: Obj +-> Obj &
         eats = {fox |-> chicken, chicken |-> grain}
        VARIABLES near,far
        INVARIANT
         near<:Obj & far<:Obj & near \/ far = Obj & near /\ far = {}
        INITIALISATION near,far := Obj,{}
        OPERATIONS
          Move_far(x) = PRE farmer:near & x<: Obj-{farmer} & card(x)<2 & safe(far) THEN
              near,far := (near - {farmer}) - x, far \/ {farmer} \/ x
          END;
          Move_near(x) = PRE farmer:far & x<: Obj-{farmer} & card(x)<2 & safe(near) THEN
              far,near := (far - {farmer}) - x, near \/ {farmer} \/ x
          END;
          YouLoose = PRE (farmer:near & not(safe(far))) or
                         (farmer:far  & not(safe(near))) THEN skip END
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        dh = DefinitionHandler(env, remove_defs_and_parse_ast)
        dh.repl_defs(root)
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env, mch)
        assert isinstance(root.children[6], AInvariantMachineClause)
        assert interpret(root.children[6], env)
        near = env.get_value("near") 
        far = env.get_value("far") 
        assert near==frozenset(["farmer","fox","chicken","grain"]) 
        assert far==frozenset([])
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="Move_far"
        bstate = next_states[0].bstate   
        #op_and_state_list = calc_possible_operations(env, mch) 
        #names = [op.opName for op in op_and_state_list]
      
        
    # not B spec.    
    def test_genAST_sub_while(self):
        string = '''
        MACHINE test
        VARIABLES varLoc, cpt
        INVARIANT
          varLoc:NAT & cpt:NAT
        INITIALISATION varLoc:= 0; cpt:=0
        OPERATIONS
        op = 
            BEGIN 
               BEGIN 
                 varLoc := 5 ; 
                 cpt := 0
               END;
               WHILE cpt<5 DO
                    varLoc := varLoc + 1;
                    cpt := cpt+1 
               INVARIANT
                    cpt : NAT & cpt<=5 & varLoc:NAT & varLoc = 5 + cpt
               VARIANT 
                  5 - cpt
               END
            END
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env._max_int = 10
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env, mch) # init VARIABLES and eval INVARIANT
        #op_and_state_list = calc_possible_operations(env, mch) 
        next_states = calc_next_states(env,mch)
        assert next_states[0].opName=="op"
        bstate = next_states[0].bstate      
        #assert op_and_state_list[0][0].opName=="op"
        varLoc = env.get_value("varLoc") 
        assert varLoc ==0
        #exec_op(env, op_and_state_list[0], mch)
        env.state_space.add_state(bstate)
        varLoc = env.get_value("varLoc") 
        assert varLoc ==10
        

    # not B spec.    
    def test_genAST_sub_while_nondeterminism(self):
        string = '''        
        MACHINE Test
        VARIABLES rand, num
        INVARIANT rand:NAT & num:INT
        INITIALISATION rand:=1; num:=4
        OPERATIONS
        op = 
        BEGIN
           num:=4;
           WHILE num-rand>0 DO
                rand::{1,2};
                num := num-rand 
           INVARIANT
                num : INT & num:-1..4 & rand:NAT1 
           VARIANT 
              num
           END
        END
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env, mch) # init VARIABLES and eval INVARIANT
        next_states = calc_next_states(env,mch)
        assert len(next_states)==4
        for n in next_states:
            bstate = n.bstate
            env.state_space.add_state(bstate)
            rand = env.get_value("rand")
            num  = env.get_value("num")
            assert (rand,num) in [(1,1),(2,0),(2,1),(2,2)] 
 
       
    def test_genAST_sub_op_call_nondeterminism(self):
        # examples/Testcase.mch        
        #MACHINE Testcase
        #VARIABLES xx
        #INVARIANT xx:NAT
        #INITIALISATION xx:=4
        #OPERATIONS
        #  op1 = xx::{1,2,3};
        #  op2(zz) = xx::{1,2,zz};
        #  rr <-- op3 = rr::{1,2,3};
        #  rr <-- op4(zz) = rr::{1,2,zz}
        #END
        string = '''
        MACHINE           Test
        INCLUDES          Testcase
        VARIABLES         yy
        INVARIANT         yy:NAT
        INITIALISATION    yy := 1
        OPERATIONS
           opA = op1;
           opB = op2(4);
           opC = yy <-- op3;
           opD = yy <-- op4(4)
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env, mch) # init VARIABLES and eval INVARIANT
        next_states = calc_next_states(env,mch)
        assert len(next_states)==3*4

    # issue 33 Page 181. 8.3B
    import pytest
    @pytest.mark.xfail
    def test_genAST_includes_with_alias(self):        
        string= '''
        MACHINE Test
        INCLUDES Alias.Testcase
        VARIABLES         yy
        INVARIANT         yy:NAT
        INITIALISATION    yy := 1
        OPERATIONS
        op = yy <-- Alias.op3
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        arbitrary_init_machine(root, env, mch) # init VARIABLES and eval INVARIANT
        next_states = calc_next_states(env,mch)        
        assert len(next_states)==3
        
        
    def test_concrete_variables(self):        
        string = '''
        MACHINE         Test
        CONCRETE_VARIABLES       xx
        INVARIANT       xx:NAT
        INITIALISATION  xx:=42
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        bstates = set_up_constants(root, env, mch)
        assert len(bstates)==0
        bstates = exec_initialisation(root, env, mch)
        assert len(bstates)==1


    def test_abstract_constants(self):        
        string = '''
        MACHINE         Tets
        PROPERTIES      num:NAT & num <4
        ABSTRACT_CONSTANTS       num
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)   

        # Test
        env = Environment()
        env._min_int = -1
        env._max_int = 5
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        bstates = set_up_constants(root, env, mch)
        assert len(bstates)==4
        

    import pytest
    @pytest.mark.xfail 
    def test_properties_without_constants(self):        
        string = '''
        MACHINE Scope /*modified Schnieder book page 115*/
		SETS S
		PROPERTIES card(S)=4 
		VARIABLES f
		INVARIANT f:S --> 0..6 
		INITIALISATION f:=S*{0}
		OPERATIONS
		op1(rr, nn) = PRE rr:S & nn:1..6 & f(rr)=0 
				  THEN f(rr):= nn
				  END;
		nn <-- op2 = nn:= SIGMA(zz).(zz:S | f(zz))
		END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)   

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        # FIXME: setting deferred set elements to config.py value.
        bstates = set_up_constants(root, env, mch) 
        S=env.get_value("S")
        assert len(S)==4 

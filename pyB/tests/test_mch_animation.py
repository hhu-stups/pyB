# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from environment import Environment
from interp import interpret, _init_machine
from helpers import file_to_AST_str, string_to_file
from animation_clui import show_ui
from animation import calc_next_states
from definition_handler import DefinitionHandler
from parsing import parse_ast
from typing import type_check_bmch

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
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        invatiant = root.children[2]
        assert isinstance(invatiant, AInvariantMachineClause)
        assert interpret(invatiant, env)
        for i in range(4):
            next_states = calc_next_states(env,mch)
            assert next_states[1][0]=="dec"
            bstate = next_states[1][3]
            env.state_space.add_state(bstate)
            assert interpret(invatiant, env)
            #op_and_state_list = calc_possible_operations(env, mch)
            #exec_op(env, op_and_state_list[1], mch)
        next_states = calc_next_states(env,mch)
        assert next_states[1][0]=="dec"
        bstate = next_states[1][3]
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
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        bstate = next_states[0][3]
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
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        bstate = next_states[0][3]
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
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 0==env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        bstate = next_states[0][3]
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
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 0 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        bstate = next_states[0][3]
        env.state_space.add_state(bstate)
        assert 1 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        bstate = next_states[0][3]
        env.state_space.add_state(bstate)
        assert 0 == env.get_value("xx")


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
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 0 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        bstate = next_states[0][3]
        env.state_space.add_state(bstate)
        assert 1 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        bstate = next_states[0][3]
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
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 0 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        bstate = next_states[0][3]
        env.state_space.add_state(bstate)
        assert 1 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        bstate = next_states[0][3]
        env.state_space.add_state(bstate)
        assert 2 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        bstate = next_states[0][3]
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
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 0 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        bstate = next_states[0][3]
        env.state_space.add_state(bstate)
        assert 1 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        bstate = next_states[0][3]
        env.state_space.add_state(bstate)
        assert 2 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states==[] # deadlock 



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
        exec ast_string

        # Test
        env = Environment()
        env._max_int = 16
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 8 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        bstate = next_states[0][3]
        env.state_space.add_state(bstate)
        assert 4 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        bstate = next_states[0][3]
        env.state_space.add_state(bstate)
        assert 2 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        bstate = next_states[0][3]
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
        exec ast_string

        # Test
        env = Environment()
        env._max_int = 16
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 8 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        bstate = next_states[0][3]
        env.state_space.add_state(bstate)
        assert 4 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        bstate = next_states[0][3]
        env.state_space.add_state(bstate)
        assert 2 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        bstate = next_states[0][3]
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
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 0 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        bstate = next_states[0][3]
        env.state_space.add_state(bstate)
        assert 1 == env.get_value("xx") or 0 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        bstate = next_states[0][3]
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
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 0 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        bstate = next_states[0][3]
        env.state_space.add_state(bstate)
        assert 1 == env.get_value("xx") or 0 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        bstate = next_states[0][3]
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
        exec ast_string

        # Test
        env = Environment()
        env._max_int = 16
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 8 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        bstate = next_states[0][3]
        env.state_space.add_state(bstate)
        assert 4 == env.get_value("xx") or 0 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        bstate = next_states[0][3]
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
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        bstate = next_states[0][3]
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
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        bstate = next_states[0][3]
        env.state_space.add_state(bstate)
        some_wrong = False
        for op_and_state in next_states:
            bstate = op_and_state[3]
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
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        assert len(next_states)== -1*env._min_int+env._max_int+1
        false_num = 0
        for op_and_state in next_states:
            bstate = op_and_state[3]
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
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 0 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        bstate = next_states[0][3]
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
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 0 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        bstate = next_states[0][3]
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
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 0 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        bstate = next_states[0][3]
        env.state_space.add_state(bstate)


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
        exec ast_string

        # Test
        env = Environment()
        env._max_int = 8
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        assert len(next_states)==4
        for op_and_state in next_states:
            bstate = op_and_state[3]
            zz = op_and_state[1][0]
            env.state_space.add_state(bstate) 
            assert zz[1] in [1,2,4,8]


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
        exec ast_string

        # Test
        env = Environment()
        env._max_int = 8
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 8 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        assert len(next_states)==5
        for op_and_state in next_states:
            bstate = op_and_state[3]
            zz = op_and_state[1][0]
            env.state_space.add_state(bstate) 
            assert zz[1] in [0,2,4,6,8]


#     def test_ani_toplevel_become_el_op_args(self):
#         string ='''
#         MACHINE del_me
#         VARIABLES xx
#         INVARIANT xx:NAT
#         INITIALISATION xx:=0
#         OPERATIONS
#           op(zz) = xx::0..zz
#         END'''
#         # Build AST
#         string_to_file(string, file_name)
#         ast_string = file_to_AST_str(file_name)
#         exec ast_string
# 
#         # Test
#         env = Environment()
#         mch = parse_ast(root, env)
#         type_check_bmch(root, mch) # also checks all included, seen, used and extend
#         _init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
#         assert isinstance(root.children[2], AInvariantMachineClause)
#         assert interpret(root.children[2], env)
#         assert 0 == env.get_value("xx")
#         next_states = calc_next_states(env,mch)
#         assert next_states[0][0]=="op"
#         assert len(next_states)==5
#         for op_and_state in next_states:
#             bstate = op_and_state[3]
#             zz = op_and_state[1][0]
#             env.state_space.add_state(bstate) 
#             xx = env.get_value("xx")
#             assert xx in range(0,zz[1]+1)
# 
# 
#     # kills ProB Performance :)
#     def test_ani_toplevel_become_such_op_args(self):
#         string ='''
#         MACHINE Test
#         VARIABLES xx
#         INVARIANT xx:NAT
#         INITIALISATION xx:=0
#         OPERATIONS
#           op(zz) = xx:(xx>=0+zz & xx<=1-zz)
#         END'''
#         # Build AST
#         string_to_file(string, file_name)
#         ast_string = file_to_AST_str(file_name)
#         exec ast_string
# 
#         # Test
#         env = Environment()
#         mch = parse_ast(root, env)
#         type_check_bmch(root, mch) # also checks all included, seen, used and extend
#         _init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
#         assert isinstance(root.children[2], AInvariantMachineClause)
#         assert interpret(root.children[2], env)
#         assert 0 == env.get_value("xx")
#         next_states = calc_next_states(env,mch)
#         assert next_states[0][0]=="op"
#         assert len(next_states)==2
#         bstate = next_states[0][3]
#         env.state_space.add_state(bstate) 
#         xx = env.get_value("xx")
#         assert xx in [0,1]


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
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert 4 == env.get_value("xx")
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        assert len(next_states)==env._max_int+(-1*env._min_int+1)
        for op_and_state in next_states:
            bstate = op_and_state[3]
            zz = op_and_state[1][0]
            env.state_space.add_state(bstate) 
            assert zz[1] in range(env._min_int, env._max_int+1)


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
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env,mch) # init VARIABLES and eval INVARIANT
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
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env,mch)
        invariant = root.children[2]
        assert isinstance(invariant, AInvariantMachineClause)
        assert interpret(invariant, env)
        atype = env.get_type("BOOK")
        assert isinstance(atype, PowerSetType)
        assert isinstance(atype.data, SetType)
        empty = env.get_value("read")
        assert empty==frozenset([])
        #BOOKS = env.get_value("BOOK")       
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="newbook"
        bstate = next_states[0][3]
        env.state_space.add_state(bstate)       
        #op_and_state_list = calc_possible_operations(env, mch)
        #exec_op(env, op_and_state_list[0], mch)
        read = env.get_value("read")
        assert len(read)==1
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="newbook"
        bstate = next_states[0][3]
        env.state_space.add_state(bstate)
        #op_and_state_list = calc_possible_operations(env, mch)
        #exec_op(env, op_and_state_list[0], mch)
        read = env.get_value("read")
        assert len(read)==2
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="newbook"
        bstate = next_states[0][3]
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
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env, mch)
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
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env, mch)
        assert isinstance(root.children[3], AInvariantMachineClause)
        assert interpret(root.children[3], env)
        empty = env.get_value("keys")
        assert empty==frozenset([])       
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="insertkey"
        bstate = next_states[0][3]
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
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env, mch)
        assert isinstance(root.children[5], AInvariantMachineClause)
        assert interpret(root.children[5], env)

        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="unlockdoor"
        bstate = next_states[0][3]
        env.state_space.add_state(bstate)
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="opendoor"
        bstate = next_states[0][3]
        env.state_space.add_state(bstate)                
        #op_and_state_list = calc_possible_operations(env, mch)
        #exec_op(env, op_and_state_list[0], mch)
        #op_and_state_list = calc_possible_operations(env, mch) #opening enabled
        #exec_op(env, op_and_state_list[0], mch)
        # Test PROMOTES:
        names = [op[0] for op in next_states]
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
        exec ast_string
        
        # Config
        #import enumeration
        #enumeration.deferred_set_elements_num = 2
        
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env, mch)
        assert isinstance(root.children[5], AInvariantMachineClause)
        assert interpret(root.children[5], env)
        #op_and_state_list = calc_possible_operations(env, mch) #opening enabled
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="insert"
        bstate = next_states[0][3]       
        # test PROMOTES:
        names = [op[0] for op in next_states]
        assert frozenset(names)==frozenset(['insert', 'lockdoor', 'extract', 'closedoor', 'quicklock'])
        empty = env.get_value("keys")
        assert empty==frozenset([])
        #exec_op(env, op_and_state_list[0], mch) # insert
        env.state_space.add_state(bstate)
        one = env.get_value("keys")
        assert len(one)==1
        next_states = calc_next_states(env,mch)
        #print next_states
        bstate = next_states[0][3]
        names = [op[0] for op in next_states]
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
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env, mch)
        assert not env.get_value("GOODS")==None
        #op_and_state_list = calc_possible_operations(env, mch) 
        #names = [op[0].opName for op in op_and_state_list]
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="setprice"
        bstate = next_states[0][3]
        names = [op[0] for op in next_states]
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
        exec ast_string
        
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env, mch)
        assert not env.get_value("GOODS")==None
        assert not env.get_value("price")==None
        assert env.get_value("takings")==0
        #op_and_state_list = calc_possible_operations(env, mch) 
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="sale"
        bstate = next_states[0][3]
        names = [op[0] for op in next_states]
        assert frozenset(names)==frozenset(['setprice', 'pricequery','total','sale'])
        
        
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
        exec ast_string
        
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env, mch)
        value = env.get_value("marriage") 
        assert value==frozenset([])
        
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="born"
        bstate = next_states[0][3]
        env.state_space.add_state(bstate)  
        names = [op[0] for op in next_states]        
        #op_and_state_list = calc_possible_operations(env, mch) 
        #names = [op[0].opName for op in op_and_state_list]
        assert frozenset(names)==frozenset(['born'])
        #exec_op(env, op_and_state_list[0], mch) # born
        #op_and_state_list = calc_possible_operations(env, mch) 
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="born"
        bstate = next_states[0][3]
        names = [op[0] for op in next_states]
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
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env, mch)
        value = env.get_value("read") 
        assert value==frozenset([])
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="show"
        bstate = next_states[0][3]
        names = [op[0] for op in next_states]         
        #op_and_state_list = calc_possible_operations(env, mch) 
        #names = [op[0].opName for op in op_and_state_list]
        assert frozenset(names)==frozenset(['show','newbook'])
        

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
        exec ast_string
        
        # Test
        dh = DefinitionHandler()
        dh.repl_defs(root)
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env, mch)
        #op_and_state_list = calc_possible_operations(env, mch) 
        #names = [op[0].opName for op in op_and_state_list]
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="nr_ready"
        bstate = next_states[0][3]
        names = [op[0] for op in next_states]  
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
        exec ast_string
        
        # Test
        dh = DefinitionHandler()
        dh.repl_defs(root)
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        _init_machine(root, env, mch)
        assert isinstance(root.children[6], AInvariantMachineClause)
        assert interpret(root.children[6], env)
        near = env.get_value("near") 
        far = env.get_value("far") 
        assert near==frozenset(["farmer","fox","chicken","grain"]) 
        assert far==frozenset([])
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="Move_far"
        bstate = next_states[0][3]   
        #op_and_state_list = calc_possible_operations(env, mch) 
        #names = [op[0].opName for op in op_and_state_list]
      
        
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
        exec ast_string

        # Test
        env = Environment()
        env._max_int = 10
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        interpret(root, env) # init VARIABLES and eval INVARIANT
        #op_and_state_list = calc_possible_operations(env, mch) 
        next_states = calc_next_states(env,mch)
        assert next_states[0][0]=="op"
        bstate = next_states[0][3]      
        #assert op_and_state_list[0][0].opName=="op"
        varLoc = env.get_value("varLoc") 
        assert varLoc ==0
        #exec_op(env, op_and_state_list[0], mch)
        env.state_space.add_state(bstate)
        varLoc = env.get_value("varLoc") 
        assert varLoc ==10
# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from environment import Environment
from interp import interpret
from helpers import file_to_AST_str, string_to_file
from animation_clui import show_ui
from animation import calc_succ_states, exec_op

file_name = "input.txt"

class TestMCHAnimation():
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
        mch = interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        for i in range(4):
            op_and_state_list = calc_succ_states(env, mch)
            env = exec_op(env, op_and_state_list, 1)
            assert interpret(root.children[2], env)
        op_and_state_list = calc_succ_states(env, mch)
        env = exec_op(env, op_and_state_list, 1)
        assert not interpret(root.children[2], env) # floor=-1


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
        mch = interpret(root, env) # init VARIABLES and eval INVARIANT
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
        mch = interpret(root, env)
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        atype = env.get_type("BOOK")
        assert isinstance(atype, PowerSetType)
        assert isinstance(atype.data, SetType)
        empty = env.get_value("read")
        assert empty==frozenset([])
        #BOOKS = env.get_value("BOOK")
        op_and_state_list = calc_succ_states(env, mch)
        env = exec_op(env, op_and_state_list, 0)
        read = env.get_value("read")
        assert len(read)==1
        op_and_state_list = calc_succ_states(env, mch)
        env = exec_op(env, op_and_state_list, 0)
        read = env.get_value("read")
        assert len(read)==2
        op_and_state_list = calc_succ_states(env, mch)
        env = exec_op(env, op_and_state_list, 0)
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
        mch = interpret(root, env)
        assert isinstance(root.children[3], AInvariantMachineClause)
        assert interpret(root.children[3], env)


    def test_schneider_inclusion(self):
        # side effect: loades examples/Doors.mch
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
        mch = interpret(root, env)
        assert isinstance(root.children[5], AInvariantMachineClause)
        assert interpret(root.children[5], env)
        op_and_state_list = calc_succ_states(env, mch)
        env = exec_op(env, op_and_state_list, 0)
        op_and_state_list = calc_succ_states(env, mch) #opening enabled
        env = exec_op(env, op_and_state_list, 0)
        names = [op[0].opName for op in op_and_state_list]
        assert  "closedoor" in names
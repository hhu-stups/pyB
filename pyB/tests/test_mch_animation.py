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
        mch = interpret(root, env)
        assert isinstance(root.children[3], AInvariantMachineClause)
        assert interpret(root.children[3], env)
        empty = env.get_value("keys")
        assert empty==frozenset([])
        op_and_state_list = calc_succ_states(env, mch)
        env = exec_op(env, op_and_state_list, 0)
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
        mch = interpret(root, env)
        assert isinstance(root.children[5], AInvariantMachineClause)
        assert interpret(root.children[5], env)
        op_and_state_list = calc_succ_states(env, mch)
        env = exec_op(env, op_and_state_list, 0)
        op_and_state_list = calc_succ_states(env, mch) #opening enabled
        env = exec_op(env, op_and_state_list, 0)
        # test PROMOTES:
        names = [op[0].opName for op in op_and_state_list]
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
        mch = interpret(root, env)
        assert isinstance(root.children[5], AInvariantMachineClause)
        assert interpret(root.children[5], env)
        op_and_state_list = calc_succ_states(env, mch) #opening enabled
        
        # test PROMOTES:
        names = [op[0].opName for op in op_and_state_list]
        assert frozenset(names)==frozenset(['insert', 'lockdoor', 'extract', 'closedoor', 'quicklock'])
        empty = env.get_value("keys")
        assert empty==frozenset([])
        env = exec_op(env, op_and_state_list, 0) # insert
        one = env.get_value("keys")
        assert len(one)==1
        op_and_state_list = calc_succ_states(env, mch) 
        names = [op[0].opName for op in op_and_state_list]
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
        mch = interpret(root, env)      
        assert not env.get_value("GOODS")==None
        op_and_state_list = calc_succ_states(env, mch) 
        names = [op[0].opName for op in op_and_state_list]
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
        mch = interpret(root, env)      
        assert not env.get_value("GOODS")==None
        assert not env.get_value("price")==None
        assert env.get_value("takings")==0
        op_and_state_list = calc_succ_states(env, mch) 
        names = [op[0].opName for op in op_and_state_list]
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
        mch = interpret(root, env)
        value = env.get_value("marriage") 
        assert value==frozenset([])
        op_and_state_list = calc_succ_states(env, mch) 
        names = [op[0].opName for op in op_and_state_list]
        assert frozenset(names)==frozenset(['born'])
        env = exec_op(env, op_and_state_list, 0) # born
        op_and_state_list = calc_succ_states(env, mch) 
        names = [op[0].opName for op in op_and_state_list]
        assert frozenset(names)==frozenset(['born', 'die'])
# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from environment import Environment
from interp import interpret
from helpers import file_to_AST_str, string_to_file
from animation_clui import show_ui
from animation import calc_possible_operations, exec_op
from definition_handler import DefinitionHandler
from parsing import parse_ast
from typing import type_check_bmch

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
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        for i in range(4):
            op_and_state_list = calc_possible_operations(env, mch)
            exec_op(env, op_and_state_list[1], mch)
            assert interpret(root.children[2], env)
        op_and_state_list = calc_possible_operations(env, mch)
        exec_op(env, op_and_state_list[1], mch)
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
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        interpret(root, env) # init VARIABLES and eval INVARIANT
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
        interpret(root, env)
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        atype = env.get_type("BOOK")
        assert isinstance(atype, PowerSetType)
        assert isinstance(atype.data, SetType)
        empty = env.get_value("read")
        assert empty==frozenset([])
        #BOOKS = env.get_value("BOOK")
        op_and_state_list = calc_possible_operations(env, mch)
        exec_op(env, op_and_state_list[0], mch)
        read = env.get_value("read")
        assert len(read)==1
        op_and_state_list = calc_possible_operations(env, mch)
        exec_op(env, op_and_state_list[0], mch)
        read = env.get_value("read")
        assert len(read)==2
        op_and_state_list = calc_possible_operations(env, mch)
        exec_op(env, op_and_state_list[0], mch)
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
        interpret(root, env)
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
        interpret(root, env)
        assert isinstance(root.children[3], AInvariantMachineClause)
        assert interpret(root.children[3], env)
        empty = env.get_value("keys")
        assert empty==frozenset([])
        op_and_state_list = calc_possible_operations(env, mch)
        exec_op(env, op_and_state_list[0], mch)
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
        interpret(root, env)
        assert isinstance(root.children[5], AInvariantMachineClause)
        assert interpret(root.children[5], env)
        op_and_state_list = calc_possible_operations(env, mch)
        exec_op(env, op_and_state_list[0], mch)
        op_and_state_list = calc_possible_operations(env, mch) #opening enabled
        exec_op(env, op_and_state_list[0], mch)
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
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        interpret(root, env)
        assert isinstance(root.children[5], AInvariantMachineClause)
        assert interpret(root.children[5], env)
        op_and_state_list = calc_possible_operations(env, mch) #opening enabled
        
        # test PROMOTES:
        names = [op[0].opName for op in op_and_state_list]
        assert frozenset(names)==frozenset(['insert', 'lockdoor', 'extract', 'closedoor', 'quicklock'])
        empty = env.get_value("keys")
        assert empty==frozenset([])
        exec_op(env, op_and_state_list[0], mch) # insert
        one = env.get_value("keys")
        assert len(one)==1
        op_and_state_list = calc_possible_operations(env, mch) 
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
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        interpret(root, env)      
        assert not env.get_value("GOODS")==None
        op_and_state_list = calc_possible_operations(env, mch) 
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
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        interpret(root, env)      
        assert not env.get_value("GOODS")==None
        assert not env.get_value("price")==None
        assert env.get_value("takings")==0
        op_and_state_list = calc_possible_operations(env, mch) 
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
        mch = parse_ast(root, env)
        type_check_bmch(root, mch) # also checks all included, seen, used and extend
        interpret(root, env)
        value = env.get_value("marriage") 
        assert value==frozenset([])
        op_and_state_list = calc_possible_operations(env, mch) 
        names = [op[0].opName for op in op_and_state_list]
        assert frozenset(names)==frozenset(['born'])
        exec_op(env, op_and_state_list[0], mch) # born
        op_and_state_list = calc_possible_operations(env, mch) 
        names = [op[0].opName for op in op_and_state_list]
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
        interpret(root, env)
        value = env.get_value("read") 
        assert value==frozenset([])
        op_and_state_list = calc_possible_operations(env, mch) 
        names = [op[0].opName for op in op_and_state_list]
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
        interpret(root, env)
        op_and_state_list = calc_possible_operations(env, mch) 
        names = [op[0].opName for op in op_and_state_list]
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
        interpret(root, env)
        assert isinstance(root.children[6], AInvariantMachineClause)
        assert interpret(root.children[6], env)
        near = env.get_value("near") 
        far = env.get_value("far") 
        assert near==frozenset(["farmer","fox","chicken","grain"]) 
        assert far==frozenset([])
        op_and_state_list = calc_possible_operations(env, mch) 
        names = [op[0].opName for op in op_and_state_list]
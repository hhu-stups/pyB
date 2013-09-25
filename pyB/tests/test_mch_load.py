# -*- coding: utf-8 -*-
from ast_nodes import *
from environment import Environment
from interp import interpret, set_up_constants
from helpers import file_to_AST_str, string_to_file
from parsing import parse_ast
from typing import type_check_bmch

file_name = "input.txt"

class TestMCHLaod():
    def test_examples_simple_acounter(self):
        string = '''
        MACHINE ACounter

        ABSTRACT_VARIABLES  ii,jj

        INVARIANT  ii:0..10 & jj:0..10 & ii<11 & jj>=0

        INITIALISATION ii,jj := 2,10

        END'''

        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)


    def test_examples_query_op(self):
        string = '''
        MACHINE Query

        VARIABLES xx

        INVARIANT  xx:NAT

        INITIALISATION xx:=1
        
        OPERATIONS
        
        rr <-- query = rr:=xx

        END'''

        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        # TODO query check
        

    def test_examples_no_query_op(self):
        string = '''
        MACHINE Query

        VARIABLES xx

        INVARIANT  xx:NAT

        INITIALISATION xx:=1
        
        OPERATIONS
        
        no_query = xx:=2

        END'''

        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        # TODO query check


    def test_examples_simple_bakery0(self):
        string ='''
        MACHINE Bakery0

        ABSTRACT_VARIABLES  aa

        INVARIANT  aa:0..2

        INITIALISATION aa:=0

        END'''

        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)


    def test_examples_simple_bakery1(self):
        string ='''
        MACHINE Bakery1

        ABSTRACT_VARIABLES  p1, p2, y1, y2

        INVARIANT  
                p1:0..2 & p2:0..2 & y1:NATURAL & y2:NATURAL &
                (p1=2 => p2<2) &
                (p2=2 => p1<2) 

        INITIALISATION  p1,p2,y1,y2 := 0,0,0,0

        END'''

        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)


    def test_examples_simple_gcd(self):
        string = '''
        MACHINE GCD
        VARIABLES x,y
        INVARIANT
        x:NAT & y:NAT
        INITIALISATION x:=3 || y:=4
        END'''

        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)


    def test_examples_simple_lift(self):
        string = '''
        MACHINE Lift

        ABSTRACT_VARIABLES  floor

        INVARIANT  floor : 0..99 /* NAT */

        INITIALISATION floor := 4
        END'''

        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)


    def test_examples_simple_testset(self):
        string = '''
        MACHINE TestSet
        SETS
        ID={aa, bb, cc}

        CONSTANTS iv
        PROPERTIES
        iv:ID
        VARIABLES xx
        INVARIANT
        xx:ID
        INITIALISATION xx:=iv
        END'''

        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[5], AInvariantMachineClause)
        assert interpret(root.children[5], env)


    def test_examples_schneider_club(self):
        string = '''
        MACHINE           Club(capacity)

        CONSTRAINTS       capacity : NAT1 & capacity <= 2

        SETS              NAME={billy, bobby}

        CONSTANTS         total

        PROPERTIES        total : NAT1 & total > 2

        VARIABLES         member, waiting

        INVARIANT         member <: NAME & waiting <: NAME 
                        & member /\ waiting = {}
                        & card(member) <= 4096
                        & card(waiting) <= total

        INITIALISATION    member := {} || waiting := {}

        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string


        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[6], AInvariantMachineClause)
        assert interpret(root.children[6], env)
        assert isinstance(root.children[1], AConstraintsMachineClause)
        assert interpret(root.children[1], env)



    def test_examples_knights_knaves(self):
        string ='''
        MACHINE KnightsKnaves
        /* Puzzle from Smullyan:
        Knights: always tell the truth
        Knaves: always lie

        1: A says: “B is a knave or C is a knave”
        2: B says “A is a knight”

        What are A & B & C?
        */
        CONSTANTS A,B,C
        PROPERTIES
        A:BOOL & B:BOOL & C:BOOL /* TRUE if they are a Knight */
        &
        (A=TRUE <=> (B=FALSE or C=FALSE)) &
        (B=TRUE <=> A=TRUE)
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        interpret(root, env)# search for CONSTANTS which make PROPERTIES True
        assert env.get_value("A") == True
        assert env.get_value("B") == True
        assert env.get_value("C") == False


    def test_structs(self):
        string = '''
        MACHINE Test
        VARIABLES RES_SET
        INVARIANT RES_SET:POW(struct(Mark:NAT, Good_enough:BOOL))
        INITIALISATION RES_SET := struct(Mark : 0..5, Good_enough : BOOL) 
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        interpret(root, env)# search for CONSTANTS which make PROPERTIES True


    def test_structs2(self):
        string = '''
        MACHINE Test
        VARIABLES RES
        INVARIANT RES:struct(Mark:NAT, Good_enough:BOOL)
        INITIALISATION RES := rec(Mark : 14, Good_enough : TRUE) 
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        interpret(root, env)# search for CONSTANTS which make PROPERTIES True


    def test_structs3(self):
        string = '''
        MACHINE Test
        VARIABLES RES, xx
        INVARIANT RES:struct(Mark:NAT, Good_enough:BOOL) & xx:NAT
        INITIALISATION RES := rec(Mark:4, Good_enough:TRUE); xx:=RES'Mark
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        interpret(root, env)# search for CONSTANTS which make PROPERTIES True
        assert env.get_value("xx") == 4


    def test_string_set(self):
        string = '''
        MACHINE Test
        VARIABLES s
        INVARIANT s:STRING
        INITIALISATION s:="Hallo Welt"
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        interpret(root, env)# search for CONSTANTS which make PROPERTIES True
        assert env.get_value("s") == "Hallo Welt"
        
        
    def test_CartesianProductOverride(self):
        string = '''
        MACHINE CartesianProductOverride
        SETS
         S;T
        CONSTANTS a,b,c
        PROPERTIES
         /* Rule Hypotheses */
         a :  S <-> T &
         dom(a) = b &
         c <: T & 
        
         /* Rule Conclusion */
         not( a <+ b * c = b * c )
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
        interpret(root, env) # eval CONSTANTS and PROPERTIES
        assert isinstance(root.children[3], APropertiesMachineClause)
        assert interpret(root.children[3], env)
   
     
    def test_set_up_constants_nondeterministic(self):        
        string = '''
        MACHINE         Param(num)
        CONSTRAINTS     num:NAT & num <4
        VARIABLES       xx
        INVARIANT       xx:NAT
        INITIALISATION  xx:=num
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        bstates = set_up_constants(root, env, mch)
        #assert len(bstates)==4
        for bstate in bstates:
            env.state_space.add_state(bstate)
            num = bstate.get_value("num", mch)
            assert num in [0,1,2,3]
            env.state_space.undo()
         
            
    def test_set_up_constants_nondeterministic(self):        
        string = '''
        MACHINE         Param(num)
        CONSTRAINTS     num:NAT & num <4
        VARIABLES       xx
        INVARIANT       xx:NAT
        INITIALISATION  xx:=num
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        bstates = set_up_constants(root, env, mch)
        assert len(bstates)==4
        for bstate in bstates:
            env.state_space.add_state(bstate)
            num = bstate.get_value("num", mch)
            assert num in [0,1,2,3]
            env.state_space.undo()


    def test_set_up_constants_nondeterministic2(self):        
        string = '''
        MACHINE         Param2
        PROPERTIES      num:NAT & num <4
        CONSTANTS       num
        VARIABLES       xx
        INVARIANT       xx:NAT
        INITIALISATION  xx:=num
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string
        
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        bstates = set_up_constants(root, env, mch)
        assert len(bstates)==4
        for bstate in bstates:
            env.state_space.add_state(bstate)
            num = bstate.get_value("num", mch)
            assert num in [0,1,2,3]
            env.state_space.undo()       
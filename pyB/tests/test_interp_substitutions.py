# -*- coding: utf-8 -*-
# also typchecking-tests
from ast_nodes import *
from btypes import *
from interp import Environment
from typing import _test_typeit
from interp import interpret, Environment
from helpers import file_to_AST_str, string_to_file

file_name = "input.txt"

class TestInterpSubstitutions():
    def test_genAST_sub_simple_asgn(self):
        # Build AST
        string = '''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx:=3
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")==3
        assert isinstance(env.get_type("xx"), IntegerType)



    def test_genAST_sub_parallel_asgn(self):
        # Build AST
        string = '''
        MACHINE Test
        VARIABLES xx, yy
        INVARIANT xx:NAT & yy:NAT
        INITIALISATION xx:=1 || yy:= 2
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")==1
        assert env.get_value("yy")==2
        assert isinstance(env.get_type("xx"), IntegerType)
        assert isinstance(env.get_type("yy"), IntegerType)


    def test_genAST_sub_multiple_asgn(self):
        # Build AST
        string = '''
        MACHINE Test
        VARIABLES xx, yy
        INVARIANT xx:NAT & yy:NAT
        INITIALISATION xx,yy:=1,2
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")==1
        assert env.get_value("yy")==2
        assert isinstance(env.get_type("xx"), IntegerType)
        assert isinstance(env.get_type("yy"), IntegerType)


    def test_genAST_sub_bool(self):
        # Build AST
        string = '''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:BOOL
        INITIALISATION xx := bool(1<2)
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")==True
        assert isinstance(env.get_type("xx"), BoolType)


    def test_genAST_sub_choice_by(self):
        # Build AST
        string = '''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx : (xx>0 & xx<4)
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")>0
        assert env.get_value("xx")<4
        assert isinstance(env.get_type("xx"), IntegerType)


    def test_genAST_sub_choice_by2(self):
        # Build AST
        string = '''
        MACHINE Test4
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx::{1,2,3,4,5}
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")>0
        assert env.get_value("xx")<6
        assert isinstance(env.get_type("xx"), IntegerType)



    def test_genAST_sub_choice_by3(self):
        # Build AST
        string = '''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx:=3 ; xx: (xx+xx>=5)
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")>=3
        assert isinstance(env.get_type("xx"), IntegerType)


    def test_genAST_sub_choice_by_primed(self):
        # Build AST
        string = '''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx:=3 ; xx: (xx+xx$0>=5)
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")>=2
        assert isinstance(env.get_type("xx"), IntegerType)


    def test_genAST_sub_func_overw(self):
        # Build AST
        string = '''
        MACHINE Test
        VARIABLES f
        INVARIANT f:POW({1,2,3}*{1,2,3})
        INITIALISATION f:={(1,2),(3,4)} ; f(3) := 1+2
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("f")==frozenset([(1,2),(3,3)])


    def test_genAST_sub_func_overw_many_args(self):
        # Build AST
        string = '''
        MACHINE Test
        VARIABLES f
        INVARIANT f:POW(({1,2}*{1,2})*{1,2})
        INITIALISATION f:={((1,1),2),((2,2),4)} ; f(2,2) := 0+1
        END
        '''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("f")==frozenset([((1,1),2),((2,2),1)])


    def test_genAST_sub_block(self):
        # Build AST
        string = '''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT 
        INITIALISATION BEGIN xx:= 1; xx:=2 END
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")==2


    def test_genAST_sub_if(self):
        # Build AST
        string = '''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT 
        INITIALISATION BEGIN xx:= 1; 
                IF 1+1=3 THEN xx:=3 
                ELSIF 1+1=2 THEN xx:=2 
                ELSIF 1+1=0 THEN xx:=0 END 
                END
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")==2


    def test_genAST_sub_if2(self):
        # Build AST
        string = '''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT 
        INITIALISATION BEGIN xx:= 1; 
                IF 1+1=3 THEN xx:=3 
                ELSIF 1+1=2 THEN xx:=2 
                ELSE xx:=0 END 
                END
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")==2


    def test_genAST_sub_if3(self):
        # Build AST
        string = '''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT 
        INITIALISATION BEGIN xx:= 1; 
                IF 1+1=3 THEN xx:=3 
                ELSIF 1+1=4 THEN xx:=2 
                ELSE xx:=0 END 
                END
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")==0


    def test_genAST_sub_if3(self):
        # Build AST
        string = '''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT 
        INITIALISATION BEGIN xx:= 1; 
                IF 1+1=3 THEN xx:=3 
                ELSE xx:=0 END 
                END
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")==0


    def test_genAST_sub_if4(self):
        # Build AST
        string = '''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT 
        INITIALISATION BEGIN xx:= 1; 
                IF 1+1=3 THEN xx:=3 END 
                END
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")==1


    def test_genAST_sub_pre(self):
        # Build AST
        string = '''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT 
        INITIALISATION BEGIN xx:=1; PRE 1+1=2 THEN xx:=2 END END
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")==2


    def test_genAST_sub_pre2(self):
        # Build AST
        string = '''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT 
        INITIALISATION BEGIN xx:=1; PRE 1+1=3 THEN xx:=2 END END
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")==1


    def test_genAST_sub_choice(self):
        # Build AST
        string = '''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT 
        INITIALISATION BEGIN xx:=1; CHOICE xx:=2 OR xx:=3 END END
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")==2 or env.get_value("xx")==3


    def test_genAST_sub_choice2(self):
        # Build AST
        string = '''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT 
        INITIALISATION BEGIN xx:=1; CHOICE xx:=2 END END
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")==2


    def test_genAST_sub_choice3(self):
        # Build AST
        string = '''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT 
        INITIALISATION BEGIN xx:=1; CHOICE xx:=2 OR xx:=3 OR xx:=4 END END
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")==2 or env.get_value("xx")==3 or env.get_value("xx")==4


    def test_genAST_sub_select(self):
        # Build AST
        string = '''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT 
        INITIALISATION BEGIN xx:=1; 
            SELECT 1+1=2 THEN xx:=2 
            WHEN 1+1=3 THEN xx:=3
            ELSE xx:=4 END END
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")==2


    def test_genAST_sub_select2(self):
        # Build AST
        string = '''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT 
        INITIALISATION BEGIN xx:=1; 
            SELECT 1+1=0 THEN xx:=2 
            WHEN 1+1=3 THEN xx:=3
            ELSE xx:=4 END END
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")==4



    def test_genAST_sub_select3(self):
        # Build AST
        string = '''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT 
        INITIALISATION BEGIN xx:=1; 
            SELECT 1+1=3 THEN xx:=2 
            WHEN 1+1=2 THEN xx:=3
            ELSE xx:=4 END END
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")==3


    def test_genAST_sub_case(self):
        # Build AST
        string = '''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT 
        INITIALISATION 
            BEGIN xx:=1; 
                CASE 1+1 OF 
                EITHER 1,2,3 THEN xx:=2 
                OR 4,5,6 THEN xx:=3 END 
                END
            END
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")==2


    def test_genAST_sub_case2(self):
        # Build AST
        string = '''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT 
        INITIALISATION 
            BEGIN xx:=1; 
                CASE 1+1 OF 
                EITHER 4,5,6 THEN xx:=2 
                OR 1,2,3 THEN xx:=3 END 
                END
            END
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")==3


    def test_genAST_sub_case3(self):
        # Build AST
        string = '''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT 
        INITIALISATION 
            BEGIN xx:=1; 
                CASE 1+1 OF 
                EITHER 4,5,6 THEN xx:=2 
                OR 7,8,9 THEN xx:=3
                ELSE xx:=4 END 
                END
            END
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")==4


    def test_genAST_sub_var(self):
        # Build AST
        string = '''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT 
        INITIALISATION BEGIN xx:=1; 
                        VAR varLoc1, varLoc2 IN
                        varLoc1 := xx + 1 ;
                        varLoc2 := 2 * varLoc1 ;
                        xx := varLoc2
                        END
                    END
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")==4


    def test_genAST_sub_any(self):
        string = '''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT 
        INITIALISATION BEGIN xx:=1;
                        ANY r1, r2 WHERE
                        r1 : NAT &
                        r2 : NAT &
                        r1*r1 + r2*r2 = 25
                        THEN
                        xx := r1 + r2
                        END
                    END
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")==5 or env.get_value("xx")==7 # 3+4 or 5+0



    def test_genAST_sub_let(self):
        string = '''
        MACHINE Test
        VARIABLES SumR, DifferenceR, Var1, Var2
        INVARIANT SumR:NAT & DifferenceR:NAT & Var1:NAT & Var2:NAT
        INITIALISATION BEGIN Var1:=2; Var2:=3;
                        LET r1, r2 BE
                        r1 = (Var1 + Var2) / 2 &
                        r2 = (Var1 - Var2) / 2
                        IN
                        SumR := r1 + r2 ||
                        DifferenceR := r1 - r2
                        END

                    END
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("SumR")==1
        assert env.get_value("DifferenceR")==3
        assert env.get_value("Var1")==2
        assert env.get_value("Var2")==3


    def test_genAST_sub_skip(self):
        string = '''
        MACHINE Test
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx:=3; BEGIN skip END
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")==3

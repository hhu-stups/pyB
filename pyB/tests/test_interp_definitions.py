# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from environment import Environment
from typing import _test_typeit
from interp import interpret
from helpers import file_to_AST_str, string_to_file
from parsing import parse_ast
from definition_handler import DefinitionHandler

file_name = "input.txt"

class TestInterpDefinitions():
    def test_genAST_int_def(self):
        # Build AST
        string = '''
        MACHINE Test
        DEFINITIONS MyType == NAT
        VARIABLES z
        INVARIANT z:MyType
        INITIALISATION z:=4
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        dh = DefinitionHandler()
        dh.repl_defs(root)
        env = Environment()
        parse_ast(root, env)
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[3], AInvariantMachineClause)
        assert interpret(root.children[3], env)



    def test_genAST_expr_def(self):
        # Build AST
        string ='''
        MACHINE Test
        DEFINITIONS Expr == 2+2
        VARIABLES z
        INVARIANT z:NAT
        INITIALISATION z:= Expr
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        dh = DefinitionHandler()
        dh.repl_defs(root)
        env = Environment()
        parse_ast(root, env)
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[3], AInvariantMachineClause)
        assert interpret(root.children[3], env)
        assert env.get_value("z")==4


    def test_genAST_para_def(self):
        # Build AST
        string ='''
        MACHINE Test
        VARIABLES z
        INVARIANT z:MyType 
        INITIALISATION z:= Expr(2)
        DEFINITIONS
        Expr(X) == 1+X;
        MyType == NAT;
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        dh = DefinitionHandler()
        dh.repl_defs(root)
        env = Environment()
        parse_ast(root, env)
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert env.get_value("z")==3


    def test_genAST_para_def2(self):
        # Build AST
        string='''
        MACHINE Test
        VARIABLES z
        INVARIANT z:MyDef(NAT)
        INITIALISATION z:= MyDef(2)
        DEFINITIONS MyDef(X) == X;
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        #Test
        dh = DefinitionHandler()
        dh.repl_defs(root)
        env = Environment()
        parse_ast(root, env)
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert env.get_value("z")==2


    def test_genAST_two_para_def(self):
        # Build AST
        string='''
        MACHINE Test
        VARIABLES z
        INVARIANT z:MyDef(NAT,{0})
        INITIALISATION z:= MyDef(5,1)
        DEFINITIONS MyDef(X,Y) == X-Y;
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        #Test
        dh = DefinitionHandler()
        dh.repl_defs(root)
        env = Environment()
        parse_ast(root, env)
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert env.get_value("z")==4


    def test_genAST_pred_def(self):
        string='''
        MACHINE Test
        VARIABLES z
        INVARIANT z:NAT & MyDef(4,1,3)
        INITIALISATION z:= 4
        DEFINITIONS MyDef(X,Y,Z) == X-Y=Z;
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        #Test
        dh = DefinitionHandler()
        dh.repl_defs(root)
        env = Environment()
        parse_ast(root, env)
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)


    def test_genAST_subst_def(self):
        string='''
        MACHINE Test
        VARIABLES z, b
        INVARIANT z:NAT & b:BOOL
        INITIALISATION Assign(z, 1+1) || Assign(b, TRUE)
        DEFINITIONS Assign(VarName,Expr) == VarName := Expr;
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        #Test
        dh = DefinitionHandler()
        dh.repl_defs(root)
        env = Environment()
        parse_ast(root, env)
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert env.get_value("z")==2
        assert env.get_value("b")==True


    def test_genAST_subst_def2(self):
        string='''
        MACHINE Test
        VARIABLES z, b, x
        INVARIANT x:NAT & z:NAT & b:BOOL
        INITIALISATION x:=2 ; Assign(x+1, z) ; Assign(TRUE, b)
        DEFINITIONS Assign(Expr, VarName) == VarName := Expr;
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        #Test
        dh = DefinitionHandler()
        dh.repl_defs(root)
        env = Environment()
        parse_ast(root, env)
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[2], AInvariantMachineClause)
        assert interpret(root.children[2], env)
        assert env.get_value("z")==3
        assert env.get_value("b")==True
        assert env.get_value("x")==2
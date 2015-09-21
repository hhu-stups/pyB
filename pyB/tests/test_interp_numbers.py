# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from environment import Environment
from interp import interpret
from util import type_with_known_types
from helpers import file_to_AST_str, string_to_file
from parsing import str_ast_to_python_ast

from config import USE_RPYTHON_CODE
if USE_RPYTHON_CODE:
     from rpython_b_objmodel import frozenset

file_name = "input.txt"

class TestInterpNumbers():

    def test_genAST_preidacte_less(self):
        # Build AST
        string_to_file("#PREDICATE 1<2", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)
        
    def test_genAST_expr_add(self):
        # Build AST
        string_to_file("#PREDICATE 1+1=3", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert not interpret(root, env)


    def test_genAST_expr_add2(self):
        # Build AST
        string_to_file("#PREDICATE 1+1=2", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)


    def test_genAST_expr_sub(self):
        # Build AST
        string_to_file("#PREDICATE 4-3=1", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)



    def test_genAST_expr_sub2(self):
        # Build AST
        string_to_file("#PREDICATE 4--3=1", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert not interpret(root, env)



    def test_genAST_expr_mul(self):
        # Build AST
        string_to_file("#PREDICATE 4*0=0", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)


    def test_genAST_expr_div1(self):
        # Build AST
        string_to_file("#PREDICATE 8/2=4", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)

    """
    def test_genAST_expr_div2(self):
        # Build AST
        string_to_file("#PREDICATE -1/4=0", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)
    """

    def test_genAST_expr_mod(self):
        # Build AST
        string_to_file("#PREDICATE 8 mod 3=2", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)


    def test_genAST_expr_exp(self):
        # Build AST
        string_to_file("#PREDICATE 2 ** 4 = 16", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)


    def test_genAST_expr_neq(self):
        # Build AST
        string_to_file("#PREDICATE 0 /= 1", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)


    def test_genAST_and(self):
        # Build AST
        string_to_file("#PREDICATE 1+1=2 & 7<8", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)


    def test_genAST_or(self):
        # Build AST
        string_to_file("#PREDICATE 4*0=0 or 4*0=4", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)


    def test_genAST_impl(self):
        # Build AST
        string_to_file("#PREDICATE 4>3 => 4>2", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)


    def test_genAST_equi(self):
        # Build AST
        string_to_file("#PREDICATE (1+1=2) <=> (2+2=4)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)


    def test_genAST_complex_arith(self):
        # Build AST
        string_to_file("#PREDICATE 6 = (2+2)*4+(10-0)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert not interpret(root, env)


    def test_genAST_complex_arith2(self):
        # Build AST
        string_to_file("#PREDICATE 26 = (2+2)*4+(10-0)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root, env)


    def test_genAST_pred_gt(self):
        # Build AST:
        string_to_file("#PREDICATE 6>x", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env.add_ids_to_frame(["x"])
        env.set_value("x", 1)
        assert interpret(root, env)

        env.set_value("x", 10)
        assert not interpret(root, env)

        env.set_value("x", 6)
        assert not interpret(root, env)


    def test_genAST_pred_ge(self):
        # Build AST:
        string_to_file("#PREDICATE 6>=x", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env.add_ids_to_frame(["x"])
        env.set_value("x", 1)
        assert interpret(root, env)

        env.set_value("x", 6)
        assert interpret(root, env)

        env.set_value("x", 7)
        assert not interpret(root, env)


    def test_genAST_pred_le(self):
        # Build AST:
        string_to_file("#PREDICATE 6<=x", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env.add_ids_to_frame(["x"])
        env.set_value("x", 1)
        assert not interpret(root, env)

        env.set_value("x", 6)
        assert interpret(root, env)

        env.set_value("x", 7)
        assert interpret(root, env)


    def test_genAST_min(self):
        # Build AST:
        string_to_file("#PREDICATE S={1,2,3,4,5} & min(S)=1", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env.add_ids_to_frame(["S"])
        type_with_known_types(root.children[0], env, [], ["S"])
        env.set_value("S", frozenset([1,2,3,4,5]))
        assert interpret(root, env)


    def test_genAST_max(self):
        # Build AST:
        string_to_file("#PREDICATE S={1,2,3,4,5} & max(S)=5", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env.add_ids_to_frame(["S"])
        type_with_known_types(root.children[0], env, [], ["S"])
        env.set_value("S", frozenset([1,2,3,4,5]))
        assert interpret(root, env)


    def test_genAST_pred_exist(self):
        # Build AST:
        string_to_file("#PREDICATE #(z).( z<4 & z>0)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        type_with_known_types(root.children[0], env, [], [])
        assert interpret(root.children[0],env)


    def test_genAST_pred_exist2(self):
        # Build AST:
        string_to_file("#PREDICATE #(x,y).( x<0 & y>0 & x>y)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        type_with_known_types(root.children[0], env, [], [])
        assert not interpret(root.children[0],env)


    def test_genAST_pred_exist3(self):
        # Build AST:
        string_to_file("#PREDICATE #(x,y).( x<0 & y>0 & y>x)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        type_with_known_types(root.children[0], env, [], [])
        assert interpret(root.children[0],env)


    def test_genAST_pred_exist_subset_nat(self):
        # Build AST:
        string_to_file("#PREDICATE  #(x).(x:S & x>4999) & S={5000}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env.add_ids_to_frame(["S"])
        env.set_value("S", frozenset([5000]))
        env._max_int = 2**16
        type_with_known_types(root.children[0], env, [], ["S"])
        assert interpret(root.children[0],env)
 
        
    def test_genAST_pred_forall(self):
        # Build AST:
        string_to_file("#PREDICATE !(z).( z<4 => z<5)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        type_with_known_types(root.children[0], env, [], [])
        assert interpret(root.children[0],env)


    def test_genAST_pred_forall2(self):
        # Build AST:
        string_to_file("#PREDICATE !(x,y,z).( x>0 & y>0 & z<4 => x+y=z)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        type_with_known_types(root.children[0], env, [], [])
        assert not interpret(root.children[0],env)


    def test_genAST_pred_sigma(self):
        # Build AST:
        string_to_file("#PREDICATE (SIGMA zz . (zz:1..5 | zz*zz))=55", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        type_with_known_types(root.children[0], env, [], [])
        assert interpret(root.children[0],env)


    def test_genAST_pred_pi(self):
        # Build AST:
        string_to_file("#PREDICATE (PI zz . (zz:1..5 | zz))=120", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        type_with_known_types(root.children[0], env, [], [])
        assert interpret(root.children[0],env)


    def test_genAST_pred_sigma2(self):
        # Build AST:
        string_to_file("#PREDICATE 4=(SIGMA zz . (zz:POW(ID) | card(zz)))", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env.add_ids_to_frame(["ID"])
        lst = [("ID", PowerSetType(SetType("ID")))]
        env.set_value("ID", frozenset(["a","b"]))
        type_with_known_types(root.children[0], env, lst, "")
        assert interpret(root.children[0],env)


    def test_genAST_pred_maxint(self):
        # Build AST
        string_to_file("#PREDICATE x<MAXINT", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env.add_ids_to_frame(["x"])
        env.set_value("x", 2)
        type_with_known_types(root.children[0], env, [], "x")
        assert interpret(root.children[0],env)


    def test_genAST_pred_minint(self):
        # Build AST
        string_to_file("#PREDICATE x>MININT", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env.add_ids_to_frame(["x"])
        env.set_value("x", 2)
        type_with_known_types(root.children[0], env, [], "x")
        assert interpret(root.children[0],env)


    def test_genAST_expr_succ(self):
        # Build AST
        string_to_file("#PREDICATE 2=succ(1)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        assert interpret(root.children[0],env)


    def test_genAST_expr_pred(self):
        # Build AST
        string_to_file("#PREDICATE 2=pred(3)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        assert interpret(root.children[0],env)


    def test_genAST_expr_natural(self):
        # Build AST
        string_to_file("#PREDICATE 1000:NATURAL", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        assert interpret(root.children[0],env)


    def test_genAST_expr_natural2(self):
        # Build AST
        string_to_file("#PREDICATE 1000:NATURAL1", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        assert interpret(root.children[0],env)


    def test_genAST_expr_natural3(self):
        # Build AST
        string_to_file("#PREDICATE 0:NATURAL1", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        assert  not interpret(root.children[0],env)


    def test_genAST_expr_integer(self):
        # Build AST
        string_to_file("#PREDICATE -54321:INTEGER", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        assert interpret(root.children[0],env)


    def test_genAST_expr_int(self):
        # Build AST
        string_to_file("#PREDICATE -1:INT", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        assert interpret(root.children[0],env)
        
        
        
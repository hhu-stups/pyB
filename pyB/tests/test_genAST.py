# -*- coding: utf-8 -*-
from ast_nodes import *
from interp import inperpret, Environment
from helpers import file_to_AST_str


file_name = "input.txt"

class TestGenAST():
    def string_to_file(self, string):
        f = open(file_name,"w")
        f.write(string)
        f.close
        return f


    def test_genAST_expr_add(self):
        # Build AST
        self.string_to_file("#PREDICATE 1+1=3")
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert not inperpret(root, env)


    def test_genAST_expr_add2(self):
        # Build AST
        self.string_to_file("#PREDICATE 1+1=2")
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert inperpret(root, env)


    def test_genAST_expr_sub(self):
        # Build AST
        self.string_to_file("#PREDICATE 4-3=1")
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert inperpret(root, env)

    def test_genAST_expr_mul(self):
        # Build AST
        self.string_to_file("#PREDICATE 4*0=0")
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert inperpret(root, env)


    def test_genAST_expr_div(self):
        # Build AST
        self.string_to_file("#PREDICATE 8/2=4")
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert inperpret(root, env)


    def test_genAST_expr_mod(self):
        # Build AST
        self.string_to_file("#PREDICATE 8 mod 3=2")
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert inperpret(root, env)


    def test_genAST_expr_neq(self):
        # Build AST
        self.string_to_file("#PREDICATE 0 /= 1")
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert inperpret(root, env)


    def test_genAST_pred_gt(self):
        # Build AST:
        self.string_to_file("#PREDICATE 6>x")
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.variable_values["x"] = 1
        assert inperpret(root, env)

        env.variable_values["x"] = 10
        assert not inperpret(root, env)

        env.variable_values["x"] = 6
        assert not inperpret(root, env)
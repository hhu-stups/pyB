# -*- coding: utf-8 -*-
from ast_nodes import *
from interp import inperpret, Environment
from helpers import file_to_AST_str, string_to_file

file_name = "input.txt"

class TestInterpSets():
    def test_genAST_member(self):
        # Build AST
        string_to_file("#PREDICATE x:S", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.variable_values["x"] = "x"
        env.variable_values["S"] = set(["x","y","z"])
        assert inperpret(root, env)

        env.variable_values["S"] = set(["a","b","c"])
        assert not inperpret(root, env)

    def test_genAST_subset(self):
        # Build AST
        string_to_file("#PREDICATE S<:T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.variable_values["T"] = set(["x","y"])
        env.variable_values["S"] = set(["x","y","z"])
        assert not inperpret(root, env)

        env.variable_values["S"] = set(["a","b","c"])
        env.variable_values["T"] = set(["a","b","c"])
        assert inperpret(root, env)





    def test_genAST_pred_set_cart(self):
        # Build AST:
        string_to_file("#PREDICATE u:S*T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["T"] = set(["x","y"])
        env.variable_values["u"] = ("a","x")
        assert inperpret(root,env)


    def test_genAST_pred_power_set(self):
        # Build AST:
        string_to_file("#PREDICATE X:POW(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["X"] = set([])
        assert inperpret(root,env)

        env.variable_values["X"] = set(["a","b"])
        assert inperpret(root,env)

        env.variable_values["X"] = set(["a","c"])
        assert not inperpret(root,env)

        env.variable_values["X"] = set(["a"])
        assert inperpret(root,env)

        env.variable_values["X"] = set(["b"])
        assert inperpret(root,env)


    def test_genAST_pred_power_set2(self):
        # Build AST:
        string_to_file("#PREDICATE X:POW(POW(S))", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["X"] = set([])
        assert inperpret(root,env)

        env.variable_values["X"] = set([frozenset([])])
        assert inperpret(root,env)

        env.variable_values["X"] = set([frozenset(["a","b"])])
        assert inperpret(root,env)

    def test_genAST_pred_pow1_set(self):
        # Build AST:
        string_to_file("#PREDICATE X:POW1(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["X"] = set(frozenset([]))
        assert not inperpret(root,env)

        env.variable_values["X"] = set(frozenset(["a"]))
        assert inperpret(root,env)

        env.variable_values["X"] = set(frozenset(["b"]))
        assert inperpret(root,env)

        env.variable_values["X"] = set(frozenset(["a","b"]))
        assert inperpret(root,env)


    def test_genAST_pred_set_contains(self):
        # Build AST:
        string_to_file("#PREDICATE 1:{0,1,2,3,4}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert inperpret(root,env)


    def test_genAST_pred_set_contains2(self):
        # Build AST:
        string_to_file("#PREDICATE 41:{0,1,2,3,4}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert not inperpret(root,env)


    def test_genAST_pred_set_contains3(self):
        # Build AST:
        string_to_file("#PREDICATE x:{x}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.variable_values["x"] = "x"
        assert inperpret(root,env)

    def test_genAST_set_enum(self):
        # Build AST:
        string_to_file("#PREDICATE yy:{aa,bb,cc}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        #Test
        env = Environment()
        env.variable_values["yy"] = "aa"
        env.variable_values["aa"] = "aa" #FIXME: maybe this is a Bug..
        env.variable_values["bb"] = "bb" #
        env.variable_values["cc"] = "cc" #
        assert inperpret(root, env)

        env.variable_values["yy"] = "yy"
        assert not inperpret(root, env)


    def test_genAST_pred_set_orderd_pair(self):
        # Build AST:
        string_to_file("#PREDICATE x|->y:{(x,y)}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.variable_values["x"] = "x"
        env.variable_values["y"] = "y"
        assert inperpret(root,env)


    def test_genAST_pred_interval(self):
        # Build AST:
        string_to_file("#PREDICATE zz:1..5", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.variable_values["zz"] = 4
        assert inperpret(root,env)

        env.variable_values["zz"] = 5
        assert inperpret(root,env)

        env.variable_values["zz"] = 6
        assert not inperpret(root,env)

        env.variable_values["zz"] = 0
        assert not inperpret(root,env)



    def test_genAST_pred_nat(self):
        # Build AST:
        string_to_file("#PREDICATE x:NAT", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.variable_values["x"] = 2
        assert inperpret(root,env)

        env.variable_values["x"] = 0
        assert inperpret(root,env)


    def test_genAST_pred_nat1(self):
        # Build AST:
        string_to_file("#PREDICATE x:NAT1", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.variable_values["x"] = 2
        assert inperpret(root,env)

        env.variable_values["x"] = 0
        assert not inperpret(root,env)



    def test_genAST_pred_set_couple(self):
        # Build AST:
        string_to_file("#PREDICATE (1,0,41):{(0,0,41),(1,0,41),(0,1,41),(1,1,41)}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert inperpret(root,env)

    def test_genAST_pred_set_couple2(self):
        # Build AST:
        string_to_file("#PREDICATE (1,2,41):{(0,0,41),(1,0,41),(0,1,41),(1,1,41)}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert not inperpret(root,env)


    def test_genAST_pred_set_compreh(self):
        # Build AST:
        string_to_file("#PREDICATE (1,0,1):{(x,y,z) | x>=0 & x<=1 & y>=0 & y<=1 & z=1}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert inperpret(root,env)


    def test_genAST_pred_set_compreh2(self):
        # Build AST:
        string_to_file("#PREDICATE (1,2):{(x,y) | x>0 & x <4 & x/=0 or y/=x}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert inperpret(root,env)


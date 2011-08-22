# -*- coding: utf-8 -*-
from ast_nodes import *
from interp import inperpret, Environment
from helpers import file_to_AST_str, string_to_file

file_name = "input.txt"

class TestGenAST():
    def test_genAST_expr_add(self):
        # Build AST
        string_to_file("#PREDICATE 1+1=3", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert not inperpret(root, env)


    def test_genAST_expr_add2(self):
        # Build AST
        string_to_file("#PREDICATE 1+1=2", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert inperpret(root, env)


    def test_genAST_expr_sub(self):
        # Build AST
        string_to_file("#PREDICATE 4-3=1", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert inperpret(root, env)


    def test_genAST_expr_mul(self):
        # Build AST
        string_to_file("#PREDICATE 4*0=0", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert inperpret(root, env)


    def test_genAST_expr_div(self):
        # Build AST
        string_to_file("#PREDICATE 8/2=4", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert inperpret(root, env)


    def test_genAST_expr_mod(self):
        # Build AST
        string_to_file("#PREDICATE 8 mod 3=2", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert inperpret(root, env)


    def test_genAST_expr_neq(self):
        # Build AST
        string_to_file("#PREDICATE 0 /= 1", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert inperpret(root, env)


    def test_genAST_and(self):
        # Build AST
        string_to_file("#PREDICATE 1+1=2 & 7<8", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert inperpret(root, env)


    def test_genAST_or(self):
        # Build AST
        string_to_file("#PREDICATE 4*0=0 or 4*0=4", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert inperpret(root, env)


    def test_genAST_impl(self):
        # Build AST
        string_to_file("#PREDICATE 4>3 => 4>2", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert inperpret(root, env)


    def test_genAST_equi(self):
        # Build AST
        string_to_file("#PREDICATE (1+1=2) <=> (2+2=4)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert inperpret(root, env)


    def test_genAST_complex_arith(self):
        # Build AST
        string_to_file("#PREDICATE 6 = (2+2)*4+(10-0)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert not inperpret(root, env)

    def test_genAST_complex_arith2(self):
        # Build AST
        string_to_file("#PREDICATE 26 = (2+2)*4+(10-0)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert inperpret(root, env)

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


    def test_genAST_pred_gt(self):
        # Build AST:
        string_to_file("#PREDICATE 6>x", file_name)
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


    def test_genAST_pred_exist(self):
        # Build AST:
        string_to_file("#PREDICATE #(z).( z<4 & z>0)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert inperpret(root,env)

    def test_genAST_pred_exist2(self):
        # Build AST:
        string_to_file("#PREDICATE #(x,y).( x<0 & y>0 & x>y)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert not inperpret(root,env)

    def test_genAST_pred_exist3(self):
        # Build AST:
        string_to_file("#PREDICATE #(x,y).( x<0 & y>0 & y>x)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert inperpret(root,env)

    def test_genAST_pred_forall(self):
        # Build AST:
        string_to_file("#PREDICATE !(z).( z<4 => z<5)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert inperpret(root,env)

    def test_genAST_pred_forall2(self):
        # Build AST:
        string_to_file("#PREDICATE !(x,y,z).( x>0 & y>0 & z<4 => x+y=z)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
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


    def test_genAST_pred_rel(self):
        # Build AST:
        string_to_file("#PREDICATE f:S<->T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["T"] = set(["x","y"])
        env.variable_values["f"] = set([("a","x")])
        assert inperpret(root,env)

        env.variable_values["f"] = set([("a","x"),("a","y")])
        assert inperpret(root,env)

        env.variable_values["f"] = set([("a","x"),("b","y")])
        assert inperpret(root,env)

        env.variable_values["f"] = set([])
        assert inperpret(root,env)


    def test_genAST_pred_rel_dom(self):
        # Build AST:
        string_to_file("#PREDICATE S=dom(f)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.variable_values["S"] = set(["a"])
        env.variable_values["f"] = set([("a","x")])
        assert inperpret(root,env)
        
        env.variable_values["f"] = set([("1","x"),("2","y"),("3","z"),("1","y")])
        env.variable_values["S"] = set(["1","2","3"])
        assert inperpret(root,env)


    def test_genAST_pred_rel_comp(self):
        # Build AST:
        string_to_file("#PREDICATE S= (p ; q)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.variable_values["S"] = set([("1","x")])
        env.variable_values["p"] = set([("1","a")])
        env.variable_values["q"] = set([("a","x")])
        assert inperpret(root,env)

        env.variable_values["S"] = set([("1","a")])
        env.variable_values["p"] = set([("1","x"),("2","y"),("3","z"),("1","y")])
        env.variable_values["q"] = set([("x","a")])
        assert inperpret(root,env)

        env.variable_values["S"] = set([("1","a"),("2","a")])
        env.variable_values["p"] = set([("1","x"),("2","x"),("3","z")])
        env.variable_values["q"] = set([("x","a")])
        assert inperpret(root,env)

    def test_genAST_pred_rel_id(self):
        # Build AST:
        string_to_file("#PREDICATE r=id(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.variable_values["S"] = set(["a","b","c"])
        env.variable_values["r"] = set([("a","a"),("b","b"),("c","c")])
        assert inperpret(root,env)

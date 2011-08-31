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


    def test_genAST_pred_rel_domres(self):
        # Build AST:
        string_to_file("#PREDICATE f=S<|r", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.variable_values["S"] = set(["a"])
        env.variable_values["f"] = set([("a","1")])
        env.variable_values["r"] = set([("a","1"),("b","42"),("c","777")])
        assert inperpret(root,env)

        env.variable_values["f"] = set([("a","1"),("a","42")])
        env.variable_values["r"] = set([("a","1"),("a","42"),("c","777")])
        assert inperpret(root,env)


    def test_genAST_pred_rel_domsub(self):
        # Build AST:
        string_to_file("#PREDICATE f=S<<|r", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.variable_values["S"] = set(["a"])
        env.variable_values["f"] = set([("b","42"),("c","777")])
        env.variable_values["r"] = set([("a","1"),("b","42"),("c","777")])
        assert inperpret(root,env)

        env.variable_values["f"] = set([("c","777")])
        env.variable_values["r"] = set([("a","1"),("a","42"),("c","777")])
        assert inperpret(root,env)


    def test_genAST_pred_rel_ranres(self):
        # Build AST:
        string_to_file("#PREDICATE f=r|>T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.variable_values["T"] = set(["1"])
        env.variable_values["f"] = set([("a","1")])
        env.variable_values["r"] = set([("a","1"),("b","42"),("c","777")])
        assert inperpret(root,env)

        env.variable_values["f"] = set([("a","1"),("b","1")])
        env.variable_values["r"] = set([("a","1"),("b","1"),("c","777")])
        assert inperpret(root,env)


    def test_genAST_pred_rel_ransub(self):
        # Build AST:
        string_to_file("#PREDICATE f=r|>>T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.variable_values["T"] = set(["1"])
        env.variable_values["f"] = set([("b","42"),("c","777")])
        env.variable_values["r"] = set([("a","1"),("b","42"),("c","777")])
        assert inperpret(root,env)

        env.variable_values["f"] = set([("c","777")])
        env.variable_values["r"] = set([("a","1"),("b","1"),("c","777")])
        assert inperpret(root,env)


    def test_genAST_pred_rel_inverse(self):
        # Build AST:
        string_to_file("#PREDICATE f=r~", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.variable_values["f"] = set([("1","a"),("42","b"),("777","c")])
        env.variable_values["r"] = set([("a","1"),("b","42"),("c","777")])
        assert inperpret(root,env)

        env.variable_values["f"] = set([])
        env.variable_values["r"] = set([])
        assert inperpret(root,env)


    def test_genAST_pred_rel_image(self):
        # Build AST:
        string_to_file("#PREDICATE f=r[S]", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.variable_values["S"] = set(["a"])
        env.variable_values["f"] = set(["1"])
        env.variable_values["r"] = set([("a","1"),("b","42"),("c","777")])
        assert inperpret(root,env)

        env.variable_values["f"] = set(["1","42"])
        env.variable_values["r"] = set([("a","1"),("a","42"),("c","777")])
        assert inperpret(root,env)

        env.variable_values["S"] = set(["a","c"])
        env.variable_values["f"] = set(["1","42","777"])
        env.variable_values["r"] = set([("a","1"),("a","42"),("c","777")])
        assert inperpret(root,env)

        env.variable_values["S"] = set(["c"])
        env.variable_values["f"] = set(["777"])
        env.variable_values["r"] = set([("a","1"),("a","42"),("c","777")])
        assert inperpret(root,env)


    def test_genAST_pred_rel_overriding(self):
        # Build AST:
        string_to_file("#PREDICATE f=r1 <+ r2", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.variable_values["f"] = set([("a","1"),("b","42"),("c","777"),("d","17")])
        env.variable_values["r1"] = set([("d","17")])
        env.variable_values["r2"] = set([("a","1"),("b","42"),("c","777")])
        assert inperpret(root,env)

        env.variable_values["f"] = set([("a","1"),("b","41"),("c","777"),("d","17")])
        env.variable_values["r2"] = set([("d","17"),("b","41")])
        env.variable_values["r1"] = set([("a","1"),("b","42"),("c","777")])
        assert inperpret(root,env)


    def test_genAST_pred_rel_proj1(self):
        # Build AST:
        string_to_file("#PREDICATE f=prj1(S,T)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.variable_values["f"] = set([])
        env.variable_values["S"] = set([])
        env.variable_values["T"] = set([])
        assert inperpret(root,env)

        env.variable_values["f"] = set([(("a","y"),"a"),(("b","y"),"b"),(("a","x"),"a"),(("b","x"),"b")])
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["T"] = set(["x","y"])
        assert inperpret(root,env)


    def test_genAST_pred_rel_proj2(self):
        # Build AST:
        string_to_file("#PREDICATE f=prj2(S,T)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.variable_values["f"] = set([])
        env.variable_values["S"] = set([])
        env.variable_values["T"] = set([])
        assert inperpret(root,env)

        env.variable_values["f"] = set([(("a","y"),"y"),(("b","y"),"y"),(("a","x"),"x"),(("b","x"),"x")])
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["T"] = set(["x","y"])
        assert inperpret(root,env)

    def test_genAST_pred_rel_direct_prod(self):
        # Build AST:
        string_to_file("#PREDICATE f= p >< q", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.variable_values["f"] = set([])
        env.variable_values["p"] = set([])
        env.variable_values["q"] = set([])
        assert inperpret(root,env)

        env.variable_values["f"] = set([])
        env.variable_values["p"] = set([("x","1"),("y","2")])
        env.variable_values["q"] = set([("a","3"),("b","4")])
        assert inperpret(root,env)

        env.variable_values["f"] = set([("x",("1","3"))])
        env.variable_values["p"] = set([("x","1"),("y","2")])
        env.variable_values["q"] = set([("x","3"),("b","4")])
        assert inperpret(root,env)


    def test_genAST_pred_rel_parallel_prod(self):
        # Build AST:
        string_to_file("#PREDICATE f= (p || q)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.variable_values["f"] = set([])
        env.variable_values["p"] = set([])
        env.variable_values["q"] = set([])
        assert inperpret(root,env)

        env.variable_values["f"] = set([(("x","a"),("1","3")),(("x","b"),("1","4"))])
        env.variable_values["p"] = set([("x","1")])
        env.variable_values["q"] = set([("a","3"),("b","4")])
        assert inperpret(root,env)


    def test_genAST_pred_part_fun(self):
        # Build AST:
        string_to_file("#PREDICATE F=S+->T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        l = []
        l.append(frozenset([]))
        l.append(frozenset([("a","x")]))
        l.append(frozenset([("a","y")]))
        l.append(frozenset([("b","x")]))
        l.append(frozenset([("b","y")]))
        l.append(frozenset([("a","x"),("b","x")]))
        l.append(frozenset([("a","y"),("b","y")]))
        l.append(frozenset([("a","x"),("b","y")]))
        l.append(frozenset([("a","y"),("b","x")]))
        env = Environment()
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["T"] = set(["x","y"])
        env.variable_values["F"] = set(l)
        assert inperpret(root,env)

        l = []
        l.append(frozenset([("1","hallo_welt")]))
        l.append(frozenset([("2","hallo_welt")]))
        l.append(frozenset([("1","hallo_welt"),("2","hallo_welt")]))
        l.append(frozenset([]))
        env.variable_values["S"] = set(["1","2"])
        env.variable_values["T"] = set(["hallo_welt",])
        env.variable_values["F"] = set(l)
        assert inperpret(root,env)


    def test_genAST_pred_total_fun(self):
        # Build AST:
        string_to_file("#PREDICATE F=S-->T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        l = []
        l.append(frozenset([("a","x"),("b","x")]))
        l.append(frozenset([("a","y"),("b","y")]))
        l.append(frozenset([("a","x"),("b","y")]))
        l.append(frozenset([("a","y"),("b","x")]))
        env = Environment()
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["T"] = set(["x","y"])
        env.variable_values["F"] = set(l)
        assert inperpret(root,env)

        l = []
        l.append(frozenset([("1","hallo_welt"),("2","hallo_welt")]))
        env.variable_values["S"] = set(["1","2"])
        env.variable_values["T"] = set(["hallo_welt",])
        env.variable_values["F"] = set(l)
        assert inperpret(root,env)

    def test_genAST_pred_part_inj_fun(self):
        # Build AST:
        string_to_file("#PREDICATE F=S>+>T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        l = []
        l.append(frozenset([]))
        l.append(frozenset([("a","x")]))
        l.append(frozenset([("a","y")]))
        l.append(frozenset([("b","x")]))
        l.append(frozenset([("b","y")]))
        l.append(frozenset([("a","x"),("b","y")]))
        l.append(frozenset([("a","y"),("b","x")]))
        env = Environment()
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["T"] = set(["x","y"])
        env.variable_values["F"] = set(l)
        assert inperpret(root,env)

        l = []
        l.append(frozenset([("1","hallo_welt")]))
        l.append(frozenset([("2","hallo_welt")]))
        l.append(frozenset([]))
        env.variable_values["S"] = set(["1","2"])
        env.variable_values["T"] = set(["hallo_welt",])
        env.variable_values["F"] = set(l)
        assert inperpret(root,env)


    def test_genAST_pred_total_inj_fun(self):
        # Build AST:
        string_to_file("#PREDICATE F=S>->T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        l = []
        l.append(frozenset([("a","x"),("b","y")]))
        l.append(frozenset([("a","y"),("b","x")]))
        env = Environment()
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["T"] = set(["x","y"])
        env.variable_values["F"] = set(l)
        assert inperpret(root,env)


    def test_genAST_pred_part_surj_fun(self):
        # Build AST:
        string_to_file("#PREDICATE F=S+->>T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        l = []
        l.append(frozenset([("a","x"),("b","y")]))
        l.append(frozenset([("a","y"),("b","x")]))
        env = Environment()
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["T"] = set(["x","y"])
        env.variable_values["F"] = set(l)
        assert inperpret(root,env)

        l = []
        l.append(frozenset([("1","hallo_welt")]))
        l.append(frozenset([("2","hallo_welt")]))
        l.append(frozenset([("1","hallo_welt"),("2","hallo_welt")]))
        env.variable_values["S"] = set(["1","2"])
        env.variable_values["T"] = set(["hallo_welt",])
        env.variable_values["F"] = set(l)
        assert inperpret(root,env)


    def test_genAST_pred_total_surj_fun(self):
        # Build AST:
        string_to_file("#PREDICATE F=S-->>T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        l = []
        l.append(frozenset([("a","x"),("b","y")]))
        l.append(frozenset([("a","y"),("b","x")]))
        env = Environment()
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["T"] = set(["x","y"])
        env.variable_values["F"] = set(l)
        assert inperpret(root,env)

        l = []
        l.append(frozenset([("1","hallo_welt"),("2","hallo_welt")]))
        env.variable_values["S"] = set(["1","2"])
        env.variable_values["T"] = set(["hallo_welt",])
        env.variable_values["F"] = set(l)
        assert inperpret(root,env)

    def test_genAST_pred_bij_fun(self):
        # Build AST:
        string_to_file("#PREDICATE F=S>->>T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        l = []
        l.append(frozenset([("a","x"),("b","y"),("c","z")]))
        l.append(frozenset([("a","y"),("b","x"),("c","z")]))
        l.append(frozenset([("a","z"),("b","y"),("c","x")]))
        l.append(frozenset([("a","x"),("b","z"),("c","y")]))
        l.append(frozenset([("a","y"),("b","z"),("c","x")]))
        l.append(frozenset([("a","z"),("b","x"),("c","y")]))
        env = Environment()
        env.variable_values["S"] = set(["a","b","c"])
        env.variable_values["T"] = set(["x","y","z"])
        env.variable_values["F"] = set(l)
        assert inperpret(root,env)

        env.variable_values["S"] = set(["1","2"])
        env.variable_values["T"] = set(["hallo_welt",])
        env.variable_values["F"] = set([])
        assert inperpret(root,env)


    def test_genAST_pred_bij_fun2(self):
        # Build AST:
        string_to_file("#PREDICATE F=S>->>T>->>U", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        l = [frozenset([(frozenset([('x2', 'y1'), ('x1', 'y2')]), 'z1'), (frozenset([('x1', 'y1'), ('x2', 'y2')]), 'z2')]), frozenset([(frozenset([('x1', 'y1'), ('x2', 'y2')]), 'z1'), (frozenset([('x2', 'y1'), ('x1', 'y2')]), 'z2')])]
        env = Environment()
        env.variable_values["S"] = set(["x1","x2"])
        env.variable_values["T"] = set(["y1","y2"])
        env.variable_values["U"] = set(["z1","z2"])
        env.variable_values["F"] = set(l)
        assert inperpret(root,env)


    def test_genAST_pred_fun_app(self):
        # Build AST:
        string_to_file("#PREDICATE f={(a,x),(b,y)} & f(b)=y", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["a"] = "a"
        env.variable_values["b"] = "b"
        env.variable_values["x"] = "x"
        env.variable_values["y"] = "y"
        env.variable_values["f"] = set([("a","x"),("b","y")])
        assert inperpret(root,env)


    def test_genAST_pred_fun_app2(self):
        # Build AST:
        string_to_file("#PREDICATE f:S*T>->>V & x:S*T & f(x)=y", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["S"] = set(["x1","x2"])
        env.variable_values["T"] = set(["y1","y2"])
        env.variable_values["V"] = set(["z1","z2","z3","z4"])
        env.variable_values["x"] = ("x1","y1")
        env.variable_values["f"] = frozenset([(("x1","y1"),"z1"),(("x2","y2"),"z2"),(("x1","y2"),"z3"),(("x2","y1"),"z4")])
        env.variable_values["y"] = "z1"
        assert inperpret(root,env)


    def test_genAST_pred_seq_empty(self):
        # Build AST:
        string_to_file("#PREDICATE []={}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        assert inperpret(root,env)


    def test_genAST_pred_seq_simple(self):
        # Build AST:
        string_to_file("#PREDICATE s:seq(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["s"] = frozenset([])
        assert inperpret(root,env)

        env.variable_values["s"] = frozenset([(1,"a")])
        assert inperpret(root,env)

        env.variable_values["s"] = frozenset([(1,"a"),(2,"b"),(3,"a")])
        assert inperpret(root,env)


    def test_genAST_pred_seq_no_empty(self):
        # Build AST:
        string_to_file("#PREDICATE s:seq1(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["s"] = frozenset([])
        assert not inperpret(root,env)

        env.variable_values["s"] = frozenset([(1,"a")])
        assert inperpret(root,env)

        env.variable_values["s"] = frozenset([(1,"b"),(2,"a"),(3,"b")])
        assert inperpret(root,env)

        env.variable_values["s"] = frozenset([(1,"a"),(1,"b"),(1,"a")])
        assert not inperpret(root,env)


    def test_genAST_pred_seq_injective(self):
        # Build AST:
        string_to_file("#PREDICATE s=iseq(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["s"] = set([frozenset([(2, 'a'), (1, 'b')]), frozenset([(1, 'a')]), frozenset([(1, 'a'), (2, 'b')]), frozenset([]), frozenset([(1, 'b')])])
        assert inperpret(root,env)

    def test_genAST_pred_seq_perm(self):
        # Build AST:
        string_to_file("#PREDICATE s=perm(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["s"] = set([frozenset([(2, 'a'), (1, 'b')]), frozenset([(1, 'a'), (2, 'b')])])
        assert inperpret(root,env)

        env.variable_values["s"] = frozenset([])
        assert not inperpret(root,env)

    def test_genAST_pred_seq_conc(self):
        # Build AST:
        string_to_file("#PREDICATE s:perm(S) & t:perm(S) => s^t:seq(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["s"] = frozenset([(2, 'a'), (1, 'b')]) 
        env.variable_values["t"] = frozenset([(1, 'a'), (2, 'b')])
        assert inperpret(root,env)

    def test_genAST_pred_seq_prepend(self):
        # Build AST:
        string_to_file("#PREDICATE s:perm(S) => a->s:seq(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["s"] = frozenset([(2, 'a'), (1, 'b')]) 
        env.variable_values["a"] = "a"
        assert inperpret(root,env)


    def test_genAST_pred_seq_append(self):
        # Build AST:
        string_to_file("#PREDICATE s:perm(S) => s<-a:seq(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["s"] = frozenset([(2, 'a'), (1, 'b')]) 
        env.variable_values["a"] = "a"
        assert inperpret(root,env)


    def test_genAST_pred_seq_size(self):
        # Build AST:
        string_to_file("#PREDICATE s=[a,b] & size(s)=2", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["s"] = frozenset([(1, 'a'), (2, 'b')]) 
        env.variable_values["a"] = "a"
        env.variable_values["b"] = "b"
        assert inperpret(root,env)


    def test_genAST_pred_seq_reverse(self):
        # Build AST:
        string_to_file("#PREDICATE s=[a,b] & rev(s)=[b,a]", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["s"] = frozenset([(1, 'a'), (2, 'b')]) 
        env.variable_values["a"] = "a"
        env.variable_values["b"] = "b"
        assert inperpret(root,env)


    def test_genAST_pred_seq_take(self):
        # Build AST:
        string_to_file("#PREDICATE s=[a,b,c,d,e]/|\\3", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["s"] = frozenset([(1, 'a'), (2, 'b')]) 
        env.variable_values["a"] = "a"
        env.variable_values["b"] = "b"
        env.variable_values["c"] = "c"
        env.variable_values["d"] = "d"
        env.variable_values["e"] = "e"
        assert inperpret(root,env)


    def test_genAST_pred_seq_drop(self):
        # Build AST:
        string_to_file("#PREDICATE s=[a,b,c,d,e]\\|/3", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["s"] = frozenset([(1, 'd'), (2, 'e')]) 
        env.variable_values["a"] = "a"
        env.variable_values["b"] = "b"
        env.variable_values["c"] = "c"
        env.variable_values["d"] = "d"
        env.variable_values["e"] = "e"
        assert inperpret(root,env)


    def test_genAST_pred_seq_first(self):
        # Build AST:
        string_to_file("#PREDICATE s=[a,b,c,d,e] & first(s)=a", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["s"] = frozenset([(1, 'a'), (2, 'b'),(3, 'c'), (4, 'd'),(5,'e')]) 
        env.variable_values["a"] = "a"
        env.variable_values["b"] = "b"
        env.variable_values["c"] = "c"
        env.variable_values["d"] = "d"
        env.variable_values["e"] = "e"
        assert inperpret(root,env)


    def test_genAST_pred_seq_last(self):
        # Build AST:
        string_to_file("#PREDICATE s=[a,b,c,d,e] & last(s)=e", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["s"] = frozenset([(1, 'a'), (2, 'b'),(3, 'c'), (4, 'd'),(5,'e')]) 
        env.variable_values["a"] = "a"
        env.variable_values["b"] = "b"
        env.variable_values["c"] = "c"
        env.variable_values["d"] = "d"
        env.variable_values["e"] = "e"
        assert inperpret(root,env)


    def test_genAST_pred_seq_tail(self):
        # Build AST:
        string_to_file("#PREDICATE s=[a,b,c,d,e] & tail(s)=t", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["s"] = frozenset([(1, 'a'), (2, 'b'),(3, 'c'), (4, 'd'),(5,'e')])
        env.variable_values["t"] = frozenset([ (2, 'b'),(3, 'c'), (4, 'd'),(5,'e')]) 
        env.variable_values["a"] = "a"
        env.variable_values["b"] = "b"
        env.variable_values["c"] = "c"
        env.variable_values["d"] = "d"
        env.variable_values["e"] = "e"
        assert inperpret(root,env)


    def test_genAST_pred_seq_front(self):
        # Build AST:
        string_to_file("#PREDICATE s=[a,b,c,d,e] & front(s)=t", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["s"] = frozenset([(1, 'a'), (2, 'b'),(3, 'c'), (4, 'd'),(5,'e')])
        env.variable_values["t"] = frozenset([(1, 'a'), (2, 'b'),(3, 'c'), (4, 'd')]) 
        env.variable_values["a"] = "a"
        env.variable_values["b"] = "b"
        env.variable_values["c"] = "c"
        env.variable_values["d"] = "d"
        env.variable_values["e"] = "e"
        assert inperpret(root,env)
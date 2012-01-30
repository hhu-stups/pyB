# -*- coding: utf-8 -*-
from ast_nodes import *
from interp import interpret, Environment
from helpers import file_to_AST_str, string_to_file
from typing import IntegerType, PowerSetType, SetType, _test_typeit

file_name = "input.txt"

class TestInterpSets():
    def test_genAST_member(self):
        # Build AST
        string_to_file("#PREDICATE x:S", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("x", "x")
        env.set_value("S", set(["x","y","z"]))
        assert interpret(root.children[0], env)

        env.set_value("S", set(["a","b","c"]))
        assert not interpret(root.children[0], env)


    def test_genAST_not_member(self):
        # Build AST
        string_to_file("#PREDICATE x/:S", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("x", "x")
        env.set_value("S", set(["x","y","z"]))
        assert not interpret(root.children[0], env)

        env.set_value("S", set(["a","b","c"]))
        assert interpret(root.children[0], env)


    def test_genAST_subset(self):
        # Build AST
        string_to_file("#PREDICATE S<:T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("T", set(["x","y"]))
        env.set_value("S", set(["x","y","z"]))
        assert not interpret(root.children[0], env)

        env.set_value("S", set(["a","b","c"]))
        env.set_value("T", set(["a","b","c"]))
        assert interpret(root.children[0], env)


    def test_genAST_subset2(self):
        # Build AST
        string_to_file("#PREDICATE {}<:{1}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert interpret(root.children[0], env)


    def test_genAST_not_subset(self):
        # Build AST
        string_to_file("#PREDICATE S/<:T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("T", set(["x","y"]))
        env.set_value("S", set(["x","y","z"]))
        assert interpret(root.children[0], env)

        env.set_value("S", set(["a","b","c"]))
        env.set_value("T", set(["a","b","c"]))
        assert not interpret(root.children[0], env)


    def test_genAST_prop_subset(self):
        # Build AST
        string_to_file("#PREDICATE S<<:T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("T", set(["x","y"]))
        env.set_value("S", set(["x","y","z"]))
        assert not interpret(root.children[0], env)

        env.set_value("S", set(["a","b","c"]))
        env.set_value("T", set(["a","b","c"]))
        assert not interpret(root.children[0], env)

        env.set_value("S", set(["x","y"]))
        env.set_value("T", set(["x","y","z"]))
        assert interpret(root.children[0], env)


    def test_genAST_not_prop_subset(self):
        # Build AST
        string_to_file("#PREDICATE S/<<:T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("T", set(["x","y"]))
        env.set_value("S", set(["x","y","z"]))
        assert interpret(root.children[0], env)

        env.set_value("S", set(["a","b","c"]))
        env.set_value("T", set(["a","b","c"]))
        assert interpret(root.children[0], env)

        env.set_value("S", set(["x","y"]))
        env.set_value("T", set(["x","y","z"]))
        assert not interpret(root.children[0], env)


    def test_genAST_pred_set_cart(self):
        # Build AST:
        string_to_file("#PREDICATE u:S*T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("S", set(["a","b"]))
        env.set_value("T", set(["x","y"]))
        env.set_value("u", ("a","x"))
        assert interpret(root.children[0],env)



    def test_genAST_pred_set_union(self):
        # Build AST:
        string_to_file("#PREDICATE A={1,2,3,4,5} & B={3,4,5,6,7} & C = A\/B", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("A", set([1,2,3,4,5]))
        env.set_value("B", set([3,4,5,6,7]))
        env.set_value("C", set([1,2,3,4,5,6,7]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_set_intersection(self):
        # Build AST:
        string_to_file("#PREDICATE A={1,2,3,4,5} & B={3,4,5,6,7} & C = A/\B", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("A", set([1,2,3,4,5]))
        env.set_value("B", set([3,4,5,6,7]))
        env.set_value("C", set([3,4,5]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_set_diff(self):
        # Build AST:
        string_to_file("#PREDICATE A={1,2,3,4,5} & B={3,4,5,6,7} & C = A-B", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("A", set([1,2,3,4,5]))
        env.set_value("B", set([3,4,5,6,7]))
        env.set_value("C", set([1,2]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_power_set(self):
        # Build AST:
        string_to_file("#PREDICATE X:POW(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("S", set(["a","b"]))
        env.set_value("X", set([]))
        assert interpret(root.children[0],env)

        env.set_value("X", set(["a","b"]))
        assert interpret(root.children[0],env)

        env.set_value("X", set(["a","c"]))
        assert not interpret(root.children[0],env)

        env.set_value("X", set(["a"]))
        assert interpret(root.children[0],env)

        env.set_value("X", set(["b"]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_power_set2(self):
        # Build AST:
        string_to_file("#PREDICATE X:POW(POW(S))", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("S", set(["a","b"]))
        env.set_value("X", set([]))
        assert interpret(root.children[0],env)

        env.set_value("X", set([frozenset([])]))
        assert interpret(root.children[0],env)

        env.set_value("X", set([frozenset(["a","b"])]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_pow1_set(self):
        # Build AST:
        string_to_file("#PREDICATE X:POW1(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("S", set(["a","b"]))
        env.set_value("X", set(frozenset([])))
        assert not interpret(root.children[0],env)

        env.set_value("X", set(frozenset(["a"])))
        assert interpret(root.children[0],env)

        env.set_value("X", set(frozenset(["b"])))
        assert interpret(root.children[0],env)

        env.set_value("X", set(frozenset(["a","b"])))
        assert interpret(root.children[0],env)


    def test_genAST_pred_set_contains(self):
        # Build AST:
        string_to_file("#PREDICATE 1:{0,1,2,3,4}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert interpret(root.children[0],env)


    def test_genAST_pred_set_contains2(self):
        # Build AST:
        string_to_file("#PREDICATE 41:{0,1,2,3,4}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert not interpret(root.children[0],env)


    def test_genAST_pred_set_contains3(self):
        # Build AST:
        string_to_file("#PREDICATE x:{x}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("x", "x")
        assert interpret(root.children[0],env)


    def test_genAST_set_enum(self):
        # Build AST:
        string_to_file("#PREDICATE yy:{aa,bb,cc}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        #Test
        env = Environment()
        env.set_value("yy", "aa")
        env.set_value("aa", "aa") #FIXME: maybe this is a Bug..
        env.set_value("bb", "bb") #
        env.set_value("cc", "cc") #
        assert interpret(root.children[0], env)

        env.set_value("yy","yy")
        assert not interpret(root.children[0], env)


    def test_genAST_pred_set_orderd_pair(self):
        # Build AST:
        string_to_file("#PREDICATE x|->y:{(x,y)}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("x", "x")
        env.set_value("y", "y")
        assert interpret(root.children[0],env)


    def test_genAST_pred_interval(self):
        # Build AST:
        string_to_file("#PREDICATE zz:1..5", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("zz", 4)
        assert interpret(root.children[0],env)

        env.set_value("zz", 5)
        assert interpret(root.children[0],env)

        env.set_value("zz", 6)
        assert not interpret(root.children[0],env)

        env.set_value("zz", 0)
        assert not interpret(root.children[0],env)


    def test_genAST_pred_nat(self):
        # Build AST:
        string_to_file("#PREDICATE x:NAT", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("x", 2)
        assert interpret(root.children[0],env)

        env.set_value("x", 0)
        assert interpret(root.children[0],env)


    def test_genAST_pred_nat1(self):
        # Build AST:
        string_to_file("#PREDICATE x:NAT1", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("x", 2)
        assert interpret(root.children[0],env)

        env.set_value("x", 0)
        assert not interpret(root.children[0],env)


    def test_genAST_pred_set_couple(self):
        # Build AST:
        string_to_file("#PREDICATE (1,0,41):{(0,0,41),(1,0,41),(0,1,41),(1,1,41)}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert interpret(root.children[0],env)


    def test_genAST_pred_set_couple2(self):
        # Build AST:
        string_to_file("#PREDICATE (1,2,41):{(0,0,41),(1,0,41),(0,1,41),(1,1,41)}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert not interpret(root.children[0],env)


    def test_genAST_pred_set_compreh(self):
        # Build AST:
        string_to_file("#PREDICATE (1,0,1):{(x,y,z) | x>=0 & x<=1 & y>=0 & y<=1 & z=1}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        _test_typeit(root.children[0], env, [], [])
        assert interpret(root.children[0],env)


    def test_genAST_pred_set_compreh2(self):
        # Build AST:
        string_to_file("#PREDICATE (1,2):{(x,y) | x>0 & x <4 & x/=0 or y/=x}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        _test_typeit(root.children[0], env, [], [])
        assert interpret(root.children[0],env)


    def test_genAST_pred_forall3(self):
        # Build AST:
        string_to_file("#PREDICATE T<:S & S:POW(ID) & !(x).(x:T => x:S)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("ID", set(["a","b"]))
        env.set_value("S", set(["a","b"]))
        env.set_value("T", set(["a"]))
        lst = [("ID", PowerSetType(SetType("ID")))]
        _test_typeit(root.children[0], env, lst, ["T","S"])
        assert interpret(root.children[0],env)


    def test_genAST_pred_forall4(self):
        # Build AST:
        string_to_file("#PREDICATE S:POW(ID) & !(X,y).(X<:S => card(X)=y)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("ID", set(["a","b"]))
        env.set_value("S", set(["a","b"]))
        lst = [("ID", PowerSetType(SetType("ID")))]
        _test_typeit(root.children[0], env, lst, ["S"])
        assert not interpret(root.children[0],env)


    def test_genAST_pred_exist4(self):
        # Build AST:
        string_to_file("#PREDICATE T<:POW(ID) & #(X).(X<:POW(ID) => X=T )", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("ID", set(["a","b"]))
        env.set_value("T", set([frozenset(["a","b"]),frozenset(["a"]),frozenset(["b"]),frozenset([])]))
        lst = [("ID", PowerSetType(SetType("ID")))]
        _test_typeit(root.children[0], env, lst, ["T"])
        assert interpret(root.children[0],env)


    def test_genAST_set_gen_union(self):
        # Build AST:
        string_to_file("#PREDICATE U:POW(POW(S)) & u=union(U)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("S", set(["a","b","c"]))
        env.set_value("U", set([frozenset(["a","b","c"])]))
        env.set_value("u", set(["a","b","c"]))
        assert interpret(root.children[0],env)
        env.set_value("U", set([frozenset(["a","b","c"]),frozenset([])]))
        env.set_value("u", set(["a","b","c"]))
        assert interpret(root.children[0],env)
        env.set_value("U", set([frozenset(["a","b"]),frozenset(["c"])]))
        env.set_value("u", set(["a","b","c"]))
        assert interpret(root.children[0],env)
        env.set_value("U", set([frozenset(["a","b"]),frozenset(["a","c"])]))
        env.set_value("u", set(["a","b","c"]))
        assert interpret(root.children[0],env)


    def test_genAST_set_gen_inter(self):
        # Build AST:
        string_to_file("#PREDICATE U:POW(POW(S)) & u=inter(U)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("S", set(["a","b","c"]))
        env.set_value("U", set([frozenset(["a","b","c"])]))
        env.set_value("u", set(["a","b","c"]))
        assert interpret(root.children[0],env)
        env.set_value("U", set([frozenset(["a","b","c"]),frozenset(["a"])]))
        env.set_value("u", set(["a"]))
        assert interpret(root.children[0],env)
        env.set_value("U", set([frozenset(["a","b"]),frozenset(["c"])]))
        env.set_value("u", set([]))
        assert interpret(root.children[0],env)
        env.set_value("U", set([frozenset(["a","b"]),frozenset(["c"]),frozenset(["a"])]))
        env.set_value("u", set([]))
        assert interpret(root.children[0],env)
        env.set_value("U", set([frozenset(["a","b"]),frozenset(["c","b"]),frozenset(["a","b"])]))
        env.set_value("u", set(["b"]))
        assert interpret(root.children[0],env)


    def test_genAST_string(self):
        # Build AST
        string_to_file("#PREDICATE s=\"Hallo Welt\"", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("s", "Hallo Welt")
        assert interpret(root.children[0],env)
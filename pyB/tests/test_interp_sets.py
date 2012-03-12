# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from interp import interpret, Environment
from helpers import file_to_AST_str, string_to_file
from typing import _test_typeit

file_name = "input.txt"

class TestInterpSets():
    def test_genAST_member(self):
        # Build AST
        string_to_file("#PREDICATE x:S", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.add_ids_to_frame(["x","S"])
        env.set_value("x", "x")
        env.set_value("S", frozenset(["x","y","z"]))
        assert interpret(root.children[0], env)

        env.set_value("S", frozenset(["a","b","c"]))
        assert not interpret(root.children[0], env)


    def test_genAST_not_member(self):
        # Build AST
        string_to_file("#PREDICATE x/:S", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.add_ids_to_frame(["x","S"])
        env.set_value("x", "x")
        env.set_value("S", frozenset(["x","y","z"]))
        assert not interpret(root.children[0], env)

        env.set_value("S", frozenset(["a","b","c"]))
        assert interpret(root.children[0], env)


    def test_genAST_subset(self):
        # Build AST
        string_to_file("#PREDICATE S<:T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.add_ids_to_frame(["T","S"])
        env.set_value("T", frozenset(["x","y"]))
        env.set_value("S", frozenset(["x","y","z"]))
        assert not interpret(root.children[0], env)

        env.set_value("S", frozenset(["a","b","c"]))
        env.set_value("T", frozenset(["a","b","c"]))
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
        env.add_ids_to_frame(["T","S"])
        env.set_value("T", frozenset(["x","y"]))
        env.set_value("S", frozenset(["x","y","z"]))
        assert interpret(root.children[0], env)

        env.set_value("S", frozenset(["a","b","c"]))
        env.set_value("T", frozenset(["a","b","c"]))
        assert not interpret(root.children[0], env)


    def test_genAST_prop_subset(self):
        # Build AST
        string_to_file("#PREDICATE S<<:T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.add_ids_to_frame(["T","S"])
        env.set_value("T", frozenset(["x","y"]))
        env.set_value("S", frozenset(["x","y","z"]))
        assert not interpret(root.children[0], env)

        env.set_value("S", frozenset(["a","b","c"]))
        env.set_value("T", frozenset(["a","b","c"]))
        assert not interpret(root.children[0], env)

        env.set_value("S", frozenset(["x","y"]))
        env.set_value("T", frozenset(["x","y","z"]))
        assert interpret(root.children[0], env)


    def test_genAST_not_prop_subset(self):
        # Build AST
        string_to_file("#PREDICATE S/<<:T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.add_ids_to_frame(["T","S"])
        env.set_value("T", frozenset(["x","y"]))
        env.set_value("S", frozenset(["x","y","z"]))
        assert interpret(root.children[0], env)

        env.set_value("S", frozenset(["a","b","c"]))
        env.set_value("T", frozenset(["a","b","c"]))
        assert interpret(root.children[0], env)

        env.set_value("S", frozenset(["x","y"]))
        env.set_value("T", frozenset(["x","y","z"]))
        assert not interpret(root.children[0], env)


    def test_genAST_pred_set_cart(self):
        # Build AST:
        string_to_file("#PREDICATE u:S*T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.add_ids_to_frame(["T","S","u"])
        env.set_value("S", frozenset(["a","b"]))
        env.set_value("T", frozenset(["x","y"]))
        env.set_value("u", ("a","x"))
        assert interpret(root.children[0],env)



    def test_genAST_pred_set_union(self):
        # Build AST:
        string_to_file("#PREDICATE A={1,2,3,4,5} & B={3,4,5,6,7} & C = A\/B", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.add_ids_to_frame(["A","B","C"])
        env.set_value("A", frozenset([1,2,3,4,5]))
        env.set_value("B", frozenset([3,4,5,6,7]))
        env.set_value("C", frozenset([1,2,3,4,5,6,7]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_set_intersection(self):
        # Build AST:
        string_to_file("#PREDICATE A={1,2,3,4,5} & B={3,4,5,6,7} & C = A/\B", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.add_ids_to_frame(["A","B","C"])
        env.set_value("A", frozenset([1,2,3,4,5]))
        env.set_value("B", frozenset([3,4,5,6,7]))
        env.set_value("C", frozenset([3,4,5]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_set_diff(self):
        # Build AST:
        string_to_file("#PREDICATE A={1,2,3,4,5} & B={3,4,5,6,7} & C = A-B", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.add_ids_to_frame(["A","B","C"])
        env.set_value("A", frozenset([1,2,3,4,5]))
        env.set_value("B", frozenset([3,4,5,6,7]))
        env.set_value("C", frozenset([1,2]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_set_diff2(self):
        # Build AST:
        string_to_file("#PREDICATE A={1,2,3,4,5} & B={3,4,5,6,7} & C = A\B", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.add_ids_to_frame(["A","B","C"])
        env.set_value("A", frozenset([1,2,3,4,5]))
        env.set_value("B", frozenset([3,4,5,6,7]))
        env.set_value("C", frozenset([1,2]))
        assert interpret(root.children[0],env)

    def test_genAST_pred_power_set(self):
        # Build AST:
        string_to_file("#PREDICATE X:POW(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.add_ids_to_frame(["X","S"])
        env.set_value("S", frozenset(["a","b"]))
        env.set_value("X", frozenset([]))
        assert interpret(root.children[0],env)

        env.set_value("X", frozenset(["a","b"]))
        assert interpret(root.children[0],env)

        env.set_value("X", frozenset(["a","c"]))
        assert not interpret(root.children[0],env)

        env.set_value("X", frozenset(["a"]))
        assert interpret(root.children[0],env)

        env.set_value("X", frozenset(["b"]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_power_set2(self):
        # Build AST:
        string_to_file("#PREDICATE X:POW(POW(S))", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.add_ids_to_frame(["S","X"])
        env.set_value("S", frozenset(["a","b"]))
        env.set_value("X", frozenset([]))
        assert interpret(root.children[0],env)

        env.set_value("X", frozenset([frozenset([])]))
        assert interpret(root.children[0],env)

        env.set_value("X", frozenset([frozenset(["a","b"])]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_pow1_set(self):
        # Build AST:
        string_to_file("#PREDICATE X:POW1(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.add_ids_to_frame(["S","X"])
        env.set_value("S", frozenset(["a","b"]))
        env.set_value("X", frozenset(frozenset([])))
        assert not interpret(root.children[0],env)

        env.set_value("X", frozenset(frozenset(["a"])))
        assert interpret(root.children[0],env)

        env.set_value("X", frozenset(frozenset(["b"])))
        assert interpret(root.children[0],env)

        env.set_value("X", frozenset(frozenset(["a","b"])))
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
        env.add_ids_to_frame(["x"])
        env.set_value("x", "x")
        assert interpret(root.children[0],env)


    def test_genAST_set_enum(self):
        # Build AST:
        string_to_file("#PREDICATE yy:{aa,bb,cc}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        #Test
        env = Environment()
        env.add_ids_to_frame(["yy","aa","bb","cc"])
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
        env.add_ids_to_frame(["x","y"])
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
        env.add_ids_to_frame(["zz"])
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
        env.add_ids_to_frame(["x"])
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
        env.add_ids_to_frame(["x"])
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
        env.add_ids_to_frame(["S","T","ID"])
        env.set_value("ID", frozenset(["a","b"]))
        env.set_value("S", frozenset(["a","b"]))
        env.set_value("T", frozenset(["a"]))
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
        env.add_ids_to_frame(["S","ID"])
        env.set_value("ID", frozenset(["a","b"]))
        env.set_value("S", frozenset(["a","b"]))
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
        env.add_ids_to_frame(["ID","T"])
        env.set_value("ID", frozenset(["a","b"]))
        env.set_value("T", frozenset([frozenset(["a","b"]),frozenset(["a"]),frozenset(["b"]),frozenset([])]))
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
        env.add_ids_to_frame(["S","U","u"])
        env.set_value("S", frozenset(["a","b","c"]))
        env.set_value("U", frozenset([frozenset(["a","b","c"])]))
        env.set_value("u", frozenset(["a","b","c"]))
        assert interpret(root.children[0],env)
        env.set_value("U", frozenset([frozenset(["a","b","c"]),frozenset([])]))
        env.set_value("u", frozenset(["a","b","c"]))
        assert interpret(root.children[0],env)
        env.set_value("U", frozenset([frozenset(["a","b"]),frozenset(["c"])]))
        env.set_value("u", frozenset(["a","b","c"]))
        assert interpret(root.children[0],env)
        env.set_value("U", frozenset([frozenset(["a","b"]),frozenset(["a","c"])]))
        env.set_value("u", frozenset(["a","b","c"]))
        assert interpret(root.children[0],env)


    def test_genAST_set_gen_inter(self):
        # Build AST:
        string_to_file("#PREDICATE U:POW(POW(S)) & u=inter(U)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.add_ids_to_frame(["S","U","u"])
        env.set_value("S", frozenset(["a","b","c"]))
        env.set_value("U", frozenset([frozenset(["a","b","c"])]))
        env.set_value("u", frozenset(["a","b","c"]))
        assert interpret(root.children[0],env)
        env.set_value("U", frozenset([frozenset(["a","b","c"]),frozenset(["a"])]))
        env.set_value("u", frozenset(["a"]))
        assert interpret(root.children[0],env)
        env.set_value("U", frozenset([frozenset(["a","b"]),frozenset(["c"])]))
        env.set_value("u", frozenset([]))
        assert interpret(root.children[0],env)
        env.set_value("U", frozenset([frozenset(["a","b"]),frozenset(["c"]),frozenset(["a"])]))
        env.set_value("u", set([]))
        assert interpret(root.children[0],env)
        env.set_value("U", set([frozenset(["a","b"]),frozenset(["c","b"]),frozenset(["a","b"])]))
        env.set_value("u", frozenset(["b"]))
        assert interpret(root.children[0],env)


    def test_genAST_set_GEN_UNION2(self):
        string = '''
        MACHINE Test
        VARIABLES xx, E2
        INVARIANT xx:NAT & E2:POW(NAT)
        INITIALISATION E2:={2,4} ; 
            xx:: UNION (x1).(x1 : E2 | {y1 | y1 : NAT & y1 <= x1}) 
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")==0 or env.get_value("xx")==1 or env.get_value("xx")==2 or env.get_value("xx")==3 or env.get_value("xx")==4


    def test_genAST_set_GEN_INTER2(self):
        string = '''
        MACHINE Test
        VARIABLES xx, E2
        INVARIANT xx:NAT & E2:POW(NAT)
        INITIALISATION E2:={2,4} ; 
            xx:: INTER (x1).(x1 : E2 | {y1 | y1 : NAT & y1 <= x1}) 
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # init VARIABLES and eval INVARIANT
        assert isinstance(root.children[1], AInvariantMachineClause)
        assert interpret(root.children[1], env)
        assert env.get_value("xx")==0 or env.get_value("xx")==1 or env.get_value("xx")==2 



    def test_genAST_string(self):
        # Build AST
        string_to_file("#PREDICATE s=\"Hallo Welt\"", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.add_ids_to_frame(["s"])
        env.set_value("s", "Hallo Welt")
        assert interpret(root.children[0],env)


    def test_genAST_bool(self):
        # Build AST
        string_to_file("#PREDICATE A:BOOL & B:BOOL & C:BOOL & (A=TRUE <=> (B=FALSE or C=FALSE)) & (B=TRUE <=> A=TRUE)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.add_ids_to_frame(["A","B","C"])
        env.set_value("A", True)
        env.set_value("B", True)
        env.set_value("C", False)
        assert interpret(root.children[0],env)

        env.set_value("A", False)
        env.set_value("B", False)
        env.set_value("C", False)
        assert not interpret(root.children[0],env)
# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from environment import Environment
from typing import _test_typeit
from helpers import file_to_AST_str, string_to_file

file_name = "input.txt"

class TestTypesSets():
    def test_types_card(self):
        # Build AST
        string_to_file("#PREDICATE card(S)=3", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.add_ids_to_frame(["S"])
        env.set_value("S", frozenset(["Huey", "Dewey", "Louie"]))
        lst = [("S", PowerSetType(SetType("X")))]
        _test_typeit(root, env, lst, [])


    def test_types_simple_set(self):
        # Build AST
        string_to_file("#PREDICATE ID={aa,bb}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.add_ids_to_frame(["aa","bb","ID"])
        env.set_value("aa", "aa")
        env.set_value("bb", "bb")
        env.set_value("ID", frozenset(["aa", "bb"]))
        lst = [("aa", SetType("X")),("bb", SetType("X"))]
        _test_typeit(root, env, lst, ["ID"])
        assert isinstance(env.get_type("ID"), PowerSetType)
        assert isinstance(env.get_type("ID").data, SetType)
        assert env.get_type("ID").data.data =="X"


    def test_types_simple_set_empty(self):
        # Build AST
        string_to_file("#PREDICATE ID={} & ID<:NAT", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["ID"])
        assert isinstance(env.get_type("ID"), PowerSetType)


    def test_types_simple_set_com(self):
        # Build AST
        string_to_file("#PREDICATE ID={x|x<10}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["ID"])
        assert isinstance(env.get_type("ID"), PowerSetType)
        assert isinstance(env.get_type("x"), IntegerType)


    def test_types_simple_set_com2(self):
        # Build AST
        string_to_file("#PREDICATE S={a,b} & ID={x,y|x<10 & y:S}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("a", SetType("X")),("b", SetType("X"))]
        _test_typeit(root, env, lst, ["S","ID"]) 
        assert isinstance(env.get_type("S"), PowerSetType)
        assert isinstance(env.get_type("ID"), PowerSetType)
        assert isinstance(env.get_type("x"), IntegerType)
        assert isinstance(env.get_type("y"), SetType)
        assert env.get_type("y").data =="X"


    def test_types_simple_set_union(self):
        # Build AST
        string_to_file("#PREDICATE S=A\/B & T=A/\\B & R = A-B", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("A", PowerSetType(SetType("X"))),("B", PowerSetType(SetType("X")))]
        _test_typeit(root, env, lst, ["S","T","R"])
        assert isinstance(env.get_type("S"), PowerSetType)
        assert isinstance(env.get_type("S").data, SetType)
        assert env.get_type("S").data.data =="X"
        assert isinstance(env.get_type("T"), PowerSetType)
        assert isinstance(env.get_type("T").data, SetType)
        assert env.get_type("T").data.data =="X"
        assert isinstance(env.get_type("R"), PowerSetType)
        assert isinstance(env.get_type("R").data, SetType)
        assert env.get_type("R").data.data =="X"


    def test_types_simple_cart_prod(self):
        # Build AST
        string_to_file("#PREDICATE S=A*B", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("A", PowerSetType(SetType("X"))),("B", PowerSetType(SetType("X")))]
        _test_typeit(root, env, lst, ["S"])
        assert isinstance(env.get_type("S"), PowerSetType)
        assert isinstance(env.get_type("S").data, CartType)


    def test_types_simple_pow(self):
        # Build AST
        string_to_file("#PREDICATE S=POW(B)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("B", PowerSetType(SetType("X")))]
        _test_typeit(root, env, lst, ["S"])
        assert isinstance(env.get_type("S"), PowerSetType)
        assert isinstance(env.get_type("S").data, PowerSetType)


    def test_types_simple_pow2(self):
        # Build AST
        string_to_file("#PREDICATE S=POW(B) & B=NAT", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["S","B"])
        assert isinstance(env.get_type("S"), PowerSetType)
        assert isinstance(env.get_type("S").data, PowerSetType)
        assert isinstance(env.get_type("B"), PowerSetType)
        assert isinstance(env.get_type("B").data, IntegerType)


    def test_types_simple_subset(self):
        # Build AST
        string_to_file("#PREDICATE S<:B", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("B", PowerSetType(SetType("X")))]
        _test_typeit(root, env, lst, ["S"])
        assert isinstance(env.get_type("S"), PowerSetType)
        assert isinstance(env.get_type("S").data, SetType)
        assert env.get_type("S").data.data == "X"


    def test_types_set_union(self):
        # Build AST
        string_to_file("#PREDICATE R=S\/T & S:POW(B)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("B", PowerSetType(SetType("X")))]
        _test_typeit(root, env, lst, ["S","R","T"])
        assert isinstance(env.get_type("S"), PowerSetType)
        assert isinstance(env.get_type("S").data, SetType)
        assert env.get_type("S").data.data == "X"
        assert isinstance(env.get_type("R"), PowerSetType)
        assert isinstance(env.get_type("R").data, SetType)
        assert env.get_type("R").data.data == "X"
        assert isinstance(env.get_type("T"), PowerSetType)
        assert isinstance(env.get_type("T").data, SetType)
        assert env.get_type("T").data.data == "X"


    def test_types_set_union2(self):
        # Build AST
        string_to_file("#PREDICATE R=S\/T & R:POW(B)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("B", PowerSetType(SetType("X")))]
        _test_typeit(root, env, lst, ["S","R","T"])
        assert isinstance(env.get_type("S"), PowerSetType)
        assert isinstance(env.get_type("S").data, SetType)
        assert env.get_type("S").data.data == "X"
        assert isinstance(env.get_type("R"), PowerSetType)
        assert isinstance(env.get_type("R").data, SetType)
        assert env.get_type("R").data.data == "X"
        assert isinstance(env.get_type("T"), PowerSetType)
        assert isinstance(env.get_type("T").data, SetType)
        assert env.get_type("T").data.data == "X"


    def test_types_set_union3(self):
        # Build AST
        string_to_file("#PREDICATE R=S\/T & T:POW(B)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("B", PowerSetType(SetType("X")))]
        _test_typeit(root, env, lst, ["S","R","T"])
        assert isinstance(env.get_type("S"), PowerSetType)
        assert isinstance(env.get_type("S").data, SetType)
        assert env.get_type("S").data.data == "X"
        assert isinstance(env.get_type("R"), PowerSetType)
        assert isinstance(env.get_type("R").data, SetType)
        assert env.get_type("R").data.data == "X"
        assert isinstance(env.get_type("T"), PowerSetType)
        assert isinstance(env.get_type("T").data, SetType)
        assert env.get_type("T").data.data == "X"


    def test_types_set_union4(self):
        # Build AST
        string_to_file("#PREDICATE T:POW(B) & R=S\/T ", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("B", PowerSetType(SetType("X")))]
        _test_typeit(root, env, lst, ["S","R","T"])
        assert isinstance(env.get_type("S"), PowerSetType)
        assert isinstance(env.get_type("S").data, SetType)
        assert env.get_type("S").data.data == "X"
        assert isinstance(env.get_type("R"), PowerSetType)
        assert isinstance(env.get_type("R").data, SetType)
        assert env.get_type("R").data.data == "X"
        assert isinstance(env.get_type("T"), PowerSetType)
        assert isinstance(env.get_type("T").data, SetType)
        assert env.get_type("T").data.data == "X"


    def test_types_set_union5(self):
        # Build AST
        string_to_file("#PREDICATE R:POW(B) & R=S\/T ", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("B", PowerSetType(SetType("X")))]
        _test_typeit(root, env, lst, ["S","R","T"])
        assert isinstance(env.get_type("S"), PowerSetType)
        assert isinstance(env.get_type("S").data, SetType)
        assert env.get_type("S").data.data == "X"
        assert isinstance(env.get_type("R"), PowerSetType)
        assert isinstance(env.get_type("R").data, SetType)
        assert env.get_type("R").data.data == "X"
        assert isinstance(env.get_type("T"), PowerSetType)
        assert isinstance(env.get_type("T").data, SetType)
        assert env.get_type("T").data.data == "X"


    def test_types_set_union6(self):
        # Build AST
        string_to_file("#PREDICATE S:POW(B) & R=S\/T ", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("B", PowerSetType(SetType("X")))]
        _test_typeit(root, env, lst, ["S","R","T"])
        assert isinstance(env.get_type("S"), PowerSetType)
        assert isinstance(env.get_type("S").data, SetType)
        assert env.get_type("S").data.data == "X"
        assert isinstance(env.get_type("R"), PowerSetType)
        assert isinstance(env.get_type("R").data, SetType)
        assert env.get_type("R").data.data == "X"
        assert isinstance(env.get_type("T"), PowerSetType)
        assert isinstance(env.get_type("T").data, SetType)
        assert env.get_type("T").data.data == "X"


    def test_types_set_power_unify(self):
        # Build AST
        string_to_file("#PREDICATE x:POW(A) & y:POW(B) & POW(A)=B & A<:NAT ", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["A","B","x","y"])
        assert isinstance(env.get_type("x"), PowerSetType)
        assert isinstance(env.get_type("x").data, IntegerType)
        assert isinstance(env.get_type("y"), PowerSetType)
        assert isinstance(env.get_type("y").data, PowerSetType)
        assert isinstance(env.get_type("A"), PowerSetType)
        assert isinstance(env.get_type("A").data, IntegerType)
        assert isinstance(env.get_type("B"), PowerSetType)
        assert isinstance(env.get_type("B").data, PowerSetType)


    def test_types_set_power_unify2(self):
        # Build AST
        string_to_file("#PREDICATE 1:S ", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["S"])
        assert isinstance(env.get_type("S"), PowerSetType)
        assert isinstance(env.get_type("S").data, IntegerType)


    def test_types_set_power_unify3(self):
        # Build AST
        string_to_file("#PREDICATE x:S & x=1", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["S","x"])
        assert isinstance(env.get_type("S"), PowerSetType)
        assert isinstance(env.get_type("S").data, IntegerType)
        assert isinstance(env.get_type("x"), IntegerType)


    def test_types_set_power_unify4(self):
        # Build AST
        string_to_file("#PREDICATE X=S & S:POW(NAT) & y:X", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["S","X","y"])
        assert isinstance(env.get_type("S"), PowerSetType)
        assert isinstance(env.get_type("S").data, IntegerType)
        assert isinstance(env.get_type("X"), PowerSetType)
        assert isinstance(env.get_type("X").data, IntegerType)
        assert isinstance(env.get_type("y"), IntegerType)


    def test_types_set_power_unify5(self):
        # Build AST
        string_to_file("#PREDICATE x:S & S:POW(NAT)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["S","x"])
        assert isinstance(env.get_type("S"), PowerSetType)
        assert isinstance(env.get_type("S").data, IntegerType)
        assert isinstance(env.get_type("x"), IntegerType)


    def test_types_set_power_unify6(self):
        # Build AST
        string_to_file("#PREDICATE x:A & x:B & A=NAT", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["x","A","B"])
        assert isinstance(env.get_type("A"), PowerSetType)
        assert isinstance(env.get_type("A").data, IntegerType)
        assert isinstance(env.get_type("B"), PowerSetType)
        assert isinstance(env.get_type("B").data, IntegerType)
        assert isinstance(env.get_type("x"), IntegerType)


    def test_types_set_power_unify7(self):
        # Build AST
        string_to_file("#PREDICATE x:POW(A) & x:POW(B) & A=NAT", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["x","A","B"])
        assert isinstance(env.get_type("A"), PowerSetType)
        assert isinstance(env.get_type("A").data, IntegerType)
        assert isinstance(env.get_type("B"), PowerSetType)
        assert isinstance(env.get_type("B").data, IntegerType)
        assert isinstance(env.get_type("x"), PowerSetType)
        assert isinstance(env.get_type("x").data, IntegerType)


    def test_types_set_power_unify8(self):
        # Build AST
        string_to_file("#PREDICATE x:POW(A) & A=NAT & x:POW(B)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["x","A","B"])
        assert isinstance(env.get_type("A"), PowerSetType)
        assert isinstance(env.get_type("A").data, IntegerType)
        assert isinstance(env.get_type("B"), PowerSetType)
        assert isinstance(env.get_type("B").data, IntegerType)
        assert isinstance(env.get_type("x"), PowerSetType)
        assert isinstance(env.get_type("x").data, IntegerType)


    def test_types_set_power_unify9(self):
        # Build AST
        string_to_file("#PREDICATE #x.(x:S=>x>=0) & S=NAT", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["S","x"])
        assert isinstance(env.get_type("S"), PowerSetType)
        assert isinstance(env.get_type("S").data, IntegerType)
        assert isinstance(env.get_type("x"), IntegerType)


    def test_types_set_comp_unify(self):
        # Build AST
        string_to_file("#PREDICATE S= {1,a,b}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["S","a","b"])
        assert isinstance(env.get_type("S"), PowerSetType)
        assert isinstance(env.get_type("S").data, IntegerType) 
        assert isinstance(env.get_type("a"), IntegerType)
        assert isinstance(env.get_type("b"), IntegerType)


    def test_types_set_comp_unify2(self):
        # Build AST
        string_to_file("#PREDICATE {a,42,b}=S", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["S","a","b"])
        assert isinstance(env.get_type("S"), PowerSetType)
        assert isinstance(env.get_type("S").data, IntegerType)
        assert isinstance(env.get_type("a"), IntegerType)
        assert isinstance(env.get_type("b"), IntegerType)


    def test_types_set_comp_unify3(self):
        # Build AST
        string_to_file("#PREDICATE a=42 & S={a}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["S","a"])
        assert isinstance(env.get_type("S"), PowerSetType)
        assert isinstance(env.get_type("S").data, IntegerType) 
        assert isinstance(env.get_type("a"), IntegerType)



    def test_types_set_comp_unify4(self):
        # Build AST
        string_to_file("#PREDICATE S={a} & a=42 ", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["S","a"])
        assert isinstance(env.get_type("S"), PowerSetType)
        assert isinstance(env.get_type("S").data, IntegerType) 
        assert isinstance(env.get_type("a"), IntegerType)


    def test_types_set_sub_unify(self):
        # Build AST
        string_to_file("#PREDICATE S=A-B & A=NAT & B=NAT", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["S","A","B"])
        assert isinstance(env.get_type("S"), PowerSetType)
        assert isinstance(env.get_type("S").data, IntegerType) 
        assert isinstance(env.get_type("A"), PowerSetType)
        assert isinstance(env.get_type("B"), PowerSetType)


    def test_types_set_cart_unify(self):
        # Build AST
        string_to_file("#PREDICATE S=A*B & A=NAT & B=NAT", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["S","A","B"])
        assert isinstance(env.get_type("S"), PowerSetType)
        assert isinstance(env.get_type("S").data, CartType) 
        assert isinstance(env.get_type("A").data, IntegerType)
        assert isinstance(env.get_type("B").data, IntegerType)


    def test_types_set_cart_unify2(self):
        # Build AST
        string_to_file("#PREDICATE NAT*NAT=A*B", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["A","B"])
        assert isinstance(env.get_type("A").data, IntegerType)
        assert isinstance(env.get_type("B").data, IntegerType)
        assert isinstance(env.get_type("A"), PowerSetType)
        assert isinstance(env.get_type("B"), PowerSetType)


    def test_types_set_cart_unify3(self):
        # Build AST
        string_to_file("#PREDICATE NAT*B=A*NAT", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["A","B"])
        assert isinstance(env.get_type("A"), PowerSetType)
        assert isinstance(env.get_type("B"), PowerSetType)
        assert isinstance(env.get_type("A").data, IntegerType)
        assert isinstance(env.get_type("B").data, IntegerType)


    def test_types_set_cart_unify4(self):
        # Build AST
        string_to_file("#PREDICATE NAT*B=A*POW(NAT)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["A","B"])
        assert isinstance(env.get_type("A"), PowerSetType)
        assert isinstance(env.get_type("B"), PowerSetType)
        assert isinstance(env.get_type("A").data, IntegerType)
        assert isinstance(env.get_type("B").data, PowerSetType)
        assert isinstance(env.get_type("B").data.data, IntegerType)


    def test_types_set_cart_tuple(self):
        # Build AST
        string_to_file("#PREDICATE x=(1,2)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["x"])
        assert isinstance(env.get_type("x"), CartType)


    def test_types_set_cart_tuple2(self):
        # Build AST:
        string_to_file("#PREDICATE x=(1,2,41) & y={(0,0,41),(1,0,41),(0,1,41),(1,1,41)}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["x","y"])
        assert isinstance(env.get_type("x"), CartType)
        assert isinstance(env.get_type("y"), PowerSetType)
        assert isinstance(env.get_type("y").data, CartType)
        assert isinstance(env.get_type("y").data.data[0].data, CartType)
        assert isinstance(env.get_type("y").data.data[1].data, IntegerType)


    def test_types_set_gen_union(self):
        # Build AST:
        string_to_file("#PREDICATE U:POW(POW(S)) & u=union(U)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("S")))]
        _test_typeit(root, env, lst, ["U","u"])
        assert isinstance(env.get_type("U"), PowerSetType)
        assert isinstance(env.get_type("U").data, PowerSetType)
        assert isinstance(env.get_type("U").data.data, SetType)
        assert isinstance(env.get_type("u"), PowerSetType)
        assert isinstance(env.get_type("u").data, SetType)


    def test_types_set_gen_inter(self):
        # Build AST:
        string_to_file("#PREDICATE U:POW(POW(S)) & u=inter(U)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("S")))]
        _test_typeit(root, env, lst, ["U","u"])
        assert isinstance(env.get_type("U"), PowerSetType)
        assert isinstance(env.get_type("U").data, PowerSetType)
        assert isinstance(env.get_type("U").data.data, SetType)
        assert isinstance(env.get_type("u"), PowerSetType)
        assert isinstance(env.get_type("u").data, SetType)


    def test_types_string(self):
        # Build AST
        string_to_file("#PREDICATE s=\"HalloWelt\"", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["s"])
        assert isinstance(env.get_type("s"), StringType)
    

    def test_types_string2(self):
        # Build AST
        string_to_file("#PREDICATE  s= [\"VIA_1\",\"VIA_2\",\"VIA_3\",\"VIA_4\"]", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string    

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["s"])
        assert isinstance(env.get_type("s"), PowerSetType)
        assert isinstance(env.get_type("s").data, CartType)
        assert isinstance(env.get_type("s").data.data[0].data, IntegerType)
        assert isinstance(env.get_type("s").data.data[1].data, StringType)


    def test_types_bool(self):
        # Build AST
        string_to_file("#PREDICATE A:BOOL & B:BOOL & C:BOOL & (A=TRUE <=> (B=FALSE or C=FALSE)) & (B=TRUE <=> A=TRUE)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["A","B","C"])
        assert isinstance(env.get_type("A"), BoolType)
        assert isinstance(env.get_type("B"), BoolType)
        assert isinstance(env.get_type("C"), BoolType)


    def test_types_bool2(self):
        # Build AST
        string_to_file("#PREDICATE A=bool(1<2)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["A"])
        assert isinstance(env.get_type("A"), BoolType)
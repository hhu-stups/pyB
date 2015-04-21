# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from environment import Environment
from util import type_with_known_types, get_type_by_name
from helpers import file_to_AST_str, string_to_file
from parsing import str_ast_to_python_ast

from config import USE_COSTUM_FROZENSET
if USE_COSTUM_FROZENSET:
     from rpython_b_objmodel import frozenset

file_name = "input.txt"

class TestTypesSets():
    def test_types_card(self):
        # Build AST
        string_to_file("#PREDICATE card(S)=3", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        env.add_ids_to_frame(["S"])
        env.set_value("S", frozenset(["Huey", "Dewey", "Louie"]))
        lst = [("S", PowerSetType(SetType("X")))]
        type_with_known_types(root, env, lst, [])


    def test_types_simple_set(self):
        # Build AST
        string_to_file("#PREDICATE ID={aa,bb}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        env.add_ids_to_frame(["aa","bb","ID"])
        env.set_value("aa", "aa")
        env.set_value("bb", "bb")
        env.set_value("ID", frozenset(["aa", "bb"]))
        lst = [("aa", SetType("X")),("bb", SetType("X"))]
        type_with_known_types(root, env, lst, ["ID"])
        assert isinstance(get_type_by_name(env, "ID"), PowerSetType)
        assert isinstance(get_type_by_name(env, "ID").data, SetType)
        assert get_type_by_name(env, "ID").data.name =="X"


    def test_types_simple_set_empty(self):
        # Build AST
        string_to_file("#PREDICATE ID={} & ID<:NAT", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["ID"])
        assert isinstance(get_type_by_name(env, "ID"), PowerSetType)


    def test_types_simple_set_com(self):
        # Build AST
        string_to_file("#PREDICATE ID={x|x<10}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["ID"])
        assert isinstance(get_type_by_name(env, "ID"), PowerSetType)
        assert isinstance(get_type_by_name(env, "x"), IntegerType)


    def test_types_simple_set_com2(self):
        # Build AST
        string_to_file("#PREDICATE S={a,b} & ID={x,y|x<10 & y:S}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("a", SetType("X")),("b", SetType("X"))]
        type_with_known_types(root, env, lst, ["S","ID"]) 
        assert isinstance(get_type_by_name(env, "S"), PowerSetType)
        assert isinstance(get_type_by_name(env, "ID"), PowerSetType)
        assert isinstance(get_type_by_name(env, "x"), IntegerType)
        assert isinstance(get_type_by_name(env, "y"), SetType)
        assert get_type_by_name(env, "y").name =="X"


    def test_types_simple_set_union(self):
        # Build AST
        string_to_file("#PREDICATE S=A\/B & T=A/\\B & R = A-B", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("A", PowerSetType(SetType("X"))),("B", PowerSetType(SetType("X")))]
        type_with_known_types(root, env, lst, ["S","T","R"])
        assert isinstance(get_type_by_name(env, "S"), PowerSetType)
        assert isinstance(get_type_by_name(env, "S").data, SetType)
        assert get_type_by_name(env, "S").data.name =="X"
        assert isinstance(get_type_by_name(env, "T"), PowerSetType)
        assert isinstance(get_type_by_name(env, "T").data, SetType)
        assert get_type_by_name(env, "T").data.name =="X"
        assert isinstance(get_type_by_name(env, "R"), PowerSetType)
        assert isinstance(get_type_by_name(env, "R").data, SetType)
        assert get_type_by_name(env, "R").data.name =="X"


    def test_types_simple_cart_prod(self):
        # Build AST
        string_to_file("#PREDICATE S=A*B", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("A", PowerSetType(SetType("X"))),("B", PowerSetType(SetType("X")))]
        type_with_known_types(root, env, lst, ["S"])
        assert isinstance(get_type_by_name(env, "S"), PowerSetType)
        assert isinstance(get_type_by_name(env, "S").data, CartType)


    def test_types_simple_pow(self):
        # Build AST
        string_to_file("#PREDICATE S=POW(B)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("B", PowerSetType(SetType("X")))]
        type_with_known_types(root, env, lst, ["S"])
        assert isinstance(get_type_by_name(env, "S"), PowerSetType)
        assert isinstance(get_type_by_name(env, "S").data, PowerSetType)


    def test_types_simple_pow2(self):
        # Build AST
        string_to_file("#PREDICATE S=POW(B) & B=NAT", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["S","B"])
        assert isinstance(get_type_by_name(env, "S"), PowerSetType)
        assert isinstance(get_type_by_name(env, "S").data, PowerSetType)
        assert isinstance(get_type_by_name(env, "B"), PowerSetType)
        assert isinstance(get_type_by_name(env, "B").data, IntegerType)


    def test_types_simple_subset(self):
        # Build AST
        string_to_file("#PREDICATE S<:B", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("B", PowerSetType(SetType("X")))]
        type_with_known_types(root, env, lst, ["S"])
        assert isinstance(get_type_by_name(env, "S"), PowerSetType)
        assert isinstance(get_type_by_name(env, "S").data, SetType)
        assert get_type_by_name(env, "S").data.name == "X"


    def test_types_set_union(self):
        # Build AST
        string_to_file("#PREDICATE R=S\/T & S:POW(B)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("B", PowerSetType(SetType("X")))]
        type_with_known_types(root, env, lst, ["S","R","T"])
        assert isinstance(get_type_by_name(env, "S"), PowerSetType)
        assert isinstance(get_type_by_name(env, "S").data, SetType)
        assert get_type_by_name(env, "S").data.name == "X"
        assert isinstance(get_type_by_name(env, "R"), PowerSetType)
        assert isinstance(get_type_by_name(env, "R").data, SetType)
        assert get_type_by_name(env, "R").data.name == "X"
        assert isinstance(get_type_by_name(env, "T"), PowerSetType)
        assert isinstance(get_type_by_name(env, "T").data, SetType)
        assert get_type_by_name(env, "T").data.name == "X"


    def test_types_set_union2(self):
        # Build AST
        string_to_file("#PREDICATE R=S\/T & R:POW(B)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("B", PowerSetType(SetType("X")))]
        type_with_known_types(root, env, lst, ["S","R","T"])
        assert isinstance(get_type_by_name(env, "S"), PowerSetType)
        assert isinstance(get_type_by_name(env, "S").data, SetType)
        assert get_type_by_name(env, "S").data.name == "X"
        assert isinstance(get_type_by_name(env, "R"), PowerSetType)
        assert isinstance(get_type_by_name(env, "R").data, SetType)
        assert get_type_by_name(env, "R").data.name == "X"
        assert isinstance(get_type_by_name(env, "T"), PowerSetType)
        assert isinstance(get_type_by_name(env, "T").data, SetType)
        assert get_type_by_name(env, "T").data.name == "X"


    def test_types_set_union3(self):
        # Build AST
        string_to_file("#PREDICATE R=S\/T & T:POW(B)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("B", PowerSetType(SetType("X")))]
        type_with_known_types(root, env, lst, ["S","R","T"])
        assert isinstance(get_type_by_name(env, "S"), PowerSetType)
        assert isinstance(get_type_by_name(env, "S").data, SetType)
        assert get_type_by_name(env, "S").data.name == "X"
        assert isinstance(get_type_by_name(env, "R"), PowerSetType)
        assert isinstance(get_type_by_name(env, "R").data, SetType)
        assert get_type_by_name(env, "R").data.name == "X"
        assert isinstance(get_type_by_name(env, "T"), PowerSetType)
        assert isinstance(get_type_by_name(env, "T").data, SetType)
        assert get_type_by_name(env, "T").data.name == "X"


    def test_types_set_union4(self):
        # Build AST
        string_to_file("#PREDICATE T:POW(B) & R=S\/T ", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("B", PowerSetType(SetType("X")))]
        type_with_known_types(root, env, lst, ["S","R","T"])
        assert isinstance(get_type_by_name(env, "S"), PowerSetType)
        assert isinstance(get_type_by_name(env, "S").data, SetType)
        assert get_type_by_name(env, "S").data.name == "X"
        assert isinstance(get_type_by_name(env, "R"), PowerSetType)
        assert isinstance(get_type_by_name(env, "R").data, SetType)
        assert get_type_by_name(env, "R").data.name == "X"
        assert isinstance(get_type_by_name(env, "T"), PowerSetType)
        assert isinstance(get_type_by_name(env, "T").data, SetType)
        assert get_type_by_name(env, "T").data.name == "X"


    def test_types_set_union5(self):
        # Build AST
        string_to_file("#PREDICATE R:POW(B) & R=S\/T ", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("B", PowerSetType(SetType("X")))]
        type_with_known_types(root, env, lst, ["S","R","T"])
        assert isinstance(get_type_by_name(env, "S"), PowerSetType)
        assert isinstance(get_type_by_name(env, "S").data, SetType)
        assert get_type_by_name(env, "S").data.name == "X"
        assert isinstance(get_type_by_name(env, "R"), PowerSetType)
        assert isinstance(get_type_by_name(env, "R").data, SetType)
        assert get_type_by_name(env, "R").data.name == "X"
        assert isinstance(get_type_by_name(env, "T"), PowerSetType)
        assert isinstance(get_type_by_name(env, "T").data, SetType)
        assert get_type_by_name(env, "T").data.name == "X"


    def test_types_set_union6(self):
        # Build AST
        string_to_file("#PREDICATE S:POW(B) & R=S\/T ", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("B", PowerSetType(SetType("X")))]
        type_with_known_types(root, env, lst, ["S","R","T"])
        assert isinstance(get_type_by_name(env, "S"), PowerSetType)
        assert isinstance(get_type_by_name(env, "S").data, SetType)
        assert get_type_by_name(env, "S").data.name == "X"
        assert isinstance(get_type_by_name(env, "R"), PowerSetType)
        assert isinstance(get_type_by_name(env, "R").data, SetType)
        assert get_type_by_name(env, "R").data.name == "X"
        assert isinstance(get_type_by_name(env, "T"), PowerSetType)
        assert isinstance(get_type_by_name(env, "T").data, SetType)
        assert get_type_by_name(env, "T").data.name == "X"


    def test_types_set_power_unify(self):
        # Build AST
        string_to_file("#PREDICATE x:POW(A) & y:POW(B) & POW(A)=B & A<:NAT ", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["A","B","x","y"])
        assert isinstance(get_type_by_name(env, "x"), PowerSetType)
        assert isinstance(get_type_by_name(env, "x").data, IntegerType)
        assert isinstance(get_type_by_name(env, "y"), PowerSetType)
        assert isinstance(get_type_by_name(env, "y").data, PowerSetType)
        assert isinstance(get_type_by_name(env, "A"), PowerSetType)
        assert isinstance(get_type_by_name(env, "A").data, IntegerType)
        assert isinstance(get_type_by_name(env, "B"), PowerSetType)
        assert isinstance(get_type_by_name(env, "B").data, PowerSetType)


    def test_types_set_power_unify2(self):
        # Build AST
        string_to_file("#PREDICATE 1:S ", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["S"])
        assert isinstance(get_type_by_name(env, "S"), PowerSetType)
        assert isinstance(get_type_by_name(env, "S").data, IntegerType)


    def test_types_set_power_unify3(self):
        # Build AST
        string_to_file("#PREDICATE x:S & x=1", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["S","x"])
        assert isinstance(get_type_by_name(env, "S"), PowerSetType)
        assert isinstance(get_type_by_name(env, "S").data, IntegerType)
        assert isinstance(get_type_by_name(env, "x"), IntegerType)


    def test_types_set_power_unify4(self):
        # Build AST
        string_to_file("#PREDICATE X=S & S:POW(NAT) & y:X", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["S","X","y"])
        assert isinstance(get_type_by_name(env, "S"), PowerSetType)
        assert isinstance(get_type_by_name(env, "S").data, IntegerType)
        assert isinstance(get_type_by_name(env, "X"), PowerSetType)
        assert isinstance(get_type_by_name(env, "X").data, IntegerType)
        assert isinstance(get_type_by_name(env, "y"), IntegerType)


    def test_types_set_power_unify5(self):
        # Build AST
        string_to_file("#PREDICATE x:S & S:POW(NAT)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["S","x"])
        assert isinstance(get_type_by_name(env, "S"), PowerSetType)
        assert isinstance(get_type_by_name(env, "S").data, IntegerType)
        assert isinstance(get_type_by_name(env, "x"), IntegerType)


    def test_types_set_power_unify6(self):
        # Build AST
        string_to_file("#PREDICATE x:A & x:B & A=NAT", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["x","A","B"])
        assert isinstance(get_type_by_name(env, "A"), PowerSetType)
        assert isinstance(get_type_by_name(env, "A").data, IntegerType)
        assert isinstance(get_type_by_name(env, "B"), PowerSetType)
        assert isinstance(get_type_by_name(env, "B").data, IntegerType)
        assert isinstance(get_type_by_name(env, "x"), IntegerType)


    def test_types_set_power_unify7(self):
        # Build AST
        string_to_file("#PREDICATE x:POW(A) & x:POW(B) & A=NAT", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["x","A","B"])
        assert isinstance(get_type_by_name(env, "A"), PowerSetType)
        assert isinstance(get_type_by_name(env, "A").data, IntegerType)
        assert isinstance(get_type_by_name(env, "B"), PowerSetType)
        assert isinstance(get_type_by_name(env, "B").data, IntegerType)
        assert isinstance(get_type_by_name(env, "x"), PowerSetType)
        assert isinstance(get_type_by_name(env, "x").data, IntegerType)


    def test_types_set_power_unify8(self):
        # Build AST
        string_to_file("#PREDICATE x:POW(A) & A=NAT & x:POW(B)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["x","A","B"])
        assert isinstance(get_type_by_name(env, "A"), PowerSetType)
        assert isinstance(get_type_by_name(env, "A").data, IntegerType)
        assert isinstance(get_type_by_name(env, "B"), PowerSetType)
        assert isinstance(get_type_by_name(env, "B").data, IntegerType)
        assert isinstance(get_type_by_name(env, "x"), PowerSetType)
        assert isinstance(get_type_by_name(env, "x").data, IntegerType)


    def test_types_set_power_unify9(self):
        # Build AST
        string_to_file("#PREDICATE #x.(x:S=>x>=0) & S=NAT", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["S","x"])
        assert isinstance(get_type_by_name(env, "S"), PowerSetType)
        assert isinstance(get_type_by_name(env, "S").data, IntegerType)
        assert isinstance(get_type_by_name(env, "x"), IntegerType)


    def test_types_set_comp_unify(self):
        # Build AST
        string_to_file("#PREDICATE S= {1,a,b}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["S","a","b"])
        assert isinstance(get_type_by_name(env, "S"), PowerSetType)
        assert isinstance(get_type_by_name(env, "S").data, IntegerType) 
        assert isinstance(get_type_by_name(env, "a"), IntegerType)
        assert isinstance(get_type_by_name(env, "b"), IntegerType)


    def test_types_set_comp_unify2(self):
        # Build AST
        string_to_file("#PREDICATE {a,42,b}=S", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["S","a","b"])
        assert isinstance(get_type_by_name(env, "S"), PowerSetType)
        assert isinstance(get_type_by_name(env, "S").data, IntegerType)
        assert isinstance(get_type_by_name(env, "a"), IntegerType)
        assert isinstance(get_type_by_name(env, "b"), IntegerType)


    def test_types_set_comp_unify3(self):
        # Build AST
        string_to_file("#PREDICATE a=42 & S={a}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["S","a"])
        assert isinstance(get_type_by_name(env, "S"), PowerSetType)
        assert isinstance(get_type_by_name(env, "S").data, IntegerType) 
        assert isinstance(get_type_by_name(env, "a"), IntegerType)



    def test_types_set_comp_unify4(self):
        # Build AST
        string_to_file("#PREDICATE S={a} & a=42 ", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["S","a"])
        assert isinstance(get_type_by_name(env, "S"), PowerSetType)
        assert isinstance(get_type_by_name(env, "S").data, IntegerType) 
        assert isinstance(get_type_by_name(env, "a"), IntegerType)


    def test_types_set_sub_unify(self):
        # Build AST
        string_to_file("#PREDICATE S=A-B & A=NAT & B=NAT", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["S","A","B"])
        assert isinstance(get_type_by_name(env, "S"), PowerSetType)
        assert isinstance(get_type_by_name(env, "S").data, IntegerType) 
        assert isinstance(get_type_by_name(env, "A"), PowerSetType)
        assert isinstance(get_type_by_name(env, "B"), PowerSetType)


    def test_types_set_cart_unify(self):
        # Build AST
        string_to_file("#PREDICATE S=A*B & A=NAT & B=NAT", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["S","A","B"])
        assert isinstance(get_type_by_name(env, "S"), PowerSetType)
        assert isinstance(get_type_by_name(env, "S").data, CartType) 
        assert isinstance(get_type_by_name(env, "A").data, IntegerType)
        assert isinstance(get_type_by_name(env, "B").data, IntegerType)


    def test_types_set_cart_unify2(self):
        # Build AST
        string_to_file("#PREDICATE NAT*NAT=A*B", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["A","B"])
        assert isinstance(get_type_by_name(env, "A").data, IntegerType)
        assert isinstance(get_type_by_name(env, "B").data, IntegerType)
        assert isinstance(get_type_by_name(env, "A"), PowerSetType)
        assert isinstance(get_type_by_name(env, "B"), PowerSetType)


    def test_types_set_cart_unify3(self):
        # Build AST
        string_to_file("#PREDICATE NAT*B=A*NAT", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["A","B"])
        assert isinstance(get_type_by_name(env, "A"), PowerSetType)
        assert isinstance(get_type_by_name(env, "B"), PowerSetType)
        assert isinstance(get_type_by_name(env, "A").data, IntegerType)
        assert isinstance(get_type_by_name(env, "B").data, IntegerType)


    def test_types_set_cart_unify4(self):
        # Build AST
        string_to_file("#PREDICATE NAT*B=A*POW(NAT)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["A","B"])
        assert isinstance(get_type_by_name(env, "A"), PowerSetType)
        assert isinstance(get_type_by_name(env, "B"), PowerSetType)
        assert isinstance(get_type_by_name(env, "A").data, IntegerType)
        assert isinstance(get_type_by_name(env, "B").data, PowerSetType)
        assert isinstance(get_type_by_name(env, "B").data.data, IntegerType)


    def test_types_set_cart_tuple(self):
        # Build AST
        string_to_file("#PREDICATE x=(1,2)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["x"])
        assert isinstance(get_type_by_name(env, "x"), CartType)


    def test_types_set_cart_tuple2(self):
        # Build AST:
        string_to_file("#PREDICATE x=(1,2,41) & y={(0,0,41),(1,0,41),(0,1,41),(1,1,41)}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["x","y"])
        assert isinstance(get_type_by_name(env, "x"), CartType)
        assert isinstance(get_type_by_name(env, "y"), PowerSetType)
        assert isinstance(get_type_by_name(env, "y").data, CartType)
        assert isinstance(get_type_by_name(env, "y").data.data[0].data, CartType)
        assert isinstance(get_type_by_name(env, "y").data.data[1].data, IntegerType)


    def test_types_set_gen_union(self):
        # Build AST:
        string_to_file("#PREDICATE U:POW(POW(S)) & u=union(U)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("S")))]
        type_with_known_types(root, env, lst, ["U","u"])
        assert isinstance(get_type_by_name(env, "U"), PowerSetType)
        assert isinstance(get_type_by_name(env, "U").data, PowerSetType)
        assert isinstance(get_type_by_name(env, "U").data.data, SetType)
        assert isinstance(get_type_by_name(env, "u"), PowerSetType)
        assert isinstance(get_type_by_name(env, "u").data, SetType)


    def test_types_set_gen_inter(self):
        # Build AST:
        string_to_file("#PREDICATE U:POW(POW(S)) & u=inter(U)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("S")))]
        type_with_known_types(root, env, lst, ["U","u"])
        assert isinstance(get_type_by_name(env, "U"), PowerSetType)
        assert isinstance(get_type_by_name(env, "U").data, PowerSetType)
        assert isinstance(get_type_by_name(env, "U").data.data, SetType)
        assert isinstance(get_type_by_name(env, "u"), PowerSetType)
        assert isinstance(get_type_by_name(env, "u").data, SetType)


    def test_types_string(self):
        # Build AST
        string_to_file("#PREDICATE s=\"HalloWelt\"", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["s"])
        assert isinstance(get_type_by_name(env, "s"), StringType)
    

    def test_types_string2(self):
        # Build AST
        string_to_file("#PREDICATE  s= [\"VIA_1\",\"VIA_2\",\"VIA_3\",\"VIA_4\"]", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)    

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["s"])
        assert isinstance(get_type_by_name(env, "s"), PowerSetType)
        assert isinstance(get_type_by_name(env, "s").data, CartType)
        assert isinstance(get_type_by_name(env, "s").data.data[0].data, IntegerType)
        assert isinstance(get_type_by_name(env, "s").data.data[1].data, StringType)


    def test_types_bool(self):
        # Build AST
        string_to_file("#PREDICATE A:BOOL & B:BOOL & C:BOOL & (A=TRUE <=> (B=FALSE or C=FALSE)) & (B=TRUE <=> A=TRUE)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["A","B","C"])
        assert isinstance(get_type_by_name(env, "A"), BoolType)
        assert isinstance(get_type_by_name(env, "B"), BoolType)
        assert isinstance(get_type_by_name(env, "C"), BoolType)


    def test_types_bool2(self):
        # Build AST
        string_to_file("#PREDICATE A=bool(1<2)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["A"])
        assert isinstance(get_type_by_name(env, "A"), BoolType)
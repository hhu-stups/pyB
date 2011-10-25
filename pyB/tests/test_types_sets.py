# -*- coding: utf-8 -*-
from ast_nodes import *
from interp import Environment
from typing import _test_typeit, IntegerType, PowerSetType, SetType, CartType
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
        env.set_value("S", set(["Huey", "Dewey", "Louie"]))
        lst = [("S", SetType("X"))]
        _test_typeit(root, env, lst, [])


    def test_types_simple_set(self):
        # Build AST
        string_to_file("#PREDICATE ID={aa,bb}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.set_value("aa", "aa")
        env.set_value("bb", "bb")
        env.set_value("ID", set(["aa", "bb"]))
        lst = [("aa", SetType("X")),("bb", SetType("X"))]
        _test_typeit(root, env, lst, ["ID"])
        assert isinstance(env.get_type("ID"), PowerSetType)
        assert isinstance(env.get_type("ID").data, SetType)
        assert env.get_type("ID").data.data =="ID"


    def test_types_simple_set_empty(self):
        # Build AST
        string_to_file("#PREDICATE ID={}", file_name)
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
        assert env.get_type("y").data =="S"


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
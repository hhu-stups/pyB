# -*- coding: utf-8 -*-
from ast_nodes import *
from interp import Environment
from typing import typeit, IntegerType, PowerSetType, SetType, CartType
from helpers import file_to_AST_str, string_to_file

file_name = "input.txt"

class TestTypesRelations():
    def test_types_relation(self):
        # Build AST
        string_to_file("#PREDICATE r=S<->T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["S"] = PowerSetType(SetType("X"))
        env.variable_type["T"] = PowerSetType(SetType("X"))
        typeit(root, env)
        assert isinstance(env.variable_type["r"], PowerSetType)
        assert isinstance(env.variable_type["r"].data, PowerSetType)
        assert isinstance(env.variable_type["r"].data.data, CartType)
        assert isinstance(env.variable_type["r"].data.data.data[0], SetType)
        assert isinstance(env.variable_type["r"].data.data.data[1], SetType)


    def test_types_domain(self):
        # Build AST
        string_to_file("#PREDICATE r:S<->T & x:dom(r)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["S"] = PowerSetType(SetType("X"))
        env.variable_type["T"] = PowerSetType(SetType("Y"))
        typeit(root, env)
        assert isinstance(env.variable_type["x"], SetType)
        assert env.variable_type["x"].data == "X"


    def test_types_range(self):
        # Build AST
        string_to_file("#PREDICATE r:S<->T & x:ran(r)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["S"] = PowerSetType(SetType("X"))
        env.variable_type["T"] = PowerSetType(SetType("Y"))
        typeit(root, env)
        assert isinstance(env.variable_type["x"], SetType)
        assert env.variable_type["x"].data == "Y"


    def test_types_fwd_comp(self):
        # Build AST
        string_to_file("#PREDICATE r0:S<->T & r1:T<->S & x:ran(r1;r0)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["S"] = PowerSetType(SetType("X"))
        env.variable_type["T"] = PowerSetType(SetType("Y"))
        typeit(root, env)
        assert isinstance(env.variable_type["x"], SetType)
        assert env.variable_type["x"].data == "X"


    def test_types_simple_identity(self):
        # Build AST
        string_to_file("#PREDICATE S=id(B)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["B"] = PowerSetType(SetType("X"))
        typeit(root, env)
        assert isinstance(env.variable_type["S"], PowerSetType)
        assert isinstance(env.variable_type["S"].data, PowerSetType)
        assert isinstance(env.variable_type["S"].data.data, CartType)
        assert isinstance(env.variable_type["S"].data.data.data[0], SetType)
        assert isinstance(env.variable_type["S"].data.data.data[1], SetType)


    def test_types_simple_sub_res(self):
        # Build AST
        string_to_file("#PREDICATE r:A<->B & v=S <| r", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["S"] = PowerSetType(SetType("X"))
        env.variable_type["A"] = PowerSetType(SetType("X"))
        env.variable_type["B"] = PowerSetType(SetType("Y"))
        typeit(root, env)
        assert isinstance(env.variable_type["v"], PowerSetType)
        assert isinstance(env.variable_type["v"].data, CartType)


    def test_types_simple_rev(self):
        # Build AST
        string_to_file("#PREDICATE r:A<->B & f = r~ & x:dom(f)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["A"] = PowerSetType(SetType("X"))
        env.variable_type["B"] = PowerSetType(SetType("Y"))
        typeit(root, env)
        assert isinstance(env.variable_type["x"], SetType)
        assert env.variable_type["x"].data =="Y"


    def test_types_simple_image(self):
        # Build AST
        string_to_file("#PREDICATE r:A<->B & S<:A & x:r[S]", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["A"] = PowerSetType(SetType("X"))
        env.variable_type["B"] = PowerSetType(SetType("Y"))
        typeit(root, env)
        assert isinstance(env.variable_type["S"], PowerSetType)
        assert isinstance(env.variable_type["S"].data, SetType)
        assert env.variable_type["S"].data.data =="X"
        assert isinstance(env.variable_type["x"], SetType)
        assert env.variable_type["x"].data == "Y"


    def test_types_simple_overwrite(self):
        # Build AST
        string_to_file("#PREDICATE r1:A<->B & r2:A<->B & r3=r1<+r2", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["A"] = PowerSetType(SetType("X"))
        env.variable_type["B"] = PowerSetType(SetType("Y"))
        typeit(root, env)
        assert isinstance(env.variable_type["r3"], PowerSetType)
        assert isinstance(env.variable_type["r3"].data, CartType)
        assert env.variable_type["r3"].data.data[0].data == "X"
        assert env.variable_type["r3"].data.data[1].data == "Y"
        assert not env.variable_type["r1"]=="r1"
        assert not env.variable_type["r2"]=="r2"


    def test_types_simple_parprod(self):
        # Build AST
        string_to_file("#PREDICATE r1:A<->B & r2:C<->D & r3=(r1 || r2)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["A"] = PowerSetType(SetType("X"))
        env.variable_type["B"] = PowerSetType(SetType("Y"))
        env.variable_type["C"] = PowerSetType(SetType("M"))
        env.variable_type["D"] = PowerSetType(SetType("N"))
        typeit(root, env)
        assert isinstance(env.variable_type["r3"], PowerSetType)
        assert isinstance(env.variable_type["r3"].data, CartType)
        assert isinstance(env.variable_type["r3"].data.data[0], CartType)
        assert isinstance(env.variable_type["r3"].data.data[1], CartType)
        x = env.variable_type["r3"].data.data[0].data[0]
        y = env.variable_type["r3"].data.data[0].data[1]
        m = env.variable_type["r3"].data.data[1].data[0]
        n = env.variable_type["r3"].data.data[1].data[1]
        assert isinstance(x, SetType)
        assert isinstance(m, SetType)
        assert isinstance(y, SetType)
        assert isinstance(n, SetType)
        assert x.data == "X"
        assert y.data == "M"
        assert m.data == "Y"
        assert n.data == "N"


    def test_types_simple_dirprod(self):
        # Build AST
        string_to_file("#PREDICATE r1:A<->B & r2:C<->D & r3=r1 >< r2", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["A"] = PowerSetType(SetType("X"))
        env.variable_type["B"] = PowerSetType(SetType("Y"))
        env.variable_type["C"] = PowerSetType(SetType("X"))
        env.variable_type["D"] = PowerSetType(SetType("Z"))
        typeit(root, env)
        assert isinstance(env.variable_type["r3"], PowerSetType)
        assert isinstance(env.variable_type["r3"].data, CartType)
        x = env.variable_type["r3"].data.data[0]
        y = env.variable_type["r3"].data.data[1].data[0]
        z = env.variable_type["r3"].data.data[1].data[1]
        assert x.data == "X"
        assert y.data == "Y"
        assert z.data == "Z"
        assert isinstance(x, SetType)
        assert isinstance(y, SetType)
        assert isinstance(z, SetType)


    def test_types_simple_proj1(self):
        # Build AST
        string_to_file("#PREDICATE r=prj1(A,B)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["A"] = PowerSetType(SetType("X"))
        env.variable_type["B"] = PowerSetType(SetType("Y"))
        typeit(root, env)
        assert isinstance(env.variable_type["r"], PowerSetType)
        assert isinstance(env.variable_type["r"].data, CartType)
        x = env.variable_type["r"].data.data[0].data[0]
        y = env.variable_type["r"].data.data[0].data[1]
        z = env.variable_type["r"].data.data[1]
        assert isinstance(x, SetType)
        assert isinstance(y, SetType)
        assert isinstance(z, SetType)
        assert x.data == "X"
        assert y.data == "Y"
        assert z.data == "X"


    def test_types_simple_proj2(self):
        # Build AST
        string_to_file("#PREDICATE r=prj2(A,B)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.variable_type["A"] = PowerSetType(SetType("X"))
        env.variable_type["B"] = PowerSetType(SetType("Y"))
        typeit(root, env)
        assert isinstance(env.variable_type["r"], PowerSetType)
        assert isinstance(env.variable_type["r"].data, CartType)
        x = env.variable_type["r"].data.data[0].data[0]
        y = env.variable_type["r"].data.data[0].data[1]
        z = env.variable_type["r"].data.data[1]
        assert isinstance(x, SetType)
        assert isinstance(y, SetType)
        assert isinstance(z, SetType)
        assert x.data == "X"
        assert y.data == "Y"
        assert z.data == "Y"
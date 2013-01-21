# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from environment import Environment
from typing import _test_typeit
from helpers import file_to_AST_str, string_to_file

file_name = "input.txt"

class TestTypesFunctions():
    def test_types_par_function(self):
        # Build AST
        string_to_file("#PREDICATE r:S+->T", file_name)
        ast_string = file_to_AST_str(file_name)
        self.type_check_function(ast_string)


    def test_types_tot_function(self):
        # Build AST
        string_to_file("#PREDICATE r:S-->T", file_name)
        ast_string = file_to_AST_str(file_name)
        self.type_check_function(ast_string)


    def test_types_par_inj_function(self):
        # Build AST
        string_to_file("#PREDICATE r:S>+>T", file_name)
        ast_string = file_to_AST_str(file_name)
        self.type_check_function(ast_string)


    def test_types_tot_inj_function(self):
        # Build AST
        string_to_file("#PREDICATE r:S>->T", file_name)
        ast_string = file_to_AST_str(file_name)
        self.type_check_function(ast_string)


    def test_types_par_sur_function(self):
        # Build AST
        string_to_file("#PREDICATE r:S+->>T", file_name)
        ast_string = file_to_AST_str(file_name)
        self.type_check_function(ast_string)


    def test_types_tot_sur_function(self):
        # Build AST
        string_to_file("#PREDICATE r:S-->>T", file_name)
        ast_string = file_to_AST_str(file_name)
        self.type_check_function(ast_string)


    def test_types_bij_function(self):
        # Build AST
        string_to_file("#PREDICATE r:S>->>T", file_name)
        ast_string = file_to_AST_str(file_name)
        self.type_check_function(ast_string)


    def test_types_part_bij_function(self):
        # Build AST
        string_to_file("#PREDICATE r:S>+>>T", file_name)
        ast_string = file_to_AST_str(file_name)
        self.type_check_function(ast_string)


    def test_types_function_app(self):
        # Build AST
        string_to_file("#PREDICATE f:S+->T & y=f(x)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("x", SetType("X")),("S", PowerSetType(SetType("X"))),("T", PowerSetType(SetType("Y")))]
        _test_typeit(root, env, lst, ["y","f"])
        assert isinstance(env.get_type("y"), SetType)
        assert env.get_type("y").data=="Y"


    def test_types_lambda(self):
        # Build AST
        string_to_file("#PREDICATE f="+"%"+"x.(x>0 & x<10|x*x)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["f","x"])
        assert isinstance(env.get_type("f"), PowerSetType)
        assert isinstance(env.get_type("f").data, CartType)
        assert isinstance(env.get_type("f").data.data[0].data, IntegerType)
        assert isinstance(env.get_type("f").data.data[1].data, IntegerType)
        assert isinstance(env.get_type("x"), IntegerType)


    def test_types_seq(self):
        # Build AST
        string_to_file("#PREDICATE s:seq(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        self.type_check_sequence(ast_string)


    def test_types_iseq(self):
        # Build AST
        string_to_file("#PREDICATE s:iseq(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        self.type_check_sequence(ast_string)


    def test_types_seq1(self):
        # Build AST
        string_to_file("#PREDICATE s:seq1(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        self.type_check_sequence(ast_string)


    def test_types_iseq1(self):
        # Build AST
        string_to_file("#PREDICATE s:iseq1(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        self.type_check_sequence(ast_string)


    def test_types_perm(self):
        # Build AST
        string_to_file("#PREDICATE s:perm(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        self.type_check_sequence(ast_string)


    def test_types_seq_conc(self):
        # Build AST
        string_to_file("#PREDICATE s:perm(S) & t:perm(S) & r=s^t", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X")))]
        _test_typeit(root, env, lst, ["r","s","t"])
        assert isinstance(env.get_type("r"), PowerSetType)
        assert isinstance(env.get_type("r").data, CartType)
        assert isinstance(env.get_type("r").data.data[0], IntegerType)
        assert isinstance(env.get_type("r").data.data[1], SetType)


    def test_types_seq_prepend(self):
        # Build AST
        string_to_file("#PREDICATE s:perm(S) & E:S & t=E->s", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X")))]
        _test_typeit(root, env, lst, ["E","s","t"])
        assert isinstance(env.get_type("t"), PowerSetType)
        assert isinstance(env.get_type("t").data, CartType)
        assert isinstance(env.get_type("t").data.data[0].data, IntegerType)
        assert isinstance(env.get_type("t").data.data[1].data, SetType)


    def test_types_seq_size(self):
        # Build AST
        string_to_file("#PREDICATE s:perm(S) & x=size(s)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X")))]
        _test_typeit(root, env, lst, ["x","s"])
        assert isinstance(env.get_type("x"), IntegerType)


    def test_types_seq_rev(self):
        # Build AST
        string_to_file("#PREDICATE s:perm(S) & t=rev(s)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X")))]
        _test_typeit(root, env, lst, ["t","s"])
        assert isinstance(env.get_type("t"), PowerSetType)
        assert isinstance(env.get_type("t").data, CartType)
        assert isinstance(env.get_type("t").data.data[0].data, IntegerType)
        assert isinstance(env.get_type("t").data.data[1].data, SetType)


    def test_types_seq_take(self):
        # Build AST
        string_to_file("#PREDICATE n=3 & s:perm(S) & t=s/|\\n", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X")))]
        _test_typeit(root, env, lst, ["t","s","n"])
        assert isinstance(env.get_type("t"), PowerSetType)
        assert isinstance(env.get_type("t").data, CartType)
        assert isinstance(env.get_type("t").data.data[0].data, IntegerType)
        assert isinstance(env.get_type("t").data.data[1].data, SetType)
        assert isinstance(env.get_type("n"), IntegerType)


    def test_types_seq_drop(self):
        # Build AST
        string_to_file("#PREDICATE n=3 & s:perm(S) & t=s\|/n", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X")))]
        _test_typeit(root, env, lst, ["t","s","n"])
        assert isinstance(env.get_type("t"), PowerSetType)
        assert isinstance(env.get_type("t").data, CartType)
        assert isinstance(env.get_type("t").data.data[0].data, IntegerType)
        assert isinstance(env.get_type("t").data.data[1].data, SetType)
        assert isinstance(env.get_type("n"), IntegerType)


    def test_types_seq_first(self):
        # Build AST
        string_to_file("#PREDICATE s:perm(S) & n=first(s)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X")))]
        _test_typeit(root, env, lst, ["s","n"])
        assert isinstance(env.get_type("n"), SetType)
        assert env.get_type("n").data == "X"


    def test_types_seq_last(self):
        # Build AST
        string_to_file("#PREDICATE s:perm(S) & n=last(s)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X")))]
        _test_typeit(root, env, lst, ["s","n"])
        assert isinstance(env.get_type("n"), SetType)
        assert env.get_type("n").data == "X"


    def test_types_seq_tail(self):
        # Build AST
        string_to_file("#PREDICATE s:perm(S) & t=tail(s)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X")))]
        _test_typeit(root, env, lst, ["s","t"])
        assert isinstance(env.get_type("t"), PowerSetType)
        assert isinstance(env.get_type("t").data, CartType)
        assert isinstance(env.get_type("t").data.data[0].data, IntegerType)
        assert isinstance(env.get_type("t").data.data[1].data, SetType)


    def test_types_seq_front(self):
        # Build AST
        string_to_file("#PREDICATE s:perm(S) & t=front(s)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X")))]
        _test_typeit(root, env, lst, ["s","t"])
        assert isinstance(env.get_type("t"), PowerSetType)
        assert isinstance(env.get_type("t").data, CartType)
        assert isinstance(env.get_type("t").data.data[0].data, IntegerType)
        assert isinstance(env.get_type("t").data.data[1].data, SetType)


    def test_types_seq_conc(self):
        # Build AST
        string_to_file("#PREDICATE ss:perm(perm(S)) & s=conc(ss)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X")))]
        _test_typeit(root, env, lst, ["s","ss"])
        assert isinstance(env.get_type("s"), PowerSetType)
        assert isinstance(env.get_type("s").data, CartType)
        assert isinstance(env.get_type("ss"), PowerSetType)
        assert isinstance(env.get_type("ss").data, CartType)


    def test_types_seq_append(self):
        # Build AST
        string_to_file("#PREDICATE s:perm(S) & E:S & t=s<-E", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X")))]
        _test_typeit(root, env, lst, ["s","t","E"])
        assert isinstance(env.get_type("t"), PowerSetType)
        assert isinstance(env.get_type("t").data, CartType)
        assert isinstance(env.get_type("t").data.data[0].data, IntegerType)
        assert isinstance(env.get_type("t").data.data[1].data, SetType)


    def test_types_seq_extention(self):
        # Build AST
        string_to_file("#PREDICATE s=[1,2,3]", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["s"])
        assert isinstance(env.get_type("s"), PowerSetType)
        assert isinstance(env.get_type("s").data, CartType)
        assert isinstance(env.get_type("s").data.data[0].data, IntegerType)
        assert isinstance(env.get_type("s").data.data[1].data, IntegerType)



    def test_types_fnc_expr(self):
        # Build AST
        string_to_file("#PREDICATE R1 = {(0|->1), (0|->2), (1|->1), (1|->7), (2|->3)} & f= fnc(R1)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["R1","f"])
        assert isinstance(env.get_type("f"), PowerSetType)
        assert isinstance(env.get_type("f").data, CartType)
        assert isinstance(env.get_type("f").data.data[0].data, IntegerType)
        assert isinstance(env.get_type("f").data.data[1].data, PowerSetType)
        assert isinstance(env.get_type("f").data.data[1].data.data, IntegerType)
        assert isinstance(env.get_type("R1"), PowerSetType)
        assert isinstance(env.get_type("R1").data, CartType)
        assert isinstance(env.get_type("R1").data.data[0].data, IntegerType)
        assert isinstance(env.get_type("R1").data.data[1].data, IntegerType)


    def type_check_sequence(self, ast_string):
        exec ast_string

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X")))]
        _test_typeit(root, env, lst, ["s"])
        assert isinstance(env.get_type("s"), PowerSetType)
        assert isinstance(env.get_type("s").data, CartType)
        assert isinstance(env.get_type("s").data.data[0].data, IntegerType)
        assert isinstance(env.get_type("s").data.data[1].data, SetType)


    def type_check_function(self, ast_string):
        exec ast_string

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X"))),("T", PowerSetType(SetType("Y")))]
        _test_typeit(root, env, lst, ["r"])
        assert isinstance(env.get_type("r"), PowerSetType)
        assert isinstance(env.get_type("r").data, CartType)
        assert isinstance(env.get_type("r").data.data[0].data, SetType)
        assert isinstance(env.get_type("r").data.data[1].data, SetType)
        assert env.get_type("r").data.data[0].data.data == "X"
        assert env.get_type("r").data.data[1].data.data == "Y"
# -*- coding: utf-8 -*-
from ast_nodes import *
from interp import Environment
from typing import typeit, IntegerType, PowerSetType, SetType, CartType
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


    def test_types_function_app(self):
        # Build AST
        string_to_file("#PREDICATE f:S+->T & y=f(x)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.set_type("x", SetType("X"))
        env.set_type("S", PowerSetType(SetType("X")))
        env.set_type("T", PowerSetType(SetType("Y")))
        typeit(root, env)
        assert isinstance(env.get_type("y"), SetType)
        assert env.get_type("y").data=="Y"


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
        env.set_type("S", PowerSetType(SetType("X")))
        typeit(root, env)
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
        env.set_type("S", PowerSetType(SetType("X")))
        typeit(root, env)
        assert isinstance(env.get_type("t"), PowerSetType)
        assert isinstance(env.get_type("t").data, CartType)
        assert isinstance(env.get_type("t").data.data[0], IntegerType)
        assert isinstance(env.get_type("t").data.data[1], SetType)


    def test_types_seq_size(self):
        # Build AST
        string_to_file("#PREDICATE s:perm(S) & x=size(s)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.set_type("S", PowerSetType(SetType("X")))
        typeit(root, env)
        assert isinstance(env.get_type("x"), IntegerType)


    def test_types_seq_rev(self):
        # Build AST
        string_to_file("#PREDICATE s:perm(S) & t=rev(s)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.set_type("S", PowerSetType(SetType("X")))
        typeit(root, env)
        assert isinstance(env.get_type("t"), PowerSetType)
        assert isinstance(env.get_type("t").data, CartType)
        assert isinstance(env.get_type("t").data.data[0], IntegerType)
        assert isinstance(env.get_type("t").data.data[1], SetType)


    def test_types_seq_take(self):
        # Build AST
        string_to_file("#PREDICATE n=3 & s:perm(S) & t=s/|\\n", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.set_type("S", PowerSetType(SetType("X")))
        typeit(root, env)
        assert isinstance(env.get_type("t"), PowerSetType)
        assert isinstance(env.get_type("t").data, CartType)
        assert isinstance(env.get_type("t").data.data[0], IntegerType)
        assert isinstance(env.get_type("t").data.data[1], SetType)
        assert isinstance(env.get_type("n"), IntegerType)


    def test_types_seq_drop(self):
        # Build AST
        string_to_file("#PREDICATE n=3 & s:perm(S) & t=s\|/n", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.set_type("S", PowerSetType(SetType("X")))
        typeit(root, env)
        assert isinstance(env.get_type("t"), PowerSetType)
        assert isinstance(env.get_type("t").data, CartType)
        assert isinstance(env.get_type("t").data.data[0], IntegerType)
        assert isinstance(env.get_type("t").data.data[1], SetType)
        assert isinstance(env.get_type("n"), IntegerType)


    def test_types_seq_first(self):
        # Build AST
        string_to_file("#PREDICATE s:perm(S) & n=first(s)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.set_type("S", PowerSetType(SetType("X")))
        typeit(root, env)
        assert isinstance(env.get_type("n"), SetType)
        assert env.get_type("n").data == "X"


    def test_types_seq_last(self):
        # Build AST
        string_to_file("#PREDICATE s:perm(S) & n=last(s)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.set_type("S", PowerSetType(SetType("X")))
        typeit(root, env)
        assert isinstance(env.get_type("n"), SetType)
        assert env.get_type("n").data == "X"


    def test_types_seq_tail(self):
        # Build AST
        string_to_file("#PREDICATE s:perm(S) & t=tail(s)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.set_type("S", PowerSetType(SetType("X")))
        typeit(root, env)
        assert isinstance(env.get_type("t"), PowerSetType)
        assert isinstance(env.get_type("t").data, CartType)
        assert isinstance(env.get_type("t").data.data[0], IntegerType)
        assert isinstance(env.get_type("t").data.data[1], SetType)


    def test_types_seq_front(self):
        # Build AST
        string_to_file("#PREDICATE s:perm(S) & t=front(s)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.set_type("S", PowerSetType(SetType("X")))
        typeit(root, env)
        assert isinstance(env.get_type("t"), PowerSetType)
        assert isinstance(env.get_type("t").data, CartType)
        assert isinstance(env.get_type("t").data.data[0], IntegerType)
        assert isinstance(env.get_type("t").data.data[1], SetType)


    def test_types_seq_append(self):
        # Build AST
        string_to_file("#PREDICATE s:perm(S) & E:S & t=s<-E", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        env.set_type("S", PowerSetType(SetType("X")))
        typeit(root, env)
        assert isinstance(env.get_type("t"), PowerSetType)
        assert isinstance(env.get_type("t").data, CartType)
        assert isinstance(env.get_type("t").data.data[0], IntegerType)
        assert isinstance(env.get_type("t").data.data[1], SetType)


    def type_check_sequence(self, ast_string):
        exec ast_string

        # Type
        env = Environment()
        env.set_type("S", PowerSetType(SetType("X")))
        typeit(root, env)
        assert isinstance(env.get_type("s"), PowerSetType)
        assert isinstance(env.get_type("s").data, CartType)
        assert isinstance(env.get_type("s").data.data[0], IntegerType)
        assert isinstance(env.get_type("s").data.data[1], SetType)


    def type_check_function(self, ast_string):
        exec ast_string

        # Type
        env = Environment()
        env.set_type("S", PowerSetType(SetType("X")))
        env.set_type("T", PowerSetType(SetType("Y")))
        typeit(root, env)
        assert isinstance(env.get_type("r"), PowerSetType)
        assert isinstance(env.get_type("r").data, CartType)
        assert isinstance(env.get_type("r").data.data[0], SetType)
        assert isinstance(env.get_type("r").data.data[1], SetType)
        assert env.get_type("r").data.data[0].data == "X"
        assert env.get_type("r").data.data[1].data == "Y"

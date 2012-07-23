# -*- coding: utf-8 -*-
from ast_nodes import *
from environment import Environment
from interp import interpret
from helpers import file_to_AST_str, string_to_file

file_name = "input.txt"

class TestQuickEnum():
    def test_quick_relation_member(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2,3,4,5} & T={1,2,3,4,5} & {(1,2)}:S<->T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.bstate.add_ids_to_frame(["S","T"])
        assert interpret(root.children[0], env)


    def test_quick_relation_member2(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2,3,4,5} & T={1,2,3,4,5} & {(6,2)}:S<->T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.bstate.add_ids_to_frame(["S","T"])
        assert not interpret(root.children[0], env)


    def test_quick_relation_member3(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2,3} & T={1,2} & {(1,2),(2,1)}:S+->T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.bstate.add_ids_to_frame(["S","T"])
        assert interpret(root.children[0], env)


    def test_quick_relation_member4(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2,3} & T={1,2} & {(1,2),(2,1)}:S>+>T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.bstate.add_ids_to_frame(["S","T"])
        assert interpret(root.children[0], env)


    def test_quick_relation_member5(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2,3} & T={1,2} & {(1,2)}:S>+>T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.bstate.add_ids_to_frame(["S","T"])
        assert interpret(root.children[0], env)


    def test_quick_relation_member6(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2,3} & T={1,2} & {(1,2),(3,2),(2,1)}:S+->>T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.bstate.add_ids_to_frame(["S","T"])
        assert interpret(root.children[0], env)


    def test_quick_relation_member7(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2,3} & T={1,2} & {(1,2),(3,2),(2,1)}:S>+>>T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.bstate.add_ids_to_frame(["S","T"])
        assert not interpret(root.children[0], env)


    def test_quick_relation_member8(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2,3} & T={1,2} & {(1,2)}:S>+>>T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.bstate.add_ids_to_frame(["S","T"])
        assert not interpret(root.children[0], env)          
 
 
    def test_quick_relation_member9(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2,3} & T={1,2} & {(1,2),(2,1)}:S>+>>T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.bstate.add_ids_to_frame(["S","T"])
        assert interpret(root.children[0], env)


    def test_quick_relation_member10(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2,3} & T={1,2} & {(1,2),(2,1)}:S-->T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.bstate.add_ids_to_frame(["S","T"])
        assert not interpret(root.children[0], env)


    def test_quick_relation_member11(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2,3} & T={1,2} & {(1,2),(2,1),(3,1)}:S-->T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.bstate.add_ids_to_frame(["S","T"])
        assert interpret(root.children[0], env)


    def test_quick_relation_member12(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2,3} & T={1,2} & {(1,2),(2,1),(3,1)}:S>->T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.bstate.add_ids_to_frame(["S","T"])
        assert not interpret(root.children[0], env)    


    def test_quick_relation_member13(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2} & T={1,2} & {(1,2),(2,1)}:S>->T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.bstate.add_ids_to_frame(["S","T"])
        assert interpret(root.children[0], env)


    def test_quick_relation_member14(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2} & T={1,2,3} & {(1,2),(2,1)}:S>->T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.bstate.add_ids_to_frame(["S","T"])
        assert interpret(root.children[0], env)


    def test_quick_relation_member15(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2,3} & T={1,2} & {(1,2),(2,1),(3,2)}:S-->>T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.bstate.add_ids_to_frame(["S","T"])
        assert interpret(root.children[0], env)


    def test_quick_relation_member16(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2} & T={1,2} & {(1,2),(2,1)}:S-->>T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.bstate.add_ids_to_frame(["S","T"])
        assert interpret(root.children[0], env)


    def test_quick_relation_member17(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2,3} & T={1,2} & {(1,1),(2,1),(3,1)}:S-->>T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.bstate.add_ids_to_frame(["S","T"])
        assert not interpret(root.children[0], env)


    def test_quick_relation_member18(self):
        # Build AST
        string_to_file("#PREDICATE S={1,2,3} & T={1,2,3} & {(1,3),(2,1),(3,2)}:S>->>T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.bstate.add_ids_to_frame(["S","T"])
        assert interpret(root.children[0], env)                   
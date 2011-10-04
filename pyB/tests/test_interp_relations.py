# -*- coding: utf-8 -*-
from ast_nodes import *
from interp import inperpret, Environment
from helpers import file_to_AST_str, string_to_file

file_name = "input.txt"

class TestInterpRelations():
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



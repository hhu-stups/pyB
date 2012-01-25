# -*- coding: utf-8 -*-
from ast_nodes import *
from interp import interpret, Environment
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
        env.set_value("S", set(["a","b"]))
        env.set_value("T", set(["x","y"]))
        env.set_value("f", set([("a","x")]))
        assert interpret(root.children[0],env)

        env.set_value("f", set([("a","x"),("a","y")]))
        assert interpret(root.children[0],env)

        env.set_value("f", set([("a","x"),("b","y")]))
        assert interpret(root.children[0],env)

        env.set_value("f", set([]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_rel_dom(self):
        # Build AST:
        string_to_file("#PREDICATE S=dom(f)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("S", set(["a"]))
        env.set_value("f", set([("a","x")]))
        assert interpret(root.children[0],env)

        env.set_value("f", set([("1","x"),("2","y"),("3","z"),("1","y")]))
        env.set_value("S", set(["1","2","3"]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_rel_ran(self):
        # Build AST:
        string_to_file("#PREDICATE {4,5,6}=ran({(1|->4),(2|->5),(3|->6)}) ", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        assert interpret(root.children[0],env)


    def test_genAST_pred_rel_comp(self):
        # Build AST:
        string_to_file("#PREDICATE S= (p ; q)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("S", set([("1","x")]))
        env.set_value("p", set([("1","a")]))
        env.set_value("q", set([("a","x")]))
        assert interpret(root.children[0],env)

        env.set_value("S", set([("1","a")]))
        env.set_value("p", set([("1","x"),("2","y"),("3","z"),("1","y")]))
        env.set_value("q", set([("x","a")]))
        assert interpret(root.children[0],env)

        env.set_value("S", set([("1","a"),("2","a")]))
        env.set_value("p", set([("1","x"),("2","x"),("3","z")]))
        env.set_value("q", set([("x","a")]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_rel_id(self):
        # Build AST:
        string_to_file("#PREDICATE r=id(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("S", set(["a","b","c"]))
        env.set_value("r", set([("a","a"),("b","b"),("c","c")]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_simple_closure(self):
        # Build AST
        string_to_file("#PREDICATE f=closure(r)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("f", set([(1,3),(3,1),(1,1),(3,3)]))
        env.set_value("r", set([(1,3),(3,1)]))
        assert interpret(root.children[0],env)

        env.set_value("f", set([(1,7),(6,2),(8,4),(1,1),(6,6),(8,8)]))
        env.set_value("r", set([(1,7),(6,2),(8,4)]))
        assert interpret(root.children[0],env)

        env.set_value("f", set([(1,7),(6,4),(8,4),(1,1),(6,6),(8,8)]))
        env.set_value("r", set([(1,7),(6,4),(8,4)]))
        assert interpret(root.children[0],env)

    def test_genAST_pred_simple_iterate(self):
        # Build AST
        string_to_file("#PREDICATE f=iterate(r,n)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("f", set([(1,1),(6,6),(8,8)])) # XXX
        env.set_value("r", set([(1,7),(6,2),(8,4)]))
        env.set_value("n",0)
        assert interpret(root.children[0],env)

        env.set_value("f", set([(1,7),(6,2),(8,4)])) 
        env.set_value("r", set([(1,7),(6,2),(8,4)]))
        env.set_value("n",1)
        assert interpret(root.children[0],env)

        env.set_value("f", set([])) 
        env.set_value("r", set([(1,7),(6,2),(8,4)]))
        env.set_value("n",2)
        assert interpret(root.children[0],env)

        env.set_value("f", set([])) # fixpoint
        env.set_value("r", set([(1,7),(6,2),(8,4)]))
        env.set_value("n",3)
        assert interpret(root.children[0],env)

        env.set_value("f", set([(1,1),(3,3)]))
        env.set_value("r", set([(1,3),(3,1)]))
        env.set_value("n",0)
        assert interpret(root.children[0],env)

        env.set_value("f", set([(1,3),(3,1)]))
        env.set_value("r", set([(1,3),(3,1)]))
        env.set_value("n",1)
        assert interpret(root.children[0],env)

        env.set_value("f", set([(1,1),(3,3)])) # "fixpoint"
        env.set_value("r", set([(1,3),(3,1)]))
        env.set_value("n",2)
        assert interpret(root.children[0],env)


    def test_genAST_pred_rel_domres(self):
        # Build AST:
        string_to_file("#PREDICATE f=S<|r", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("S", set(["a"]))
        env.set_value("f", set([("a","1")]))
        env.set_value("r", set([("a","1"),("b","42"),("c","777")]))
        assert interpret(root.children[0],env)

        env.set_value("f", set([("a","1"),("a","42")]))
        env.set_value("r", set([("a","1"),("a","42"),("c","777")]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_rel_domsub(self):
        # Build AST:
        string_to_file("#PREDICATE f=S<<|r", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("S", set(["a"]))
        env.set_value("f", set([("b","42"),("c","777")]))
        env.set_value("r", set([("a","1"),("b","42"),("c","777")]))
        assert interpret(root.children[0],env)

        env.set_value("f", set([("c","777")]))
        env.set_value("r", set([("a","1"),("a","42"),("c","777")]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_rel_ranres(self):
        # Build AST:
        string_to_file("#PREDICATE f=r|>T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("T", set(["1"]))
        env.set_value("f", set([("a","1")]))
        env.set_value("r", set([("a","1"),("b","42"),("c","777")]))
        assert interpret(root.children[0],env)

        env.set_value("f", set([("a","1"),("b","1")]))
        env.set_value("r", set([("a","1"),("b","1"),("c","777")]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_rel_ransub(self):
        # Build AST:
        string_to_file("#PREDICATE f=r|>>T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("T", set(["1"]))
        env.set_value("f", set([("b","42"),("c","777")]))
        env.set_value("r", set([("a","1"),("b","42"),("c","777")]))
        assert interpret(root.children[0],env)

        env.set_value("f", set([("c","777")]))
        env.set_value("r", set([("a","1"),("b","1"),("c","777")]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_rel_inverse(self):
        # Build AST:
        string_to_file("#PREDICATE f=r~", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("f", set([("1","a"),("42","b"),("777","c")]))
        env.set_value("r", set([("a","1"),("b","42"),("c","777")]))
        assert interpret(root.children[0],env)

        env.set_value("f", set([]))
        env.set_value("r", set([]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_rel_image(self):
        # Build AST:
        string_to_file("#PREDICATE f=r[S]", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("S", set(["a"]))
        env.set_value("f", set(["1"]))
        env.set_value("r", set([("a","1"),("b","42"),("c","777")]))
        assert interpret(root.children[0],env)

        env.set_value("f", set(["1","42"]))
        env.set_value("r", set([("a","1"),("a","42"),("c","777")]))
        assert interpret(root.children[0],env)

        env.set_value("S", set(["a","c"]))
        env.set_value("f", set(["1","42","777"]))
        env.set_value("r", set([("a","1"),("a","42"),("c","777")]))
        assert interpret(root.children[0],env)

        env.set_value("S", set(["c"]))
        env.set_value("f", set(["777"]))
        env.set_value("r", set([("a","1"),("a","42"),("c","777")]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_rel_overriding(self):
        # Build AST:
        string_to_file("#PREDICATE f=r1 <+ r2", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("f", set([("a","1"),("b","42"),("c","777"),("d","17")]))
        env.set_value("r1", set([("d","17")]))
        env.set_value("r2", set([("a","1"),("b","42"),("c","777")]))
        assert interpret(root.children[0],env)

        env.set_value("f", set([("a","1"),("b","41"),("c","777"),("d","17")]))
        env.set_value("r2", set([("d","17"),("b","41")]))
        env.set_value("r1", set([("a","1"),("b","42"),("c","777")]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_rel_proj1(self):
        # Build AST:
        string_to_file("#PREDICATE f=prj1(S,T)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("f", set([]))
        env.set_value("S", set([]))
        env.set_value("T", set([]))
        assert interpret(root.children[0],env)

        env.set_value("f", set([(("a","y"),"a"),(("b","y"),"b"),(("a","x"),"a"),(("b","x"),"b")]))
        env.set_value("S", set(["a","b"]))
        env.set_value("T", set(["x","y"]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_rel_proj2(self):
        # Build AST:
        string_to_file("#PREDICATE f=prj2(S,T)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("f", set([]))
        env.set_value("S", set([]))
        env.set_value("T", set([]))
        assert interpret(root.children[0],env)

        env.set_value("f", set([(("a","y"),"y"),(("b","y"),"y"),(("a","x"),"x"),(("b","x"),"x")]))
        env.set_value("S", set(["a","b"]))
        env.set_value("T", set(["x","y"]))
        assert interpret(root.children[0],env)

    def test_genAST_pred_rel_direct_prod(self):
        # Build AST:
        string_to_file("#PREDICATE f= p >< q", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("f", set([]))
        env.set_value("p", set([]))
        env.set_value("q", set([]))
        assert interpret(root.children[0],env)

        env.set_value("f", set([]))
        env.set_value("p", set([("x","1"),("y","2")]))
        env.set_value("q", set([("a","3"),("b","4")]))
        assert interpret(root.children[0],env)

        env.set_value("f", set([("x",("1","3"))]))
        env.set_value("p", set([("x","1"),("y","2")]))
        env.set_value("q", set([("x","3"),("b","4")]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_rel_parallel_prod(self):
        # Build AST:
        string_to_file("#PREDICATE f= (p || q)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("f", set([]))
        env.set_value("p", set([]))
        env.set_value("q", set([]))
        assert interpret(root.children[0],env)

        env.set_value("f", set([(("x","a"),("1","3")),(("x","b"),("1","4"))]))
        env.set_value("p", set([("x","1")]))
        env.set_value("q", set([("a","3"),("b","4")]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_rel_repr(self):
        # Build AST:
        string_to_file("#PREDICATE f={aa|->aa, aa|->bb, bb|->bb, bb|->aa} & f=ID*ID", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("aa","aa") # XXX
        env.set_value("bb","bb") # XXX
        env.set_value("ID", set(["aa","bb"]))
        env.set_value("f", set([("aa","bb"),("aa","aa"),("bb","aa"),("bb","bb")]))
        assert interpret(root.children[0],env)
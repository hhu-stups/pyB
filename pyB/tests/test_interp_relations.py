# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
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
        env.set_value("S", frozenset(["a","b"]))
        env.set_value("T", frozenset(["x","y"]))
        env.set_value("f", frozenset([("a","x")]))
        assert interpret(root.children[0],env)

        env.set_value("f", frozenset([("a","x"),("a","y")]))
        assert interpret(root.children[0],env)

        env.set_value("f", frozenset([("a","x"),("b","y")]))
        assert interpret(root.children[0],env)

        env.set_value("f", frozenset([]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_rel_dom(self):
        # Build AST:
        string_to_file("#PREDICATE S=dom(f)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("S", frozenset(["a"]))
        env.set_value("f", frozenset([("a","x")]))
        assert interpret(root.children[0],env)

        env.set_value("f", frozenset([("1","x"),("2","y"),("3","z"),("1","y")]))
        env.set_value("S", frozenset(["1","2","3"]))
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
        env.set_value("S", frozenset([("1","x")]))
        env.set_value("p", frozenset([("1","a")]))
        env.set_value("q", frozenset([("a","x")]))
        assert interpret(root.children[0],env)

        env.set_value("S", frozenset([("1","a")]))
        env.set_value("p", frozenset([("1","x"),("2","y"),("3","z"),("1","y")]))
        env.set_value("q", frozenset([("x","a")]))
        assert interpret(root.children[0],env)

        env.set_value("S", frozenset([("1","a"),("2","a")]))
        env.set_value("p", frozenset([("1","x"),("2","x"),("3","z")]))
        env.set_value("q", frozenset([("x","a")]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_rel_id(self):
        # Build AST:
        string_to_file("#PREDICATE r=id(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("S", frozenset(["a","b","c"]))
        env.set_value("r", frozenset([("a","a"),("b","b"),("c","c")]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_simple_closure(self):
        # Build AST
        string_to_file("#PREDICATE f=closure(r)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("f", frozenset([(1,3),(3,1),(1,1),(3,3)]))
        env.set_value("r", frozenset([(1,3),(3,1)]))
        assert interpret(root.children[0],env)

        env.set_value("f", frozenset([(1,7),(6,2),(8,4),(1,1),(6,6),(8,8)]))
        env.set_value("r", frozenset([(1,7),(6,2),(8,4)]))
        assert interpret(root.children[0],env)

        env.set_value("f", frozenset([(1,7),(6,4),(8,4),(1,1),(6,6),(8,8)]))
        env.set_value("r", frozenset([(1,7),(6,4),(8,4)]))
        assert interpret(root.children[0],env)

    def test_genAST_pred_simple_iterate(self):
        # Build AST
        string_to_file("#PREDICATE f=iterate(r,n)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("f", frozenset([(1,1),(6,6),(8,8)])) # XXX
        env.set_value("r", frozenset([(1,7),(6,2),(8,4)]))
        env.set_value("n",0)
        assert interpret(root.children[0],env)

        env.set_value("f", frozenset([(1,7),(6,2),(8,4)])) 
        env.set_value("r", frozenset([(1,7),(6,2),(8,4)]))
        env.set_value("n",1)
        assert interpret(root.children[0],env)

        env.set_value("f", frozenset([])) 
        env.set_value("r", frozenset([(1,7),(6,2),(8,4)]))
        env.set_value("n",2)
        assert interpret(root.children[0],env)

        env.set_value("f", frozenset([])) # fixpoint
        env.set_value("r", frozenset([(1,7),(6,2),(8,4)]))
        env.set_value("n",3)
        assert interpret(root.children[0],env)

        env.set_value("f", frozenset([(1,1),(3,3)]))
        env.set_value("r", frozenset([(1,3),(3,1)]))
        env.set_value("n",0)
        assert interpret(root.children[0],env)

        env.set_value("f", frozenset([(1,3),(3,1)]))
        env.set_value("r", frozenset([(1,3),(3,1)]))
        env.set_value("n",1)
        assert interpret(root.children[0],env)

        env.set_value("f", frozenset([(1,1),(3,3)])) # "fixpoint"
        env.set_value("r", frozenset([(1,3),(3,1)]))
        env.set_value("n",2)
        assert interpret(root.children[0],env)


    def test_genAST_pred_rel_domres(self):
        # Build AST:
        string_to_file("#PREDICATE f=S<|r", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("S", frozenset(["a"]))
        env.set_value("f", frozenset([("a","1")]))
        env.set_value("r", frozenset([("a","1"),("b","42"),("c","777")]))
        assert interpret(root.children[0],env)

        env.set_value("f", frozenset([("a","1"),("a","42")]))
        env.set_value("r", frozenset([("a","1"),("a","42"),("c","777")]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_rel_domsub(self):
        # Build AST:
        string_to_file("#PREDICATE f=S<<|r", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("S", frozenset(["a"]))
        env.set_value("f", frozenset([("b","42"),("c","777")]))
        env.set_value("r", frozenset([("a","1"),("b","42"),("c","777")]))
        assert interpret(root.children[0],env)

        env.set_value("f", frozenset([("c","777")]))
        env.set_value("r", frozenset([("a","1"),("a","42"),("c","777")]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_rel_ranres(self):
        # Build AST:
        string_to_file("#PREDICATE f=r|>T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("T", frozenset(["1"]))
        env.set_value("f", frozenset([("a","1")]))
        env.set_value("r", frozenset([("a","1"),("b","42"),("c","777")]))
        assert interpret(root.children[0],env)

        env.set_value("f", frozenset([("a","1"),("b","1")]))
        env.set_value("r", frozenset([("a","1"),("b","1"),("c","777")]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_rel_ransub(self):
        # Build AST:
        string_to_file("#PREDICATE f=r|>>T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("T", frozenset(["1"]))
        env.set_value("f", frozenset([("b","42"),("c","777")]))
        env.set_value("r", frozenset([("a","1"),("b","42"),("c","777")]))
        assert interpret(root.children[0],env)

        env.set_value("f", frozenset([("c","777")]))
        env.set_value("r", frozenset([("a","1"),("b","1"),("c","777")]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_rel_inverse(self):
        # Build AST:
        string_to_file("#PREDICATE f=r~", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("f", frozenset([("1","a"),("42","b"),("777","c")]))
        env.set_value("r", frozenset([("a","1"),("b","42"),("c","777")]))
        assert interpret(root.children[0],env)

        env.set_value("f", frozenset([]))
        env.set_value("r", frozenset([]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_rel_image(self):
        # Build AST:
        string_to_file("#PREDICATE f=r[S]", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("S", frozenset(["a"]))
        env.set_value("f", frozenset(["1"]))
        env.set_value("r", frozenset([("a","1"),("b","42"),("c","777")]))
        assert interpret(root.children[0],env)

        env.set_value("f", frozenset(["1","42"]))
        env.set_value("r", frozenset([("a","1"),("a","42"),("c","777")]))
        assert interpret(root.children[0],env)

        env.set_value("S", frozenset(["a","c"]))
        env.set_value("f", frozenset(["1","42","777"]))
        env.set_value("r", frozenset([("a","1"),("a","42"),("c","777")]))
        assert interpret(root.children[0],env)

        env.set_value("S", frozenset(["c"]))
        env.set_value("f", frozenset(["777"]))
        env.set_value("r", frozenset([("a","1"),("a","42"),("c","777")]))
        assert interpret(root.children[0],env)

        env.set_value("r", frozenset([(3,5), (3,9), (6,3), (9,2)]))
        env.set_value("S", frozenset([1, 2, 3]))
        env.set_value("f", frozenset([5,9]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_rel_overriding(self):
        # Build AST:
        string_to_file("#PREDICATE f=r1 <+ r2", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("f", frozenset([("a","1"),("b","42"),("c","777"),("d","17")]))
        env.set_value("r1", frozenset([("d","17")]))
        env.set_value("r2", frozenset([("a","1"),("b","42"),("c","777")]))
        assert interpret(root.children[0],env)

        env.set_value("f", frozenset([("a","1"),("b","41"),("c","777"),("d","17")]))
        env.set_value("r2", frozenset([("d","17"),("b","41")]))
        env.set_value("r1", frozenset([("a","1"),("b","42"),("c","777")]))
        assert interpret(root.children[0],env)

        env.set_value("r1", frozenset([(2,7), (3,4), (5,1), (9,5)]))
        env.set_value("r2", frozenset([(3,5), (3,9), (6,3), (9,2)]))
        env.set_value("f", frozenset([(3,5), (3,9), (6,3), (9,2), (2,7), (5,1)]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_rel_proj1(self):
        # Build AST:
        string_to_file("#PREDICATE f=prj1(S,T)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("f", frozenset([]))
        env.set_value("S", frozenset([]))
        env.set_value("T", frozenset([]))
        assert interpret(root.children[0],env)

        env.set_value("f", frozenset([(("a","y"),"a"),(("b","y"),"b"),(("a","x"),"a"),(("b","x"),"b")]))
        env.set_value("S", frozenset(["a","b"]))
        env.set_value("T", frozenset(["x","y"]))
        assert interpret(root.children[0],env)

        env.set_value("S", frozenset([1,4]))
        env.set_value("T", frozenset([2,3]))
        env.set_value("f", frozenset([((1,2),1),((1,3),1),((4,2),4),((4,3),4)]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_rel_proj2(self):
        # Build AST:
        string_to_file("#PREDICATE f=prj2(S,T)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("f", frozenset([]))
        env.set_value("S", frozenset([]))
        env.set_value("T", frozenset([]))
        assert interpret(root.children[0],env)

        env.set_value("f", frozenset([(("a","y"),"y"),(("b","y"),"y"),(("a","x"),"x"),(("b","x"),"x")]))
        env.set_value("S", frozenset(["a","b"]))
        env.set_value("T", frozenset(["x","y"]))
        assert interpret(root.children[0],env)

        env.set_value("S", frozenset([1,4]))
        env.set_value("T", frozenset([2,3]))
        env.set_value("f", frozenset([((1,2),2),((1,3),3),((4,2),2),((4,3),3)]))
        assert interpret(root.children[0],env)



    def test_genAST_pred_rel_direct_prod(self):
        # Build AST:
        string_to_file("#PREDICATE f= p >< q", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("f", frozenset([]))
        env.set_value("p", frozenset([]))
        env.set_value("q", frozenset([]))
        assert interpret(root.children[0],env)

        env.set_value("f", frozenset([]))
        env.set_value("p", frozenset([("x","1"),("y","2")]))
        env.set_value("q", frozenset([("a","3"),("b","4")]))
        assert interpret(root.children[0],env)

        env.set_value("f", frozenset([("x",("1","3"))]))
        env.set_value("p", frozenset([("x","1"),("y","2")]))
        env.set_value("q", frozenset([("x","3"),("b","4")]))
        assert interpret(root.children[0],env)

        env.set_value("f", frozenset([(7,(11,20)), (2,(11,21))]))
        env.set_value("p", frozenset([(8,10), (7,11), (2,11), (6,12)]))
        env.set_value("q", frozenset([(1,20), (7,20), (2,21), (1,22)]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_rel_parallel_prod(self):
        # Build AST:
        string_to_file("#PREDICATE f= (p || q)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        env.set_value("f", frozenset([]))
        env.set_value("p", frozenset([]))
        env.set_value("q", frozenset([]))
        assert interpret(root.children[0],env)

        env.set_value("f", frozenset([(("x","a"),("1","3")),(("x","b"),("1","4"))]))
        env.set_value("p", frozenset([("x","1")]))
        env.set_value("q", frozenset([("a","3"),("b","4")]))
        assert interpret(root.children[0],env)

        env.set_value("p", frozenset([(1,11), (4,12)]))
        env.set_value("q", frozenset([(2,21), (7,22)]))
        env.set_value("f", frozenset([((1,2),(11,21)), ((1,7),(11,22)),((4,2),(12,21)), ((4,7),(12,22))]))
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
        env.set_value("ID", frozenset(["aa","bb"]))
        env.set_value("f", frozenset([("aa","bb"),("aa","aa"),("bb","aa"),("bb","bb")]))
        assert interpret(root.children[0],env)
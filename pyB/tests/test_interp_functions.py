# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from environment import Environment
from interp import interpret
from helpers import file_to_AST_str, string_to_file
from util import type_with_known_types
from parsing import str_ast_to_python_ast

file_name = "input.txt"

class TestInterpFunctions():
    def test_genAST_pred_part_fun(self):
        # Build AST:
        string_to_file("#PREDICATE F=S+->T", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        l = []
        l.append(frozenset([]))
        l.append(frozenset([("a","x")]))
        l.append(frozenset([("a","y")]))
        l.append(frozenset([("b","x")]))
        l.append(frozenset([("b","y")]))
        l.append(frozenset([("a","x"),("b","x")]))
        l.append(frozenset([("a","y"),("b","y")]))
        l.append(frozenset([("a","x"),("b","y")]))
        l.append(frozenset([("a","y"),("b","x")]))
        env = Environment()
        env.add_ids_to_frame(["S","T","F"])
        env.set_value("S", frozenset(["a","b"]))
        env.set_value("T", frozenset(["x","y"]))
        env.set_value("F", frozenset(l))
        assert interpret(root.children[0],env)

        l = []
        l.append(frozenset([("1","hallo_welt")]))
        l.append(frozenset([("2","hallo_welt")]))
        l.append(frozenset([("1","hallo_welt"),("2","hallo_welt")]))
        l.append(frozenset([]))
        env.set_value("S", frozenset(["1","2"]))
        env.set_value("T", frozenset(["hallo_welt",]))
        env.set_value("F", frozenset(l))
        assert interpret(root.children[0],env)


    def test_genAST_pred_total_fun(self):
        # Build AST:
        string_to_file("#PREDICATE F=S-->T", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        l = []
        l.append(frozenset([("a","x"),("b","x")]))
        l.append(frozenset([("a","y"),("b","y")]))
        l.append(frozenset([("a","x"),("b","y")]))
        l.append(frozenset([("a","y"),("b","x")]))
        env = Environment()
        env.add_ids_to_frame(["S","T","F"])
        env.set_value("S", frozenset(["a","b"]))
        env.set_value("T", frozenset(["x","y"]))
        env.set_value("F", frozenset(l))
        assert interpret(root.children[0],env)

        l = []
        l.append(frozenset([("1","hallo_welt"),("2","hallo_welt")]))
        env.set_value("S", frozenset(["1","2"]))
        env.set_value("T", frozenset(["hallo_welt",]))
        env.set_value("F", frozenset(l))
        assert interpret(root.children[0],env)


    def test_genAST_pred_part_inj_fun(self):
        # Build AST:
        string_to_file("#PREDICATE F=S>+>T", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        l = []
        l.append(frozenset([]))
        l.append(frozenset([("a","x")]))
        l.append(frozenset([("a","y")]))
        l.append(frozenset([("b","x")]))
        l.append(frozenset([("b","y")]))
        l.append(frozenset([("a","x"),("b","y")]))
        l.append(frozenset([("a","y"),("b","x")]))
        env = Environment()
        env.add_ids_to_frame(["S","T","F"])
        env.set_value("S", frozenset(["a","b"]))
        env.set_value("T", frozenset(["x","y"]))
        env.set_value("F", frozenset(l))
        assert interpret(root.children[0],env)

        l = []
        l.append(frozenset([("1","hallo_welt")]))
        l.append(frozenset([("2","hallo_welt")]))
        l.append(frozenset([]))
        env.set_value("S", frozenset(["1","2"]))
        env.set_value("T", frozenset(["hallo_welt",]))
        env.set_value("F", frozenset(l))
        assert interpret(root.children[0],env)


    def test_genAST_pred_total_inj_fun(self):
        # Build AST:
        string_to_file("#PREDICATE F=S>->T", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        l = []
        l.append(frozenset([("a","x"),("b","y")]))
        l.append(frozenset([("a","y"),("b","x")]))
        env = Environment()
        env.add_ids_to_frame(["S","T","F"])
        env.set_value("S", frozenset(["a","b"]))
        env.set_value("T", frozenset(["x","y"]))
        env.set_value("F", frozenset(l))
        assert interpret(root.children[0],env)


    def test_genAST_pred_part_surj_fun(self):
        # Build AST:
        string_to_file("#PREDICATE F=S+->>T", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        l = []
        l.append(frozenset([("a","x"),("b","y")]))
        l.append(frozenset([("a","y"),("b","x")]))
        env = Environment()
        env.add_ids_to_frame(["S","T","F"])
        env.set_value("S", frozenset(["a","b"]))
        env.set_value("T", frozenset(["x","y"]))
        env.set_value("F", frozenset(l))
        assert interpret(root.children[0],env)

        l = []
        l.append(frozenset([("1","hallo_welt")]))
        l.append(frozenset([("2","hallo_welt")]))
        l.append(frozenset([("1","hallo_welt"),("2","hallo_welt")]))
        env.set_value("S", frozenset(["1","2"]))
        env.set_value("T", frozenset(["hallo_welt",]))
        env.set_value("F", frozenset(l))
        assert interpret(root.children[0],env)


    def test_genAST_pred_total_surj_fun(self):
        # Build AST:
        string_to_file("#PREDICATE F=S-->>T", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        l = []
        l.append(frozenset([("a","x"),("b","y")]))
        l.append(frozenset([("a","y"),("b","x")]))
        env = Environment()
        env.add_ids_to_frame(["S","T","F"])
        env.set_value("S", frozenset(["a","b"]))
        env.set_value("T", frozenset(["x","y"]))
        env.set_value("F", frozenset(l))
        assert interpret(root.children[0],env)

        l = []
        l.append(frozenset([("1","hallo_welt"),("2","hallo_welt")]))
        env.set_value("S", frozenset(["1","2"]))
        env.set_value("T", frozenset(["hallo_welt",]))
        env.set_value("F", frozenset(l))
        assert interpret(root.children[0],env)


    def test_genAST_pred_part_bij_fun(self):
        # Build AST
        string_to_file("#PREDICATE F=S>+>>T", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        env = Environment()
        env.add_ids_to_frame(["S","T","F"])
        env.set_value("S", frozenset(["a","b"]))
        env.set_value("T", frozenset(["x","y","z"]))
        env.set_value("F", frozenset([]))
        assert interpret(root.children[0],env)

        env.set_value("S", frozenset(["a","b"]))
        env.set_value("T", frozenset(["x","y"]))
        l = [frozenset([("a","x"),("b","y")])]
        l.append(frozenset([("a","y"),("b","x")]))
        env.set_value("F", frozenset(l))
        assert interpret(root.children[0],env)

        env.set_value("S", frozenset(["a","b","c"]))
        env.set_value("T", frozenset(["x","y"]))
        l = [frozenset([("a","x"),("b","y")])]
        l.append(frozenset([("a","x"),("c","y")]))
        l.append(frozenset([("a","y"),("b","x")]))
        l.append(frozenset([("a","y"),("c","x")]))
        l.append(frozenset([("b","x"),("c","y")]))
        l.append(frozenset([("b","y"),("c","x")]))
        env.set_value("F", frozenset(l))
        assert interpret(root.children[0],env)

    def test_genAST_pred_bij_fun(self):
        # Build AST:
        string_to_file("#PREDICATE F=S>->>T", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        l = []
        l.append(frozenset([("a","x"),("b","y"),("c","z")]))
        l.append(frozenset([("a","y"),("b","x"),("c","z")]))
        l.append(frozenset([("a","z"),("b","y"),("c","x")]))
        l.append(frozenset([("a","x"),("b","z"),("c","y")]))
        l.append(frozenset([("a","y"),("b","z"),("c","x")]))
        l.append(frozenset([("a","z"),("b","x"),("c","y")]))
        env = Environment()
        env.add_ids_to_frame(["S","T","F"])
        env.set_value("S", frozenset(["a","b","c"]))
        env.set_value("T", frozenset(["x","y","z"]))
        env.set_value("F", frozenset(l))
        assert interpret(root.children[0],env)

        env.set_value("S", frozenset(["1","2"]))
        env.set_value("T", frozenset(["hallo_welt",]))
        env.set_value("F", frozenset([]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_bij_fun2(self):
        # Build AST:
        string_to_file("#PREDICATE F=S>->>T>->>U", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        l = [frozenset([(frozenset([('x2', 'y1'), ('x1', 'y2')]), 'z1'), (frozenset([('x1', 'y1'), ('x2', 'y2')]), 'z2')]), frozenset([(frozenset([('x1', 'y1'), ('x2', 'y2')]), 'z1'), (frozenset([('x2', 'y1'), ('x1', 'y2')]), 'z2')])]
        env = Environment()
        env.add_ids_to_frame(["S","T","F","U"])
        env.set_value("S", frozenset(["x1","x2"]))
        env.set_value("T", frozenset(["y1","y2"]))
        env.set_value("U", frozenset(["z1","z2"]))
        env.set_value("F", frozenset(l))
        assert interpret(root.children[0],env)


    def test_genAST_pred_fun_app(self):
        # Build AST:
        string_to_file("#PREDICATE f={(a,x),(b,y)} & f(b)=y", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        env = Environment()
        env.add_ids_to_frame(["a","b","x","y","f"])
        env.set_value("a", "a")
        env.set_value("b", "b")
        env.set_value("x", "x")
        env.set_value("y", "y")
        env.set_value("f", frozenset([("a","x"),("b","y")]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_fun_app2(self):
        # Build AST:
        string_to_file("#PREDICATE f:S*T>->>V & x:S*T & f(x)=y", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        env = Environment()
        env.add_ids_to_frame(["S","T","f","V","x","y"])
        env.set_value("S", frozenset(["x1","x2"]))
        env.set_value("T", frozenset(["y1","y2"]))
        env.set_value("V", frozenset(["z1","z2","z3","z4"]))
        env.set_value("x", ("x1","y1"))
        env.set_value("f", frozenset([(("x1","y1"),"z1"),(("x2","y2"),"z2"),(("x1","y2"),"z3"),(("x2","y1"),"z4")]))
        env.set_value("y", "z1")
        assert interpret(root.children[0],env)


    def test_genAST_pred_fun_app3(self):
        # Build AST:
        string_to_file("#PREDICATE f={((1,1),42),((2,2),777)} & zz=f(1,1)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        env = Environment()
        env.add_ids_to_frame(["zz","f"])
        env.set_value("f", frozenset([((1,1),42),((2,2),777)]))
        env.set_value("zz", 42)
        assert interpret(root.children[0],env)


    def test_genAST_pred_fun_app4(self):
        # Build AST:
        string_to_file("#PREDICATE f={((1,1,1),42),((2,2,2),777)} & zz=f(2,2,2)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        env = Environment()
        env.add_ids_to_frame(["zz","f"])
        env.set_value("f", frozenset([(((1,1),1),42),(((2,2),2),777)]))
        env.set_value("zz", 777)
        assert interpret(root.children[0],env)


    def test_genAST_pred_fun_app5(self):
        # Build AST:
        string_to_file("#PREDICATE f={(2,42),(1,777)} & #z.(z:NAT & 42=f(z))", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        env = Environment()
        env.add_ids_to_frame(["f"])
        type_with_known_types(root.children[0], env, [], ["f"])
        assert interpret(root.children[0],env)


    def test_genAST_pred_seq_empty(self):
        # Build AST:
        string_to_file("#PREDICATE []={}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        env = Environment()
        assert interpret(root.children[0],env)


    def test_genAST_lambda(self):
        # Build AST
        string_to_file("#PREDICATE f="+"%"+"x.(x>0 & x<4|x*x)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        env = Environment()
        env.add_ids_to_frame(["f"])
        type_with_known_types(root, env, [], ["f","x"])
        env.set_value("f", frozenset([(1,1),(2,4),(3,9)]))
        assert interpret(root.children[0],env)


    def test_genAST_lambda2(self):
        # Build AST
        string_to_file("#PREDICATE f="+"%"+"x,y,z.(x:1..2 & y:1..2 & z:1..2|x+y+z)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        env = Environment()
        env.add_ids_to_frame(["f"])
        type_with_known_types(root, env, [], ["f","x"])
        env.set_value("f", frozenset([(((1,1),1),3),(((1,1),2),4),(((1,2),1),4),(((2,1),1),4),(((1,2),2),5),(((2,2),1),5),(((2,1),2),5),(((2,2),2),6)]))
        assert interpret(root.children[0],env)

    def test_genAST_pred_seq_simple(self):
        # Build AST:
        string_to_file("#PREDICATE s:seq(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        env = Environment()
        env.add_ids_to_frame(["s","S"])
        env.set_value("S", frozenset(["a","b"]))
        env.set_value("s", frozenset([]))
        assert interpret(root.children[0],env)

        env.set_value("s", frozenset([(1,"a")]))
        assert interpret(root.children[0],env)

        env.set_value("s", frozenset([(1,"a"),(2,"b"),(3,"a")]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_seq_no_empty(self):
        # Build AST:
        string_to_file("#PREDICATE s:seq1(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        env = Environment()
        env.add_ids_to_frame(["s","S"])
        env.set_value("S", frozenset(["a","b"]))
        env.set_value("s", frozenset([]))
        assert not interpret(root.children[0],env)

        env.set_value("s", frozenset([(1,"a")]))
        assert interpret(root.children[0],env)

        env.set_value("s", frozenset([(1,"b"),(2,"a"),(3,"b")]))
        assert interpret(root.children[0],env)

        env.set_value("s", frozenset([(1,"a"),(1,"b"),(1,"a")]))
        assert not interpret(root.children[0],env)


    def test_genAST_pred_seq_injective(self):
        # Build AST:
        string_to_file("#PREDICATE s=iseq(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        env = Environment()
        env.add_ids_to_frame(["s","S"])
        env.set_value("S", frozenset(["a","b"]))
        env.set_value("s", frozenset([frozenset([(2, 'a'), (1, 'b')]), frozenset([(1, 'a')]), frozenset([(1, 'a'), (2, 'b')]), frozenset([]), frozenset([(1, 'b')])]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_seq_perm(self):
        # Build AST:
        string_to_file("#PREDICATE s=perm(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        env = Environment()
        env.add_ids_to_frame(["s","S"])
        env.set_value("S", frozenset(["a","b"]))
        env.set_value("s", frozenset([frozenset([(2, 'a'), (1, 'b')]), frozenset([(1, 'a'), (2, 'b')])]))
        assert interpret(root.children[0],env)

        env.set_value("s", frozenset([]))
        assert not interpret(root.children[0],env)


    def test_genAST_pred_seq_conc(self):
        # Build AST:
        string_to_file("#PREDICATE s:perm(S) & t:perm(S) => s^t:seq(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        env = Environment()
        env.add_ids_to_frame(["s","S","t"])
        env.set_value("S", frozenset(["a","b"]))
        env.set_value("s", frozenset([(2, 'a'), (1, 'b')]))
        env.set_value("t", frozenset([(1, 'a'), (2, 'b')]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_seq_prepend(self):
        # Build AST:
        string_to_file("#PREDICATE s:perm(S) => a->s:seq(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        env = Environment()
        env.add_ids_to_frame(["s","S","a"])
        env.set_value("S", frozenset(["a","b"]))
        env.set_value("s", frozenset([(2, 'a'), (1, 'b')]))
        env.set_value("a", "a")
        assert interpret(root.children[0],env)


    def test_genAST_pred_seq_append(self):
        # Build AST:
        string_to_file("#PREDICATE s:perm(S) => s<-a:seq(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        env = Environment()
        env.add_ids_to_frame(["s","S","a"])
        env.set_value("S", frozenset(["a","b"]))
        env.set_value("s", frozenset([(2, 'a'), (1, 'b')]))
        env.set_value("a", "a")
        assert interpret(root.children[0],env)


    def test_genAST_pred_seq_size(self):
        # Build AST:
        string_to_file("#PREDICATE s=[a,b] & size(s)=2", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        env = Environment()
        env.add_ids_to_frame(["a","b","s"])
        env.set_value("s", frozenset([(1, 'a'), (2, 'b')]))
        env.set_value("a", "a")
        env.set_value("b", "b")
        assert interpret(root.children[0],env)


    def test_genAST_pred_seq_reverse(self):
        # Build AST:
        string_to_file("#PREDICATE s=[a,b] & rev(s)=[b,a]", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        env = Environment()
        env.add_ids_to_frame(["a","b","s"])
        env.set_value("s", frozenset([(1, 'a'), (2, 'b')]))
        env.set_value("a", "a")
        env.set_value("b", "b")
        assert interpret(root.children[0],env)


    def test_genAST_pred_seq_take(self):
        # Build AST:
        string_to_file("#PREDICATE s=[a,b,c,d,e]/|\\3", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        env = Environment()
        env.add_ids_to_frame(["a","b","c","d","e","s"])
        env.set_value("s", frozenset([(1, 'a'), (2, 'b')]))
        env.set_value("a", "a")
        env.set_value("b", "b")
        env.set_value("c", "c")
        env.set_value("d", "d")
        env.set_value("e", "e")
        assert interpret(root.children[0],env)


    def test_genAST_pred_seq_drop(self):
        # Build AST:
        string_to_file("#PREDICATE s=[a,b,c,d,e]\\|/3", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        env = Environment()
        env.add_ids_to_frame(["a","b","c","d","e","s"])
        env.set_value("s", frozenset([(1, 'd'), (2, 'e')]))
        env.set_value("a", "a")
        env.set_value("b", "b")
        env.set_value("c", "c")
        env.set_value("d", "d")
        env.set_value("e", "e")
        assert interpret(root.children[0],env)


    def test_genAST_pred_seq_first(self):
        # Build AST:
        string_to_file("#PREDICATE s=[a,b,c,d,e] & first(s)=a", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        env = Environment()
        env.add_ids_to_frame(["a","b","c","d","e","s"])
        env.set_value("s", frozenset([(1, 'a'), (2, 'b'),(3, 'c'), (4, 'd'),(5,'e')]))
        env.set_value("a", "a")
        env.set_value("b", "b")
        env.set_value("c", "c")
        env.set_value("d", "d")
        env.set_value("e", "e")
        assert interpret(root.children[0],env)


    def test_genAST_pred_seq_last(self):
        # Build AST:
        string_to_file("#PREDICATE s=[a,b,c,d,e] & last(s)=e", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        env = Environment()
        env.add_ids_to_frame(["a","b","c","d","e","s"])
        env.set_value("s", frozenset([(1, 'a'), (2, 'b'),(3, 'c'), (4, 'd'),(5,'e')]))
        env.set_value("a", "a")
        env.set_value("b", "b")
        env.set_value("c", "c")
        env.set_value("d", "d")
        env.set_value("e", "e")
        assert interpret(root.children[0],env)


    def test_genAST_pred_seq_tail(self):
        # Build AST:
        string_to_file("#PREDICATE s=[a,b,c,d,e] & tail(s)=t", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        env = Environment()
        env.add_ids_to_frame(["a","b","c","d","e","s","t"])
        env.set_value("s", frozenset([(1, 'a'), (2, 'b'),(3, 'c'), (4, 'd'),(5,'e')]))
        env.set_value("t", frozenset([ (2, 'b'),(3, 'c'), (4, 'd'),(5,'e')]))
        env.set_value("a", "a")
        env.set_value("b", "b")
        env.set_value("c", "c")
        env.set_value("d", "d")
        env.set_value("e", "e")
        assert interpret(root.children[0],env)


    def test_genAST_pred_seq_front(self):
        # Build AST:
        string_to_file("#PREDICATE s=[a,b,c,d,e] & front(s)=t", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        env = Environment()
        env.add_ids_to_frame(["a","b","c","d","e","s","t"])
        env.set_value("s", frozenset([(1, 'a'), (2, 'b'),(3, 'c'), (4, 'd'),(5,'e')]))
        env.set_value("t", frozenset([(1, 'a'), (2, 'b'),(3, 'c'), (4, 'd')])) 
        env.set_value("a", "a")
        env.set_value("b", "b")
        env.set_value("c", "c")
        env.set_value("d", "d")
        env.set_value("e", "e")
        assert interpret(root.children[0],env)


    def test_genAST_pred_seq_of_seq(self):
        # Build AST:
        string_to_file("#PREDICATE s:perm(perm(S))", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        env = Environment()
        env.add_ids_to_frame(["S","s"])
        env.set_value("S", frozenset(["a","b"]))
        env.set_value("s", frozenset([(2, frozenset([(1, 'a'), (2, 'b')])), (1, frozenset([(2, 'a'), (1, 'b')]))]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_seq_conc(self):
        # Build AST:
        string_to_file("#PREDICATE s:perm(perm(S)) & t=conc(s)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        env = Environment()
        env.add_ids_to_frame(["t","s","S"])
        env.set_value("S", frozenset(["a","b"]))
        env.set_value("s", frozenset([(2, frozenset([(1, 'a'), (2, 'b')])), (1, frozenset([(2, 'a'), (1, 'b')]))]))
        env.set_value("t", frozenset([(1, 'b'),(2, 'a'),(3, 'a'),(4, 'b')]))
        assert interpret(root.children[0],env)


    def test_genAST_pred_fnc_expr(self):
        # Build AST
        string_to_file("#PREDICATE R1 = {(0|->1), (0|->2), (1|->1), (1|->7), (2|->3)} & f= fnc(R1)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env.add_ids_to_frame(["R1","f"])
        assert interpret(root.children[0],env)
        assert env.get_value("f") == frozenset([(0,frozenset([1,2])),(1,frozenset([1,7])),(2,frozenset([3]))])


    def test_large_function(self):
        # Build AST
        string_to_file("#PREDICATE {}:INT+->>INT", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert not interpret(root.children[0], env)
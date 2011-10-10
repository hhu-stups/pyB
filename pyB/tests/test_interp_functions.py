# -*- coding: utf-8 -*-
from ast_nodes import *
from interp import interpret, Environment
from helpers import file_to_AST_str, string_to_file

file_name = "input.txt"

class TestInterpFunctions():
    def test_genAST_pred_part_fun(self):
        # Build AST:
        string_to_file("#PREDICATE F=S+->T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

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
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["T"] = set(["x","y"])
        env.variable_values["F"] = set(l)
        assert interpret(root,env)

        l = []
        l.append(frozenset([("1","hallo_welt")]))
        l.append(frozenset([("2","hallo_welt")]))
        l.append(frozenset([("1","hallo_welt"),("2","hallo_welt")]))
        l.append(frozenset([]))
        env.variable_values["S"] = set(["1","2"])
        env.variable_values["T"] = set(["hallo_welt",])
        env.variable_values["F"] = set(l)
        assert interpret(root,env)


    def test_genAST_pred_total_fun(self):
        # Build AST:
        string_to_file("#PREDICATE F=S-->T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        l = []
        l.append(frozenset([("a","x"),("b","x")]))
        l.append(frozenset([("a","y"),("b","y")]))
        l.append(frozenset([("a","x"),("b","y")]))
        l.append(frozenset([("a","y"),("b","x")]))
        env = Environment()
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["T"] = set(["x","y"])
        env.variable_values["F"] = set(l)
        assert interpret(root,env)

        l = []
        l.append(frozenset([("1","hallo_welt"),("2","hallo_welt")]))
        env.variable_values["S"] = set(["1","2"])
        env.variable_values["T"] = set(["hallo_welt",])
        env.variable_values["F"] = set(l)
        assert interpret(root,env)

    def test_genAST_pred_part_inj_fun(self):
        # Build AST:
        string_to_file("#PREDICATE F=S>+>T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        l = []
        l.append(frozenset([]))
        l.append(frozenset([("a","x")]))
        l.append(frozenset([("a","y")]))
        l.append(frozenset([("b","x")]))
        l.append(frozenset([("b","y")]))
        l.append(frozenset([("a","x"),("b","y")]))
        l.append(frozenset([("a","y"),("b","x")]))
        env = Environment()
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["T"] = set(["x","y"])
        env.variable_values["F"] = set(l)
        assert interpret(root,env)

        l = []
        l.append(frozenset([("1","hallo_welt")]))
        l.append(frozenset([("2","hallo_welt")]))
        l.append(frozenset([]))
        env.variable_values["S"] = set(["1","2"])
        env.variable_values["T"] = set(["hallo_welt",])
        env.variable_values["F"] = set(l)
        assert interpret(root,env)


    def test_genAST_pred_total_inj_fun(self):
        # Build AST:
        string_to_file("#PREDICATE F=S>->T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        l = []
        l.append(frozenset([("a","x"),("b","y")]))
        l.append(frozenset([("a","y"),("b","x")]))
        env = Environment()
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["T"] = set(["x","y"])
        env.variable_values["F"] = set(l)
        assert interpret(root,env)


    def test_genAST_pred_part_surj_fun(self):
        # Build AST:
        string_to_file("#PREDICATE F=S+->>T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        l = []
        l.append(frozenset([("a","x"),("b","y")]))
        l.append(frozenset([("a","y"),("b","x")]))
        env = Environment()
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["T"] = set(["x","y"])
        env.variable_values["F"] = set(l)
        assert interpret(root,env)

        l = []
        l.append(frozenset([("1","hallo_welt")]))
        l.append(frozenset([("2","hallo_welt")]))
        l.append(frozenset([("1","hallo_welt"),("2","hallo_welt")]))
        env.variable_values["S"] = set(["1","2"])
        env.variable_values["T"] = set(["hallo_welt",])
        env.variable_values["F"] = set(l)
        assert interpret(root,env)


    def test_genAST_pred_total_surj_fun(self):
        # Build AST:
        string_to_file("#PREDICATE F=S-->>T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        l = []
        l.append(frozenset([("a","x"),("b","y")]))
        l.append(frozenset([("a","y"),("b","x")]))
        env = Environment()
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["T"] = set(["x","y"])
        env.variable_values["F"] = set(l)
        assert interpret(root,env)

        l = []
        l.append(frozenset([("1","hallo_welt"),("2","hallo_welt")]))
        env.variable_values["S"] = set(["1","2"])
        env.variable_values["T"] = set(["hallo_welt",])
        env.variable_values["F"] = set(l)
        assert interpret(root,env)

    def test_genAST_pred_bij_fun(self):
        # Build AST:
        string_to_file("#PREDICATE F=S>->>T", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        l = []
        l.append(frozenset([("a","x"),("b","y"),("c","z")]))
        l.append(frozenset([("a","y"),("b","x"),("c","z")]))
        l.append(frozenset([("a","z"),("b","y"),("c","x")]))
        l.append(frozenset([("a","x"),("b","z"),("c","y")]))
        l.append(frozenset([("a","y"),("b","z"),("c","x")]))
        l.append(frozenset([("a","z"),("b","x"),("c","y")]))
        env = Environment()
        env.variable_values["S"] = set(["a","b","c"])
        env.variable_values["T"] = set(["x","y","z"])
        env.variable_values["F"] = set(l)
        assert interpret(root,env)

        env.variable_values["S"] = set(["1","2"])
        env.variable_values["T"] = set(["hallo_welt",])
        env.variable_values["F"] = set([])
        assert interpret(root,env)


    def test_genAST_pred_bij_fun2(self):
        # Build AST:
        string_to_file("#PREDICATE F=S>->>T>->>U", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        l = [frozenset([(frozenset([('x2', 'y1'), ('x1', 'y2')]), 'z1'), (frozenset([('x1', 'y1'), ('x2', 'y2')]), 'z2')]), frozenset([(frozenset([('x1', 'y1'), ('x2', 'y2')]), 'z1'), (frozenset([('x2', 'y1'), ('x1', 'y2')]), 'z2')])]
        env = Environment()
        env.variable_values["S"] = set(["x1","x2"])
        env.variable_values["T"] = set(["y1","y2"])
        env.variable_values["U"] = set(["z1","z2"])
        env.variable_values["F"] = set(l)
        assert interpret(root,env)


    def test_genAST_pred_fun_app(self):
        # Build AST:
        string_to_file("#PREDICATE f={(a,x),(b,y)} & f(b)=y", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["a"] = "a"
        env.variable_values["b"] = "b"
        env.variable_values["x"] = "x"
        env.variable_values["y"] = "y"
        env.variable_values["f"] = set([("a","x"),("b","y")])
        assert interpret(root,env)


    def test_genAST_pred_fun_app2(self):
        # Build AST:
        string_to_file("#PREDICATE f:S*T>->>V & x:S*T & f(x)=y", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["S"] = set(["x1","x2"])
        env.variable_values["T"] = set(["y1","y2"])
        env.variable_values["V"] = set(["z1","z2","z3","z4"])
        env.variable_values["x"] = ("x1","y1")
        env.variable_values["f"] = frozenset([(("x1","y1"),"z1"),(("x2","y2"),"z2"),(("x1","y2"),"z3"),(("x2","y1"),"z4")])
        env.variable_values["y"] = "z1"
        assert interpret(root,env)


    def test_genAST_pred_seq_empty(self):
        # Build AST:
        string_to_file("#PREDICATE []={}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        assert interpret(root,env)


    def test_genAST_pred_seq_simple(self):
        # Build AST:
        string_to_file("#PREDICATE s:seq(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["s"] = frozenset([])
        assert interpret(root,env)

        env.variable_values["s"] = frozenset([(1,"a")])
        assert interpret(root,env)

        env.variable_values["s"] = frozenset([(1,"a"),(2,"b"),(3,"a")])
        assert interpret(root,env)


    def test_genAST_pred_seq_no_empty(self):
        # Build AST:
        string_to_file("#PREDICATE s:seq1(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["s"] = frozenset([])
        assert not interpret(root,env)

        env.variable_values["s"] = frozenset([(1,"a")])
        assert interpret(root,env)

        env.variable_values["s"] = frozenset([(1,"b"),(2,"a"),(3,"b")])
        assert interpret(root,env)

        env.variable_values["s"] = frozenset([(1,"a"),(1,"b"),(1,"a")])
        assert not interpret(root,env)


    def test_genAST_pred_seq_injective(self):
        # Build AST:
        string_to_file("#PREDICATE s=iseq(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["s"] = set([frozenset([(2, 'a'), (1, 'b')]), frozenset([(1, 'a')]), frozenset([(1, 'a'), (2, 'b')]), frozenset([]), frozenset([(1, 'b')])])
        assert interpret(root,env)

    def test_genAST_pred_seq_perm(self):
        # Build AST:
        string_to_file("#PREDICATE s=perm(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["s"] = set([frozenset([(2, 'a'), (1, 'b')]), frozenset([(1, 'a'), (2, 'b')])])
        assert interpret(root,env)

        env.variable_values["s"] = frozenset([])
        assert not interpret(root,env)

    def test_genAST_pred_seq_conc(self):
        # Build AST:
        string_to_file("#PREDICATE s:perm(S) & t:perm(S) => s^t:seq(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["s"] = frozenset([(2, 'a'), (1, 'b')]) 
        env.variable_values["t"] = frozenset([(1, 'a'), (2, 'b')])
        assert interpret(root,env)

    def test_genAST_pred_seq_prepend(self):
        # Build AST:
        string_to_file("#PREDICATE s:perm(S) => a->s:seq(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["s"] = frozenset([(2, 'a'), (1, 'b')]) 
        env.variable_values["a"] = "a"
        assert interpret(root,env)


    def test_genAST_pred_seq_append(self):
        # Build AST:
        string_to_file("#PREDICATE s:perm(S) => s<-a:seq(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["S"] = set(["a","b"])
        env.variable_values["s"] = frozenset([(2, 'a'), (1, 'b')]) 
        env.variable_values["a"] = "a"
        assert interpret(root,env)


    def test_genAST_pred_seq_size(self):
        # Build AST:
        string_to_file("#PREDICATE s=[a,b] & size(s)=2", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["s"] = frozenset([(1, 'a'), (2, 'b')]) 
        env.variable_values["a"] = "a"
        env.variable_values["b"] = "b"
        assert interpret(root,env)


    def test_genAST_pred_seq_reverse(self):
        # Build AST:
        string_to_file("#PREDICATE s=[a,b] & rev(s)=[b,a]", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["s"] = frozenset([(1, 'a'), (2, 'b')]) 
        env.variable_values["a"] = "a"
        env.variable_values["b"] = "b"
        assert interpret(root,env)


    def test_genAST_pred_seq_take(self):
        # Build AST:
        string_to_file("#PREDICATE s=[a,b,c,d,e]/|\\3", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["s"] = frozenset([(1, 'a'), (2, 'b')]) 
        env.variable_values["a"] = "a"
        env.variable_values["b"] = "b"
        env.variable_values["c"] = "c"
        env.variable_values["d"] = "d"
        env.variable_values["e"] = "e"
        assert interpret(root,env)


    def test_genAST_pred_seq_drop(self):
        # Build AST:
        string_to_file("#PREDICATE s=[a,b,c,d,e]\\|/3", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["s"] = frozenset([(1, 'd'), (2, 'e')]) 
        env.variable_values["a"] = "a"
        env.variable_values["b"] = "b"
        env.variable_values["c"] = "c"
        env.variable_values["d"] = "d"
        env.variable_values["e"] = "e"
        assert interpret(root,env)


    def test_genAST_pred_seq_first(self):
        # Build AST:
        string_to_file("#PREDICATE s=[a,b,c,d,e] & first(s)=a", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["s"] = frozenset([(1, 'a'), (2, 'b'),(3, 'c'), (4, 'd'),(5,'e')]) 
        env.variable_values["a"] = "a"
        env.variable_values["b"] = "b"
        env.variable_values["c"] = "c"
        env.variable_values["d"] = "d"
        env.variable_values["e"] = "e"
        assert interpret(root,env)


    def test_genAST_pred_seq_last(self):
        # Build AST:
        string_to_file("#PREDICATE s=[a,b,c,d,e] & last(s)=e", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["s"] = frozenset([(1, 'a'), (2, 'b'),(3, 'c'), (4, 'd'),(5,'e')]) 
        env.variable_values["a"] = "a"
        env.variable_values["b"] = "b"
        env.variable_values["c"] = "c"
        env.variable_values["d"] = "d"
        env.variable_values["e"] = "e"
        assert interpret(root,env)


    def test_genAST_pred_seq_tail(self):
        # Build AST:
        string_to_file("#PREDICATE s=[a,b,c,d,e] & tail(s)=t", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["s"] = frozenset([(1, 'a'), (2, 'b'),(3, 'c'), (4, 'd'),(5,'e')])
        env.variable_values["t"] = frozenset([ (2, 'b'),(3, 'c'), (4, 'd'),(5,'e')]) 
        env.variable_values["a"] = "a"
        env.variable_values["b"] = "b"
        env.variable_values["c"] = "c"
        env.variable_values["d"] = "d"
        env.variable_values["e"] = "e"
        assert interpret(root,env)


    def test_genAST_pred_seq_front(self):
        # Build AST:
        string_to_file("#PREDICATE s=[a,b,c,d,e] & front(s)=t", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        env.variable_values["s"] = frozenset([(1, 'a'), (2, 'b'),(3, 'c'), (4, 'd'),(5,'e')])
        env.variable_values["t"] = frozenset([(1, 'a'), (2, 'b'),(3, 'c'), (4, 'd')]) 
        env.variable_values["a"] = "a"
        env.variable_values["b"] = "b"
        env.variable_values["c"] = "c"
        env.variable_values["d"] = "d"
        env.variable_values["e"] = "e"
        assert interpret(root,env)
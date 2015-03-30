# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from environment import Environment
from typing import type_check_bmch
from util import type_with_known_types, get_type_by_name
from parsing import parse_ast, str_ast_to_python_ast
from helpers import file_to_AST_str, string_to_file

from config import USE_COSTUM_FROZENSET
if USE_COSTUM_FROZENSET:
     from rpython_b_objmodel import frozenset

file_name = "input.txt"

class TestTypesRelations():
    def test_types_relation(self):
        # Build AST
        string_to_file("#PREDICATE r=S<->T", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X"))),("T", PowerSetType(SetType("X")))]
        type_with_known_types(root, env, lst, ["r"])
        assert isinstance(get_type_by_name(env, "r"), PowerSetType)
        assert isinstance(get_type_by_name(env, "r").data, PowerSetType)
        assert isinstance(get_type_by_name(env, "r").data.data, CartType)
        assert isinstance(get_type_by_name(env, "r").data.data.data[0].data, SetType)
        assert isinstance(get_type_by_name(env, "r").data.data.data[1].data, SetType)


    def test_types_relation_set_enum(self):
        # Build AST
        string_to_file("#PREDICATE r = {8|->10, 7|->11, 2|->11, 6|->12}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["r"])
        assert isinstance(get_type_by_name(env, "r"), PowerSetType)
        assert isinstance(get_type_by_name(env, "r").data, CartType)
        assert isinstance(get_type_by_name(env, "r").data.data[0].data, IntegerType)
        assert isinstance(get_type_by_name(env, "r").data.data[1].data, IntegerType)


    def test_types_domain(self):
        # Build AST
        string_to_file("#PREDICATE r:S<->T & x:dom(r)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X"))),("T", PowerSetType(SetType("Y")))]
        type_with_known_types(root, env, lst, ["r","x"])
        assert isinstance(get_type_by_name(env, "x"), SetType)
        assert get_type_by_name(env, "x").data == "X"


    def test_types_dom_unify(self):
        # Build AST
        string_to_file("#PREDICATE d=A*B & c=dom(d) & A=NAT & B=NAT", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        env = Environment()
        type_with_known_types(root, env, [], ["c","d","A","B"])
        assert isinstance(get_type_by_name(env, "A"), PowerSetType)
        assert isinstance(get_type_by_name(env, "B"), PowerSetType)
        assert isinstance(get_type_by_name(env, "c"), PowerSetType)
        assert isinstance(get_type_by_name(env, "d"), PowerSetType)
        assert isinstance(get_type_by_name(env, "d").data, CartType)


    def test_types_ran_unify(self):
        # Build AST
        string_to_file("#PREDICATE d=A*B & c=ran(d) & A=NAT & B=NAT", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        env = Environment()
        type_with_known_types(root, env, [], ["c","d","A","B"])
        assert isinstance(get_type_by_name(env, "A"), PowerSetType)
        assert isinstance(get_type_by_name(env, "B"), PowerSetType)
        assert isinstance(get_type_by_name(env, "c"), PowerSetType)
        assert isinstance(get_type_by_name(env, "d"), PowerSetType)
        assert isinstance(get_type_by_name(env, "d").data, CartType)


    def test_types_range(self):
        # Build AST
        string_to_file("#PREDICATE r:S<->T & x:ran(r)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X"))),("T", PowerSetType(SetType("Y")))]
        type_with_known_types(root, env, lst, ["r","x"])
        assert isinstance(get_type_by_name(env, "x"), SetType)
        assert get_type_by_name(env, "x").data == "Y"


    def test_types_fwd_comp(self):
        # Build AST
        string_to_file("#PREDICATE r0:S<->T & r1:T<->S & x:ran(r1;r0)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X"))),("T", PowerSetType(SetType("Y")))]
        type_with_known_types(root, env, lst, ["r0","r1","x"])
        assert isinstance(get_type_by_name(env, "x"), SetType)
        assert get_type_by_name(env, "x").data == "Y"


    def test_types_simple_identity(self):
        # Build AST
        string_to_file("#PREDICATE S=id(B)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("B", PowerSetType(SetType("X")))]
        type_with_known_types(root, env, lst, ["S"])
        assert isinstance(get_type_by_name(env, "S"), PowerSetType)
        assert isinstance(get_type_by_name(env, "S").data, CartType)
        assert isinstance(get_type_by_name(env, "S").data.data[0].data, SetType)
        assert isinstance(get_type_by_name(env, "S").data.data[1].data, SetType)


    def test_types_simple_iterate(self):
        # Build AST
        string_to_file("#PREDICATE f=iterate(r,n)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        l = [("r", PowerSetType(CartType(PowerSetType(IntegerType()),PowerSetType(IntegerType()))))]
        type_with_known_types(root, env, l, ["f","n"])
        assert isinstance(get_type_by_name(env, "f"), PowerSetType)
        assert isinstance(get_type_by_name(env, "f").data, CartType)
        assert isinstance(get_type_by_name(env, "r"), PowerSetType)
        assert isinstance(get_type_by_name(env, "r").data, CartType)
        assert isinstance(get_type_by_name(env, "n"), IntegerType)


    def test_types_simple_closure(self):
        # Build AST
        string_to_file("#PREDICATE f=closure(r)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        l = [("r", PowerSetType(CartType(PowerSetType(IntegerType()),PowerSetType(IntegerType()))))]
        type_with_known_types(root, env, l, ["f"])
        assert isinstance(get_type_by_name(env, "f"), PowerSetType)
        assert isinstance(get_type_by_name(env, "f").data, CartType)
        assert isinstance(get_type_by_name(env, "r"), PowerSetType)
        assert isinstance(get_type_by_name(env, "r").data, CartType)


    def test_types_simple_closure1(self):
        # Build AST
        string_to_file("#PREDICATE f=closure1(r)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        l = [("r", PowerSetType(CartType(PowerSetType(IntegerType()),PowerSetType(IntegerType()))))]
        type_with_known_types(root, env, l, ["f"])
        assert isinstance(get_type_by_name(env, "f"), PowerSetType)
        assert isinstance(get_type_by_name(env, "f").data, CartType)
        assert isinstance(get_type_by_name(env, "r"), PowerSetType)
        assert isinstance(get_type_by_name(env, "r").data, CartType)


    def test_types_simple_sub_res(self):
        # Build AST
        string_to_file("#PREDICATE r:A<->B & v=S <| r", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X"))),("A", PowerSetType(SetType("X"))),("B", PowerSetType(SetType("Y")))]
        type_with_known_types(root, env, lst, ["r","v"])
        assert isinstance(get_type_by_name(env, "v"), PowerSetType)
        assert isinstance(get_type_by_name(env, "v").data, CartType)


    def test_types_simple_rev(self):
        # Build AST
        string_to_file("#PREDICATE r:A<->B & f = r~ & x:dom(f)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("A", PowerSetType(SetType("X"))),("B", PowerSetType(SetType("Y")))]
        type_with_known_types(root, env, lst, ["r","x","f"])
        assert isinstance(get_type_by_name(env, "x"), SetType)
        assert get_type_by_name(env, "x").data =="Y"


    def test_types_simple_image(self):
        # Build AST
        string_to_file("#PREDICATE r:A<->B & S<:A & x:r[S]", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("A", PowerSetType(SetType("X"))),("B", PowerSetType(SetType("Y")))]
        type_with_known_types(root, env, lst, ["r","S","x"])
        assert isinstance(get_type_by_name(env, "S"), PowerSetType)
        assert isinstance(get_type_by_name(env, "S").data, SetType)
        assert get_type_by_name(env, "S").data.data =="X"
        assert isinstance(get_type_by_name(env, "x"), SetType)
        assert get_type_by_name(env, "x").data == "Y"


    def test_types_simple_overwrite(self):
        # Build AST
        string_to_file("#PREDICATE r1:A<->B & r2:A<->B & r3=r1<+r2", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("A", PowerSetType(SetType("X"))),("B", PowerSetType(SetType("Y")))]
        type_with_known_types(root, env, lst, ["r1","r2","r3"])
        assert isinstance(get_type_by_name(env, "r3"), PowerSetType)
        assert isinstance(get_type_by_name(env, "r3").data, CartType)
        assert get_type_by_name(env, "r3").data.data[0].data.data == "X"
        assert get_type_by_name(env, "r3").data.data[1].data.data == "Y"
        assert not get_type_by_name(env, "r1")=="r1"
        assert not get_type_by_name(env, "r2")=="r2"


    def test_types_simple_parprod(self):
        # Build AST
        string_to_file("#PREDICATE r1:A<->B & r2:C<->D & r3=(r1 || r2)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("A", PowerSetType(SetType("X"))),("B", PowerSetType(SetType("Y"))),("C", PowerSetType(SetType("M"))),("D", PowerSetType(SetType("N")))]
        type_with_known_types(root, env, lst, ["r1","r2","r3"])
        assert isinstance(get_type_by_name(env, "r3"), PowerSetType)
        assert isinstance(get_type_by_name(env, "r3").data, CartType)
        assert isinstance(get_type_by_name(env, "r3").data.data[0].data, CartType)
        assert isinstance(get_type_by_name(env, "r3").data.data[1].data, CartType)
        x = get_type_by_name(env, "r3").data.data[0].data.data[0].data
        y = get_type_by_name(env, "r3").data.data[0].data.data[1].data
        m = get_type_by_name(env, "r3").data.data[1].data.data[0].data
        n = get_type_by_name(env, "r3").data.data[1].data.data[1].data
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
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        # A and C POW(X)
        lst = [("A", PowerSetType(SetType("X"))),("B", PowerSetType(SetType("Y"))),("C", PowerSetType(SetType("X"))),("D", PowerSetType(SetType("Z")))]
        type_with_known_types(root, env, lst, ["r1","r2","r3"])
        assert isinstance(get_type_by_name(env, "r3"), PowerSetType)
        assert isinstance(get_type_by_name(env, "r3").data, CartType)
        x = get_type_by_name(env, "r3").data.data[0].data
        y = get_type_by_name(env, "r3").data.data[1].data.data[0].data
        z = get_type_by_name(env, "r3").data.data[1].data.data[1].data
        assert x.data == "X"
        assert y.data == "Y"
        assert z.data == "Z"
        assert isinstance(x, SetType)
        assert isinstance(y, SetType)
        assert isinstance(z, SetType)


    def test_types_simple_dirprod2(self):
        # Build AST
        string_to_file("#PREDICATE f = {7|->11} & g = {7|->20} & f >< g = {(7|->(11|->20))}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["f","g"])


    def test_types_simple_dirprod3(self):
        string = '''
        MACHINE Test
        SETS C; D; X ={a,b,c}
        CONSTANTS r1, r2, r3, A, B
        PROPERTIES r1:A<->C & r2:B<->D & r3=r1 >< r2 &  A<:X & B<:X
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        print ast_string
        root = str_ast_to_python_ast(ast_string)       
     
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)


    def test_types_simple_proj1(self):
        # Build AST
        string_to_file("#PREDICATE r=prj1(A,B)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("A", PowerSetType(SetType("X"))),("B", PowerSetType(SetType("Y")))]
        type_with_known_types(root, env, lst, ["r"])
        assert isinstance(get_type_by_name(env, "r"), PowerSetType)
        assert isinstance(get_type_by_name(env, "r").data, CartType)
        x = get_type_by_name(env, "r").data.data[0].data.data[0].data
        y = get_type_by_name(env, "r").data.data[0].data.data[1].data
        z = get_type_by_name(env, "r").data.data[1].data
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
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("A", PowerSetType(SetType("X"))),("B", PowerSetType(SetType("Y")))]
        type_with_known_types(root, env, lst, ["r"])
        assert isinstance(get_type_by_name(env, "r"), PowerSetType)
        assert isinstance(get_type_by_name(env, "r").data, CartType)
        x = get_type_by_name(env, "r").data.data[0].data.data[0].data
        y = get_type_by_name(env, "r").data.data[0].data.data[1].data
        z = get_type_by_name(env, "r").data.data[1].data
        assert isinstance(x, SetType)
        assert isinstance(y, SetType)
        assert isinstance(z, SetType)
        assert x.data == "X"
        assert y.data == "Y"
        assert z.data == "Y"


    def test_types_rel_repr(self):
        # Build AST:
        string_to_file("#PREDICATE f={aa|->aa, aa|->bb, bb|->bb, bb|->aa} & g=A*A", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("A", PowerSetType(SetType("X"))),("aa",SetType("X")),("bb",SetType("X"))]
        type_with_known_types(root, env, lst, ["f","g"])
        assert isinstance(get_type_by_name(env, "g"), PowerSetType)
        assert isinstance(get_type_by_name(env, "g").data, CartType)
        assert isinstance(get_type_by_name(env, "f"), PowerSetType)
        assert isinstance(get_type_by_name(env, "f").data, CartType)


    def test_types_rel_expr(self):
        # Build AST:
        string_to_file("#PREDICATE f1 = {(-1|->{0, 2}), (1|->{6, 8}), (3|->{3})} & r= rel(f1)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        type_with_known_types(root, env, [], ["f1","r"])
        assert isinstance(get_type_by_name(env, "f1"), PowerSetType)
        assert isinstance(get_type_by_name(env, "f1").data, CartType)
        assert isinstance(get_type_by_name(env, "f1").data.data[0].data, IntegerType)
        assert isinstance(get_type_by_name(env, "f1").data.data[1].data, PowerSetType)
        assert isinstance(get_type_by_name(env, "f1").data.data[1].data.data, IntegerType)
        assert isinstance(get_type_by_name(env, "r"), PowerSetType)
        assert isinstance(get_type_by_name(env, "r").data, CartType)
        assert isinstance(get_type_by_name(env, "r").data.data[0].data, IntegerType)
        assert isinstance(get_type_by_name(env, "r").data.data[1].data, IntegerType)


    def test_types_couple_element(self):
        string = '''
        MACHINE          Test
        VARIABLES        xx, aa, bb
        INVARIANT        xx<:INTEGER*NATURAL1 & (aa,bb): xx
        INITIALISATION   xx:={(1,2),(4,5)} ; aa:=1 ; bb:=2
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        assert isinstance(get_type_by_name(env, "xx"), PowerSetType)
        assert isinstance(get_type_by_name(env, "xx").data, CartType)
        assert isinstance(get_type_by_name(env, "xx").data.data[0], PowerSetType)
        assert isinstance(get_type_by_name(env, "xx").data.data[1], PowerSetType)
        assert isinstance(get_type_by_name(env, "xx").data.data[0].data, IntegerType)
        assert isinstance(get_type_by_name(env, "xx").data.data[1].data, IntegerType)
        assert isinstance(get_type_by_name(env, "aa"), IntegerType)
        assert isinstance(get_type_by_name(env, "bb"), IntegerType)


    def test_types_couple_element2(self):
        string = '''
        MACHINE         Test
        VARIABLES       xx, yy
        INVARIANT       xx<:(INTEGER*NATURAL1) & yy<:NAT*INTEGER*NATURAL1
        INITIALISATION  xx:={(1,2),(4,5)} ; yy:=%(n,d).((n,d) : xx| n+d)
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        assert isinstance(get_type_by_name(env, "xx"), PowerSetType)
        assert isinstance(get_type_by_name(env, "xx").data, CartType)
        assert isinstance(get_type_by_name(env, "xx").data.data[0], PowerSetType)
        assert isinstance(get_type_by_name(env, "xx").data.data[1], PowerSetType)
        assert isinstance(get_type_by_name(env, "xx").data.data[0].data, IntegerType)
        assert isinstance(get_type_by_name(env, "xx").data.data[1].data, IntegerType)

        
    def test_types_complex_function_image(self):
        string = '''
        MACHINE         Test
        VARIABLES       yy, xx
        INVARIANT       yy<:%aa.(aa:xx | prj1(INTEGER, INTEGER)(aa)) & xx<:INTEGER * NATURAL1 
        INITIALISATION  xx:={(1,2),(2,2)} ; yy:={((1,2),1),((2,2),2)}
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)     
 
 
    def test_types_complex_function_image2(self):
        string = '''
        MACHINE         Test
        VARIABLES       yy, xx
        INVARIANT       yy<:%aa,bb.((aa,bb):xx | prj1(INTEGER, INTEGER)(aa,bb)) & xx<:INTEGER * NATURAL1 
        INITIALISATION  xx:={(1,2),(2,2)} ; yy:={((1,2),1),((2,2),2)}
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)       


    def test_types_complex_function_image3(self):
        string = '''
        MACHINE         Test
        VARIABLES       f,g
        INVARIANT       g<:%aa,bb,cc.((aa,bb):NAT1*NAT &cc:NAT| f(cc, aa, bb)) & f<: NAT * NAT1 * NAT * NAT  
        INITIALISATION  f:={(1,1,1,1),(1,1,1,1)} ; g:={}
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        assert isinstance(get_type_by_name(env, "g"), PowerSetType)
        assert isinstance(get_type_by_name(env, "g").data, CartType)
        assert isinstance(get_type_by_name(env, "g").data.data[0], PowerSetType)
        assert isinstance(get_type_by_name(env, "g").data.data[1], PowerSetType)
        assert isinstance(get_type_by_name(env, "g").data.data[0].data, CartType)
        assert isinstance(get_type_by_name(env, "g").data.data[1].data, IntegerType)
        
 
    def test_types_complex_function_image4(self):
        string = '''
        MACHINE         Test
        VARIABLES       f,g
        INVARIANT       g<:%aa,bb,cc.((aa,bb):NAT1*NAT &cc:NAT| f(cc |-> aa |-> bb)) & f<: NAT * NAT1 * NAT * NAT 
        INITIALISATION  f:={(1,1,1,1),(1,1,1,1)} ; g:={}
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) 
        assert isinstance(get_type_by_name(env, "g"), PowerSetType)
        assert isinstance(get_type_by_name(env, "g").data, CartType)
        assert isinstance(get_type_by_name(env, "g").data.data[0], PowerSetType)
        assert isinstance(get_type_by_name(env, "g").data.data[1], PowerSetType)
        assert isinstance(get_type_by_name(env, "g").data.data[0].data, CartType)
        assert isinstance(get_type_by_name(env, "g").data.data[1].data, IntegerType)      


    def test_types_complex_function_image5(self):
        string = '''
        MACHINE         Test
        VARIABLES       f,g
        INVARIANT       g<:%aa,bb,cc.((aa,bb):NAT1*NAT &cc:NAT| f(cc , aa |-> bb)) & f<: NAT * NAT1 * NAT * NAT 
        INITIALISATION  f:={(1,1,1,1),(1,1,1,1)} ; g:={}
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) 
        assert isinstance(get_type_by_name(env, "g"), PowerSetType)
        assert isinstance(get_type_by_name(env, "g").data, CartType)
        assert isinstance(get_type_by_name(env, "g").data.data[0], PowerSetType)
        assert isinstance(get_type_by_name(env, "g").data.data[1], PowerSetType)
        assert isinstance(get_type_by_name(env, "g").data.data[0].data, CartType)
        assert isinstance(get_type_by_name(env, "g").data.data[1].data, IntegerType)  
        

    def test_types_complex_function_image6(self):
        string = '''
        MACHINE         Test
        VARIABLES       f,g
        INVARIANT       g<:%aa,bb,cc.(aa:NAT & bb:NAT & cc:NAT| f(aa |-> bb) |-> cc) & f<: NAT * NAT *NAT 
        INITIALISATION  f:={(1,1,1),(1,1,1)}  ; g:={}
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)         
        assert isinstance(get_type_by_name(env, "g"), PowerSetType)
        assert isinstance(get_type_by_name(env, "g").data, CartType)
        assert isinstance(get_type_by_name(env, "g").data.data[0], PowerSetType)
        assert isinstance(get_type_by_name(env, "g").data.data[1], PowerSetType)
        assert isinstance(get_type_by_name(env, "g").data.data[0].data, CartType)
        assert isinstance(get_type_by_name(env, "g").data.data[1].data, CartType)
   
        
    def test_types_complex_function_image7(self):
        string = '''
        MACHINE         Test
        VARIABLES       f,g
        INVARIANT       g(f(1 |-> 1) |-> 1) /= 42 & f<: NAT * NAT *NAT
        INITIALISATION  f:={(1,1,1),(1,1,1)}  ; g:={(1,1,1)}
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) 
                
    
    # POW(((INTEGER*(INTEGER*INTEGER))*INTEGER)*INTEGER) is type of f
    def test_types_complex_function_image8(self):
        string = '''
        MACHINE         Test
        VARIABLES       f,x,y,z
        INVARIANT       f(x,y,z)=42 & x=1 & y = (1,1) & z=1
        INITIALISATION  f:={((1,(1,1)),1,42),((1,(1,1)),1,42)} ; x:=1; z:=1 ; y:=(1,1)
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)    



    def test_types_complex_union_empty_set(self):          
        string = '''MACHINE Test
        SETS U = {g, h, i}; R={j,k,l}        
        CONSTANTS gg
        PROPERTIES
        gg : U +-> (R >+> R) & gg = { g |-> {j |-> l}, h |-> {k |-> k}, i |-> {}} 
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)       
     
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        assert isinstance(get_type_by_name(env, "gg"), PowerSetType)
        assert isinstance(get_type_by_name(env, "gg").data, CartType)
        assert isinstance(get_type_by_name(env, "gg").data.data[0], PowerSetType)
        assert isinstance(get_type_by_name(env, "gg").data.data[1], PowerSetType)
        assert isinstance(get_type_by_name(env, "gg").data.data[0].data, SetType)
        assert get_type_by_name(env, "gg").data.data[0].data.data =="U"
        image_type = get_type_by_name(env, "gg").data.data[1].data.data
        assert isinstance(image_type, CartType)
        assert isinstance(image_type.data[0].data, SetType)
        assert isinstance(image_type.data[1].data, SetType)
        assert image_type.data[0].data.data=="R"
        assert image_type.data[1].data.data=="R"
        
                
    def test_types_complex_union_empty_set2(self):          
        string = '''
        MACHINE Test
        SETS U = {g, h, i}; R={j,k,l}        
        CONSTANTS ff, gg
        PROPERTIES
        gg : U +-> (R >+> R) & gg = { g |-> {j |-> l}, h |-> {k |-> k}, i |-> {}} &
        ff = (U * {{}} <+ gg) (g) 
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)       
     
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        assert isinstance(get_type_by_name(env, "gg"), PowerSetType)
        assert isinstance(get_type_by_name(env, "gg").data, CartType)
        assert isinstance(get_type_by_name(env, "gg").data.data[0], PowerSetType)
        assert isinstance(get_type_by_name(env, "gg").data.data[1], PowerSetType)
        assert isinstance(get_type_by_name(env, "gg").data.data[0].data, SetType)
        assert get_type_by_name(env, "gg").data.data[0].data.data =="U"
        image_type = get_type_by_name(env, "gg").data.data[1].data.data
        assert isinstance(image_type, CartType)
        assert isinstance(image_type.data[0].data, SetType)
        assert isinstance(image_type.data[1].data, SetType)
        assert image_type.data[0].data.data=="R"
        assert image_type.data[1].data.data=="R"
        
        image_type = get_type_by_name(env, "ff").data
        assert isinstance(image_type, CartType)
        assert isinstance(image_type.data[0].data, SetType)
        assert isinstance(image_type.data[1].data, SetType)
        assert image_type.data[0].data.data=="R"
        assert image_type.data[1].data.data=="R"
        

    def test_types_complex_union_empty_set3(self):    
        string = '''
        MACHINE Test
        SETS S={a, b}; T={d, e}; U = {g, h, i}; R={j,k,l}        
        CONSTANTS ff, gg, hh
        PROPERTIES
        gg : U +-> (R >+> R) & gg = { g |-> {j |-> l}, h |-> {k |-> k}, i |-> {}} &
        hh : S * T --> (U +-> (R >+> R)) & hh={(a|->d) |-> {}, (a|->e)|->{}, (b|->d) |-> {}, (b|->e)|->{}} &
        ff = %(xx, yy).(xx : S +-> T & yy : U |   
             (U * {{}} <+ gg) (yy) \/  union (((U * {{}}) <+ union (hh[xx])) [{yy}]))
        END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)       
     
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
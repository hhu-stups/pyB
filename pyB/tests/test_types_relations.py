# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from environment import Environment
from typing import _test_typeit, type_check_bmch
from parsing import parse_ast
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
        lst = [("S", PowerSetType(SetType("X"))),("T", PowerSetType(SetType("X")))]
        _test_typeit(root, env, lst, ["r"])
        assert isinstance(env.get_type("r"), PowerSetType)
        assert isinstance(env.get_type("r").data, PowerSetType)
        assert isinstance(env.get_type("r").data.data, CartType)
        assert isinstance(env.get_type("r").data.data.data[0].data, SetType)
        assert isinstance(env.get_type("r").data.data.data[1].data, SetType)


    def test_types_relation_set_enum(self):
        # Build AST
        string_to_file("#PREDICATE r = {8|->10, 7|->11, 2|->11, 6|->12}", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["r"])
        assert isinstance(env.get_type("r"), PowerSetType)
        assert isinstance(env.get_type("r").data, CartType)
        assert isinstance(env.get_type("r").data.data[0].data, IntegerType)
        assert isinstance(env.get_type("r").data.data[1].data, IntegerType)


    def test_types_domain(self):
        # Build AST
        string_to_file("#PREDICATE r:S<->T & x:dom(r)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X"))),("T", PowerSetType(SetType("Y")))]
        _test_typeit(root, env, lst, ["r","x"])
        assert isinstance(env.get_type("x"), SetType)
        assert env.get_type("x").data == "X"


    def test_types_dom_unify(self):
        # Build AST
        string_to_file("#PREDICATE d=A*B & c=dom(d) & A=NAT & B=NAT", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        _test_typeit(root, env, [], ["c","d","A","B"])
        assert isinstance(env.get_type("A"), PowerSetType)
        assert isinstance(env.get_type("B"), PowerSetType)
        assert isinstance(env.get_type("c"), PowerSetType)
        assert isinstance(env.get_type("d"), PowerSetType)
        assert isinstance(env.get_type("d").data, CartType)


    def test_types_ran_unify(self):
        # Build AST
        string_to_file("#PREDICATE d=A*B & c=ran(d) & A=NAT & B=NAT", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        env = Environment()
        _test_typeit(root, env, [], ["c","d","A","B"])
        assert isinstance(env.get_type("A"), PowerSetType)
        assert isinstance(env.get_type("B"), PowerSetType)
        assert isinstance(env.get_type("c"), PowerSetType)
        assert isinstance(env.get_type("d"), PowerSetType)
        assert isinstance(env.get_type("d").data, CartType)


    def test_types_range(self):
        # Build AST
        string_to_file("#PREDICATE r:S<->T & x:ran(r)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X"))),("T", PowerSetType(SetType("Y")))]
        _test_typeit(root, env, lst, ["r","x"])
        assert isinstance(env.get_type("x"), SetType)
        assert env.get_type("x").data == "Y"


    def test_types_fwd_comp(self):
        # Build AST
        string_to_file("#PREDICATE r0:S<->T & r1:T<->S & x:ran(r1;r0)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X"))),("T", PowerSetType(SetType("Y")))]
        _test_typeit(root, env, lst, ["r0","r1","x"])
        assert isinstance(env.get_type("x"), SetType)
        assert env.get_type("x").data == "Y"


    def test_types_simple_identity(self):
        # Build AST
        string_to_file("#PREDICATE S=id(B)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("B", PowerSetType(SetType("X")))]
        _test_typeit(root, env, lst, ["S"])
        assert isinstance(env.get_type("S"), PowerSetType)
        assert isinstance(env.get_type("S").data, CartType)
        assert isinstance(env.get_type("S").data.data[0].data, SetType)
        assert isinstance(env.get_type("S").data.data[1].data, SetType)


    def test_types_simple_iterate(self):
        # Build AST
        string_to_file("#PREDICATE f=iterate(r,n)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        l = [("r", PowerSetType(CartType(PowerSetType(IntegerType(None)),PowerSetType(IntegerType(None)))))]
        _test_typeit(root, env, l, ["f","n"])
        assert isinstance(env.get_type("f"), PowerSetType)
        assert isinstance(env.get_type("f").data, CartType)
        assert isinstance(env.get_type("r"), PowerSetType)
        assert isinstance(env.get_type("r").data, CartType)
        assert isinstance(env.get_type("n"), IntegerType)


    def test_types_simple_closure(self):
        # Build AST
        string_to_file("#PREDICATE f=closure(r)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        l = [("r", PowerSetType(CartType(PowerSetType(IntegerType(None)),PowerSetType(IntegerType(None)))))]
        _test_typeit(root, env, l, ["f"])
        assert isinstance(env.get_type("f"), PowerSetType)
        assert isinstance(env.get_type("f").data, CartType)
        assert isinstance(env.get_type("r"), PowerSetType)
        assert isinstance(env.get_type("r").data, CartType)


    def test_types_simple_closure1(self):
        # Build AST
        string_to_file("#PREDICATE f=closure1(r)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        l = [("r", PowerSetType(CartType(PowerSetType(IntegerType(None)),PowerSetType(IntegerType(None)))))]
        _test_typeit(root, env, l, ["f"])
        assert isinstance(env.get_type("f"), PowerSetType)
        assert isinstance(env.get_type("f").data, CartType)
        assert isinstance(env.get_type("r"), PowerSetType)
        assert isinstance(env.get_type("r").data, CartType)


    def test_types_simple_sub_res(self):
        # Build AST
        string_to_file("#PREDICATE r:A<->B & v=S <| r", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X"))),("A", PowerSetType(SetType("X"))),("B", PowerSetType(SetType("Y")))]
        _test_typeit(root, env, lst, ["r","v"])
        assert isinstance(env.get_type("v"), PowerSetType)
        assert isinstance(env.get_type("v").data, CartType)


    def test_types_simple_rev(self):
        # Build AST
        string_to_file("#PREDICATE r:A<->B & f = r~ & x:dom(f)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("A", PowerSetType(SetType("X"))),("B", PowerSetType(SetType("Y")))]
        _test_typeit(root, env, lst, ["r","x","f"])
        assert isinstance(env.get_type("x"), SetType)
        assert env.get_type("x").data =="Y"


    def test_types_simple_image(self):
        # Build AST
        string_to_file("#PREDICATE r:A<->B & S<:A & x:r[S]", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("A", PowerSetType(SetType("X"))),("B", PowerSetType(SetType("Y")))]
        _test_typeit(root, env, lst, ["r","S","x"])
        assert isinstance(env.get_type("S"), PowerSetType)
        assert isinstance(env.get_type("S").data, SetType)
        assert env.get_type("S").data.data =="X"
        assert isinstance(env.get_type("x"), SetType)
        assert env.get_type("x").data == "Y"


    def test_types_simple_overwrite(self):
        # Build AST
        string_to_file("#PREDICATE r1:A<->B & r2:A<->B & r3=r1<+r2", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("A", PowerSetType(SetType("X"))),("B", PowerSetType(SetType("Y")))]
        _test_typeit(root, env, lst, ["r1","r2","r3"])
        assert isinstance(env.get_type("r3"), PowerSetType)
        assert isinstance(env.get_type("r3").data, CartType)
        assert env.get_type("r3").data.data[0].data.data == "X"
        assert env.get_type("r3").data.data[1].data.data == "Y"
        assert not env.get_type("r1")=="r1"
        assert not env.get_type("r2")=="r2"


    def test_types_simple_parprod(self):
        # Build AST
        string_to_file("#PREDICATE r1:A<->B & r2:C<->D & r3=(r1 || r2)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("A", PowerSetType(SetType("X"))),("B", PowerSetType(SetType("Y"))),("C", PowerSetType(SetType("M"))),("D", PowerSetType(SetType("N")))]
        _test_typeit(root, env, lst, ["r1","r2","r3"])
        assert isinstance(env.get_type("r3"), PowerSetType)
        assert isinstance(env.get_type("r3").data, CartType)
        assert isinstance(env.get_type("r3").data.data[0].data, CartType)
        assert isinstance(env.get_type("r3").data.data[1].data, CartType)
        x = env.get_type("r3").data.data[0].data.data[0].data
        y = env.get_type("r3").data.data[0].data.data[1].data
        m = env.get_type("r3").data.data[1].data.data[0].data
        n = env.get_type("r3").data.data[1].data.data[1].data
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
        lst = [("A", PowerSetType(SetType("X"))),("B", PowerSetType(SetType("Y"))),("C", PowerSetType(SetType("X"))),("D", PowerSetType(SetType("Z")))]
        _test_typeit(root, env, lst, ["r1","r2","r3"])
        assert isinstance(env.get_type("r3"), PowerSetType)
        assert isinstance(env.get_type("r3").data, CartType)
        x = env.get_type("r3").data.data[0].data
        y = env.get_type("r3").data.data[1].data.data[0].data
        z = env.get_type("r3").data.data[1].data.data[1].data
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
        exec ast_string

        # Type
        env = Environment()
        _test_typeit(root, env, [], ["f","g"])


    def test_types_simple_proj1(self):
        # Build AST
        string_to_file("#PREDICATE r=prj1(A,B)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Type
        env = Environment()
        lst = [("A", PowerSetType(SetType("X"))),("B", PowerSetType(SetType("Y")))]
        _test_typeit(root, env, lst, ["r"])
        assert isinstance(env.get_type("r"), PowerSetType)
        assert isinstance(env.get_type("r").data, CartType)
        x = env.get_type("r").data.data[0].data.data[0].data
        y = env.get_type("r").data.data[0].data.data[1].data
        z = env.get_type("r").data.data[1].data
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
        lst = [("A", PowerSetType(SetType("X"))),("B", PowerSetType(SetType("Y")))]
        _test_typeit(root, env, lst, ["r"])
        assert isinstance(env.get_type("r"), PowerSetType)
        assert isinstance(env.get_type("r").data, CartType)
        x = env.get_type("r").data.data[0].data.data[0].data
        y = env.get_type("r").data.data[0].data.data[1].data
        z = env.get_type("r").data.data[1].data
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
        exec ast_string

        # Type
        env = Environment()
        lst = [("A", PowerSetType(SetType("X"))),("aa",SetType("X")),("bb",SetType("X"))]
        _test_typeit(root, env, lst, ["f","g"])
        assert isinstance(env.get_type("g"), PowerSetType)
        assert isinstance(env.get_type("g").data, CartType)
        assert isinstance(env.get_type("f"), PowerSetType)
        assert isinstance(env.get_type("f").data, CartType)


    def test_types_rel_expr(self):
        # Build AST:
        string_to_file("#PREDICATE f1 = {(-1|->{0, 2}), (1|->{6, 8}), (3|->{3})} & r= rel(f1)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        _test_typeit(root, env, [], ["f1","r"])
        assert isinstance(env.get_type("f1"), PowerSetType)
        assert isinstance(env.get_type("f1").data, CartType)
        assert isinstance(env.get_type("f1").data.data[0].data, IntegerType)
        assert isinstance(env.get_type("f1").data.data[1].data, PowerSetType)
        assert isinstance(env.get_type("f1").data.data[1].data.data, IntegerType)
        assert isinstance(env.get_type("r"), PowerSetType)
        assert isinstance(env.get_type("r").data, CartType)
        assert isinstance(env.get_type("r").data.data[0].data, IntegerType)
        assert isinstance(env.get_type("r").data.data[1].data, IntegerType)


    def test_types_couple_element(self):
        string = '''
        MACHINE          Test
        VARIABLES        xx, aa, bb
        INVARIANT        xx<:INTEGER*NATURAL1 & (aa,bb): xx
        INITIALISATION   xx:={(1,2),(4,5)} ; aa:=1 ; bb:=2
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string
        
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        assert isinstance(env.get_type("xx"), PowerSetType)
        assert isinstance(env.get_type("xx").data, CartType)
        assert isinstance(env.get_type("xx").data.data[0], PowerSetType)
        assert isinstance(env.get_type("xx").data.data[1], PowerSetType)
        assert isinstance(env.get_type("xx").data.data[0].data, IntegerType)
        assert isinstance(env.get_type("xx").data.data[1].data, IntegerType)
        assert isinstance(env.get_type("aa"), IntegerType)
        assert isinstance(env.get_type("bb"), IntegerType)


    def test_types_couple_element2(self):
        string = '''
        MACHINE         Test
		VARIABLES       xx, yy
		INVARIANT       xx<:(INTEGER*NATURAL1) & yy<:NAT*INTEGER*NATURAL1
		INITIALISATION  xx:={(1,2),(4,5)} ; yy:=%(n,d).((n,d) : xx| n+d)
		END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string
        
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        assert isinstance(env.get_type("xx"), PowerSetType)
        assert isinstance(env.get_type("xx").data, CartType)
        assert isinstance(env.get_type("xx").data.data[0], PowerSetType)
        assert isinstance(env.get_type("xx").data.data[1], PowerSetType)
        assert isinstance(env.get_type("xx").data.data[0].data, IntegerType)
        assert isinstance(env.get_type("xx").data.data[1].data, IntegerType)

        
    def test_types_complex_function_image(self):
        string = '''
        MACHINE         Test
		VARIABLES       yy, xx
		INVARIANT       yy<:%aa.(aa:xx | prj1(INTEGER, INTEGER)(aa)) & xx<:INTEGER * NATURAL1 
		INITIALISATION  xx:={(1,2),(2,2)} ; yy:={((1,2),1),((2,2),2)}
		END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string
        
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
        exec ast_string
        
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
        exec ast_string
        
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        assert isinstance(env.get_type("g"), PowerSetType)
        assert isinstance(env.get_type("g").data, CartType)
        assert isinstance(env.get_type("g").data.data[0], PowerSetType)
        assert isinstance(env.get_type("g").data.data[1], PowerSetType)
        assert isinstance(env.get_type("g").data.data[0].data, CartType)
        assert isinstance(env.get_type("g").data.data[1].data, IntegerType)
        
 
    def test_types_complex_function_image4(self):
        string = '''
		MACHINE         Test
		VARIABLES       f,g
		INVARIANT       g<:%aa,bb,cc.((aa,bb):NAT1*NAT &cc:NAT| f(cc |-> aa |-> bb)) & f<: NAT * NAT1 * NAT * NAT 
		INITIALISATION  f:={(1,1,1,1),(1,1,1,1)} ; g:={}
		END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string
        
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) 
        assert isinstance(env.get_type("g"), PowerSetType)
        assert isinstance(env.get_type("g").data, CartType)
        assert isinstance(env.get_type("g").data.data[0], PowerSetType)
        assert isinstance(env.get_type("g").data.data[1], PowerSetType)
        assert isinstance(env.get_type("g").data.data[0].data, CartType)
        assert isinstance(env.get_type("g").data.data[1].data, IntegerType)      


    def test_types_complex_function_image5(self):
        string = '''
		MACHINE         Test
		VARIABLES       f,g
		INVARIANT       g<:%aa,bb,cc.((aa,bb):NAT1*NAT &cc:NAT| f(cc , aa |-> bb)) & f<: NAT * NAT1 * NAT * NAT 
		INITIALISATION  f:={(1,1,1,1),(1,1,1,1)} ; g:={}
		END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string
        
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch) 
        assert isinstance(env.get_type("g"), PowerSetType)
        assert isinstance(env.get_type("g").data, CartType)
        assert isinstance(env.get_type("g").data.data[0], PowerSetType)
        assert isinstance(env.get_type("g").data.data[1], PowerSetType)
        assert isinstance(env.get_type("g").data.data[0].data, CartType)
        assert isinstance(env.get_type("g").data.data[1].data, IntegerType)  
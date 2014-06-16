# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from environment import Environment
from util import type_with_known_types, get_type_by_name
from helpers import file_to_AST_str, string_to_file
from parsing import str_ast_to_python_ast,  parse_ast
from typing import type_check_bmch

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
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("x", SetType("X")),("S", PowerSetType(SetType("X"))),("T", PowerSetType(SetType("Y")))]
        type_with_known_types(root, env, lst, ["y","f"])
        assert isinstance(get_type_by_name(env, "y"), SetType)
        assert get_type_by_name(env, "y").data=="Y"


    def test_types_function_app2(self):
        # Build AST
        string_to_file("#PREDICATE f= {1 |-> \"aa\", 2 |-> \"bb\"}(xx) & xx=1 ", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["xx","f"])
        assert isinstance(get_type_by_name(env, "f"), StringType)
        assert isinstance(get_type_by_name(env, "xx"), IntegerType)
                

    def test_types_lambda(self):
        # Build AST
        string_to_file("#PREDICATE f="+"%"+"x.(x>0 & x<10|x*x)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["f","x"])
        assert isinstance(get_type_by_name(env, "f"), PowerSetType)
        assert isinstance(get_type_by_name(env, "f").data, CartType)
        assert isinstance(get_type_by_name(env, "f").data.data[0].data, IntegerType)
        assert isinstance(get_type_by_name(env, "f").data.data[1].data, IntegerType)
        assert isinstance(get_type_by_name(env, "x"), IntegerType)
        lambda_node = root.children[0].children[1]
        assert isinstance(lambda_node, ALambdaExpression)
        image_type = env.get_lambda_type_by_node(lambda_node)
        assert isinstance(image_type, IntegerType)


    def test_types_lambda2(self):
        # Build AST
        string_to_file("#PREDICATE f="+"%"+"(x,y).(x=0 & y=10|TRUE)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["f","x","y"])
        assert isinstance(get_type_by_name(env, "f"), PowerSetType)
        assert isinstance(get_type_by_name(env, "f").data, CartType)
        assert isinstance(get_type_by_name(env, "f").data.data[0], PowerSetType)
        assert isinstance(get_type_by_name(env, "f").data.data[1], PowerSetType)
        dom_type = get_type_by_name(env, "f").data.data[0]
        img_type = get_type_by_name(env, "f").data.data[1] #only present if lambda is ass. to var
        assert isinstance(img_type.data, BoolType)
        assert isinstance(dom_type.data, CartType)
        assert isinstance(dom_type.data.data[0], PowerSetType)
        assert isinstance(dom_type.data.data[1], PowerSetType)
        assert isinstance(dom_type.data.data[0].data, IntegerType)
        assert isinstance(dom_type.data.data[1].data, IntegerType)
        lambda_node = root.children[0].children[1]
        assert isinstance(lambda_node, ALambdaExpression)
        image_type = env.get_lambda_type_by_node(lambda_node) # this function always returns a type
        assert isinstance(image_type, BoolType)


    def test_types_type_arg(self):
        # Build AST
        string_to_file("#PREDICATE paid: 1..5 --> BOOL & switcher: 1..5 --> {0, 1} & !(i).(paid(i) = FALSE => switcher(i) = 1)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["paid","switcher"])
        # TODO:


    def test_types_type_arg2(self):
        # Build AST
        string_to_file("#PREDICATE f: NAT * NAT * BOOL --> BOOL  & !(x,y,z).(f(x,y,z) = FALSE => 1+1=2)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["f"])
        # TODO:        


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
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X")))]
        type_with_known_types(root, env, lst, ["r","s","t"])
        assert isinstance(get_type_by_name(env, "r"), PowerSetType)
        assert isinstance(get_type_by_name(env, "r").data, CartType)
        assert isinstance(get_type_by_name(env, "r").data.data[0], IntegerType)
        assert isinstance(get_type_by_name(env, "r").data.data[1], SetType)


    def test_types_seq_prepend(self):
        # Build AST
        string_to_file("#PREDICATE s:perm(S) & E:S & t=E->s", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X")))]
        type_with_known_types(root, env, lst, ["E","s","t"])
        assert isinstance(get_type_by_name(env, "t"), PowerSetType)
        assert isinstance(get_type_by_name(env, "t").data, CartType)
        assert isinstance(get_type_by_name(env, "t").data.data[0].data, IntegerType)
        assert isinstance(get_type_by_name(env, "t").data.data[1].data, SetType)


    def test_types_seq_size(self):
        # Build AST
        string_to_file("#PREDICATE s:perm(S) & x=size(s)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X")))]
        type_with_known_types(root, env, lst, ["x","s"])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)


    def test_types_seq_rev(self):
        # Build AST
        string_to_file("#PREDICATE s:perm(S) & t=rev(s)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X")))]
        type_with_known_types(root, env, lst, ["t","s"])
        assert isinstance(get_type_by_name(env, "t"), PowerSetType)
        assert isinstance(get_type_by_name(env, "t").data, CartType)
        assert isinstance(get_type_by_name(env, "t").data.data[0].data, IntegerType)
        assert isinstance(get_type_by_name(env, "t").data.data[1].data, SetType)


    def test_types_seq_take(self):
        # Build AST
        string_to_file("#PREDICATE n=3 & s:perm(S) & t=s/|\\n", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X")))]
        type_with_known_types(root, env, lst, ["t","s","n"])
        assert isinstance(get_type_by_name(env, "t"), PowerSetType)
        assert isinstance(get_type_by_name(env, "t").data, CartType)
        assert isinstance(get_type_by_name(env, "t").data.data[0].data, IntegerType)
        assert isinstance(get_type_by_name(env, "t").data.data[1].data, SetType)
        assert isinstance(get_type_by_name(env, "n"), IntegerType)


    def test_types_seq_drop(self):
        # Build AST
        string_to_file("#PREDICATE n=3 & s:perm(S) & t=s\|/n", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X")))]
        type_with_known_types(root, env, lst, ["t","s","n"])
        assert isinstance(get_type_by_name(env, "t"), PowerSetType)
        assert isinstance(get_type_by_name(env, "t").data, CartType)
        assert isinstance(get_type_by_name(env, "t").data.data[0].data, IntegerType)
        assert isinstance(get_type_by_name(env, "t").data.data[1].data, SetType)
        assert isinstance(get_type_by_name(env, "n"), IntegerType)


    def test_types_seq_first(self):
        # Build AST
        string_to_file("#PREDICATE s:perm(S) & n=first(s)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X")))]
        type_with_known_types(root, env, lst, ["s","n"])
        assert isinstance(get_type_by_name(env, "n"), SetType)
        assert get_type_by_name(env, "n").data == "X"


    def test_types_seq_last(self):
        # Build AST
        string_to_file("#PREDICATE s:perm(S) & n=last(s)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X")))]
        type_with_known_types(root, env, lst, ["s","n"])
        assert isinstance(get_type_by_name(env, "n"), SetType)
        assert get_type_by_name(env, "n").data == "X"


    def test_types_seq_tail(self):
        # Build AST
        string_to_file("#PREDICATE s:perm(S) & t=tail(s)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X")))]
        type_with_known_types(root, env, lst, ["s","t"])
        assert isinstance(get_type_by_name(env, "t"), PowerSetType)
        assert isinstance(get_type_by_name(env, "t").data, CartType)
        assert isinstance(get_type_by_name(env, "t").data.data[0].data, IntegerType)
        assert isinstance(get_type_by_name(env, "t").data.data[1].data, SetType)


    def test_types_seq_front(self):
        # Build AST
        string_to_file("#PREDICATE s:perm(S) & t=front(s)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X")))]
        type_with_known_types(root, env, lst, ["s","t"])
        assert isinstance(get_type_by_name(env, "t"), PowerSetType)
        assert isinstance(get_type_by_name(env, "t").data, CartType)
        assert isinstance(get_type_by_name(env, "t").data.data[0].data, IntegerType)
        assert isinstance(get_type_by_name(env, "t").data.data[1].data, SetType)


    def test_types_seq_conc(self):
        # Build AST
        string_to_file("#PREDICATE ss:perm(perm(S)) & s=conc(ss)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X")))]
        type_with_known_types(root, env, lst, ["s","ss"])
        assert isinstance(get_type_by_name(env, "s"), PowerSetType)
        assert isinstance(get_type_by_name(env, "s").data, CartType)
        assert isinstance(get_type_by_name(env, "ss"), PowerSetType)
        assert isinstance(get_type_by_name(env, "ss").data, CartType)
   
        
    def test_types_seq_conc2(self):
        # Build AST
        string_to_file("#PREDICATE s=conc([[2, 5], [-1, -2, 9], [], [5]])", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)    

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["s"])
        assert isinstance(get_type_by_name(env, "s"), PowerSetType)
        assert isinstance(get_type_by_name(env, "s").data, CartType)
        assert isinstance(get_type_by_name(env, "s").data.data[0], PowerSetType)   
        assert isinstance(get_type_by_name(env, "s").data.data[1], PowerSetType)       
        assert isinstance(get_type_by_name(env, "s").data.data[0].data, IntegerType)   
        assert isinstance(get_type_by_name(env, "s").data.data[1].data, IntegerType)          


    def test_types_seq_conc3(self):
        # Build AST
        string_to_file("#PREDICATE S=[[2, 5], [-1, -2, 9], [], [5]] & s=conc(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)    

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["s","S"])
        assert isinstance(get_type_by_name(env, "s"), PowerSetType)
        assert isinstance(get_type_by_name(env, "s").data, CartType)
        assert isinstance(get_type_by_name(env, "s").data.data[0], PowerSetType)   
        assert isinstance(get_type_by_name(env, "s").data.data[1], PowerSetType)       
        assert isinstance(get_type_by_name(env, "s").data.data[0].data, IntegerType)   
        assert isinstance(get_type_by_name(env, "s").data.data[1].data, IntegerType) 
        assert isinstance(get_type_by_name(env, "S"), PowerSetType)
        assert isinstance(get_type_by_name(env, "S").data, CartType)
        assert isinstance(get_type_by_name(env, "S").data.data[0], PowerSetType)   
        assert isinstance(get_type_by_name(env, "S").data.data[1], PowerSetType) 
        assert isinstance(get_type_by_name(env, "S").data.data[0].data, IntegerType)
        assert isinstance(get_type_by_name(env, "S").data.data[1].data.data, CartType)
        assert isinstance(get_type_by_name(env, "S").data.data[1].data.data.data[0], PowerSetType)
        assert isinstance(get_type_by_name(env, "S").data.data[1].data.data.data[1], PowerSetType)
        assert isinstance(get_type_by_name(env, "S").data.data[1].data.data.data[0].data, IntegerType)
        assert isinstance(get_type_by_name(env, "S").data.data[1].data.data.data[1].data, IntegerType)
                
                
    def test_types_seq_append(self):
        # Build AST
        string_to_file("#PREDICATE s:perm(S) & E:S & t=s<-E", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X")))]
        type_with_known_types(root, env, lst, ["s","t","E"])
        assert isinstance(get_type_by_name(env, "t"), PowerSetType)
        assert isinstance(get_type_by_name(env, "t").data, CartType)
        assert isinstance(get_type_by_name(env, "t").data.data[0].data, IntegerType)
        assert isinstance(get_type_by_name(env, "t").data.data[1].data, SetType)


    def test_types_seq_extention(self):
        # Build AST
        string_to_file("#PREDICATE s=[1,2,3]", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["s"])
        assert isinstance(get_type_by_name(env, "s"), PowerSetType)
        assert isinstance(get_type_by_name(env, "s").data, CartType)
        assert isinstance(get_type_by_name(env, "s").data.data[0].data, IntegerType)
        assert isinstance(get_type_by_name(env, "s").data.data[1].data, IntegerType)


    def test_types_seq_extention2(self):
        string = '''
        MACHINE Test
		CONSTANTS s, x
		PROPERTIES s=[17+4,x, 5] & x=42 		
		END'''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)       
     
        # Test
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        assert isinstance(get_type_by_name(env, "s"), PowerSetType)
        assert isinstance(get_type_by_name(env, "s").data, CartType)
        assert isinstance(get_type_by_name(env, "s").data.data[0].data, IntegerType)
        assert isinstance(get_type_by_name(env, "s").data.data[1].data, IntegerType)


    def test_types_fnc_expr(self):
        # Build AST
        string_to_file("#PREDICATE R1 = {(0|->1), (0|->2), (1|->1), (1|->7), (2|->3)} & f= fnc(R1)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        type_with_known_types(root, env, [], ["R1","f"])
        assert isinstance(get_type_by_name(env, "f"), PowerSetType)
        assert isinstance(get_type_by_name(env, "f").data, CartType)
        assert isinstance(get_type_by_name(env, "f").data.data[0].data, IntegerType)
        assert isinstance(get_type_by_name(env, "f").data.data[1].data, PowerSetType)
        assert isinstance(get_type_by_name(env, "f").data.data[1].data.data, IntegerType)
        assert isinstance(get_type_by_name(env, "R1"), PowerSetType)
        assert isinstance(get_type_by_name(env, "R1").data, CartType)
        assert isinstance(get_type_by_name(env, "R1").data.data[0].data, IntegerType)
        assert isinstance(get_type_by_name(env, "R1").data.data[1].data, IntegerType)


    def type_check_sequence(self, ast_string):
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X")))]
        type_with_known_types(root, env, lst, ["s"])
        assert isinstance(get_type_by_name(env, "s"), PowerSetType)
        assert isinstance(get_type_by_name(env, "s").data, CartType)
        assert isinstance(get_type_by_name(env, "s").data.data[0].data, IntegerType)
        assert isinstance(get_type_by_name(env, "s").data.data[1].data, SetType)


    def type_check_function(self, ast_string):
        root = str_ast_to_python_ast(ast_string)

        # Type
        env = Environment()
        lst = [("S", PowerSetType(SetType("X"))),("T", PowerSetType(SetType("Y")))]
        type_with_known_types(root, env, lst, ["r"])
        assert isinstance(get_type_by_name(env, "r"), PowerSetType)
        assert isinstance(get_type_by_name(env, "r").data, CartType)
        assert isinstance(get_type_by_name(env, "r").data.data[0].data, SetType)
        assert isinstance(get_type_by_name(env, "r").data.data[1].data, SetType)
        assert get_type_by_name(env, "r").data.data[0].data.data == "X"
        assert get_type_by_name(env, "r").data.data[1].data.data == "Y"
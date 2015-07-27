# -*- coding: utf-8 -*-
from ast_nodes import *
from helpers import file_to_AST_str, string_to_file
from pretty_printer import pretty_print
from parsing import str_ast_to_python_ast

from config import USE_RPYTHON_CODE
if USE_RPYTHON_CODE:
     from rpython_b_objmodel import frozenset

file_name = "input.txt"

class TestPrettyPrinter():
    def test_pp_numbers(self):
        # Build AST
        string_to_file("#PREDICATE 1+2<3 & 4-5>6 & 7*8>=9 & 10/11<=12 & 13 mod 14=15 & 1/=-1", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # PPrint
        out = pretty_print(root.children[0])
        assert out=="1+2<3 & 4-5>6 & 7*8>=9 & 10/11<=12 & 13 mod 14=15 & 1/=-1"


    def test_pp_numbers2(self):
        # Build AST
        string_to_file("#PREDICATE !(z).(z<9 => not (1=1) or 1=2) <=> #(z).(z<8 & z=5)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # PPrint
        out = pretty_print(root.children[0])
        assert out =="!(z).(z<9 => not (1=1) or 1=2) <=> #(z).(z<8 & z=5)"
        

    def test_pp_numbers3(self):
        # Build AST
        string_to_file("#PREDICATE NAT<:NAT1 & NATURAL<:NATURAL1 & INT<:INTEGER", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # PPrint
        out = pretty_print(root.children[0])
        assert out =="NAT<:NAT1 & NATURAL<:NATURAL1 & INT<:INTEGER"


    def test_pp_numbers4(self):
        # Build AST
        string_to_file("#PREDICATE SIGMA(z).(z<4|z)=5 & PI(z).(z<0|z)=5", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # PPrint
        out = pretty_print(root.children[0])
        assert out =="SIGMA(z).(z<4|z)=5 & PI(z).(z<0|z)=5"        


    def test_pp_sets(self):
        # Build AST
        string_to_file("#PREDICATE E:S & E/:S & S<:T & S/<:T & S<<:T & S/<<:T", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # PPrint
        out = pretty_print(root.children[0])
        assert out=="E:S & E/:S & S<:T & S/<:T & S<<:T & S/<<:T"


    def test_pp_sets2(self):
        # Build AST
        string_to_file("#PREDICATE {}<:{a} & S\/T<:S/\T & S-T<:S*T & {a,b}<:{x|x<7}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # PPrint
        out = pretty_print(root.children[0])
        assert out=="{}<:{a} & S\/T<:S/\T & S-T<:S*T & {a,b}<:{x,|x<7}"


    def test_pp_sets3(self):
        # Build AST
        string_to_file("#PREDICATE E|->F:POW(S) & {S}:POW1(T) & card(S)=42 & union(U)=inter(u)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # PPrint
        out = pretty_print(root.children[0])
        assert out=="E|->F:POW(S) & {S}:POW1(T) & card(S)=42 & union(U)=inter(u)"


    def test_pp_sets4(self): #TODO: FIN(S) and FIN1(S)
        # Build AST
        string_to_file("#PREDICATE UNION (z).(z<42|x)=INTER (z).(z<42|x)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # PPrint
        out = pretty_print(root.children[0])
        assert out=="UNION (z).(z<42|x)=INTER (z).(z<42|x)"


    def test_pp_relations(self): 
        # Build AST
        string_to_file("#PREDICATE r:S<->T & dom(r)=ran(r) & r=(p;q) & r:id(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
    
        # PPrint
        out = pretty_print(root.children[0])
        assert out=="r:S<->T & dom(r)=ran(r) & r=(p;q) & r:id(S)"    


    def test_pp_relations2(self): 
        # Build AST
        string_to_file("#PREDICATE S<|r=S<<|r & r|>T=r|>>T & r~=r1<+r2 & iterate(r,n)=r[S]", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # PPrint
        out = pretty_print(root.children[0])
        assert out=="S<|r=S<<|r & r|>T=r|>>T & r~=r1<+r2 & iterate(r,n)=r[S]" 


    def test_pp_relations3(self): 
        # Build AST
        string_to_file("#PREDICATE p><q=(p||q) & closure(r)=closure1(r) & prj1(S,T)=prj2(S,T)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # PPrint
        out = pretty_print(root.children[0])
        assert out=="p><q=(p||q) & closure(r)=closure1(r) & prj1(S,T)=prj2(S,T)"  


    def test_pp_functions(self): 
        # Build AST
        string_to_file("#PREDICATE S+->T=S-->T & S>+>T=S>->T & S+->>T=S-->>T & S>->>T=S>+>>T", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
    
        # PPrint
        out = pretty_print(root.children[0])
        assert out=="S+->T=S-->T & S>+>T=S>->T & S+->>T=S-->>T & S>->>T=S>+>>T"       


    def test_pp_functions2(self): 
        # Build AST
        string_to_file("#PREDICATE %(z).(z<4|z)=f(E)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
    
        # PPrint
        out = pretty_print(root.children[0])
        assert out=="%(z).(z<4|z)=f(E)"
        
        
    def test_pp_sequences(self): 
        # Build AST
        string_to_file("#PREDICATE <>=[] & seq(S)=seq1(S) & iseq(S)=iseq1(S) & x:perm(S)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
    
        # PPrint
        out = pretty_print(root.children[0])
        assert out=="[]=[] & seq(S)=seq1(S) & iseq(S)=iseq1(S) & x:perm(S)"  #[] : lose of information 
        

    def test_pp_sequences2(self): 
        # Build AST
        string_to_file("#PREDICATE s^t=r & E->s=r & s<-E=r & [E]=[E,F]", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
    
        # PPrint
        out = pretty_print(root.children[0])
        assert out=="s^t=r & E->s=r & s<-E=r & [E]=[E,F]"    


    def test_pp_sequences3(self): 
        # Build AST
        string_to_file("#PREDICATE size(s)=42 & rev(s)=r & s/|\\n=s\|/n & last(s)=first(s)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
    
        # PPrint
        out = pretty_print(root.children[0])
        assert out=="size(s)=42 & rev(s)=r & s/|\\n=s\|/n & last(s)=first(s)"  


    def test_pp_sequences4(self): 
        # Build AST
        string_to_file("#PREDICATE conc(ss)=r & front(s)=tail(s)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
    
        # PPrint
        out = pretty_print(root.children[0])
        assert out=="conc(ss)=r & front(s)=tail(s)" 


    def test_pp_miscellaneous1(self): 
        # Build AST
        string_to_file("#PREDICATE MAXINT/=MIINT & TRUE:BOOL & FALSE/:STRING & x.y=5", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)   

        # PPrint
        out = pretty_print(root.children[0])
        assert out=="MAXINT/=MIINT & TRUE:BOOL & FALSE/:STRING & x.y=5"


    def test_pp_miscellaneous2(self): 
        # Build AST
        string_to_file("#PREDICATE rel(f)=r & func(r)=f & bool(1<2)=TRUE & succ(s)=pred(t)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)   

        # PPrint
        out = pretty_print(root.children[0])
        assert out=="rel(f)=r & func(r)=f & bool(1<2)=TRUE & succ(s)=pred(t)"  
  

    def test_pp_miscellaneous3(self): 
        # Build AST
        string_to_file("#PREDICATE RES=rec(Mark:14,Good_enough:TRUE) & xx=RES'Mark", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)   

        # PPrint
        out = pretty_print(root.children[0])
        assert out=="RES=rec(Mark:14,Good_enough:TRUE) & xx=RES'Mark"       
           

    def test_pp_miscellaneous4(self): 
        # Build AST
        string_to_file("#PREDICATE RES:struct(Mark:NAT,Good_enough:BOOL)", file_name)
        ast_string = file_to_AST_str(file_name)
        print ast_string
        root = str_ast_to_python_ast(ast_string)   

        # PPrint
        out = pretty_print(root.children[0])
        assert out=="RES:struct(Mark:NAT,Good_enough:BOOL)"            
           
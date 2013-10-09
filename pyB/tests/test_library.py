# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from environment import Environment
from interp import interpret
from helpers import file_to_AST_str, string_to_file
from parsing import parse_ast
from typing import type_check_bmch
from definition_handler import DefinitionHandler

file_name = "input.txt"

# http://www.stups.uni-duesseldorf.de/ProB/index.php5/External_Functions
class TestLibrary():
    def test_library_length(self):
        string = '''
        MACHINE LibraryStrings
        CONSTANTS length
        PROPERTIES
          /* compute the length of a string */
          length: STRING --> INTEGER &
          length = %x.(x:STRING|STRING_LENGTH(x)) 
        DEFINITIONS
          STRING_LENGTH(x) == length(x);
          EXTERNAL_FUNCTION_STRING_LENGTH == STRING --> INTEGER;
        ASSERTIONS
          length("abc") = 3;
          length("") = 0;
          length("hello") = 5
        END
        '''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        dh = DefinitionHandler(env)                                   
        dh.repl_defs(root)
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        assert isinstance(env.get_type("length"), PowerSetType)
        assert isinstance(env.get_type("length").data, CartType)
        assert isinstance(env.get_type("length").data.data[0].data, StringType)
        assert isinstance(env.get_type("length").data.data[1].data, IntegerType)
        interpret(root, env)
        assert isinstance(root.children[4], AAssertionsMachineClause)
        interpret(root.children[4], env)


    # TODO: find args for append-function
    # TODO: {x|x:{"abc","abcabc","hello"} & #(prefx).(append(prefx,"c")=x)} = {"abcabc","abc"};
    def test_library_append(self):        
        string = '''
        MACHINE m
        DEFINITIONS
            EXTERNAL_FUNCTION_STRING_APPEND == STRING*STRING --> STRING;
            STRING_APPEND(x,y) == append(x,y);
            STRING_LENGTH(x) == length(x);
            EXTERNAL_FUNCTION_STRING_LENGTH == STRING --> INTEGER;
        ABSTRACT_CONSTANTS
            append, length
        PROPERTIES
            append = %(x,y).(x: STRING & y: STRING | STRING_APPEND(x,y)) &
            length: STRING --> INTEGER &
            length = %x.(x:STRING|STRING_LENGTH(x))  
        ASSERTIONS
            append("abc","abc") = "abcabc";
            append("","abc") = "abc";
            append("abc","") = "abc";
            /*{x|x:{"abc","abcabc","hello"} & #(prefx).(append(prefx,"c")=x)} = {"abcabc","abc"};*/
            {x|x/="" & #y.(append(x,y)="abc" & y/="")} = {"a","ab"}; /* compute true prefixes */
            {x|x/="" & #y.(append(y,x)="abc" & y/="")} = {"c","bc"}; /* compute true postfixes */
            {y|y/="" & #(x,z).(append(x,append(y,z))="abc" & length(x)+length(z)>0)} =  		
            /* compute true substrings */ {"a","ab","b","bc","c"};
            {y|y/="" & #(x,z).(append(append(x,y),z)="abc" & length(x)+length(z)>0)} = 
		 	/* compute true substrings */ {"a","ab","b","bc","c"}
        END'''
        # TODO: prolog-style args
        # {x|x:{"abc","abcabc","hello"} & #(prefx).(append(prefx,"c")=x)} = {"abcabc","abc"};
        # Build AST    
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        dh = DefinitionHandler(env)                                   
        dh.repl_defs(root)
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        assert isinstance(env.get_type("append"), PowerSetType)
        assert isinstance(env.get_type("append").data, CartType)
        assert isinstance(env.get_type("append").data.data[0].data, CartType)
        assert isinstance(env.get_type("append").data.data[0].data.data[0].data, StringType)
        assert isinstance(env.get_type("append").data.data[0].data.data[1].data, StringType)
        assert isinstance(env.get_type("append").data.data[1].data, StringType)
        interpret(root, env) 
        assert isinstance(root.children[4], AAssertionsMachineClause)
        interpret(root.children[4], env)
        

    def test_library_split(self):
        string = '''
        MACHINE LibraryStrings
        CONSTANTS split
        PROPERTIES
          /* split a string according to a delimiter string into a sequence of strings */
		  split: STRING * STRING --> (INTEGER<->STRING) & 
		  split = %(x,y).(x:STRING & y:STRING|STRING_SPLIT(x,y)) 
        DEFINITIONS
		  STRING_SPLIT(x,y) == split(x,y);
		  EXTERNAL_FUNCTION_STRING_SPLIT == ((STRING*STRING) --> (INTEGER<->STRING));
        ASSERTIONS
		  split("filename.ext",".") = ["filename","ext"];
		  split("filename.ext","/") = ["filename.ext"];
		  split("/usr/local/lib","/") = ["","usr","local","lib"];
		  split("/","/") = ["",""];
		  split("abcabc","bc") = ["a","a",""]
        END
        '''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        dh = DefinitionHandler(env)                                   
        dh.repl_defs(root)
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        assert isinstance(env.get_type("split"), PowerSetType)
        assert isinstance(env.get_type("split").data, CartType)
        assert isinstance(env.get_type("split").data.data[0].data, CartType)
        assert isinstance(env.get_type("split").data.data[0].data.data[0].data, StringType)
        assert isinstance(env.get_type("split").data.data[0].data.data[1].data, StringType)
        assert isinstance(env.get_type("split").data.data[1].data.data, CartType)  
        assert isinstance(env.get_type("split").data.data[1].data.data.data[0].data, IntegerType)
        assert isinstance(env.get_type("split").data.data[1].data.data.data[1].data, StringType)      
        interpret(root, env) 
        assert isinstance(root.children[4], AAssertionsMachineClause)
        interpret(root.children[4], env)

                
    def test_library_chars(self):
        string = '''
        MACHINE LibraryStrings
        CONSTANTS chars, length, append
        PROPERTIES
          append = %(x,y).(x: STRING & y: STRING | STRING_APPEND(x,y)) & 
		  /* obtain the characters of a string as a B sequence of strings of length 1 */
		  chars: STRING --> (INTEGER <-> STRING) &
		  chars = %(s).(s:STRING|STRING_CHARS(s)) &
		  /* compute the length of a string */
          length: STRING --> INTEGER &
          length = %x.(x:STRING|STRING_LENGTH(x)) 
        DEFINITIONS
          EXTERNAL_FUNCTION_STRING_APPEND == STRING*STRING --> STRING;
          STRING_APPEND(x,y) == append(x,y);
		  STRING_CHARS(x) == chars(x);
		  EXTERNAL_FUNCTION_STRING_CHARS == (STRING --> (INTEGER<->STRING));
		  STRING_LENGTH(x) == length(x);
          EXTERNAL_FUNCTION_STRING_LENGTH == STRING --> INTEGER
        ASSERTIONS
		  chars("") = <>;
		  chars("abc") = ["a","b","c"];
		  /* find strings with b as character: */
		  {x|x:{"abc","abcabc","hello"} & "b" : ran(chars(x))} = {"abc", "abcabc"};
		  /* now find strings which have the same character set */
		  {x|x:{"abc","abcabc","hello"} & 
			#y.(y:{"abc","abcabc","hello"} & ran(chars(x))=ran(chars(y)) & x/=y)} = {"abc", "abcabc"};
			!(x,y).(x:{"abc","hello",""} & y:{"abc","hello",""}
			  => chars(append(x,y)) = chars(x)^chars(y))

        END
        '''
        # TODO: performance		  
		#  /* now find permutations */
		#  {x|x:{"abc","hello","cba",""} & #(y,p).(y:{"abc","hello","cba",""} & p:perm(1..size(chars(x))) &  x/=y & length(x)=length(y) & /* a bit slower without this condition */
		#  (p;chars(x)) = chars(y))} = {"abc","cba"}
		# TODO: performance (30 sec)
		#  card({x,y,z,v| x: {"abc","abcabcd","filename.ext","/usr/local/lib"} & 
        #      y:ran(chars(x)) & z:ran(chars(x)) & y/=z & 
        #      v:ran(chars(x)) & y/=v & z/=v &
        #      length(x)+length(y)+length(z)+length(v)=6 }) = 6;
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string
        
        # Test
        env = Environment()
        dh = DefinitionHandler(env)                                   
        dh.repl_defs(root)
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        assert isinstance(env.get_type("chars"), PowerSetType)
        assert isinstance(env.get_type("chars").data, CartType)
        assert isinstance(env.get_type("chars").data.data[0].data, StringType)
        assert isinstance(env.get_type("chars").data.data[1].data.data, CartType)  
        assert isinstance(env.get_type("chars").data.data[1].data.data.data[0].data, IntegerType)
        assert isinstance(env.get_type("chars").data.data[1].data.data.data[1].data, StringType) 
        interpret(root, env) 
        assert isinstance(root.children[4], AAssertionsMachineClause)
        interpret(root.children[4], env)
 
      
    def test_library_codes(self):
        string = '''
        MACHINE LibraryStrings
        CONSTANTS codes, append
        PROPERTIES
          append = %(x,y).(x: STRING & y: STRING | STRING_APPEND(x,y)) &
          /* obtain the characters of a string as a B sequence of Ascii codes; it is reversible */
		  codes: STRING --> (INTEGER <-> INTEGER) &
		  codes = %(s).(s:STRING|STRING_CODES(s))
        DEFINITIONS
		  STRING_CODES(x) == codes(x);
		  EXTERNAL_FUNCTION_STRING_CODES == (STRING --> (INTEGER<->INTEGER));
          EXTERNAL_FUNCTION_STRING_APPEND == STRING*STRING --> STRING;
          STRING_APPEND(x,y) == append(x,y)		  
        ASSERTIONS
		  codes("") = <>;
		  /* codes(" ") = [32]; the Java parser currently swallows whitespace within strings */
		  codes("abc") = [97,98,99];
		  {x| codes(x) = codes("abc") ^ codes("abc")} = {"abcabc"};
		  !(x,y).(x:{"abc","hello",""} & y:{"abc","hello",""}
			  => codes(append(x,y)) = codes(x)^codes(y))
        END
        '''	  
		# FIXME: composition typechecking bug
		#		  {x| codes(x) = (codes("abc") ; succ) } = {"bcd"};
		# TODO: prolog style args
		# {x| codes(x) = %i.(i:1..26|96+i)} = {"abcdefghijklmnopqrstuvwxyz"}
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string
        
        # Test
        env = Environment()
        dh = DefinitionHandler(env)                                   
        dh.repl_defs(root)
        mch = parse_ast(root, env)
        type_check_bmch(root, env, mch)
        assert isinstance(env.get_type("codes"), PowerSetType)
        assert isinstance(env.get_type("codes").data, CartType)
        assert isinstance(env.get_type("codes").data.data[0].data, StringType)
        assert isinstance(env.get_type("codes").data.data[1].data.data, CartType)  
        assert isinstance(env.get_type("codes").data.data[1].data.data.data[0].data, IntegerType)
        assert isinstance(env.get_type("codes").data.data[1].data.data.data[1].data, IntegerType) 
        interpret(root, env) 
        assert isinstance(root.children[4], AAssertionsMachineClause)
        interpret(root.children[4], env)
                

  

  

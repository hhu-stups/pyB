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
        #interpret(root, env) #performance: improve constraintsolving first


    def test_library_append(self):        
        string = '''
        MACHINE m
        DEFINITIONS
            EXTERNAL_FUNCTION_STRING_APPEND == STRING*STRING --> STRING;
            STRING_APPEND(x,y) == aa(x,y);
        ABSTRACT_CONSTANTS
            aa
        PROPERTIES
            aa = %(x,y).(x: STRING & y: STRING | STRING_APPEND(x,y)) 
        END'''
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
        assert isinstance(env.get_type("aa"), PowerSetType)
        assert isinstance(env.get_type("aa").data, CartType)
        assert isinstance(env.get_type("aa").data.data[0].data, CartType)
        assert isinstance(env.get_type("aa").data.data[0].data.data[0].data, StringType)
        assert isinstance(env.get_type("aa").data.data[0].data.data[1].data, StringType)
        assert isinstance(env.get_type("aa").data.data[1].data, StringType)
        interpret(root, env) #performance: improve constraintsolving first
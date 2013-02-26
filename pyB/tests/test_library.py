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
        dh = DefinitionHandler()                                   
        dh.repl_defs(root)
        env = Environment()
        mch = parse_ast(root, env)
        type_check_bmch(root, mch)
        #interpret(root, env) #performance: improve constraintsolving first
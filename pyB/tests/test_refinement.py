# -*- coding: utf-8 -*-
from ast_nodes import *
from environment import Environment
from interp import interpret
from helpers import file_to_AST_str, string_to_file
file_name = "input.txt"

class TestRefinement():
    def test_examples_bookr(self):
        string = '''
        REFINEMENT        BooksR
        REFINES           Books
        VARIABLES         scheme
        INVARIANT         scheme : iseq(BOOK) & ran(scheme) = BOOK - read
        INITIALISATION    scheme :: perm(BOOK)
        OPERATIONS
            bb <-- newbook = PRE scheme /= <> THEN  /* added by mal */
                bb := first(scheme);scheme := tail(scheme) END
        END
        '''
        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string
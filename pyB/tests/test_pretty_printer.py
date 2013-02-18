# -*- coding: utf-8 -*-
from ast_nodes import *
from helpers import file_to_AST_str, string_to_file
from pretty_printer import pretty_print

file_name = "input.txt"

class TestPrettyPrinter():
    def test_pp_numbers(self):
        # Build AST
        string_to_file("#PREDICATE 1+2<3 & 4-5>6 & 7*8>=9 & 10/11<=12 & 13 mod 14=15 & 1/=1", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # PPrint
        out = pretty_print(root.children[0])
        assert out=="1+2<3 & 4-5>6 & 7*8>=9 & 10/11<=12 & 13 mod 14=15 & 1/=1"
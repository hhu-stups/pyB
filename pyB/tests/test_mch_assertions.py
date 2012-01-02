# -*- coding: utf-8 -*-
from ast_nodes import *
from interp import interpret, Environment
from helpers import file_to_AST_str, string_to_file

file_name = "input.txt"

class TestInterpSets():
    def test_abrial_book(self):
        string = '''
        MACHINE BBook_Page80
        /* Translation of example from page 82 of Abrial's B-Book */
        CONSTANTS p,q,u,s,t
        PROPERTIES
        p = {3|->5, 3|->9, 6|->3, 9|->2} &
        q = {2|->7, 3|->4, 5|->1, 9|->5} &
        u = {1,2,3} &
        s = {4,7,3} &
        t = {4,8,1}
        ASSERTIONS
        p~ = {5|->3, 9|->3, 3|->6, 2|->9};
        dom(p) = {3,6,9};
        ran(p) = {5,9,3,2};
        (p;q) = {3|->1, 3|->5, 6|->4, 9|->7};
        id(u) = {1|->1, 2|->2, 3|->3};
        s <|p = {3|->5, 3|->9};
        p |> t = {};
        s <<| p = {6|->3, 9|->2};
        p |>> t = {3|->5, 3|->9, 6|->3, 9|->2}
        END
        '''

        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env)
        assert isinstance(root.children[2], AAssertionsMachineClause)
        for pred in root.children[2].children:
            assert interpret(pred, env)
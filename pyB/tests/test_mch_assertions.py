# -*- coding: utf-8 -*-
from ast_nodes import *
from interp import interpret, Environment
from helpers import file_to_AST_str, string_to_file

file_name = "input.txt"

class TestMCHAssert():
    def test_abrial_book_page82(self):
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
        interpret(root, env) # eval CONSTANTS and PROPERTIES
        # eval ASSERTIONS (again)
        assert isinstance(root.children[2], AAssertionsMachineClause)
        for pred in root.children[2].children:
            assert interpret(pred, env)


    def test_abrial_book_page82_fail(self):
        # changes example: change 3|->5 to 1->5 in p (PROPERTIES-clause)
        string = '''
        MACHINE BBook_Page80
        /* Translation of example from page 82 of Abrial's B-Book */
        CONSTANTS p,q,u,s,t
        PROPERTIES
        p = {1|->5, 3|->9, 6|->3, 9|->2} &
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
        interpret(root, env) # eval CONSTANTS and PROPERTIES
        # eval ASSERTIONS (again)
        assert isinstance(root.children[2], AAssertionsMachineClause)
        assert not interpret(root.children[2].children[0], env)
        assert not interpret(root.children[2].children[1], env)
        assert interpret(root.children[2].children[2], env)
        assert not interpret(root.children[2].children[3], env)
        assert interpret(root.children[2].children[4], env)
        assert not interpret(root.children[2].children[5], env)
        assert interpret(root.children[2].children[6], env)
        assert not interpret(root.children[2].children[7], env)
        assert not interpret(root.children[2].children[8], env)


    def test_abrial_book_page83(self):
        string = '''
        MACHINE BBook_Page83
        /* Translation of example from page 83 of Abrial's B-Book */
        CONSTANTS p,w,q,f,g,s,t,h,k
        PROPERTIES
        p = {3|->5, 3|->9, 6|->3, 9|->2} &
        w = {1, 2, 3} &
        p[w] = {5,9} &
        q = {2|->7, 3|->4, 5|->1, 9|->5} &
        q <+ p = {3|->5, 3|->9, 6|->3, 9|->2, 2|->7, 5|->1} &
        f = {8|->10, 7|->11, 2|->11, 6|->12} &
        g = {1|->20, 7|->20, 2|->21, 1|->22} &
        f >< g = {(7|->(11|->20)), (2|->(11|->21))} &
        s = {1,4} &
        t = {2,3} &
        prj1(s,t) = {((1|->2)|->1),((1|->3)|->1),((4|->2)|->4),((4|->3)|->4)} &
        prj2(s,t) = {((1|->2)|->2),((1|->3)|->3),((4|->2)|->2),((4|->3)|->3)} &
        h = {1|->11, 4|->12} &
        k = {2|->21, 7|->22} &
        (h||k) = { (1,2) |-> (11,21), (1,7) |-> (11,22),
                    (4,2) |-> (12,21), (4,7) |-> (12,22) }
        ASSERTIONS
        p[w] = {5,9};
        q <+ p = {(3|->5),(3|->9),(6|->3),(9|->2),(2|->7),(5|->1)};
        f >< g = {(7|->(11|->20)), (2|->(11|->21))};
        prj1(s,t) = {((1|->2)|->1),((1|->3)|->1),((4|->2)|->4),((4|->3)|->4)};
        prj2(s,t) = {((1|->2)|->2),((1|->3)|->3),((4|->2)|->2),((4|->3)|->3)};
        (h||k) = { (1,2) |-> (11,21), (1,7) |-> (11,22),
                    (4,2) |-> (12,21), (4,7) |-> (12,22) }
        END'''

        # Build AST
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        interpret(root, env) # eval CONSTANTS and PROPERTIES
        # eval ASSERTIONS (again)
        assert isinstance(root.children[2], AAssertionsMachineClause)
        assert interpret(root.children[2].children[0], env)
        assert interpret(root.children[2].children[1], env)
        assert interpret(root.children[2].children[2], env)
        assert interpret(root.children[2].children[3], env)
        assert interpret(root.children[2].children[4], env)
        assert interpret(root.children[2].children[5], env)
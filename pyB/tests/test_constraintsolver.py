# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from environment import Environment
from helpers import file_to_AST_str, string_to_file
from typing import _test_typeit
from constrainsolver import calc_constraint_domain

file_name = "input.txt"

class TestConstraintSolver():
    def test_forAll(self):
        # Build AST:
        string_to_file("#PREDICATE !(z).((z:NAT & z>2 & z<5) => (z>1 & z<=10))", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        _test_typeit(root, env, [], [""])
        assert isinstance(env.get_type("z"), IntegerType)
        unqantPred = root.children[0]
        assert isinstance(unqantPred, AUniversalQuantificationPredicate)
        varList = unqantPred.children[0:-1]
        P = unqantPred.children[-1].children[0]
        Q = unqantPred.children[-1].children[1]
        assert isinstance(P, Predicate)
        assert isinstance(Q, Predicate)
        domain = calc_constraint_domain(env, varList, P)
        assert domain[0]==[3,4]

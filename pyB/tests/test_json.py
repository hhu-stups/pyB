# -*- coding: utf-8 -*-
import json
from ast_nodes import *
from btypes import *
from helpers import file_to_AST_str, string_to_file
from parsing import parse_json

file_name = "input.txt"

class TestJSON():
    def test_json_add(self):
        import helpers
        helpers.option_str = "-json"
        
        # Build AST
        string_to_file("#PREDICATE 1+1=3", file_name)
        ast_string = file_to_AST_str(file_name)
        lst = json.loads(ast_string)
        root = parse_json(lst)
        
        # Test
        assert isinstance(root, APredicateParseUnit)
        assert isinstance(root.children[0], AEqualPredicate)
        assert isinstance(root.children[0].children[0], AAddExpression)
        assert isinstance(root.children[0].children[1], AIntegerExpression)
        addNode = root.children[0].children[0]
        assert isinstance(addNode.children[0], AIntegerExpression)
        assert isinstance(addNode.children[1], AIntegerExpression)
        assert addNode.children[0].intValue==1
        assert addNode.children[0].intValue==1
        assert root.children[0].children[1].intValue==3
        helpers.option_str = "-python"


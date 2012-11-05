# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from bstate import BState
from config import *

# TODO: This must be a singelton object
class Environment():
    def __init__(self):
        # Types of AST-ID-Nodes: Node->type.
        # This map is used by the enumeration
        # and was created and filled by typeit of the module typing.
        self.node_to_type_map = {}
        # AST-SubTrees: ID(String)->AST
        #self.definition_id_to_ast = {}
        self.mch_operation_type = [] # rettype, opname, paratype
        self.bstate = BState(None)   # current Working B-State
        self.mch = None              # current Working B-Machine
        self.solutions = {}          # read by a solution-file
        # from config 
        # for possible modification after module import time (tests)
        self._min_int = min_int
        self._max_int = max_int


    # used for debugging and cli-ui
    def print_env(self):
        self.bstate.print_state()


    # This method should only(!) be used by the typechecking-tests.
    # It returns the type of the id "string"
    def get_type(self, string):
        assert isinstance(string,str)
        # linear search for ID with the name string
        for node in self.node_to_type_map:
            assert isinstance(node, AIdentifierExpression)
            # FIXME: scoping: if there is more than one "string"
            # e.g x:Nat & !x.(x:S=>card(x)=3)...
            if node.idName==string:
                return self.node_to_type_map[node]
        raise Exception("lookup-error: unknown type of %s" % string)


    # A KeyError or a false assert is a typechecking bug
    # Used by the eumerator: all_values
    def get_type_by_node(self, node):
        assert isinstance(node, AIdentifierExpression)
        #print "XXX:",node.idName, node, self
        assert node in self.node_to_type_map
        atype = self.node_to_type_map[node]
        assert isinstance(atype, BType)
        return atype


    # reference to the owner-mch of this state/env
    def set_mch(self, mch):
        self.mch = mch
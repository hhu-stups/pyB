# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from bstate import BState

class Environment():
    def __init__(self):
        # Types of AST-ID-Nodes: Node->type.
        # This map is used by the enumeration
        # and was created and filled by typeit of the module typing.
        self.node_to_type_map = {}
        # AST-SubTrees: ID(String)->AST
        #self.definition_id_to_ast = {}
        self.mch_operation_type = [] # rettype, opname, paratype
        self.bstate = BState()  #current Working B-State
        self.mch = None         #current Working B-Machine

    # used for debugging and cli-ui
    def print_env(self):
        #print self.mch.name
        self.bstate.print_state()
        #print "Types:"
        #for node in self.node_to_type_map:
        #    print node.idName,":", self.node_to_type_map[node]


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
        # lookup in other mch
        #if not self.mch.included_mch == [] or not self.mch.seen_mch ==[] or not self.mch.used_mch==[] or not self.mch.extended_mch==[]:
        #    for m in self.mch.included_mch + self.mch.seen_mch + self.mch.used_mch + self.mch.extended_mch:
        #        atype = m.state.get_type(string)
        #        if not atype==None:
        #            return atype
        raise Exception("lookup-error: unknown type of %s" % string)


    # A KeyError or a false assert is a typechecking bug
    # Used by the eumerator: all_values
    def get_type_by_node(self, node):
        assert isinstance(node, AIdentifierExpression)
        #print "XXX:",node.idName, node, self
        assert node in self.node_to_type_map
        atype = self.node_to_type_map[node]
        #else:
        #    # lookup in other mch
        #    if not self.bstate.mch.included_mch == [] or not self.bstate.mch.seen_mch ==[] or not self.bstate.mch.used_mch==[] or not self.bstate.mch.extended_mch==[]:
        #        for m in self.bstate.mch.included_mch + self.bstate.mch.seen_mch + self.bstate.mch.used_mch + self.bstate.mch.extended_mch:
        #            try:
        #                atype = m.env.get_type_by_node(node)
        #                assert not atype==None
        #                assert isinstance(atype, BType)
        #                return atype
        #            except Exception:
        #                continue
        #    raise Exception("lookup-error: unknown type of %s" % node.idName) 
        assert isinstance(atype, BType)
        return atype


    # reference to the owner-mch of this state/env
    def set_mch(self, mch):
        self.mch = mch
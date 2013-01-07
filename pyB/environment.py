# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from statespace import StateSpace
from config import *
from bexceptions import ValueNotInBStateException

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
        self.state_space = StateSpace()   # statespace        
        self.solutions = {}          # read by a solution-file
        # from config 
        # for possible modification after module import time (tests)
        self._min_int = MIN_INT
        self._max_int = MAX_INT
        self.root_mch = None
        self.current_mch = None              # current Working B-Machine


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


    def get_state(self):
        return self.state_space.get_state()


    def lookup_bmachine(self, idName, mch):
        for m in mch.included_mch + mch.seen_mch + mch.used_mch + mch.extended_mch:
            if idName in m.names:
                return m
            else:
                bmachine = self.lookup_bmachine(idName, m)
                if not bmachine==None:
                    return bmachine
        return None


    # encapsule kind of parse-unit and statespace
    def set_value(self, id_Name, value):
        bstate = self.get_state()
        bmachine = self.root_mch 
        try:
            bstate.set_value(id_Name, value, bmachine)
            return
        except ValueNotInBStateException:
            assert id_Name not in bmachine.names
        # lookup-fail in root. check child-bmachine
        bmachine = self.lookup_bmachine(id_Name, self.root_mch)
        bstate.set_value(id_Name, value, bmachine)

        
    def get_value(self, id_Name):
        bstate = self.get_state()
        bmachine = self.root_mch 
        try:
            return bstate.get_value(id_Name, bmachine)
        except ValueNotInBStateException:
            assert id_Name not in bmachine.names
        # lookup-fail in root. check child-bmachine
        bmachine = self.lookup_bmachine(id_Name, self.root_mch)
        return bstate.get_value(id_Name, bmachine)
    
    
    def add_ids_to_frame(self, ids):
        bstate = self.get_state()
        bmachine = self.root_mch # TODO lookup
        bstate.add_ids_to_frame(ids, bmachine)   

    
    def push_new_frame(self, nodes):
        bstate = self.get_state()
        bmachine = self.root_mch # TODO lookup
        bstate.push_new_frame(nodes, bmachine) 

    
    def pop_frame(self):
        bstate = self.get_state()
        bmachine = self.root_mch # TODO lookup
        bstate.pop_frame(bmachine) 
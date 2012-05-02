# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *

class Environment():
    def __init__(self):
        # Values of global and local vars: string -> value.
        # NEW FRAME on this stack via append <=> New Var. Scope.
        self.value_stack = [{}]
        # Types of AST-ID-Nodes: Node->type.
        # This map is used by the enumeration
        # and was created and filled by typeit of the module typing.
        self.node_to_type_map = {}
        # AST-SubTrees: ID(String)->AST
        self.definition_id_to_ast = {}
        self.last_env = None # used in undo
        self.mch = None
        self.mch_operation_type = [] # rettype, opname, paratype

    # used for debugging and cli-ui
    def print_env(self):
        print self.mch.name
        for value_map in self.value_stack:
            string = ""
            for name in value_map:
                string += name + ":" + str(value_map[name]) + " "
            print string
        for m in self.mch.included_mch:
            m.state.print_env()
        #print "Types:"
        #for node in self.node_to_type_map:
        #    print node.idName,":", self.node_to_type_map[node]


    # used in undo
    def save_last_env(self):
        import copy
        self.last_env = copy.deepcopy(self)

    def set_definition(self, id_Name, ast):
        assert isinstance(id_Name, str)
        self.definition_id_to_ast[id_Name] = ast


    def get_ast_by_definition(self, id_Name):
        assert isinstance(id_Name, str)
        return self.definition_id_to_ast[id_Name]


    def get_value(self, id_Name):
        assert isinstance(id_Name, str)
        value_map_copy =  [x for x in self.value_stack] # no ref. copy
        value_map_copy.reverse()
        stack_depth = len(value_map_copy)
        # lookup own mch:
        for i in range(stack_depth):
            try:
                return value_map_copy[i][id_Name]
            except KeyError:
                continue
        # lookup included mch:
        if not self.mch.included_mch == []:
            for m in self.mch.included_mch:
                try:
                    return m.state.get_value(id_Name)
                except KeyError:
                    continue
        # No entry in the value_stack. The Variable with the name id_Name
        # is unknown. This is an Error found by the typechecker
        # TODO: raise custom exception. e.g lookuperror
        print "LookupErr:", id_Name
        raise KeyError



    # TODO: (maybe) check if value has the correct type
    # used by tests and emumaration and substitutipn
    def set_value(self, id_Name, value):
        for i in range(len(self.value_stack)):
            top_map = self.value_stack[-(i+1)]
            if id_Name in top_map:
                top_map[id_Name] = value
                return
        # lookup included mch:
        if not self.mch.included_mch == []:
            for m in self.mch.included_mch:
                try:
                    return m.state.set_value(id_Name, value)
                except KeyError:
                    continue
        print "LookupErr:", id_Name
        raise KeyError


    def add_ids_to_frame(self, ids):
        top_map = self.value_stack[-1]
        for i in ids:
            assert isinstance(i,str)
            if not top_map.has_key(i):
                top_map[i] = None


    # This method is used only(!) by the typechecking-tests.
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


    # A KeyError or a false assert is a typechecking bug
    # Used by the eumerator: all_values
    def get_type_by_node(self, node):
        assert isinstance(node, AIdentifierExpression)
        atype = self.node_to_type_map[node]
        assert isinstance(atype, BType) 
        return atype


    # new scope:
    # push a new frame with new local vars
    def push_new_frame(self, nodes):
        # TODO: throw warning if local var with 
        # the same name like a global var. This is not a B error
        # but maybe not intended by the User
        var_map = {}
        for node in nodes:
            assert isinstance(node, AIdentifierExpression)
            var_map[node.idName] = node.idName
        self.value_stack.append(var_map)


    # leave scope: throw all values of local vars away
    def pop_frame(self):
        self.value_stack.pop()


    # reference to the owner-mch of this state/env
    def set_mch(self, mch):
        self.mch = mch
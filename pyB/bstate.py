from ast_nodes import *
from btypes import *

# BState: Set of Values
class BState():
    def __init__(self, bmachine, names=[], solutions={}):
        # Values of global and local vars: string -> value.
        # NEW FRAME on this stack via append <=> New Var. Scope.
        self.value_stack = [{}]
        self.mch = bmachine
        self.last_bstate = None # used in undo
        self._write_solutions(names, solutions)
    
    
    def _write_solutions(self, names, solutions):
        vstack = self.value_stack[-1]
        for name in names:
            if name in solutions or self.mch.name+"."+name in solutions:
                vstack[name] = solutions[name]
    
    # used in undo
    def save_last_state(self):
        import copy
        self.last_bstate = copy.deepcopy(self)
        
    def print_state(self):
        if self.mch:
            print self.mch.name
        for value_map in self.value_stack:
            string = ""
            for name in value_map:
                string += name + ":" + str(value_map[name]) + " "
            print string
        if self.mch:
            for m in self.mch.included_mch:
                m.bstate.print_state() 


    def get_value(self, id_Name):
        if isinstance(id_Name, AIdentifierExpression):
            print id_Name.idName
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
        if self.mch and (not self.mch.included_mch == [] or not self.mch.seen_mch ==[] or not self.mch.used_mch==[] or not self.mch.extended_mch==[]):
            for m in self.mch.included_mch + self.mch.seen_mch + self.mch.used_mch + self.mch.extended_mch:
                try:
                    value = m.bstate.get_value(id_Name)
                    return value
                except KeyError:
                    continue
        # No entry in the value_stack. The Variable with the name id_Name
        # is unknown. This is an Error found by the typechecker
        # TODO: raise custom exception. e.g lookuperror
        string = "get LookupErr: %s" % (id_Name)
        raise KeyError(string)


    # TODO: (maybe) check if value has the correct type
    # used by tests and emumaration and substitution
    def set_value(self, id_Name, value):
        for i in range(len(self.value_stack)):
            top_map = self.value_stack[-(i+1)]
            if id_Name in top_map:
                top_map[id_Name] = value
                return
        # lookup included mch, no seen mch!
        # if id_Name is a variable which is part of a seen mch M than self must be the state of M!
        if self.mch and (not self.mch.included_mch == [] or not self.mch.seen_mch ==[] or not self.mch.used_mch == [] or not self.mch.extended_mch==[]):
            for m in self.mch.included_mch + self.mch.seen_mch + self.mch.used_mch + self.mch.extended_mch:
                try:
                    return m.bstate.set_value(id_Name, value)
                except KeyError:
                    continue
        string = "set LookupErr: %s" % (id_Name)
        raise KeyError(string)


    # leave scope: throw all values of local vars away
    def pop_frame(self):
        self.value_stack.pop()


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


    def add_ids_to_frame(self, ids):
        top_map = self.value_stack[-1]
        for i in ids:
            assert isinstance(i,str)
            if not top_map.has_key(i):
                top_map[i] = None
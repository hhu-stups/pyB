from ast_nodes import *
from btypes import *
from bmachine import BMachine
from bexceptions import ValueNotInBStateException

# BState: Set of all Values of all B-machines 
class BState():
    def __init__(self):
        # bmch_dict is a dict of value stacks: bmachine -> list(dict1, dict2, ...)
        # Values of global and local vars: string -> value.
        # NEW FRAME on this stack via append <=> New Var. Scope.
        # special case: Predicates and Expressions have no bmachine
        # in this case the mapping is: None -> list(dict1, dict2, ...)
        self.bmch_dict = {None:[{}]} # empty entry for states without Bmachine (Predicated and Expressions)
    
    
    # TODO: implement me
    def equal(self, bstate):
        pass
        
        
    def clone(self):
        c = BState()
        for key in self.bmch_dict:
            value_stack = self.bmch_dict[key]
            vs = []
            for d in value_stack:
                vs.append(d.copy())
            #vs.reverse()
            c.bmch_dict[key] = vs
        return c
    
    
    def add_mch_state(self, bmachine, names=[], solutions={}):
        value_stack = self._write_solutions(names, solutions, bmachine)
        self.bmch_dict[bmachine] = value_stack 
 
    
    def _write_solutions(self, names, solutions, bmachine):
        vstack = {}
        for name in names:
            if name in solutions or bmachine.name+"."+name in solutions:
                vstack[name] = solutions[name]
            else:
                vstack[name] = None # default init
        return [vstack]
    

    def get_value(self, id_Name, bmachine):
        if isinstance(id_Name, AIdentifierExpression): # debug
            print id_Name.idName
        assert isinstance(id_Name, str)
        assert isinstance(bmachine, BMachine) or bmachine==None
        value_stack = self.bmch_dict[bmachine]
        value_map_copy =  [x for x in value_stack] # no ref. copy
        value_map_copy.reverse()
        stack_depth = len(value_map_copy)
        # lookup own mch:
        for i in range(stack_depth):
            try:
                return value_map_copy[i][id_Name]
            except KeyError:
                continue
        # No entry in the value_stack. The Variable with the name id_Name
        # is unknown for the machine bmachine. 
        string = "state.get() LookupError: %s" % (id_Name)
        print string
        raise ValueNotInBStateException(string)
        
        # lookup included mch:
		#         if self.mch and (not self.mch.included_mch == [] or not self.mch.seen_mch ==[] or not self.mch.used_mch==[] or not self.mch.extended_mch==[]):
		#             for m in self.mch.included_mch + self.mch.seen_mch + self.mch.used_mch + self.mch.extended_mch:
		#                 try:
		#                     value = m.bstate.get_value(id_Name)
		#                     return value
		#                 except KeyError:
		#                     continue



    # TODO: (maybe) check if value has the correct type
    # used by tests and enumeration and substitution
    def set_value(self, id_Name, value, bmachine):
        assert isinstance(bmachine, BMachine) or bmachine==None
        value_stack = self.bmch_dict[bmachine]
        for i in range(len(value_stack)):
            top_map = value_stack[-(i+1)]
            if id_Name in top_map:
                top_map[id_Name] = value
                return
        # No entry in the value_stack. The Variable with the name id_Name
        # is unknown for the machine bmachine. 
        string = "state.set() LookupError: %s" % (id_Name)
        print string
        raise ValueNotInBStateException(string)
        
        # lookup included mch, no seen mch!
        # if id_Name is a variable which is part of a seen mch M than self must be the state of M!
		#         if self.mch and (not self.mch.included_mch == [] or not self.mch.seen_mch ==[] or not self.mch.used_mch == [] or not self.mch.extended_mch==[]):
		#             for m in self.mch.included_mch + self.mch.seen_mch + self.mch.used_mch + self.mch.extended_mch:
		#                 try:
		#                     m.bstate.set_value(id_Name, value)
		#                     return
		#                 except KeyError:
		#                     continue



    # leave scope: throw all values of local vars away
    def pop_frame(self, bmachine):
        value_stack =  self.bmch_dict[bmachine]
        value_stack.pop() # ref


    # new scope:
    # push a new frame with new local vars
    def push_new_frame(self, nodes, bmachine):
        # TODO: throw warning if local var with 
        # the same name like a global var. This is not a B error
        # but maybe not intended by the User
        var_map = {}
        for node in nodes:
            assert isinstance(node, AIdentifierExpression)
            var_map[node.idName] = node.idName
        value_stack = self.bmch_dict[bmachine]
        value_stack.append(var_map) # ref


    def add_ids_to_frame(self, ids, bmachine):
        value_stack =  self.bmch_dict[bmachine]
        top_map = value_stack[-1]
        for i in ids:
            assert isinstance(i,str)
            if not top_map.has_key(i):
                top_map[i] = None
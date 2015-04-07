from ast_nodes import *
from btypes import *
from bmachine import BMachine
from bexceptions import ValueNotInBStateException
from config import USE_COSTUM_FROZENSET
if USE_COSTUM_FROZENSET:
     from rpython_b_objmodel import frozenset

# BState: Set of all values (constants and variabels) of all B-machines
# Used by state_space.py. 
class BState():
    def __init__(self):
        # (1) bmch_dict is a dict of value stacks: bmachine -> list(dict1, dict2, ...)
        # (2) Every dict maps values of global and local vars: string -> value.
        # (3) NEW FRAME (dict) on this stack via append <=> New Var. Scope.
        # special case: Predicates and Expressions have no bmachine
        # in this case the mapping is: None -> list(dict1, dict2, ...)
        self.bmch_dict = {None:[{}]} # empty entry for states without Bmachine (Predicated and Expressions)
    
    
    # debug-helper
    def print_bstate(self):
        for bmch in self.bmch_dict:
            if bmch==None:
                print "Predicate or Expression:", self.bmch_dict[bmch]
            else:
                print bmch.mch_name, ":", self.bmch_dict[bmch]
     
                
    def equal(self, bstate):
        if not len(self.bmch_dict)==len(bstate.bmch_dict):
            return False
        try:
            for bmachine_key in self.bmch_dict.keys():
                self_dictionary_list  = self.bmch_dict[bmachine_key]
                other_dictionary_list = bstate.bmch_dict[bmachine_key]
                if not len(self_dictionary_list)==len(other_dictionary_list):
                    return False
                while not len(self_dictionary_list)==0:
                    self_dictionary  = self_dictionary_list.pop()
                    other_dictionary = other_dictionary_list.pop()
                    if not len(self_dictionary)==len(other_dictionary):
                        return False
                    for key in self_dictionary.keys():
                        self_value  = self_dictionary[key]
                        other_value = other_dictionary[key]
                        if not self_value==other_value:
                            return False
        except KeyError:
            return False
        return True
        
    
    # e.g used by animation to calculated the next state 
    # without affecting the current one    
    def clone(self):
        c = BState()
        for key in self.bmch_dict:
            value_stack = self.bmch_dict[key]
            vs = []
            for d in value_stack:
                vs.append(d.copy())
            c.bmch_dict[key] = vs
        return c
 
    
    # called only once (per b-machine) after successful parsing
    def register_new_bmachine(self, bmachine, all_names):
        value_stack = {}
        for name in all_names:
            value_stack[name] = None  # default init
        self.bmch_dict[bmachine] = [value_stack]
    

    def get_value(self, id_Name, bmachine):
        #print "lookup of %s in %s" % (id_Name, bmachine.mch_name)
        #if isinstance(id_Name, AIdentifierExpression): # debug
        #    print id_Name.idName
        assert isinstance(id_Name, str)
        assert isinstance(bmachine, BMachine) or bmachine==None #None if Predicate or Expression
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
        # No entry in the value_stack. The variable/constant with the name 'id_Name'
        # is unknown for the machine 'bmachine'. 
        # case(1): called by env.get_value method: This may be ok during lookup
        # case(2): Bug inside pyB or the B machine
        if bmachine:
            name = bmachine.mch_name
        else:
            name = "Predicate or Expression"
        string = "bstate.get() LookupError: %s in %s" % (id_Name, name)
        #print string
        #self.print_bstate()
        raise ValueNotInBStateException(string)


    # TODO: (maybe) check if value has the correct type - but this can be better done static
    # used by tests and enumeration and substitution
    def set_value(self, id_Name, value, bmachine):
        #print
        #print value, id_Name
        assert isinstance(bmachine, BMachine) or bmachine==None
        value_stack = self.bmch_dict[bmachine]
        for i in range(len(value_stack)):
            top_map = value_stack[-(i+1)]
            if id_Name in top_map:
                top_map[id_Name] = value
                return
        # No entry in the value_stack. The variable/constant with the name 'id_Name'
        # is unknown for the machine 'bmachine'. 
        # case(1): called by env.get_value method: This may be ok during lookup
        # case(2): Bug inside pyB or the B machine
        if bmachine:
            name = bmachine.mch_name
        else:
            name = "Predicate or Expression"
        string = "bstate.set() LookupError: %s in %s" % (id_Name, name)
        #print string
        raise ValueNotInBStateException(string)


    # leave scope: throw all values of local vars away
    def pop_frame(self, bmachine):
        value_stack =  self.bmch_dict[bmachine]
        value_stack.pop() # ref


    # new scope:
    # push a new frame with new local vars
    def push_new_frame(self, nodes, bmachine):
        #print "push_new_frame", [x.idName for x in nodes], bmachine
        # TODO: throw warning if local var with 
        # the same name like a global var. This is not a B error
        # but maybe not intended by the User. 
        # It should be found static and not at runtime
        var_map = {}
        for node in nodes:
            assert isinstance(node, AIdentifierExpression)
            var_map[node.idName] = node.idName + "_NO_VALUE"
        value_stack = self.bmch_dict[bmachine]
        value_stack.append(var_map) # ref


    def add_ids_to_frame(self, ids, bmachine):
        #print "add_ids_to_frame", ids, bmachine
        value_stack =  self.bmch_dict[bmachine]
        top_map = value_stack[-1]
        for id in ids:
            assert isinstance(id,str)
            if not top_map.has_key(id):
                top_map[id] = None
    
    
    # used in use_constants_solutions and use_variables_solutions
    # to "manually" write to the correct entry 
    def get_bmachine_by_name(self, name):
        for bmachine in self.bmch_dict:
            if bmachine.mch_name==name:
                return bmachine
        raise Exception("BUG! unknown B-machine: %s" % name) 
    
    def get_valuestack_depth_of_all_bmachines(self):
        result = []
        # XXX: nondeterminism
        for bm in self.bmch_dict:
            valuestack_length = len(self.bmch_dict[bm])
            result.append(tuple([bm,valuestack_length]))
        return result.copy()
from ast_nodes import *
from btypes import *
from bmachine import BMachine
from bexceptions import ValueNotInBStateException
from config import USE_RPYTHON_CODE, USE_RPYTHON_MAP
from collections import OrderedDict
from rpython_b_objmodel import W_None, W_Object



if USE_RPYTHON_CODE:
    from rpython_b_objmodel import frozenset
    from rpython.rlib import jit
else:
    import mockjit as jit
    from mockjit import promote


# from  META-TRACING JUST-IN-TIME COMPILATION FOR RPYTHON by c.f. bolz    
class Structure(object):
    def __init__(self):
        self.indexes = {}
        self.other_structures = {}

    @jit.elidable
    def length(self):
        return len(self.indexes)
        
    @jit.elidable
    def getindex(self, name):
        return self.indexes.get(name, -1)
        
    @jit.elidable
    def add_attribute(self, name):
        if name not in self.other_structures: 
            new = Structure()
            new.indexes.update(self.indexes)
            new.indexes[name] = len(self.indexes)
            self.other_structures[name] = new
            return new
        return self.other_structures[name] 


EMPTY_STRUCTURE = Structure()

"""
class VariableMap(object):
    def __init__(self, cls):
        self.cls = cls
        self.map = Map()
        self.storage = []
    
    def getfield(self, name):
        map = self.map
        promote(map)
        index = map.getindex(name) 
        if index != -1:
            return self.storage[index] 
        return None
        
    def write_attribute(self, name, value): 
        map = self.map
        promote(map)
        index = map.getindex(name) 
        if index != -1:
            self.storage[index] = value
            return
        self.map = map.add_attribute(name)
        self.storage.append(value)

"""         

class RPythonMap:
    def __init__(self):
        self.storage = []
        self.structure = EMPTY_STRUCTURE
         
    def __getitem__(self, name):
        structure = jit.promote(self.structure)
        index = structure.getindex(name)
        if index != -1:
            return self.storage[index]
        raise KeyError()
             
    def __setitem__(self, name, value):
        structure = jit.promote(self.structure)
        index = structure.getindex(name)
        if index != -1:
            self.storage[index] = value
            return
        self.structure = structure.add_attribute(name)
        self.storage.append(value)  

    def __contains__(self, name):
        structure = jit.promote(self.structure)
        index = structure.getindex(name)
        return index != -1
    has_key = __contains__
        
    def copy(self):
        clone = RPythonMap()
        clone.structure = self.structure
        clone.storage = list(self.storage)
        return clone
        
    def __len__(self):
        structure = jit.promote(self.structure)
        return structure.length()
        
    def keys(self):
        return self.structure.indexes.keys()
        
                
# BState: Set of all values (constants and variabels) of all B-machines
# Used by state_space.py. 
class BState():
    def __init__(self):
        # (1) bmch_dict is a dict of value stacks: bmachine -> list(dict1, dict2, ...)
        # (2) Every dict maps values of global and local vars: string -> value.
        # (3) NEW FRAME (dict) on this stack via append <=> New Var. Scope.
        # special case: Predicates and Expressions have no bmachine
        # in this case the mapping is: None -> list(dict1, dict2, ...)
        #self.bmch_dict = OrderedDict({None:[{}]}) # empty entry for states without Bmachine (Predicated and Expressions)
        if USE_RPYTHON_MAP:
            self.bmch_list = [None]
            self.stack_list = [[RPythonMap()]]
        else:
            self.bmch_list = [None]
            self.stack_list = [[{}]]
        # used to print history 
        self.prev_bstate = None
        self.opName = ""
        self.parameter_values = None
    
    
    # debug-helper
    def print_bstate(self):
        string = self.__repr__()
        print string
        """    
    def __get_sorted_key_list(self, dic):
        key_list = []
        for key in dic:
            if key_list == []:
                key_list.append(key)
            else:
                for index in range(len(key_list)):
                    if key>key_list[index]:
                        continue
                    else:
                        key_list.insert(index,key)
        return key_list
        
        
    def __get_sorted_machine_list(self, dic):
        key_list = [] 
        for bmch in dic:
            if bmch is None:
                continue
            if key_list == []:
                key_list.append(bmch)
            else:
                for index in range(len(key_list)):
                    if bmch.mch_name > key_list[index].mch_name:
                        continue
                    else:
                        key_list.insert(index, bmch)
        if None in dic:
            key_list.append(None)
        return key_list       
        """
    # TODO: cache value, dont compute twice         
    def __repr__(self):
        string = ""
        from rpython_b_objmodel import W_Integer, W_Boolean, W_Set_Element, W_String, W_Tuple, frozenset
        #sorted_bmch_list = self.__get_sorted_machine_list(self.bmch_dict)
        #for bmch in sorted_bmch_list:
        for i in range(len(self.stack_list)):
            bmch  = self.bmch_list[i]
            if bmch is None:
                string += "Predicate or Expression:"
            else:
                string += bmch.mch_name + ":" 
            
            value_stack = self.get_bmachine_stack(bmch)               
            lst = "["
            for dic in value_stack:
                d = "{"
                #sorted_key_list = self.__get_sorted_key_list(dic)
                sorted_key_list = []
                # This code does only work for B machines. 
                if bmch is not None:
                    sorted_key_list = bmch.get_variable_printing_order()
                for k in sorted_key_list:
                #for k in dic:
                    if USE_RPYTHON_CODE:
                        w_obj = dic[k]
                        if isinstance(w_obj, W_Integer):
                            value = str(w_obj.ivalue)
                        elif isinstance(w_obj, W_Boolean):
                            value = str(w_obj.bvalue)
                        elif isinstance(w_obj, W_Set_Element):
                            value = w_obj.string
                        elif isinstance(w_obj, W_String):
                            value = w_obj.string
                        elif isinstance(w_obj, frozenset):
                            value = ""
                            for le in w_obj.lst:
                                value = value + str(le) # TODO: performance
                        elif isinstance(w_obj, W_Tuple):
                            value = str(w_obj.tvalue[0])+str(w_obj.tvalue[1])
                        else:
                            value = ""
                    else:
                        value = dic[k]
                    d += k +":"+ str(value) + " "
                d +="}"   
                lst += d
            lst += "]"
            string = string + lst + '\n' 
        return string    
   
   
    def __hash__(self):
        if USE_RPYTHON_CODE:
            from rpython.rlib.objectmodel import compute_hash
            hash_str = compute_hash(self.__repr__())
        else:
            hash_str = hash(self.__repr__())
        #print "XXX" + self.__repr__() + str(hash_str) + "XXX"
        return hash_str  
                
    def equal(self, bstate):
        if not len(self.bmch_list)==len(bstate.bmch_list):
            return False
        try:
            for j in range(len(self.stack_list)):
                self_dictionary_list  = self.stack_list[j]
                other_dictionary_list = bstate.stack_list[j]
                if not len(self_dictionary_list)==len(other_dictionary_list):
                    return False
                for i in range(len(self_dictionary_list)):
                    self_dictionary  = self_dictionary_list[i]
                    other_dictionary = other_dictionary_list[i]
                    if not len(self_dictionary)==len(other_dictionary):
                        return False
                    for key in self_dictionary.keys():
                        self_value  = self_dictionary[key]
                        other_value = other_dictionary[key]
                        if self_value is None and other_value is None:
                            continue
                        if USE_RPYTHON_CODE:
                            assert isinstance(self_value, W_Object)
                            assert isinstance(other_value, W_Object)
                            if not self_value.__eq__(other_value):
                                return False
                        else:
                            if not self_value==other_value:
                                return False
        except KeyError:
            return False
        return True
        
    
    # e.g used by animation to calculated the next state 
    # without affecting the current one    
    def clone(self):
        c = BState()
        for i in range(len(self.stack_list)):
            value_stack = self.stack_list[i]
            vs = []
            for d in value_stack:
                vs.append(d.copy())
            if i==0:
                c.stack_list[0] = vs
            else:
                c.stack_list.append(vs)
        assert len(c.stack_list)==len(self.stack_list)
        c.bmch_list = self.bmch_list # this is only ok because it is not possible to add or remove machines during model checking
        c.prev_bstate = self.prev_bstate
        c.opName = self.opName
        c.parameter_values = self.parameter_values
        return c
 
    
    # called only once (per b-machine) after successful parsing
    def register_new_bmachine(self, bmachine, all_names):
        assert bmachine is not None
        
        if USE_RPYTHON_MAP:
            value_dict = RPythonMap()
        else:
            value_dict = {}
        for name in all_names:
            value_dict[name] = None  # default init
        
        assert len(self.stack_list)==len(self.bmch_list)
        
        bmachine.index = len(self.bmch_list)  
        self.bmch_list.append(bmachine)
        self.stack_list.append([value_dict])
    
    def get_bmachine_stack(self, bmachine):
        if bmachine is None:
            return self.stack_list[0]
        return self.stack_list[bmachine.index]
    
    @jit.unroll_safe
    def get_value(self, id_Name, bmachine):
        #print "lookup of %s in %s" % (id_Name, bmachine.mch_name)
        #if isinstance(id_Name, AIdentifierExpression): # debug
        #    print id_Name.idName
        assert isinstance(id_Name, str)
        assert isinstance(bmachine, BMachine) or bmachine is None #None if Predicate or Expression
        value_stack = self.get_bmachine_stack(bmachine)
        #stack_depth = len(value_stack)
        # lookup own mch:
        for i in range(len(value_stack)-1, -1, -1):
            try:
                result = value_stack[i][id_Name]
                return result
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
    @jit.unroll_safe
    def set_value(self, id_Name, value, bmachine):
        #print
        #print value, id_Name
        assert isinstance(bmachine, BMachine) or bmachine is None
        value_stack = self.get_bmachine_stack(bmachine)
        for i in range(len(value_stack)-1, -1, -1):
            top_map = value_stack[i]
            #print "fooooo", top_map.storage, top_map.keys(), value 
            if id_Name in top_map.keys():
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
        value_stack = self.get_bmachine_stack(bmachine)
        value_stack.pop() # ref


    # new scope:
    # push a new frame with new local vars
    def push_new_frame(self, nodes, bmachine):
        #print "push_new_frame", [x.idName for x in nodes], bmachine
        # TODO: throw warning if local var with 
        # the same name like a global var. This is not a B error
        # but maybe not intended by the User. 
        # It should be found static and not at runtime
        if USE_RPYTHON_MAP:
            var_map = RPythonMap()
        else:
            var_map = {}
        for node in nodes:
            assert isinstance(node, AIdentifierExpression)
            if USE_RPYTHON_CODE:
                var_map[node.idName] = W_None()
            else:
                var_map[node.idName] = node.idName + "_NO_VALUE"
        value_stack = self.get_bmachine_stack(bmachine)
        value_stack.append(var_map) # ref

    @jit.unroll_safe
    def add_ids_to_frame(self, ids, bmachine):
        #print "add_ids_to_frame", ids, bmachine
        if bmachine is not None:
            bmachine.add_to_variable_printing_order(ids)
        
        value_stack = self.get_bmachine_stack(bmachine)
            
        top_map = value_stack[-1]
        for id in ids:
            assert isinstance(id,str)
            if not top_map.has_key(id):
                top_map[id] = None
    
    
    # used in use_constants_solutions and use_variables_solutions
    # to "manually" write to the correct entry 
    def get_bmachine_by_name(self, name):
        for bmachine in self.bmch_list:
            if bmachine is not None and bmachine.mch_name==name:
                return bmachine
        raise Exception("PyB BUG! unknown B-machine: %s" % name) 
   
    """ 
    def get_valuestack_depth_of_all_bmachines(self):
        result = []
        # XXX: nondeterminism
        for value_stack in self.stack_list:
            valuestack_length = len(value_stack)
            result.append(tuple([bm,valuestack_length]))
        return result.copy()
    """
        
    def add_prev_bstate(self, prev, opName, parameter_values):
        self.prev_bstate = prev
        self.opName = opName
        self.parameter_values = parameter_values
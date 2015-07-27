from ast_nodes import *
from config import USE_RPYTHON_CODE
from enumeration import create_all_seq_w_fixlen
from relation_helpers import *
from symbolic_sets import SymbolicSet


if USE_RPYTHON_CODE:
     from rpython_b_objmodel import frozenset

# represents NOT a sequence, but a set of sequences
class SymbolicSequenceSet(SymbolicSet):
    def __init__(self, aset, env, interpret, node):
        SymbolicSet.__init__(self, env, interpret)
        self.aset = aset
        self.node = node  
    
    def make_generator(self):
        yield frozenset([])
        S = self.aset
        for i in range(1, self.env._max_int+1):
            sequences = create_all_seq_w_fixlen(list(S),i)
            for sequence in sequences:
                yield sequence
        
    def __contains__(self, element):
        S = self.aset
        if not is_a_function(element):
            return False
        
        for tup in element:
            number = tup[0]
            e      = tup[1]
            if not isinstance(number, int) or number>len(element) or number<1:
                return False 
            if e not in S:
                return False
        return True
        

class SymbolicSequence1Set(SymbolicSet):
    def __init__(self, aset, env, interpret, node):
        SymbolicSet.__init__(self, env, interpret)
        self.aset = aset
        self.node = node  
    
    def make_generator(self):
        S = self.aset
        for i in range(1, self.env._max_int+1):
            sequences = create_all_seq_w_fixlen(list(S),i)
            for sequence in sequences:
                yield sequence
        
    def __contains__(self, element):
        S = self.aset
        if element==frozenset([]):
            return False  
        if not is_a_function(element):
            return False
        
        for tup in element:
            number = tup[0]
            e      = tup[1]
            if not isinstance(number, int) or number>len(element) or number<1:
                return False 
            if e not in S:
                return False
        return True
            
        

class SymbolicISequenceSet(SymbolicSet):
    def __init__(self, aset, env, interpret, node):
        SymbolicSet.__init__(self, env, interpret)
        self.aset = aset
        self.node = node  
    
    def make_generator(self):
        yield frozenset([])
        S = self.aset
        for i in range(1, self.env._max_int+1):
            sequences = create_all_seq_w_fixlen(list(S),i)
            for sequence in sequences:
                if is_a_inje_function(sequence):
                    yield sequence
        
    def __contains__(self, element):
        S = self.aset
        if not is_a_inje_function(element):
            return False
        if not is_a_function(element):
            return False
        
        for tup in element:
            number = tup[0]
            e      = tup[1]
            if not isinstance(number, int) or number>len(element) or number<1:
                return False 
            if e not in S:
                return False
        return True


class SymbolicISequence1Set(SymbolicSet):
    def __init__(self, aset, env, interpret, node):
        SymbolicSet.__init__(self, env, interpret)
        self.aset = aset
        self.node = node  
    
    def make_generator(self):
        yield frozenset([]) #TODO: check this
        S = self.aset
        for i in range(1, self.env._max_int+1):
            sequences = create_all_seq_w_fixlen(list(S),i)
            for sequence in sequences:
                if is_a_inje_function(sequence):
                    yield sequence
        
    def __contains__(self, element):
        S = self.aset
        if element==frozenset([]):
            return False  
        if not is_a_inje_function(element):
            return False
        if not is_a_function(element):
            return False
         
        for tup in element:
            number = tup[0]
            e      = tup[1]
            if not isinstance(number, int) or number>len(element) or number<1:
                return False 
            if e not in S:
                return False
        return True
        
  
class SymbolicPermutationSet(SymbolicSet):
    def __init__(self, aset, env, interpret, node):
        SymbolicSet.__init__(self, env, interpret)
        self.aset = aset
        self.node = node  
    
    def make_generator(self):
        S = self.aset
        for i in range(1, self.env._max_int+1):
            sequences = create_all_seq_w_fixlen(list(S),i)
            for sequence in sequences:
                if is_a_inje_function(sequence) and is_a_surj_function(sequence, S):
                    yield sequence
        
    def __contains__(self, element):
        S = self.aset   
        if not is_a_surj_function(element, S):
            return False
        if not is_a_inje_function(element):
            return False
        if not is_a_function(element):
            return False
             
        for tup in element:
            number = tup[0]
            e      = tup[1]
            if not isinstance(number, int) or number>len(element) or number<1:
                return False 
            if e not in S:
                return False
        return True       
        
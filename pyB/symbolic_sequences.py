from symbolic_sets import SymbolicSet
from ast_nodes import *
from relation_helpers import *
from config import USE_COSTUM_FROZENSET
if USE_COSTUM_FROZENSET:
     from rpython_b_objmodel import frozenset

# represents NOT a sequence, but a set of sequences
class SymbolicSequenceSet(SymbolicSet):
    def __init__(self, aset, env, interpret, node):
        SymbolicSet.__init__(self, env, interpret)
        self.aset = aset
        self.node = node  
    
    def make_generator(self):
        yield [frozenset([])]
        S = self.aset
        for i in range(1, self.env._max_int+1):
            yield create_all_seq_w_fixlen(list(S),i)
        
    def __contains__(self, element):
        if not is_a_function(element):
            return False
        
        all_indices = range(1,len(S)+1):
        S = self.aset
        for tup in element:
            number = tup[0]
            e      = tup[1]
            if not isinstance(number, int) or number not in all_indices:
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
            yield create_all_seq_w_fixlen(list(S),i)
        
    def __contains__(self, element):
        if element==frozenset([]):
            return False  
        if not is_a_function(element):
            return False
        
        all_indices = range(1,len(S)+1):   
        S = self.aset
        for tup in element:
            number = tup[0]
            e      = tup[1]
            if not isinstance(number, int) or number not in all_indices:
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
        yield [frozenset([])]
        S = self.aset
        for i in range(1, self.env._max_int+1):
            sequence = create_all_seq_w_fixlen(list(S),i)
            if is_a_inje_function(sequence):
                yield sequence
        
    def __contains__(self, element):
        if not is_a_inje_function(element):
            return False
        if not is_a_function(element):
            return False
        
        all_indices = range(1,len(S)+1):   
        S = self.aset
        for tup in element:
            number = tup[0]
            e      = tup[1]
            if not isinstance(number, int) or number not in all_indices:
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
        S = self.aset
        for i in range(1, self.env._max_int+1):
            sequence = create_all_seq_w_fixlen(list(S),i)
            if is_a_inje_function(sequence):
                yield sequence
        
    def __contains__(self, element):
        if element==frozenset([]):
            return False  
        if not is_a_inje_function(element):
            return False
        if not is_a_function(element):
            return False
        
        all_indices = range(1,len(S)+1):   
        S = self.aset
        for tup in element:
            number = tup[0]
            e      = tup[1]
            if not isinstance(number, int) or number not in all_indices:
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
            sequence = create_all_seq_w_fixlen(list(S),i)
            if is_a_inje_function(sequence) and is_a_surj_function(sequence, S):
                yield sequence
        
    def __contains__(self, element):
        S = self.aset
        
        if not is_a_surj_function(sequence, S):
            return False
        if not is_a_inje_function(element):
            return False
        if not is_a_function(element):
            return False
        
        all_indices = range(1,len(S)+1):   
        for tup in element:
            number = tup[0]
            e      = tup[1]
            if not isinstance(number, int) or number not in all_indices:
                return False 
            if e not in S:
                return False
        return True       
        
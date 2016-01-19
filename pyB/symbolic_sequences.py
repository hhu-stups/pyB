from ast_nodes import *
from config import USE_RPYTHON_CODE
from enumeration import create_all_seq_w_fixlen
from relation_helpers import *
from rpython_b_objmodel import W_Object
from symbolic_sets import SymbolicSet


if USE_RPYTHON_CODE:
     from rpython_b_objmodel import frozenset
     
     
def _check_element_in_sequence(element, sequence):
	for tup in element:
		if USE_RPYTHON_CODE:
			number = tup.tvalue[0].ivalue
			e      = tup.tvalue[1]
		else:
			number = tup[0]
			e      = tup[1]
		if not isinstance(number, int) or number>len(element) or number<1:
			return False 
		if not sequence.__contains__(e):
			return False
	return True
        
class AbstractSymbolicSequence(SymbolicSet):
    def enumerate_all(self):
        if not self.explicit_set_computed:
            assert isinstance(self, W_Object)
            assert isinstance(self, SymbolicSet)
            result = []
            # RPython typing constraints made this ugly code necessary 
            if isinstance(self, SymbolicSequenceSet):
                for e in self.SymbolicSequenceSet_generator():
                     result.append(e)
            elif isinstance(self, SymbolicSequence1Set):
                for e in self.SymbolicSequence1Set_generator():
                     result.append(e)
            elif isinstance(self, SymbolicISequenceSet):
                for e in self.SymbolicISequenceSet_generator():
                     result.append(e)
            elif isinstance(self, SymbolicISequence1Set):
                for e in self.SymbolicISequence1Set_generator():
                     result.append(e)
            elif isinstance(self, SymbolicPermutationSet):
                for e in self.SymbolicPermutationSet_generator():
                     result.append(e)  
            else:
                raise Exception("INTERNAL ERROR: unimplemented sequence enumeration")                                           
            self.explicit_set_repr = frozenset(result)
            self.explicit_set_computed = True
        return self.explicit_set_repr

    def __repr__(self):
        return "@symbolic sequence"
        
# represents NOT a sequence, but a set of sequences
class SymbolicSequenceSet(AbstractSymbolicSequence):
    def __init__(self, aset, env, node):
        SymbolicSet.__init__(self, env)
        self.aset = aset
        self.node = node  
    
    def SymbolicSequenceSet_generator(self):
        yield frozenset([])
        S = self.aset
        for i in range(1, self.env._max_int+1):
            if USE_RPYTHON_CODE:
                images = S.lst
            else:
                images = list(S)
            sequences = create_all_seq_w_fixlen(images, i)
            for sequence in sequences:
                yield sequence

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicSequenceSet_gen = self.SymbolicSequenceSet_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicSequenceSet_gen.next()   
                
    def __contains__(self, element):
        S = self.aset
        if not is_a_function(element):
            return False    
        return _check_element_in_sequence(element, S)
        

class SymbolicSequence1Set(AbstractSymbolicSequence):
    def __init__(self, aset, env, node):
        SymbolicSet.__init__(self, env)
        self.aset = aset
        self.node = node  
    
    def SymbolicSequence1Set_generator(self):
        S = self.aset
        for i in range(1, self.env._max_int+1):
            if USE_RPYTHON_CODE:
                images = S.lst
            else:
                images = list(S)
            sequences = create_all_seq_w_fixlen(images, i)
            for sequence in sequences:
                yield sequence

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicSequence1Set_gen = self.SymbolicSequence1Set_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicSequence1Set_gen.next()   
                
    def __contains__(self, element):
        S = self.aset
        if element==frozenset([]):
            return False  
        if not is_a_function(element):
            return False
        return _check_element_in_sequence(element, S)
            


class SymbolicISequenceSet(AbstractSymbolicSequence):
    def __init__(self, aset, env, node):
        SymbolicSet.__init__(self, env)
        self.aset = aset
        self.node = node  
    
    def SymbolicISequenceSet_generator(self):
        yield frozenset([])
        S = self.aset
        for i in range(1, self.env._max_int+1):
            if USE_RPYTHON_CODE:
                images = S.lst
            else:
                images = list(S)
            sequences = create_all_seq_w_fixlen(images, i)
            for sequence in sequences:
                if is_a_inje_function(sequence):
                    yield sequence

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicISequenceSet_gen = self.SymbolicISequenceSet_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicISequenceSet_gen.next() 
                
    def __contains__(self, element):
        S = self.aset
        if not is_a_inje_function(element):
            return False
        if not is_a_function(element):
            return False
        return _check_element_in_sequence(element, S)

  
class SymbolicISequence1Set(AbstractSymbolicSequence):
    def __init__(self, aset, env, node):
        SymbolicSet.__init__(self, env)
        self.aset = aset
        self.node = node  
    
    def SymbolicISequence1Set_generator(self):
        yield frozenset([]) #TODO: check this
        S = self.aset
        for i in range(1, self.env._max_int+1):
            if USE_RPYTHON_CODE:
                images = S.lst
            else:
                images = list(S)
            sequences = create_all_seq_w_fixlen(images, i)
            for sequence in sequences:
                if is_a_inje_function(sequence):
                    yield sequence

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicISequence1Set_gen = self.SymbolicISequence1Set_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicISequence1Set_gen.next() 
                
    def __contains__(self, element):
        S = self.aset
        if element==frozenset([]):
            return False  
        if not is_a_inje_function(element):
            return False
        if not is_a_function(element):
            return False
        return _check_element_in_sequence(element, S)
        

class SymbolicPermutationSet(AbstractSymbolicSequence):
    def __init__(self, aset, env, node):
        SymbolicSet.__init__(self, env)
        self.aset = aset
        self.node = node  
    
    def SymbolicPermutationSet_generator(self):
        S = self.aset
        for i in range(1, self.env._max_int+1):
            if USE_RPYTHON_CODE:
                images = S.lst
            else:
                images = list(S)
            sequences = create_all_seq_w_fixlen(images, i)
            for sequence in sequences:
                if is_a_inje_function(sequence) and is_a_surj_function(sequence, S):
                    yield sequence
 
    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicPermutationSet_gen = self.SymbolicPermutationSet_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicPermutationSet_gen.next() 
               
    def __contains__(self, element):
        S = self.aset   
        if not is_a_surj_function(element, S):
            return False
        if not is_a_inje_function(element):
            return False
        if not is_a_function(element):
            return False
        return _check_element_in_sequence(element, S)     
        
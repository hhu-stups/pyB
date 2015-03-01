# Wrapped basic types to allow RPYTHOn Typing (everthing is a W_Object)

class W_Object:
    pass

# sadly only single inheritance allow in RPYTHON :(
# reimplementation of all needed integer operations
# special methods are NOT supported by RPython. But they allow easy switching of
# build-in types and wrapped types in the python version. A measurement of 
# speed- and space-loose  is possible.
# Immutable (always return W_XXX) to get better performance results with RPTYHON-tranlation
# TODO: < > <=
class W_Integer(W_Object):
    def __init__(self, value):
        assert isinstance(value, int)
        self.value = value
    
    def __add__(self, other):
        assert isinstance(other, W_Integer)
        return W_Integer(self.value+other.value)   
    
    def __sub__(self, other):
        assert isinstance(other, W_Integer)
        return W_Integer(self.value - other.value)         

    def __mul__(self, other):
        assert isinstance(other, W_Integer)
        return W_Integer(self.value * other.value)
        
    def __div__(self, other):
        assert isinstance(other, W_Integer)
        return W_Integer(self.value / other.value)      
        
    def __lt__(self, other):
        assert isinstance(other, W_Integer)
        return W_Boolean(self.value < other.value)   
        
    def __le__(self, other):
        assert isinstance(other, W_Integer)
        return W_Boolean(self.value <= other.value)
         
    def __eq__(self, other):
        assert isinstance(other, W_Integer)
        return W_Boolean(self.value < other.value) 
        
    def __ne__(self, other):
        assert isinstance(other, W_Integer)
        return W_Boolean(self.value != other.value) 
            
    def __gt__(self, other):
        assert isinstance(other, W_Integer)
        return W_Boolean(self.value > other.value) 
        
    def __ge__(self, other):
        assert isinstance(other, W_Integer)
        return W_Boolean(self.value >= other.value) 
    
    def __neg__(self):
        return W_Integer(-1*self.value)


class W_Boolean(W_Object):
    def __init__(self, value):
        assert isinstance(value, bool)
        self.value = value 
      
    def __and__(self, other):
        assert isinstance(other, W_Boolean)
        return W_Boolean(self.value and other.value)
                
    def __or__(self, other):
        assert isinstance(other, W_Boolean)
        return W_Boolean(self.value or other.value)
        
    def __not__(self):
        return W_Boolean(not self.value)

class W_None(W_Object):
    pass


# an import of this module will overwrite the frozenset build-in type
# TODO: replace with more efficient implementation 
class frozenset(W_Object):
    def __init__(self, lst=[]):
        self.lst = []
        # frozenset([1,1,2])==frozenset([1,2])
        # TODO: maybe the performance improves if cases like frozenset([1,1,2])
        # are not used by any pyB code. (only enumerated sets and the repl. needs this check than) 
        for e in lst:
            if e not in self.lst:
                self.lst.append(e)
        
    def __len__(self):
        return len(self.lst)
        
    def __contains__(self, element):
        return element in self.lst
        
    def issubset(self, other):
        for e in self.lst:
            if e not in other:
                return False
        return True
        
    def issuperset(self, other):
        for e in other.lst:
            if e not in self.lst:
                return False
        return True
    
    def union(self, other):
        result = list(other.lst)
        for e in self.lst:
            if e not in result:
                result.append(e)
        return frozenset(result)
    
    def intersection(self, other):
        result = []
        for e in self.lst:
            if e in other.lst:
                result.append(e)
        return frozenset(result)
        
    
    def difference(self, other):
        result = list(self.lst)
        for e in other.lst:
            if e in result:
                result.remove(e)
        frozenset(result)
        
    def copy(self):
        return frozenset(self.lst)
    
    # WARNING: set([1,2,3])!=frozenset([1,2,3]) 
    def __eq__(self, other):
        #print "equal", self, other
        #print self.lst, other.lst
        if not isinstance(other, frozenset):
            return False
        if not len(self)==len(other):
            return False

        for e in self.lst:
            if e not in other.lst:
                return False
        return True
        
    def __ne__(self, other):
        return not self==other  
        
    # only a copy of the instance will prevent an enumeration bug. This 
    # Bug ocures when the set is enumerated twice(or more) at the same time
    # e.g 
    # for x in S:
    #    for y in S: ...
    # (used by recursive generators 
    def __iter__(self):
        copy = frozenset(self.lst)
        copy.generator = self.make_generator()
        return copy
    
    # also enables list(frozenset s) cast
    def next(self):
        return self.generator.next()
    
    def make_generator(self):
        for e in self.lst:
            yield e 
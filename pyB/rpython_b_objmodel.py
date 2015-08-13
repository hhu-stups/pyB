# Wrapped basic types to allow RPYTHOn Typing (everthing is a W_Object)

class W_Object:
    def __contains__(self, e):
        raise Exception("abstract W_Object instance _contains_ called")

class W_Tuple(W_Object):
    def __init__(self, value):
        assert isinstance(value, tuple)
        self.value = value
           
# sadly only single inheritance allow in RPYTHON :(
# reimplementation of all needed integer operations
# special methods are NOT supported by RPython. But they allow easy switching of
# build-in types and wrapped types in the python version. A measurement of 
# speed- and space-loose  is possible.
# Immutable (always return W_XXX) to get better performance results with RPTYHON-tranlation
class W_Integer(W_Object):
    def __init__(self, value):
        #assert isinstance(value, int)
        self.value = value
        
    def __repr__(self):
        return str(self.value)
        
    def __str__(self):
        return str(self.value)
    
    def __add__(self, other):
        assert isinstance(other, W_Integer)
        return (self.value+other.value)   
    
    def __sub__(self, other):
        assert isinstance(other, W_Integer)
        return (self.value - other.value)         

    def __mul__(self, other):
        assert isinstance(other, W_Integer)
        return (self.value * other.value)
        
    # Maybe unused
    def __div__(self, other):
        assert isinstance(other, W_Integer)
        return (self.value / other.value) 
        
    def __floordiv__(self, other):     
        assert isinstance(other, W_Integer)
        return (self.value // other.value) 
                
    def __lt__(self, other):
        assert isinstance(other, W_Integer)
        return self.value < other.value  
        
    def __le__(self, other):
        assert isinstance(other, W_Integer)
        return self.value <= other.value
         
    def __eq__(self, other):
        assert isinstance(other, W_Integer)
        return self.value == other.value 
        
    def __ne__(self, other):
        assert isinstance(other, W_Integer)
        return self.value != other.value 
            
    def __gt__(self, other):
        assert isinstance(other, W_Integer)
        return self.value > other.value 
        
    def __ge__(self, other):
        #assert isinstance(other, W_Integer)
        return self.value >= other.value
    
    def __neg__(self):
        return -1*self.value
        
    def __mod__(self, other):
        return (self.value % other.value)

    def __contains__(self, e):
        raise Exception("Nothing is member of a W_Integer")


class W_Boolean(W_Object):
    def __init__(self, value):
        #assert isinstance(value, bool)
        self.value = value 
      
    def __and__(self, other):
        #assert isinstance(other, W_Boolean)
        boolean = self.value and other.value
        #assert isinstance(boolean, bool)
        return boolean
                
    def __or__(self, other):
        #assert isinstance(other, W_Boolean)
        boolean = self.value or other.value
        #assert isinstance(boolean, bool)
        return boolean
        
    def __not__(self):
        boolean = not self.value
        assert isinstance(boolean, bool)
        return boolean
    
    def __eq__(self, other):
        assert isinstance(other, W_Boolean)
        boolean = self.value == other.value
        return boolean

    def __repr__(self):
        return str(self.value)
    
    def __str__(self):
        return str(self.value)

    def __contains__(self, e):
        raise Exception("Nothing is member of a W_Boolean")
        
class W_None(W_Object):
    def __contains__(self, e):
        raise Exception("Nothing is member of a W_None")

# elements of enumerated sets or machine parameter sets     
class W_Set_Element(W_Object):
    def __init__(self, string):
        self.string


class W_String(W_Object):
    def __init__(self, string):
        self.string

# an import of this module will overwrite the frozenset build-in type
# TODO: replace with more efficient implementation.
# Different enumeration order than build-in frozenset.
class frozenset(W_Object):
    def __init__(self, lst=[]):
        self.lst = []
        # frozenset([1,1,2])==frozenset([1,2])
        # TODO: maybe the performance improves if cases like frozenset([1,1,2])
        # are not used by any pyB code. (only enumerated sets and the repl. needs this check than) 
        for e in lst:
            if e not in self.lst:
                self.lst.append(e)
    
    
    def __repr__(self):
        return str(self.lst)
        
    def __len__(self):
        return len(self.lst)
        
    def __contains__(self, element):
        # Todo: avoid reference compare in list of lists (set of sets)
        return element.value in [e.value for e in self.lst]
        
    def issubset(self, other):
        for e in self.lst:
            if e not in other.lst:
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
        return frozenset(result)
        
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
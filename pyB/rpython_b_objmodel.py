# Wrapped basic types to allow RPYTHOn Typing (everthing is a W_Object)
# Immutable (always return W_XXX) to get better performance results with RPTYHON-tranlation
# except boolean methods!

class W_Object:
    _settled_ = True
    _attrs_ = []
    
    def __init__(self):
        pass
        
    def __contains__(self, e):
        raise Exception("abstract W_Object instance _contains_ called")

    def __repr__(self):
        return "w-obj"

class W_Tuple(W_Object):
    def __init__(self, tvalue):
        # e.g. W_Tuple((W_Tuple((W_Integer(1),W_Integer(2))),W_Integer(3)))
        assert isinstance(tvalue, tuple) or isinstance(tvalue, W_Tuple)
        if isinstance(tvalue, tuple):
            assert isinstance(tvalue[0], W_Object) 
            assert isinstance(tvalue[1], W_Object) 
        self.tvalue = tvalue
        
    def __eq__(self, other):
        if not isinstance(other, W_Tuple):
            return False
        return self.tvalue[0].__eq__(other.tvalue[0]) and self.tvalue[1].__eq__(other.tvalue[1])
        
    def __ne__(self, other):
        assert isinstance(other, tuple)
        return self.tvalue != other.tvalue
       
    def __getitem__(self, key):
        if key==0:
            return self.tvalue[0]
        elif key==1:
            return self.tvalue[1]
        else:
            raise Exception("PyB-ERROR: illegal tuple index in W_Tuple")      

    def __repr__(self):
        return str(self.tvalue)
    
    def clone(self):
        t0 = self.tvalue[0].clone()
        t1 = self.tvalue[1].clone()
        return W_Tuple((t0,t1))
           
# sadly only single inheritance allow in RPYTHON :(
# reimplementation of all needed integer operations
# special methods are NOT supported by RPython. But they allow easy switching of
# build-in types and wrapped types in the python version. A measurement of 
# speed- and space-loose  is possible.
class W_Integer(W_Object):
    #_settled_ = True
    
    def __init__(self, ivalue):
        assert isinstance(ivalue, int)
        self.ivalue = ivalue
        
    def __repr__(self):
        return str(self.ivalue)
        
    def __str__(self):
        return str(self.ivalue)
    
    def __add__(self, other):
        assert isinstance(other, W_Integer)
        return W_Integer(self.ivalue + other.ivalue)   
    
    def __sub__(self, other):
        assert isinstance(other, W_Integer)
        return W_Integer(self.ivalue - other.ivalue)         

    def __mul__(self, other):
        assert isinstance(other, W_Integer)
        return  W_Integer(self.ivalue * other.ivalue)
        
    # Maybe unused
    def __div__(self, other):
        assert isinstance(other, W_Integer)
        return W_Integer(self.ivalue / other.ivalue) 
        
    def __floordiv__(self, other):     
        assert isinstance(other, W_Integer)
        return W_Integer(self.ivalue // other.ivalue) 
                
    def __lt__(self, other):
        assert isinstance(other, W_Integer)
        #print "DEBUG:", self.ivalue, other.ivalue  ,self.ivalue < other.ivalue  
        return self.ivalue < other.ivalue  
        
    def __le__(self, other):
        assert isinstance(other, W_Integer)
        return self.ivalue <= other.ivalue
         
    def __eq__(self, other):
        if not isinstance(other, W_Integer):
            return False
        return self.ivalue == other.ivalue 
        
    def __ne__(self, other):
        assert isinstance(other, W_Integer)
        return self.ivalue != other.ivalue 
            
    def __gt__(self, other):
        assert isinstance(other, W_Integer)
        return self.ivalue > other.ivalue 
        
    def __ge__(self, other):
        assert isinstance(other, W_Integer)
        return self.ivalue >= other.ivalue
    
    def __neg__(self):
        return W_Integer(-1*self.ivalue)
        
    def __mod__(self, other):
        return W_Integer(self.ivalue % other.ivalue)

    def __contains__(self, e):
        raise Exception("Nothing is member of a W_Integer")

    def clone(self):
        return W_Integer(self.ivalue)

class W_Boolean(W_Object):
    #_settled_ = True
    
    def __init__(self, bvalue):
        #assert isinstance(value, bool)
        self.bvalue = bvalue 
      
    def __and__(self, other):
        assert isinstance(other, W_Boolean)
        boolean = self.bvalue and other.bvalue
        #assert isinstance(boolean, bool)
        return boolean
                
    def __or__(self, other):
        assert isinstance(other, W_Boolean)
        boolean = self.bvalue or other.bvalue
        #assert isinstance(boolean, bool)
        return boolean
        
    def __not__(self):
        boolean = not self.bvalue
        assert isinstance(boolean, bool)
        return boolean
    
    def __eq__(self, other):
        if not isinstance(other, W_Boolean):
            return False
        boolean = self.bvalue == other.bvalue
        assert isinstance(boolean, bool)
        return boolean

    def __repr__(self):
        return str(self.bvalue)
    
    def __str__(self):
        return str(self.bvalue)

    def __contains__(self, e):
        raise Exception("Nothing is member of a W_Boolean")

    def clone(self):
        return W_Boolean(self.bvalue)
        
class W_None(W_Object):
    #_settled_ = True

    def __contains__(self, e):
        raise Exception("Nothing is member of a W_None")

    def __repr__(self):
        return "None"

    def clone(self):
        return W_None()

# elements of enumerated sets or machine parameter sets     
class W_Set_Element(W_Object):
    #_settled_ = True
    
    def __init__(self, string):
        assert isinstance(string, str)
        self.string = string

    def __eq__(self, other):
        if not isinstance(other, W_Set_Element):
            return False
        return self.string==other.string

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return self.string

    def clone(self):
        return W_Set_Element(self.string)
        
class W_String(W_Object):
    #_settled_ = True
    
    def __init__(self, string):
        assert isinstance(string, str)
        self.string = string

    def __eq__(self, other):
        if not isinstance(other, W_String):
            return False
        return self.string==other.string

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return self.string

    def clone(self):
        return W_String(self.string)
        
# an import of this module will overwrite the frozenset build-in type
# TODO: replace with more efficient implementation.
# Different enumeration order than build-in frozenset.
class frozenset(W_Object):
    #_settled_ = True

    def __init__(self, L=None):
        W_Object.__init__(self)
        if L is None:
            L = []
        self.lst = []
        # frozenset([1,1,2])==frozenset([1,2])
        # TODO: maybe the performance improves if cases like frozenset([1,1,2])
        # are not used by any pyB code. (only enumerated sets and the repl. needs this check than) 
        assert isinstance(L, list)
        for e in L:
            skip = False
            for e2 in self.lst:
                if e.__eq__(e2):
                    skip = True
            if not skip:
                assert isinstance(e, W_Object)
                self.lst.append(e)
    
    
    def __repr__(self):
        return str(self.lst)
        
    def __len__(self):
        return len(self.lst)
        
    def __contains__(self, element):
        # Todo: avoid reference compare in list of lists (set of sets)
        for e in self.lst:
            if element.__eq__(e):
                return True
        return False


    def issubset(self, other):
        for e in self.lst:
            found = False
            for e2 in other.lst:
                if e.__eq__(e2):
                    found = True
            if not found:
                return False
        return True
        
    def issuperset(self, other):
        for e in other.lst:
            found = False
            for e2 in self.lst:
                if e.__eq__(e2):
                    found = True
            if not found:
                return False
        return True
 
    def union(self, other):
        result = list(other.lst)
        for e in self.lst:
            skip = False
            for e2 in result:
                if e.__eq__(e2):
                    skip = True
            if not skip:
                result.append(e)
        return frozenset(result)
    
    def intersection(self, other):
        result = []
        for e in self.lst:
            for e2 in other.lst:
                if e.__eq__(e2):
                    result.append(e)  
        return frozenset(result)
        
    def __sub__(self, other):
        return self.difference(other)
        
    def difference(self, other):
        result = list(self.lst)
        for e in other.lst:
            for e2 in result:
                if e2.__eq__(e):
                    result.remove(e)                    
        return frozenset(result)
        
    def copy(self):
        return frozenset(self.lst)
    
    # WARNING: set([1,2,3])!=frozenset([1,2,3]) 
    def __eq__(self, other):
        from symbolic_sets import SymbolicSet
        if not isinstance(other, frozenset) and not isinstance(other, SymbolicSet):
            return False
           
        assert isinstance(other, frozenset) or isinstance(other, SymbolicSet)
        if not self.__len__()==other.__len__():
            return False
        if isinstance(other, frozenset):
            for e in self.lst:
                found = False     
                for e2 in other.lst:
                    if e2.__eq__(e):
                        found = True
                        break
                if not found:   
                    return False
            return True
        else:
            for e in self.lst:
                found = False     
                for e2 in other:
                    if e2.__eq__(e):
                        found = True
                        break
                if not found:   
                    return False
            return True     
        
    def __ne__(self, other):
        return not self.__eq__(other)
        
    # only a copy of the instance will prevent an enumeration bug. This 
    # Bug ocures when the set is enumerated twice(or more) at the same time
    # e.g 
    # for x in S:
    #    for y in S: ...
    # (used by recursive generators) 
    def __iter__(self):
        copy = frozenset(self.lst)
        copy.generator = self.w_frozenset_generator()
        return copy
    
    # also enables list(frozenset s) cast
    def next(self):
        return self.generator.next()
    
    def w_frozenset_generator(self):
        for e in self.lst:
            yield e 
    
    def clone(self):
        lst = []
        for e in self.lst:
            lst.append(e.clone())
        return frozenset(lst)
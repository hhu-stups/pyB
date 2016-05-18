# Wrapped basic types to allow RPYTHOn Typing (everthing is a W_Object)
# Immutable (always return W_XXX) to get better performance results with RPTYHON-tranlation
# except boolean methods!
import sys
sys.path.append("/Users/johnwitulski/witulski/git/pyB/pypy/")
from rpython.rlib.objectmodel import r_dict
from rpython.rlib.objectmodel import compute_hash


def my_eq(obj0, obj1):
    return obj0.__eq__(obj1)

def my_hash(obj):
    return obj.__my_hash__()

class W_Object:
    #_settled_ = True
    #_attrs_ = []
    
    def __init__(self):
        pass
        
    def __contains__(self, e):
        raise Exception("abstract W_Object instance _contains_ called")

    def __repr__(self):
        return "w-obj"
        
    def __my_hash__(self):
        hash = compute_hash(self.__repr__())
        return hash

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
        
    # Cantor pairing function
    # https://en.wikipedia.org/wiki/Pairing_function
    def __my_hash__(self):
        x = self.tvalue[0].__my_hash__()
        y = self.tvalue[1].__my_hash__()
        return y+((x+y)*(x+y+1))/2

           
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


    def __my_hash__(self):
        return self.ivalue
        
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

    def __my_hash__(self):
        if self.bvalue:
            return 1
        else:
            return 0 
        
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
        self.hashmap = r_dict(my_eq, my_hash)
        # frozenset([1,1,2])==frozenset([1,2])
        # TODO: maybe the performance improves if cases like frozenset([1,1,2])
        # are not used by any pyB code. (only enumerated sets and the repl. needs this check then) 
        assert isinstance(L, list)
        for e in L:
            self.hashmap[e] = True
        self.repr_string = None
        self.hash_computed = False
        self.my_hash = 0
    
    # TODO: more efficient impl
    def __repr__(self):
        if self.repr_string is None:           
            string = ["{"]
            for e in self.hashmap:
                string.append(str(e) +",")
            string.append("}")   
            self.repr_string = "".join(string)
        return self.repr_string
        
    def __len__(self):
        return len(self.hashmap)
        
    def __contains__(self, element):
        # This uses the my_eq method.
        # In case of set of sets this will call the _eq_ method of this class
        return element in self.hashmap


    def issubset(self, other):
        for e in self.hashmap:
            if e not in other.hashmap:
                return False
        return True
        
    def issuperset(self, other):
        for e in other.hashmap:
            if e not in self.hashmap:
                return False
        return True
 
    def union(self, other):
        #new_map = r_dict(my_eq, my_hash)
        #for e in self.hashmap:
        #    new_map[e] = True
        #for e in other.hashmap:
        #    new_map[e] = True
        result = frozenset()
        new_map = self.hashmap.copy()
        new_map.update(other.hashmap)      
        result.hashmap =  new_map 
        return result
    
    def intersection(self, other):
        new_map = r_dict(my_eq, my_hash)
        for e in other.hashmap:
            if e in self.hashmap:
                new_map[e] = True
        result = frozenset()
        result.hashmap =  new_map 
        return result
        
    def __sub__(self, other):
        return self.difference(other)
        
    def difference(self, other):
        new_map = self.hashmap.copy()
        for e in other.hashmap:
            if e in new_map:
                new_map.pop(e)
        result = frozenset()
        result.hashmap =  new_map 
        return result
        
    def copy(self):
        result = frozenset()
        result.hashmap = self.hashmap.copy()
        return result
    
    # WARNING: set([1,2,3])!=frozenset([1,2,3]) 
    def __eq__(self, other):
        from symbolic_sets import SymbolicSet
        if not isinstance(other, frozenset) and not isinstance(other, SymbolicSet):
            return False
         
        assert isinstance(other, frozenset) or isinstance(other, SymbolicSet)
        if not self.__len__()==other.__len__():
            return False
        #if self.__len__()==0 and other.__len__()==0:
        #    return True
        if isinstance(other, frozenset):    
            for e in self.hashmap:
                if not e in other.hashmap:
                    return False
            for e in other.hashmap:
                if not e in self.hashmap:
                    return False
            return True
            # Wrong: e.g. {1} : {{1},{1,2}}
            #return self.hashmap == other.hashmap
        else:
            for e in self.hashmap:
                if not other.__contains__(e):
                    return False
            for e in other:
                if not e in self.hashmap:
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
        copy = frozenset()
        copy.hashmap = self.hashmap.copy()
        copy.generator = self.w_frozenset_generator()
        return copy
    
    # also enables list(frozenset s) cast
    def next(self):
        return self.generator.next()
    
    def w_frozenset_generator(self):
        for e in self.hashmap:
            yield e 
    
    def clone(self):
        new_map = self.hashmap.copy()
        clone = frozenset()
        for e in self.hashmap:
            clone.hashmap[e.clone()] = True
        return clone
        
    def to_list(self):
        #lst = []
        #for e in self.hashmap:
        #    lst.append(e)
        #return lst
        return self.hashmap.keys()
     
    
        """
    # Cantor k-tuple function
    # https://en.wikipedia.org/wiki/Pairing_function        
    def __my_hash__(self):
        if not self.hash_computed:
            hash = 0 # empty set hash is 0
            lst = self.hashmap.keys()
            if not len(lst)==0:
                hash = lst.pop().__my_hash__()
            
            while not len(lst)==0:
                x = hash
                y = lst.pop().__my_hash__()
                hash = y+((x+y)*(x+y+1))/2
            self.my_hash = hash
            self.hash_computed = True
        return self.my_hash
        """

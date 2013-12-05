# this classes represent set which should not be enumerated as long as possible (beste case: never)
# warning: some set behavior is implemented inside the interpreter
# and its helper-methodes and NOT here
# x (not)in S implemented in quick_eval.py (called by Belong-predicates x:S)

class FakeSet(object):
    def __init__(self, env):
        self.env = env # min and max int values may be needed for large sets
    
    def __mul__(self, aset):
        return FakeCartSet(self, aset)
    
    def __rmul__(self, aset):
        return FakeCartSet(aset, self)
    
    def __eq__(self, aset):
        if self.__class__ == aset.__class__:
            return True
        return False

    def __ne__(self, aset):
        if self.__class__ == aset.__class__:
            return False
        return True

class LargeSet(FakeSet):
    pass
    

class InfiniteSet(FakeSet):
    ## WARNING: python only accept int as return values
    ## so __len__ is not implemented
    pass


class NaturalSet(InfiniteSet):
    def __contains__(self, element):
        return isinstance(element, int) and element >= 0 
    
    def __le__(self, aset): # NaturalSet <= aset
        if isinstance(aset, (NaturalSet,IntegerSet)):
            return True
        return False 
    
    def __ge__(self, aset): # NaturalSet >= aset
        if isinstance(aset, (IntegerSet, IntSet)): # no neg nums
            return False
        elif isinstance(aset, frozenset):
            for x in aset:
                if x<0:
                    return False
            return True
        elif isinstance(aset, (NatSet, Nat1Set, NaturalSet, Natural1Set)):
            return True 
        raise NotImplementedError("inclusion with unknown set-type")
       
    def __lt__(self, aset): # NaturalSet < aset
        if isinstance(aset,IntegerSet):
            return True
        return False

    def __gt__(self, aset): # NaturalSet > aset
        if isinstance(aset, (IntegerSet, NaturalSet, IntSet)):
            return False
        elif isinstance(aset, frozenset):
            for x in aset:
                if x<0:
                    return False
                return True
        elif isinstance(aset, (NatSet, Nat1Set, Natural1Set)):
            return True 
        raise NotImplementedError("inclusion with unknown set-type")  
    
        

class Natural1Set(InfiniteSet):
    def __contains__(self, element):
        return isinstance(element, int) and element > 0  
    
    def __le__(self, aset): # Natural1Set <= aset
        if isinstance(aset, InfiniteSet):
            return True
        return False
 
    def __ge__(self, aset): # Natural1Set >= aset
        if isinstance(aset, (NaturalSet, IntegerSet, NatSet, IntSet)): # zero
            return False
        elif isinstance(aset, frozenset):
            for x in aset:
                if x<=0:
                    return False
            return True
        elif isinstance(aset, (Nat1Set, Natural1Set)):
            return True 
        raise NotImplementedError("inclusion with unknown set-type")

    def __lt__(self, aset): # Natural1Set < aset
        if isinstance(aset,(IntegerSet, NaturalSet)):
            return True
        return False

    def __gt__(self, aset): # Natura1lSet > aset
        if isinstance(aset,(InfiniteSet, LargeSet)):
            return False
        elif isinstance(aset, frozenset):
            for x in aset:
                if x<0:
                    return False
                return True
        raise NotImplementedError("inclusion with unknown set-type")  


# the infinite B-set INTEGER    
class IntegerSet(InfiniteSet): 
    def __contains__(self, element):
        return isinstance(element, int)
    
    def __le__(self, aset): # IntegerSet <= aset
        if isinstance(aset, IntegerSet):
            return True
        return False

    def __ge__(self, aset): # IntegerSet >= aset
        if isinstance(aset, FakeSet): 
            return True
        elif isinstance(aset, frozenset):
            for x in aset:
                if not int(x):
                    return False
            return True
        raise NotImplementedError("inclusion with unknown set-type")

    def __lt__(self, aset): # IntegerSet < aset
        return False

    def __gt__(self, aset): # IntegerSet > aset
        if isinstance(aset,IntegerSet):
            return False
        elif isinstance(aset, frozenset):
            for x in aset:
                if x<0:
                    return False
                return True
        elif isinstance(aset, (NatSet, Nat1Set, IntSet, NaturalSet, Natural1Set)):
            return True 
        raise NotImplementedError("inclusion with unknown set-type")  

        
# if min and max-int change over exec. this class will notice this change (env)
class NatSet(LargeSet):
    def __contains__(self, element):
        return isinstance(element, int) and element >=0 and element <= self.env._max_int
    
    
    def __len__(self):
        return self.env._max_int+1
     
        
    def __le__(self, aset): # NatSet <=
        if isinstance(aset, (NatSet, IntSet, NaturalSet, IntegerSet)):
            return True
        elif isinstance(aset, frozenset):
            for x in aset:
                if not self.__contains__(x):
                    return False
            return len(aset)>=self.__len__()
        elif isinstance(aset, (Natural1Set, Nat1Set)):
            return False
        raise NotImplementedError("inclusion with unknown set-type")
    
    def __ge__(self, aset): # NatSet >= aset
        if isinstance(aset, (InfiniteSet, IntSet)): 
            return False
        elif isinstance(aset, (NatSet, Nat1Set)):
            return True
        elif isinstance(aset, frozenset):
            for x in aset:
                if x<=0:
                    return False
            return True
        raise NotImplementedError("inclusion with unknown set-type")
        

    def __lt__(self, aset): # NatSet < aset
        if isinstance(aset,(IntegerSet, NaturalSet, IntSet)):
            return True
        return False
        
    def __gt__(self, aset): # NatSet > aset
        if isinstance(aset,InfiniteSet,  IntSet, NatSet):
            return False
        elif isinstance(aset, frozenset):
            for x in aset:
                if x<0:
                    return False
                return True
        elif isinstance(aset, Nat1Set):
            return True 
        raise NotImplementedError("inclusion with unknown set-type")         
        
    def __or__(self, aset):
        if isinstance(aset, NatSet):
            return self
        elif isinstance(aset, Nat1Set):
            return aset
        elif isinstance(aset, IntSet):
            return aset
        elif isinstance(aset, InfiniteSet):
            return aset
        else:
            raise NotImplementedError()
  
      
class Nat1Set(LargeSet):
    def __contains__(self, element):
        return isinstance(element, int) and element >0 and element <= self.env._max_int

    def __len__(self):
        return self.env._max_int
    
    def __le__(self, aset): # Nat1Set <=
        if isinstance(aset, (InfiniteSet, LargeSet)):
            return True
        elif isinstance(aset, frozenset):
            for x in aset:
                if not self.__contains__(x):
                    return False
            return len(aset)>=self.__len__()
        raise NotImplementedError("inclusion with unknown set-type")
    
    def __ge__(self, aset): # Nat1Set >= aset
        if isinstance(aset, (NatSet, IntSet,InfiniteSet)): 
            return False
        elif isinstance(aset, Nat1Set):
            return True
        elif isinstance(aset, frozenset):
            for x in aset:
                if x<0:
                    return False
            return True
        raise NotImplementedError("inclusion with unknown set-type")

    def __lt__(self, aset): # Nat1Set < aset
        if isinstance(aset, Nat1Set):
            return False
        return True     

    def __gt__(self, aset): # Nat1Set > aset
        if isinstance(aset,(InfiniteSet,LargeSet)):
            return False
        elif isinstance(aset, frozenset):
            for x in aset:
                if x<0:
                    return False
                return True
        raise NotImplementedError("inclusion with unknown set-type")  

class IntSet(LargeSet):
    def __contains__(self, element):
        return isinstance(element, int) and element >= self.env._min_int and element <= self.env._max_int

    def __len__(self):
        return self.env._max_int + (-1)*self.env._min_int + 1 
    
    def __le__(self, aset): # IntSet <=
        if isinstance(aset, (IntSet, IntegerSet)):
            return True
        elif isinstance(aset, frozenset):
            for x in aset:
                if not self.__contains__(x):
                    return False
            return len(aset)>=self.__len__()
        elif isinstance (aset, (NatSet, Nat1Set, NaturalSet, Natural1Set)):
            return False
        raise NotImplementedError("inclusion with unknown set-type")
    
    def __ge__(self, aset): # IntSet >= aset
        if isinstance(aset, InfiniteSet): 
            return False
        elif isinstance(aset, LargeSet):
            return True
        elif isinstance(aset, frozenset):
            for x in aset:
                if not int(x):
                    return False
            return True
        raise NotImplementedError("inclusion with unknown set-type") 

    def __lt__(self, aset): # IntSet < aset
        if isinstance(aset, IntegerSet):
            return True
        return False    

    def __gt__(self, aset): # IntSet > aset
        if isinstance(aset,(InfiniteSet, IntSet)):
            return False
        elif isinstance(aset, frozenset):
            for x in aset:
                if x<0:
                    return False
                return True
        elif isinstance(aset, (Nat1Set, NatSet)):
            return True 
        raise NotImplementedError("inclusion with unknown set-type")  

class FakeCartSet(FakeSet):
    def __init__(self, aset0, aset1):
        self.left_set = aset0
        self.right_set = aset1
    
    def __contains__(self, element):
        if isinstance(element, tuple):
            l = element[0]
            r = element[1]
        else:
            raise NotImplementedError()
        return l in self.left_set and r in self.right_set
    
    def __eq__(self, aset):
        if not isinstance(aset, FakeCartSet):
            return False
        elif (self.left_set==aset.left_set) and (self.right_set==aset.right_set):
            return True
        return False
    
    def __ne__(self, aset):
        return not self.__eq__(aset)


class FakePowerSet(FakeSet):
    pass #TODO: implement me
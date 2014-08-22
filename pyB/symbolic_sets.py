# this classes represent set which should not be enumerated as long as possible (beste case: never)
# warning: some set behavior is implemented inside the interpreter and its helper-methodes and NOT here
# design decision: most functionality should implemented in this module. the goal is that
# symbolic sets behave like frozensets (as much as possible) 
# x (not)in S implemented in quick_eval.py (called by Belong-predicates x:S)
from bexceptions import ValueNotInDomainException, DontKnowIfEqualException
from helpers import double_element_check, remove_tuples, build_arg_by_type
from btypes import *
from config import PRINT_WARNINGS
from pretty_printer import pretty_print
from symbolic_helpers import check_syntacticly_equal,make_explicit_set_of_realtion_lists 


class SymbolicSet(object):
    # evn: min and max int values may be needed for large sets 
    # interpret: for function call on tuple-sets
    def __init__(self, env, interpret):
        self.env = env 
        self.interpret = interpret
    
    def __mul__(self, aset):
        return SymbolicCartSet(self, aset, self.env, self.interpret)
    
    def __rmul__(self, aset):
        return SymbolicCartSet(aset, self, self.env, self.interpret)
    
    def __eq__(self, aset):
        if aset==None:
            return False
        print "WARNING: equalety not implemented for symbolic sets!", self," and", aset
        raise Exception("fail: can not compare symbolic set")
        #if self.__class__ == aset.__class__:
        #    return True
        #return False

    def __ne__(self, aset):
        if aset==None:
            return True
        print "WARNING: equalety not implemented for symbolic sets!", self," and", aset
        raise Exception("fail: can not compare symbolic set")
        #if self.__class__ == aset.__class__:
        #    return False
        #return True

class LargeSet(SymbolicSet):
    def __sub__(self, other):
        # TODO: add possible symbolic cases
        assert isinstance(other, frozenset)
        return self.enumerate_all()-other
    

class InfiniteSet(SymbolicSet):
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
    
    def __eq__(self, aset):
        if self.__class__ == aset.__class__:
            return True
        return False
    
    def __ne__(self, aset):
        if self.__class__ == aset.__class__:
            return False
        return True
        

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

    def __eq__(self, aset):
        if self.__class__ == aset.__class__:
            return True
        return False
    
    def __ne__(self, aset):
        if self.__class__ == aset.__class__:
            return False
        return True


# the infinite B-set INTEGER    
class IntegerSet(InfiniteSet): 
    def __contains__(self, element):
        return isinstance(element, int) or isinstance(element, IntegerType) #type for symbolic checks
    
    def __le__(self, aset): # IntegerSet <= aset
        if isinstance(aset, IntegerSet):
            return True
        return False

    def __ge__(self, aset): # IntegerSet >= aset
        if isinstance(aset, SymbolicSet): 
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
    
    def __eq__(self, aset):
        if self.__class__ == aset.__class__:
            return True
        return False
    
    def __ne__(self, aset):
        if self.__class__ == aset.__class__:
            return False
        return True

        
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

    def __eq__(self, aset):
        if self.__class__ == aset.__class__:
            return True
        return False
    
    def __ne__(self, aset):
        if self.__class__ == aset.__class__:
            return False
        return True

    def enumerate_all(self):
        return frozenset(range(0,self.env._max_int+1))
    
    def __len__(self):
        return self.env._max_int+1

    # not used for performance reasons
    #def __getitem__(self, key):
    #    return key
  
      
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

    def __eq__(self, aset):
        if self.__class__ == aset.__class__:
            return True
        return False
    
    def __ne__(self, aset):
        if self.__class__ == aset.__class__:
            return False
        return True
    
    def enumerate_all(self):
        return frozenset(range(1,self.env._max_int+1))

    def __len__(self):
        return self.env._max_int

    # not used for performance reasons
    #def __getitem__(self, key):
    #    return 1+key
        

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

    def __eq__(self, aset):
        if self.__class__ == aset.__class__:
            return True
        return False
    
    def __ne__(self, aset):
        if self.__class__ == aset.__class__:
            return False
        return True

    def enumerate_all(self):
        return frozenset(range(self.env._min_int, self.env._max_int+1))

    def __len__(self):
        return -1*self.env._min_int+self.env._max_int+1
 
    # not used for performance reasons   
    #def __getitem__(self, key):
    #    return self.env._min_int+key

class StringSet(SymbolicSet):
    def __contains__(self, element):
        return isinstance(element, str) or isinstance(element, StringType)
    
    # aSet<:STRING
    def issubset(self, aSet):
        if isinstance(aSet, StringSet):
            return True
        return False
    
    # aSet<:STRING(!)
    def issuperset(self, aSet):
        if isinstance(aSet, StringSet):
            return True
        if isinstance(aSet, frozenset):
            for e in aSet:
                if not isinstance(e, str):
                    return False
            return True
        return False
    
    def __eq__(self, aset):
        if self.__class__ == aset.__class__:
            return True
        return False
    
    def __ne__(self, aset):
        if self.__class__ == aset.__class__:
            return False
        return True
    
    def enumerate_all(self): # FIXME: hack
        return frozenset(self.env.all_strings)
  
    
class SymbolicCartSet(SymbolicSet):
    def __init__(self, aset0, aset1, env, interpret):
        SymbolicSet.__init__(self, env, interpret)
        self.left_set = aset0
        self.right_set = aset1
    
    def __contains__(self, element):
        #print "elemet", element
        if isinstance(element, tuple):
            l = element[0]
            r = element[1]
        else:
            raise NotImplementedError()
        return l in self.left_set and r in self.right_set
    
    def __eq__(self, aset):
        if not isinstance(aset, SymbolicCartSet):
            return False
        elif (self.left_set==aset.left_set) and (self.right_set==aset.right_set):
            return True
        return False
    
    def __ne__(self, aset):
        return not self.__eq__(aset)


class SymbolicUnionSet(SymbolicSet):
    def __init__(self, aset0, aset1, env, interpret):
        SymbolicSet.__init__(self, env, interpret)
        self.left_set = aset0
        self.right_set = aset1
        self.explicit_set_repr = None
    
    # function call of set
    def __getitem__(self, arg):
        if isinstance(self.left_set, SymbolicLambda) and isinstance(self.right_set, SymbolicLambda):
            try:
                result = self.left_set[arg] 
                return result
            except:
                result = self.right_set[arg] 
                return result
        raise Exception("Not implemented: relation symbolic membership")  

    def __eq__(self, aset):
        if aset==None:
            return False
        if isinstance(aset, SymbolicUnionSet):
            # may throw a DontKnowIfEqualException
            if check_syntacticly_equal(self, aset):
                return True
        if isinstance(aset, frozenset):
            if self.explicit_set_repr==None:
                self.explicit_set_repr = self.enumerate_all()
            return aset == self.explicit_set_repr
        raise DontKnowIfEqualException("lambda compare not implemented")
    
    def enumerate_all(self):
        if self.explicit_set_repr==None:
            L = self.left_set.enumerate_all()
            R = self.right_set.enumerate_all()
            self.explicit_set_repr = L + R
        return self.explicit_set_repr 

class SymbolicPowerSet(SymbolicSet):
    def __init__(self, aset, env, interpret):
        SymbolicSet.__init__(self, env, interpret)
        self.set = aset

    # e:S (element:self.set)
    def __contains__(self, element):
        print element
        print self.set
        raise Exception("not implemented")    


class SymbolicIntervalSet(LargeSet):
    def __init__(self, l, r, env, interpret):
        SymbolicSet.__init__(self, env, interpret)
        self.l = l
        self.r = r
        
    # e:S (element:l..r)
    def __contains__(self, element):
        if not isinstance(element, int):
            raise Exception("Interval membership with non-integer")
        if element<=self.r and element>=self.l:
            return True
        else:
            return False
    
    def enumerate_all(self):
        left = self.l
        right = self.r        
        return frozenset(range(left, right+1)) # TODO: Problem if to large


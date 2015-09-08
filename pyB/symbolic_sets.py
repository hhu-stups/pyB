# this classes represent set which should not be enumerated as long as possible (beste case: never)
# warning: some set behavior is implemented inside the interpreter and its helper-methodes and NOT here
# design decision: most functionality should implemented in this module. the goal is that
# symbolic sets behave like frozensets (as much as possible) 
# x (not)in S implemented in quick_eval.py (called by Belong-predicates x:S)
from bexceptions import ValueNotInDomainException, DontKnowIfEqualException, InfiniteSetLengthException
from btypes import *
from config import PRINT_WARNINGS, USE_RPYTHON_CODE
from helpers import double_element_check, remove_tuples, build_arg_by_type, enumerate_cross_product
from pretty_printer import pretty_print
from rpython_b_objmodel import W_Object, W_Integer, W_String, W_Tuple
from symbolic_helpers import check_syntacticly_equal, generate_powerset


if USE_RPYTHON_CODE:
     from rpython_b_objmodel import frozenset


##############
# Base-class and Primitive Sets
###############
# SymbolicSet, LargeSet, InfiniteSet
# Int-,Nat-,Nat1-,Natural-,Natural1-,Integer and StringSet


class SymbolicSet(W_Object):
    # env: min and max int values may be needed for large sets 
    # interpret: for function call on tuple-sets
    def __init__(self, env, interpret):
        self.env = env 
        self.interpret = interpret
        self.explicit_set_computed = False
        # Otherwise Rpython can not 'prove' this attrs are present 
        self.aSet = None
        self.left_set = None
        self.right_set = None

    def __mul__(self, aset):
        return SymbolicCartSet(self, aset, self.env, self.interpret)
    
    def __rmul__(self, aset):
        return SymbolicCartSet(aset, self, self.env, self.interpret)
        
    # default implementation
    def __sub__(self, aset):
        if PRINT_WARNINGS:
            print "\033[1m\033[91mWARNING\033[00m: default (brute force) function sub implementation called", self, aset
        
        self_values = self.enumerate_all()
        if not isinstance(aset, frozenset):
            values = aset.enumerate_all()
        else:
            values = aset
        return self_values.__sub__(values)
    
    def __rsub__(self, aset):
        return self.__sub__(aset, self)
            
    # delegate to method if syntactic suger is used S & T    
    def __and__(self, aset):
        return self.intersection(aset)
        
    def __rand__(self, aset):
        return self.__and__(aset, self)
    
    # delegate to method if syntactic suger is used S | T
    def __or__(self, aset):
        return self.union(aset)  
    
    def __ror__(self, aset):
        return self.__or__(aset, self)     
    
    # delegate to method if syntactic suger is used S > T
    def __ge__(self, aset):
        return self.issuperset(aset)

    # delegate to method if syntactic suger is used S < T        
    def __le__(self, aset):
        return self.issubset(aset)
    
    def __len__(self):
        return len(self.enumerate_all())
            
    # default implementation
    def __eq__(self, aset):
        if aset is None:
            return False
        if PRINT_WARNINGS:
            print "\033[1m\033[91mWARNING\033[00m: default (brute force) equality implementation called", self, aset
        
        self_values = self.enumerate_all()
        if not isinstance(aset, frozenset):
            values = aset.enumerate_all()
        else:
            values = aset
        return values.__eq__(self_values) 


    # default implementation
    def __ne__(self, aset):
        if PRINT_WARNINGS:
            print "\033[1m\033[91mWARNING\033[00m: default (brute force) unequality implementation called", self, aset
        return not self.__eq__(aset)       


    # default implementation
    def intersection(self, aset): 
        if PRINT_WARNINGS:
            print "\033[1m\033[91mWARNING\033[00m: default (brute force) intersection implementation called", self, aset
        result = []
        # Use enumerate all to avoid push/pop in every interation
        
        if not isinstance(aset, frozenset):
            values = aset.enumerate_all()
        else:
            values = aset
        for e in values:      
           if USE_RPYTHON_CODE:
               for element in self:
                   if element.__eq__(e):
                       result.append(e)
           else:
               if e in self: 
                   result.append(e)
        return frozenset(result)


    # default implementation
    def union(self, aset): 
        if PRINT_WARNINGS:
            print "\033[1m\033[91mWARNING\033[00m: default (brute force) union implementation called", self, aset
        result = []
        # Use enumerate all to avoid push/pop in every interation
        if not isinstance(aset, frozenset):
            values = aset.enumerate_all()
        else:
            values = aset
        return values.union(self.enumerate_all())
        
    # default implementation
    def issuperset(self, aset):
        if PRINT_WARNINGS:
            print "\033[1m\033[91mWARNING\033[00m: default (brute force) superset-check implementation called", self, aset
        if not isinstance(aset, frozenset):
            values = aset.enumerate_all()
        else:
            values = aset
                       
        for e in values:
           if USE_RPYTHON_CODE:
               e_in_self = False
               for element in self:
                   if element.__eq__(e):
                       e_in_self = True
               if not e_in_self:
                   return False
           else:
               if e not in self: 
                   return False
        return True           
      
    # default implementation
    def issubset(self, aset):
        if PRINT_WARNINGS:
            print "\033[1m\033[91mWARNING\033[00m: default (brute force) subset-check implementation called", self, aset
        for e in self:    
            if USE_RPYTHON_CODE:
               e_in_aset = False
               for element in aset:
                   if element.__eq__(e):
                       e_in_aset = True
               if not e_in_aset:
                  return False
            else:
               if e not in aset: 
                   return False
        return True        

    # default implementation
    def __contains__(self, element):
        if PRINT_WARNINGS:
            print "\033[1m\033[91mWARNING\033[00m: default (brute force) membership-check implementation called", self, element
        values = self.enumerate_all() 
        
        if USE_RPYTHON_CODE:
            for e in values:
                if element.__eq__(e):
                    return True
            return False
        else:
            return element in aSet

        
    # default implementation
    def __getitem__(self, args):
        if PRINT_WARNINGS:
            print "\033[1m\033[91mWARNING\033[00m: default (brute force) function app f(x) implementation called", self, args
        # set may be a relation
        aset = self.enumerate_all()
        result = []
        for t in aset:
            if USE_RPYTHON_CODE:
                if t.tvalue[0].__eq__(args):
                    result.append(t.tvalue[1])
            else:
                if t[0]==args:
                    result.append(t[1])
        # if only one value, return value
        if len(result)==1:
            return result[0]
        # else, return list of values (will be packed into a set by interp function)
        elif len(result)>1:
            return result
        raise ValueNotInDomainException(args) 

    def enumerate_all(self):
        if not self.explicit_set_computed:
            assert isinstance(self, W_Object)
            assert isinstance(self, SymbolicSet)
            result = []
            # RPython typing constraints made this ugly code necessary 
            if isinstance(self, SymbolicPower1Set):
                for e in self.SymbolicPower1Set_generator():
                     result.append(e)
            elif isinstance(self, SymbolicPowerSet):
                for e in self.SymbolicPowerSet_generator():
                     result.append(e)
            elif isinstance(self, SymbolicDifferenceSet):
                for e in self.SymbolicDifferenceSet_generator():
                     result.append(e)
            elif isinstance(self, SymbolicIntersectionSet):
                for e in self.SymbolicIntersectionSet_generator():
                     result.append(e)
            elif isinstance(self, StringSet):
                for e in self.StringSet_generator():
                     result.append(e)
            elif isinstance(self, IntSet):
                for e in self.IntSet_generator():
                     result.append(e)
            elif isinstance(self, Nat1Set):
                for e in self.Nat1Set_generator():
                     result.append(e)
            elif isinstance(self, NatSet):
                for e in self.NatSet_generator():
                     result.append(e)
            elif isinstance(self, IntegerSet):
                for e in self.IntegerSet_generator():
                     result.append(e)
            elif isinstance(self, Natural1Set):
                for e in self.Natural1Set_generator():
                     result.append(e)
            elif isinstance(self, NaturalSet):
                for e in self.NaturalSet_generator():
                     result.append(e)
            else:
                raise Exception("INTERNAL ERROR: unimplemented enumeration")                                           
            self.explicit_set_repr = frozenset(result)
            self.explicit_set_computed = True
        return self.explicit_set_repr

class LargeSet(SymbolicSet):
    pass
    

class InfiniteSet(SymbolicSet):
    # must return an integer, returning float("inf") is not an option
    def __len__(self):
        from bexceptions import InfiniteSetLengthException
        raise InfiniteSetLengthException("InfiniteSet")


# FIXME: set comprehension
class NaturalSet(InfiniteSet):
    def __contains__(self, element):
        return isinstance(element, int) and element >= 0 
    
    def issubset(self, aset): # NaturalSet <= aset
        if isinstance(aset, NaturalSet) or isinstance(aset, IntegerSet):
            return True
        # TODO: SetComp {x|x:NATURAL}, union, inter, UNION, INTER
        return False 
    
    def issuperset(self, aset): # NaturalSet >= aset
        if isinstance(aset, IntegerSet) or isinstance(aset, IntSet): # no neg nums
            return False
        elif isinstance(aset, frozenset):
            for x in aset:
                if USE_RPYTHON_CODE:
                    cond = x.ivalue<0
                else:
                    cond = x<0
                if cond:
                    return False
            return True
        elif isinstance(aset, NatSet) or isinstance(aset, Nat1Set) or isinstance(aset, NaturalSet) or isinstance(aset, Natural1Set):
            return True 
        raise NotImplementedError("inclusion with unknown set-type")
       
    def __lt__(self, aset): # NaturalSet < aset
        if isinstance(aset,IntegerSet):
            return True
        return False

    def __gt__(self, aset): # NaturalSet > aset
        if isinstance(aset, IntegerSet) or isinstance(aset, NaturalSet) or isinstance(aset, IntSet):
            return False
        elif isinstance(aset, frozenset):
            # TODO: equal impl like >= something is wrong
            for x in aset:
                if USE_RPYTHON_CODE:
                    cond = x.ivalue<0
                else:
                    cond = x<0
                if cond:
                    return False
            return True
        elif isinstance(aset, NatSet) or isinstance(aset, Nat1Set) or  isinstance(aset, Natural1Set):
            return True 
        raise NotImplementedError("inclusion with unknown set-type")  
    
    def __eq__(self, aset):
        if isinstance(aset, NaturalSet):
            return True
        return False
    
    def __ne__(self, aset):
        if isinstance(aset, NaturalSet):
            return False
        return True

    def NaturalSet_generator(self):
        i = 0
        while True:
            if USE_RPYTHON_CODE:
                yield W_Integer(i)
            else:
                yield i
            i = i +1  
    
    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.NaturalSet_gen = self.NaturalSet_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.NaturalSet_gen.next()
 
  
# FIXME: set comprehension        
class Natural1Set(InfiniteSet):
    def __contains__(self, element):
        return isinstance(element, int) and element > 0  
    
    def issubset(self, aset): # Natural1Set <= aset
        if isinstance(aset, InfiniteSet):
            return True
        return False
 
    def issuperset(self, aset): # Natural1Set >= aset
        if isinstance(aset, NaturalSet) or isinstance(aset, IntegerSet) or isinstance(aset, NatSet) or isinstance(aset, IntSet): # zero
            return False
        elif isinstance(aset, frozenset):
            for x in aset:
                if USE_RPYTHON_CODE:
                    cond = x.ivalue<=0
                else:
                    cond = x<=0
                if cond:
                    return False
            return True
        elif isinstance(aset, Nat1Set) or isinstance(aset, Natural1Set):
            return True 
        raise NotImplementedError("inclusion with unknown set-type")

    def __lt__(self, aset): # Natural1Set < aset
        if isinstance(aset, IntegerSet) or isinstance(aset, NaturalSet):
            return True
        return False

    def __gt__(self, aset): # Natura1lSet > aset
        if isinstance(aset, InfiniteSet) or isinstance(aset, LargeSet):
            return False
        elif isinstance(aset, frozenset):
            for x in aset:
                if USE_RPYTHON_CODE:
                    cond = x.ivalue<0
                else:
                    cond = x<0
                if cond:
                    return False
                return True
        raise NotImplementedError("inclusion with unknown set-type")  

    def __eq__(self, aset):
        if isinstance(aset, Natural1Set):
            return True
        return False
   
    def __ne__(self, aset):
        if isinstance(aset, Natural1Set):
            return False
        return True
    
    def Natural1Set_generator(self):
        i = 1
        while True:
            if USE_RPYTHON_CODE:
                yield W_Integer(i)
            else:
                yield i
            i = i +1  

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.Natural1Set_gen = self.Natural1Set_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.Natural1Set_gen.next()


# the infinite B-set INTEGER 
# FIXME: set comprehension   
class IntegerSet(InfiniteSet): 
    def __contains__(self, element):
        return isinstance(element, int) or isinstance(element, IntegerType) #type for symbolic checks
    
    def issubset(self, aset): # IntegerSet <= aset
        if isinstance(aset, IntegerSet):
            return True
        return False

    def issuperset(self, aset): # IntegerSet >= aset
        if isinstance(aset, SymbolicSet): 
            return True
        elif isinstance(aset, frozenset):
            for x in aset:
                if not isinstance(x, int):
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
                if USE_RPYTHON_CODE:
                    cond = x.ivalue<0
                else:
                    cond = x<0
                if cond:
                    return False
                return True
        elif isinstance(aset, NatSet) or isinstance(aset, Nat1Set) or isinstance(aset, IntSet) or isinstance(aset, NaturalSet) or isinstance(aset, Natural1Set):
            return True 
        raise NotImplementedError("inclusion with unknown set-type")  
   
    def __eq__(self, aset):
        if isinstance(aset, IntegerSet):
            return True
        return False

    def __ne__(self, aset):
        if isinstance(aset, IntegerSet):
            return False
        return True
    
    def IntegerSet_generator(self):
        i = 1
        if USE_RPYTHON_CODE:
            yield W_Integer(0)
        else:
            yield 0
        while True:
            if USE_RPYTHON_CODE:
                yield W_Integer(i)
                yield W_Integer(-i)
            else:
                yield i
                yield -i
            i = i +1     

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.IntegerSet_gen = self.IntegerSet_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.IntegerSet_gen.next()
        
     
# if min and max-int change over exec. this class will notice this change (env)
# FIXME: set comprehension
class NatSet(LargeSet):
    def __contains__(self, element):
        return isinstance(element, int) and element >=0 and element <= self.env._max_int
      
    def __len__(self):
        return self.env._max_int+1
     
    def issubset(self, aset): # NatSet <=
        if isinstance(aset, NatSet) or isinstance(aset, IntSet) or isinstance(aset, NaturalSet) or isinstance(aset, IntegerSet):
            return True
        elif isinstance(aset, frozenset):
            for x in aset:
                if not self.__contains__(x):
                    return False
            return len(aset)>=self.__len__()
        elif isinstance(aset, Natural1Set) or isinstance(aset, Nat1Set):
            return False
        raise NotImplementedError("inclusion with unknown set-type")
    
    def issuperset(self, aset): # NatSet >= aset
        if isinstance(aset, InfiniteSet) or isinstance(aset, IntSet) : 
            return False
        elif isinstance(aset, NatSet) or isinstance(aset,  Nat1Set):
            return True
        elif isinstance(aset, frozenset):
            for x in aset:
                if USE_RPYTHON_CODE:
                    cond = x.ivalue<=0
                else:
                    cond = x<=0
                if cond:
                    return False
            return True
        raise NotImplementedError("inclusion with unknown set-type")       

    def __lt__(self, aset): # NatSet < aset
        if isinstance(aset, IntegerSet) or isinstance(aset, NaturalSet) or isinstance(aset, IntSet):
            return True
        return False
        
    def __gt__(self, aset): # NatSet > aset
        if isinstance(aset,InfiniteSet) or isinstance(aset, IntSet) or isinstance(aset, NatSet):
            return False
        elif isinstance(aset, frozenset):
            for x in aset:
                if USE_RPYTHON_CODE:
                    cond = x.ivalue<0
                else:
                    cond = x<0
                if cond:
                    return False
                return True
        elif isinstance(aset, Nat1Set):
            return True 
        raise NotImplementedError("inclusion with unknown set-type")         
    
       
    def union(self, aset):
        if isinstance(aset, NatSet):
            return self
        elif isinstance(aset, Nat1Set):
            return self
        elif isinstance(aset, IntSet):
            return aset
        elif isinstance(aset, InfiniteSet):
            return aset
        else:
            raise NotImplementedError("Union of NAT1 and %s" % aset)

    def __eq__(self, aset):
        if isinstance(aset, NatSet):
            return True
        return False
    
    def __ne__(self, aset):
        if isinstance(aset, NatSet):
            return False
        return True


    def NatSet_generator(self):
        for i in range(0, self.env._max_int+1):
            if USE_RPYTHON_CODE:
                yield W_Integer(i)
            else:
                yield i      

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.NatSet_gen = self.NatSet_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.NatSet_gen.next()
        
    # not used for performance reasons
    #def __getitem__(self, key):
    #    return key

  
# FIXME: set comprehension      
class Nat1Set(LargeSet):
    def __contains__(self, element):
        return isinstance(element, int) and element >0 and element <= self.env._max_int

    def __len__(self):
        return self.env._max_int
    
    def issubset(self, aset): # Nat1Set <=
        if isinstance(aset, InfiniteSet) or isinstance(aset, LargeSet):
            return True
        elif isinstance(aset, frozenset):
            for x in aset:
                if not self.__contains__(x):
                    return False
            return len(aset)>=self.__len__()
        raise NotImplementedError("inclusion with unknown set-type")
    
    def issuperset(self, aset): # Nat1Set >= aset
        if isinstance(aset, NatSet) or isinstance(aset, IntSet) or isinstance(aset, InfiniteSet): 
            return False
        elif isinstance(aset, Nat1Set):
            return True
        elif isinstance(aset, frozenset):
            for x in aset:
                if USE_RPYTHON_CODE:
                    cond = x.ivalue<0
                else:
                    cond = x<0
                if cond:
                    return False
            return True
        raise NotImplementedError("inclusion with unknown set-type")

    def __lt__(self, aset): # Nat1Set < aset
        if isinstance(aset, Nat1Set):
            return False
        return True     

    def __gt__(self, aset): # Nat1Set > aset
        if isinstance(aset, InfiniteSet) or isinstance(aset, LargeSet):
            return False
        elif isinstance(aset, frozenset):
            #TODO: same imple like >= something is wrong
            for x in aset:
                if USE_RPYTHON_CODE:
                    cond = x.ivalue<0
                else:
                    cond = x<0
                if cond: 
                    return False
                return True
        raise NotImplementedError("inclusion with unknown set-type")  

    def __eq__(self, aset):
        if isinstance(aset, Nat1Set):
            return True
        me = self.enumerate_all()
        return aset.__eq__(me)
    
    def __ne__(self, aset):
        if isinstance(aset, Nat1Set):
            return False
        me = self.enumerate_all()
        return not aset.__eq__(me)
        
    def Nat1Set_generator(self):
        for i in range(1, self.env._max_int+1):
            if USE_RPYTHON_CODE:
                yield W_Integer(i)
            else:
                yield i   

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.Nat1Set_gen = self.Nat1Set_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.Nat1Set_gen.next()


    # not used for performance reasons
    #def __getitem__(self, key):
    #    return 1+key
        

# FIXME: set comprehension
class IntSet(LargeSet):
    def __contains__(self, element):
        return isinstance(element, int) and element >= self.env._min_int and element <= self.env._max_int
    
    def issubset(self, aset): # IntSet <=
        if isinstance(aset, IntSet) or isinstance(aset,  IntegerSet):
            return True
        elif isinstance(aset, frozenset):
            for x in aset:
                if not self.__contains__(x):
                    return False
            return len(aset)>=self.__len__()
        elif isinstance (aset, NatSet) or isinstance(aset, Nat1Set)  or isinstance(aset, NaturalSet) or isinstance(aset, Natural1Set):
            return False
        raise NotImplementedError("inclusion with unknown set-type")
    
    def issuperset(self, aset): # IntSet >= aset
        if isinstance(aset, InfiniteSet): 
            return False
        elif isinstance(aset, LargeSet):
            return True
        elif isinstance(aset, frozenset):
            for x in aset:
                if not isinstance(x, int):
                    return False
            return True
        raise NotImplementedError("inclusion with unknown set-type") 

    def __lt__(self, aset): # IntSet < aset
        if isinstance(aset, IntegerSet):
            return True
        return False    

    def __gt__(self, aset): # IntSet > aset
        if isinstance(aset, InfiniteSet) or isinstance(aset, IntSet):
            return False
        elif isinstance(aset, frozenset):
            for x in aset:
                if USE_RPYTHON_CODE:
                    cond = x.ivalue<0
                else:
                    cond = x<0
                if cond:
                    return False
                return True
        elif isinstance(aset, Nat1Set) or isinstance(aset, NatSet):
            return True 
        raise NotImplementedError("inclusion with unknown set-type")  

    def __eq__(self, aset):
        if isinstance(aset, IntSet):
            return True
        return False
    
    def __ne__(self, aset):
        if isinstance(aset, IntSet):
            return False
        return True

    def __len__(self):
        return -1*self.env._min_int+self.env._max_int+1

    # TODO: alternate positive and negative values
    def IntSet_generator(self):
        for i in range(self.env._min_int, self.env._max_int+1):
            if USE_RPYTHON_CODE:
                yield W_Integer(i)
            else:
                yield i    
 
    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.IntSet_gen = self.IntSet_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.IntSet_gen.next()
        
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
        if isinstance(aset, StringSet):
            return True
        return False
    
    def __ne__(self, aset):
        if isinstance(aset, StringSet):
            return False
        return True
    
    def StringSet_generator(self):
        for i in self.env.all_strings:
            if USE_RPYTHON_CODE:
                yield W_String(i)
            else:
                yield i
  

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.StringSet_gen = self.StringSet_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.StringSet_gen.next()

##############
# Symbolic binary operations 
##############
# No symbolic implementation: singelton, set enum, empty set, pair
# Set comprehension in module: symbolic_functions_with_predicate.py
# Union, Intersection, Difference, Cartesian product


class SymbolicUnionSet(SymbolicSet):
    def __init__(self, aset0, aset1, env, interpret):
        SymbolicSet.__init__(self, env, interpret)
        self.left_set = aset0
        self.right_set = aset1
    
    # function call of set
    def __getitem__(self, arg):
        if isinstance(self.left_set, SymbolicSet) and isinstance(self.right_set, SymbolicSet):
            try:
                result = self.left_set[arg] 
                return result
            except:
                result = self.right_set[arg] 
                return result
        # TODO frozensets
        raise Exception("Not implemented: relation symbolic membership")  
    
    def enumerate_all(self):
        if not self.explicit_set_computed:
            if isinstance(self.left_set, SymbolicSet):
                L = self.left_set.enumerate_all()
            else:
                L = self.left_set
            if isinstance(self.right_set, SymbolicSet):
                R = self.right_set.enumerate_all()
            else:                
                R = self.right_set
            assert isinstance(L, frozenset)
            assert isinstance(R, frozenset)
            self.explicit_set_repr = L.union(R)
            self.explicit_set_computed = True
        return self.explicit_set_repr

    # TODO: write test-case
    def __contains__(self, element):
        assert self.left_set is not None
        assert self.right_set is not None
        return element in self.right_set or element in self.left_set
        
    # TODO: think of caching possibilities 
    def SymbolicUnionSet_generator(self):
        double = []
        for x in self.left_set:
            double.append(x)
            yield x
        for y in self.right_set:
            if USE_RPYTHON_CODE:
                y_in_double = False
                for x in double:
                   if y.__eq__(x):
                       y_in_double = True
                if not y_in_double:
                    yield y
            else:
                if y not in double:
                    yield y

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicUnionSet_gen = self.SymbolicUnionSet_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicUnionSet_gen.next()
 
         

class SymbolicIntersectionSet(SymbolicSet):
    def __init__(self, aset0, aset1, env, interpret):
        SymbolicSet.__init__(self, env, interpret)
        self.left_set = aset0
        self.right_set = aset1

    def __contains__(self, element):
        assert self.left_set is not None
        assert self.right_set is not None                     
        contains_right = False
        contains_left = False
        if USE_RPYTHON_CODE:
            for x in self.right_set:
                if x.__eq__(element):
                    contains_right = True
            for x in self.left_set:
                if x.__eq__(element):
                    contains_left = True           
        else:
            contains_right = element in self.right_set
            contains_left  = element in self.left_set    
        return contains_right and contains_left
            
    # try to iterate the finite one    
    def SymbolicIntersectionSet_generator(self):
        assert self.left_set is not None
        assert self.right_set is not None 
        
        # TODO: checking for a (finite) frozenset and including rpython code in
        # nested loop does not translate. Reason unknown
        if USE_RPYTHON_CODE:
            for x in self.left_set:
                for y in self.right_set:
                    if x.__eq__(y):
                        yield x
                        break
        else:     
            if isinstance(self.left_set, frozenset):
                for x in self.left_set:
                        if x in self.right_set:
                            yield x
            else:
                for x in self.right_set:
                        if x in self.left_set:
                            yield x        
        
    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicIntersectionSet_gen = self.SymbolicIntersectionSet_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicIntersectionSet_gen.next()    


class SymbolicDifferenceSet(SymbolicSet):
    def __init__(self, aset0, aset1, env, interpret):
        SymbolicSet.__init__(self, env, interpret)
        self.left_set = aset0
        self.right_set = aset1

    def __contains__(self, element):
        assert self.left_set is not None
        assert self.right_set is not None
        contains_right = False
        contains_left = False
        if USE_RPYTHON_CODE:
            for x in self.right_set:
                if x.__eq__(element):
                    contains_right = True
            for x in self.left_set:
                if x.__eq__(element):
                    contains_left = True           
        else:
            contains_right = element in self.right_set
            contains_left  = element in self.left_set                          
        return contains_left and not contains_right
        
    def SymbolicDifferenceSet_generator(self):
        assert self.left_set is not None
        assert self.right_set is not None
        for x in self.left_set:
            if USE_RPYTHON_CODE:
                x_in_right_set = False
                for y in self.right_set: 
                    if y.__eq__(x):
                        x_in_right_set = True
                if not x_in_right_set:
                    yield x
            else:
                if x not in self.right_set:
                    yield x

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicDifferenceSet_gen = self.SymbolicDifferenceSet_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicDifferenceSet_gen.next()           
 
        
class SymbolicCartSet(SymbolicSet):
    def __init__(self, aset0, aset1, env, interpret):
        SymbolicSet.__init__(self, env, interpret)
        self.left_set = aset0
        self.right_set = aset1
    
    def __contains__(self, element):
        #print "element", element
        if isinstance(element, tuple):
            l = element[0]
            r = element[1]
        elif isinstance(element, W_Tuple):
            l = element.tvalue[0]
            r = element.tvalue[1]
        else:
            raise NotImplementedError()
        contains_left = False
        contains_right = False
        if USE_RPYTHON_CODE:
            for e in self.left_set:
                if l.__eq__(e):
                    contains_left = True
            for e in self.right_set:
                if r.__eq__(e):
                    contains_right = True           
        else:
            contains_left = l in self.left_set
            contains_right = r in self.right_set
        return contains_left and contains_right
    
    def __eq__(self, aset):
        if isinstance(aset, SymbolicCartSet):
            return (self.left_set.__eq__(aset.left_set)) and (self.right_set.__eq__(aset.right_set))
        else:
            return SymbolicSet.__eq__(self, aset) 
    
    def __ne__(self, aset):
        return not self.__eq__(aset)
        
    def enumerate_all(self):
        if not self.explicit_set_computed:
            if isinstance(self.left_set, SymbolicSet):
                aset0 = self.left_set.enumerate_all()
            else:
                aset0 = self.left_set
            if isinstance(self.right_set, SymbolicSet):
                aset1 = self.right_set.enumerate_all()
            else:
                aset1 = self.right_set
            lst = []
            for x in aset0:
                for y in aset1:
                    if USE_RPYTHON_CODE:
                        lst.append(W_Tuple((x,y)))
                    else:
                        lst.append((x,y))
                    
            self.explicit_set_repr = frozenset(lst)
            self.explicit_set_computed = True
        return self.explicit_set_repr

    def SymbolicCartSet_generator(self):
        return enumerate_cross_product(self.left_set, self.right_set)
 

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicCartSet_gen = self.SymbolicCartSet_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicCartSet_gen.next()  

#################
# Unary Set operations
#################
# No implementation: FIN, FIN1   
# POW, POW1
# missing: union, inter, UNION, INTER
        
class SymbolicPowerSet(SymbolicSet):
    def __init__(self, aset, env, interpret):
        SymbolicSet.__init__(self, env, interpret)
        self.aSet = aset

    # e:S (element:self.set)
    def __contains__(self, element):
        assert self.aSet is not None
        if element is None:
            return False
        if not isinstance(element, frozenset):
            element = element.enumerate_all()
            
        assert element is not None
        for e in element:
            if USE_RPYTHON_CODE:
                e_in_aSet = False
                for x in self.aSet:
                    if e.__eq__(x):
                        e_in_aSet = True
                if not e_in_aSet:
                    return False
            else:
                if e not in self.aSet:
                    return False
        return True

    def SymbolicPowerSet_generator(self):
        assert self.aSet is not None
        
        yield frozenset([])
        # size = |S|*|T|
        try:
            size = self.aSet.__len__()
        except InfiniteSetLengthException:
            size = float("inf")
        i =0
        while i!=size:
            for lst in generate_powerset(self.aSet, size=i+1, skip=0):
                assert len(lst)==i+1
                yield frozenset(lst)
            i = i+1

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicPowerSet_gen = self.SymbolicPowerSet_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicPowerSet_gen.next() 

class SymbolicPower1Set(SymbolicSet):
    def __init__(self, aset, env, interpret):
        SymbolicSet.__init__(self, env, interpret)
        self.aSet = aset

    # e:S (element:self.set)
    def __contains__(self, element):
        assert self.aSet is not None
        if element is None:
            return False
        if not isinstance(element, frozenset):
            element = element.enumerate_all()
        if element.__eq__(frozenset([])):
            return False
        
        assert element is not None
        for e in element:
            if USE_RPYTHON_CODE:
                e_in_aSet = False
                for x in self.aSet:
                    if e.__eq__(x):
                        e_in_aSet = True
                if not e_in_aSet:
                    return False
            else:
                if e not in self.aSet:
                    return False
        return True

    def SymbolicPower1Set_generator(self):
        assert self.aSet is not None
        
        # size = |S|*|T|
        try:
            size = self.aSet.__len__()
        except InfiniteSetLengthException:
            size = float("inf")
        i =0
        while i!=size:
            for lst in generate_powerset(self.aSet, size=i+1, skip=0):
                assert len(lst)==i+1
                yield frozenset(lst)
            i = i+1
      

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicPower1Set_gen = self.SymbolicPower1Set_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicPower1Set_gen.next() 


class SymbolicIntervalSet(LargeSet):
    def __init__(self, l, r, env, interpret):
        SymbolicSet.__init__(self, env, interpret)
        assert isinstance(l, int)
        assert isinstance(r, int)
        self.l = l
        self.r = r
        
    # e:S (element:l..r)
    def __contains__(self, element):                     
        if not isinstance(element, int) and not isinstance(element, W_Integer):
            raise Exception("Interval membership with non-integer: %s" % element)
        if element>=self.l and element<=self.r:
            return True
        else:
            return False
            
    def __eq__(self, other):            
        if isinstance(other, SymbolicIntervalSet):
            return other.l==self.l and other.r==self.r
        return SymbolicSet.__eq__(self,other)  
    
    def enumerate_all(self):        
        if not self.explicit_set_computed:
            assert isinstance(self.l, int)
            assert isinstance(self.r, int)
            
            self.explicit_set_repr = frozenset(range(self.l, self.r+1)) # TODO: Problem if to large  
            self.explicit_set_computed = True   
        return self.explicit_set_repr

    def SymbolicIntervalSet_generator(self):
        for i in range(self.l, self.r+1):
            if USE_RPYTHON_CODE:
                yield W_Integer(i)
            else:
                yield i

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicIntervalSet_gen = self.SymbolicIntervalSet_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicIntervalSet_gen.next()     
    
        
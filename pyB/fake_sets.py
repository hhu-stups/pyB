# this classes represent set which should not be enumerated as long as possible (beste case: never)
# warning: some set behavior is implemented inside the interpreter
# and its helper-methodes and NOT here
# x (not)in S implemented in quick_eval.py (called by Belong-predicates x:S)

class FakeSet:
    def __init__(self, env):
        self.env = env # min and max int values may be needed
    
    def __mul__(self, aset):
        return FakeCartSet(self, aset)
    
    def __rmul__(self, aset):
        return FakeCartSet(aset, self)
    
    def __eq__(self, aset):
        if self.__class__ == aset.__class__:
            return True
        return False


class LargeSet(FakeSet):
    pass
    

class InfiniteSet(FakeSet):
    pass


class NaturalSet(InfiniteSet):
    def __contains__(self, element):
        return isinstance(element, int) and element >= 0  


class Natural1Set(InfiniteSet):
    def __contains__(self, element):
        return isinstance(element, int) and element > 0  
 

# the infinite B-set INTEGER    
class IntegerSet(InfiniteSet): 
    def __contains__(self, element):
        return isinstance(element, int)
        
        
# if min and max-int change over exec. this class will notice this change (env)
class NatSet(LargeSet):
    def __contains__(self, element):
        return isinstance(element, int) and element >=0 and element <= self.env._max_int
  
      
class Nat1Set(LargeSet):
    def __contains__(self, element):
        return isinstance(element, int) and element >0 and element <= self.env._max_int


class IntSet(LargeSet):
    def __contains__(self, element):
        return isinstance(element, int) and element >= self.env._min_int and element <= self.env._max_int
    

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


class FakePowerSet(FakeSet):
    pass #TODO: implement me
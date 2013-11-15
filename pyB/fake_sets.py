# this classes represent set which should not be enumerated as long as possible (beste case: never)
# warning: some set behavior is implemented inside the interpreter
# and its helper-methodes and NOT here

class FakeSet:
    def __init__(self, env):
        self.env = env # min and max int values may be needed
    
    def __mul__(self, aset):
        return FakeCartSet(self, aset)


class LargeSet(FakeSet):
    pass
    

class InfiniteSet(FakeSet):
    pass


class NaturalSet(InfiniteSet):
    pass    


class Natural1Set(InfiniteSet):
    pass
    

# TODO: if min and max-int change over exec. this class musst notice this change
class NatSet(LargeSet):
    pass
    

class Nat1Set(LargeSet):
    pass


class IntSet(LargeSet):
    pass
    

class IntegerSet(InfiniteSet):
    pass # the infinite B-set INTEGER
    

class FakeCartSet(FakeSet):
    def __init__(self, aset0, aset1):
        self.aset0 = aset0
        self.aset1 = aset1


class FakePowerSet(FakeSet):
    pass
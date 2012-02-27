# -*- coding: utf-8 -*-

class BType: # Baseclass used to repr. concrete type
    pass

class StringType(BType):
    pass

class BoolType(BType):
    pass

class IntegerType(BType):
    def __init__(self, number_or_None):
        # maybe this data is useless for typechecking
        self.data = number_or_None 


class PowerSetType(BType):
    def __init__(self, aset_type):
        self.data = aset_type


class SetType(BType):
    def __init__(self, name):
        self.data = name # None when name unknown


class EmptySetType(BType):
    def __init__(self):
        pass


# pairtype
class CartType(BType):
    def __init__(self, setA, setB):
        self.data = (setA, setB)


class UnknownType(): # no BType: used later to throw Exceptions
    # the arg real_type is only set by tests!
    def __init__(self, name, real_type):
        # this member is used to learn the name of sets
        self.name = name
        # if this is still None after typechecking 
        # than a Typeerror has been found
        self.real_type = real_type


# will be decidet in resolve()
class PowCartORIntegerType(UnknownType):
    def __init__(self, arg1, arg2):
        UnknownType.__init__(self, None,None)
        self.data = (arg1, arg2)


# will be decidet in resolve()
class PowORIntegerType(UnknownType):
    def __init__(self, arg1, arg2):
        UnknownType.__init__(self, None,None)
        self.data = (arg1, arg2)

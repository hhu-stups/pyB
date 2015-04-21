# -*- coding: utf-8 -*-
#
# B Language Reference Manual - Version 1.8.6 
# Page 14: 3.2. B-Types
#
# Type ::= Basic_type
#        	 | “P” “(“ Type “)”
#        	 | Type x Type
#        	 | “struct” “(“ (Ident “:” Type)+”,” “)”
#        	 | “(“ Type “)”
# Basic_type ::= “Z”
#        	 | “BOOL”
#       	 | “STRING”
#        	 | Ident


# Introduced to enable RPython translation. 
# NEVER TO BE INSTANTIATED! 
class AbstractType:
    pass


class BType(AbstractType): # Baseclass used to repr. concrete type
    pass

class StringType(BType):
    pass

class BoolType(BType):
    pass

class IntegerType(BType):
    def __init__(self):
        pass
        

class PowerSetType(BType):
    def __init__(self, aset_type):
        self.data = aset_type


class SetType(BType):
    def __init__(self, name):
        assert isinstance(name, str)
        self.name = name # None when name unknown


# pairtype: Type x Type
class CartType(BType):
    def __init__(self, setA, setB):
        assert isinstance(setA, PowerSetType)
        assert isinstance(setB, PowerSetType)
        self.data = (setA, setB)


# “struct” “(“ (Ident “:” Type)+”,” “)”
class StructType(BType):
    def __init__(self, dictionary):
        assert isinstance(dictionary, dict)
        self.data = dictionary


class UnknownType(AbstractType): # no BType: used later to throw exceptions, a type-variable 
    def __init__(self, type_name):
        # this member is used to learn the name of sets and for debugging
        self.type_name = type_name
        # if this is still None after typechecking 
        # than a Typeerror has been found
        self.real_type = None


# will be decided in resolve()
class PowCartORIntegerType(UnknownType):
    def __init__(self, arg1, arg2):
        UnknownType.__init__(self, "PowCartORIntegerType")
        self.data = (arg1, arg2)


# will be decided in resolve()
# arg1 and arg2 have both the type IntegerType OR the type 
# PowerSetType (of something known at resolve phase)
class PowORIntegerType(UnknownType):
    def __init__(self, arg1, arg2):
        UnknownType.__init__(self, "PowORIntegerType")
        self.data = (arg1, arg2) 
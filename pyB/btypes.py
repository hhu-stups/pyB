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
# eq_type method needed for Rpython translation


# Introduced to enable RPython translation. 
# NEVER TO BE INSTANTIATED! 
class AbstractType:
    pass


class BType(AbstractType): # Baseclass used to repr. concrete type
    pass

class StringType(BType):
    def eq_type(self, other):
        if isinstance(other, StringType):
            return True
        return False

class BoolType(BType):
    def eq_type(self, other):
        if isinstance(other, BoolType):
            return True
        return False

class IntegerType(BType):
    def __init__(self):
        pass
        
    def eq_type(self, other):
        if isinstance(other, IntegerType):
            return True
        return False
        

class PowerSetType(BType):
    def __init__(self, aset_type):
        self.data = aset_type

    def eq_type(self, other):
        if isinstance(other, PowerSetType):
            return True
        return False


class SetType(BType):
    def __init__(self, name):
        assert isinstance(name, str)
        self.name = name # None when name unknown

    def eq_type(self, other):
        if isinstance(other, SetType):
            return True
        return False


# pairtype: Type x Type
class CartType(BType):
    def __init__(self, setA, setB):
        assert isinstance(setA, PowerSetType)
        assert isinstance(setB, PowerSetType)
        self.left = setA
        self.right = setB

    def eq_type(self, other):
        if isinstance(other, CartType):
            return True
        return False


# “struct” “(“ (Ident “:” Type)+”,” “)”
class StructType(BType):
    def __init__(self, dictionary):
        # NOT RPYTHON
        #assert isinstance(dictionary, dict)
        self.dictionary = dictionary

    def eq_type(self, other):
        if isinstance(other, StructType):
            return True
        return False

class UnknownType(AbstractType): # no BType: used later to throw exceptions, a type-variable 
    def __init__(self, type_name):
        # this member is used to learn the name of sets and for debugging
        self.type_name = type_name
        # if this is still None after typechecking 
        # than a Typeerror has been found
        self.real_type = None

    #def __eq__(self, other):
    #    # if already more informations present this unification is a bug if true, even if iis strictly speaking false
    #    if isinstance(other, PowCartORIntegerType) or isinstance(other, PowORIntegerType):
    #        return False
    #    if isinstance(other, UnknownType):#XXX
    #        return True
    #    return False


# will be decided in resolve()
class PowCartORIntegerType(UnknownType):
    def __init__(self, arg1, arg2):
        UnknownType.__init__(self, "PowCartORIntegerType")
        self.left  = arg1
        self.right = arg2

    #def __eq__(self, other):
    #    if isinstance(other, PowCartORIntegerType):#XXX
    #        return True
    #    return False

# will be decided in resolve()
# arg1 and arg2 have both the type IntegerType OR the type 
# PowerSetType (of something known at resolve phase)
class PowORIntegerType(UnknownType):
    def __init__(self, arg1, arg2):
        UnknownType.__init__(self, "PowORIntegerType")
        self.left  = arg1
        self.right = arg2

    #def __eq__(self, other):
    #    if isinstance(other, PowORIntegerType): #XXX
    #        return True
    #    return False

class BTypeException(Exception):
    def __init__(self, string):
        self.value = string

# caused by e.g: f={(1,42)} & x=f[5] 
class ValueNotInDomainException(BTypeException):   
    def __init__(self, value):
        self.value = value

class ConstraintNotImplementedException(BTypeException):
    def __init__(self, node):
        self.value = node

class ValueNotInBStateException(BTypeException):
    def __init__(self, value):
        self.value = value
        
class INITNotPossibleException(BTypeException):
    def __init__(self, string):
        self.value = string

class SETUPNotPossibleException(BTypeException):
    def __init__(self, string):
        self.value = string

class ResolveFailedException(BTypeException):
    def __init__(self, string):
        self.value = string